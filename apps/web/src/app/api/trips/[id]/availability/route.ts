import { proxyApi } from "@/lib/api-proxy";
import { NextResponse } from "next/server";

export async function GET(
  request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const { id } = await context.params;
  if (
    !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id)
  ) {
    return NextResponse.json(
      {
        code: "TRIP_NOT_FOUND",
        message: "Không tìm thấy chuyến đi.",
        details: [],
      },
      { status: 404, headers: { "Cache-Control": "no-store" } },
    );
  }
  return proxyApi(request, `/v1/trips/${encodeURIComponent(id)}/availability`);
}
