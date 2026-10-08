"""Request correlation and metadata-only logs. Never log paths, bodies or exception text."""

import json
import logging
from time import perf_counter
from uuid import uuid4

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("wayo.requests")
logger.setLevel(logging.INFO)
logger.propagate = False
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)


class RequestLogging:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        # Generate our own ID: untrusted header values cannot inject log content.
        request_id = str(uuid4())
        scope.setdefault("state", {})["request_id"] = request_id
        started = perf_counter()
        status = 500
        response_started = False

        async def correlated(message: Message):
            nonlocal status, response_started
            if message["type"] == "http.response.start":
                status = message["status"]
                response_started = True
                headers = message.setdefault("headers", [])
                headers.append((b"x-request-id", request_id.encode()))
                if not any(name.lower() == b"cache-control" for name, _ in headers):
                    headers.append((b"cache-control", b"no-store"))
            await send(message)

        try:
            # Buffer only a bounded JSON body, including chunked requests without Content-Length.
            if scope["method"] in ("POST", "PUT", "PATCH"):
                data = bytearray()
                while True:
                    message = await receive()
                    if message["type"] == "http.disconnect":
                        return
                    data.extend(message.get("body", b""))
                    if len(data) > 65_536:
                        await JSONResponse(
                            status_code=413,
                            content={
                                "code": "PAYLOAD_TOO_LARGE",
                                "message": "Dữ liệu gửi lên quá dài.",
                                "details": [],
                            },
                        )(scope, receive, correlated)
                        return
                    if not message.get("more_body", False):
                        break
                consumed = False

                async def buffered():
                    nonlocal consumed
                    if not consumed:
                        consumed = True
                        return {"type": "http.request", "body": bytes(data), "more_body": False}
                    return await receive()

                await self.app(scope, buffered, correlated)
            else:
                await self.app(scope, receive, correlated)
        except Exception:
            if response_started:
                raise
            await JSONResponse(
                status_code=500,
                content={
                    "code": "INTERNAL_ERROR",
                    "message": "Có lỗi xử lý. Vui lòng thử lại sau.",
                    "details": [],
                },
            )(scope, receive, correlated)
        finally:
            route = scope.get("route")
            logger.info(
                json.dumps(
                    {
                        "event": "http_request",
                        "request_id": request_id,
                        "method": scope["method"],
                        "route": getattr(route, "path", "unmatched"),
                        "status": status,
                        "latency_ms": round((perf_counter() - started) * 1000, 2),
                    }
                )
            )
