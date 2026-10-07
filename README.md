# Wayo

AI travel planner cá nhân hóa cho du lịch tự túc Việt Nam, bắt đầu từ Đà Lạt.

## Trạng thái hiện tại

Foundation: Next.js web + FastAPI, form trip tiếng Việt, schema validation và OpenAPI-generated TypeScript. Chưa tích hợp auth, database, POI, routing hoặc AI; chưa lưu chuyến đi. Không cần API key để chạy phần hiện tại.

- [Kế hoạch và checklist](docs/WAYO_IMPLEMENTATION_PLAN.md)
- [Tiến độ sprint 1](docs/SPRINT_01_STATUS.md)
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

Copy `apps/web/.env.example` thành `apps/web/.env.local` nếu cần đổi URL API. Mặc định API ở `http://127.0.0.1:8000`. Foundation API chưa có biến môi trường bắt buộc. Không đưa khóa thật vào source.

## Chạy local

Terminal 1, từ root:

```bash
.venv/bin/uvicorn app.main:app --app-dir apps/api --reload --host 127.0.0.1 --port 8000
```

Terminal 2, từ root:

```bash
npm run dev
```

Mở `http://localhost:3000`. Điền giờ đến/rời 2–4 ngày, kiểm tra form. FastAPI docs: `http://127.0.0.1:8000/docs`, liveness: `/health`.

Web gọi same-origin `/api/trips/validate`; Next.js chuyển tiếp tới FastAPI `/v1/trips/validate`, timeout 8 giây. Nếu API chưa chạy, form báo không kết nối được và giữ dữ liệu đã nhập. Route này không lưu dữ liệu hoặc gọi provider.

## Kiểm tra

```bash
.venv/bin/ruff check apps/api
.venv/bin/ruff format --check apps/api
.venv/bin/pytest apps/api/tests
npm run lint
npm run typecheck
npm run format:check
npm run build
```

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
apps/api/        FastAPI, Pydantic schemas, OpenAPI, tests
apps/web/        Next.js App Router, form, server proxy, typed client
data/            Template nhập POI, chưa có data thật
evals/           Scenario specs cho planner tương lai
docs/            Product spec, decisions, wireframes, progress
```

## Phạm vi tiếp theo

Thiết kế ERD/migrations PostgreSQL, Supabase Auth + owner isolation, Trip CRUD và staging. Sau đó mới curate POI, ranking, planner và routing. Xem checklist để tránh coi input validation là itinerary generation.

Tài liệu framework tham chiếu: [Next.js installation](https://nextjs.org/docs/app/getting-started/installation), [FastAPI first steps](https://fastapi.tiangolo.com/tutorial/first-steps/).
