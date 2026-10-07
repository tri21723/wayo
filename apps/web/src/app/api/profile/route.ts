import { proxyApi } from "@/lib/api-proxy";

export async function GET(request: Request) {
  return proxyApi(request, "/v1/profile");
}
export async function PUT(request: Request) {
  return proxyApi(request, "/v1/profile");
}
