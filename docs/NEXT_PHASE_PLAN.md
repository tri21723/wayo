# Sau foundation — M1 Data & taste, chuẩn bị M2

Ngày lập: 08/10/2026. Trạng thái: TODO. Phạm vi được chọn: tiếp tục phát triển local, chuẩn bị deployment; chưa triển khai staging. Xem [review foundation](FOUNDATION_REVIEW.md) và [backlog tổng thể](WAYO_IMPLEMENTATION_PLAN.md).

## Mục tiêu và phần tái sử dụng

M1 kết thúc khi người dùng nhập sở thích, lưu trip và nhận danh sách địa điểm Đà Lạt **thật, có nguồn, phù hợp điều kiện**, còn admin có thể cập nhật và kiểm duyệt dữ liệu. M1 chưa tạo lịch trình khả thi; đó là gate M2.

Tái sử dụng auth/owner/admin guard, profile + trip snapshot, Trip CRUD/revision, catalog/importer, availability, weekly visit windows, discovery và provider adapters hiện có. Không viết lại foundation hoặc coi catalog trống là hoàn tất dữ liệu.

Mã `M1-xx` dưới đây là task con, liên kết task gốc để tránh đếm tiến độ hai lần. Một task chỉ DONE khi có code/dataset, kiểm thử, tài liệu và bằng chứng nghiệm thu. Mỗi người giữ tối đa 1–2 task DOING. Ước lượng là ngày công tập trung, không phải deadline; giả định một developer và chủ dự án hỗ trợ xác minh dữ liệu. Các task lớn tách thành PR theo checklist.

## Board và thứ tự phụ thuộc

| ID     | Task gốc             | Đầu ra                                          | Vai trò        | Phụ thuộc                               | Ngày công | Trạng thái |
| ------ | -------------------- | ----------------------------------------------- | -------------- | --------------------------------------- | --------- | ---------- |
| M1-01  | DATA-01, DB-01/03    | Dictionary, rubric, ADR schema catalog          | BE + DATA      | Foundation local                        | 1–2       | TODO       |
| M1-02  | DB-01/03, DATA-02/06 | Migration, provenance, revision, import an toàn | BE             | M1-01                                   | 2–3       | TODO       |
| M1-03  | DATA-04              | Admin API và audit                              | BE             | M1-02                                   | 2–3       | TODO       |
| M1-04  | DATA-04, UI-05       | Admin UI kiểm duyệt                             | FE             | M1-03                                   | 2–3       | TODO       |
| M1-05  | DATA-01/03           | Pilot 10 POI có nguồn                           | DATA + QA      | M1-01; import sau M1-02                 | 2–3       | TODO       |
| M1-06  | DATA-03/06/07        | 30–50 POI và coverage report                    | DATA + QA      | M1-02, M1-05                            | 3–5       | TODO       |
| M1-07  | TASTE-01/05          | Wizard, resume/edit, usability notes            | FE + QA        | Profile hiện có                         | 2–3       | TODO       |
| M1-08  | RANK-01/02/03        | Filter/ranker có breakdown và version           | BE             | M1-02, M1-05                            | 2–3       | TODO       |
| M1-09  | RANK-04, QA          | 50 persona, regression và demo M1               | QA + FE + BE   | M1-04/06/07/08                          | 2–3       | TODO       |
| M2-P01 | BASE-07, PLAN-01     | Routing qualification và quyết định provider    | BE + chủ dự án | Endpoint, quota/chi phí đã chốt         | 1–2       | TODO       |
| OPS-01 | BASE-06              | CI xanh trên GitHub, artifact sẵn deploy        | BE             | Commit/push theo yêu cầu                | 0.5–1     | TODO       |
| OPS-02 | BASE-03/06           | Staging và nghiệm thu hai tài khoản             | BE + QA        | User chọn hosting, config riêng, OPS-01 | 1–2       | DEFERRED   |

M1 khoảng **18–28 ngày công**, gồm cả curation; thời gian thực tế phụ thuộc việc kiểm chứng nguồn. Có thể làm wizard và curation song song với admin nếu có người phụ trách riêng. Routing qualification khoảng 1–2 ngày công ngoài M1. Đánh giá lại ước lượng sau pilot 10 POI, không hứa lịch cố định khi chưa biết chất lượng nguồn.

Đường phụ thuộc chính: M1-01 → M1-02 → M1-03/04 và M1-05/06 → M1-08 → M1-09. Staging hoãn theo lựa chọn hiện tại, không chặn phát triển M1 local; phải hoàn tất trước nghiệm thu staging hoặc mời người dùng bên ngoài.

