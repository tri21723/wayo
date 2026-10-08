import json
from datetime import UTC, date, datetime, timedelta
from typing import Literal

import httpx
import pytest
from pydantic import ValidationError

from app.providers.adapters import LlmAdapter, RoutingAdapter, WeatherAdapter
from app.providers.contracts import ForecastRequest, MatrixRequest
from app.providers.transport import ProviderError, ProviderTransport
from app.schemas import Contract
from app.settings import Settings


class Ping(Contract):
    result: Literal["ok"]


def transport(handler, **changes):
    settings = Settings(
        _env_file=None,
        **{
            "providers_enabled": ["routing", "weather", "llm"],
            "routing_base_url": "https://routing.example",
            "weather_base_url": "https://weather.example",
            "llm_model": "configured-test-model",
            "llm_api_key": "private-test-key",
            **changes,
        },
    )
    return ProviderTransport(settings, httpx.MockTransport(handler))


def points():
    return MatrixRequest(
        points=[{"latitude": 11.94, "longitude": 108.44}, {"latitude": 11.95, "longitude": 108.45}]
    )


def test_routing_coordinate_order_units_and_unreachable_cells():
    def handler(request):
        assert "/table/v1/driving/108.44,11.94;108.45,11.95" in str(request.url)
        assert "fallback_speed" not in request.url.params
        return httpx.Response(
            200,
            json={
                "code": "Ok",
                "durations": [[0, None], [90, 0]],
                "distances": [[0, None], [1200, 0]],
            },
        )

    result = RoutingAdapter(transport(handler)).matrix(points())
    assert result.durations_seconds == [[0, None], [90, 0]]
    assert result.distances_meters[1][0] == 1200
    assert result.retrieved_at.tzinfo is not None


@pytest.mark.parametrize(
    "body,code",
    [
        ({"code": "NoTable"}, "NO_ROUTE"),
        ({"code": "Ok", "durations": [[0]], "distances": [[0]]}, "INVALID_RESPONSE"),
        (
            {"code": "Ok", "durations": [[0, -1], [1, 0]], "distances": [[0, 1], [1, 0]]},
            "INVALID_RESPONSE",
        ),
    ],
)
def test_invalid_route_results_do_not_become_travel_estimates(body, code):
    with pytest.raises(ProviderError, match=code):
        RoutingAdapter(transport(lambda _: httpx.Response(200, json=body))).matrix(points())


@pytest.mark.parametrize(
    "status,code",
    [(429, "PROVIDER_RATE_LIMITED"), (500, "PROVIDER_UNAVAILABLE"), (302, "PROVIDER_UNAVAILABLE")],
)
def test_http_failures_redacted_no_retry_count_toward_limit(status, code):
    called = []
    gateway = transport(
        lambda request: called.append(request) or httpx.Response(status, text="private-secret"),
        provider_max_calls=1,
    )
    with pytest.raises(ProviderError, match=code) as caught:
        RoutingAdapter(gateway).matrix(points())
    assert "private-secret" not in str(caught.value)
    with pytest.raises(ProviderError, match="CALL_LIMIT"):
        RoutingAdapter(gateway).matrix(points())
    assert len(called) == 1


def test_disabled_provider_makes_no_network_call():
    gateway = transport(lambda _: pytest.fail("Network must not be called"), providers_enabled=[])
    with pytest.raises(ProviderError, match="PROVIDER_DISABLED"):
        RoutingAdapter(gateway).matrix(points())
    assert gateway.calls == 0


@pytest.mark.parametrize(
    "failure,code",
    [
        (lambda _: (_ for _ in ()).throw(httpx.ReadTimeout("private-secret")), "PROVIDER_TIMEOUT"),
        (lambda _: httpx.Response(200, text="not-json-private-secret"), "INVALID_RESPONSE"),
        (lambda _: httpx.Response(200, text=" " * 524_289), "RESPONSE_TOO_LARGE"),
    ],
)
def test_transport_limits_and_redaction(failure, code):
    with pytest.raises(ProviderError, match=code):
        RoutingAdapter(transport(failure)).matrix(points())


