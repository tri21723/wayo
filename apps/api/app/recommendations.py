"""Deterministic discovery based only on the saved trip, never itinerary feasibility."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from app.auth import UserId
from app.catalog import PlaceRecord, verified_places
from app.database import Database
from app.schemas import ApiError, Contract, InputNotice, TripRequest
from app.trips import owned

ALIASES = {
    "cafe": "cafe",
    "cà phê": "cafe",
    "nature": "nature",
    "thiên nhiên": "nature",
    "photography": "photography",
    "chụp ảnh": "photography",
    "food": "food",
    "đồ ăn local": "food",
    "ẩm thực": "food",
    "culture": "culture",
    "văn hóa": "culture",
    "nightlife": "nightlife",
    "hoạt động buổi tối": "nightlife",
}
ACCESS = {
    "trekking": "trekking",
    "stairs": "stairs",
    "cầu thang": "stairs",
    "alcohol": "alcohol",
    "rượu bia": "alcohol",
    "nơi đông người": "crowd",
}
LABELS = {
    "cafe": "Cà phê",
    "nature": "Thiên nhiên",
    "photography": "Chụp ảnh",
    "food": "Ẩm thực",
    "culture": "Văn hóa",
    "nightlife": "Hoạt động buổi tối",
}


class SuggestedPlace(Contract):
    place: PlaceRecord
    matched_interests: list[str]
    reasons: list[str]
    warnings: list[str]


class Recommendations(Contract):
    trip_revision: int
    algorithm_version: str = "saved-trip-tags-v1"
    items: list[SuggestedPlace]
    notices: list[InputNotice]


def rank_places(trip: TripRequest, places: list[PlaceRecord], limit: int):
    interests = {
        ALIASES[value.strip().casefold()]
        for value in trip.preferences
        if value.strip().casefold() in ALIASES
    }
    notices = [
        InputNotice(
            code="DISCOVERY_ONLY",
            message=(
                "Dựa trên bản chuyến đi đã lưu, chưa dùng profile cá nhân. Đây là gợi ý khám phá; "
                "chưa kiểm tra giờ mở cửa theo ngày đi, tuyến đường, lịch trình hoặc tổng chi phí."
            ),
        )
    ]
    unknown_preferences = [
        value for value in trip.preferences if value.strip().casefold() not in ALIASES
    ]
    if unknown_preferences:
        notices.append(
            InputNotice(
                code="UNMAPPED_PREFERENCES",
                message=("Chưa hiểu các sở thích: " + ", ".join(unknown_preferences)),
            )
        )
    excluded_tags = set()
    restrictions = set()
    unknown_exclusions = []
    for value in trip.exclusions:
        normalized = value.strip().casefold()
        if normalized in ALIASES:
            excluded_tags.add(ALIASES[normalized])
        elif normalized in ACCESS:
            restrictions.add(ACCESS[normalized])
        else:
            unknown_exclusions.append(value)
    if unknown_exclusions:
        notices.append(
            InputNotice(
                code="UNSUPPORTED_EXCLUSIONS",
                message=(
                    "Chưa thể kiểm tra các điều cần tránh: "
                    + ", ".join(unknown_exclusions)
                    + ". Chưa hiển thị gợi ý để tránh bỏ qua yêu cầu của bạn."
                ),
            )
        )
        return [], notices
    candidates = []
    total_budget = trip.budget.amount_vnd * (
        trip.people_count if trip.budget.scope == "per_person" else 1
    )
    for place in places:
        if place.hours == []:
            continue
        if set(place.tags) & excluded_tags:
            continue
        if any(
            (place.crowd not in ("quiet", "moderate"))
            if key == "crowd"
            else getattr(place, key) is not False
            for key in restrictions
        ):
            continue
        if trip.budget.mode == "hard":
            # Screening one activity against whole-trip cap is necessary but not sufficient.
            if place.price is None:
                continue
            activity_cost = place.price.max_vnd * (
                trip.people_count if place.price.unit == "per_person" else 1
            )
            if activity_cost > total_budget:
                continue
        matches = sorted(set(place.tags) & interests)
        warnings = ["Chưa kiểm tra lịch mở cửa thực tế cho thời gian chuyến đi."]
        if place.hours is None:
            warnings.append("Chưa có giờ mở cửa được xác minh.")
        if place.price is None:
            warnings.append("Chưa có khoảng giá được xác minh.")
        if trip.budget.mode == "hard":
            warnings.append(
                "Giá riêng hoạt động nằm dưới trần; chưa đảm bảo tổng ngân sách chuyến đi."
            )
        reasons = (
            ["Hợp sở thích: " + ", ".join(LABELS[tag] for tag in matches)]
            if matches
            else ["Địa điểm để khám phá thêm, chưa trùng sở thích đã chọn."]
        )
        if restrictions:
            reasons.append("Có dữ liệu đáp ứng các điều cần tránh đã hỗ trợ.")
        candidates.append(
            SuggestedPlace(
                place=place, matched_interests=matches, reasons=reasons, warnings=warnings
            )
        )
    candidates.sort(key=lambda item: (-len(item.matched_interests), item.place.slug))
    counts: dict[str, int] = {}
    selected = []
    for candidate in candidates:
        category = candidate.place.category
        if counts.get(category, 0) >= 2:
            continue
        selected.append(candidate)
        counts[category] = counts.get(category, 0) + 1
        if len(selected) == limit:
            break
    notices.append(
        InputNotice(
            code="DIVERSITY_LIMIT", message="Tối đa hai địa điểm mỗi nhóm để đa dạng lựa chọn."
        )
    )
    if not selected:
        notices.append(
            InputNotice(
                code="NO_ELIGIBLE_PLACES",
                message=("Chưa có địa điểm được xác minh gần đây đáp ứng bộ lọc của chuyến đi."),
            )
        )
    return selected, notices


router = APIRouter(
    tags=["Discovery"], responses={status: {"model": ApiError} for status in (401, 404, 422, 503)}
)


@router.get(
    "/v1/trips/{trip_id}/recommendations",
    response_model=Recommendations,
    operation_id="getRecommendations",
)
def recommendations(
    trip_id: UUID, user_id: UserId, session: Database, limit: Annotated[int, Query(ge=1, le=12)] = 6
):
    row = owned(session, user_id, trip_id)
    trip = TripRequest.model_validate(row.trip_data)
    items, notices = rank_places(trip, verified_places(session), limit)
    return Recommendations(trip_revision=row.revision, items=items, notices=notices)