## Checklist triển khai và nghiệm thu

### M1-01 — Chuẩn hóa dữ liệu trước khi mở rộng catalog

- [ ] Đối chiếu `Place` hiện có với nhu cầu discovery/planner: category, tags, coordinates, duration, price unit, weekly hours, date exceptions, indoor/outdoor, dietary, accessibility, crowd/effort.
- [ ] Quy định `unknown`, `not_applicable`, `closed`, `stale`; không dùng 0/false thay dữ kiện chưa biết.
- [ ] Mỗi nhóm dữ kiện có nguồn, URL, ngày kiểm chứng, người kiểm chứng, confidence và attribution/quyền lưu. Không lấy ví dụ trong blueprint làm dữ liệu thật.
- [ ] Chốt ADR phần nào giữ JSON versioned, phần nào tách bảng/index; danh tính POI ổn định khi sửa tên/slug, không làm mất liên kết trip tương lai.
- [ ] Cập nhật template và ví dụ tổng hợp trong tests; tách fixture khỏi dataset thật.

**Nghiệm thu:** hai người đọc cùng record hiểu giống nhau về giá/giờ/độ mới; record thiếu dữ liệu không được tự chuyển verified; ADR ghi migration/backward compatibility và các truy vấn cần tối ưu.

### M1-02 — Persistence, import và freshness

- [ ] Migration giữ nguyên users/trips/profiles/catalog; bổ sung revision/catalog schema version và provenance theo ADR, index cần thiết.
- [ ] Nâng cấp importer dry-run: normalize, phát hiện trùng ID/provider/name + tọa độ, báo dòng/field sai và nguồn mâu thuẫn; không tự gộp record chưa chắc chắn.
- [ ] Import không ghi đè bản admin vừa sửa: expected revision hoặc conflict report; batch lỗi rollback toàn bộ.
- [ ] Chính sách freshness cấu hình theo nhóm dữ kiện, có `checked_at`/`expires_at` hoặc phép tính tương đương; mốc 30/90 ngày là đề xuất cần chốt, không mặc định đúng cho mọi field.
- [ ] Test migrate fresh/upgrade/downgrade trên PostgreSQL; bảo toàn dữ liệu cũ, RLS và browser roles không có quyền schema.
- [ ] Test round-trip dữ liệu, idempotent import, duplicate, stale revision, malformed evidence và transaction rollback.

**Nghiệm thu:** import lại không nhân bản; dữ liệu cũ đọc được; record disabled không xuất hiện ở discovery; mọi thay đổi có revision và nguồn truy vết. Chạy trên DB dùng một lần trước khi áp dụng môi trường thật.

### M1-03 — Admin API có kiểm duyệt và audit

- [ ] List/detail/create/update/disable/verify, phân trang và filter missing/stale/status/category; mọi route dùng admin allowlist server-only.
- [ ] Định nghĩa transition draft → verified → stale/disabled; verify yêu cầu đủ evidence critical và ghi người/thời điểm kiểm chứng.
- [ ] Update dùng expected revision; stale write trả 409, không overwrite âm thầm.
- [ ] Audit append-only ghi actor ID, action, POI ID, before/after phù hợp, reason, timestamp trong cùng transaction; không ghi token hoặc profile cá nhân.
- [ ] Dùng chung service giữa importer và admin để không có đường ghi bỏ qua audit/validation; import gắn actor/run ID rõ ràng.
- [ ] Test 401/403, metadata giả admin, transition sai, stale write, rollback audit, dữ liệu riêng tư không xuất hiện trong lỗi/log.

**Nghiệm thu:** user thường không đọc/ghi API admin; admin tắt POI thì discovery loại ngay; mọi mutation đã commit có audit tương ứng. Sinh và kiểm tra OpenAPI/types.

### M1-04 — Admin UI phục vụ curation

- [ ] Trang danh sách có search/filter, trạng thái dữ liệu và lý do chưa đủ verify.
- [ ] Editor có đơn vị giá/duration, tuần/ngày ngoại lệ, nguồn theo field; xem preview record trước lưu.
- [ ] Verify/disable cần thao tác rõ ràng và lý do; hiển thị audit history, conflict có reload mà không tự ghi đè.
- [ ] Loading/empty/error/retry, labels/bàn phím và layout mobile; UI guard đi cùng API guard.
- [ ] Browser flow: tạo draft → thêm evidence → verify → discovery thấy → disable → discovery không thấy; non-admin bị chặn, hai tab conflict.

**Nghiệm thu:** người phụ trách dữ liệu có thể hoàn thành một record mà không sửa JSON bằng tay. BFF không cache dữ liệu quản trị và giữ error/request ID contract.

