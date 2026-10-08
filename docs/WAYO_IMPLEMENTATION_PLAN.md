# Wayo — Kế hoạch triển khai và checklist MVP

Ngày lập: 07/10/2026. Trạng thái: đang triển khai sprint đầu; auth và Trip CRUD đã có code, chờ cấu hình dịch vụ thật/staging. Xem [tiến độ và bằng chứng](SPRINT_01_STATUS.md).

Nguồn: [Wayo Product & Technical Blueprint](../Wayo_Product_Technical_Blueprint.md), mục 1–77. Tài liệu này chuyển định hướng trong blueprint thành công việc có thể theo dõi; các lựa chọn bổ sung bên dưới là đề xuất, chưa phải quyết định đã được chủ dự án xác nhận. Không coi các ví dụ địa điểm, giá, điểm match hoặc free tier trong blueprint là dữ liệu đã xác minh.

## 1. Kết quả cần đạt

Một người dùng có thể nhập sở thích và điều kiện chuyến đi Đà Lạt 2–4 ngày, nhận lịch trình cá nhân hóa có thời gian di chuyển, xem trên timeline và bản đồ, sửa bằng thao tác hoặc ngôn ngữ tự nhiên, xem dự toán và chia sẻ bằng link.

Ưu tiên: **dữ liệu đáng tin → lịch trình khả thi → sửa lịch an toàn → trải nghiệm dễ dùng**.

Demo nghiệm thu chính: couple từ TP.HCM, 3N2Đ, 4 triệu/người, thích cafe/chụp ảnh/local food, không trekking; tạo lịch rồi yêu cầu “Ngày 2 trời mưa”. Hệ thống thay hoạt động phù hợp, tính lại tuyến và chi phí, giữ các sự kiện đã khóa, lưu phiên bản mới và đồng bộ bản đồ.

## 2. Phạm vi và giả định

### 2.1 Các mốc sản phẩm

| Mốc | Phạm vi | Điều kiện qua mốc |
|---|---|---|
| M0 — Foundation | Spec, schema, repo, auth, trip CRUD | Tạo và đọc trip riêng tư trên staging |
| M1 — Data & taste | Dữ liệu Đà Lạt, admin, onboarding, ranking | Truy xuất địa điểm hợp gu với nguồn rõ ràng |
| M2 — Vertical slice | Planner + routing + timeline/map cơ bản | Tạo một chuyến đi đầu-cuối từ dữ liệu thật |
| M3 — Alpha | Editor, copilot, weather replan, versioning | Demo chính chạy được, lỗi quan trọng có xử lý |
| M4 — Beta ready | Share, feedback, đo lường, kiểm thử, vận hành | Đạt release gate trước khi mời người dùng |
| M5 — Beta evaluated | 30–50 người dùng mục tiêu | Có báo cáo hành vi, chất lượng và ưu tiên tiếp theo |

### 2.2 Trong phạm vi

- Web responsive, tiếng Việt, Đà Lạt, couple/nhóm bạn nhỏ; mặc định lập kế hoạch theo giờ Việt Nam.
- Taste onboarding 6–10 tương tác; profile có thể sửa và dùng lại.
- Trip input có ngày giờ đến/rời, số người, ngân sách, điểm lưu trú hoặc điểm neo, phương tiện, nhịp đi, điều kiện bắt buộc.
- Structured retrieval, ranking, constraint planner, route optimization, budget estimate.
- Timeline/map, thêm/xóa/thay/sắp xếp hoạt động; copilot sửa state thật.
- Replan khi người dùng yêu cầu hoặc nhận đề xuất thời tiết; có diff và undo.
- Share chỉ đọc, admin dữ liệu, feedback cơ bản, quan sát lỗi và chi phí.

### 2.3 Sau alpha hoặc hoãn

- Destination recommendation nhiều thành phố chỉ bật khi có đủ dữ liệu đối chiếu và khả năng lập lịch cho các thành phố được cho chọn. Alpha Đà Lạt dùng cấu hình chuyến đi, không dựng bảng match giả.
- Feedback được thu từ alpha; tự học taste từ hành vi phức tạp và embedding nâng cao có thể theo sau baseline ranking.
- Drag & drop có thể đến sau nút di chuyển/thay thế nếu thiếu thời gian; manual editor vẫn bắt buộc.
- Không booking/payment, native app, social, expense splitting, group voting, multi-country, tracking chuyến bay, autonomous background travel agent.
- Chưa xây microservices, Kafka, Kubernetes, vector DB riêng hoặc optimizer phức tạp trước khi baseline cho thấy nhu cầu.

### 2.4 Giả định để ước lượng

- Chưa có code ứng dụng trong các file được khảo sát; tính kế hoạch từ bước foundation.
- Mốc 10 tuần là khung mục tiêu, phù hợp hơn khi có 2 người phát triển và người hỗ trợ dữ liệu/QA bán thời gian. Nếu solo, dự trù khoảng 14–18 tuần và đánh giá lại sau vertical slice; đây là ước lượng lập kế hoạch, không phải cam kết.
- Mỗi tuần là tuần làm việc tính từ ngày khởi động, chưa gắn deadline lịch cụ thể.
- Provider, phiên bản package, quota, giá và điều khoản lưu dữ liệu phải được kiểm tra lúc lựa chọn; không mặc định còn free tier như blueprint.

## 3. Những quyết định cần chốt trước khi code phụ thuộc

Ghi quyết định vào `docs/decisions/` khi triển khai. Có thể bắt đầu bằng mặc định đề xuất, nhưng cần lưu lý do thay đổi.

