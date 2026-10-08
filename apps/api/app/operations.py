"""Minimal operational endpoints; probes never call external providers."""

from pathlib import Path
from typing import Literal

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from fastapi import APIRouter
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from app.auth import AdminId
from app.database import engine_for
from app.errors import api_error
from app.models import Place, TravelProfile, Trip, User
from app.schemas import ApiError, Contract
from app.settings import get_settings

router = APIRouter(tags=["Operations"])


class Readiness(Contract):
    status: Literal["ready"] = "ready"
    database: Literal["ready"] = "ready"
    migrations: Literal["current"] = "current"
    auth: Literal["configured"] = "configured"


class AdminStatus(Contract):
    role: Literal["admin"] = "admin"
    environment: Literal["local", "staging", "production"]


@router.get("/ready", response_model=Readiness, responses={503: {"model": ApiError}})
def ready() -> Readiness:
    settings = get_settings()
    if not settings.database_url or not settings.supabase_url:
        raise api_error(503, "NOT_READY", "Database hoặc đăng nhập chưa được cấu hình.")
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    expected = set(ScriptDirectory.from_config(config).get_heads())
    try:
        with engine_for(settings.database_url).connect() as connection:
            connection.execute(text("SELECT 1"))
            current = set(MigrationContext.configure(connection).get_current_heads())
            if current != expected:
                raise api_error(503, "MIGRATIONS_PENDING", "Database chưa ở migration hiện hành.")
            for model in (User, Trip, TravelProfile, Place):
                connection.execute(select(model).limit(0))
    except SQLAlchemyError as exc:
        raise api_error(503, "NOT_READY", "Database chưa sẵn sàng.") from exc
    return Readiness()


@router.get(
    "/v1/admin/status",
    response_model=AdminStatus,
    responses={status: {"model": ApiError} for status in (401, 403, 503)},
)
def admin_status(_admin: AdminId) -> AdminStatus:
    return AdminStatus(environment=get_settings().environment)
