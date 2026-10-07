"use client";

import { useState } from "react";
import { getRecommendations, type Recommendations } from "@/lib/api";

export function TripRecommendations({
  tripId,
  revision,
}: {
  tripId: string;
  revision: number;
}) {
  const [data, setData] = useState<Recommendations | null>(null);
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);
  async function load() {
    if (pending) return;
    setPending(true);
    setError("");
    setData(null);
    try {
      const result = await getRecommendations(tripId);
      if (result.trip_revision !== revision)
        throw new Error(
          "Chuyến đi đã thay đổi ở nơi khác. Hãy tải lại bản đã lưu trước khi xem gợi ý.",
        );
      setData(result);
    } catch (caught) {
      setError(
        caught instanceof Error ? caught.message : "Chưa tải được gợi ý.",
      );
    } finally {
      setPending(false);
    }
  }
  return (
    <section
      className="form-card discovery"
      aria-labelledby="discovery-heading"
    >
      <h2 id="discovery-heading">Khám phá địa điểm</h2>
      <p>
        Dùng sở thích và các điều cần tránh trong bản chuyến đi đã lưu. Hãy lưu
        thay đổi trước khi xem gợi ý.
      </p>
      <button
        type="button"
        className="primary"
        disabled={pending}
        onClick={load}
      >
        {pending ? "Đang tìm địa điểm…" : "Xem gợi ý địa điểm"}
      </button>
      {error && (
        <p role="alert" className="message error">
          {error}
        </p>
      )}
      {data && (
        <>
          <div role="status">
            {data.notices.map((notice) => (
              <p key={notice.code}>{notice.message}</p>
            ))}
          </div>
          <div className="trip-grid">
            {data.items.map(({ place, reasons, warnings }) => (
              <article className="place-card" key={place.slug}>
                <h3>{place.name}</h3>
                <p>{place.address}</p>
                <p>
                  {place.price
                    ? `${place.price.min_vnd.toLocaleString("vi-VN")}–${place.price.max_vnd.toLocaleString("vi-VN")} đ / ${place.price.unit === "per_person" ? "người" : "nhóm"}`
                    : "Giá: chưa xác minh"}
                </p>
                {place.duration_minutes != null && (
                  <p>Thời lượng tham khảo: {place.duration_minutes} phút.</p>
                )}
                <ul>
                  {reasons.map((reason) => (
                    <li key={reason}>{reason}</li>
                  ))}
                </ul>
                <ul className="place-warnings">
                  {warnings.map((warning) => (
                    <li key={warning}>{warning}</li>
                  ))}
                </ul>
                <details>
                  <summary>Nguồn thông tin</summary>
                  <ul>
                    {place.sources.map((source, index) => (
                      <li key={`${source.url}:${index}`}>
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          Nguồn {index + 1}
                        </a>{" "}
                        · Kiểm tra{" "}
                        {new Date(source.checked_at).toLocaleDateString(
                          "vi-VN",
                          { timeZone: "Asia/Ho_Chi_Minh" },
                        )}
                        <p>{source.note}</p>
                      </li>
                    ))}
                  </ul>
                </details>
              </article>
            ))}
          </div>
        </>
      )}
    </section>
  );
}
