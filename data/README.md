# Catalog địa điểm Đà Lạt

Catalog hiện chưa có POI thật đã xác minh. Không nhập fixture trong tests vào Supabase thật.

Contract chính thức cho importer là JSON `CatalogBatch` trong `apps/api/app/catalog.py`. `places.template.csv` là capture template cũ, chưa thể nhập trực tiếp; chuyển dữ liệu sang JSON và kiểm tra nguồn trước khi import.

## Quy trình

1. Curate thông tin từ nguồn phù hợp, ghi URL, ngày kiểm tra có timezone và note cho từng nhóm dữ kiện.
2. Tạo file JSON có `schema_version: 1` và `places` (1–500 bản ghi). Mỗi địa điểm có slug ổn định; ban đầu dùng status draft. Xem contract hoặc schema JSON để biết các trường bắt buộc.
3. Kiểm tra offline, không ghi database:

   ```sh
   .venv/bin/python apps/api/scripts/import_places.py /path/to/curated-places.json
   ```

4. Khi người curate xác minh đầy đủ, đặt status verified. Kiểm tra lại, sau đó ghi vào database cấu hình trong `apps/api/.env`:

   ```sh
   .venv/bin/python apps/api/scripts/import_places.py /path/to/curated-places.json --apply
   ```

5. Mở trip đã lưu → **Xem gợi ý địa điểm**. Chỉ địa điểm verified với tất cả nguồn không quá 90 ngày và đáp ứng exclusions mới xuất hiện.

Apply chạy một transaction cho cả file. Nhập lại cùng slug cập nhật bản ghi hiện có; không tạo ID mới. File thiếu địa điểm không xóa nó; đổi status disabled để gỡ khỏi gợi ý. Chạy tuần tự các batch. Dry-run không so với dữ liệu đã có trong DB; apply kiểm tra thêm trùng tên/địa chỉ.

## Schema JSON cho editor

Chạy từ thư mục repo:

```sh
PYTHONPATH=apps/api .venv/bin/python -c 'import json; from app.catalog import CatalogBatch; print(json.dumps(CatalogBatch.model_json_schema(), ensure_ascii=False, indent=2))' > /tmp/wayo-catalog.schema.json
```

Không dùng giá 0 hoặc access false để thay thế dữ liệu chưa biết: dùng null. `hours` là các khung `{weekday, opens, closes}`, Monday=0, giờ địa phương Việt Nam. Mỗi source có `{url, checked_at, fields, note}`; fields thuộc identity/coordinates/tags/access/price/hours/duration/diet. Verified đòi nguồn cho mọi nhóm thông tin đã điền.

Validator không kiểm chứng sự thật của trang nguồn. Không thể đổi sang verified chỉ vì file qua validation. Quy định chi tiết và giới hạn discovery: [ADR 0004](../docs/decisions/0004-curated-discovery.md).

## Chế độ ăn và mức vận động

Catalog hỗ trợ thêm `dietary_options: ["vegetarian", "vegan"]` (chỉ ghi các lựa chọn có thật) và `effort: "easy" | "moderate" | "challenging"`. Cả hai có thể null khi chưa biết. Verified có dietary_options cần source field `diet`; effort cần source field `access`. Không tự suy diễn chế độ ăn từ tên món/địa điểm. Discovery dùng thông tin này theo [ADR 0005](../docs/decisions/0005-trip-taste-snapshot.md).

## Lịch mở cửa đầy đủ

Khi hours là một danh sách, discovery coi các thứ không xuất hiện là không mở. Chỉ nhập danh sách sau khi xác minh lịch đầy đủ cả tuần. Nếu mới biết một phần, để hours null. Hai window liên tiếp không có khoảng đóng cửa được gộp khi tính giờ có thể ghé. Chưa hỗ trợ lịch ngoại lệ/ngày lễ; kết quả chỉ là tham khảo theo lịch tuần. Xem [ADR 0007](../docs/decisions/0007-opening-hours-and-visit-windows.md).