def weather_body():
    midnight = datetime(2026, 10, 8, tzinfo=UTC)
    return {
        "utc_offset_seconds": 0,
        "hourly": {
            "time": [
                (midnight + timedelta(hours=index)).strftime("%Y-%m-%dT%H:%M")
                for index in range(24)
            ],
            "precipitation": [None] + [1.2] * 23,
            "precipitation_probability": [None] + [70] * 23,
        },
    }


def forecast():
    return ForecastRequest(
        latitude=11.94, longitude=108.44, starts_on=date(2026, 10, 8), ends_on=date(2026, 10, 8)
    )


def test_weather_utc_and_missing_data_preserved():
    result = WeatherAdapter(transport(lambda _: httpx.Response(200, json=weather_body()))).forecast(
        forecast(), now=datetime(2026, 10, 8, tzinfo=UTC)
    )
    assert len(result.hours) == 24
    assert result.hours[0].precipitation_mm is None
    assert result.hours[1].rain_probability == 70
    assert "CC BY 4.0" in result.attribution


def test_forecast_outside_horizon_makes_no_call():
    gateway = transport(lambda _: pytest.fail("No forecast outside horizon"))
    with pytest.raises(ProviderError, match="OUTSIDE_FORECAST_HORIZON"):
        WeatherAdapter(gateway).forecast(forecast(), now=datetime(2026, 9, 1, tzinfo=UTC))
    assert gateway.calls == 0


@pytest.mark.parametrize(
    "change", ["missing_hour", "bad_probability", "wrong_timezone", "wrong_date"]
)
def test_forecast_partial_or_invalid_data_rejected(change):
    body = weather_body()
    if change == "missing_hour":
        body["hourly"]["time"].pop()
    if change == "bad_probability":
        body["hourly"]["precipitation_probability"][1] = 101
    if change == "wrong_timezone":
        body["utc_offset_seconds"] = 25200
    if change == "wrong_date":
        body["hourly"]["time"][0] = "2026-10-09T00:00"
    with pytest.raises(ProviderError, match="INVALID_RESPONSE"):
        WeatherAdapter(transport(lambda _: httpx.Response(200, json=body))).forecast(
            forecast(), now=datetime(2026, 10, 8, tzinfo=UTC)
        )


def llm_body(text='{"result":"ok"}'):
    return {
        "status": "completed",
        "output": [{"type": "message", "content": [{"type": "output_text", "text": text}]}],
    }


def test_llm_structured_schema_store_off_and_token_cap():
    def handler(request):
        body = json.loads(request.content)
        assert body["store"] is False and body["max_output_tokens"] == 512
        assert body["text"]["format"]["strict"] is True
        assert body["text"]["format"]["schema"]["additionalProperties"] is False
        assert "tools" not in body
        return httpx.Response(200, json=llm_body())

    assert LlmAdapter(transport(handler)).structured("Ping", Ping).result == "ok"


@pytest.mark.parametrize(
    "body,code",
    [
        (llm_body("invalid-json"), "INVALID_RESPONSE"),
        (llm_body('{"result":"ok","extra":"bad"}'), "INVALID_RESPONSE"),
        ({"status": "incomplete"}, "INCOMPLETE_RESPONSE"),
        (
            {
                "status": "completed",
                "output": [{"type": "message", "content": [{"type": "refusal"}]}],
            },
            "PROVIDER_REFUSAL",
        ),
    ],
)
def test_llm_refusal_incomplete_and_invalid_output(body, code):
    with pytest.raises(ProviderError, match=code):
        LlmAdapter(transport(lambda _: httpx.Response(200, json=body))).structured("Ping", Ping)


def test_invalid_input_rejected_before_call():
    with pytest.raises(ValidationError):
        MatrixRequest(points=[{"latitude": float("nan"), "longitude": 108}] * 2)
    gateway = transport(lambda _: pytest.fail("No call for oversized input"))
    with pytest.raises(ProviderError, match="INVALID_REQUEST"):
        LlmAdapter(gateway).structured("x" * 4001, Ping)
    assert gateway.calls == 0
