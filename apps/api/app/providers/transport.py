"""Explicit opt-in, finite calls and response limits; no automatic retries or caching."""

import json
from time import monotonic
from typing import Literal

import httpx

from app.settings import Settings

Service = Literal["routing", "weather", "llm"]


class ProviderError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)  # Never retain credentials, URLs or provider response bodies.


class ProviderTransport:
    def __init__(self, settings: Settings, transport: httpx.BaseTransport | None = None):
        self.settings = settings
        self.transport = transport
        self.calls = 0  # One instance per planning/spike operation, never a global quota.

    def request(self, service: Service, method: str, url: str, **kwargs) -> dict:
        if service not in self.settings.providers_enabled:
            raise ProviderError("PROVIDER_DISABLED")
        if self.calls >= self.settings.provider_max_calls:
            raise ProviderError("CALL_LIMIT")
        self.calls += 1  # Failed attempts count too.
        deadline = monotonic() + self.settings.provider_timeout_seconds
        try:
            with (
                httpx.Client(
                    timeout=self.settings.provider_timeout_seconds,
                    transport=self.transport,
                    follow_redirects=False,
                    trust_env=False,
                ) as client,
                client.stream(method, url, **kwargs) as response,
            ):
                if response.status_code == 429:
                    raise ProviderError("PROVIDER_RATE_LIMITED")
                if not 200 <= response.status_code < 300:
                    raise ProviderError("PROVIDER_UNAVAILABLE")
                data = bytearray()
                for chunk in response.iter_bytes():
                    if monotonic() > deadline:
                        raise ProviderError("PROVIDER_TIMEOUT")
                    data.extend(chunk)
                    if len(data) > 524_288:
                        raise ProviderError("RESPONSE_TOO_LARGE")
                result = json.loads(data)
                if not isinstance(result, dict):
                    raise ProviderError("INVALID_RESPONSE")
                return result
        except httpx.TimeoutException:
            raise ProviderError("PROVIDER_TIMEOUT") from None
        except httpx.HTTPError:
            raise ProviderError("PROVIDER_UNAVAILABLE") from None
        except (ValueError, UnicodeDecodeError):
            raise ProviderError("INVALID_RESPONSE") from None