| ID | Câu hỏi | Mặc định đề xuất | Hạn chốt |
|---|---|---|---|
| D01 | Alpha có bao nhiêu điểm đến? | Chỉ Đà Lạt; multi-destination sau alpha | W1 |
| D02 | Ngân sách bao gồm gì? | Toàn chuyến/người; phân tách di chuyển liên tỉnh, lưu trú, ăn uống, vé, di chuyển nội đô, dự phòng | W1 |
| D03 | Ngân sách là hard hay soft? | Mặc định soft có cảnh báo; nếu user bật “không vượt” thì hard trên mức ước tính bảo thủ | W1 |
| D04 | Phương tiện nào được hỗ trợ? | Chọn một mode provider hỗ trợ đáng tin; không gắn nhãn xe máy cho kết quả ô tô | W1, xác thực W4 |
| D05 | Xử lý thiếu giờ mở cửa? | Gắn unknown; không tuyên bố đã kiểm tra; ưu tiên địa điểm đủ dữ liệu | W2 |
| D06 | Lịch trú và hành trình đến Đà Lạt? | User nhập điểm neo, giờ đến/rời và chi phí dự kiến; không tích hợp booking | W1 |
| D07 | Tự động sửa lịch đến mức nào? | User yêu cầu thì áp dụng bản hợp lệ và cho undo; thay đổi từ weather cần user chấp nhận | W1 |
| D08 | Provider và giới hạn chi phí? | Một LLM, một routing provider, một weather provider qua adapter; đặt trần/ngày và/trip | W1–W2 |
| D09 | Đăng nhập và chia sẻ? | Auth trước khi lưu trip; share riêng bằng token thu hồi được, mặc định chỉ đọc | W1 |
| D10 | Team, giờ làm và ngân sách? | Phân vai theo năng lực; cập nhật forecast sau W2 và W5 | Trước sprint đầu |

Các quyết định D02–D06 trực tiếp ảnh hưởng planner, schema và tiêu chí “khả thi”; không để UI tự diễn giải khác backend.

## 4. Kiến trúc triển khai đề xuất

Giữ stack blueprint: Next.js/TypeScript cho web; FastAPI/Pydantic/SQLAlchemy cho backend; Supabase PostgreSQL + pgvector cho dữ liệu. Dùng một backend dạng modular monolith. LLM chỉ parse yêu cầu, chọn intent và giải thích; code thực hiện tính toán và kiểm tra.

```text
Web → API/auth → Trip/Profile services
                     ↓
             Planner orchestration
                     ↓
DB filter → rank → route matrix → schedule/optimize → validate
                                                     ↓
                                          LLM explanation
                                                     ↓
                                      immutable version → UI
```

Routing phải có trước nghiệm thu planner; khoảng cách đường chim bay không được dùng làm thời gian hành trình cuối cùng. Tối ưu thứ tự phải kiểm tra lại time window và fixed events sau mỗi thay đổi.

### Cấu trúc repo dự kiến

```text
apps/web/                  # Next.js, timeline, map, copilot, admin
apps/api/app/              # API, services, planning, ranking, providers
apps/api/tests/            # unit/integration, planner regression
data/                      # schema seed, dữ liệu có quyền lưu, provenance
evals/                     # personas, scenarios, baseline, báo cáo
docs/decisions/            # quyết định kỹ thuật/sản phẩm
docs/runbooks/             # deploy, restore, lỗi provider, data refresh
infra/                     # cấu hình môi trường và triển khai
```

### Các contract cần thống nhất

- `TripRequest`: dates, arrival/departure, timezone, people_count, budget amount/scope/mode, transport, anchor, preferences, exclusions, fixed_events.
- `Place`: ID nội bộ ổn định, tọa độ, category, tags, duration, price range + đơn vị, hours + exceptions, status, provenance và độ mới từng dữ kiện quan trọng.
- `ItineraryItem`: loại place/meal/transfer/rest/fixed_event; chỉ item địa điểm tham chiếu place ID thật. Có start/end, cost range, travel duration, source và validation status.
- `ItineraryVersion`: snapshot bất biến của days/items/costs/assumptions; parent version, change reason, request ID. Khôi phục bằng tạo version mới từ snapshot cũ.
- `PlanningResult`: `valid`, `needs_attention` hoặc `infeasible`, kèm violations/unknowns, quality metadata, latency, provider usage.
- `PlanningJob`: queued/running/succeeded/failed/cancelled, request id, timeout; xử lý retry không tạo bản lịch trùng.
- API dùng schema sinh OpenAPI; lỗi có code ổn định. Generation/replan có idempotency key; cập nhật kèm expected version để tránh ghi đè khi mở hai tab.

## 5. Cách theo dõi công việc

Task ID cố định để dùng trong commit, issue hoặc board. Checkbox chỉ đánh dấu khi có bằng chứng nghiệm thu; trạng thái chi tiết và phần triển khai chưa nghiệm thu đầy đủ được ghi trong [Sprint 01](SPRINT_01_STATUS.md).

Luồng: `TODO → DOING → REVIEW → DONE`; dùng `BLOCKED` nếu có phụ thuộc chưa giải quyết. Giới hạn khoảng 1–2 task DOING/người.

- P0: bắt buộc cho alpha đáng tin.
- P1: bắt buộc trước beta công khai hoặc cải thiện alpha như ghi ở từng mục.
- P2: sau alpha/beta; không chặn release alpha.
- Vai trò: PM = sản phẩm, FE = frontend, BE = backend, DATA = dữ liệu, QA = kiểm thử. Một người có thể giữ nhiều vai trò.
- Task lớn hơn 2 ngày nên tách thành issue con lúc vào sprint. Không tính tiến độ bằng số checkbox đơn thuần; ưu tiên milestone đã nghiệm thu.

