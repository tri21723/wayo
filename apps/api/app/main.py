from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas import ApiError, ErrorDetail, Health, InputNotice, TripRequest, TripValidation

app = FastAPI(
    title="Wayo API",
    version="0.1.0",
    description="Foundation contracts. Input validation only; no trip persistence or planning yet.",
)


@app.exception_handler(RequestValidationError)
async def invalid_request(_request: Request, exc: RequestValidationError) -> JSONResponse:
    # Do not reflect user input or Pydantic exception context in public errors.
    error = ApiError(
        code="VALIDATION_ERROR",
        message="Thông tin chuyến đi chưa hợp lệ.",
        details=[
            ErrorDetail(
                field=".".join(str(part) for part in issue["loc"] if part != "body"),
                message=issue["msg"].removeprefix("Value error, "),
            )
            for issue in exc.errors()
        ],
    )
    return JSONResponse(status_code=422, content=error.model_dump())


@app.get("/health", response_model=Health, operation_id="getHealth")
def health() -> Health:
    """Liveness only. This does not assert database/provider readiness."""
    return Health()


@app.post(
    "/v1/trips/validate",
    response_model=TripValidation,
    responses={422: {"model": ApiError}},
    operation_id="validateTrip",
)
def validate_trip(trip: TripRequest) -> TripValidation:
    """Validate a draft without saving it or asserting itinerary feasibility."""
    notices = [
        InputNotice(
            code="NOT_PLANNED",
            message=(
                "Đã kiểm tra đầu vào; chưa tạo lịch trình, kiểm tra tuyến hoặc dự toán chi phí."
            ),
        )
    ]
    if trip.anchor is None:
        notices.append(
            InputNotice(
                code="ANCHOR_REQUIRED_FOR_PLANNING",
                message="Cần bổ sung điểm lưu trú/điểm neo trước khi lập tuyến di chuyển.",
            )
        )
    if trip.budget.mode == "hard":
        notices.append(
            InputNotice(
                code="BUDGET_NOT_ESTIMATED",
                message="Giới hạn ngân sách đã ghi nhận; chưa có dự toán để kiểm tra mức trần.",
            )
        )
    return TripValidation(
        trip_days=trip.trip_days,
        total_budget_vnd=trip.budget.amount_vnd
        * (trip.people_count if trip.budget.scope == "per_person" else 1),
        notices=notices,
        trip=trip,
    )
