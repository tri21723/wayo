# Sprint 01 — Foundation

Cập nhật: 08/10/2026. User chọn hoàn tất foundation local và chuẩn bị deployment. Auth/Trip CRUD đã được user nghiệm thu trên Supabase thật; foundation local có operational probes, admin guard, provider adapters và standalone deployment. M0 staging chưa hoàn tất; xem [checklist local](FOUNDATION_CHECKLIST.md).

## Tiến độ task

| Task     | Trạng thái | Bằng chứng / phần còn lại                                                                                                                                             |
| -------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROD-01  | DOING      | Scope trong ADR 0001; provider/budget/nhân lực còn mở                                                                                                                 |
| PROD-02  | DONE       | Alpha spec có 9 user stories, acceptance và error paths                                                                                                               |
| PROD-03  | REVIEW     | Wireframe và các màn setup/login/trip list/editor; chưa walkthrough với người dùng                                                                                    |
| PROD-04  | DONE       | Spec phân biệt input validity, itinerary feasibility, budget và constraints                                                                                           |
| BASE-01  | REVIEW     | Repo, scripts, env examples, locks và README; đã kiểm chứng cài từ source sạch local; staging gate còn mở                                                             |
| BASE-02  | REVIEW     | Web/API/OpenAPI/types, error contract, readiness/logs, standalone; chờ staging                                                                                        |
| BASE-03  | REVIEW     | SQLAlchemy + Alembic 0001, schema riêng; đã thử trên PostgreSQL tạm; đã áp dụng Supabase thật                                                                         |
| BASE-04  | REVIEW     | Supabase client + JWT verification + owner isolation; user đã xác nhận auth chạy đúng trên Supabase thật; admin allowlist server-only đã có; chưa có admin catalog UI |
| BASE-05  | REVIEW     | Trip create/list/get/update/delete và UI đã implement; user đã xác nhận test local với Supabase thật thành công; staging chưa có                                      |
| BASE-06  | DOING      | CI thêm PostgreSQL/browser/container build+smoke; artifact deployment và Docker Desktop smoke đã qua; chưa xác minh GitHub/staging                                    |
| BASE-07  | DOING      | Adapter OSRM/Open-Meteo/OpenAI + contract tests, timeout/usage caps; live qualification/model/cost còn mở                                                             |
| DB-01    | DOING      | ERD/migrations users/trips có thật; profiles và catalog JSON đã có; schema chuẩn hóa destinations/tags/sources/hours còn thiếu                                        |
| DB-02/05 | TODO       | Revision trip draft không thay thế immutable itinerary version history/undo                                                                                           |
| TASTE-04 | DOING      | Anchor/fixed events/day schedule đã có; map picker và travel validation còn thiếu                                                                                     |
| DATA-01  | DOING      | Capture template; chưa chọn nguồn và curate POI                                                                                                                       |
| QA-02/03 | DOING      | Auth/CRUD/validation tests và browser flows; planner/e2e provider thật chưa có                                                                                        |

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
3. Hoàn thiện onboarding wizard, curate POI thật và ranking group/time/distance.
4. Itinerary schema/versioning + constraint planner + route provider.

## Đợt tiếp theo — Sở thích cá nhân (2026-10-07)

- [x] Trang `/profile`: sáu nhóm câu hỏi, lưu/sửa và tải lại khi có xung đột.
- [x] Profile API riêng theo JWT owner, schema version 1 và deterministic taste vector.
- [x] Migration 0002 đã áp dụng Supabase thật; bảng profile có RLS, browser roles không truy cập trực tiếp; Alembic không có schema drift. Test nâng từ 0001 giữ nguyên trip.
- [x] API tests cho persistence, isolation, validation, conflict và migration trên SQLite/PostgreSQL.
- [ ] Người dùng nghiệm thu profile trên Supabase thật.
- [ ] Wizard progress/back và đánh giá onboarding với người dùng; snapshot/override đã hoàn tất ở đợt sau.
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
- [ ] Admin review/audit, schema chuẩn hóa đầy đủ và ranker group/distance/time/season.

