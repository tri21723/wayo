"""Intersect weekly opening hours with saved-trip availability; routing is not inferred."""

from datetime import date, datetime, time, timedelta
from typing import Literal

from pydantic import AwareDatetime, Field

from app.availability import AvailableDay
from app.catalog import PlaceRecord
from app.schemas import Contract, Vietnam


class VisitWindow(Contract):
    starts_at: AwareDatetime
    latest_start_at: AwareDatetime
    ends_at: AwareDatetime
    duration_minutes: int = Field(ge=5, le=720)


class VisitTiming(Contract):
    status: Literal["fits_known_hours", "unknown_hours", "unknown_duration", "no_window"]
    windows: list[VisitWindow] = Field(default_factory=list)


def visit_timing(place: PlaceRecord, days: list[AvailableDay]) -> VisitTiming:
    available = [block for day in days for block in day.blocks if block.kind == "available"]
    if not available or (
        place.duration_minutes is not None
        and all(block.minutes < place.duration_minutes for block in available)
    ):
        return VisitTiming(status="no_window")
    # Unknown data cannot establish a visit window or an assertion of infeasibility.
    if place.hours is None:
        return VisitTiming(status="unknown_hours")
    intersections = []
    for day in days:
        local_date = date.fromisoformat(day.date)
        opening = sorted(
            [
                (
                    datetime.combine(local_date, time.fromisoformat(window.opens), Vietnam),
                    datetime.combine(local_date, time.fromisoformat(window.closes), Vietnam),
                )
                for window in place.hours
                if window.weekday == local_date.weekday()
            ],
        )
        # Adjacent weekly windows describe continuous opening, not a closure.
        merged = []
        for start, end in opening:
            if merged and merged[-1][1] == start:
                merged[-1] = (merged[-1][0], end)
            else:
                merged.append((start, end))
        for block in day.blocks:
            if block.kind != "available":
                continue
            for opens, closes in merged:
                start, end = max(block.starts_at, opens), min(block.ends_at, closes)
                if start < end:
                    intersections.append((start, end))
    if not intersections:
        return VisitTiming(status="no_window")
    if place.duration_minutes is None:
        return VisitTiming(status="unknown_duration")
    duration = timedelta(minutes=place.duration_minutes)
    windows = [
        VisitWindow(
            starts_at=start,
            latest_start_at=end - duration,
            ends_at=end,
            duration_minutes=place.duration_minutes,
        )
        for start, end in intersections
        if end - start >= duration
    ]
    return VisitTiming(status="fits_known_hours" if windows else "no_window", windows=windows[:12])
