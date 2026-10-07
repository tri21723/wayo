import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import jwt
import pytest
from alembic import command
from alembic.config import Config
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy import inspect, text

from app import auth
from app.database import engine_for
from app.main import app
from app.settings import get_settings

ISSUER = "https://test-project.supabase.co/auth/v1"
KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)


def token(user_id, **changes):
    now = datetime.now(UTC)
    claims = {
        "sub": str(user_id),
        "iss": ISSUER,
        "aud": "authenticated",
        "role": "authenticated",
        "iat": now,
        "exp": now + timedelta(minutes=5),
    }
    claims.update(changes)
    return jwt.encode(claims, KEY, algorithm="RS256", headers={"kid": "test-key"})


def headers(user_id, **changes):
    return {"Authorization": f"Bearer {token(user_id, **changes)}"}


@pytest.fixture
def storage(tmp_path, monkeypatch):
    url = os.environ.get("WAYO_TEST_DATABASE_URL", f"sqlite:///{tmp_path}/trips.db")
    if not url.startswith("sqlite:") and not url.split("?")[0].endswith("_test"):
        raise RuntimeError("Storage tests require a disposable database ending in _test.")
    monkeypatch.setenv("WAYO_DATABASE_URL", url)
    monkeypatch.setenv("WAYO_SUPABASE_URL", "https://test-project.supabase.co")
    get_settings.cache_clear()
    monkeypatch.setattr(
        auth,
        "signing_keys",
        lambda _issuer: SimpleNamespace(
            get_signing_key_from_jwt=lambda _token: SimpleNamespace(key=KEY.public_key())
        ),
    )
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    command.upgrade(config, "head")
    with TestClient(app) as client:
        yield client, config, engine_for(url)
    command.downgrade(config, "base")
    engine_for(url).dispose()
    engine_for.cache_clear()
    get_settings.cache_clear()


@pytest.fixture
def payload():
    return {
        "request_id": str(uuid4()),
        "title": "Đà Lạt cuối tuần",
        "trip": {
            "origin": "TP.HCM",
            "arrival_at": "2026-11-06T12:00:00+07:00",
            "departure_at": "2026-11-08T17:00:00+07:00",
            "people_count": 2,
            "group_type": "couple",
            "budget": {"amount_vnd": 4_000_000},
        },
    }


