# Foundation local — checklist nghiệm thu

Phạm vi được chọn ngày 2026-10-08: hoàn tất foundation local, chuẩn bị deployment. M0 staging trong plan tổng thể vẫn là mốc riêng. Checklist này không bao gồm dữ liệu POI thật, itinerary planner, AI copilot hoặc admin catalog.

## Engineering local

- [x] **BASE-01 local:** npm/Python lockfiles, env examples, scripts và hướng dẫn cài từ source sạch; không cần secret để build hoặc test.
- [x] **BASE-02 local:** web/API, health/readiness, OpenAPI/types, BFF, error contract và giới hạn request body.
- [x] **BASE-03 local:** migrations 0001–0003, fresh/upgrade/downgrade, PostgreSQL/SQLite; schema app private và RLS; tách cấu hình môi trường.
- [x] **BASE-04 local:** JWT verification, owner isolation, admin allowlist server-only, quyền mặc định đóng; user đã nghiệm thu Auth với Supabase thật ở đợt trước.
- [x] **BASE-05 local:** Trip CRUD/list và UI, persistence, idempotency, optimistic concurrency; user đã nghiệm thu local/Supabase ở đợt trước.
- [x] **BASE-06 preparation:** CI lint/typecheck/build/contracts/API/browser; Dockerfiles, Compose migration → ready → web, smoke script, deployment/rollback runbook. Container build/run smoke local đã qua; workflow GitHub chưa xác minh.
- [x] **BASE-07 contract foundation:** adapter routing/weather/LLM, config opt-in, timeout, response/call/token limits, typed errors, HTTP mock contract spike, CLI dry-run và live opt-in; ghi nguồn/qualification cần tiếp tục.
- [x] Request ID + metadata logs và lỗi nội bộ che dữ liệu; không ghi token/profile/body/DB URL trong log app.

## Bằng chứng local

- 132 test API qua trên SQLite và PostgreSQL dùng một lần; migrations, RLS, quyền owner/admin và readiness được kiểm tra.
- Build standalone, lint, typecheck, Ruff và format được kiểm tra.
- Browser flow và smoke web standalone → API → PostgreSQL được ghi trong [status sprint](SPRINT_01_STATUS.md).
- Kiểm chứng cài lại từ source không có dotenv/node_modules/venv trong `/tmp`; không ghi dữ liệu vào Supabase thật.

## Review bổ sung

- [x] Chặn khóa Supabase secret/service-role trước build public bundle.
- [x] Xóa kết quả phiên cũ và bỏ qua response đến muộn khi đổi user/logout trên form home.
- [x] Giữ request ID cho BFF DELETE 204.
- [x] Thêm regression tests và lệnh `npm run test:web` vào CI.

Chi tiết và giới hạn kiểm chứng: [review foundation](FOUNDATION_REVIEW.md). Công việc tiếp theo: [plan M1](NEXT_PHASE_PLAN.md).

## Gate sau foundation local

- [x] Docker Desktop/WSL: build cả hai image, Compose migration → API → web healthy và smoke qua PostgreSQL dùng một lần.
- [ ] Push và xác minh workflow GitHub chạy xanh trên commit triển khai cuối.
- [ ] Tạo môi trường staging riêng, TLS/reverse proxy và Supabase redirects; deploy và smoke.
- [ ] Nghiệm thu đăng nhập, trip CRUD và owner isolation trên staging bằng hai tài khoản thật.
- [ ] Provider qualification: key/model/endpoint phù hợp, live quality/latency/quota/cost/cache; chưa chạy LLM trả phí.

Những gate này chưa được coi là hoàn tất. Provider adapters chưa nối với planner và không tạo itinerary. Bật provider chỉ qua cấu hình server sau qualification. Chi tiết: [ADR 0009](decisions/0009-local-foundation-and-deployment.md), [deployment](runbooks/DEPLOYMENT.md), [provider spikes](runbooks/PROVIDER_SPIKES.md).
