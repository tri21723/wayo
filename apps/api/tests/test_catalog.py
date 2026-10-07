import json
import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from test_trip_storage import create, headers

from app.catalog import CatalogBatch, PlaceRecord, import_batch, verified_places
from app.models import Place
from app.recommendations import rank_places
from app.schemas import TripRequest


def poi(slug="test-cafe", **changes):
    return {
        "slug": slug,
        "name": "Synthetic test POI " + slug,
        "address": "Synthetic fixture address",
        "category": "cafe",
        "latitude": 11.94,
        "longitude": 108.44,
        "tags": ["cafe", "photography"],
        "status": "verified",
        "trekking": False,
        "sources": [
            {
                "url": "https://example.org/test-fixture",
                "checked_at": (datetime.now(UTC) - timedelta(days=1)).isoformat(),
                "fields": [
                    "identity",
                    "coordinates",
                    "tags",
                    "access",
                    "price",
                    "hours",
                    "duration",
                ],
                "note": "Synthetic fixture only. Not a real venue or source.",
            }
        ],
        **changes,
    }


def batch(*records):
    return CatalogBatch.model_validate({"places": records})


def test_catalog_upsert_rollback_and_freshness(storage):
    _, config, engine = storage
    stale = poi("old")
    stale["sources"][0]["checked_at"] = (datetime.now(UTC) - timedelta(days=91)).isoformat()
    with Session(engine) as session, session.begin():
        assert import_batch(session, batch(poi(), poi("draft", status="draft"), stale)) == {
            "created": 3,
            "updated": 0,
        }
    with Session(engine) as session, session.begin():
        assert import_batch(session, batch(poi(name="Updated name"))) == {
            "created": 0,
            "updated": 1,
        }
    with pytest.raises(ValueError), Session(engine) as session, session.begin():
        import_batch(session, batch(poi("duplicate", name="  UPDATED   name  ")))
    with pytest.raises(RuntimeError), Session(engine) as session, session.begin():
        import_batch(session, batch(poi("rolled-back")))
        raise RuntimeError("Simulated failed batch")
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(Place)) == 3
        records = verified_places(session)
        assert len(records) == 1 and records[0].name == "Updated name"
    if engine.dialect.name == "postgresql":
        command.check(config)


@pytest.mark.parametrize(
    "change",
    [
        {"latitude": 91},
        {"longitude": float("nan")},
        {"slug": "../bad"},
        {"tags": ["cafe", "cafe"]},
        {"price": {"min_vnd": 200, "max_vnd": 100, "unit": "group"}},
        {"hours": [{"weekday": 0, "opens": "20:00", "closes": "09:00"}]},
        {
            "hours": [
                {"weekday": 1, "opens": "08:00", "closes": "12:00"},
                {"weekday": 1, "opens": "11:00", "closes": "13:00"},
            ]
        },
        {"sources": []},
        {"trekking": "false"},
    ],
)
def test_invalid_catalog_records_rejected(change):
    with pytest.raises(ValidationError):
        batch(poi(**change))


def test_evidence_and_duplicate_checks():
    record = poi()
    record["sources"][0]["fields"] = ["identity"]
    with pytest.raises(ValidationError):
        batch(record)
    record = poi()
    record["sources"][0]["checked_at"] = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    with pytest.raises(ValidationError):
        batch(record)
    record = poi()
    record["sources"][0]["url"] = "javascript:alert(1)"
    with pytest.raises(ValidationError):
        batch(record)
    with pytest.raises(ValidationError):
        batch(poi(), poi())
    with pytest.raises(ValidationError):
        batch(poi("one", name="Same"), poi("two", name="same"))


