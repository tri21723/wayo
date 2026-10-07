import hashlib
import json
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Query, Response
from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import IntegrityError

from app.auth import UserId
from app.database import Database
from app.errors import api_error
from app.models import Trip, User
from app.schemas import ApiError, SavedTrip, TripCreate, TripList, TripUpdate

router = APIRouter(
    prefix="/v1/trips",
    tags=["Trips"],
    responses={status: {"model": ApiError} for status in (401, 404, 409, 422, 503)},
)


def as_saved(row: Trip) -> SavedTrip:
    return SavedTrip(
        id=row.id,
        title=row.title,
        trip=row.trip_data,
        revision=row.revision,
        created_at=row.created_at.replace(tzinfo=UTC)
        if not row.created_at.tzinfo
        else row.created_at,
        updated_at=row.updated_at.replace(tzinfo=UTC)
        if not row.updated_at.tzinfo
        else row.updated_at,
    )


def owned(session: Database, user_id: UUID, trip_id: UUID) -> Trip:
    row = session.scalar(select(Trip).where(Trip.id == trip_id, Trip.owner_id == user_id))
    if row is None:
        raise api_error(404, "TRIP_NOT_FOUND", "Không tìm thấy chuyến đi.")
    return row


@router.post(
    "",
    response_model=SavedTrip,
    status_code=201,
    operation_id="createTrip",
    responses={200: {"model": SavedTrip, "description": "Previously created request replay"}},
)
def create_trip(payload: TripCreate, response: Response, user_id: UserId, session: Database):
    digest = hashlib.sha256(
        json.dumps(
            payload.model_dump(mode="json", exclude={"request_id"}),
            sort_keys=True,
            ensure_ascii=False,
        ).encode()
    ).hexdigest()

    def previous_request():
        return session.scalar(
            select(Trip).where(Trip.owner_id == user_id, Trip.request_id == payload.request_id)
        )

    def replay(row: Trip):
        if row.create_hash != digest:
            raise api_error(409, "REQUEST_CONFLICT", "Mã yêu cầu đã được dùng cho dữ liệu khác.")
        response.status_code = 200
        return as_saved(row)

    if previous := previous_request():
        return replay(previous)
    now = datetime.now(UTC)
    dialect_insert = sqlite_insert if session.bind.dialect.name == "sqlite" else pg_insert
    session.execute(
        dialect_insert(User).values(id=user_id, created_at=now).on_conflict_do_nothing()
    )
    row = Trip(
        id=uuid4(),
        owner_id=user_id,
        request_id=payload.request_id,
        create_hash=digest,
        title=payload.title,
        trip_data=payload.trip.model_dump(mode="json"),
        revision=1,
        created_at=now,
        updated_at=now,
    )
    session.add(row)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        if previous := previous_request():
            return replay(previous)
        raise
    session.refresh(row)
    return as_saved(row)


@router.get("", response_model=TripList, operation_id="listTrips")
def list_trips(
    user_id: UserId,
    session: Database,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    rows = session.scalars(
        select(Trip)
        .where(Trip.owner_id == user_id)
        .order_by(Trip.updated_at.desc(), Trip.id.desc())
        .offset(offset)
        .limit(limit)
    )
    total = session.scalar(select(func.count()).select_from(Trip).where(Trip.owner_id == user_id))
    return TripList(items=[as_saved(row) for row in rows], total=total, limit=limit, offset=offset)


@router.get("/{trip_id}", response_model=SavedTrip, operation_id="getTrip")
def get_trip(trip_id: UUID, user_id: UserId, session: Database):
    return as_saved(owned(session, user_id, trip_id))


@router.put("/{trip_id}", response_model=SavedTrip, operation_id="updateTrip")
def update_trip(trip_id: UUID, payload: TripUpdate, user_id: UserId, session: Database):
    owned(session, user_id, trip_id)
    result = session.execute(
        update(Trip)
        .where(
            Trip.id == trip_id, Trip.owner_id == user_id, Trip.revision == payload.expected_revision
        )
        .values(
            title=payload.title,
            trip_data=payload.trip.model_dump(mode="json"),
            revision=Trip.revision + 1,
            updated_at=datetime.now(UTC),
        )
    )
    if result.rowcount != 1:
        session.rollback()
        raise api_error(
            409, "REVISION_CONFLICT", "Chuyến đi đã thay đổi. Hãy tải lại trước khi lưu."
        )
    session.commit()
    return as_saved(owned(session, user_id, trip_id))


@router.delete("/{trip_id}", status_code=204, operation_id="deleteTrip")
def delete_trip(
    trip_id: UUID,
    user_id: UserId,
    session: Database,
    expected_revision: Annotated[int, Query(ge=1)],
):
    owned(session, user_id, trip_id)
    result = session.execute(
        delete(Trip).where(
            Trip.id == trip_id, Trip.owner_id == user_id, Trip.revision == expected_revision
        )
    )
    if result.rowcount != 1:
        session.rollback()
        raise api_error(
            409, "REVISION_CONFLICT", "Chuyến đi đã thay đổi. Hãy tải lại trước khi xóa."
        )
    session.commit()
    return Response(status_code=204)
