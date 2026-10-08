"use client";

import { useRef, useState } from "react";
import { TripDaySchedule, readDaySchedule } from "./trip-day-schedule";
import type { TripRequest } from "@/lib/api";

function vietnamTime(value: string) {
  return new Date(new Date(value).getTime() + 7 * 60 * 60 * 1000)
    .toISOString()
    .slice(0, 23);
}

function eventTime(value: string, original?: string) {
  const local = `${value}+07:00`;
  // Retain original timezone/precision when an existing time wasn't edited.
  return original && new Date(local).getTime() === new Date(original).getTime()
    ? original
    : local;
}

export function readConstraints(form: FormData, initial?: TripRequest) {
  const labels = form.getAll("event_label");
  const starts = form.getAll("event_start");
  const ends = form.getAll("event_end");
  const ids = form.getAll("event_id");
  return {
    day_schedule: readDaySchedule(form),
    anchor: form.has("use_anchor")
      ? {
          label: String(form.get("anchor_label")),
          latitude: Number(form.get("anchor_latitude")),
          longitude: Number(form.get("anchor_longitude")),
        }
      : null,
    fixed_events: labels.map((label, index) => {
      const original = initial?.fixed_events?.[Number(ids[index])];
      return {
        label: String(label),
        starts_at: eventTime(String(starts[index]), original?.starts_at),
        ends_at: eventTime(String(ends[index]), original?.ends_at),
      };
    }),
  };
}

export function TripConstraints({
  initial,
  onChange,
}: {
  initial?: TripRequest;
  onChange: () => void;
}) {
  const [anchorEnabled, setAnchorEnabled] = useState(Boolean(initial?.anchor));
  const [events, setEvents] = useState<
    { id: number; event?: NonNullable<TripRequest["fixed_events"]>[number] }[]
  >(() => (initial?.fixed_events ?? []).map((event, id) => ({ id, event })));
  const nextId = useRef(events.length);
  return (
    <>
      <TripDaySchedule initial={initial?.day_schedule} onChange={onChange} />
      <fieldset className="choice-group constraint-group">
        <legend>Điểm lưu trú / điểm xuất phát</legend>
        <p className="field-help">
          Thêm tọa độ khách sạn hoặc nơi bắt đầu di chuyển tại Đà Lạt. Hiện chưa
          có tìm kiếm địa chỉ trên bản đồ.
        </p>
        <label className="checkbox">
          <input
            type="checkbox"
            name="use_anchor"
            checked={anchorEnabled}
            onChange={(event) => {
              setAnchorEnabled(event.target.checked);
              onChange();
            }}
          />
          Tôi đã có điểm lưu trú / xuất phát
        </label>
        <fieldset
          disabled={!anchorEnabled}
          hidden={!anchorEnabled}
          className="anchor-fields"
        >
          <legend className="sr-only">Thông tin điểm lưu trú</legend>
          <label>
            Tên điểm lưu trú / xuất phát
            <input
              name="anchor_label"
              defaultValue={initial?.anchor?.label ?? ""}
              required
              maxLength={120}
            />
          </label>
          <div className="field-row">
            <label>
              Vĩ độ
              <input
                name="anchor_latitude"
                type="number"
                step="any"
                min={-90}
                max={90}
                required
                defaultValue={initial?.anchor?.latitude ?? ""}
              />
            </label>
            <label>
              Kinh độ
              <input
                name="anchor_longitude"
                type="number"
                step="any"
                min={-180}
                max={180}
                required
                defaultValue={initial?.anchor?.longitude ?? ""}
              />
            </label>
          </div>
          <p className="field-help">
            Nhập tọa độ thập phân, ví dụ vĩ độ 11.94 và kinh độ 108.44. Tọa độ
            chưa được đối chiếu với địa chỉ.
          </p>
        </fieldset>
      </fieldset>
      <fieldset className="choice-group constraint-group">
        <legend>Sự kiện cố định</legend>
        <p className="field-help">
          Giữ thời gian cho lịch hẹn, vé tham quan hoặc bữa ăn đã đặt. Giờ Việt
          Nam (UTC+7); sự kiện phải nằm trong chuyến đi và không trùng nhau. Tối
          đa 20 sự kiện.
        </p>
        {events.length === 0 && <p>Chưa có sự kiện cố định.</p>}
        {events.map(({ id, event }, index) => (
          <fieldset className="fixed-event" key={id}>
            <legend>Sự kiện {index + 1}</legend>
            <input type="hidden" name="event_id" value={id} />
            <label>
              Tên sự kiện {index + 1}
              <input
                name="event_label"
                required
                maxLength={120}
                defaultValue={event?.label ?? ""}
              />
            </label>
            <div className="field-row">
              <label>
                Bắt đầu sự kiện {index + 1}
                <input
                  name="event_start"
                  type="datetime-local"
                  step="any"
                  required
                  defaultValue={event ? vietnamTime(event.starts_at) : ""}
                />
              </label>
              <label>
                Kết thúc sự kiện {index + 1}
                <input
                  name="event_end"
                  type="datetime-local"
                  step="any"
                  required
                  defaultValue={event ? vietnamTime(event.ends_at) : ""}
                />
              </label>
            </div>
            <button
              type="button"
              className="text-button"
              onClick={() => {
                setEvents((current) =>
                  current.filter((item) => item.id !== id),
                );
                onChange();
              }}
            >
              Xóa sự kiện {index + 1}
            </button>
          </fieldset>
        ))}
        <button
          type="button"
          className="text-button"
          disabled={events.length >= 20}
          onClick={() => {
            const id = nextId.current++;
            setEvents((current) => [...current, { id, event: undefined }]);
            onChange();
          }}
        >
          + Thêm sự kiện cố định
        </button>
      </fieldset>
    </>
  );
}