Đây là phần đầu của DB-01, DATA-02 và E05; chưa đánh dấu toàn bộ các task hoàn tất. Chi tiết: [ADR catalog](decisions/0004-curated-discovery.md), [hướng dẫn import](../data/README.md).

Kiểm chứng catalog: 64 test API qua trên SQLite/PostgreSQL, thêm test nâng migration giữ nguyên profile/trip qua cả hai database. 4/4 browser flows trên production đạt. Ruff, lint, typecheck, format và production build đạt. Migration 0003 đã áp dụng Supabase thật: không schema drift, cả bốn bảng có RLS, browser roles không có schema access. Không nhập fixture hay POI chưa xác minh vào Supabase.

## Snapshot sở thích theo chuyến đi (2026-10-07)

- [x] Áp dụng profile vào form tạo/sửa trip; lưu snapshot answers + revision nguồn.
- [x] Chỉnh preferences/exclusions/pace/diet/crowd/adventure riêng cho trip, không ghi profile.
- [x] Xác minh nguồn snapshot theo owner và revision; giữ snapshot cũ sau khi profile thay đổi.
- [x] Tương thích trip/hash tạo cũ, bảo toàn trường mới khi editor cũ không gửi.
- [x] Discovery v2 lọc dietary có evidence, ưu tiên crowd/effort theo sở thích, không nới exclusions.
- [ ] Nghiệm thu luồng áp dụng profile với tài khoản Supabase thật.

Không cần migration hoặc biến môi trường mới. TASTE-03 hoàn tất phần API/UI snapshot và override; wizard onboarding và dữ liệu POI thật vẫn còn. Chi tiết: [ADR 0005](decisions/0005-trip-taste-snapshot.md).

Kiểm chứng snapshot hoàn tất ngày 2026-10-08: 70 test API đã qua trên SQLite và PostgreSQL; bộ snapshot được chạy lại sau chỉnh sửa tương thích editor cũ và đạt trên cả hai. Cả 6 browser flows đã đạt (5 ở lượt chung, test apply/override chạy lại đạt sau sửa selector combobox). Production build, lint, typecheck, Ruff và format đạt. Tests trình duyệt dùng Auth/API mock, chưa thay thế nghiệm thu Supabase thật.

## Điểm lưu trú và sự kiện cố định (2026-10-08)

- [x] Form tạo/sửa trip có tên + tọa độ điểm lưu trú/xuất phát; có thể bỏ chọn để xóa.
- [x] Thêm/xóa tối đa 20 sự kiện cố định, nhập giờ Việt Nam; giữ đúng nội dung các dòng còn lại khi xóa một dòng.
- [x] Lưu/đọc lại bằng contract anchor/fixed_events đã có; thay đổi dữ liệu hủy kết quả validation cũ.
- [x] Thời gian sự kiện không chỉnh sửa giữ nguyên timezone/độ chính xác đã lưu.
- [ ] Tìm địa chỉ/chọn điểm trên bản đồ, xác minh vị trí và địa điểm cụ thể của sự kiện.
- [ ] Thời gian nghỉ theo ngày và kiểm tra khả thi di chuyển giữa các sự kiện.

TASTE-04 vẫn chưa hoàn tất toàn bộ acceptance. Không thêm migration, provider hoặc biến môi trường. Tọa độ nhập tay chỉ kiểm tra miền hợp lệ; chưa xác minh khớp địa chỉ hay nằm trong vùng phục vụ. Giờ sự kiện được API kiểm tra nằm trong trip, kết thúc sau bắt đầu và không chồng lấn.

Kiểm chứng thiết lập chuyến đi: 50 test API validation/storage qua trên SQLite tạm; 7/7 browser flows qua trên production build, bao gồm giữ nguyên timestamp có timezone/độ chính xác khi không sửa. Lint, typecheck, format, Ruff và build đạt. Browser tests mock Auth/API; cần nghiệm thu bằng tài khoản thật.

