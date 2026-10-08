# ADR 0006 — Bảng thời gian theo ngày trước khi lập lịch

Ngày: 2026-10-08. Trạng thái: accepted cho preview thời gian.

`GET /v1/trips/{id}/availability` đọc trip đã lưu, xác minh owner và trả revision, các ngày theo timezone Asia/Ho_Chi_Minh, sự kiện cố định cùng khoảng chưa xếp hoạt động. Endpoint chỉ đọc; không tạo itinerary version hoặc đổi trip.

Mỗi ngày gồm các block không chồng lấn: fixed, available hoặc outside_activity_hours. Khung hoạt động tham khảo hiện là 09:00–21:00, bị giới hạn bởi giờ đến/về. Sự kiện cố định được giữ cả khi nằm ngoài khung tham khảo; sự kiện qua nửa đêm được chia theo ngày nhưng tổng thời lượng không đổi. Ngày về đúng 00:00 vẫn có một ngày rỗng để khớp cách đếm calendar days hiện có.

Các khoảng trống là thời gian chưa phân bổ. Chưa trừ bữa ăn, nghỉ, buffer hoặc di chuyển; chưa thể khẳng định đủ thời gian ghé một POI. UI ghi rõ giới hạn này và không gọi kết quả là lịch trình hoàn chỉnh. Tính toán giữ số phút dạng float để không mất thời gian của booking có giây; UI làm tròn xuống số phút còn lại. Không sử dụng khoảng trống này để tự nới các ràng buộc sự kiện.

UI chỉ tải khi người dùng chọn **Xem thời gian theo ngày**. Nếu revision phản hồi khác trip đang xem, báo tải lại; khi trip được lưu phiên bản mới, panel được khởi tạo lại để không hiển thị kết quả cũ. Khi lỗi hoặc retry, xóa kết quả cũ. Sở thích, budget và catalog chưa tham gia vào phép chia thời gian.

Không cần migration, biến môi trường hoặc dịch vụ ngoài. Đây là nền cho PLAN-03/04; các task còn thiếu gồm thời gian nghỉ tùy chỉnh, địa điểm sự kiện, travel matrix, giờ mở cửa thực tế, phân bổ POI và versioning lịch trình.

Kiểm chứng: chia giờ đến/về, booking qua đêm, đến muộn/về sớm, UTC→Vietnam, ngày rỗng, booking chiếm cả khung ngày, thời lượng có giây, owner isolation và read-only. Browser flow kiểm tra block fixed, số phút, ngày rỗng, stale revision và lỗi tải.
