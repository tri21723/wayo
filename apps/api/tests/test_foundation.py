import json
import logging
from uuid import UUID, uuid4

import pytest
from alembic import command
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from test_trip_storage import headers

from app.main import app
from app.observability import RequestLogging, logger
from app.settings import Settings, get_settings


def test_admin_allowlist_and_metadata_cannot_grant_admin(storage, monkeypatch):
    client, _, _ = storage
    admin, regular = uuid4(), uuid4()
    monkeypatch.setenv("WAYO_ADMIN_USER_IDS", json.dumps([str(admin)]))
    get_settings.cache_clear()
    assert client.get("/v1/admin/status").status_code == 401
    for metadata in ({"user_metadata": {"role": "admin"}}, {"app_metadata": {"role": "admin"}}):
        assert (
            client.get("/v1/admin/status", headers=headers(regular, **metadata)).status_code == 403
        )
    response = client.get("/v1/admin/status", headers=headers(admin))
    assert response.status_code == 200
    assert response.json() == {"role": "admin", "environment": "local"}
    monkeypatch.setenv("WAYO_ADMIN_USER_IDS", "[]")
    get_settings.cache_clear()
    assert client.get("/v1/admin/status", headers=headers(admin)).status_code == 403


def test_readiness_checks_migration_and_never_changes_database(storage):
    client, config, _ = storage
    assert client.get("/health").status_code == 200
    assert client.get("/ready").json() == {
        "status": "ready",
        "database": "ready",
        "migrations": "current",
        "auth": "configured",
    }
    command.downgrade(config, "0002")
    response = client.get("/ready")
    assert response.status_code == 503 and response.json()["code"] == "MIGRATIONS_PENDING"
    assert client.get("/health").status_code == 200
    command.upgrade(config, "head")
    assert client.get("/ready").status_code == 200


def test_missing_readiness_config_is_redacted(monkeypatch):
    monkeypatch.setattr("app.operations.get_settings", lambda: Settings(_env_file=None))
    with TestClient(app) as client:
        assert client.get("/ready").status_code == 503


def test_request_logs_and_id_do_not_include_private_input(storage, caplog):
    client, _, _ = storage
    logger.addHandler(caplog.handler)
    try:
        with caplog.at_level(logging.INFO):
            response = client.get(
                "/v1/trips?secret=private-query",
                headers={
                    "Authorization": "Bearer secret-token",
                    "X-Request-ID": "untrusted-private-id",
                },
            )
            assert response.status_code == 401
            request_id = response.headers["X-Request-ID"]
            UUID(request_id)
            assert response.headers["Cache-Control"] == "no-store"
            client.get("/private-path-that-must-not-be-logged")
        records = [
            json.loads(record.message) for record in caplog.records if record.name == logger.name
        ]
        assert any(
            record["request_id"] == request_id and record["route"] == "/v1/trips"
            for record in records
        )
        assert all(
            "private" not in json.dumps(record) and "secret-token" not in json.dumps(record)
            for record in records
        )
        assert records[-1]["route"] == "unmatched"
    finally:
        logger.removeHandler(caplog.handler)


def test_request_body_limit_for_chunked_input(storage):
    client, _, _ = storage
    response = client.post("/v1/trips/validate", content=iter([b" " * 40_000, b" " * 40_000]))
    assert response.status_code == 413
    assert response.json()["code"] == "PAYLOAD_TOO_LARGE"
    assert "X-Request-ID" in response.headers


def test_unexpected_exception_is_redacted_and_correlated():
    test_app = FastAPI()
    test_app.add_middleware(RequestLogging)

    @test_app.get("/broken")
    def broken():
        raise RuntimeError("postgres://private-password secret-token")

    with TestClient(test_app) as client:
        response = client.get("/broken")
    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"
    assert "private-password" not in response.text
    assert response.headers["X-Request-ID"]


@pytest.mark.parametrize(
    "changes",
    [
        {"database_url": "sqlite:///private.db"},
        {"database_url": "postgresql+psycopg://u:private-password@db/wayo"},
        {"supabase_url": "http://supabase.example"},
        {"weather_base_url": "http://weather.example"},
    ],
)
def test_deployment_config_fails_closed_without_exposing_secrets(changes):
    config = {
        "environment": "staging",
        "database_url": "postgresql+psycopg://u:private-password@db/wayo?sslmode=require",
        "supabase_url": "https://auth.example",
        **changes,
    }
    with pytest.raises(ValidationError) as caught:
        Settings(_env_file=None, **config)
    assert "private-password" not in str(caught.value)


def test_provider_defaults_disabled_and_secrets_hidden():
    settings = Settings(_env_file=None, llm_api_key="private-key", database_url="private-db")
    assert settings.providers_enabled == []
    assert "private-key" not in repr(settings) and "private-db" not in repr(settings)
