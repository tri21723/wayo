import { proxyApi } from "@/lib/api-proxy";

export async function POST(request: Request) {
  return proxyApi(request, "/v1/trips");
}
export async function GET(request: Request) {
  const input = new URL(request.url).searchParams;
  const query = new URLSearchParams({
    offset: input.get("offset") ?? "0",
    limit: input.get("limit") ?? "20",
  });
  return proxyApi(request, `/v1/trips?${query}`);
}