Mẫu issue:

```text
ID / tên:
Priority / milestone:
Owner / status / estimate:
Depends on:
Đầu vào và phạm vi:
Checklist triển khai:
Acceptance criteria:
Bằng chứng: PR / test report / demo / dataset version
Blocker và bước tiếp theo:
```

## 6. Backlog triển khai chi tiết

### E00 — Product spec và thiết kế luồng · W1 · PM + FE + BE

Phụ thuộc: không. Đầu ra: spec và wireframe đủ để xây foundation.

- [ ] **PROD-01 · P0** Chốt persona, trip 2–4 ngày, supported modes và ngoài phạm vi; ghi D01–D10 cùng người phụ trách quyết định.
- [x] **PROD-02 · P0** Viết user stories cho onboarding → trip → generate → edit → replan → share; mỗi story có happy path, dữ liệu thiếu và lỗi.
- [ ] **PROD-03 · P0** Wireframe landing, onboarding, trip setup, trip list, workspace, share, admin; thiết kế mobile list/map toggle và chat drawer.
- [x] **PROD-04 · P0** Định nghĩa feasible/unknown/infeasible, budget scope, fixed events, nhịp đi, bữa ăn và nghỉ; thống nhất copy hiển thị cảnh báo.
- [ ] **PROD-05 · P1** Chốt event taxonomy và công thức KPI ở mục 9; xác định cách lấy feedback “đã dùng để đi thật”.

Nghiệm thu: walkthrough demo chính trên wireframe; không còn mâu thuẫn giữa input trip, budget và quy tắc planner.

### E01 — Foundation, auth và môi trường · W1–W2 · FE + BE

Phụ thuộc: PROD-01, PROD-02.

- [ ] **BASE-01 · P0** Tạo repo structure, scripts chạy local, `.env.example`, formatter/linter, dependency lock; README cho máy mới.
- [ ] **BASE-02 · P0** Khởi tạo web/API, health endpoint, OpenAPI và typed API client; xử lý lỗi chung.
- [ ] **BASE-03 · P0** Tạo database migration workflow; tách local/staging/production, seed sample không chứa dữ liệu cá nhân.
- [ ] **BASE-04 · P0** Tích hợp auth; backend kiểm tra token/expiry, quyền owner/admin; kiểm tra RLS nếu truy cập trực tiếp qua Supabase. Không lộ service key ra frontend.
- [ ] **BASE-05 · P0** Trip CRUD và trip list tối thiểu; không user nào đọc/sửa được trip của user khác.
- [ ] **BASE-06 · P0** CI chạy lint/typecheck/build và các test liên quan; deploy staging có web → API → DB.
- [ ] **BASE-07 · P0** Adapter skeleton và spike LLM/routing/weather; ghi khả năng hỗ trợ, quota, điều khoản cache, chi phí; đặt timeout và cấu hình trần sử dụng.

Nghiệm thu: máy mới chạy theo README; user A tạo trip, user B bị từ chối truy cập; staging dùng cấu hình riêng và không chứa secret trong bundle/log.

### E02 — Schema và versioning · W1–W2 · BE

Phụ thuộc: PROD-04, BASE-03.

- [ ] **DB-01 · P0** ERD và migrations cho users/profiles/trips, destinations, places/categories/tags, sources/hours/seasonality; constraint và index truy vấn chính.
- [ ] **DB-02 · P0** Schema itinerary_versions/days/items; quy định quan hệ version và active version, tránh hai nơi lưu state mâu thuẫn.
- [ ] **DB-03 · P0** Lưu provenance theo field hoặc nhóm dữ kiện; hỗ trợ nhiều nguồn, giờ ngoại lệ, đóng cửa vĩnh viễn/tạm thời, missing/unknown.
- [ ] **DB-04 · P0** Thiết kế giá theo người/nhóm/phòng/chuyến, khoảng min–max, tiền VND; phân biệt user estimate và provider estimate.
- [ ] **DB-05 · P0** Transaction lưu version hoàn chỉnh + đổi active pointer; optimistic concurrency, idempotency, undo bằng version mới.
- [ ] **DB-06 · P1** Tables feedback/interactions/share tokens/planning jobs và retention; embedding có model/version để reindex. Hoãn trip_members nếu chưa có cộng tác.

Nghiệm thu: migrate database sạch, lưu/đọc được trip nhiều version, không có orphan items; lỗi giữa transaction không để lại lịch nửa hoàn chỉnh.

### E03 — Place intelligence và admin · W2–W4, duy trì liên tục · DATA + BE + FE

Phụ thuộc: DB-01, DB-03, BASE-04.

- [ ] **DATA-01 · P0** Data dictionary, taxonomy, seed template và rubric confidence; xác định nguồn được phép dùng/lưu, attribution và quyền dùng ảnh.
- [ ] **DATA-02 · P0** Import có validation, normalize, deduplicate theo name/location/provider ID; giữ record gốc và báo cáo lỗi để sửa.
- [ ] **DATA-03 · P0** Curate 30–50 địa điểm đầu tiên đủ cafe/ăn uống/indoor/outdoor cho vertical slice; kiểm tra thực tế tọa độ, nguồn, giờ và giá.
- [ ] **DATA-04 · P0** Admin list/detail/add/edit/disable/verify; filter stale, missing hours/coordinates/source; phân quyền admin và audit thay đổi.
- [ ] **DATA-05 · P0** Mở rộng mục tiêu 150 POI: cafe 30, food 35, nature 25, attraction 20, night 10, culture 10, local 10, other 10; category chính không đếm trùng.
- [ ] **DATA-06 · P0** Freshness policy đề xuất <30, 30–90, >90 ngày; dữ liệu critical được kiểm tra lại trước beta; địa điểm disabled không vào retrieval.
- [ ] **DATA-07 · P0** Coverage report: tỷ lệ đủ source/coordinates/hours/price, số indoor alternatives, vùng địa lý; audit thủ công mẫu POI và xử lý nguồn mâu thuẫn.
- [ ] **DATA-08 · P1** Runbook refresh định kỳ và tiếp nhận báo sai từ user; xác định người chịu trách nhiệm và SLA nội bộ.