## Bảng thời gian theo ngày (2026-10-08)

- [x] API owner-scoped tính block fixed/available/outside_activity_hours từ trip đã lưu.
- [x] Giới hạn theo giờ đến/về, timezone Việt Nam, tách booking qua đêm và giữ ngày về đúng nửa đêm.
- [x] UI xem từng ngày, sự kiện cố định, số phút còn lại; retry và từ chối revision cũ.
- [ ] Thời gian ăn/nghỉ, buffer, travel matrix, opening-hour validation và phân bổ POI.

Khung tham khảo 09:00–21:00; khoảng trống chưa đảm bảo khả thi ghé thăm địa điểm. Không tạo itinerary/version hay cần migration. PLAN-03/04 vẫn chưa hoàn tất. Chi tiết: [ADR 0006](decisions/0006-daily-availability.md).

Kiểm chứng bảng thời gian: 6 test API mới qua trên SQLite tạm; 8/8 browser flows qua trên production build. Ruff, lint, typecheck, format và build đạt. Browser tests dùng Auth/API mock; còn nghiệm thu với tài khoản Supabase thật.

## Giờ mở cửa và giờ có thể ghé (2026-10-08)

- [x] Discovery v3 giao lịch mở cửa theo tuần với thời gian trống của trip.
- [x] Loại địa điểm đóng cửa trong các ngày đi hoặc không còn khoảng liên tục đủ duration.
- [x] Phân biệt thiếu hours/duration với không có khoảng phù hợp, không tự đoán dữ liệu.
- [x] UI hiển thị giờ bắt đầu sớm/muộn và hạn kết thúc, cùng giới hạn chưa tính route/rest/ngoại lệ.
- [ ] Lịch ngoại lệ/ngày lễ, thời gian nghỉ, routing, itinerary scheduler và POI thật.

Không cần migration hoặc cấu hình thêm. PLAN-03 có thêm validation weekly windows; chưa hoàn tất hard-constraint validator đầy đủ. Chi tiết: [ADR 0007](decisions/0007-opening-hours-and-visit-windows.md).

Kiểm chứng giờ có thể ghé: toàn bộ 88 test API qua trên SQLite tạm, 8/8 browser flows qua trên production build (discovery kiểm tra cả window có đủ dữ liệu và hours chưa biết). Ruff, lint, typecheck, format và build đạt. Chưa nhập POI thật, chưa kiểm chứng lịch ngoại lệ hoặc route provider.

## Giờ hoạt động và khoảng nghỉ hằng ngày (2026-10-08)

- [x] Trip setup lưu khung giờ cùng ngày và tối đa 6 khoảng nghỉ lặp mỗi ngày; kiểm tra trong khung và không trùng nhau.
- [x] Bảng thời gian hiển thị rest; giữ sự kiện khi trùng nghỉ và không trừ thời gian hai lần.
- [x] Discovery dùng khoảng trống đã loại giờ nghỉ để kiểm tra giờ ghé.
- [x] Trip cũ mặc định 09:00–21:00 không nghỉ; giữ retry hash và cấu hình khi client cũ không gửi trường mới.
- [ ] Lịch riêng từng ngày, tự xếp bữa ăn/nghỉ theo pace, buffer và routing.

Không cần migration hoặc cấu hình Supabase thêm. PLAN-04 và TASTE-04 vẫn chưa hoàn tất toàn bộ; xem [ADR 0008](decisions/0008-custom-daily-schedule.md). Các giới hạn 09:00–21:00 và chưa tính giờ nghỉ trong ghi chú trước được thay bằng cấu hình mới này.

Kiểm chứng: toàn bộ 98 test API qua trên SQLite tạm và 8/8 browser flows qua trên production build; Ruff, lint, TypeScript, format và production build đạt. CI bổ sung test lịch hằng ngày vào lượt PostgreSQL. Kiểm thử trình duyệt dùng Auth/API mock, không thay nghiệm thu bằng tài khoản Supabase thật.

