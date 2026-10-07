from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    MetaData,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    metadata = MetaData(schema="wayo")


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Trip(Base):
    __tablename__ = "trips"
    __table_args__ = (
        UniqueConstraint("owner_id", "request_id", name="uq_trips_owner_request"),
        CheckConstraint("revision >= 1", name="ck_trips_revision"),
        Index("ix_trips_owner_updated", "owner_id", "updated_at", "id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("wayo.users.id", ondelete="CASCADE"))
    request_id: Mapped[UUID] = mapped_column(Uuid)
    create_hash: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(120))
    trip_data: Mapped[dict] = mapped_column(JSON)
    revision: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class TravelProfile(Base):
    __tablename__ = "travel_profiles"
    __table_args__ = (
        CheckConstraint("revision >= 1", name="ck_profiles_revision"),
        CheckConstraint("schema_version = 1", name="ck_profiles_schema_version"),
    )

    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("wayo.users.id", ondelete="CASCADE"), primary_key=True
    )
    answers: Mapped[dict] = mapped_column(JSON)
    schema_version: Mapped[int] = mapped_column()
    revision: Mapped[int] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Place(Base):
    __tablename__ = "places"
    __table_args__ = (
        CheckConstraint("destination_id = 'da-lat'", name="ck_places_destination"),
        CheckConstraint(
            "status IN ('draft','verified','stale','disabled')", name="ck_places_status"
        ),
        Index("ix_places_destination_status", "destination_id", "status"),
    )

    slug: Mapped[str] = mapped_column(String(100), primary_key=True)
    destination_id: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20))
    record: Mapped[dict] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
