# Chuẩn bị deployment Wayo

Phạm vi hiện tại: foundation local và artifact triển khai. Chưa deploy staging/production. Có thể chạy Node/Python trực tiếp; Docker là gói tự host đã chuẩn bị. Gói này chưa thay thế reverse proxy/TLS, backup hoặc provider qualification.

## Tách môi trường

Dùng project Supabase và database riêng cho local/staging/production. Đặt `WAYO_ENVIRONMENT` đúng môi trường; staging/production yêu cầu URL PostgreSQL `?sslmode=require` hoặc `verify-full` và HTTPS Supabase. Không dùng database thật trong pytest. Tests chỉ dùng SQLite tạm hoặc PostgreSQL tên kết thúc `_test`.

Không copy dotenv local vào image. Supabase URL/publishable key là build args public của web; không truyền service_role/secret key. Đổi project/key public cần build lại web. URL DB, danh sách admin và khóa provider chỉ ở runtime API. Giữ file môi trường ngoài Git, giới hạn quyền đọc.

## Docker Compose

Cần Docker Engine + Compose v2 hoạt động (trên WSL bật integration trong Docker Desktop).

```bash
cp infra/.env.example infra/.env
# Điền project URL, publishable key và database cho môi trường này.
docker compose --env-file infra/.env -f infra/compose.yaml config --quiet
docker compose --env-file infra/.env -f infra/compose.yaml build
docker compose --env-file infra/.env -f infra/compose.yaml up -d
docker compose --env-file infra/.env -f infra/compose.yaml ps
python3 scripts/check_foundation.py --web-url http://localhost:3000
```

`migrate` chạy Alembic head trước API; API healthy trước web. Database nằm ngoài Compose, không tạo/xóa database tự động. Dùng connection direct/session pooler có quyền schema owner cho migration. Backend hiện dùng table owner và owner filter; không expose schema `wayo` cho browser.

Web bind `127.0.0.1:3000`; API chỉ trong mạng Compose. Khi tự host, cấu hình reverse proxy HTTPS phía trước, giới hạn body/timeouts và cập nhật Supabase Site URL/redirect allowlist cho domain thực. Nếu API/web khác host, dùng `WAYO_API_URL` server-only; browser vẫn gọi same-origin `/api`.

Không dùng public demo routing làm production mặc định. Providers trong Compose tắt. Cấu hình/khóa provider sẽ được bổ sung sau qualification.

## Admin và kiểm tra

`WAYO_ADMIN_USER_IDS` là JSON array UUID từ Supabase Auth Users. Mặc định `[]`; cập nhật runtime và khởi động lại API để cấp/thu hồi quyền. Kiểm tra `/v1/admin/status` với bearer token trong môi trường của bạn; không paste token vào issue/log. Endpoint chưa có CRUD catalog admin.

`/health` chỉ xác nhận process sống. `/ready` kiểm tra DB/migration và cấu hình Auth, không kiểm tra provider hoặc login thật. `/api/health` và smoke script kiểm tra web → API → DB. Nghiệm thu thêm bằng hai tài khoản: A tạo trip, B không đọc/sửa/xóa được; login/logout và reload trip phải hoạt động.

Logs API là JSON metadata có X-Request-ID, không ghi nội dung người dùng. Giữ request ID khi báo lỗi. Không bật SQL echo hoặc access log chứa query trong môi trường có dữ liệu thật.

## Migration và rollback

Chạy migration trước khi nhận traffic; không chạy cùng lúc từ nhiều replica. Backup DB trước thay đổi schema. Chỉ dùng `alembic downgrade` trên DB thử khi đã xác nhận migration không làm mất dữ liệu cần giữ. Rollback app bằng image tag cũ chỉ khi schema vẫn tương thích; không tự động downgrade database thật.

Khi deploy lại bằng cùng image tag, bảo đảm migration job chạy lại:

```bash
docker compose --env-file infra/.env -f infra/compose.yaml stop web api
docker compose --env-file infra/.env -f infra/compose.yaml run --rm migrate
docker compose --env-file infra/.env -f infra/compose.yaml up -d api web
```

Mỗi môi trường đặt `WAYO_IMAGE_TAG` riêng theo release. M0 staging chỉ hoàn tất sau deploy, smoke, nghiệm thu auth/owner và xác minh CI xanh; không đánh dấu chỉ vì Dockerfile tồn tại.

## Smoke Docker riêng, không dùng Supabase thật

Đã kiểm chứng trên Docker Desktop/WSL ngày 2026-10-08. Cấu hình sample dùng PostgreSQL container dùng một lần và Auth URL/key giả; chỉ kiểm tra pipeline, không đăng nhập Supabase thật. Web dùng cổng 3201 để tránh dev server 3000.

```bash
docker compose -p wayo-foundation-check --env-file infra/smoke.env.example -f infra/compose.yaml -f infra/compose.smoke.yaml build
docker compose -p wayo-foundation-check --env-file infra/smoke.env.example -f infra/compose.yaml -f infra/compose.smoke.yaml up -d
python3 scripts/check_foundation.py --web-url http://127.0.0.1:3201
docker compose -p wayo-foundation-check --env-file infra/smoke.env.example -f infra/compose.yaml -f infra/compose.smoke.yaml ps -a
docker compose -p wayo-foundation-check --env-file infra/smoke.env.example -f infra/compose.yaml -f infra/compose.smoke.yaml down --volumes --remove-orphans
```

Lệnh cuối chỉ dọn project smoke và database dùng một lần. CI dùng cùng config; không đưa key/URL database thật vào file smoke. Smoke override cố định database/Auth/project image thử, nên không dùng nhầm credentials đã export ở shell. Nếu đã export `WAYO_WEB_PORT`, bỏ biến này để smoke dùng cổng 3201.
