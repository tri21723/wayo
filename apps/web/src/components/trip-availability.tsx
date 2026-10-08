"use client";

import { useState } from "react";
import { getAvailability, type TripAvailability } from "@/lib/api";

function time(value: string) {
  return new Date(value).toLocaleTimeString("vi-VN", {
    timeZone: "Asia/Ho_Chi_Minh",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function TripAvailabilityPanel({
  tripId,
  revision,
}: {
  tripId: string;
  revision: number;
}) {
  const [data, setData] = useState<TripAvailability | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  async function load() {
    if (pending) return;
    setPending(true);
    setError("");
    setData(null);
    try {
      const result = await getAvailability(tripId);
      if (result.trip_revision !== revision)
        throw new Error(
          "Chuyến đi đã thay đổi. Hãy tải lại bản đã lưu trước khi xem thời gian.",
        );
      setData(result);
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Chưa tải được thời gian chuyến đi.",
      );
    } finally {
      setPending(false);
    }
  }
  return (
    <section
      className="form-card availability"
      aria-labelledby="availability-heading"
    >
      <h2 id="availability-heading">Thời gian theo ngày</h2>
      <p>
        Dựa trên giờ đến/về, giờ hoạt động, khoảng nghỉ và sự kiện đã lưu. Hãy
        lưu thay đổi trước khi xem.
      </p>
      <button
        type="button"
        className="primary"
        disabled={pending}
        onClick={load}
      >
        {pending ? "Đang tính thời gian…" : "Xem thời gian theo ngày"}
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
          <div className="availability-days">
            {data.days.map((day) => (
              <article key={day.date} className="place-card">
                <h3>Ngày {day.date.split("-").reverse().join("/")}</h3>
                <p>
                  Còn {Math.floor(day.available_minutes)} phút trong giờ hoạt
                  động tham khảo.
                </p>
                {day.blocks.length === 0 ? (
                  <p>Không có khoảng thời gian trong ngày này.</p>
                ) : (
                  <ol className="time-blocks">
                    {day.blocks.map((block) => (
                      <li
                        className={`time-block ${block.kind}`}
                        key={`${block.starts_at}:${block.kind}`}
                      >
                        <span>
                          {time(block.starts_at)}–{time(block.ends_at)}
                          {block.ends_at.slice(0, 10) !== day.date
                            ? " (ngày kế tiếp)"
                            : ""}
                        </span>
                        <strong>{block.label}</strong>
                      </li>
                    ))}
                  </ol>
                )}
              </article>
            ))}
          </div>
        </>
      )}
    </section>
  );
}
