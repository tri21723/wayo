from datetime import UTC, datetime, timedelta
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.providers.contracts import ForecastRequest, MatrixRequest, TravelMatrix, WeatherForecast
from app.providers.transport import ProviderError, ProviderTransport

T = TypeVar("T", bound=BaseModel)


def checked[T: BaseModel](result_type: type[T], data: dict) -> T:
    try:
        return result_type.model_validate(data)
    except ValidationError:
        raise ProviderError("INVALID_RESPONSE") from None


class RoutingAdapter:
    def __init__(self, transport: ProviderTransport):
        self.transport = transport

    def matrix(self, request: MatrixRequest) -> TravelMatrix:
        base = self.transport.settings.routing_base_url
        if base is None:
            raise ProviderError("PROVIDER_NOT_CONFIGURED")
        coordinates = ";".join(f"{p.longitude},{p.latitude}" for p in request.points)
        data = self.transport.request(
            "routing",
            "GET",
            f"{str(base).rstrip('/')}/table/v1/driving/{coordinates}",
            params={"annotations": "duration,distance", "skip_waypoints": "true"},
        )
        if data.get("code") != "Ok":
            raise ProviderError("NO_ROUTE" if data.get("code") == "NoTable" else "INVALID_RESPONSE")
        count = len(request.points)
        for key in ("durations", "distances"):
            rows = data.get(key)
            if (
                not isinstance(rows, list)
                or len(rows) != count
                or any(not isinstance(row, list) or len(row) != count for row in rows)
            ):
                raise ProviderError("INVALID_RESPONSE")
        # Null is unreachable/unknown; never replace it with straight-line travel.
        return checked(
            TravelMatrix,
            {
                "retrieved_at": datetime.now(UTC),
                "durations_seconds": data["durations"],
                "distances_meters": data["distances"],
            },
        )


class WeatherAdapter:
    def __init__(self, transport: ProviderTransport):
        self.transport = transport

    def forecast(self, request: ForecastRequest, *, now: datetime | None = None) -> WeatherForecast:
        now = (now or datetime.now(UTC)).astimezone(UTC)
        if request.starts_on < now.date() or request.ends_on >= now.date() + timedelta(days=16):
            raise ProviderError("OUTSIDE_FORECAST_HORIZON")
        base = self.transport.settings.weather_base_url
        if base is None:
            raise ProviderError("PROVIDER_NOT_CONFIGURED")
        data = self.transport.request(
            "weather",
            "GET",
            f"{str(base).rstrip('/')}/v1/forecast",
            params={
                "latitude": request.latitude,
                "longitude": request.longitude,
                "start_date": request.starts_on.isoformat(),
                "end_date": request.ends_on.isoformat(),
                "hourly": "precipitation,precipitation_probability",
                "timezone": "UTC",
            },
        )
        hourly = data.get("hourly")
        if not isinstance(hourly, dict) or data.get("utc_offset_seconds") != 0:
            raise ProviderError("INVALID_RESPONSE")
        arrays = [hourly.get(key) for key in ("time", "precipitation", "precipitation_probability")]
        expected_hours = ((request.ends_on - request.starts_on).days + 1) * 24
        if any(not isinstance(value, list) or len(value) != expected_hours for value in arrays):
            raise ProviderError("INVALID_RESPONSE")
        hours = []
        for index, (at, rain, probability) in enumerate(zip(*arrays, strict=True)):
            expected_at = datetime.combine(request.starts_on, datetime.min.time(), UTC) + timedelta(
                hours=index
            )
            if at != expected_at.strftime("%Y-%m-%dT%H:%M"):
                raise ProviderError("INVALID_RESPONSE")
            hours.append(
                {"at": expected_at, "precipitation_mm": rain, "rain_probability": probability}
            )
        return checked(WeatherForecast, {"retrieved_at": now, "hours": hours})


class LlmAdapter:
    def __init__(self, transport: ProviderTransport):
        self.transport = transport

    def structured(self, prompt: str, result_type: type[T]) -> T:
        settings = self.transport.settings
        if not settings.llm_api_key or not settings.llm_model:
            raise ProviderError("PROVIDER_NOT_CONFIGURED")
        if not 1 <= len(prompt) <= 4000:
            raise ProviderError("INVALID_REQUEST")
        schema = result_type.model_json_schema()

        def strict_objects(node):
            if isinstance(node, dict):
                if node.get("type") == "object" and (
                    node.get("additionalProperties") is not False
                    or set(node.get("required", [])) != set(node.get("properties", {}))
                ):
                    raise ProviderError("INVALID_REQUEST")
                for child in node.values():
                    strict_objects(child)
            elif isinstance(node, list):
                for child in node:
                    strict_objects(child)

        strict_objects(schema)
        data = self.transport.request(
            "llm",
            "POST",
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {settings.llm_api_key.get_secret_value()}",
            },
            json={
                "model": settings.llm_model,
                "input": prompt,
                "store": False,
                "max_output_tokens": settings.llm_max_output_tokens,
                "text": {
                    "format": {
                        "type": "json_schema",
                        "name": "wayo_result",
                        "strict": True,
                        "schema": schema,
                    }
                },
            },
        )
        if data.get("status") != "completed":
            raise ProviderError("INCOMPLETE_RESPONSE")
        output = data.get("output")
        if not isinstance(output, list):
            raise ProviderError("INVALID_RESPONSE")
        texts = []
        for item in output:
            if not isinstance(item, dict):
                raise ProviderError("INVALID_RESPONSE")
            if item.get("type") != "message":
                continue  # Reasoning metadata is not an instruction or a tool call.
            content = item.get("content")
            if not isinstance(content, list):
                raise ProviderError("INVALID_RESPONSE")
            for part in content:
                if not isinstance(part, dict):
                    raise ProviderError("INVALID_RESPONSE")
                if part.get("type") == "refusal":
                    raise ProviderError("PROVIDER_REFUSAL")
                if part.get("type") == "output_text" and isinstance(part.get("text"), str):
                    texts.append(part["text"])
        if len(texts) != 1:
            raise ProviderError("INVALID_RESPONSE")
        try:
            return result_type.model_validate_json(texts[0])
        except ValidationError:
            raise ProviderError("INVALID_RESPONSE") from None
