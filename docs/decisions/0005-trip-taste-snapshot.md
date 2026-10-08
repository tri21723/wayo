# ADR 0005 — Áp dụng profile vào trip bằng snapshot tường minh

Ngày: 2026-10-07. Trạng thái: accepted.

## Hành vi

Trong form tạo/sửa trip, người dùng chọn **Áp dụng sở thích cá nhân**. Thao tác đọc profile và thay thế các lựa chọn taste của bản nháp: interests, exclusions, pace, diet, crowd và adventure. Giao diện thông báo rõ phạm vi thay thế; chưa ghi database cho tới khi người dùng kiểm tra và lưu trip.

Trip lưu `taste_snapshot` gồm schema_version, profile_revision và toàn bộ answers gốc. Các trường preferences/exclusions/pace/diet/crowd/adventure của trip là lựa chọn hiệu lực; người dùng có thể sửa riêng sau khi áp dụng. Snapshot là dấu vết nguồn, không phải bộ ràng buộc được hợp nhất lại mỗi khi rank.

- Thay đổi profile không thay đổi snapshot hoặc dữ liệu hiệu lực của trip đã lưu.
- Sửa trip không ghi profile. Nút áp dụng có thể lấy bản profile mới hơn khi người dùng chủ động chọn.
- Không bắt buộc có profile để tạo trip; người dùng có thể điền trực tiếp.
- Form giữ nguyên title/dates/budget khi áp dụng; mọi kết quả validation cũ bị hủy để phải kiểm tra lại.
- Đăng xuất/đổi tài khoản xóa các lựa chọn đã nhập từ profile khỏi form tạo trip; kết quả GET profile đến muộn không được áp dụng cho tài khoản khác.

## API và tương thích

Khi tạo hoặc thay snapshot, API kiểm tra revision và answers khớp profile của chủ JWT. PostgreSQL khóa row profile trong transaction tới khi ghi trip xong. Snapshot không hợp lệ hoặc đã cũ trả `409 PROFILE_CHANGED`; UI giữ bản nháp và hướng dẫn áp dụng lại. Snapshot đã lưu và không thay đổi vẫn hợp lệ sau khi profile được chỉnh sửa.

Các update trip tiếp tục dùng optimistic revision. Snapshot không chứa owner do client cung cấp. API không tự đọc profile trong mỗi lần retrieval/ranking.

Các trường mới là tùy chọn với mặc định tương thích: snapshot null, diet unrestricted, crowd neutral, adventure null. Trip cũ đọc được mà không cần migration. Khi editor cũ PUT thiếu các trường mới, backend giữ giá trị trước đó để tránh mất ràng buộc; client mới có thể gửi giá trị mặc định/null tường minh để đổi hoặc xóa. Canonical create hash bỏ các trường mới nếu bằng mặc định để giữ idempotency cho yêu cầu tạo từ bản cũ.

## Discovery v2

- Lấy preferences/exclusions và các trường hiệu lực từ trip đã lưu, không từ profile live.
- Với địa điểm category food/cafe hoặc tag food, diet vegetarian/vegan cần `dietary_options` phù hợp. Vegan cũng đáp ứng vegetarian. Unknown/null/[] không đủ bằng chứng và bị lọc. Các điểm tham quan không phục vụ ăn uống không bị loại chỉ vì thiếu dietary_options.
- Catalog verified có dietary_options cần nguồn có field `diet`. Mức vận động `effort` cần evidence access. Các trường mới là optional nên POI cũ vẫn đọc được.
- Thứ tự: số interests khớp giảm dần, rồi số tiêu chí crowd/adventure khớp giảm dần, cuối cùng slug tăng dần. Mỗi tiêu chí khớp có lý do hiển thị; unknown không được thưởng điểm.
- Crowd và adventure là sở thích mềm; trekking/stairs/alcohol và exclusions khác vẫn là bộ lọc cứng. “Không khí yên tĩnh” không đồng nghĩa tự loại mọi nơi đông người; người dùng chọn thêm điều cần tránh nếu muốn loại.
- Diet không biểu diễn dị ứng, nhiễm chéo hay nhu cầu y tế. Chưa có dữ liệu/kiểm chứng cho các điều kiện này.
- Pace được lưu cho planner sau này; discovery chưa lập lịch. Các giới hạn route/time/season/total-budget của ADR 0004 còn hiệu lực.

Kiểm chứng: API SQLite/PostgreSQL cho snapshot, owner/source validation, sửa profile độc lập, override, retry hash cũ, bảo toàn field khi client cũ sửa, dietary evidence/filter và tie-break. Browser tests cho apply/override/save/reload và response profile đến sau logout.
