import type { components } from "./api-schema";
import { getSupabase } from "./supabase";

export type TripRequest = components["schemas"]["TripRequest"];
export type TripValidation = components["schemas"]["TripValidation"];
export type SavedTrip = components["schemas"]["SavedTrip"];
export type TripList = components["schemas"]["TripList"];
export type TripCreate = components["schemas"]["TripCreate"];
export type TripUpdate = components["schemas"]["TripUpdate"];
type ApiError = components["schemas"]["ApiError"];

export class RequestError extends Error {
  constructor(
    public code: string,
    message: string,
    public status: number,
  ) {
    super(message);
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  authenticated = true,
  expectedOwner?: string,
): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body) headers.set("Content-Type", "application/json");
  if (authenticated) {
    const result = await getSupabase()?.auth.getSession();
    if (!result?.data.session || result.error)
      throw new RequestError(
        "UNAUTHENTICATED",
        "Vui lòng đăng nhập để tiếp tục.",
        401,
      );
    if (expectedOwner && result.data.session.user.id !== expectedOwner)
      throw new RequestError(
        "SESSION_CHANGED",
        "Tài khoản đã thay đổi. Vui lòng kiểm tra lại chuyến đi.",
        401,
      );
    headers.set("Authorization", `Bearer ${result.data.session.access_token}`);
  }
  const response = await fetch(path, {
    ...options,
    headers,
    cache: "no-store",
    signal: AbortSignal.timeout(12_000),
  });
  if (!response.ok) {
    const error = (await response.json()) as ApiError;
    throw new RequestError(
      error.code,
      error.details?.map((detail) => detail.message).join(" ") ||
        error.message ||
        "Yêu cầu chưa thành công. Vui lòng thử lại.",
      response.status,
    );
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export const validateTrip = (trip: TripRequest) =>
  request<TripValidation>(
    "/api/trips/validate",
    { method: "POST", body: JSON.stringify(trip) },
    false,
  );
export const createTrip = (payload: TripCreate, expectedOwner?: string) =>
  request<SavedTrip>(
    "/api/trips",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    true,
    expectedOwner,
  );
export const listTrips = (offset = 0) =>
  request<TripList>(`/api/trips?offset=${offset}&limit=20`);
export const getTrip = (id: string) =>
  request<SavedTrip>(`/api/trips/${encodeURIComponent(id)}`);
export const updateTrip = (
  id: string,
  payload: TripUpdate,
  expectedOwner?: string,
) =>
  request<SavedTrip>(
    `/api/trips/${encodeURIComponent(id)}`,
    {
      method: "PUT",
      body: JSON.stringify(payload),
    },
    true,
    expectedOwner,
  );
export const deleteTrip = (id: string, revision: number) =>
  request<void>(
    `/api/trips/${encodeURIComponent(id)}?expected_revision=${revision}`,
    { method: "DELETE" },
  );

export type TasteAnswers = components["schemas"]["TasteAnswers"];
export type SavedProfile = components["schemas"]["SavedProfile"];
export const getProfile = () => request<SavedProfile>("/api/profile");
export const saveProfile = (answers: TasteAnswers, revision: number) =>
  request<SavedProfile>("/api/profile", {
    method: "PUT",
    body: JSON.stringify({ answers, expected_revision: revision }),
  });

export type Recommendations = components["schemas"]["Recommendations"];
export const getRecommendations = (id: string) =>
  request<Recommendations>(
    `/api/trips/${encodeURIComponent(id)}/recommendations`,
  );

export type TripAvailability = components["schemas"]["TripAvailability"];
export const getAvailability = (id: string) =>
  request<TripAvailability>(
    `/api/trips/${encodeURIComponent(id)}/availability`,
  );
