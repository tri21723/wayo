# ADR 0009 — Hoàn tất foundation local, chuẩn bị deployment

Ngày: 2026-10-08. Trạng thái: accepted cho phạm vi user đã chọn: foundation local và chuẩn bị deployment.

M0 trong plan gốc yêu cầu staging. Đợt này hoàn tất phần engineering local của BASE-01–07; không đồng nhất với gate M0 staging. POI thật, planner, routing qualification, admin catalog, versioning và AI copilot thuộc các mốc sau.

## Auth và vận hành

JWT vẫn được kiểm chữ ký/issuer/audience/expiry; quyền owner không đổi. Admin dùng `WAYO_ADMIN_USER_IDS` do operator cấu hình, mặc định rỗng; không lấy quyền từ body, user_metadata hoặc app_metadata. `/v1/admin/status` xác nhận dependency cho các route quản trị tương lai. Chưa có UI admin/catalog review.

`/health` là liveness; `/ready` kiểm tra cấu hình Auth, kết nối DB, Alembic head và bảng app. `/api/health` đi qua BFF tới `/ready`, dùng cho smoke web → API → DB. Auth readiness chỉ xác nhận cấu hình, không khẳng định JWKS/login đang hoạt động. Không gọi provider trong health probe.

Request ID do server tạo và trả ở header. JSON logs chỉ ghi method, route template, status, latency và ID; không ghi query, URL thực chứa ID, body, token, exception text hoặc thông tin connection. Request body giới hạn 64 KiB kể cả chunked. Lỗi chưa xử lý trả contract 500 chung. Uvicorn production tắt access log mặc định để không log query string. Các logs này là baseline HTTP, chưa có planner-stage tracing/cost accounting.

## Provider boundary

Adapter OSRM table, Open-Meteo hourly và OpenAI Responses có contract riêng, finite/typed validation, timeout, giới hạn response 512 KiB, số calls theo operation và output tokens LLM. Không retry tự động, không cache, không gọi từ route public. Mặc định tắt; kết quả thiếu/không có tuyến không bị thay bằng số giả. CLI inspection không gọi mạng; `--live` gọi tối đa một lần và vẫn cần opt-in trong cấu hình.

Chưa chốt provider production/model, chưa gọi LLM trả phí, chưa xác minh chất lượng tuyến Đà Lạt hoặc forecast provider thật. Contract spike bằng HTTP mock là bằng chứng foundation; provider qualification là gate trước tích hợp planner, không được gắn nhãn đã làm xong.

## Deployment

Dockerfiles nhiều stage, user không phải root, `.dockerignore` loại dotenv/secret và artifact local. Web standalone trace từ monorepo root. Chỉ URL/key Supabase public đi vào build; DB/admin/provider credentials ở runtime API. Compose chạy migration một lần rồi API ready, rồi web; API không publish port ra host. Web bind localhost để đặt reverse proxy/TLS phía trước khi triển khai.

Mỗi môi trường dùng dotenv/project/database riêng. Staging/production yêu cầu PostgreSQL TLS, Supabase HTTPS. Không auto-migrate từ từng worker, không seed fixture vào DB thật. CI thêm build image và smoke trên database dùng một lần. Docker Desktop/WSL đã được user bật và kiểm chứng ngày 2026-10-08: image build, Compose migration/API/web health và smoke PostgreSQL tạm đạt. CI dùng cùng Compose smoke recipe; chưa xác minh run trên GitHub hoặc staging.
