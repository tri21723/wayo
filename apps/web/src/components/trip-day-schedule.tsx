"use client";

import { useRef, useState } from "react";
import type { TripRequest } from "@/lib/api";

type Schedule = NonNullable<TripRequest["day_schedule"]>;

export function readDaySchedule(form: FormData): Schedule {
  const labels = form.getAll("break_label");
  const starts = form.getAll("break_start");
  const ends = form.getAll("break_end");
  return {
    starts_at: String(form.get("activity_start")),
    ends_at: String(form.get("activity_end")),
    breaks: labels.map((label, index) => ({
      label: String(label),
      starts_at: String(starts[index]),
      ends_at: String(ends[index]),
    })),
  };
}

export function TripDaySchedule({
  initial,
  onChange,
}: {
  initial?: Schedule;
  onChange: () => void;
}) {
  const [breaks, setBreaks] = useState(() =>
    (initial?.breaks ?? []).map((rest, id) => ({ id, rest })),
  );
  const nextId = useRef(breaks.length);
  return (
    <fieldset className="choice-group constraint-group">
      <legend>Giờ hoạt động và nghỉ hằng ngày</legend>
      <p className="field-help">
        Áp dụng mỗi ngày theo giờ Việt Nam, trong cùng ngày. Khoảng nghỉ phải
        nằm trong giờ hoạt động và không trùng nhau. Sự kiện cố định được ưu
        tiên khi trùng giờ nghỉ. Chưa tự thêm bữa ăn hoặc thời gian di chuyển.
      </p>
      <div className="field-row">
        <label>
          Bắt đầu hoạt động
          <input
            name="activity_start"
            type="time"
            required
            defaultValue={initial?.starts_at ?? "09:00"}
          />
        </label>
        <label>
          Kết thúc hoạt động
          <input
            name="activity_end"
            type="time"
            required
            defaultValue={initial?.ends_at ?? "21:00"}
          />
        </label>
      </div>
      {breaks.length === 0 && <p>Chưa dành thời gian ăn/nghỉ hằng ngày.</p>}
      {breaks.map(({ id, rest }, index) => (
        <fieldset className="fixed-event" key={id}>
          <legend>Khoảng nghỉ {index + 1}</legend>
          <label>
            Tên khoảng nghỉ {index + 1}
            <input
              name="break_label"
              required
              maxLength={120}
              defaultValue={rest.label}
            />
          </label>
          <div className="field-row">
            <label>
              Bắt đầu nghỉ {index + 1}
              <input
                name="break_start"
                type="time"
                required
                defaultValue={rest.starts_at}
              />
            </label>
            <label>
              Kết thúc nghỉ {index + 1}
              <input
                name="break_end"
                type="time"
                required
                defaultValue={rest.ends_at}
              />
            </label>
          </div>
          <button
            type="button"
            className="text-button"
            onClick={() => {
              setBreaks((current) => current.filter((item) => item.id !== id));
              onChange();
            }}
          >
            Xóa khoảng nghỉ {index + 1}
          </button>
        </fieldset>
      ))}
      <button
        type="button"
        className="text-button"
        disabled={breaks.length >= 6}
        onClick={() => {
          const id = nextId.current++;
          setBreaks((current) => [
            ...current,
            { id, rest: { label: "", starts_at: "12:00", ends_at: "13:00" } },
          ]);
          onChange();
        }}
      >
        + Thêm khoảng nghỉ hằng ngày
      </button>
    </fieldset>
  );
}
