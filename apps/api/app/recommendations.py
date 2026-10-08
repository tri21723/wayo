"""Deterministic discovery based only on the saved trip, never itinerary feasibility."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from app.auth import UserId
from app.availability import available_days
from app.catalog import PlaceRecord, verified_places
from app.database import Database
from app.schemas import ApiError, Contract, InputNotice, TripRequest
from app.trips import owned
from app.visit_windows import VisitTiming, visit_timing

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
    matched_context: list[str]
    reasons: list[str]
    warnings: list[str]
    timing: VisitTiming


class Recommendations(Contract):
    trip_revision: int
    algorithm_version: str = "saved-trip-hours-v3"
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
                "Dựa trên sở thích và điều chỉnh riêng trong bản chuyến đi đã lưu. "
                "Đây là gợi ý khám phá; "
                "đối chiếu lịch mở cửa theo tuần với khoảng trống 09:00–21:00 và sự kiện cố định. "
                "Chưa kiểm tra ngày lễ/ngoại lệ, tuyến đường, nghỉ/ăn uống hoặc tổng chi phí."
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
    days = available_days(trip)
    candidates = []
    total_budget = trip.budget.amount_vnd * (
        trip.people_count if trip.budget.scope == "per_person" else 1
    )
    for place in places:
        timing = visit_timing(place, days)
        if timing.status == "no_window":
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
        serves_food = place.category in ("food", "cafe") or "food" in place.tags
        if trip.diet != "unrestricted" and serves_food:
            options = set(place.dietary_options or [])
            if "vegan" in options:
                options.add("vegetarian")
            if trip.diet not in options:
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
        context = []
        if (trip.crowd == "quiet" and place.crowd == "quiet") or (
            trip.crowd == "lively" and place.crowd == "busy"
        ):
            context.append("Không khí phù hợp lựa chọn của bạn.")
        if trip.adventure is not None and trip.adventure == place.effort:
            context.append("Mức vận động phù hợp lựa chọn của bạn.")
        warnings = ["Chưa kiểm tra ngày lễ/ngoại lệ, thời gian ăn/nghỉ và di chuyển."]
        if timing.status == "unknown_duration":
            warnings.append("Chưa có thời lượng tham quan để kiểm tra đủ thời gian ghé.")
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
        reasons.extend(context)
        if timing.status == "fits_known_hours":
            reasons.append("Có khoảng trống đủ thời lượng ghé theo lịch mở cửa đã lưu.")
        if trip.diet != "unrestricted" and serves_food:
            reasons.append("Có lựa chọn ăn chay phù hợp chế độ ăn đã chọn, theo nguồn đã kiểm tra.")
        if restrictions:
            reasons.append("Có dữ liệu đáp ứng các điều cần tránh đã hỗ trợ.")
        candidates.append(
            SuggestedPlace(
                place=place,
                matched_interests=matches,
                matched_context=context,
                reasons=reasons,
                warnings=warnings,
                timing=timing,
            )
        )
    candidates.sort(
        key=lambda item: (-len(item.matched_interests), -len(item.matched_context), item.place.slug)
    )
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