def create(client, user_id, payload):
    response = client.post("/v1/trips", headers=headers(user_id), json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_crud_persists_across_requests_and_sessions(storage, payload):
    client, _, engine = storage
    user = uuid4()
    trip = create(client, user, payload)
    engine.dispose()  # Subsequent request must read persisted data through a fresh connection.
    assert client.get(f"/v1/trips/{trip['id']}", headers=headers(user)).json() == trip
    response = client.put(
        f"/v1/trips/{trip['id']}",
        headers=headers(user),
        json={
            "title": "Tên mới",
            "trip": payload["trip"],
            "expected_revision": 1,
        },
    )
    assert response.status_code == 200
    assert response.json()["revision"] == 2
    listing = client.get("/v1/trips", headers=headers(user)).json()
    assert listing["total"] == 1
    assert listing["items"][0]["title"] == "Tên mới"
    assert (
        client.delete(
            f"/v1/trips/{trip['id']}?expected_revision=2", headers=headers(user)
        ).status_code
        == 204
    )
    assert client.get(f"/v1/trips/{trip['id']}", headers=headers(user)).status_code == 404


def test_other_user_cannot_read_update_delete_or_list(storage, payload):
    client, _, _ = storage
    owner, other = uuid4(), uuid4()
    trip = create(client, owner, payload)
    path = f"/v1/trips/{trip['id']}"
    assert client.get(path, headers=headers(other)).status_code == 404
    assert (
        client.put(
            path,
            headers=headers(other),
            json={
                "title": "Hijack",
                "trip": payload["trip"],
                "expected_revision": 1,
            },
        ).status_code
        == 404
    )
    assert client.delete(path + "?expected_revision=1", headers=headers(other)).status_code == 404
    assert client.get("/v1/trips", headers=headers(other)).json()["total"] == 0
    assert client.get(path, headers=headers(owner)).json()["revision"] == 1


def test_stale_update_and_delete_are_rejected(storage, payload):
    client, _, _ = storage
    user = uuid4()
    trip = create(client, user, payload)
    path = f"/v1/trips/{trip['id']}"
    update = {"title": "New version", "trip": payload["trip"], "expected_revision": 1}
    assert client.put(path, headers=headers(user), json=update).status_code == 200
    assert (
        client.put(path, headers=headers(user), json=update).json()["code"] == "REVISION_CONFLICT"
    )
    assert client.delete(path + "?expected_revision=1", headers=headers(user)).status_code == 409
    assert client.get(path, headers=headers(user)).json()["revision"] == 2


def test_idempotent_create_and_conflicting_request_key(storage, payload):
    client, _, _ = storage
    user = uuid4()
    trip = create(client, user, payload)
    replay = client.post("/v1/trips", headers=headers(user), json=payload)
    assert replay.status_code == 200
    assert replay.json()["id"] == trip["id"]
    changed = {**payload, "title": "Different payload"}
    assert client.post("/v1/trips", headers=headers(user), json=changed).status_code == 409
    assert client.get("/v1/trips", headers=headers(user)).json()["total"] == 1
    assert create(client, uuid4(), payload)["id"] != trip["id"]


def test_no_auth_and_owner_injection(storage, payload):
    client, _, _ = storage
    assert client.get("/v1/trips").status_code == 401
    assert client.post("/v1/trips", json=payload).status_code == 401
    payload["owner_id"] = str(uuid4())
    assert client.post("/v1/trips", headers=headers(uuid4()), json=payload).status_code == 422


@pytest.mark.parametrize(
    "claims",
    [
        {"exp": datetime.now(UTC) - timedelta(minutes=1)},
        {"iss": "https://other.supabase.co/auth/v1"},
        {"aud": "wrong-audience"},
        {"role": "service_role"},
        {"is_anonymous": True},
        {"sub": "not-a-uuid"},
    ],
)
def test_invalid_claims_denied(storage, claims):
    client, _, _ = storage
    assert client.get("/v1/trips", headers=headers(uuid4(), **claims)).status_code == 401


def test_tampered_signature_and_disallowed_algorithm(storage):
    client, _, _ = storage
    other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    claims = jwt.decode(token(uuid4()), options={"verify_signature": False})
    forged = jwt.encode(claims, other_key, algorithm="RS256", headers={"kid": "test-key"})
    assert client.get("/v1/trips", headers={"Authorization": f"Bearer {forged}"}).status_code == 401
    legacy = jwt.encode(
        claims,
        "long-test-secret-which-is-not-a-production-secret",
        algorithm="HS256",
        headers={"kid": "test-key"},
    )
    assert client.get("/v1/trips", headers={"Authorization": f"Bearer {legacy}"}).status_code == 401


def test_invalid_update_does_not_change_data(storage, payload):
    client, _, _ = storage
    user = uuid4()
    trip = create(client, user, payload)
    payload["trip"]["people_count"] = 0
    response = client.put(
        f"/v1/trips/{trip['id']}",
        headers=headers(user),
        json={
            "title": "Bad",
            "trip": payload["trip"],
            "expected_revision": 1,
        },
    )
    assert response.status_code == 422
    assert client.get(f"/v1/trips/{trip['id']}", headers=headers(user)).json() == trip


def test_list_pagination_and_limits(storage, payload):
    client, _, _ = storage
    user = uuid4()
    for index in range(3):
        create(client, user, {**payload, "request_id": str(uuid4()), "title": str(index)})
    first = client.get("/v1/trips?limit=2", headers=headers(user)).json()
    second = client.get("/v1/trips?limit=2&offset=2", headers=headers(user)).json()
    assert first["total"] == 3 and len(first["items"]) == 2 and len(second["items"]) == 1
    assert not ({row["id"] for row in first["items"]} & {row["id"] for row in second["items"]})
    assert client.get("/v1/trips?limit=101", headers=headers(user)).status_code == 422


def test_migration_matches_tables_and_postgres_rls(storage):
    _, _, engine = storage
    namespace = "wayo" if engine.dialect.name == "postgresql" else None
    assert {"users", "trips", "travel_profiles", "places"} <= set(
        inspect(engine).get_table_names(schema=namespace)
    )
    if namespace:
        with engine.connect() as connection:
            assert (
                connection.execute(
                    text(
                        "SELECT count(*) FROM pg_class c "
                        "JOIN pg_namespace n ON n.oid=c.relnamespace "
                        "WHERE n.nspname='wayo' AND c.relrowsecurity"
                    )
                ).scalar()
                == 4
            )


def test_missing_expiry_and_malformed_jwt_denied(storage):
    client, _, _ = storage
    claims = jwt.decode(token(uuid4()), options={"verify_signature": False})
    del claims["exp"]
    no_exp = jwt.encode(claims, KEY, algorithm="RS256", headers={"kid": "test-key"})
    for invalid in (no_exp, "not-a-token"):
        assert (
            client.get("/v1/trips", headers={"Authorization": f"Bearer {invalid}"}).status_code
            == 401
        )


def test_jwks_failure_returns_unavailable_not_authenticated(storage, monkeypatch):
    client, _, _ = storage

    def offline(_issuer):
        raise jwt.PyJWKClientConnectionError("Private network failure")

    monkeypatch.setattr(auth, "signing_keys", offline)
    response = client.get("/v1/trips", headers=headers(uuid4()))
    assert response.status_code == 503
    assert response.json()["code"] == "AUTH_UNAVAILABLE"
    assert "Private network failure" not in response.text


def test_es256_signature_is_supported(storage, monkeypatch):
    from cryptography.hazmat.primitives.asymmetric import ec

    client, _, _ = storage
    key = ec.generate_private_key(ec.SECP256R1())
    claims = jwt.decode(token(uuid4()), options={"verify_signature": False})
    signed = jwt.encode(claims, key, algorithm="ES256", headers={"kid": "ec-key"})
    monkeypatch.setattr(
        auth,
        "signing_keys",
        lambda _issuer: SimpleNamespace(
            get_signing_key_from_jwt=lambda _token: SimpleNamespace(key=key.public_key())
        ),
    )
    assert client.get("/v1/trips", headers={"Authorization": f"Bearer {signed}"}).status_code == 200


def test_reapplying_migration_keeps_existing_data(storage, payload):
    client, config, _ = storage
    user = uuid4()
    trip = create(client, user, payload)
    command.upgrade(config, "head")
    assert client.get(f"/v1/trips/{trip['id']}", headers=headers(user)).json() == trip


def test_profile_roundtrip_isolation_and_conflicts(storage, payload):
    client, config, engine = storage
    user, other = uuid4(), uuid4()
    answers = {
        "interests": ["nature", "cafe"],
        "pace": "relaxed",
        "crowd": "quiet",
        "adventure": "easy",
        "diet": "vegan",
        "exclusions": ["trekking", "stairs"],
    }
    path = "/v1/profile"
    assert client.get(path).status_code == 401
    assert client.put(path, json={}).status_code == 401
    assert client.get(path, headers=headers(user)).json()["answers"] is None
    body = {"expected_revision": 0, "answers": answers}
    response = client.put(path, headers=headers(user), json=body)
    assert response.status_code == 200, response.text
    saved = response.json()
    assert saved["revision"] == 1 and saved["schema_version"] == 1
    assert saved["vector"] == {
        "cafe": 1,
        "nature": 1,
        "photography": 0,
        "food": 0,
        "culture": 0,
        "nightlife": 0,
    }
    engine.dispose()
    command.upgrade(config, "head")
    if engine.dialect.name == "postgresql":
        command.check(config)
    assert client.get(path, headers=headers(user)).json() == saved
    assert client.get(path, headers=headers(other)).json()["revision"] == 0
    assert client.put(path, headers=headers(user), json=body).status_code == 409
    assert (
        client.put(path, headers=headers(other), json={**body, "expected_revision": 1}).status_code
        == 409
    )
    trip = create(client, user, payload)
    changed = client.put(
        path,
        headers=headers(user),
        json={
            "expected_revision": 1,
            "answers": {**answers, "diet": "unrestricted", "exclusions": []},
        },
    )
    assert changed.status_code == 200 and changed.json()["revision"] == 2
    assert changed.json()["vector"] == saved["vector"]
    assert (
        client.put(path, headers=headers(user), json={**body, "expected_revision": 1}).status_code
        == 409
    )
    assert client.get(f"/v1/trips/{trip['id']}", headers=headers(user)).json() == trip


@pytest.mark.parametrize(
    "invalid",
    [
        {"interests": []},
        {"interests": ["nature", "nature"]},
        {"interests": ["unknown"]},
        {"pace": "fast"},
        {"diet": "unknown"},
        {"exclusions": ["stairs", "stairs"]},
        {"exclusions": ["unknown"]},
        {"owner_id": "injected"},
    ],
)
def test_profile_invalid_answers_never_persist(storage, invalid):
    client, _, _ = storage
    user = uuid4()
    answers = {
        "interests": ["nature"],
        "pace": "balanced",
        "crowd": "neutral",
        "adventure": "easy",
        "diet": "unrestricted",
        "exclusions": [],
    }
    response = client.put(
        "/v1/profile",
        headers=headers(user),
        json={
            "expected_revision": 0,
            "answers": {**answers, **invalid},
        },
    )
    assert response.status_code == 422
    assert client.get("/v1/profile", headers=headers(user)).json()["revision"] == 0


def test_profile_migration_preserves_existing_trips(storage, payload):
    client, config, _ = storage
    command.downgrade(config, "0001")
    user = uuid4()
    saved = create(client, user, payload)
    command.upgrade(config, "head")
    assert client.get(f"/v1/trips/{saved['id']}", headers=headers(user)).json() == saved
    assert client.get("/v1/profile", headers=headers(user)).json()["revision"] == 0
