# Chạy đăng nhập và lưu chuyến đi

Phần kiểm tra đầu vào vẫn chạy khi chưa cấu hình dịch vụ. Để đăng ký/đăng nhập và lưu trip thật, cần Supabase Auth và PostgreSQL. Có thể dùng database cùng project Supabase hoặc PostgreSQL local; project Auth của frontend và backend phải giống nhau.

## 1. Cấu hình Supabase

Trong project Supabase của bạn:

1. Bật đăng nhập email/password. Nếu bật xác nhận email, hoàn tất xác nhận trước khi đăng nhập.
2. Cấu hình Site URL cho môi trường local là `http://localhost:3000` và production URL khi deploy. Email xác nhận dùng Site URL của project.
3. Dùng JWT signing key bất đối xứng ES256 hoặc RS256. Backend hiện không hỗ trợ shared-secret HS256 legacy.
4. Lấy Project URL và **publishable key** cho frontend. Không dùng service-role/secret key trên web.
5. Lấy connection string PostgreSQL cho backend: ưu tiên direct connection hoặc session pooler theo khả năng IPv4/IPv6 của môi trường. Không dùng transaction pooler cho migrations.

Cơ chế xác minh theo tài liệu [Supabase JWT](https://supabase.com/docs/guides/auth/jwts) và [Signing keys](https://supabase.com/docs/guides/auth/signing-keys). Web dùng [signInWithPassword](https://supabase.com/docs/reference/javascript/auth-signinwithpassword). Backend xác minh JWT bằng JWKS của URL đã cấu hình, không tin issuer hoặc key URL tùy ý trong token.

## 2. Tạo file môi trường

Từ root project:

```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local
```

Chỉ chạy `cp` khi file đích chưa tồn tại; nếu đã có thì thêm/sửa biến cần thiết để giữ cấu hình hiện có. Không gửi password database hoặc secret lên chat/Git.

`apps/api/.env`:

```dotenv
WAYO_DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/postgres?sslmode=require
WAYO_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
```

URL-encode ký tự đặc biệt trong password. Với PostgreSQL local có thể bỏ `sslmode=require` khi server local chưa bật TLS. Dùng tài khoản sở hữu schema/table cho đợt MVP; giới hạn database chỉ backend truy cập. Không đưa connection string vào biến `NEXT_PUBLIC_*`.

`apps/web/.env.local`:

```dotenv
WAYO_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_YOUR_KEY
```

Biến `NEXT_PUBLIC_*` được nhúng vào web build: restart dev server sau thay đổi, rebuild trước khi deploy.

## 3. Cập nhật dependency và migrate

```bash
nvm use
npm ci
.venv/bin/python -m pip install -r apps/api/requirements.lock
.venv/bin/python -m pip install --no-deps --no-build-isolation -e 'apps/api[dev]'
.venv/bin/alembic -c apps/api/alembic.ini upgrade head
```

API đọc `.env` theo đường dẫn trong `apps/api`, không phụ thuộc working directory. Migration tạo schema riêng `wayo`, bảng `users`, `trips` và Alembic version marker. Nó không thay đổi bảng `auth.users` của Supabase. Chạy lại `upgrade head` không tạo lại bảng hay xóa dữ liệu.

Không thêm schema `wayo` vào danh sách exposed schemas của Supabase Data API. RLS bật và không có policy cho browser role; backend dùng role sở hữu table và kiểm tra owner trên mọi query. `users.id` lấy từ JWT `sub`, không có email/password trong database ứng dụng.

## 4. Chạy

Terminal 1:

```bash
.venv/bin/uvicorn app.main:app --app-dir apps/api --reload --host 127.0.0.1 --port 8000
```

Terminal 2:

```bash
npm run dev
```

Truy cập `http://localhost:3000/login`, đăng ký/đăng nhập. Tại trang chủ: nhập trip → kiểm tra → lưu. Tại `/trips`: mở bản nháp → sửa → kiểm tra → lưu thay đổi. Reload trình duyệt để kiểm tra dữ liệu vẫn còn. Xóa cần xác nhận trên giao diện.

Có thể đăng nhập ở tab mới để giữ form đang nhập. Phiên auth đồng bộ giữa các tab bằng Supabase client. Backend xác minh chữ ký/issuer/audience/expiry/role trước khi đọc dữ liệu.

## 5. Mã lỗi thường gặp

| Mã                                | Ý nghĩa / xử lý                                                                                 |
| --------------------------------- | ----------------------------------------------------------------------------------------------- |
| UNAUTHENTICATED / INVALID_SESSION | Đăng nhập lại; kiểm tra frontend và backend cùng Supabase project, signing key đúng ES256/RS256 |
| AUTH_NOT_CONFIGURED               | Chưa có `WAYO_SUPABASE_URL` ở backend                                                           |
| AUTH_UNAVAILABLE                  | Backend chưa lấy được JWKS; kiểm tra network tới Supabase                                       |
| DATABASE_NOT_CONFIGURED           | Chưa có database URL                                                                            |
| DATABASE_UNAVAILABLE              | Kiểm tra kết nối, quyền database và đã chạy migration; thông tin nội bộ không trả về client     |
| TRIP_NOT_FOUND                    | Trip không tồn tại hoặc không thuộc user hiện tại                                               |
| REVISION_CONFLICT                 | Trip đã đổi ở tab khác; tải lại bản đã lưu trước khi chỉnh tiếp                                 |
| REQUEST_CONFLICT                  | Một request ID dùng cho hai payload khác nhau; frontend tự cấp ID theo draft                    |

Đăng xuất xóa phiên ở trình duyệt hiện tại. JWT đã phát hành vẫn có thể hợp lệ tới khi hết hạn; backend hiện xác minh offline bằng JWKS, chưa thực hiện token revocation tức thời. Không đồng nghĩa đăng xuất mọi thiết bị.

## 6. Kiểm thử

```bash
.venv/bin/pytest apps/api/tests
npm run typecheck
npm run lint
npm run build
npx playwright install chromium
npm run test:e2e
```

Bộ API mặc định dùng SQLite tạm trong thư mục test để test nhanh. Để kiểm tra PostgreSQL, tạo database **riêng, dùng để xóa/tạo lại**, tên kết thúc bằng `_test`, rồi đặt `WAYO_TEST_DATABASE_URL` và chạy `apps/api/tests/test_trip_storage.py`. Tests chạy upgrade/downgrade và không được dùng với database thật.

Playwright chạy server riêng ở `127.0.0.1:3100`, mock dịch vụ Supabase và API ở browser để kiểm tra UI; không gửi email/tạo tài khoản thật. Test backend riêng dùng JWT có chữ ký RSA/EC thật và database thật/tạm. Cần smoke test với project Supabase thật trước staging; hiện chưa có credentials để thực hiện bước đó.

## Sở thích cá nhân

Migration `0002` thêm `wayo.travel_profiles`; dùng cùng lệnh `alembic upgrade head` như phần database ở trên. Không cần biến môi trường mới hoặc bật Data API.

Sau khi API/web nạp code mới, mở `/profile` hoặc chọn **Sở thích của tôi**:

1. Đăng nhập, chọn ít nhất một sở thích, điều chỉnh nhịp đi/chế độ ăn và các điều cần tránh.
2. Lưu, tải lại trang, xác nhận lựa chọn còn nguyên.
3. Mở hai tab cùng profile, lưu tab thứ nhất rồi lưu tab còn lại: tab thứ hai phải báo xung đột và cho tải lại.
4. Đăng xuất: nội dung profile phải bị ẩn. Tài khoản khác không được nhìn thấy profile cũ.
5. Kiểm tra trip đã lưu vẫn giữ nguyên nội dung.

Trong form trip, chọn **Áp dụng sở thích cá nhân**, chỉnh riêng nếu cần, kiểm tra rồi lưu. Profile mới hơn không tự thay đổi trip đã lưu. Không cần nhập POI giả để thử luồng này.

Browser tests mặc định chạy dev server riêng. Có thể thử production build bằng `WAYO_E2E=1 npm run build`, sau đó `WAYO_E2E_PRODUCTION=1 npm run test:e2e`. Các yêu cầu Auth và API trong browser tests được mock, không tạo tài khoản hoặc dữ liệu thật.

## Nghiệm thu snapshot sở thích

1. Lưu profile có sở thích thiên nhiên, chế độ ăn thuần chay và tránh cầu thang.
2. Tạo trip → Áp dụng sở thích cá nhân. Xác nhận các lựa chọn đã điền.
3. Đổi chế độ ăn của riêng trip sang ăn chay, kiểm tra và lưu.
4. Sửa profile sang sở thích khác, mở lại trip: snapshot và lựa chọn riêng phải giữ nguyên.
5. Mở hai tab; áp dụng profile trong tab trip rồi sửa profile ở tab kia trước khi lưu trip: lưu trip phải báo profile đã thay đổi. Bấm áp dụng lại nếu muốn dùng bản mới.

Dietary discovery chỉ hiện địa điểm ăn uống có evidence phù hợp; catalog chưa có dữ liệu thật sẽ tiếp tục hiện trạng thái trống.

## Nghiệm thu điểm lưu trú và sự kiện cố định

1. Trong form trip, bật **Tôi đã có điểm lưu trú / xuất phát**, nhập tên và tọa độ thập phân của địa điểm.
2. Chọn **+ Thêm sự kiện cố định**; nhập tên, bắt đầu và kết thúc theo giờ Việt Nam. Mỗi sự kiện cần nằm trong khoảng ngày/giờ trip.
3. Kiểm tra và lưu; mở lại trip, xác nhận tọa độ và sự kiện giữ nguyên.
4. Thử tạo hai sự kiện chồng giờ hoặc nằm ngoài trip: API phải báo lỗi, bản đã lưu giữ nguyên.
5. Xóa một dòng sự kiện, kiểm tra các dòng còn lại không đổi. Bỏ chọn điểm lưu trú, xóa toàn bộ sự kiện, kiểm tra và lưu: lần mở sau phải trống.

Hiện nhập tọa độ thủ công, chưa có tìm địa chỉ trên bản đồ. Sự kiện chỉ giữ thời gian; chưa có địa điểm sự kiện hoặc kiểm tra thời gian di chuyển. Không cần cấu hình dịch vụ mới.
