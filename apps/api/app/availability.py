"""Local-calendar availability from saved trip bounds and fixed bookings."""

from datetime import datetime, time, timedelta
from typing import Literal
from uuid import UUID

from fastapi import APIRouter
from pydantic import AwareDatetime

from app.auth import UserId
from app.database import Database
from app.schemas import ApiError, Contract, InputNotice, TripRequest, Vietnam
from app.trips import owned


class TimeBlock(Contract):
    starts_at: AwareDatetime
    ends_at: AwareDatetime
    label: str
    kind: Literal["fixed", "available", "outside_activity_hours"]
    minutes: float


class AvailableDay(Contract):
    date: str
    blocks: list[TimeBlock]
    available_minutes: float


class TripAvailability(Contract):
    trip_revision: int
    days: list[AvailableDay]
    notices: list[InputNotice]


def block(start: datetime, end: datetime, kind: str, label: str) -> TimeBlock:
    return TimeBlock(
        starts_at=start,
        ends_at=end,
        kind=kind,
        label=label,
        minutes=(end - start).total_seconds() / 60,
    )


def available_days(trip: TripRequest) -> list[AvailableDay]:
    """09:00–21:00 provisional activity hours; never subtract overlapping time twice."""
    arrival = trip.arrival_at.astimezone(Vietnam)
    departure = trip.departure_at.astimezone(Vietnam)
    events = sorted(trip.fixed_events, key=lambda item: item.starts_at)
    days = []
    date = arrival.date()
    while date <= departure.date():
        midnight = datetime.combine(date, time.min, Vietnam)
        next_midnight = midnight + timedelta(days=1)
        start = max(arrival, midnight)
        end = min(departure, next_midnight)
        # Retain the arrival/departure date even if it contains no positive duration.
        blocks = []
        if start < end:
            activity_start = max(start, datetime.combine(date, time(9), Vietnam))
            activity_end = min(end, datetime.combine(date, time(21), Vietnam))
            boundaries = {start, end}
            for value in (activity_start, activity_end):
                if start < value < end:
                    boundaries.add(value)
            day_events = []
            for event in events:
                event_start = event.starts_at.astimezone(Vietnam)
                event_end = event.ends_at.astimezone(Vietnam)
                clipped_start = max(start, event_start)
                clipped_end = min(end, event_end)
                if clipped_start < clipped_end:
                    boundaries.update((clipped_start, clipped_end))
                    day_events.append((clipped_start, clipped_end, event.label))
            ordered = sorted(boundaries)
            for left, right in zip(ordered, ordered[1:], strict=False):
                matching = next((label for a, b, label in day_events if a <= left < b), None)
                if matching is not None:
                    kind, label = "fixed", matching
                elif activity_start <= left and right <= activity_end:
                    kind, label = "available", "Thời gian chưa xếp hoạt động"
                else:
                    kind, label = "outside_activity_hours", "Ngoài giờ hoạt động tham khảo"
                if blocks and blocks[-1].kind == kind and blocks[-1].label == label:
                    blocks[-1] = block(blocks[-1].starts_at, right, kind, label)
                else:
                    blocks.append(block(left, right, kind, label))
        days.append(
            AvailableDay(
                date=date.isoformat(),
                blocks=blocks,
                available_minutes=sum(item.minutes for item in blocks if item.kind == "available"),
            )
        )
        date += timedelta(days=1)
    return days


router = APIRouter(
    tags=["Planning inputs"], responses={status: {"model": ApiError} for status in (401, 404, 503)}
)


@router.get(
    "/v1/trips/{trip_id}/availability",
    response_model=TripAvailability,
    operation_id="getAvailability",
)
def availability(trip_id: UUID, user_id: UserId, session: Database):
    row = owned(session, user_id, trip_id)
    trip = TripRequest.model_validate(row.trip_data)
    notices = [
        InputNotice(
            code="PROVISIONAL_ACTIVITY_HOURS",
            message=(
                "Khoảng trống tính trong giờ hoạt động tham khảo 09:00–21:00 mỗi ngày, "
                "giới hạn bởi giờ đến/về và sự kiện cố định. "
                "Chưa dành thời gian cho bữa ăn, nghỉ và di chuyển."
            ),
        )
    ]
    if trip.anchor is None:
        notices.append(
            InputNotice(
                code="MISSING_ANCHOR",
                message="Bổ sung điểm lưu trú/xuất phát để tính tuyến ở bước tiếp theo.",
            )
        )
    return TripAvailability(trip_revision=row.revision, days=available_days(trip), notices=notices)
