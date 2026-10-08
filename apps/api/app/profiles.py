"""Explicit, versioned travel preferences; hard constraints never become scores."""

from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.auth import UserId
from app.database import Database
from app.errors import api_error
from app.models import TravelProfile, User
from app.schemas import ApiError
from app.taste import TasteAnswers, taste_vector


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=0, strict=True)
    answers: TasteAnswers


class SavedProfile(BaseModel):
    schema_version: Literal[1] = 1
    revision: int = 0
    answers: TasteAnswers | None = None
    vector: dict[str, float] = Field(default_factory=dict)
    updated_at: datetime | None = None


def serialize(row: TravelProfile | None) -> SavedProfile:
    if row is None:
        return SavedProfile()
    answers = TasteAnswers.model_validate(row.answers)
    return SavedProfile(
        revision=row.revision,
        answers=answers,
        vector=taste_vector(answers),
        updated_at=row.updated_at.replace(tzinfo=UTC)
        if row.updated_at.tzinfo is None
        else row.updated_at,
    )


router = APIRouter(
    prefix="/v1/profile",
    tags=["Profile"],
    responses={status: {"model": ApiError} for status in (401, 409, 422, 503)},
)


@router.get("", response_model=SavedProfile, operation_id="getProfile")
def get_profile(user_id: UserId, session: Database):
    return serialize(session.get(TravelProfile, user_id))


@router.put("", response_model=SavedProfile, operation_id="saveProfile")
def save_profile(payload: ProfileUpdate, user_id: UserId, session: Database):
    now = datetime.now(UTC)
    insert = sqlite_insert if session.bind.dialect.name == "sqlite" else pg_insert
    if payload.expected_revision == 0:
        session.execute(insert(User).values(id=user_id, created_at=now).on_conflict_do_nothing())
        result = session.execute(
            insert(TravelProfile)
            .values(
                owner_id=user_id,
                answers=payload.answers.model_dump(mode="json"),
                schema_version=1,
                revision=1,
                updated_at=now,
            )
            .on_conflict_do_nothing()
            .returning(TravelProfile.owner_id)
        )
    else:
        result = session.execute(
            update(TravelProfile)
            .where(
                TravelProfile.owner_id == user_id,
                TravelProfile.revision == payload.expected_revision,
            )
            .values(
                answers=payload.answers.model_dump(mode="json"),
                revision=TravelProfile.revision + 1,
                updated_at=now,
            )
            .returning(TravelProfile.owner_id)
        )
    if result.scalar_one_or_none() is None:
        session.rollback()
        raise api_error(
            409, "REVISION_CONFLICT", "Sở thích đã thay đổi. Hãy tải lại trước khi lưu."
        )
    session.commit()
    return serialize(session.get(TravelProfile, user_id))