### M1-05/M1-06 — POI thật và coverage

- [ ] Pilot 10 POI: đa dạng cafe/food/indoor/outdoor, khu trung tâm và ngoài trung tâm; có record thiếu/nguồn mâu thuẫn để thử workflow.
- [ ] Xác minh tọa độ, tên/địa chỉ, duration, giờ hoạt động, giá và cách tính; lưu nguồn theo quyền sử dụng. Giá/giờ không xác minh được giữ unknown.
- [ ] Chủ dự án/DATA duyệt pilot, sửa dictionary/workflow trước khi mở rộng.
- [ ] Tăng lên 30–50 POI thật, không tính fixture hoặc duplicate; gợi ý coverage tối thiểu: 6 cafe, 8 food, 6 trải nghiệm indoor, 6 outdoor (nhóm có thể giao nhau; tổng POI đếm ID duy nhất).
- [ ] Ít nhất 20 POI có đủ coordinates + duration + hours + evidence để làm ứng viên planner; nếu không đạt thì ghi thiếu coverage, không tăng confidence để đạt số lượng.
- [ ] Báo cáo source/coordinates/hours/price/duration completeness, tuổi dữ liệu, category, khu vực, dietary evidence và indoor alternatives; list cụ thể POI cần xử lý.
- [ ] Audit thủ công ít nhất 10 record, gồm tất cả record có nguồn mâu thuẫn; ghi dataset version và ngày review.

**Nghiệm thu:** dataset được truy vết và import có báo cáo; discovery không hiển thị dữ kiện thiếu như đã xác minh. Số lượng 30–50 là gate M1, mục tiêu 100–150 trước beta giữ ở DATA-05 và chưa làm trong sprint này.

### M1-07 — Wizard sở thích

- [ ] Tách profile hiện có thành 6–10 tương tác ngắn với progress/back/skip; skip dùng default/unknown theo contract, không suy ra sở thích.
- [ ] Hoàn thành/lưu/sửa lại, conflict và lỗi mạng giữ dữ liệu nhập; tái sử dụng snapshot/override đã có.
- [ ] Luồng guest → login rõ ràng; đổi tài khoản/đăng xuất không mang profile hoặc phản hồi đang chờ sang phiên khác.
- [ ] Browser tests cho back/skip/save/edit/retry/conflict/sign-out; keyboard/mobile.
- [ ] Walkthrough với 3–5 người thử khi có thể, ghi vấn đề và thời gian hoàn thành; không coi persona tổng hợp là người dùng thật.

**Nghiệm thu kỹ thuật:** wizard dùng được end-to-end với profile API, cùng lựa chọn tạo cùng vector. TASTE-05 chỉ DONE khi có quan sát người dùng thật; nếu chưa có người thử thì ghi riêng REVIEW, không chặn kiểm thử kỹ thuật.

### M1-08 — Ranking deterministic có bằng chứng

- [ ] Tách hard filters và soft scoring; trả reason codes cho excluded/unknown để debug và giải thích.
- [ ] Tái sử dụng exclusions, dietary, freshness và weekly windows; bổ sung group/mode/season chỉ khi có dữ liệu và quy tắc được định nghĩa.
- [ ] Config/version cho trọng số và score breakdown; missing feature không bị coi như dữ kiện đã biết; tie-break ID ổn định.
- [ ] Diversity category và deduplicate; hiển thị vì sao phù hợp + nguồn + giới hạn còn thiếu.
- [ ] Distance feature chỉ dùng khi có anchor/coordinates, ghi rõ khoảng cách tham khảo; thời gian di chuyển cuối cùng phải dùng routing thật tại M2.
- [ ] Không gọi shortlist price filter là kiểm tra toàn bộ ngân sách trip; phần lưu trú/di chuyển/buffer chờ budget service M2.
- [ ] Test invariants hard exclusions, status, stale evidence, unknown hours, fixed/rest windows, empty candidates; regression với pilot rồi dataset đầy đủ.

**Nghiệm thu:** thứ tự ổn định, gu khác tạo kết quả khác có thể giải thích; không nới hard constraints để có đủ kết quả và không hiển thị score như xác suất hài lòng. RANK-02 tổng thể chỉ DONE khi đủ feature đã cam kết; phần distance/travel phụ thuộc routing ghi rõ nếu còn thiếu.

### M1-09 — Đánh giá và đóng mốc