Nghiệm thu: mọi POI được planner chọn có ID tồn tại, tọa độ hợp lệ và nguồn; field thiếu được đánh dấu unknown. Đạt 100–150 POI chất lượng trước beta, hướng đến 150; số lượng không thay thế coverage.

### E04 — Taste profile và trip setup · W3 · FE + BE

Cập nhật 2026-10-07: đã có `/profile`, GET/PUT private, sáu nhóm câu hỏi và vector version 1. TASTE-03 đã có snapshot/override tường minh; discovery dùng lựa chọn hiệu lực của trip. TASTE-01 còn wizard. Xem `docs/decisions/0003-explicit-taste-profile.md`.

Phụ thuộc: BASE-05, DB-01, PROD-03.

- [ ] **TASTE-01 · P0** Onboarding 6–10 tương tác, progress/back/skip; hoàn thành rồi sửa lại được, không ép điền mọi sở thích.
- [x] **TASTE-02 · P0** Mapping câu trả lời → taste vector có bounds/defaults và schema version; loại trừ trekking/dietary/accessibility tách khỏi điểm sở thích mềm.
- [x] **TASTE-03 · P0** Profile API/UI; trip có snapshot và override để sửa trip không vô tình sửa profile gốc.
- [ ] **TASTE-04 · P0** Trip setup validate ngày giờ, số người, budget scope, mode, anchor, fixed events và thời gian nghỉ; form tiếng Việt rõ đơn vị.
  - Cập nhật 2026-10-08: đã có UI anchor bằng tọa độ và fixed-event editor, lưu/sửa/xóa; còn map picker, giờ nghỉ và kiểm tra di chuyển.
- [ ] **TASTE-05 · P1** Kiểm tra onboarding với người dùng thử; ghi completion/time/drop-off và điều chỉnh câu hỏi gây nhầm.

Nghiệm thu: cùng input tạo vector nhất quán; exclusion không bị ranker biến thành sở thích thấp; trip đủ dữ kiện để planner chạy hoặc hỏi đúng phần còn thiếu.

### E05 — Retrieval và ranking · W3–W4 · BE + DATA

Cập nhật 2026-10-07: có catalog/importer, lọc verified/fresh/exclusions, tag ranking deterministic và UI discovery. Đã có snapshot/override profile và dietary/context matching. Chưa có POI thật, group/distance/time/season scoring hoặc planner. Xem ADR 0004; các task dưới đây chưa đủ acceptance toàn bộ.

Phụ thuộc: DATA-03, TASTE-02, TASTE-04.

- [ ] **RANK-01 · P0** Structured filter theo destination/status/mode/exclusions/giờ/ngân sách; lưu lý do loại ứng viên.
- [ ] **RANK-02 · P0** Baseline deterministic ranker: taste, group, budget, season/time, distance/crowd penalties; trọng số cấu hình được, tie-break ổn định.
- [ ] **RANK-03 · P0** Trả score breakdown và evidence để UI/LLM giải thích; có category diversity, tránh toàn cafe hoặc duplicate POI.
- [ ] **RANK-04 · P0** Tạo 50 persona kiểm thử; gắn expected exclusions và tập kết quả phù hợp để review, không coi dữ liệu giả là phản hồi khách hàng.
- [ ] **RANK-05 · P1** pgvector embeddings + hybrid retrieval, metadata filter, model version và refresh khi content thay đổi; so sánh với baseline trước khi bật mặc định.
- [ ] **RANK-06 · P2** Destination ranker nhiều thành phố, score explanation và màn recommendation; chỉ release khi dữ liệu tương ứng đủ dùng. Match score là điểm tương đối, không phải xác suất hài lòng.

Nghiệm thu: không trả POI disabled/khác destination/vi phạm exclusion; persona khác gu cho kết quả khác có thể giải thích; khi thiếu ứng viên trả thiếu dữ liệu, không bịa địa điểm.

### E06 — Routing, budget và constraint planner · W4–W5 · BE

Cập nhật 2026-10-08: có preview thời gian từng ngày từ trip bounds/fixed events, gồm booking qua đêm và khung 09:00–21:00 tham khảo. Đã đối chiếu weekly opening hours với khoảng trống, hiển thị earliest/latest start khi đủ duration. Chưa có routing, lịch ngoại lệ, meal/rest/buffer hay phân bổ POI; PLAN-03/04 chưa đủ acceptance. Xem ADR 0006.

Phụ thuộc: RANK-01–04, DB-02–05, BASE-07. Đây là đường găng.

