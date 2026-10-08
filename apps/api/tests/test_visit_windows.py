from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session
from test_catalog import batch, poi
from test_trip_storage import create, headers

from app.availability import available_days
from app.catalog import PlaceRecord, import_batch
from app.recommendations import rank_places
from app.schemas import TripRequest
from app.visit_windows import visit_timing


def record(**changes):
    return PlaceRecord.model_validate(poi(**changes))


def opening(weekday=5, opens="09:00", closes="17:00"):
    return {"weekday": weekday, "opens": opens, "closes": closes}


def request(payload, **changes):
    return TripRequest.model_validate({**payload["trip"], **changes})


def test_weekday_arrival_departure_and_last_start(payload):
    trip = request(payload)
    place = record(hours=[opening(4), opening(5), opening(6)], duration_minutes=60)
    timing = visit_timing(place, available_days(trip))
    assert timing.status == "fits_known_hours"
    assert [window.starts_at.isoformat() for window in timing.windows] == [
        "2026-11-06T12:00:00+07:00",
        "2026-11-07T09:00:00+07:00",
        "2026-11-08T09:00:00+07:00",
    ]
    assert all(window.latest_start_at.hour == 16 for window in timing.windows)
    assert all(
        window.latest_start_at + timedelta(minutes=60) == window.ends_at
        for window in timing.windows
    )
    closed = record(hours=[opening(0)], duration_minutes=60)
    assert visit_timing(closed, available_days(trip)).status == "no_window"


def test_fixed_event_splits_windows_and_cannot_sum_short_gaps(payload):
    trip = request(
        payload,
        fixed_events=[
            {
                "label": "Booking",
                "starts_at": "2026-11-07T10:00:00+07:00",
                "ends_at": "2026-11-07T11:00:00+07:00",
            }
        ],
    )
    days = available_days(trip)
    timing = visit_timing(record(hours=[opening(closes="12:00")], duration_minutes=60), days)
    assert [(window.starts_at.hour, window.ends_at.hour) for window in timing.windows] == [
        (9, 10),
        (11, 12),
    ]
    assert all(window.latest_start_at == window.starts_at for window in timing.windows)
    assert (
        visit_timing(record(hours=[opening(closes="12:00")], duration_minutes=90), days).status
        == "no_window"
    )


def test_adjacent_opening_windows_merge_but_lunch_closure_does_not(payload):
    days = available_days(request(payload))
    adjacent = record(
        hours=[opening(closes="10:00"), opening(opens="10:00", closes="11:00")], duration_minutes=90
    )
    assert visit_timing(adjacent, days).status == "fits_known_hours"
    separated = record(
        hours=[opening(closes="10:00"), opening(opens="10:30", closes="11:30")], duration_minutes=90
    )
    assert visit_timing(separated, days).status == "no_window"


@pytest.mark.parametrize(
    "hours,duration,status",
    [
        (None, 60, "unknown_hours"),
        ([opening()], None, "unknown_duration"),
        ([], None, "no_window"),
        ([opening(0)], None, "no_window"),
    ],
)
def test_missing_data_distinct_from_closed(payload, hours, duration, status):
    timing = visit_timing(
        record(hours=hours, duration_minutes=duration), available_days(request(payload))
    )
    assert timing.status == status and not timing.windows


def test_no_available_time_excludes_even_unknown_hours(payload):
    trip = request(
        payload, arrival_at="2026-11-06T22:00:00+07:00", departure_at="2026-11-07T07:00:00+07:00"
    )
    assert visit_timing(record(hours=None), available_days(trip)).status == "no_window"


def test_timezone_and_overnight_booking(payload):
    trip = request(
        payload,
        arrival_at="2026-11-06T05:00:00Z",
        fixed_events=[
            {
                "label": "Overnight",
                "starts_at": "2026-11-06T13:00:00Z",
                "ends_at": "2026-11-07T03:00:00Z",
            }
        ],
    )
    timing = visit_timing(
        record(hours=[opening(opens="09:00", closes="12:00")], duration_minutes=60),
        available_days(trip),
    )
    assert timing.windows[0].starts_at.isoformat() == "2026-11-07T10:00:00+07:00"


def test_ranker_filters_closed_before_diversity_cap(payload):
    trip = request(payload, preferences=["Cafe"])
    places = [
        record(slug="a-closed", hours=[opening(0)], duration_minutes=60),
        record(slug="b-open", hours=[opening()], duration_minutes=60),
        record(slug="c-unknown", hours=None),
        record(slug="d-short", hours=[opening(closes="09:10")], duration_minutes=60),
    ]
    items, _ = rank_places(trip, places, 6)
    assert [item.place.slug for item in items] == ["b-open", "c-unknown"]
    assert items[0].timing.status == "fits_known_hours"
    assert items[1].timing.status == "unknown_hours"
    assert any("đủ thời lượng" in reason for reason in items[0].reasons)


def test_api_returns_time_windows_and_filters_known_closures(storage, payload):
    client, _, engine = storage
    user = uuid4()
    saved = create(client, user, payload)
    with Session(engine) as session, session.begin():
        import_batch(
            session,
            batch(
                poi("closed", hours=[opening(0)], duration_minutes=60),
                poi("open", hours=[opening()], duration_minutes=60),
            ),
        )
    response = client.get(f"/v1/trips/{saved['id']}/recommendations", headers=headers(user))
    assert response.status_code == 200
    items = response.json()["items"]
    assert [item["place"]["slug"] for item in items] == ["open"]
    assert items[0]["timing"]["windows"][0]["latest_start_at"] == "2026-11-07T16:00:00+07:00"
    assert response.json()["algorithm_version"] == "saved-trip-hours-v3"
