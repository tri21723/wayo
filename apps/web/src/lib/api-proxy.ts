import { NextResponse } from "next/server";

function error(status: number, code: string, message: string) {
  return NextResponse.json(
    { code, message, details: [] },
    { status, headers: { "Cache-Control": "no-store" } },
  );
}

export async function proxyApi(
  request: Request,
  path: string,
  authenticated = true,
) {
  const authorization = request.headers.get("Authorization");
  if (authenticated && !authorization?.startsWith("Bearer "))
    return error(401, "UNAUTHENTICATED", "Vui lòng đăng nhập để tiếp tục.");
  let body: string | undefined;
  if (["POST", "PUT"].includes(request.method)) {
    try {
      const reader = request.body?.getReader();
      const decoder = new TextDecoder("utf-8", { fatal: true });
      let bytes = 0;
      body = "";
      if (reader) {
        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          bytes += value.byteLength;
          if (bytes > 65_536) {
            await reader.cancel();
            return error(
              413,
              "PAYLOAD_TOO_LARGE",
              "Thông tin chuyến đi quá dài.",
            );
          }
          body += decoder.decode(value, { stream: true });
        }
      }
      body += decoder.decode();
      JSON.parse(body);
    } catch {
      return error(400, "INVALID_JSON", "Dữ liệu gửi lên không hợp lệ.");
    }
  }
  try {
    const base = process.env.WAYO_API_URL ?? "http://127.0.0.1:8000";
    const headers = new Headers();
    if (body) headers.set("Content-Type", "application/json");
    if (authenticated && authorization)
      headers.set("Authorization", authorization);
    const response = await fetch(`${base}${path}`, {
      method: request.method,
      headers,
      body,
      signal: AbortSignal.timeout(8_000),
      cache: "no-store",
      redirect: "error",
    });
    if (response.status === 204)
      return new Response(null, {
        status: 204,
        headers: { "Cache-Control": "no-store" },
      });
    if (
      ![200, 201, 400, 401, 403, 404, 409, 413, 422, 429, 500, 503].includes(
        response.status,
      )
    )
      throw new Error("UPSTREAM_ERROR");
    const responseHeaders = new Headers({ "Cache-Control": "no-store" });
    const requestId = response.headers.get("X-Request-ID");
    if (requestId && /^[0-9a-f-]{36}$/.test(requestId))
      responseHeaders.set("X-Request-ID", requestId);
    return NextResponse.json(await response.json(), {
      status: response.status,
      headers: responseHeaders,
    });
  } catch {
    return error(
      503,
      "API_UNAVAILABLE",
      "Chưa kết nối được Wayo API. Vui lòng thử lại sau.",
    );
  }
}
