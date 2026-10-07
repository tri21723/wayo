# Wayo Alpha — Product spec v0.1

Trạng thái: spec triển khai ban đầu. Liên quan PROD-01, PROD-02, PROD-04. Quyết định và điểm còn mở: [ADR 0001](../decisions/0001-alpha-foundation.md).

## Persona và lời hứa

Người Việt 22–35 tuổi, đi Đà Lạt tự túc theo couple/nhóm bạn nhỏ trong 2–4 ngày, thích ăn uống/local/chụp ảnh, cần lịch vừa sức và ít công sức sắp xếp. Alpha ưu tiên lịch khả thi hơn số hoạt động. Không booking, thanh toán hoặc theo dõi hành trình tự động.

## User stories và acceptance

| ID   | Nhu cầu                       | Thành công                                                              | Thiếu dữ liệu/lỗi                                                          |
| ---- | ----------------------------- | ----------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| US01 | Tôi mô tả gu nhanh            | 6–10 tương tác; sửa lại được; lưu profile sau auth                      | Skip dùng default có nhãn; không suy ra constraint từ câu bỏ qua           |
| US02 | Tôi nhập điều kiện chuyến đi  | Ngày đến/rời, group, budget/scope, pace, mode rõ; input được validate   | Hiển thị lỗi, giữ form; thiếu anchor chỉ cho draft, chưa route             |
| US03 | Tôi tạo lịch phù hợp          | POI ID thật, meals/rest/travel, đúng giờ và fixed event; cost breakdown | Infeasible giải thích constraint; provider lỗi không ghi lịch dở dang      |
| US04 | Tôi xem lịch và bản đồ        | Chọn ngày/card đồng bộ marker; thấy source, freshness, price range      | Map lỗi vẫn đọc timeline; rating/ảnh thiếu không giả lập                   |
| US05 | Tôi sửa bằng nút              | Add/remove/replace/move qua cùng validator; có diff/version/undo        | Conflict hai tab yêu cầu refresh/retry; không ghi đè im lặng               |
| US06 | Tôi nói “ngày 2 nhẹ hơn”      | Parse intent, giữ locked events, replan và commit một version hợp lệ    | Intent mơ hồ hỏi ngày/đối tượng; LLM lỗi vẫn sửa bằng nút                  |
| US07 | Tôi cần lịch thay thế khi mưa | Indoor alternatives phù hợp, route/cost cập nhật, diff rõ               | Ngoài forecast horizon gắn giả định; không có alternative thì nêu conflict |
| US08 | Tôi chia sẻ kế hoạch          | Link chỉ đọc snapshot, thu hồi được                                     | Token hết hạn/thu hồi không trả dữ liệu; không lộ profile/chat             |
| US09 | Tôi phản hồi trải nghiệm      | Feedback gắn đúng place/trip version; gửi lại không nhân bản            | Mất mạng có retry; không tự coi xóa item là dislike                        |

## Quy tắc thời gian và ngân sách

- Timestamp aware; hiển thị theo giờ Việt Nam. Số ngày = ngày rời trừ ngày đến + 1, từ 2 đến 4.
- Event có end > start, nằm trong window chuyến đi; hai fixed events không overlap. Validator đầu vào chưa kiểm tra travel time giữa events.
- Planner bắt buộc chèn travel và buffer trước khi kết luận không overlap; không dùng đường chim bay làm thời gian thực tế.
- Opening windows phải đủ toàn bộ duration, gồm split shifts/overnight/holiday exceptions. Missing hours → unknown. Hoạt động outdoor không được mặc định có hours 24/7.
- Bữa ăn/nghỉ có thể là item không gắn POI; chỉ item tham chiếu địa điểm mới bắt buộc `place_id`. Slot bữa ăn mặc định là preference cấu hình được; user-fixed meal mới là hard event.
- Budget là amount nguyên VND theo người hoặc cả nhóm. Tổng cap nhóm = per-person × số người, hoặc amount group. Không làm tròn bằng float.
- Chi phí phải gồm liên tỉnh/lưu trú/ăn uống/vé/nội đô/dự phòng; hạng mục chưa biết không tính là 0.
- Soft budget cho phép cảnh báo vượt và đề xuất giảm. Hard budget chỉ pass nếu upper estimate đủ các hạng mục ≤ cap; đây là kiểm tra dự toán, không đảm bảo giá tương lai.

## Trạng thái sản phẩm

| Trạng thái        | Ý nghĩa                                               | UI                                                   |
| ----------------- | ----------------------------------------------------- | ---------------------------------------------------- |
| input_valid       | Draft đúng schema/ràng buộc đầu vào                   | “Thông tin đầu vào hợp lệ”, chưa gọi là lịch khả thi |
| valid             | Lịch đủ bằng chứng và không có hard violation đã biết | Cho sử dụng, vẫn thể hiện nguồn và dự toán           |
| needs_attention   | Dữ liệu critical chưa đủ kiểm tra                     | Nêu unknown cụ thể, đề nghị verify/đổi               |
| infeasible        | Không thể đáp ứng hard constraints                    | Không tự bỏ constraint; cho phương án nới            |
| technical_failure | API/provider/worker lỗi                               | Giữ bản lịch trước, retry hữu hạn                    |

## Demo nghiệm thu khi hoàn thành alpha

Couple 3N2Đ, 4 triệu/người, đến Đà Lạt trưa ngày đầu và rời chiều ngày cuối; cafe, photography, local food, không trekking. Generate → xem route/time/cost → khóa bữa tối → yêu cầu ngày 2 mưa → kiểm tra diff → lịch mới vẫn giữ bữa tối → undo → share snapshot. Đây là mục tiêu, chưa có trong foundation.
