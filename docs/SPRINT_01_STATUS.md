# Sprint 01 — Foundation

Cập nhật: 07/10/2026. Mục tiêu đợt đầu: spec alpha + bộ khung web/API + contract trip được kiểm thử. Chưa đạt milestone M0 vì auth, persistence và staging chưa triển khai.

## Tiến độ task

| Task     | Trạng thái       | Bằng chứng / phần còn lại                                                                             |
| -------- | ---------------- | ----------------------------------------------------------------------------------------------------- |
| PROD-01  | DOING            | ADR 0001 xác định scope; D08 provider/budget và D10 nhân lực còn mở                                   |
| PROD-02  | DONE             | `docs/product/ALPHA_SPEC.md`: 9 stories, acceptance và error paths                                    |
| PROD-03  | REVIEW           | `docs/product/WIREFRAMES.md`; form setup có code, chưa walkthrough mọi màn với người dùng             |
| PROD-04  | DONE             | Spec phân biệt input_valid/valid/unknown/infeasible, budget, time, fixed events                       |
| BASE-01  | REVIEW           | Monorepo folders, README, scripts, env examples, runtime pin, dependency locks; chưa thử trên máy mới |
| BASE-02  | REVIEW           | Next.js/FastAPI, health, validation endpoint, OpenAPI + generated types + error contract; chờ staging |
| BASE-06  | DOING            | Có workflow kiểm tra và remote GitHub; chưa xác minh CI trên GitHub hoặc deploy staging               |
| TASTE-04 | DOING (một phần) | Form và backend validation; chưa có anchor picker/fixed-event editor/persistence                      |
| DATA-01  | DOING (một phần) | Có capture template và quy tắc field; chưa chọn nguồn/rights/provenance schema cuối                   |
| QA-02    | DOING (một phần) | Test input API; chưa có ranking/planner/auth để test                                                  |

Các task khác giữ TODO; không đánh dấu triển khai auth/DB/planner hoàn tất từ form demo.

## Những gì dùng được

- Mở web tiếng Việt và nhập chuyến đi Đà Lạt 2–4 ngày.
- Kiểm tra ngày giờ/timezone, số người, ngân sách theo người/nhóm, fixed event bounds/overlap và mâu thuẫn preferences/exclusions qua API.
- Hiển thị lỗi/kết quả và giữ form khi API không kết nối được.
- Tính tổng cap nhóm; đây chưa phải dự toán chi phí.
- Sinh TypeScript từ schema backend, kèm workflow phát hiện contract drift.

## Kiểm chứng

Kết quả cuối đợt: kiểm tra local đã qua. Các lệnh tái hiện nằm trong README; CI trên GitHub và staging chưa chạy.

- Web: ESLint pass, `next typegen + tsc --noEmit` pass, production build pass. Next.js build cần chạy ngoài sandbox hạn chế.
- HTTP smoke test trên production server: trang chủ 200; trip hợp lệ qua proxy trả 200 và tổng budget đúng; ngày sai trả 422; JSON lỗi trả 400; backend tắt trả 503 `API_UNAVAILABLE`.
- OpenAPI snapshot khớp backend; TypeScript được sinh từ snapshot. Prettier kiểm tra toàn bộ file thuộc phạm vi thành công.
- API: 20 test đã pass; Ruff lint/format pass. TestClient bị treo trong sandbox hạn chế, cùng bộ test pass ngoài sandbox.
- Có một deprecation warning của Starlette TestClient về httpx; chưa ảnh hưởng kết quả test. Theo dõi khi nâng dependency test.
- Npm audit: 5 high findings cùng chuỗi lint `eslint-config-next → @next/eslint-plugin-next → fast-glob → micromatch → braces`. Đây là dev dependency; không áp dụng `audit fix --force` vì đề xuất hạ config về Next 14 trong project Next 16. Cần xử lý/đánh giá lại trước beta.
- Chưa có visual browser test hoặc kiểm thử accessibility tự động; mới có responsive CSS và native form labels.

## Giới hạn môi trường

Đã khởi tạo Git trên nhánh `main` và kết nối remote `origin` tới `https://github.com/tri21723/wayo.git`. Workflow CI đã viết; trạng thái chạy trên GitHub chưa được xác minh. Không có credentials Supabase, routing, weather hoặc LLM được cấu hình; phần hiện tại không yêu cầu chúng.

## Tiếp theo

1. DB-01/02: ERD và migrations PostgreSQL cho users/profiles/trips/places/versions.
2. BASE-04/05: Supabase Auth, owner isolation, Trip CRUD; kiểm thử hai user.
3. Chọn môi trường staging và cấu hình secrets ngoài source; chạy end-to-end save/read trip.
4. Hoàn thiện DATA-01 rồi curate 10 POI thật có nguồn để kiểm chứng schema.
