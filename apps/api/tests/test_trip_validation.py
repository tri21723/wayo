from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def trip():
    return {
        "origin": "TP.HCM",
        "arrival_at": "2026-11-06T12:00:00+07:00",
        "departure_at": "2026-11-08T17:00:00+07:00",
        "people_count": 2,
        "group_type": "couple",
        "budget": {"amount_vnd": 4_000_000},
    }


def test_health_is_liveness_only():
    assert client.get("/health").json()["status"] == "ok"


def test_per_person_budget_and_missing_anchor_notice(trip):
    response = client.post("/v1/trips/validate", json=trip)
    assert response.status_code == 200
    body = response.json()
    assert body["trip_days"] == 3
    assert body["total_budget_vnd"] == 8_000_000
    assert body["status"] == "input_valid"
    assert "ANCHOR_REQUIRED_FOR_PLANNING" in {notice["code"] for notice in body["notices"]}


def test_group_budget_is_not_multiplied(trip):
    trip["budget"]["scope"] = "group"
    assert client.post("/v1/trips/validate", json=trip).json()["total_budget_vnd"] == 4_000_000


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("departure_at", "2026-11-05T17:00:00+07:00"),
        ("departure_at", "2026-11-06T17:00:00+07:00"),
        ("departure_at", "2026-11-10T17:00:00+07:00"),
        ("arrival_at", "2026-11-06T12:00:00"),
        ("people_count", 0),
        ("people_count", 3),
        ("people_count", True),
        ("destination_id", "nha-trang"),
        ("transport_mode", "motorcycle"),
        ("origin", "   "),
        ("unexpected", "private-input"),
    ],
)
def test_invalid_inputs_rejected_without_echoing_input(trip, field, value):
    trip[field] = value
    response = client.post("/v1/trips/validate", json=trip)
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert "private-input" not in response.text


def test_trip_days_use_vietnam_dates(trip):
    trip["arrival_at"] = "2026-11-06T18:00:00Z"  # Nov 7 in Vietnam
    trip["departure_at"] = "2026-11-08T17:30:00Z"  # Nov 9 in Vietnam
    assert client.post("/v1/trips/validate", json=trip).json()["trip_days"] == 3


def test_fixed_event_outside_trip_rejected(trip):
    trip["fixed_events"] = [
        {
            "label": "Ăn tối",
            "starts_at": "2026-11-09T18:00:00+07:00",
            "ends_at": "2026-11-09T19:00:00+07:00",
        }
    ]
    assert client.post("/v1/trips/validate", json=trip).status_code == 422


def test_overlapping_fixed_events_rejected(trip):
    event = {
        "label": "Ăn tối",
        "starts_at": "2026-11-07T18:00:00+07:00",
        "ends_at": "2026-11-07T19:00:00+07:00",
    }
    trip["fixed_events"] = [event, deepcopy(event)]
    assert client.post("/v1/trips/validate", json=trip).status_code == 422


def test_hard_budget_not_claimed_as_verified(trip):
    trip["budget"]["mode"] = "hard"
    response = client.post("/v1/trips/validate", json=trip).json()
    assert "BUDGET_NOT_ESTIMATED" in {notice["code"] for notice in response["notices"]}


def test_malformed_json_uses_error_contract():
    response = client.post(
        "/v1/trips/validate", content="{", headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_conflicting_preferences_rejected(trip):
    trip.update(preferences=["Trekking"], exclusions=["Trekking"])
    assert client.post("/v1/trips/validate", json=trip).status_code == 422
