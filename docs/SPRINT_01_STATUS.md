# Sprint 01 — Foundation

Cập nhật: 07/10/2026. Đã có code cho auth và storage bản nháp; đã kết nối Supabase thật và chạy migration; chưa đạt M0 vì chưa nghiệm thu đăng nhập/lưu trip với tài khoản thật và chưa triển khai staging.

## Tiến độ task

| Task     | Trạng thái | Bằng chứng / phần còn lại                                                                                                             |
| -------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| PROD-01  | DOING      | Scope trong ADR 0001; provider/budget/nhân lực còn mở                                                                                 |
| PROD-02  | DONE       | Alpha spec có 9 user stories, acceptance và error paths                                                                               |
| PROD-03  | REVIEW     | Wireframe và các màn setup/login/trip list/editor; chưa walkthrough với người dùng                                                    |
| PROD-04  | DONE       | Spec phân biệt input validity, itinerary feasibility, budget và constraints                                                           |
| BASE-01  | REVIEW     | Repo, scripts, env examples, locks và README; chưa thử trên máy mới                                                                   |
| BASE-02  | REVIEW     | Web/API/OpenAPI/generated types/error contract; chờ staging                                                                           |
| BASE-03  | REVIEW     | SQLAlchemy + Alembic 0001, schema riêng; đã thử trên PostgreSQL tạm; đã áp dụng Supabase thật                                         |
| BASE-04  | REVIEW     | Supabase client + JWT verification + owner isolation; user đã xác nhận auth chạy đúng trên Supabase thật; admin authorization chưa có |
| BASE-05  | REVIEW     | Trip create/list/get/update/delete và UI đã implement; user đã xác nhận test local với Supabase thật thành công; staging chưa có      |
| BASE-06  | DOING      | CI bổ sung PostgreSQL và Playwright; chưa xác minh run mới trên GitHub, chưa deploy                                                   |
| DB-01    | DOING      | ERD/migrations users/trips có thật; profiles và catalog JSON đã có; schema chuẩn hóa destinations/tags/sources/hours còn thiếu                                    |
| DB-02/05 | TODO       | Revision trip draft không thay thế immutable itinerary version history/undo                                                           |
| TASTE-04 | DOING      | Form và validation có thể lưu; chưa anchor picker/fixed-event editor                                                                  |
| DATA-01  | DOING      | Capture template; chưa chọn nguồn và curate POI                                                                                       |
| QA-02/03 | DOING      | Auth/CRUD/validation tests và browser flows; planner/e2e provider thật chưa có                                                        |

Các task chỉ đánh dấu DONE khi đủ acceptance, không suy từ việc có code. Xem [plan chính](WAYO_IMPLEMENTATION_PLAN.md) và [ADR storage/auth](decisions/0002-trip-storage-and-auth.md).

## Đầu ra hiện có

- Form Đà Lạt 2–4 ngày, validation, budget scope và fixed-event constraints.
- Đăng ký/đăng nhập email/password, đăng xuất phiên local khi có cấu hình Supabase.
- Lưu trip private, danh sách phân trang, đọc/sửa/xóa có xác nhận; reload không mất dữ liệu DB.
- Idempotency khi retry create; revision check chống ghi đè hoặc xóa bản đã đổi ở tab khác.
- Token verification RS256/ES256, issuer/audience/expiry/role; owner lấy từ JWT, không từ client.
- Schema riêng `wayo`, bật RLS và không expose trực tiếp browser; app thực thi owner filter bằng backend.
- UI thiếu cấu hình vẫn cho dùng validation và giải thích tính năng tài khoản chưa mở.

## Kiểm chứng đợt storage/auth

- 39 test API qua trên PostgreSQL tạm, gồm các test validation, owner isolation, JWT và migration.
- Bộ storage/auth cũng đã qua SQLite test nhanh trước khi chạy PostgreSQL.
- Kiểm tra migration drift/rollback, lint/typecheck/build và Playwright đang được cập nhật trong đợt này.
- Browser tests mock Supabase/API; không thay thế live Supabase smoke test.
- Starlette TestClient có deprecation warning về httpx; test vẫn pass.
- Npm audit từng báo 5 high findings trong chuỗi tooling lint; cần theo dõi trước beta, chưa ép downgrade config Next.js để xử lý.

## Cấu hình còn thiếu

