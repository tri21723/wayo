"""One explicitly requested live call. Default is read-only config inspection."""

import argparse
import json
from datetime import UTC, datetime
from typing import Literal

from app.providers.adapters import LlmAdapter, RoutingAdapter, WeatherAdapter
from app.providers.contracts import ForecastRequest, MatrixRequest
from app.providers.transport import ProviderError, ProviderTransport
from app.schemas import Contract
from app.settings import get_settings


class Ping(Contract):
    result: Literal["ok"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["routing", "weather", "llm"], required=True)
    parser.add_argument(
        "--live", action="store_true", help="One external call; LLM may incur charges."
    )
    args = parser.parse_args()
    settings = get_settings()
    configured = {
        "routing": settings.routing_base_url is not None,
        "weather": settings.weather_base_url is not None,
        "llm": bool(settings.llm_api_key and settings.llm_model),
    }[args.provider]
    if not args.live:
        print(
            json.dumps(
                {
                    "provider": args.provider,
                    "configured": configured,
                    "enabled": args.provider in settings.providers_enabled,
                    "calls": 0,
                }
            )
        )
        return 0
    transport = ProviderTransport(settings.model_copy(update={"provider_max_calls": 1}))
    try:
        if args.provider == "routing":
            result = RoutingAdapter(transport).matrix(
                MatrixRequest(
                    points=[
                        {"latitude": 11.9404, "longitude": 108.4583},
                        {"latitude": 11.9452, "longitude": 108.4419},
                    ]
                )
            )
            summary = {
                "points": len(result.durations_seconds),
                "mode": result.mode,
                "known_cells": sum(
                    cell is not None for row in result.durations_seconds for cell in row
                ),
            }
        elif args.provider == "weather":
            today = datetime.now(UTC).date()
            result = WeatherAdapter(transport).forecast(
                ForecastRequest(
                    latitude=11.9404,
                    longitude=108.4583,
                    starts_on=today,
                    ends_on=today,
                )
            )
            summary = {"hours": len(result.hours)}
        else:
            result = LlmAdapter(transport).structured('Return {"result":"ok"}.', Ping)
            summary = {"result": result.result}
        print(
            json.dumps(
                {"provider": args.provider, "status": "ok", "calls": transport.calls, **summary}
            )
        )
        return 0
    except ProviderError as exc:
        print(json.dumps({"provider": args.provider, "status": exc.code, "calls": transport.calls}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