- [ ] **PLAN-01 · P0** Routing adapter: matrix/directions, mode, units, provider timestamp; handle quota/timeout/no-route và cache theo quyền provider.
- [ ] **PLAN-02 · P0** Budget service tính từng nhóm chi phí, min–max, per-person/group conversion, shared cost và dự phòng; không double-count lưu trú/di chuyển.
- [ ] **PLAN-03 · P0** Hard-constraint validator: trip bounds, overlap, travel time, opening windows, fixed events, exclusions; xử lý giờ qua đêm và ngày ngoại lệ.
- [ ] **PLAN-04 · P0** Scheduler phân bổ ngày, bữa ăn, nghỉ, duration và buffer; giới hạn hoạt động theo pace; tính điểm neo đầu/cuối ngày.
- [ ] **PLAN-05 · P0** Optimizer greedy + local improvement có time windows; route mới luôn revalidate; so với baseline tổng travel minutes với cùng tập POI.
- [ ] **PLAN-06 · P0** Phân biệt infeasible với unknown; khi quá ngân sách/thiếu giờ/không có tuyến, trả nguyên nhân và phương án nới điều kiện; không âm thầm bỏ hard constraint.
- [ ] **PLAN-07 · P0** Generate endpoint/job có status, idempotency, timeout/cancel, lưu metadata; không publish kết quả lỗi dở dang.
- [ ] **PLAN-08 · P0** Bộ regression ban đầu: đóng cửa, overlap, ít POI, mưa, budget thấp, trip 2/3/4 ngày, arrive late, fixed event, route failure, unknown hours.

Nghiệm thu: vertical slice tạo lịch từ POI thật, routing thật, budget phân tách; kết quả valid không có hard violation đã biết. Trường hợp vô nghiệm phải được báo đúng.

### E07 — Trip workspace và manual editor · W5–W6 · FE + BE

Phụ thuộc: PROD-03, PLAN-07; có thể dựng UI với contract fixture sớm hơn.

- [ ] **UI-01 · P0** Timeline theo ngày, card có thời gian/giá/duration/travel/reason/source/freshness; không hiển thị rating/ảnh giả khi thiếu.
- [ ] **UI-02 · P0** Map markers/route đồng bộ ngày và selection; map unavailable vẫn đọc được timeline; không nối đường thẳng rồi gọi đó là route.
- [ ] **UI-03 · P0** Controls add/remove/replace/move/lock item; server tính lại lịch, chi phí và validation; báo lý do edit bị từ chối.
- [ ] **UI-04 · P0** Version history, before/after diff, undo; trạng thái tab cũ nhận conflict và reload/retry rõ ràng.
- [ ] **UI-05 · P0** Responsive mobile, keyboard labels, loading/progress/empty/error/retry, giữ input khi lỗi.
- [ ] **UI-06 · P1** Drag & drop với kết quả giống manual controls; thao tác bàn phím thay thế và không bỏ qua validator.

Nghiệm thu: chỉnh một activity làm timeline/map/budget đổi cùng version; refresh không mất state; xem và chỉnh được trên mobile.

### E08 — LLM integration và copilot · W6–W7 · BE + FE

Phụ thuộc: PLAN-03–07, DB-05, UI-03–04.

- [ ] **AI-01 · P0** LLM adapter với structured output/schema validation, timeout, retry giới hạn, prompt version và usage logging đã bỏ dữ liệu nhạy cảm.
- [ ] **AI-02 · P0** Preference/intent parser cho thay địa điểm, nhẹ hơn, giảm budget, local food, tránh đông; hỏi rõ nếu thiếu ngày/đối tượng cần đổi.
- [ ] **AI-03 · P0** Tool registry allowlist, schema arguments và kiểm tra owner ở mọi mutation; chỉ cho thao tác trên trip đang được cấp quyền.
- [ ] **AI-04 · P0** Enforce place IDs thuộc tập DB/candidates hợp lệ; explanation dựa trên evidence, không thêm rating/giờ/giá không có nguồn.
- [ ] **AI-05 · P0** Orchestrator intent → retrieve → plan → validate → commit version; thất bại giữ nguyên version cũ; xử lý chat request trùng.
- [ ] **AI-06 · P0** Copilot UI hiển thị trạng thái, thay đổi thực tế, lý do và undo; LLM lỗi vẫn dùng manual editor.
- [ ] **AI-07 · P0** Kiểm thử JSON lỗi, ID bịa, tool ngoài allowlist, prompt injection trong mô tả nguồn, timeout và concurrent updates.

Nghiệm thu: năm intent trong AI-02 sửa state thật và qua validator; không thể dùng chat sửa trip khác; không lưu prose thành lịch trình.

### E09 — Weather và replanning · W7–W8 · BE + FE

Phụ thuộc: AI-05, DATA-07, PLAN-01–06.

- [ ] **WEATHER-01 · P0** Weather adapter có vị trí, forecast timestamp, forecast horizon và freshness; trip ngoài horizon không được coi dự báo là chắc chắn.
- [ ] **WEATHER-02 · P0** Weather suitability rules cấu hình được; phân biệt mưa dự báo và giả định user “ngày 2 mưa”; không coi mọi POI indoor đều an toàn/phù hợp.
- [ ] **WEATHER-03 · P0** Tìm alternatives theo taste/time/budget/route; giữ fixed/locked/completed items và chỉ thay phần tương lai liên quan.
- [ ] **WEATHER-04 · P0** Chạy lại schedule/route/budget/validator, tạo version và diff; nếu không có phương án thì nêu conflict, không thay bằng địa điểm bịa.
- [ ] **WEATHER-05 · P1** Intent “ngủ quên đến 10h”; lấy ngày giờ tại destination, cắt phần đã qua, tính lại phần còn lại.
- [ ] **WEATHER-06 · P0** Kiểm thử forecast lỗi/quá hạn, thiếu indoor POI, fixed event ngoài trời và kết quả replan ổn định.

Nghiệm thu: demo chính hoàn chỉnh; weather provider lỗi không làm mất lịch; thay đổi chủ động từ forecast cần người dùng chấp nhận.

