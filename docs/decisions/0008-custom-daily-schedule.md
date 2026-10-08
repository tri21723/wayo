# ADR 0008 — Giờ hoạt động và khoảng nghỉ hằng ngày

Ngày: 2026-10-08. Trạng thái: accepted.

Trip có `day_schedule`: `starts_at`, `ends_at` dạng HH:mm theo giờ Việt Nam, và tối đa 6 `breaks` có tên và giờ bắt đầu/kết thúc. Khung giờ cùng ngày, kết thúc sau bắt đầu; khoảng nghỉ phải nằm trong khung và không chồng nhau. Hai khoảng liền nhau hợp lệ. Cấu hình lặp mỗi ngày, được giới hạn bởi giờ đến/về. Chưa hỗ trợ lịch riêng từng ngày hoặc khung hoạt động qua đêm.

Mặc định 09:00–21:00, không có khoảng nghỉ, giữ kết quả của trip cũ. Người dùng thêm bữa ăn/nghỉ chủ động; không tự suy đoán từ pace. Editor giữ định danh dòng ổn định khi xóa, thay đổi làm mất hiệu lực kết quả kiểm tra trước đó.

Availability chia block tại các ranh giới giờ hoạt động, sự kiện và khoảng nghỉ. Thứ tự ưu tiên: fixed event, rest, available, outside_activity_hours. Khi booking trùng nghỉ, vẫn giữ booking và chỉ trừ phần hợp của thời gian bận; UI/API giải thích quy tắc ưu tiên. Mỗi phút chỉ thuộc một block. Discovery chỉ giao opening windows với block available nên không gợi ý giờ ghé trong khoảng nghỉ. Đây vẫn là kiểm tra từng địa điểm độc lập, chưa tạo lịch có tuyến di chuyển hoặc tự xếp bữa ăn.

Trip lưu JSON nên không cần migration. Create digest bỏ day_schedule mặc định để request cũ retry vẫn khớp hash. Update bỏ qua trường này từ client cũ giữ cấu hình đã lưu; gửi breaks rỗng xóa các khoảng nghỉ. OpenAPI và TypeScript được tạo lại. Không thêm provider hoặc biến môi trường.

Thay phần giờ cố định và giới hạn về khoảng nghỉ của ADR 0006/0007; các giới hạn về route, buffer, ngày lễ và dataset thật vẫn áp dụng.
