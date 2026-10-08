# ADR 0007 — Giờ có thể ghé theo lịch tuần và khoảng trống của trip

Ngày: 2026-10-08. Trạng thái: accepted cho discovery v3.

Discovery kết hợp lịch mở cửa theo tuần trong catalog với bảng khoảng trống của ADR 0006. Mỗi địa điểm được kiểm tra độc lập, chưa tạo itinerary và chưa đặt chỗ.

## Trạng thái

- `fits_known_hours`: đã có lịch mở cửa và duration, có ít nhất một khoảng liên tục đủ thời lượng.
- `unknown_hours`: còn thời gian trống nhưng chưa có lịch mở cửa. Không đưa ra giờ bắt đầu.
- `unknown_duration`: lịch mở cửa có giao với khoảng trống nhưng chưa có duration. Không đoán thời lượng.
- `no_window`: không còn khoảng trống, không có giao với giờ mở cửa hoặc không có khoảng liên tục đủ duration. Loại khỏi kết quả trước khi xếp hạng và giới hạn category.

Nếu tất cả khoảng trống ngắn hơn duration đã biết, có thể loại ngay dù chưa biết giờ mở cửa. Không cộng hai khoảng bị ngăn bởi booking hoặc giờ đóng cửa.

`hours: null` là lịch chưa biết. `hours: []` là không có khung mở cửa. Khi có danh sách weekly windows, thứ không xuất hiện được coi là không mở trong lịch đó. Curator cần xác minh đầy đủ cả tuần trước khi lưu danh sách; dữ liệu từng phần phải để null thay vì suy ra các ngày khác đóng cửa.

## Phép tính

Dùng ngày địa phương Việt Nam và thứ tương ứng, lấy giao của opening windows với block available (09:00–21:00, đã giới hạn bởi arrival/departure và loại fixed events). Hai window mở liên tiếp được gộp vì không có giờ đóng ở giữa. Booking qua đêm được chia từ bảng thời gian; UTC đầu vào quy đổi đúng về ngày Việt Nam.

Mỗi window kết quả có `starts_at`, `latest_start_at`, `ends_at` và duration. Người dùng có thể bắt đầu từ starts_at tới latest_start_at (bao gồm cả hai đầu); toàn bộ thời lượng phải kết thúc không muộn hơn ends_at. Khoảng vừa đúng duration có một thời điểm bắt đầu duy nhất. API trả tối đa 12 window đầu theo thời gian; UI hiển thị 3 và số window khác trong phản hồi.

Các gợi ý có thể dùng chung một khoảng trống; đây là lựa chọn độc lập. Không khẳng định có thể ghé tất cả. Chưa tính tuyến, buffer, bữa ăn/nghỉ, ngày lễ, giờ ngoại lệ hoặc thời tiết. Nhãn UI ghi tham khảo và cảnh báo các phần chưa kiểm tra. Không đổi điểm taste/context hoặc nới exclusion/budget để tạo window.

## Tương thích

Thêm `timing` vào mỗi SuggestedPlace; algorithm_version là saved-trip-hours-v3. Trip và catalog hiện có không cần migration hay biến môi trường mới. Catalog thật còn trống; tests dùng fixture tổng hợp rõ ràng và không nhập vào Supabase.

Kiểm chứng: đúng weekday, clip arrival/departure, latest-start boundary, booking chia khoảng, duration thiếu/giờ thiếu/đóng cửa, window liền nhau và giờ nghỉ trưa, UTC và booking qua đêm, lọc trước category cap, API trả timing. UI kiểm tra cả window đã biết và trạng thái giờ chưa biết.
