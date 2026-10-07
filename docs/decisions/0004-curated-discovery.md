# ADR 0004 — Catalog có nguồn và gợi ý từ bản trip đã lưu

Ngày: 2026-10-07. Trạng thái: accepted cho discovery baseline, chưa phải planner.

## Lưu trữ và dữ liệu

Migration 0003 thêm `wayo.places`: slug ổn định làm khóa chính, destination/status có index và constraint; nội dung POI, các khung giờ, tags và evidence lưu trong JSON có schema version 1. Cách này cho phép thay đổi contract trong alpha; chưa thay thế toàn bộ schema chuẩn hóa destinations/tags/sources/hours trong DB-01.

Schema private, bật RLS; browser không có API ghi catalog. Import là công cụ cho operator có quyền database. Không có POI thật được seed trong migration; fixture trong tests là dữ liệu giả rõ ràng.

- Slug lowercase ASCII; tên/địa chỉ trim, so trùng theo casefold và khoảng trắng. Phát hiện trùng slug và tên/địa chỉ trong batch, tên/địa chỉ đã có dưới slug khác trong DB. Chưa có fuzzy matching hoặc phát hiện hai tên khác nhau của cùng địa điểm.
- Sources dùng URL HTTP(S), không chứa user/password; thời điểm kiểm tra phải có timezone và không trong tương lai. Không tự truy cập URL hoặc tự coi URL là bằng chứng đã xác minh.
- Người curate chịu trách nhiệm kiểm tra nội dung. `verified` đòi hỏi evidence cho identity/coordinates/tags và tất cả nhóm thông tin tùy chọn đã điền. Validator kiểm tra tính đầy đủ/cấu trúc, không xác minh sự thật của nguồn.
- Giá chưa biết là null; 0 chỉ dùng khi có nguồn xác nhận miễn phí. Khoảng giá nguyên VND theo người hoặc nhóm; chưa hỗ trợ giá phòng/combo/điều kiện khuyến mãi.
- Trekking/stairs/alcohol là ba trạng thái true/false/null. Null không có nghĩa là không có hạn chế. Crowd là quiet/moderate/busy/null.
- Giờ theo thứ trong tuần, timezone Việt Nam, không cho chồng lấn hoặc overnight trong một window; null là chưa biết, [] là không có khung mở cửa và bị loại khỏi gợi ý. Chưa xử lý ngày lễ, ngoại lệ hoặc lịch mùa vụ; discovery chưa dùng giờ để khẳng định có thể ghé thăm.
- Chỉ đọc bản `verified` có tất cả nguồn được kiểm tra trong 90 ngày gần nhất. Tài liệu cũ vẫn lưu để curator cập nhật; không âm thầm hiện như dữ liệu mới.

## Nhập liệu

JSON batch tối đa 500 địa điểm / 5 MB. Dry-run không mở kết nối DB. `--apply` kiểm tra cả file trước khi mở transaction, rồi upsert theo slug; mọi lỗi rollback cả batch. Upsert thay thế toàn bộ nội dung một địa điểm; không xóa các địa điểm vắng trong file. Dùng status disabled để gỡ khỏi discovery.

Dry-run xác minh cấu trúc/trùng trong file; kiểm tra trùng với database thực hiện khi apply. Chạy tuần tự từng batch; chưa có workflow review nhiều operator hay audit history cho catalog.

## Gợi ý

`GET /v1/trips/{id}/recommendations` xác minh owner trước khi đọc catalog. Trả trip revision để UI từ chối gợi ý cho bản trip đã đổi ở tab khác. Chỉ dùng preferences/exclusions/budget của trip đã lưu; chưa đọc profile live, chưa có snapshot/override profile cho trip.

- Chuẩn hóa các sở thích hiện có trong form sang sáu interest keys. Sở thích chưa hiểu có notice.
- Exclusions theo tags và trekking/stairs/alcohol/crowd; thiếu thông tin để đáp ứng exclusion thì loại địa điểm. Exclusion chưa hỗ trợ (ví dụ “Lịch quá dày”, cần planner) khiến kết quả trống và có thông báo rõ.
- Với hard budget: loại giá chưa biết và hoạt động có giá tối đa tính cho cả nhóm vượt ngân sách toàn chuyến. Đây chỉ là sàng lọc từng hoạt động, không đảm bảo tổng chi phí.
- Xếp theo số sở thích khớp giảm dần, tie-break slug tăng dần; tối đa hai địa điểm mỗi category, giới hạn 1–12 (UI lấy 6). Không tạo phần trăm phù hợp hoặc xác suất giả.
- Hiển thị lý do, thiếu dữ liệu và nguồn kiểm chứng. Không kiểm tra routing, thời tiết, mùa vụ, giờ đến, tổng chi phí hoặc tính khả thi lịch trình.

Phần còn lại: curate POI thật có nguồn, admin review, snapshot taste, hỗ trợ dietary/accessibility đầy đủ, ranking group/distance/time/season, planner và routing. Không đánh dấu DATA-03 hoặc RANK-02 hoàn tất.
