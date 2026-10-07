# Alpha — Wireframe luồng chính

Liên quan PROD-03. Đây là wireframe mức cấu trúc; visual card/map/editor chi tiết sẽ làm khi có contract itinerary. Màn nhập trip đã được hiện thực ở `apps/web/src/app/page.tsx`.

## Flow

```text
Landing → Onboarding → Trip setup → Sign in/save → Generate
                                                   ↓
Trip list ←────────────────────────────────── Workspace
                                                   ↓
                                     Edit/replan → Diff/Undo
                                                   ↓
                                             Share snapshot

Admin (role riêng) → Place list → Detail/edit/verify
```

Alpha bỏ màn chọn nhiều destination, hiển thị Đà Lạt cố định. Trong foundation, form dừng ở “Kiểm tra thông tin”; không hiển thị nút tạo lịch chưa hoạt động.

## Desktop workspace mục tiêu

```text
┌ Wayo ─ Trip title ─ Version ─ Budget ─ Share ┐
│ Day 1 / Day 2 / Day 3      Validation status │
├───────────────────────┬─────────────────────┤
│ Timeline              │ Map                 │
│ start-end / place     │ markers + route      │
│ price / reason/source │ selected place       │
│ travel to next        │ detail panel         │
│ replace/delete/lock   │                      │
├───────────────────────┴─────────────────────┤
│ Ask Wayo…        / change summary / undo     │
└─────────────────────────────────────────────┘
```

Mobile: header → day tabs → List/Map toggle → cards → copilot drawer. Không ép map cạnh timeline trên màn nhỏ. Buttons thay thế drag & drop, mọi input có label, kết quả thay đổi có status announcement.

## Nội dung và state từng màn

| Màn        | Thành phần                                                              | Empty/loading/error                                   |
| ---------- | ----------------------------------------------------------------------- | ----------------------------------------------------- |
| Landing    | Value proposition, bắt đầu trip, giải thích scope Đà Lạt                | Không quảng cáo tính năng chưa release                |
| Onboarding | Progress, visual choices, back/skip                                     | Default được ghi rõ; giữ bước khi retry               |
| Trip setup | Origin, arrival/departure, group, budget/scope, pace, mode, preferences | Inline/global error, không reset form khi lỗi         |
| Trip list  | Tên trip, dates, status, tạo trip                                       | Empty CTA; private loading; auth expired              |
| Workspace  | Day tabs, timeline, map, budget, copilot, version                       | Generating progress; infeasible reasons; map fallback |
| Share      | Read-only version, days, cost, source                                   | Revoked/expired generic message, không leak metadata  |
| Admin      | Search/filter stale/unknown, edit/disable/verify/source                 | Permission denied; validation conflict; import errors |

## Replan interaction

1. User gửi intent hoặc mở đề xuất forecast.
2. Hiển thị đang xử lý, tránh double-submit.
3. User-requested: commit khi hợp lệ, show diff + undo. Forecast chủ động: show preview, user accept mới commit.
4. Error/infeasible: giữ nguyên lịch, hiển thị nguyên nhân và cách thử lại.
