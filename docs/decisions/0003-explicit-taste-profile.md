# ADR 0003 — Sở thích cá nhân có phiên bản

Cập nhật: phần snapshot/override và discovery dùng sở thích được bổ sung trong [ADR 0005](0005-trip-taste-snapshot.md).

Ngày: 2026-10-07. Trạng thái: accepted cho phần lưu profile alpha.

- `/profile` có sáu nhóm câu hỏi, lưu và sửa lại sau đăng nhập. Có thể bỏ qua onboarding bằng cách tiếp tục tạo trip; chưa có wizard từng bước hoặc đo completion/drop-off.
- `GET /v1/profile` trả revision 0 và answers null khi chưa lưu. Không tạo row từ thao tác đọc.
- `PUT /v1/profile` nhận toàn bộ answers và expected_revision. Revision 0 tạo lần đầu; các lần sau dùng compare-and-swap. Xung đột trả 409, UI giữ nội dung đang sửa và cho tải lại có cảnh báo bỏ thay đổi.
- Chủ sở hữu lấy từ JWT; client không được truyền owner_id. Bảng `wayo.travel_profiles` có RLS, thuộc schema private; backend thực thi owner isolation.
- Schema version 1: sáu chiều cafe/nature/photography/food/culture/nightlife; mỗi chiều được chọn = 1, còn lại = 0. Vector được tính từ answers khi đọc, không lưu hai bản dễ lệch nhau. Đây là tín hiệu sở thích tường minh, không phải xác suất thích địa điểm.
- Pace, crowd và adventure lưu riêng; diet và exclusions là ràng buộc riêng, không bị chuyển thành điểm thấp. Chưa có ranker áp dụng các ràng buộc này.
- Danh sách enum được giới hạn, loại trùng bị từ chối, thứ tự được chuẩn hóa; dữ liệu không biết bị từ chối thay vì đoán ý.
- Chưa tự sao chép profile vào trip. Các trip hiện có giữ nguyên; snapshot/override sẽ triển khai cùng đầu vào cho ranking để không ngầm thay đổi ý định đã lưu.
- Migration 0002 chỉ thêm bảng profile; tests kiểm tra nâng từ 0001 không đổi trips. Không có POI giả hoặc dữ liệu lịch trình được tạo trong migration.

Kiểm chứng: API tests với SQLite và PostgreSQL cho persistence, owner isolation, validation, CAS, migration drift (PostgreSQL), và giữ nguyên trip. Browser test mock Supabase/API cho save/reload/conflict/sign-out; không thay thế nghiệm thu profile với tài khoản Supabase thật.
