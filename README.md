# Wayo

AI travel planner cá nhân hóa cho du lịch tự túc Việt Nam, bắt đầu từ Đà Lạt.

## Trạng thái hiện tại

Next.js + FastAPI có form trip, Supabase Auth, lưu/sửa sở thích tại `/profile`, lưu/đọc/sửa/xóa bản nháp bằng PostgreSQL và kiểm tra quyền sở hữu. Đã có bảng thời gian theo ngày, catalog/importer và gợi ý địa điểm từ trip đã lưu; chưa có POI thật, routing hoặc AI planner. Phần kiểm tra đầu vào chạy không cần API key; đăng nhập/lưu trip cần cấu hình dịch vụ.

- [Kế hoạch và checklist](docs/WAYO_IMPLEMENTATION_PLAN.md)
- [Checklist nghiệm thu foundation local](docs/FOUNDATION_CHECKLIST.md)
- [Review foundation và các lỗi đã sửa](docs/FOUNDATION_REVIEW.md)
- [Plan tiếp theo: M1 Data & taste → M2](docs/NEXT_PHASE_PLAN.md)
- [Chuẩn bị deployment](docs/runbooks/DEPLOYMENT.md)
- [Provider contract spikes](docs/runbooks/PROVIDER_SPIKES.md)
- [Tiến độ sprint 1](docs/SPRINT_01_STATUS.md)
- [Nhập catalog địa điểm có nguồn](data/README.md)
- [Cấu hình Supabase Auth + PostgreSQL](docs/runbooks/LOCAL_AUTH_DATABASE.md)
- [Alpha product spec](docs/product/ALPHA_SPEC.md)
- [Wireframes](docs/product/WIREFRAMES.md)
- [Quyết định nền tảng](docs/decisions/0001-alpha-foundation.md)

## Yêu cầu

Node.js 22, npm, Python 3.12 có `venv`. Các lệnh dưới đây chạy trên Linux/WSL từ thư mục repo trừ khi ghi rõ. Nếu dùng nvm, chạy `nvm use` trước; `.nvmrc` chọn Node 22, tránh shell đang dùng Node 16.

## Cài đặt

```bash
nvm use
npm ci
python3 -m venv .venv
.venv/bin/python -m pip install -r apps/api/requirements.lock
.venv/bin/python -m pip install --no-deps --no-build-isolation -e 'apps/api[dev]'
```

Copy `apps/web/.env.example` thành `apps/web/.env.local` nếu cần đổi URL API. Mặc định API ở `http://127.0.0.1:8000`. Để bật tài khoản và persistence, làm theo [hướng dẫn cấu hình](docs/runbooks/LOCAL_AUTH_DATABASE.md); nếu chưa cấu hình, validation vẫn hoạt động. Không đưa khóa thật vào source.

## Chạy local

Terminal 1, từ root:

```bash
.venv/bin/uvicorn app.main:app --app-dir apps/api --reload --host 127.0.0.1 --port 8000 --no-access-log
```

Terminal 2, từ root:

```bash
npm run dev
```

Mở `http://localhost:3000`. Điền giờ đến/rời 2–4 ngày, kiểm tra form. FastAPI docs: `http://127.0.0.1:8000/docs`, liveness: `/health`; readiness DB/migrations/Auth config: `/ready`. Web → API → DB: `/api/health`.

Web gọi same-origin `/api/trips/validate`; Next.js chuyển tiếp tới FastAPI `/v1/trips/validate`, timeout 8 giây. Nếu API chưa chạy, form báo không kết nối được và giữ dữ liệu đã nhập. Route validation không lưu dữ liệu hoặc gọi provider. CRUD `/api/trips` yêu cầu đăng nhập và lưu database. Không có AI generation ở bản này.

## Kiểm tra

```bash
.venv/bin/ruff check apps/api scripts
.venv/bin/ruff format --check apps/api scripts
.venv/bin/pytest apps/api/tests
npm run test:web
npm run lint
npm run typecheck
npm run format:check
npm run build
npx playwright install chromium
npm run test:e2e
```

## Chạy bản production local

```bash
npm run build
npm run start
python3 scripts/check_foundation.py --web-url http://localhost:3000
```

`start` dùng standalone và copy static assets; mặc định bind localhost. Có thể truyền `-- --port 3200 --hostname 127.0.0.1`. Smoke yêu cầu API có cấu hình database/Auth và migration hiện hành; build/test không cần credentials thật. Nếu muốn Docker, xem deployment runbook. Mỗi môi trường dùng file config và Supabase project riêng.

Admin mặc định tắt. Cấu hình `WAYO_ADMIN_USER_IDS` server-only cho dependency admin; chưa có admin catalog UI. Providers mặc định tắt; CLI inspect không gọi mạng, `--live` cần opt-in. Chưa có planner hoặc AI generation.

## Thay đổi contract

Sửa `apps/api/app/schemas.py`, bổ sung test rồi sinh lại schema/types:

```bash
.venv/bin/python apps/api/scripts/export_openapi.py
npm run api:types
npm run typecheck
```

Commit cả `apps/api/openapi.json` và `apps/web/src/lib/api-schema.d.ts`. Không sửa file types sinh tự động. CI kiểm tra contract không bị lệch.

## Cấu trúc

```text
apps/api/        FastAPI, schemas, SQLAlchemy models, Alembic, auth, tests
apps/web/        Next.js, auth, trip list/editor, server proxy, typed client
data/            Template nhập POI, chưa có data thật
evals/           Scenario specs cho planner tương lai
docs/            Product spec, decisions, wireframes, progress
```

## Phạm vi tiếp theo

Foundation local có auth/owner/admin, trip CRUD, readiness/logs, adapter nền và artifact deployment. Supabase thật đã kết nối và Docker smoke đã qua. Sau review foundation, ưu tiên dictionary/schema catalog, admin/audit, 30–50 POI có nguồn, wizard và ranking; xem plan M1 phía trên. CI trên GitHub còn cần xác minh; staging triển khai khi được yêu cầu. Xem checklist để tránh coi input validation là itinerary generation.

Tài liệu framework tham chiếu: [Next.js installation](https://nextjs.org/docs/app/getting-started/installation), [FastAPI first steps](https://fastapi.tiangolo.com/tutorial/first-steps/).