## Hoàn tất engineering foundation local (2026-10-08)

Theo phạm vi user chọn: local + chuẩn bị deployment. [Checklist foundation](FOUNDATION_CHECKLIST.md) tách gate local khỏi M0 staging.

- [x] Readiness kiểm tra database, migration và Auth config; BFF `/api/health` và smoke script.
- [x] Admin dependency từ allowlist server-only, deny mặc định, không tin metadata do client gửi.
- [x] Request ID, JSON metadata logs, body cap 64 KiB và error contract 500 đã redaction.
- [x] Ba adapter provider, default disabled, giới hạn operation/call/token/response, typed failure, không automatic retry/cache.
- [x] Dockerfiles/Compose không chứa dotenv; standalone launcher, migration job, health dependency và environment guard cho TLS.
- [x] CI và deployment/provider runbooks cập nhật; checklist tổng giữ các gate ngoài local chưa hoàn tất.

Kiểm chứng: 132 test API qua trên SQLite và PostgreSQL tạm, migration/RLS/owner/admin/readiness đạt. Provider tests dùng HTTP mock; không gọi LLM trả phí, không chạm dữ liệu Supabase thật. Docker Engine chưa hoạt động trong WSL; không coi image build/run hoặc GitHub workflow là đã xác minh.

Nghiệm thu cuối: 8 browser flows chính qua bằng standalone launcher; case BFF mới qua khi chạy lại với raw invalid JSON (tổng 9 flows). Cài Node/Python từ source sạch không dotenv thành công, pip check không lỗi; build và toàn bộ 132 tests trên venv sạch cũng qua. Smoke HTTP web standalone cổng riêng → API → PostgreSQL trả ready, homepage 200 và X-Request-ID được forward. Ba CLI provider inspection đều có calls=0. Không dừng dev server của user.

## Nghiệm thu Docker Desktop (2026-10-08)

- [x] Docker Desktop 29.5.2 / Compose 5.1.4 kết nối WSL; build API và web images thành công.
- [x] Project `wayo-foundation-check` chạy PostgreSQL 16 dùng một lần, migrate exit 0 ở head 0003; cả 4 bảng app bật RLS.
- [x] PostgreSQL/API/web healthy; smoke web → API → DB ready, homepage 200, private route 401, valid trip 200 và invalid day schedule 422.
- [x] API/web chạy UID 10001; không có dotenv trong runtime; provider mặc định disabled; request ID đi qua BFF.
- [x] Lưu Compose smoke override/config mẫu và cập nhật CI dùng cùng quy trình đã kiểm chứng.

Giới hạn Docker/WSL ở ghi chú trước đã được giải quyết sau khi user mở Docker Desktop. Cấu hình Auth là project/key giả chỉ cho smoke; không thay nghiệm thu Supabase thật. Container/database/network smoke được dọn sau kiểm chứng; images còn trong cache. Không đổi dữ liệu Supabase hoặc dev server của user. GitHub run và staging vẫn chưa nghiệm thu.

## Review sau foundation local (2026-10-08)

Đã sửa guard public Supabase key trước build, state/response cũ khi đổi phiên trên form tạo trip và request ID của BFF 204. API 132 tests và browser 12 flows đã qua; xem [review đầy đủ](FOUNDATION_REVIEW.md) để phân biệt kết quả mới với bằng chứng Docker/PostgreSQL trước đó. Phạm vi local giữ nguyên; staging và live provider qualification còn mở.

Kế hoạch triển khai hiện hành: [M1 Data & taste, chuẩn bị M2](NEXT_PHASE_PLAN.md), ưu tiên dictionary/schema → admin/audit → 30–50 POI → wizard/ranking/evaluation. Không lặp lại foundation hoặc coi revision draft là itinerary version history.
