# Provider contract spike — foundation local

Ngày đối chiếu tài liệu: 2026-10-08. Các adapter đã có test HTTP mock cho contract và lỗi; chưa được nối với planner/public endpoint. Đây là lựa chọn thử nghiệm, chưa chốt provider production.

| Boundary | Contract thử nghiệm                                                | Cấu hình                             | Giới hạn còn lại                                                               |
| -------- | ------------------------------------------------------------------ | ------------------------------------ | ------------------------------------------------------------------------------ |
| Routing  | OSRM table, driving, longitude/latitude, giây/mét, null giữ nguyên | `WAYO_ROUTING_BASE_URL`              | Chưa kiểm tra chất lượng/mode/coverage Đà Lạt; profile phụ thuộc data server   |
| Weather  | Open-Meteo hourly UTC, mưa/probability, thời điểm truy xuất        | `WAYO_WEATHER_BASE_URL`              | 1–16 ngày trong horizon; chưa có weather rules/replan; cần xác nhận quyền dùng |
| LLM      | OpenAI Responses, strict JSON schema, refusal/incomplete thành lỗi | `WAYO_LLM_API_KEY`, `WAYO_LLM_MODEL` | Chưa chọn model/đo chi phí/chạy live; không tool calling hoặc generation       |

[OSRM docs](https://project-osrm.org/docs/v5.24.0/api/#table-service) quy định đơn vị và null cho cặp không có tuyến. [Policy demo server](https://github.com/Project-OSRM/osrm-backend/wiki/Api-usage-policy) không thay thế SLA production; không cấu hình demo URL mặc định. Cần provider/self-host và điều khoản sử dụng/cache rõ trước planner.

[Open-Meteo docs](https://open-meteo.com/en/docs) mô tả forecast. [Terms](https://open-meteo.com/en/terms) giới hạn free API cho non-commercial (dưới 10.000 calls/ngày, 5.000/giờ, 600/phút); commercial cần gói phù hợp. Attribution CC BY 4.0 nằm trong contract. Adapter không cache; cần rà soát license và cache policy trước persist/reuse dữ liệu.

[OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs) là nguồn cho JSON schema. Model phải được operator chọn tương thích. Không dùng free-tier giả định; xem [pricing](https://platform.openai.com/docs/pricing) và quota tài khoản khi qualification. Adapter giới hạn input 4.000 ký tự, output token cấu hình, `store=false`; không gửi full profile/chat mặc định. Giới hạn operation không phải trần chi tiêu toàn tài khoản; cần provider-side budget/monitoring trước production.

## Chạy

Mặc định chỉ xem trạng thái cấu hình, không mạng:

```bash
.venv/bin/python apps/api/scripts/spike_providers.py --provider routing
.venv/bin/python apps/api/scripts/spike_providers.py --provider weather
.venv/bin/python apps/api/scripts/spike_providers.py --provider llm
```

Muốn live: cấu hình URL/key/model server-only và thêm provider tương ứng vào `WAYO_PROVIDERS_ENABLED` (JSON array), rồi thêm `--live`. CLI gọi tối đa một lần; LLM có thể phát sinh phí. Không chạy LLM live trong CI. Default timeout 10 giây, cap 10 calls/operation, output 512 tokens, response 512 KiB, không automatic retry/cache. HTTP 429/timeout/invalid JSON/refusal được trả bằng error code đã che dữ liệu; không in provider response hoặc key.

Routing spike dùng hai tọa độ khảo sát ở Đà Lạt, không ghi thành POI hay dữ liệu người dùng. Weather dùng ngày hiện tại UTC. LLM chỉ yêu cầu schema ping; không tạo itinerary. Bằng chứng mock nằm ở `test_provider_foundation.py`. Cần báo cáo live latency, quality, quota, cost và cache permissions trước chốt D04–D06.
