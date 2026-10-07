import { NextResponse } from "next/server";

export async function POST(request: Request) {
  let payload: unknown;
  try {
    payload = await request.json();
  } catch {
    return NextResponse.json(
      {
        code: "INVALID_JSON",
        message: "Dữ liệu gửi lên không hợp lệ.",
        details: [],
      },
      { status: 400 },
    );
  }
  try {
    const apiUrl = process.env.WAYO_API_URL ?? "http://127.0.0.1:8000";
    const response = await fetch(`${apiUrl}/v1/trips/validate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(8_000),
      cache: "no-store",
    });
    if (response.status !== 200 && response.status !== 422)
      throw new Error("UPSTREAM_ERROR");
    return NextResponse.json(await response.json(), {
      status: response.status,
    });
  } catch {
    return NextResponse.json(
      {
        code: "API_UNAVAILABLE",
        message: "Chưa kết nối được Wayo API. Vui lòng thử lại sau.",
        details: [],
      },
      { status: 503 },
    );
  }
}
