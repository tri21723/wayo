from uuid import uuid4

import pytest
from pydantic import ValidationError
from test_catalog import poi
from test_trip_storage import create, headers

from app.availability import available_days
from app.catalog import PlaceRecord
from app.recommendations import rank_places
from app.schemas import DaySchedule, TripRequest


def schedule(**changes):
    return {
        "starts_at": "10:00",
        "ends_at": "18:00",
        "breaks": [{"label": "Lunch", "starts_at": "12:00", "ends_at": "13:00"}],
        **changes,
    }


@pytest.mark.parametrize(
    "changes",
    [
        {"starts_at": "25:00"},
        {"starts_at": "9:00"},
        {"ends_at": "10:00"},
        {"ends_at": "08:00"},
        {"breaks": [{"label": "Lunch", "starts_at": "09:00", "ends_at": "11:00"}]},
        {"breaks": [{"label": "Lunch", "starts_at": "12:00", "ends_at": "12:00"}]},
        {
            "breaks": [
                {"label": "Lunch", "starts_at": "12:00", "ends_at": "13:00"},
                {"label": "Rest", "starts_at": "12:30", "ends_at": "14:00"},
            ]
        },
    ],
)
def test_invalid_schedule(changes):
    with pytest.raises(ValidationError):
        DaySchedule.model_validate(schedule(**changes))


def test_recurring_break_clipping_and_fixed_priority(payload):
    trip = TripRequest.model_validate(
        {
            **payload["trip"],
            "day_schedule": schedule(),
            "fixed_events": [
                {
                    "label": "Booking",
                    "starts_at": "2026-11-07T12:30:00+07:00",
                    "ends_at": "2026-11-07T13:30:00+07:00",
                },
            ],
        }
    )
    days = available_days(trip)
    assert [day.available_minutes for day in days] == [300, 390, 360]
    assert sum(block.minutes for day in days for block in day.blocks) == 53 * 60
    assert [(block.kind, block.minutes) for block in days[1].blocks] == [
        ("outside_activity_hours", 600),
        ("available", 120),
        ("rest", 30),
        ("fixed", 60),
        ("available", 270),
        ("outside_activity_hours", 360),
    ]


def test_break_prevents_visit_and_adjacent_breaks_allowed(payload):
    config = schedule(
        breaks=[
            {"label": "Lunch", "starts_at": "12:00", "ends_at": "13:00"},
            {"label": "Rest", "starts_at": "13:00", "ends_at": "14:00"},
        ]
    )
    trip = TripRequest.model_validate({**payload["trip"], "day_schedule": config})
    place = PlaceRecord.model_validate(
        poi(hours=[{"weekday": 5, "opens": "12:00", "closes": "14:00"}], duration_minutes=60)
    )
    assert rank_places(trip, [place], 6)[0] == []


def test_schedule_persistence_old_editor_clear_and_retry(storage, payload):
    client, _, _ = storage
    user = uuid4()
    payload["trip"]["day_schedule"] = schedule()
    saved = create(client, user, payload)
    url = f"/v1/trips/{saved['id']}"
    assert client.post("/v1/trips", headers=headers(user), json=payload).status_code == 200
    changed = {**payload, "trip": {**payload["trip"], "day_schedule": schedule(ends_at="19:00")}}
    assert client.post("/v1/trips", headers=headers(user), json=changed).status_code == 409
    legacy = {key: value for key, value in payload["trip"].items() if key != "day_schedule"}
    response = client.put(
        url,
        headers=headers(user),
        json={"title": "Updated", "trip": legacy, "expected_revision": 1},
    )
    assert response.status_code == 200
    assert response.json()["trip"]["day_schedule"] == schedule()
    response = client.put(
        url,
        headers=headers(user),
        json={
            "title": "Updated",
            "trip": {**legacy, "day_schedule": schedule(breaks=[])},
            "expected_revision": 2,
        },
    )
    assert response.status_code == 200
    assert client.get(url, headers=headers(user)).json()["trip"]["day_schedule"]["breaks"] == []
