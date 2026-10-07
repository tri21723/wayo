# Planner scenarios đầu tiên

Các scenario này là đặc tả nghiệm thu cho planner tương lai, không phải kết quả đã chạy. Test đầu vào đang chạy tại `apps/api/tests/`.

| ID   | Tình huống                                       | Kết quả kỳ vọng khi có planner                     |
| ---- | ------------------------------------------------ | -------------------------------------------------- |
| SC01 | Couple 3N2Đ relaxed, đủ dữ liệu                  | Không quá dày, meals/rest/travel đầy đủ            |
| SC02 | User loại trekking                               | Không chọn POI trekking dù taste score cao         |
| SC03 | Cafe chỉ mở 10–17h                               | Không xếp ngoài window hoặc duration vượt giờ đóng |
| SC04 | POI không rõ opening hours                       | needs_attention hoặc thay POI đủ dữ liệu           |
| SC05 | Budget hard không đủ                             | infeasible/đề nghị nới, không che chi phí thiếu    |
| SC06 | Đến trưa ngày đầu, về sớm ngày cuối              | Mọi item nằm trong arrival/departure bounds        |
| SC07 | Hai fixed event đủ gap giờ nhưng không đủ travel | Phát hiện infeasible bằng route duration           |
| SC08 | Ngày 2 mưa, bữa tối đã khóa                      | Thay outdoor phù hợp, giữ bữa tối, revalidate      |
| SC09 | Route provider timeout/no-route                  | Không publish lịch valid dùng travel giả           |
| SC10 | Hai request replan cùng base version             | Chỉ một commit, request cũ nhận conflict           |
