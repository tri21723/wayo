import { proxyApi } from "@/lib/api-proxy";
import { NextResponse } from "next/server";

async function handle(
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
  const query = new URLSearchParams();
  if (request.method === "DELETE")
    query.set(
      "expected_revision",
      new URL(request.url).searchParams.get("expected_revision") ?? "",
    );
  return proxyApi(
    request,
    `/v1/trips/${encodeURIComponent(id)}${query.size ? `?${query}` : ""}`,
  );
}
export { handle as GET, handle as PUT, handle as DELETE };
