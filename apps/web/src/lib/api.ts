import type { components } from "./api-schema";

export type TripRequest = components["schemas"]["TripRequest"];
export type TripValidation = components["schemas"]["TripValidation"];
type ApiError = components["schemas"]["ApiError"];

export async function validateTrip(trip: TripRequest): Promise<TripValidation> {
  const response = await fetch("/api/trips/validate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(trip),
    signal: AbortSignal.timeout(12_000),
  });
  if (!response.ok) {
    const error = (await response.json()) as ApiError;
    throw new Error(
      error.details?.map((detail) => detail.message).join(" ") ||
        error.message ||
        "Không thể kiểm tra chuyến đi. Vui lòng thử lại.",
    );
  }
  return response.json();
}
