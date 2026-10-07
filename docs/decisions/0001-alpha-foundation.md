# ADR 0001 — Phạm vi và contract alpha

Ngày: 07/10/2026. Trạng thái: mặc định triển khai ban đầu, có thể điều chỉnh theo phản hồi chủ dự án. Không coi các lựa chọn này là xác nhận về nhân lực, ngân sách hoặc nhà cung cấp.

## Quyết định

| ID  | Quyết định triển khai                                                                                                       | Trạng thái                                       |
| --- | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| D01 | Alpha chỉ Đà Lạt; 2–4 ngày tính theo ngày lịch Việt Nam                                                                     | Áp dụng                                          |
| D02 | Budget nguyên VND, scope `per_person` hoặc `group`, cho toàn chuyến; phải thể hiện đầy đủ hạng mục khi có estimator         | Áp dụng contract                                 |
| D03 | Soft mặc định; hard chỉ được xác nhận khi upper estimate của đầy đủ hạng mục không vượt cap                                 | Áp dụng contract; chưa có estimator              |
| D04 | Prototype chọn `driving` (ô tô/taxi). Không hỗ trợ hoặc suy diễn xe máy từ route ô tô                                       | Tạm thời; phải kiểm chứng provider trước planner |
| D05 | Thiếu opening hours là unknown, không được coi là luôn mở                                                                   | Áp dụng spec                                     |
| D06 | Giờ đến/rời có timezone bắt buộc. Điểm neo có thể thiếu khi nhập draft nhưng bắt buộc trước route planning                  | Áp dụng contract                                 |
| D07 | User yêu cầu sửa: validate rồi commit, có undo. Weather chủ động: đề xuất diff, chờ user chấp nhận                          | Áp dụng spec                                     |
| D08 | Chưa chọn LLM/weather/routing provider, chưa đăng ký dịch vụ hoặc đặt trần chi phí thay chủ dự án                           | Chờ spike và ngân sách                           |
| D09 | Supabase Auth dự kiến; chưa có auth/persistence thì chỉ expose validation stateless, không giả user hoặc lưu trip công khai | Áp dụng foundation                               |
| D10 | Chưa biết quy mô team, giờ làm, ngân sách; không gắn deadline cố định                                                       | Còn mở                                           |

## Ranh giới implementation đầu tiên

Web nhập trip → same-origin Next.js proxy → FastAPI validate → trả kết quả có cấu trúc. Không ghi database, không gọi AI hoặc provider, không tạo itinerary giả. `input_valid` chỉ nói đầu vào đúng contract, khác `valid` của một lịch đã qua planner.

Couple đúng 2 người; nhóm bạn 1–4 người (cho phép draft nhóm chưa đủ người). UI nhập giờ địa phương Việt Nam và gửi offset `+07:00`; backend chấp nhận timestamp aware và tính số ngày theo `Asia/Ho_Chi_Minh`. Thông tin quá khứ chưa bị cấm vì cần dùng fixture và xem lại chuyến đi; khi tạo kế hoạch tương lai sẽ có policy riêng.

Next.js và FastAPI chạy riêng. Browser không gọi trực tiếp FastAPI nên foundation không bật CORS rộng. URL API là biến server-only. Trip endpoint hiện không persist nên chưa cần auth; CRUD sau này bắt buộc owner authorization.

## Hệ quả và bước tiếp theo

- Dữ liệu địa điểm thật, matrix và cost estimate phải có trước khi gọi output là itinerary khả thi.
- Trước auth/DB cần migration strategy, project Supabase và cấu hình môi trường; không nhập secret vào source.
- Node 22 đã có trong môi trường nhưng shell mặc định dùng Node 16; repo thêm `.nvmrc` để chọn đúng runtime. Theo [tài liệu Next.js](https://nextjs.org/docs/app/getting-started/installation), cần runtime mới hơn Node 16.
- API contract sinh qua OpenAPI theo [FastAPI](https://fastapi.tiangolo.com/tutorial/first-steps/), sau đó generate TypeScript; không duy trì hai bản schema thủ công.
- Các package được khóa theo phiên bản cài và kiểm thử thực tế; chưa cam kết deploy provider.
