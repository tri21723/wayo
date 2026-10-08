from uuid import uuid4

from test_trip_storage import create, headers

from app.availability import available_days
from app.schemas import TripRequest


def trip(payload, **changes):
    return TripRequest.model_validate({**payload["trip"], **changes})


def test_arrival_departure_clip_and_total_time(payload):
    request = trip(payload)
    days = available_days(request)
    assert [day.available_minutes for day in days] == [540, 720, 480]
    assert days[0].blocks[0].starts_at.isoformat() == "2026-11-06T12:00:00+07:00"
    assert days[-1].blocks[-1].ends_at.isoformat() == "2026-11-08T17:00:00+07:00"
    for day in days:
        for left, right in zip(day.blocks, day.blocks[1:], strict=False):
            assert left.ends_at == right.starts_at
        assert all(item.minutes > 0 for item in day.blocks)
    assert sum(item.minutes for day in days for item in day.blocks) == 53 * 60


def test_overnight_event_split_and_no_double_count(payload):
    request = trip(
        payload,
        fixed_events=[
            {
                "label": "Overnight booking",
                "starts_at": "2026-11-06T20:00:00+07:00",
                "ends_at": "2026-11-07T10:00:00+07:00",
            }
        ],
    )
    days = available_days(request)
    assert [day.available_minutes for day in days] == [480, 660, 480]
    fixed = [item for day in days for item in day.blocks if item.kind == "fixed"]
    assert len(fixed) == 2 and sum(item.minutes for item in fixed) == 14 * 60
    assert fixed[0].ends_at == fixed[1].starts_at


def test_late_arrival_early_departure_no_activity(payload):
    request = trip(
        payload, arrival_at="2026-11-06T22:00:00+07:00", departure_at="2026-11-07T07:00:00+07:00"
    )
    days = available_days(request)
    assert [day.available_minutes for day in days] == [0, 0]
    assert all(item.kind == "outside_activity_hours" for day in days for item in day.blocks)


def test_midnight_departure_keeps_empty_date_and_timezone(payload):
    # UTC input represents local arrival at 12:00 and departure exactly at midnight.
    request = trip(payload, arrival_at="2026-11-06T05:00:00Z", departure_at="2026-11-07T17:00:00Z")
    days = available_days(request)
    assert [day.date for day in days] == ["2026-11-06", "2026-11-07", "2026-11-08"]
    assert days[-1].blocks == [] and days[-1].available_minutes == 0


def test_full_activity_window_booked_and_fractional_time(payload):
    request = trip(
        payload,
        fixed_events=[
            {
                "label": "Booking",
                "starts_at": "2026-11-07T09:00:00+07:00",
                "ends_at": "2026-11-07T21:00:00+07:00",
            }
        ],
    )
    days = available_days(request)
    assert days[1].available_minutes == 0
    assert [item.kind for item in days[1].blocks] == [
        "outside_activity_hours",
        "fixed",
        "outside_activity_hours",
    ]
    request = trip(
        payload,
        fixed_events=[
            {
                "label": "Short booking",
                "starts_at": "2026-11-07T09:00:00+07:00",
                "ends_at": "2026-11-07T09:00:30+07:00",
            }
        ],
    )
    assert available_days(request)[1].available_minutes == 719.5


def test_availability_endpoint_owner_revision_and_no_writes(storage, payload):
    client, _, _ = storage
    owner = uuid4()
    saved = create(client, owner, payload)
    url = f"/v1/trips/{saved['id']}/availability"
    assert client.get(url).status_code == 401
    assert client.get(url, headers=headers(uuid4())).status_code == 404
    response = client.get(url, headers=headers(owner))
    assert response.status_code == 200
    assert response.json()["trip_revision"] == 1
    assert len(response.json()["days"]) == 3
    assert any(item["code"] == "MISSING_ANCHOR" for item in response.json()["notices"])
    assert client.get(f"/v1/trips/{saved['id']}", headers=headers(owner)).json() == saved
