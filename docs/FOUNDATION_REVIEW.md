# Review foundation local — 08/10/2026

## Kết luận và phạm vi

Foundation local đủ nền để chuyển sang M1 Data & taste sau các bản sửa trong đợt review này. M0 staging trong kế hoạch tổng thể vẫn chưa hoàn tất. Không phát hiện blocker khác trong phạm vi đã kiểm tra; đây không phải chứng nhận production hoặc security audit toàn diện.

Review dựa trên code auth/owner/admin, CRUD/idempotency/revision, schema/migrations/RLS, profile/snapshot, API/BFF/errors/logs, provider adapters, Docker/CI và các test hiện có. Không chạy migration trên Supabase thật, không gọi provider trả phí và không triển khai staging. Các phát hiện dưới đây là từ code, không phải bằng chứng đã xảy ra lộ dữ liệu trên môi trường đang chạy.

## Các vấn đề đã sửa

| ID      | Mức độ                | Vấn đề và ảnh hưởng                                                                                                                   | Cách sửa                                                                                                                                                       | Bằng chứng                                                                                 |
| ------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| FND-R01 | Cao khi cấu hình nhầm | Runtime chỉ chặn `sb_secret_`, không chặn legacy service-role JWT; biến `NEXT_PUBLIC_*` có thể được inline trước khi runtime kiểm tra | Guard trong Next config trước build, chỉ nhận publishable/legacy anon; runtime dùng cùng validator, lỗi không in key                                           | Unit test public/anon/secret/service-role/malformed; build với secret fixture bị từ chối   |
| FND-R02 | Trung bình            | Form home giữ link đã lưu sau logout khi không có snapshot; phản hồi save/validation cũ có thể khôi phục state của phiên trước        | Reset kết quả/request key khi đổi user; epoch bỏ qua response/error/finally cũ, kể cả quay lại cùng user; kiểm tra owner trước gửi mutation sau `getSession()` | Ba E2E mới: logout sau save, trong save, trong validation; draft tự nhập vẫn dùng lại được |
| FND-R03 | Thấp                  | BFF trả 204 trước khi forward request ID, mất correlation cho delete thành công                                                       | Tạo headers chung trước nhánh 204, giữ no-store và body rỗng                                                                                                   | Unit test gọi module BFF thực với upstream 204 giả lập                                     |

FND-R02 liên quan state phía browser; backend vẫn xác minh owner của mọi trip. Request đã gửi có thể được server hoàn tất trước/sau logout; bản sửa ngăn kết quả cũ xuất hiện hoặc payload được gửi dưới user khác khi lấy session, không hứa hủy transaction đã nhận ở server.

## Kiểm chứng đợt review

- API: **132/132** test qua trên SQLite dùng một lần; backend/schema không đổi trong đợt này.
- Browser: **12/12** flow qua trên Next dev server riêng cổng 3100, gồm 9 flow cũ và 3 regression mới. Auth/API được mock; không thay thế nghiệm thu Supabase thật.
- Node regression: **6/6** tests qua, gồm public-key validation, chặn mutation khi session khác owner và forwarding request ID ở BFF 204; thêm `npm run test:web` vào CI.
- Lint và typecheck: qua.
- Build âm tính: `sb_secret_review_fixture` bị chặn tại Next config, trước compile. Không sử dụng hoặc in secret thật.
- Production standalone build: qua với cấu hình public fixture, output `.next-e2e` riêng. Format toàn repo và `git diff --check`: qua.
- Docker build/run smoke, PostgreSQL 132 tests, fresh install và non-root/no-dotenv image đã qua ở đợt foundation trước; không coi đó là lần chạy mới của review này. Chi tiết trong [Sprint 01](SPRINT_01_STATUS.md).

Không đổi dependency, public API contract hoặc migration. Chỉ cần khởi động lại/rebuild web để nhận sửa đổi; biến môi trường public vẫn được cố định khi build.

## Các gate còn mở

- GitHub CI cần chạy xanh trên commit được push; file workflow và local tests không chứng minh remote CI đã chạy.
- Staging/TLS/redirects và nghiệm thu hai tài khoản thật giữ DEFERRED theo lựa chọn của user.
- Profile/snapshot mới cần walkthrough bằng tài khoản Supabase thật ngoài browser mocks.
- Provider adapters hiện chỉ đạt contract/mock foundation; live routing quality/quota/cache/cost là gate trước planner. Chưa bật LLM/weather live.
- Catalog chưa có POI thật; admin catalog, wizard đầy đủ, itinerary versions/planner/editor/copilot là công việc tiếp theo, không phải tính năng đã hoàn thành.

Đầu ra tiếp theo: [plan M1 và chuẩn bị M2](NEXT_PHASE_PLAN.md), có task con, phụ thuộc, ước lượng, checklist và gate nghiệm thu. Ưu tiên dictionary/schema → admin/audit → dữ liệu thật → ranking/evaluation.
