# Place data — khởi tạo contract

Chưa có POI thật đã xác minh trong repo. Không dùng fixture kỹ thuật để tạo lịch cho người dùng.

`places.template.csv` là header nhập liệu ban đầu, phục vụ DATA-01 và kiểm chứng schema. Trước khi nhập 10 POI mẫu, cần chọn nguồn, kiểm tra quyền lưu/ảnh và provenance. Chưa tuyên bố DATA-03 hoàn thành.

- `id`: ID nội bộ ổn định, không lấy từ LLM.
- `category`: cafe/food/nature/attraction/night/culture/local/other, một category chính.
- `latitude/longitude`: số trong miền hợp lệ và xác minh đúng địa điểm.
- `price_min_vnd/price_max_vnd/price_unit`: giá nguyên VND; unit per_person/group/room/trip; thiếu để trống, không ghi 0.
- `duration_minutes`: ước lượng duration, ghi nguồn hoặc đánh dấu editorial trong evidence.
- `hours_status`: known/unknown; `opening_hours_json` sẽ chứa weekday/windows/exceptions theo schema DB sắp tới.
- `status`: draft/verified/stale/disabled. Chỉ status hợp lệ theo policy mới được retrieval.
- `source_url/source_checked_at`: bằng chứng xuất xứ và thời điểm kiểm tra; import chính thức cần nhiều nguồn theo từng field.
- `evidence_notes`: mâu thuẫn, quyền dùng nội dung, cách xác minh và hạn chế.

Đây là template capture, chưa phải database schema hoặc import pipeline production.
