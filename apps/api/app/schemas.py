from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, StringConstraints, model_validator

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Vietnam = ZoneInfo("Asia/Ho_Chi_Minh")


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Budget(Contract):
    amount_vnd: int = Field(gt=0, le=1_000_000_000, strict=True)
    scope: Literal["per_person", "group"] = "per_person"
    mode: Literal["soft", "hard"] = "soft"
    currency: Literal["VND"] = "VND"


class Anchor(Contract):
    label: Text
    latitude: float = Field(ge=-90, le=90, allow_inf_nan=False)
    longitude: float = Field(ge=-180, le=180, allow_inf_nan=False)


class FixedEvent(Contract):
    label: Text
    starts_at: AwareDatetime
    ends_at: AwareDatetime

    @model_validator(mode="after")
    def chronological(self) -> Self:
        if self.ends_at <= self.starts_at:
            raise ValueError("Sự kiện phải kết thúc sau khi bắt đầu.")
        return self


class Pace(StrEnum):
    RELAXED = "relaxed"
    BALANCED = "balanced"
    ACTIVE = "active"


class TripRequest(Contract):
    destination_id: Literal["da-lat"] = "da-lat"
    origin: Text
    arrival_at: AwareDatetime
    departure_at: AwareDatetime
    timezone: Literal["Asia/Ho_Chi_Minh"] = "Asia/Ho_Chi_Minh"
    people_count: int = Field(ge=1, le=4, strict=True)
    group_type: Literal["couple", "friends"]
    budget: Budget
    # Driving is provisional until the routing integration is evaluated.
    transport_mode: Literal["driving"] = "driving"
    pace: Pace = Pace.RELAXED
    anchor: Anchor | None = None
    preferences: list[Text] = Field(default_factory=list, max_length=20)
    exclusions: list[Text] = Field(default_factory=list, max_length=20)
    fixed_events: list[FixedEvent] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def valid_trip_window(self) -> Self:
        if self.departure_at <= self.arrival_at:
            raise ValueError("Giờ rời Đà Lạt phải sau giờ đến.")
        if not 2 <= self.trip_days <= 4:
            raise ValueError("Alpha hỗ trợ chuyến đi từ 2 đến 4 ngày theo giờ Việt Nam.")
        if self.group_type == "couple" and self.people_count != 2:
            raise ValueError("Chuyến đi couple cần đúng 2 người.")
        events = sorted(self.fixed_events, key=lambda event: event.starts_at)
        for event in events:
            if event.starts_at < self.arrival_at or event.ends_at > self.departure_at:
                raise ValueError("Sự kiện cố định phải nằm trong thời gian chuyến đi.")
        for previous, current in zip(events, events[1:], strict=False):
            if current.starts_at < previous.ends_at:
                raise ValueError("Các sự kiện cố định không được trùng giờ.")
        if set(self.preferences) & set(self.exclusions):
            raise ValueError("Một sở thích không thể đồng thời là điều cần tránh.")
        return self

    @property
    def trip_days(self) -> int:
        start = self.arrival_at.astimezone(Vietnam).date()
        end = self.departure_at.astimezone(Vietnam).date()
        return (end - start).days + 1


class InputNotice(Contract):
    code: str
    message: str


class TripValidation(Contract):
    status: Literal["input_valid"] = "input_valid"
    trip_days: int
    total_budget_vnd: int
    notices: list[InputNotice]
    trip: TripRequest


class ErrorDetail(Contract):
    field: str
    message: str


class ApiError(Contract):
    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)


class Health(Contract):
    status: Literal["ok"] = "ok"
    service: Literal["wayo-api"] = "wayo-api"
    version: Literal["0.1.0"] = "0.1.0"


class TripCreate(Contract):
    request_id: UUID
    title: Text
    trip: TripRequest


class TripUpdate(Contract):
    expected_revision: int = Field(ge=1, strict=True)
    title: Text
    trip: TripRequest


class SavedTrip(Contract):
    id: UUID
    title: str
    trip: TripRequest
    revision: int
    created_at: datetime
    updated_at: datetime


class TripList(Contract):
    items: list[SavedTrip]
    total: int
    offset: int
    limit: int
