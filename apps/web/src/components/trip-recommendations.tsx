"use client";

import { useState } from "react";
function visitTime(value: string) {
  return new Date(value).toLocaleString("vi-VN", {
    timeZone: "Asia/Ho_Chi_Minh",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

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
            {data.items.map(({ place, reasons, warnings, timing }) => (
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
                {timing?.status === "fits_known_hours" && (
                  <div className="visit-windows">
                    <h4>Khoảng giờ có thể ghé (tham khảo)</h4>
                    <p>
                      Chọn giờ bắt đầu trong mỗi khoảng dưới đây. Các lựa chọn
                      độc lập; chưa cộng thời gian di chuyển.
                    </p>
                    <ul>
                      {(timing.windows ?? []).slice(0, 3).map((window) => (
                        <li key={`${window.starts_at}:${window.ends_at}`}>
                          Bắt đầu từ {visitTime(window.starts_at)} đến{" "}
                          {visitTime(window.latest_start_at)} ·{" "}
                          {window.duration_minutes} phút · kết thúc trước hoặc
                          lúc {visitTime(window.ends_at)}
                        </li>
                      ))}
                    </ul>
                    {(timing.windows ?? []).length > 3 && (
                      <p>
                        Còn {(timing.windows ?? []).length - 3} khoảng giờ khác.
                      </p>
                    )}
                  </div>
                )}
                {timing?.status === "unknown_hours" && (
                  <p>Chưa xác định giờ có thể ghé: thiếu lịch mở cửa.</p>
                )}
                {timing?.status === "unknown_duration" && (
                  <p>
                    Chưa xác định giờ có thể ghé: thiếu thời lượng tham quan.
                  </p>
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