### E10 — Share, feedback và analytics · W8–W9 · FE + BE + PM

Phụ thuộc: UI-01–05, DB-06, PROD-05.

- [ ] **SHIP-01 · P1** Share link token khó đoán, revoke/expiry, read-only; chọn snapshot version để người nhận không thấy draft; không lộ profile/chat/email và không index mặc định.
- [ ] **SHIP-02 · P1** Feedback liked/neutral/disliked + crowded/expensive/far; chống gửi lặp, gắn đúng POI và version; có báo sai dữ liệu.
- [ ] **SHIP-03 · P1** Event instrumentation: onboarding, trip created, generation succeeded/failed, edit/replan, share, trip-used confirmation; dedup events và ghi anonymous/internal test flag.
- [ ] **SHIP-04 · P1** Dashboard/funnel tối thiểu; phân biệt thất bại kỹ thuật với infeasible input và abandoned request.
- [ ] **SHIP-05 · P2** Update taste có giới hạn từ explicit feedback, cho reset/override; không suy ra dislike chỉ từ hành động xóa vì hết giờ.

Nghiệm thu: người ngoài xem được snapshot chia sẻ nhưng không sửa/đọc riêng tư; revoke có hiệu lực; event test không tính vào KPI thật.

### E11 — Evaluation, vận hành và release · Xuyên suốt, tập trung W9 · QA + BE + FE

Phụ thuộc: bắt đầu từ PROD-04; release phụ thuộc E03–E10 theo priority.

- [ ] **QA-01 · P0** Tạo scenario schema, 50 profiles × 10 trip configs = 500 case có expected hard constraints; tách feasible, infeasible và unknown, cố định dataset version.
- [ ] **QA-02 · P0** Unit/property tests cho giờ, chi phí, constraint, ranking; integration tests cho generate/replan/version transaction/auth.
- [ ] **QA-03 · P0** End-to-end demo chính và manual edit/undo/share; test denied access, expired session, double submit và hai tab.
- [ ] **QA-04 · P0** Offline eval toàn bộ 500 case; mock provider response có kiểm soát và chạy live smoke test nhỏ để phát hiện integration mismatch.
- [ ] **QA-05 · P1** Đo p50/p95 generation/replan, peak concurrency nhỏ và cost/trip; đặt budget/latency release thresholds sau baseline đầu tiên.
- [ ] **OPS-01 · P0** Structured logs/traces với request ID, planner stage, version, latency, cost và constraint result; không log token auth hoặc full profile/chat mặc định.
- [ ] **OPS-02 · P0** Rate limit, input/tool limits, finite retries, provider quota alarms, redaction và secret management.
- [ ] **OPS-03 · P1** Backup/restore rehearsal trên môi trường thử, rollback deploy/migration strategy, monitoring và runbook sự cố/provider fallback.
- [ ] **OPS-04 · P1** Kiểm tra luồng xóa dữ liệu user, thu hồi share, retention logs; thông báo dữ liệu nào gửi provider và cơ chế feedback rõ ràng.
- [ ] **OPS-05 · P1** Release checklist ký nhận bằng report, known issues và người phụ trách vận hành; đóng blocker trước beta.

Nghiệm thu: đạt gate ở mục 9–10; rollback và restore có bằng chứng, không chỉ có tài liệu mô tả.

### E12 — Beta và học từ người dùng · W10 và cửa sổ theo dõi sau đó · PM + QA

Phụ thuộc: OPS-05.

- [ ] **BETA-01 · P1** Chuẩn bị recruitment 30–50 người đúng persona, hướng dẫn ngắn, câu hỏi feedback, event consent; chủ dự án quyết định kênh mời.
- [ ] **BETA-02 · P1** Chạy pilot khoảng 5 người trước, quan sát thao tác và sửa blocker; sau đó mở cohort lớn hơn.
- [ ] **BETA-03 · P1** Thu bug theo severity, ghi thời gian tạo lịch, chỉnh sửa và mức hữu ích; không chỉ hỏi cảm nhận chung.
- [ ] **BETA-04 · P1** Theo dõi sau ngày đi để xác nhận dùng thực tế; đo quay lại trong cửa sổ 30 ngày, không kết luận retention chỉ trong W10.
- [ ] **BETA-05 · P1** Báo cáo metrics + phỏng vấn + chi phí + giới hạn dữ liệu; quyết định cải thiện Đà Lạt hay mở destination tiếp theo.

Nghiệm thu: báo cáo có mẫu số và cửa sổ thời gian; phân biệt đăng ký, tạo trip, thực sự đi và quay lại. Kế hoạch không bao gồm việc tự gửi lời mời ở thời điểm lập tài liệu.

## 7. Lịch triển khai và phụ thuộc

| Tuần | Trọng tâm | Kết quả kiểm tra cuối tuần |
|---|---|---|
| W1 | E00, E01, thiết kế E02 | Spec + wireframe, staging, auth/trip skeleton |
| W2 | E02, E03, provider spike | Version schema, admin cơ bản, 30–50 POI có nguồn |
| W3 | E04, E05 baseline, tăng data | Profile → filtered/ranked POI; UI dùng fixture |
| W4 | E06 routing/budget/validator, E05 eval | Matrix thật + constraint tests; data coverage report |
| W5 | E06 scheduler/optimizer, E07 cơ bản | M2: generate → lưu → timeline/map bằng dữ liệu thật |
| W6 | E07 editor/version UI, E08 adapter | Edit/undo an toàn, copilot intent đầu tiên |
| W7 | E08 copilot, E09 weather | Năm intent + weather alternatives |
| W8 | E09 hoàn thiện, E10 | M3: demo mưa đầy đủ; share/feedback bắt đầu |
| W9 | E10, E11 hardening | M4: eval report, KPI, runbook, release gate |
| W10 | E12 pilot và beta rollout | Dữ liệu activation/usability; bắt đầu theo dõi trip thực |
| Sau W10 | Follow-up theo lịch chuyến đi | M5: usage thật, retention, quyết định roadmap |