Đã có cấu hình local Supabase/database thật trong hai file `.env` được Git bỏ qua. Đã xác minh publishable key, email auth, JWKS ES256/RS256 tương thích và kết nối PostgreSQL qua TLS. Migration `0001` đã áp dụng: bảng `wayo.users`, `wayo.trips` có RLS; role `anon` và `authenticated` không có quyền truy cập trực tiếp schema. Alembic xác nhận schema khớp models. Người dùng đã xác nhận test auth và Trip CRUD thành công trên Supabase thật. Xem [hướng dẫn local auth/database](runbooks/LOCAL_AUTH_DATABASE.md).

Không có mock identity/auth bypass trong code runtime. Tests ký token riêng và dùng database dùng một lần. Chưa có credentials routing/weather/LLM, chưa có POI thật và chưa tạo itinerary AI.

## Bước tiếp theo

1. Nghiệm thu trang sở thích với tài khoản thật; triển khai staging.
2. DB-01 tiếp: destinations/places/evidence; DATA-01/03 curate POI có nguồn.
3. Snapshot/override taste cho trip, hoàn thiện onboarding và ranking baseline.
4. Itinerary schema/versioning + constraint planner + route provider.

## Đợt tiếp theo — Sở thích cá nhân (2026-10-07)

- [x] Trang `/profile`: sáu nhóm câu hỏi, lưu/sửa và tải lại khi có xung đột.
- [x] Profile API riêng theo JWT owner, schema version 1 và deterministic taste vector.
- [x] Migration 0002 đã áp dụng Supabase thật; bảng profile có RLS, browser roles không truy cập trực tiếp; Alembic không có schema drift. Test nâng từ 0001 giữ nguyên trip.
- [x] API tests cho persistence, isolation, validation, conflict và migration trên SQLite/PostgreSQL.
- [ ] Người dùng nghiệm thu profile trên Supabase thật.
- [ ] Wizard progress/back, trip snapshot/override và đánh giá onboarding với người dùng.
- [ ] Catalog POI có nguồn, importer và deterministic ranking.

Chi tiết quyết định: [ADR profile](decisions/0003-explicit-taste-profile.md). Các mục TASTE-01/03 chưa hoàn tất toàn bộ acceptance trong plan.

Kiểm tra đợt profile: 10 test profile/migration qua trên cả SQLite và PostgreSQL; các test API còn lại đã qua trong lượt toàn bộ trước đó. Lint, typecheck, format và production build đạt. Supabase đã ở revision 0002, không có schema drift.

Browser tests trên production build: **3/3 đạt**, gồm Trip CRUD, retry không tạo trùng và profile save/reload/conflict/sign-out. Lượt dev server trước đó timeout khi compile trang chi tiết; production không tái hiện.

## Catalog và discovery baseline (2026-10-07)

- [x] Migration 0003 thêm catalog private/RLS, JSON contract version 1 và nguồn theo nhóm dữ liệu.
- [x] CLI JSON import: dry-run mặc định, validate cả batch, upsert theo slug, kiểm tra trùng và rollback cả batch khi lỗi.
- [x] API gợi ý owner-scoped từ trip đã lưu, lọc verified/fresh/exclusions và sàng lọc giá riêng hoạt động khi hard budget.
- [x] Thứ tự deterministic theo số sở thích khớp, tie-break slug, tối đa hai địa điểm mỗi category.
- [x] UI gợi ý, nguồn, thiếu dữ liệu, lỗi/retry và phát hiện trip revision đã đổi.
- [ ] Curate 30–50 POI thật có nguồn (DATA-03); hiện catalog trống.
- [ ] Admin review/audit, schema chuẩn hóa đầy đủ, trip taste snapshot và ranker group/distance/time/season.

Đây là phần đầu của DB-01, DATA-02 và E05; chưa đánh dấu toàn bộ các task hoàn tất. Chi tiết: [ADR catalog](decisions/0004-curated-discovery.md), [hướng dẫn import](../data/README.md).

Kiểm chứng catalog: 64 test API qua trên SQLite/PostgreSQL, thêm test nâng migration giữ nguyên profile/trip qua cả hai database. 4/4 browser flows trên production đạt. Ruff, lint, typecheck, format và production build đạt. Migration 0003 đã áp dụng Supabase thật: không schema drift, cả bốn bảng có RLS, browser roles không có schema access. Không nhập fixture hay POI chưa xác minh vào Supabase.
