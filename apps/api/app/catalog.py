"""Curated POI contract. Import records are assertions by a human curator, not a crawler."""

from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal, Self

from pydantic import AwareDatetime, Field, HttpUrl, StringConstraints, model_validator
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.models import Place
from app.profiles import Interest
from app.schemas import Contract, Text

Slug = Annotated[str, StringConstraints(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=100)]
EvidenceField = Literal["identity", "coordinates", "tags", "access", "price", "hours", "duration"]


class Evidence(Contract):
    url: HttpUrl
    checked_at: AwareDatetime
    fields: list[EvidenceField] = Field(min_length=1, max_length=7)
    note: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]

    @model_validator(mode="after")
    def valid_evidence(self) -> Self:
        if self.url.username or self.url.password:
            raise ValueError("Source URL must not contain credentials.")
        if self.checked_at > datetime.now(UTC):
            raise ValueError("Evidence cannot be checked in the future.")
        if len(self.fields) != len(set(self.fields)):
            raise ValueError("Duplicate evidence fields.")
        return self


class Price(Contract):
    min_vnd: int = Field(ge=0, le=1_000_000_000, strict=True)
    max_vnd: int = Field(ge=0, le=1_000_000_000, strict=True)
    unit: Literal["per_person", "group"]

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.max_vnd < self.min_vnd:
            raise ValueError("Maximum price must not be below minimum price.")
        return self


class OpeningWindow(Contract):
    weekday: int = Field(ge=0, le=6, strict=True, description="Monday=0; Vietnam local time")
    opens: Annotated[str, StringConstraints(pattern=r"^(?:[01][0-9]|2[0-3]):[0-5][0-9]$")]
    closes: Annotated[str, StringConstraints(pattern=r"^(?:[01][0-9]|2[0-3]):[0-5][0-9]$")]

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.closes <= self.opens:
            raise ValueError("Split overnight windows by day; closes must follow opens.")
        return self


class PlaceRecord(Contract):
    schema_version: Literal[1] = 1
    slug: Slug
    destination_id: Literal["da-lat"] = "da-lat"
    name: Text
    address: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
    category: Literal["cafe", "food", "nature", "attraction", "nightlife", "culture"]
    latitude: float = Field(ge=-90, le=90, allow_inf_nan=False)
    longitude: float = Field(ge=-180, le=180, allow_inf_nan=False)
    tags: list[Interest] = Field(min_length=1, max_length=6)
    status: Literal["draft", "verified", "stale", "disabled"] = "draft"
    # Unknown access is distinct from confirmed absence of a restriction.
    trekking: bool | None = Field(default=None, strict=True)
    stairs: bool | None = Field(default=None, strict=True)
    alcohol: bool | None = Field(default=None, strict=True)
    crowd: Literal["quiet", "moderate", "busy"] | None = None
    price: Price | None = None
    duration_minutes: int | None = Field(default=None, ge=5, le=720, strict=True)
    hours: list[OpeningWindow] | None = Field(default=None, max_length=28)
    sources: list[Evidence] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def coherent(self) -> Self:
        if len(self.tags) != len(set(self.tags)):
            raise ValueError("Duplicate tags.")
        covered = {field for source in self.sources for field in source.fields}
        required = {"identity", "coordinates", "tags"}
        if any(
            value is not None for value in (self.trekking, self.stairs, self.alcohol, self.crowd)
        ):
            required.add("access")
        for field in ("price", "hours", "duration"):
            value = self.duration_minutes if field == "duration" else getattr(self, field)
            if value is not None:
                required.add(field)
        if self.status == "verified" and not required <= covered:
            raise ValueError("Verified records need evidence for every supplied field group.")
        if self.hours is not None:
            windows = sorted(self.hours, key=lambda item: (item.weekday, item.opens))
            for previous, current in zip(windows, windows[1:], strict=False):
                if previous.weekday == current.weekday and previous.closes > current.opens:
                    raise ValueError("Opening windows overlap.")
        return self

    def fresh(self, now: datetime) -> bool:
        # All claimed facts must have been checked within 90 days.
        return all(now - timedelta(days=90) <= source.checked_at <= now for source in self.sources)


class CatalogBatch(Contract):
    schema_version: Literal[1] = 1
    places: list[PlaceRecord] = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def unique_places(self) -> Self:
        slugs = [item.slug for item in self.places]
        identities = [identity(item) for item in self.places]
        if len(slugs) != len(set(slugs)) or len(identities) != len(set(identities)):
            raise ValueError("Duplicate slug or name/address in batch.")
        return self


def identity(record: PlaceRecord) -> tuple[str, str]:
    return (" ".join(record.name.casefold().split()), " ".join(record.address.casefold().split()))


def import_batch(session: Session, batch: CatalogBatch) -> dict[str, int]:
    """Atomic upserts; caller owns commit. Slugs are stable editorial identifiers."""
    insert = sqlite_insert if session.bind.dialect.name == "sqlite" else pg_insert
    incoming_slugs = {record.slug for record in batch.places}
    identities = {
        identity(PlaceRecord.model_validate(row.record)): row.slug
        for row in session.scalars(select(Place))
        if row.slug not in incoming_slugs
    }
    for record in batch.places:
        if identity(record) in identities:
            raise ValueError("Name/address already exists under a different slug.")
        identities[identity(record)] = record.slug
    created = updated = 0
    for record in batch.places:
        existing = session.get(Place, record.slug)
        if existing:
            updated += 1
        else:
            created += 1
        statement = insert(Place).values(
            slug=record.slug,
            destination_id=record.destination_id,
            status=record.status,
            record=record.model_dump(mode="json"),
            updated_at=datetime.now(UTC),
        )
        session.execute(
            statement.on_conflict_do_update(
                index_elements=[Place.slug],
                set_={
                    "status": statement.excluded.status,
                    "record": statement.excluded.record,
                    "updated_at": statement.excluded.updated_at,
                },
            )
        )
    return {"created": created, "updated": updated}


def verified_places(session: Session) -> list[PlaceRecord]:
    rows = session.scalars(
        select(Place)
        .where(
            Place.destination_id == "da-lat",
            Place.status == "verified",
        )
        .order_by(Place.slug)
    )
    now = datetime.now(UTC)
    return [record for row in rows if (record := PlaceRecord.model_validate(row.record)).fresh(now)]
