import hashlib
import json
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session
from test_catalog import poi
from test_trip_storage import headers

from app.catalog import PlaceRecord
from app.models import Trip
from app.recommendations import rank_places
from app.schemas import TripCreate, TripRequest


def answers(**changes):
    return {
        "interests": ["cafe"],
        "pace": "relaxed",
        "crowd": "quiet",
        "adventure": "easy",
        "diet": "vegan",
        "exclusions": ["stairs"],
        **changes,
    }


def save_profile(client, user, revision=0, **changes):
    response = client.put(
        "/v1/profile",
        headers=headers(user),
        json={"expected_revision": revision, "answers": answers(**changes)},
    )
    assert response.status_code == 200, response.text
    profile = response.json()
    return {
        "schema_version": 1,
        "profile_revision": profile["revision"],
        "answers": profile["answers"],
    }


def test_snapshot_survives_profile_changes_and_trip_overrides(storage, payload):
    client, _, _ = storage
    user = uuid4()
    snapshot = save_profile(client, user)
    payload["trip"].update(
        taste_snapshot=snapshot,
        diet="vegan",
        preferences=["Cafe"],
        exclusions=["stairs"],
        crowd="quiet",
        adventure="easy",
    )
    created = client.post("/v1/trips", headers=headers(user), json=payload)
    assert created.status_code == 201
    trip = created.json()
    newer = save_profile(client, user, 1, interests=["nature"], diet="unrestricted")
    url = f"/v1/trips/{trip['id']}"
    assert client.get(url, headers=headers(user)).json() == trip
    # Retrying a successful create still works even after profile changes.
    assert client.post("/v1/trips", headers=headers(user), json=payload).status_code == 200
    edited = {**trip["trip"], "diet": "vegetarian", "preferences": ["Văn hóa"], "exclusions": []}
    response = client.put(
        url,
        headers=headers(user),
        json={"title": trip["title"], "trip": edited, "expected_revision": 1},
    )
    assert response.status_code == 200
    assert response.json()["trip"]["taste_snapshot"] == snapshot
    assert response.json()["trip"]["diet"] == "vegetarian"
    assert client.get("/v1/profile", headers=headers(user)).json()["answers"] == newer["answers"]
    # Explicit reapply may replace provenance with the owner's current profile.
    edited["taste_snapshot"] = newer
    response = client.put(
        url,
        headers=headers(user),
        json={"title": trip["title"], "trip": edited, "expected_revision": 2},
    )
    assert response.status_code == 200 and response.json()["trip"]["taste_snapshot"] == newer
    assert (
        client.put(
            url,
            headers=headers(user),
            json={"title": trip["title"], "trip": edited, "expected_revision": 2},
        ).status_code
        == 409
    )

    # An older editor cannot silently clear new fields it does not send.
    legacy = {
        key: value
        for key, value in edited.items()
        if key not in ("taste_snapshot", "diet", "crowd", "adventure", "day_schedule")
    }
    response = client.put(
        url,
        headers=headers(user),
        json={"title": trip["title"], "trip": legacy, "expected_revision": 3},
    )
    assert response.status_code == 200
    assert response.json()["trip"]["taste_snapshot"] == newer
    assert response.json()["trip"]["diet"] == "vegetarian"


def test_new_snapshot_requires_current_owners_answers(storage, payload):
    client, _, _ = storage
    user = uuid4()
    snapshot = save_profile(client, user)
    payload["trip"]["taste_snapshot"] = snapshot
    assert client.post("/v1/trips", headers=headers(uuid4()), json=payload).status_code == 409
    forged = {**snapshot, "answers": {**snapshot["answers"], "diet": "vegetarian"}}
    payload["trip"]["taste_snapshot"] = forged
    assert client.post("/v1/trips", headers=headers(user), json=payload).status_code == 409
    save_profile(client, user, 1, interests=["food"])
    payload["trip"]["taste_snapshot"] = snapshot
    response = client.post("/v1/trips", headers=headers(user), json=payload)
    assert response.status_code == 409 and response.json()["code"] == "PROFILE_CHANGED"
    assert client.get("/v1/trips", headers=headers(user)).json()["total"] == 0


def test_legacy_create_hash_replay_and_defaults(storage, payload):
    client, _, engine = storage
    user = uuid4()
    response = client.post("/v1/trips", headers=headers(user), json=payload)
    assert response.status_code == 201
    created = response.json()
    data = TripCreate.model_validate(payload).model_dump(mode="json", exclude={"request_id"})
    for key in ("taste_snapshot", "diet", "crowd", "adventure", "day_schedule"):
        del data["trip"][key]
    old_hash = hashlib.sha256(
        json.dumps(data, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()
    with Session(engine) as session, session.begin():
        row = session.get(Trip, UUID(created["id"]))
        row.create_hash = old_hash
        row.trip_data = data["trip"]
    replay = client.post("/v1/trips", headers=headers(user), json=payload)
    assert replay.status_code == 200
    assert replay.json()["trip"]["taste_snapshot"] is None
    assert replay.json()["trip"]["diet"] == "unrestricted"


def test_diet_requires_evidence_and_filters_only_food_venues(payload):
    record = poi(dietary_options=["vegan"])
    with pytest.raises(ValidationError):
        PlaceRecord.model_validate(record)

    def food(slug, options):
        value = poi(slug, dietary_options=options)
        value["sources"][0]["fields"].append("diet")
        return PlaceRecord.model_validate(value)

    places = [
        food("vegan", ["vegan"]),
        food("vegetarian", ["vegetarian"]),
        food("unknown", None),
        PlaceRecord.model_validate(poi("park", category="nature", tags=["nature"])),
    ]
    trip = TripRequest.model_validate({**payload["trip"], "diet": "vegan"})
    result, _ = rank_places(trip, places, 6)
    assert {item.place.slug for item in result} == {"vegan", "park"}
    result, _ = rank_places(trip.model_copy(update={"diet": "vegetarian"}), places, 6)
    assert {item.place.slug for item in result} == {"vegan", "vegetarian", "park"}


def test_context_breaks_interest_ties_without_weakening_exclusions(payload):
    trip = TripRequest.model_validate(
        {
            **payload["trip"],
            "preferences": ["Cafe"],
            "crowd": "quiet",
            "adventure": "easy",
            "exclusions": ["stairs"],
        }
    )
    places = [
        PlaceRecord.model_validate(poi(slug, crowd=crowd, effort=effort, stairs=stairs))
        for slug, crowd, effort, stairs in [
            ("a", None, None, False),
            ("b", "quiet", "easy", True),
            ("c", "quiet", "easy", False),
            ("d", "quiet", None, False),
        ]
    ]
    result, _ = rank_places(trip, places, 6)
    assert [item.place.slug for item in result] == ["c", "d"]
    assert len(result[0].matched_context) == 2