Đường găng:

```text
Spec → schema → POI có chất lượng → filter/rank
                                  ↓
Provider spike → routing → constraint planner → vertical slice
                                                ↓
                                   versioned editor → copilot
                                                        ↓
                                   weather replan → eval → beta
```

Có thể làm song song: UI với contract fixtures; curate data trong lúc backend phát triển; viết eval từ khi chốt constraints. Không chờ W9 mới kiểm thử. Để khoảng 20% capacity mỗi sprint cho tích hợp/sửa lỗi; nếu quá tải thì dời P2, drag & drop, semantic retrieval nâng cao trước. Không cắt data provenance, hard validator, auth hoặc versioning để giữ ngày ra mắt.

## 8. Definition of Done

Một task chỉ DONE khi:

- [ ] Đạt acceptance criteria và xử lý empty/error/unknown có liên quan.
- [ ] Có bằng chứng phù hợp: demo, test, report hoặc dataset đã kiểm tra.
- [ ] Code thay đổi vượt lint/typecheck/build và test tương ứng; không thêm test chỉ lặp lại implementation.
- [ ] API/schema/data migration được cập nhật cùng consumer; không hard-code secret.
- [ ] Kiểm tra quyền truy cập với thay đổi liên quan dữ liệu người dùng.
- [ ] Tính năng đã tích hợp trên staging; known limitations được ghi rõ.
- [ ] Owner cập nhật trạng thái và các task bị ảnh hưởng.

## 9. Chất lượng và đo lường

### 9.1 Release metrics kỹ thuật

Các target blueprint là mục tiêu cần đo, chưa phải kết quả đã đạt. Các kiểm tra dữ liệu xác định được trong code nên có gate chặt hơn target thống kê.

| Metric | Cách đo | Gate/target đề xuất |
|---|---|---|
| Referential validity | Place-backed items có ID tồn tại và active / tổng place-backed items | 100% trên output được publish |
| Coordinate validity | Place-backed items có tọa độ hợp lệ / tổng | 100% trên output được publish |
| Real-world place validity | POI còn hoạt động, đúng vị trí qua audit / POI được audit | >99% theo blueprint; báo kích thước mẫu |
| Known hard violations | Vi phạm đã xác định trong lịch mang nhãn valid | 0 trong suite release |
| Opening-hour violation | Items ngoài giờ / items có hours đủ xác minh | <2% theo blueprint; báo riêng coverage unknown |
| Impossible schedule | Lịch được audit không thực thi được / lịch được audit | <3%; mọi lỗi xác định được phải chặn publish valid |
| Budget deviation | Phần vượt ngân sách dự toán / budget, trên các lịch soft-budget | <10% mục tiêu; báo riêng tỷ lệ vượt và nhóm chi phí chưa biết |
| Hard-budget compliance | Lịch publish valid có upper estimate vượt cap | 0; không đồng nghĩa đảm bảo giá thực tế |
| Planner failure | Lỗi kỹ thuật / request hợp lệ, dedup retry | <2%; infeasible và cancellation báo riêng |
| Generation latency | Từ submit hợp lệ đến lịch dùng được, gồm queue và provider | p95 <120 giây là mục tiêu sản phẩm đề xuất |
| Route quality | Travel minutes của optimized so với baseline trên cùng POI/constraints | Không tăng nếu không cải thiện ràng buộc/điểm mục tiêu; báo trade-off |
| Cost | Tổng LLM + route + weather usage / completed trip và replan | Chốt trần sau spike; cảnh báo trước khi vượt |

Không gọi chênh lệch giữa dự toán và budget là độ chính xác giá thực tế. Muốn đo độ chính xác dự toán cần thu actual spend sau chuyến đi và so sánh cùng phạm vi chi phí. Không dùng missing hours để làm đẹp tỷ lệ vi phạm.

### 9.2 Product metrics

| Metric | Định nghĩa |
|---|---|
| Activation | User beta được mời/onboard vào cohort tạo được itinerary đầu tiên / tổng cohort đủ điều kiện; target >60%, công bố rõ denominator |
| Itinerary acceptance | Activities gốc còn giữ trong phiên bản user chấp nhận / tổng activities gốc; tách các thay đổi do mưa |
| Replanning usage | Trip có ít nhất một replan thành công / trip có lịch đã tạo |
| Share rate | Trip tạo share link / trip có lịch đã tạo |
| North Star | Trip đến ngày đi có xác nhận thực sự dùng lịch / trip đã tạo và đến ngày đi; báo thêm tỷ lệ không phản hồi |
| Return | User tạo trip thứ hai trong 30 ngày / user đã tạo trip đầu đủ thời gian theo dõi |

Đối chiếu mục tiêu blueprint với cohort 50 người: >30 tạo itinerary hoàn chỉnh, >20 thấy hữu ích, >10 dùng đi thật, >5 quay lại. Đây là tín hiệu định hướng; không coi mẫu nhỏ là bằng chứng product-market fit. Destination recommendation acceptance chưa đo ở alpha một điểm đến.

## 10. Checklist trước khi mở beta