- [ ] 50 persona tổng hợp versioned trong `evals/`, có expected exclusions/allowed candidates; phân bố 2/3/4 ngày, couple/friends, budget, quiet/lively, dietary, stairs/trekking, late arrival và fixed/rest constraints.
- [ ] Báo cáo 0 vi phạm hard exclusions/status/owner; liệt kê case thiếu ứng viên hoặc cần nguồn tốt hơn.
- [ ] Review top kết quả bằng rubric relevance/diversity/evidence; lưu baseline để so sánh, không tạo “accuracy” từ nhãn chưa duyệt.
- [ ] Demo local: wizard → tạo trip → apply profile → discovery thật → admin disable POI → refresh; kiểm tra hai tài khoản, conflict và lỗi mạng.
- [ ] API PostgreSQL + browser + build/lint/typecheck/contracts/format xanh; cập nhật trạng thái task gốc theo đúng phần hoàn tất.
- [ ] Chốt dataset version, report, PR/commit và danh sách known limitations trước khi mở planner.

**Gate M1:** admin workflow hoạt động, 30–50 POI có nguồn với coverage đạt, onboarding/discovery có regression; không còn lỗi nghiêm trọng đã biết ở quyền truy cập hoặc dữ liệu. Thiếu nguồn/coverage thì ưu tiên curation, không chuyển sang generate để che thiếu dữ liệu.

## M2-P01 — Qualification routing trước planner

- [ ] Chọn endpoint phù hợp Đà Lạt/driving; xác minh điều khoản, quota, cache và chi phí tại thời điểm sử dụng, ghi ADR. Không mặc định public demo endpoint phù hợp production.
- [ ] Đối chiếu ít nhất 10 cặp tọa độ trung tâm/ngoại thành, chiều đi/về, điểm không có tuyến; xác nhận đơn vị và mode.
- [ ] Ghi latency, errors, quota và dự toán calls/trip; chốt timeout/call budget/cache policy và xử lý partial/null matrix.
- [ ] Directions/geometry để map dùng tuyến thật; không gọi đường thẳng là tuyến đường.
- [ ] Kết quả không đạt thì chọn provider khác; chưa có routing đạt chuẩn thì planner không được báo valid dựa trên số phút tự đoán.

Weather/LLM live qualification làm ở mốc cần dùng; không cần bật hoặc chi tiền để hoàn tất M1.

## M2 — Lộ trình kế tiếp sau gate dữ liệu

| Thứ tự | Task gốc      | Đầu ra và tiêu chí chính                                                                                                 | Phụ thuộc             |
| ------ | ------------- | ------------------------------------------------------------------------------------------------------------------------ | --------------------- |
| 1      | DB-02/04/05   | Itinerary snapshot bất biến, active pointer, giá/đơn vị, idempotency/revision/undo transaction; test rollback và hai tab | M1 schema, ADR budget |
| 2      | PLAN-01/02    | Matrix thật + budget toàn chuyến min/max theo đơn vị; lỗi provider/unknown minh bạch                                     | M2-P01, DB-04         |
| 3      | PLAN-03/04/06 | Validator độc lập, scheduler giữ fixed/rest/anchor/bounds/hours/travel; valid/unknown/infeasible                         | Coverage M1, bước 2   |
| 4      | PLAN-05/07/08 | Greedy baseline + cải thiện có revalidate; generate job idempotent, timeout/cancel và regression                         | Bước 1–3              |
| 5      | UI-01/02/05   | Timeline/map cùng version, nguồn/giá/travel/cảnh báo; map lỗi vẫn đọc lịch                                               | Generate contract     |
| 6      | QA + gate M2  | Demo trip thật 2/3/4 ngày, reload không mất lịch; không hard violation, API/provider lỗi giữ bản cũ                      | Bước 1–5              |

Chỉ sau M2 mới mở manual editor/version UI đầy đủ, copilot và weather replan (M3). Embeddings, multi-destination và chia sẻ không nằm trong sprint dữ liệu này. Ước lượng M2 sẽ lập lại khi biết routing/coverage, tránh cộng tuần dựa trên giả định chưa kiểm chứng.

## Ba task nên bắt đầu ngay khi triển khai tiếp

1. **M1-01:** rà catalog hiện tại, viết dictionary + ADR + fixture minh họa thiếu/đủ dữ liệu.
2. **M1-02:** migration/revision/provenance và importer bảo toàn dữ liệu; kiểm chứng PostgreSQL dùng một lần.
3. **M1-03:** admin API/audit có tests, làm nền cho UI và pilot curation.

Chủ dự án có thể chuẩn bị nguồn POI muốn dùng trong lúc code các task này. Hosting staging, ngân sách provider và người kiểm chứng dữ liệu cần chốt trước phần phụ thuộc tương ứng; không cần chờ các quyết định đó để bắt đầu M1-01.
