"use client";

import { useState, type FormEvent } from "react";
import { validateTrip, type TripRequest, type TripValidation } from "@/lib/api";

const tasteOptions = [
  "Cafe",
  "Thiên nhiên",
  "Chụp ảnh",
  "Đồ ăn local",
  "Văn hóa",
];
const avoidOptions = ["Trekking", "Nơi đông người", "Lịch quá dày"];
const money = new Intl.NumberFormat("vi-VN", {
  style: "currency",
  currency: "VND",
});

export function TripForm() {
  const [group, setGroup] = useState<"couple" | "friends">("couple");
  const [preferences, setPreferences] = useState([
    "Cafe",
    "Chụp ảnh",
    "Đồ ăn local",
  ]);
  const [exclusions, setExclusions] = useState(["Trekking"]);
  const [result, setResult] = useState<TripValidation | null>(null);
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  function toggle(
    value: string,
    values: string[],
    update: (next: string[]) => void,
  ) {
    update(
      values.includes(value)
        ? values.filter((item) => item !== value)
        : [...values, value],
    );
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending) return;
    const form = new FormData(event.currentTarget);
    // datetime-local contains no timezone. This product explicitly uses Vietnam time.
    const trip: TripRequest = {
      destination_id: "da-lat",
      origin: String(form.get("origin")),
      arrival_at: `${form.get("arrival")}+07:00`,
      departure_at: `${form.get("departure")}+07:00`,
      timezone: "Asia/Ho_Chi_Minh",
      people_count: group === "couple" ? 2 : Number(form.get("people")),
      group_type: group,
      budget: {
        amount_vnd: Number(form.get("budget")),
        scope: form.get("scope") as "per_person" | "group",
        mode: form.get("hard_budget") ? "hard" : "soft",
        currency: "VND",
      },
      transport_mode: "driving",
      pace: form.get("pace") as TripRequest["pace"],
      preferences,
      exclusions,
      fixed_events: [],
      anchor: null,
    };
    setPending(true);
    setResult(null);
    setError("");
    try {
      setResult(await validateTrip(trip));
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Có lỗi kết nối. Vui lòng thử lại.",
      );
    } finally {
      setPending(false);
    }
  }

  return (
    <section className="form-card" aria-labelledby="trip-heading">
      <div className="section-heading">
        <span className="step">01</span>
        <div>
          <h2 id="trip-heading">Phác thảo chuyến đi</h2>
          <p>Đà Lạt · 2–4 ngày · Couple hoặc nhóm bạn</p>
        </div>
      </div>
      <form
        onSubmit={submit}
        onChange={() => {
          setResult(null);
          setError("");
        }}
      >
        <fieldset disabled={pending} className="form-fields">
          <legend className="sr-only">Thông tin chuyến đi</legend>
          <div className="field-row">
            <label>
              Xuất phát từ
              <input
                name="origin"
                defaultValue="TP.HCM"
                required
                maxLength={120}
                autoComplete="off"
              />
            </label>
            <label>
              Điểm đến
              <input value="Đà Lạt" readOnly />
            </label>
          </div>
          <div className="field-row">
            <label>
              Đến Đà Lạt lúc
              <input
                name="arrival"
                type="datetime-local"
                required
                aria-describedby="date-help"
              />
            </label>
            <label>
              Rời Đà Lạt lúc
              <input
                name="departure"
                type="datetime-local"
                required
                aria-describedby="date-help"
              />
            </label>
          </div>
          <p className="field-help" id="date-help">
            Giờ Việt Nam (UTC+7). Tính từ ngày đến đến ngày về, tối đa 4 ngày.
          </p>
          <div className="field-row">
            <label>
              Người đồng hành
              <select
                name="group"
                value={group}
                onChange={(event) =>
                  setGroup(event.target.value as "couple" | "friends")
                }
              >
                <option value="couple">Hai người / Couple</option>
                <option value="friends">Nhóm bạn</option>
              </select>
            </label>
            <label>
              Số người
              {group === "couple" ? (
                <input value="2" readOnly />
              ) : (
                <input
                  name="people"
                  type="number"
                  defaultValue="3"
                  min="1"
                  max="4"
                  step="1"
                  required
                />
              )}
            </label>
          </div>
          <div className="field-row">
            <label>
              Ngân sách (VND)
              <input
                name="budget"
                type="number"
                defaultValue="4000000"
                min="1"
                max="1000000000"
                step="1"
                required
              />
            </label>
            <label>
              Cách tính
              <select name="scope" defaultValue="per_person">
                <option value="per_person">Mỗi người / toàn chuyến</option>
                <option value="group">Cả nhóm / toàn chuyến</option>
              </select>
            </label>
          </div>
          <p className="field-help">
            Dự kiến gồm đi lại, lưu trú, ăn uống, trải nghiệm và dự phòng.
          </p>
          <label className="checkbox">
            <input type="checkbox" name="hard_budget" />
            Không vượt ngân sách dự toán
          </label>
          <div className="field-row">
            <label>
              Nhịp đi
              <select name="pace" defaultValue="relaxed">
                <option value="relaxed">Thảnh thơi</option>
                <option value="balanced">Cân bằng</option>
                <option value="active">Nhiều trải nghiệm</option>
              </select>
            </label>
            <label>
              Di chuyển nội đô
              <select name="transport">
                <option value="driving">Ô tô / taxi</option>
              </select>
            </label>
          </div>
          <fieldset className="choice-group">
            <legend>Bạn thích trải nghiệm nào?</legend>
            <div className="chips">
              {tasteOptions.map((taste) => (
                <button
                  type="button"
                  key={taste}
                  aria-pressed={preferences.includes(taste)}
                  onClick={() => {
                    toggle(taste, preferences, setPreferences);
                    setResult(null);
                    setError("");
                  }}
                >
                  {taste}
                </button>
              ))}
            </div>
          </fieldset>
          <fieldset className="choice-group">
            <legend>Bạn muốn tránh điều gì?</legend>
            <div className="chips">
              {avoidOptions.map((avoid) => (
                <button
                  type="button"
                  key={avoid}
                  aria-pressed={exclusions.includes(avoid)}
                  onClick={() => {
                    toggle(avoid, exclusions, setExclusions);
                    setResult(null);
                    setError("");
                  }}
                >
                  {avoid}
                </button>
              ))}
            </div>
          </fieldset>
          <button className="primary" type="submit">
            {pending ? "Đang kiểm tra…" : "Kiểm tra thông tin chuyến đi"}
            <span aria-hidden="true">↗</span>
          </button>
        </fieldset>
        <p className="field-help">
          Thông tin chỉ dùng để kiểm tra, chưa được lưu.
        </p>
        {error && (
          <div className="message error" role="alert">
            {error}
          </div>
        )}
        {result && (
          <div className="message success" role="status">
            <h3>Thông tin đầu vào hợp lệ</h3>
            <p>
              {result.trip_days} ngày · {result.trip.people_count} người · Tổng
              ngân sách {money.format(result.total_budget_vnd)}
            </p>
            <ul>
              {result.notices.map((notice) => (
                <li key={notice.code}>{notice.message}</li>
              ))}
            </ul>
          </div>
        )}
      </form>
    </section>
  );
}