- [ ] Demo 3N2Đ và “ngày 2 mưa” chạy trên staging bằng provider thật.
- [ ] POI source/coordinates/status đạt gate; dữ liệu thiếu được gắn nhãn; đủ phương án indoor và bữa ăn.
- [ ] Bộ 500 scenarios có báo cáo và không còn known hard violation trong output valid.
- [ ] Edit/replan/undo không mất fixed events hoặc ghi đè version do concurrent request.
- [ ] Auth/owner/admin/share read-only và revoke đã kiểm thử.
- [ ] Timeout/quota/LLM JSON lỗi/route unavailable có trạng thái và retry hữu hạn.
- [ ] Mobile xem được lịch, map và controls; thao tác chính không phụ thuộc drag & drop.
- [ ] Không còn blocker: mất dữ liệu, lộ dữ liệu, lịch sai được gắn valid, không tạo/xem/sửa được trip.
- [ ] Có monitoring, trần chi phí, backup/restore và rollback đã thử.
- [ ] Analytics dùng denominator rõ; có cách lấy feedback sau chuyến đi.
- [ ] Known issues, người trực xử lý và phạm vi beta được ghi lại.

## 11. Rủi ro và phương án xử lý

| Rủi ro | Dấu hiệu sớm | Xử lý |
|---|---|---|
| Curate dữ liệu chậm | W2 chưa đủ 30–50 POI có nguồn | Giảm vùng phục vụ, ưu tiên coverage; không thay bằng POI bịa |
| Hours/giá lỗi thời | Nhiều nguồn mâu thuẫn/unknown | Queue verify, hiển thị độ mới, giảm confidence, không gắn valid vô điều kiện |
| Routing không phù hợp mode | Mode không hỗ trợ hoặc tuyến bất thường | Spike sớm, giới hạn mode công khai, chọn provider thay thế qua adapter |
| Planner quá tham | Nhiều case vô nghiệm, ngày quá dày | Baseline đơn giản + validator; trả ít hoạt động hơn hoặc hỏi nới constraint |
| LLM sửa sai state | ID lạ, event khóa bị thay | Allowlist, DB validation, transaction, version conflict và regression suite |
| Vượt chi phí/latency | Retry nhiều, matrix lớn, prompt dài | Filter/top-k, cache hợp lệ, timeout, quota, đo từng stage |
| Timeline 10 tuần không đủ | Hai sprint liên tiếp trượt gate | Reforecast, dời P2/P1 tùy gate, giữ chất lượng core |
| UI đẹp nhưng thiếu giá trị | User sửa gần hết hoặc không mang lịch đi | Quan sát pilot, phân tích lý do sửa, ưu tiên usefulness hơn feature mới |
| Kết luận beta quá sớm | User chưa đến ngày đi | Theo dõi cohort sau W10, tách chưa có dữ liệu khỏi thất bại |

## 12. Việc nên làm ngay trong sprint đầu

1. Chốt D01–D10 và phạm vi alpha, đặc biệt budget/mode/giờ đến-rời.
2. Hoàn thành PROD-02–04: user stories, wireframe workspace và quy tắc khả thi.
3. Tạo repo, môi trường và migrations; triển khai auth/trip CRUD trên staging.
4. Tạo seed template; curate 10 POI mẫu thật để kiểm chứng schema trước khi nhập hàng loạt.
5. Spike route/LLM/weather và ghi giới hạn/cost; chuẩn bị 10 scenario planner đầu tiên.

Điểm kết thúc sprint đầu: có thể đăng nhập, tạo trip, lưu dữ liệu, xem 10 POI mẫu có nguồn và có contract rõ để bắt đầu ranking/planning. Chưa yêu cầu chatbot hoặc itinerary hoàn chỉnh ở mốc này.

## 13. Bảng cập nhật tiến độ tuần

Sao chép bảng này mỗi tuần; liên kết task ID đến issue nếu dùng công cụ quản lý bên ngoài.

| Tuần | Milestone | Task DONE + bằng chứng | DOING + owner | BLOCKED + lý do | Quyết định/cắt scope | Forecast |
|---|---|---|---|---|---|---|
| W1 | M0 | — | — | — | — | Chưa khởi động |

Checklist review tuần:

- [ ] Demo đầu ra có thể dùng, đối chiếu gate milestone.
- [ ] Cập nhật task status, owner, estimate còn lại và blocker.
- [ ] Xem data coverage, eval failures, latency và chi phí nếu đã có pipeline.
- [ ] Chốt tối đa 3 kết quả chính cho tuần tiếp theo.
- [ ] Ghi decision log khi đổi scope hoặc định nghĩa metric.
- [ ] Điều chỉnh forecast dựa trên năng lực thực tế; không tự đánh dấu DONE vì đã đến hạn.

## 14. Đối chiếu với blueprint

| Nhóm blueprint | Phần kế hoạch triển khai |
|---|---|
| 1–9, 38–40, 69–77: positioning, scope, demo | Mục 1–3, E00, E12 |
| 10–17, 41–44: taste/data/RAG/ranking | E02–E05, E10 |
| 18–23, 29–33: planner, route, agents, version, weather | E06, E08, E09 |
| 24–28, 45–48, 72: stack, API, architecture | E01, E02, mục 4 |
| 34–37: UI/coplan | E07, E08 |
| 49–60: roadmap, evaluation, metrics | Mục 7–10, E11–E12 |
| 61–67: monetization và tầm nhìn dài hạn | Backlog sau beta; không chặn MVP |
| 68: technical risks | Mục 11 và các release gate |

Các điều chỉnh chủ ý so với roadmap gốc: tích hợp routing trước nghiệm thu planner; dựng UI cơ bản sớm để có vertical slice; eval và observability xuyên suốt; multi-destination dời sau alpha; theo dõi kết quả beta kéo dài theo ngày đi thực tế.