def test_ranker_deterministic_exclusions_and_diversity(payload):
    trip = TripRequest.model_validate(
        {**payload["trip"], "preferences": ["Cafe", "Chụp ảnh"], "exclusions": ["Trekking"]}
    )
    places = [
        PlaceRecord.model_validate(record)
        for record in [
            poi("closed", hours=[]),
            poi("z"),
            poi("b"),
            poi("a"),
            poi("unsafe", trekking=True),
            poi("unknown", trekking=None),
            poi("nature", category="nature", tags=["nature"]),
        ]
    ]
    items, _ = rank_places(trip, places, 6)
    reversed_items, _ = rank_places(trip, list(reversed(places)), 6)
    assert [item.place.slug for item in items] == ["a", "b", "nature"]
    assert items == reversed_items
    assert items[0].matched_interests == ["cafe", "photography"]
    assert any("khoảng giá" in warning for warning in items[0].warnings)
    blocked = trip.model_copy(update={"exclusions": ["Lịch quá dày"]})
    items, notices = rank_places(blocked, places, 6)
    assert not items and any(item.code == "UNSUPPORTED_EXCLUSIONS" for item in notices)
    tagged = trip.model_copy(update={"exclusions": ["Cafe"]})
    items, _ = rank_places(tagged, places, 6)
    assert [item.place.slug for item in items] == ["nature"]


def test_hard_budget_uses_group_cost_and_unknown_access_fails_closed(payload):
    trip = TripRequest.model_validate(
        {
            **payload["trip"],
            "budget": {"amount_vnd": 100, "scope": "group", "mode": "hard"},
            "exclusions": ["Nơi đông người"],
        }
    )

    def place(slug, price, **rest):
        return PlaceRecord.model_validate(poi(slug, price=price, **rest))

    places = [
        place("unknown-price", None, crowd="quiet"),
        place("unknown-crowd", {"min_vnd": 1, "max_vnd": 20, "unit": "group"}),
        place("expensive", {"min_vnd": 40, "max_vnd": 60, "unit": "per_person"}, crowd="quiet"),
        place("okay", {"min_vnd": 30, "max_vnd": 50, "unit": "per_person"}, crowd="quiet"),
    ]
    items, _ = rank_places(trip, places, 6)
    assert [item.place.slug for item in items] == ["okay"]
    assert any("chưa đảm bảo" in warning for warning in items[0].warnings)


def test_recommendation_endpoint_owner_scope_and_empty_state(storage, payload):
    client, _, engine = storage
    owner = uuid4()
    trip = create(client, owner, payload)
    url = f"/v1/trips/{trip['id']}/recommendations"
    assert client.get(url).status_code == 401
    assert client.get(url, headers=headers(uuid4())).status_code == 404
    empty = client.get(url, headers=headers(owner))
    assert empty.status_code == 200 and empty.json()["items"] == []
    with Session(engine) as session, session.begin():
        import_batch(session, batch(poi()))
    response = client.get(url, headers=headers(owner)).json()
    assert response["trip_revision"] == 1
    assert response["items"][0]["place"]["slug"] == "test-cafe"
    assert client.get(url + "?limit=0", headers=headers(owner)).status_code == 422
    assert client.get(url + "?limit=13", headers=headers(owner)).status_code == 422
    with Session(engine) as session, session.begin():
        import_batch(session, batch(poi(status="disabled")))
    assert client.get(url, headers=headers(owner)).json()["items"] == []


def test_cli_dry_run_never_connects_and_rejects_invalid_batch(tmp_path):
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps({"places": [poi()]}))
    script = Path(__file__).resolve().parents[1] / "scripts/import_places.py"
    env = {**os.environ, "WAYO_DATABASE_URL": "postgresql+psycopg://invalid.invalid/unused"}
    result = subprocess.run(
        [sys.executable, str(script), str(path)],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0 and "no database writes" in result.stdout
    path.write_text(json.dumps({"places": [poi(), poi()]}))
    result = subprocess.run(
        [sys.executable, str(script), str(path), "--apply"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1 and "Duplicate" in result.stdout
    assert "invalid.invalid" not in result.stdout


def test_catalog_migration_preserves_profile_and_trip(storage, payload):
    client, config, _ = storage
    command.downgrade(config, "0002")
    user = uuid4()
    trip = create(client, user, payload)
    profile = client.put(
        "/v1/profile",
        headers=headers(user),
        json={
            "expected_revision": 0,
            "answers": {
                "interests": ["cafe"],
                "pace": "relaxed",
                "crowd": "quiet",
                "adventure": "easy",
                "diet": "unrestricted",
                "exclusions": [],
            },
        },
    )
    assert profile.status_code == 200
    command.upgrade(config, "head")
    assert client.get(f"/v1/trips/{trip['id']}", headers=headers(user)).json() == trip
    assert client.get("/v1/profile", headers=headers(user)).json() == profile.json()
