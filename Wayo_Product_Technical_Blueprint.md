# Wayo — AI Travel Planner cá nhân hóa cho du lịch tự túc tại Việt Nam

> **Tagline gợi ý:** *Travel your way.*

---

# 1. Tầm nhìn sản phẩm

**Wayo** là một **AI Travel Planning Agent** giúp người dùng từ trạng thái:

> “Tôi muốn đi đâu đó cuối tuần nhưng chưa biết đi đâu, ở đâu, ăn gì và sắp xếp thế nào”

đến:

> “Đây là chuyến đi hoàn chỉnh của tôi: điểm đến, lịch trình, chi phí, bản đồ, phương án dự phòng và tất cả đều phù hợp với sở thích của tôi.”

Wayo không chỉ tạo một đoạn văn lịch trình bằng LLM.

Hệ thống phải:

**Hiểu người dùng → tìm địa điểm thật → đánh giá địa điểm → xây lịch trình → kiểm tra tính khả thi → tối ưu di chuyển → giải thích → tiếp tục điều chỉnh khi có thay đổi.**

---

# 2. Vấn đề thực sự cần giải quyết

Người dùng hiện có thể hỏi một chatbot AI:

> “Lên lịch trình Đà Lạt 3 ngày 2 đêm cho tôi.”

Vì vậy, nếu Wayo chỉ tạo itinerary thì sản phẩm gần như không có lợi thế cạnh tranh rõ ràng.

Giá trị cần tạo nằm ở 5 vấn đề sâu hơn:

| Vấn đề | Wayo giải quyết |
|---|---|
| Không biết đi đâu | Destination Recommendation |
| Không biết nơi nào hợp gu | Taste Matching |
| Lịch trình AI thường không khả thi | Constraint-aware Planning |
| Di chuyển lòng vòng | Route Optimization |
| Thay đổi kế hoạch rất phiền | AI Re-planning |

Ngoài ra phải giải quyết một vấn đề cực quan trọng:

## Trust

Một lịch trình trông hay nhưng chứa:

- quán đã đóng;
- điểm cách nhau quá xa;
- địa điểm mở lúc 10h nhưng lịch trình đến lúc 8h;
- ngân sách vượt quá giới hạn;
- trekking ngay sau một chuyến bay đêm;

thì gần như vô dụng.

**Wayo phải ưu tiên “feasible itinerary” hơn “beautiful itinerary”.**

---

# 3. Positioning

Không nên positioning Wayo là:

> AI chatbot cho du lịch.

Nên là:

> **AI agent tự xây và tối ưu chuyến đi cá nhân hóa cho người Việt.**

Hoặc:

> **Your personal AI travel planner for Vietnam.**

Tên **Wayo** cũng phù hợp với định vị này vì gợi đến “your way” — chuyến đi theo cách của riêng bạn.

---

# 4. Chiến lược cạnh tranh

Thị trường AI trip planner hiện đã có nhiều sản phẩm mạnh về itinerary, map, booking và collaboration.

Vì vậy Wayo không nên cố thắng bằng số lượng feature.

## Wedge nên chọn

**Vietnam-first + Preference-first + Feasibility-first**

Tức là:

> Wayo không cần biết nhiều địa điểm nhất.  
> Wayo cần hiểu chuyến đi nào phù hợp với người dùng nhất.

---

# 5. Target User ban đầu

Không nên phục vụ tất cả traveler ngay lập tức.

## Primary Persona

**Gen Z & Millennials, 22–35 tuổi**

Đặc điểm:

- du lịch tự túc;
- thường đi 2–4 ngày;
- đi couple / nhóm bạn;
- budget khoảng 2–10 triệu/người;
- quan tâm ăn uống;
- thích trải nghiệm local;
- thích chụp ảnh;
- muốn lịch trình đủ chi tiết nhưng không quá cứng.

Đây nên là nhóm khách hàng đầu tiên.

## Persona sau MVP

- gia đình có trẻ nhỏ;
- solo traveler;
- nhóm 5–10 người;
- foreign traveler tại Việt Nam;
- business traveler kết hợp leisure.

---

# 6. Core Job-to-be-Done

Người dùng không thực sự muốn “một lịch trình”.

Họ muốn:

> “Hãy giúp tôi quyết định và tổ chức chuyến đi mà tôi sẽ thích, với ít công sức nhất.”

Wayo vì vậy phải giải quyết toàn bộ decision process:

```text
Dream
 ↓
Where should I go?
 ↓
What fits me?
 ↓
What should I do?
 ↓
Can I afford it?
 ↓
Is this itinerary realistic?
 ↓
How do I move around?
 ↓
What if something changes?
```

---

# 7. Phạm vi sản phẩm

Wayo nên phát triển qua 4 level:

| Level | Sản phẩm |
|---|---|
| L0 | AI itinerary generator |
| L1 | Personalized planner |
| L2 | AI travel agent |
| L3 | Travel ecosystem |

MVP nên đạt **L1**, đồng thời đặt nền móng cho **L2**.

Không nên cố đạt L3 ngay từ đầu.

---

# 8. MVP chính xác nên làm gì?

## MVP v1

Người dùng có thể:

1. Tạo travel profile.
2. Nhập thông tin chuyến đi.
3. Nhận destination recommendation.
4. Chọn destination.
5. AI tạo itinerary.
6. Xem itinerary trên timeline.
7. Xem toàn bộ địa điểm trên map.
8. Chỉnh sửa itinerary.
9. Chat với AI để thay đổi lịch trình.
10. Hệ thống tự tối ưu lại lịch.
11. Xem estimated budget.
12. Share chuyến đi bằng link.

### Ví dụ

Người dùng nhập:

```text
Đi với bạn gái
3 ngày 2 đêm
Budget 4 triệu/người
Xuất phát TP.HCM
Thích cafe đẹp, thiên nhiên, đồ ăn local
Không thích trekking
Không muốn lịch quá dày
```

Wayo tạo:

```text
Travel Profile

Travel style:
- Couple
- Relaxed
- Foodie
- Photography
- Nature

Budget:
~4M/person

Pacing:
Light

Adventure:
Low

Destination candidates:
1. Đà Lạt — 92%
2. Quy Nhơn — 83%
3. Phan Thiết — 77%
```

Sau khi chọn Đà Lạt:

```text
DAY 1

07:00
Khởi hành

12:00
Check-in / gửi hành lý

13:00
Ăn trưa

14:30
Cafe

16:30
Điểm ngắm hoàng hôn

18:30
Nghỉ

19:30
Dinner

21:00
Night activity
```

Từng item nên chứa:

- ảnh;
- địa chỉ;
- tọa độ;
- rating;
- estimated cost;
- thời gian cần thiết;
- thời gian di chuyển;
- lý do AI chọn;
- source;
- opening hours nếu có.

---

# 9. Những feature KHÔNG làm trong MVP

Không nên làm ngay:

- booking flight trực tiếp;
- booking hotel trực tiếp;
- payment;
- MoMo/VNPay;
- live traffic agent;
- flight tracking;
- AI video recap;
- photobook;
- social network;
- expense splitting;
- group voting;
- vision phân tích Instagram;
- native mobile app;
- multi-country itinerary.

Những thứ trên hấp dẫn nhưng sẽ khiến scope nổ rất nhanh.

---

# 10. Điểm khác biệt quan trọng nhất: Travel Taste Profile

Wayo nên xây một **Travel Taste Vector** cho mỗi user.

Ví dụ:

```json
{
  "nature": 0.85,
  "food": 0.92,
  "photography": 0.88,
  "culture": 0.35,
  "nightlife": 0.20,
  "adventure": 0.25,
  "luxury": 0.30,
  "local_experience": 0.90,
  "crowd_tolerance": 0.25,
  "pace": "relaxed"
}
```

Profile này được tạo từ:

- onboarding;
- địa điểm user like/dislike;
- lịch trình user chỉnh;
- chuyến đi trước;
- feedback sau chuyến đi.

Qua thời gian Wayo hiểu user ngày càng tốt hơn.

Đây mới là personalization thực sự.

---

# 11. Onboarding

Không nên bắt người dùng điền một form quá dài.

Mục tiêu:

**6–10 interaction, hoàn thành trong khoảng 2 phút.**

Ví dụ:

## Đi với ai?

```text
Solo
Couple
Friends
Family
```

## Gu hình ảnh

Chọn những ảnh / phong cách thích:

```text
Beach
Mountain
Cafe
Old town
Luxury resort
Street food
Nature
Nightlife
```

## Travel pace

```text
😌 Relax

🚶 Balanced

🏃 Explore everything
```

## Food

```text
Street food
Local
Cafe
Fine dining
Vegetarian
```

## Adventure

```text
Easy
Moderate
Adventure
```

## Crowds

```text
Popular places are fine

Balanced

Avoid crowds
```

AI biến các câu trả lời thành **Travel Taste Profile**.

---

# 12. Destination Recommendation Engine

Không nên để LLM tự nghĩ hoàn toàn:

> “Tôi thấy Đà Lạt phù hợp.”

Hệ thống nên score destination.

Ví dụ:

```text
DestinationScore =
0.30 × taste_match
+ 0.20 × budget_match
+ 0.15 × season_match
+ 0.15 × trip_duration_match
+ 0.10 × transport_match
+ 0.10 × group_match
```

Kết quả:

| Destination | Score |
|---|---:|
| Đà Lạt | 0.91 |
| Quy Nhơn | 0.84 |
| Phú Yên | 0.79 |
| Nha Trang | 0.68 |

LLM chủ yếu làm nhiệm vụ:

**giải thích vì sao destination phù hợp.**

---

# 13. Place Intelligence

Mỗi địa điểm trong database không chỉ có name + description.

Cần một schema đủ phong phú.

Ví dụ:

```text
Place

name
category
latitude
longitude

average_price
duration_minutes

opening_hours

indoor/outdoor

best_time_of_day

suitable_for:
couple
family
friends
solo

tags:
romantic
photography
food
local
nature
quiet

crowd_level

rain_suitable

seasonality

verification_status

source_url
last_verified_at
```

Ví dụ:

```text
Tiệm cà phê X

category:
cafe

tags:
photography
couple
quiet
mountain_view

best_time:
15:30–17:30

duration:
90 min

cost:
80k–150k

rain_suitable:
true
```

Nhờ vậy itinerary engine có thể reasoning bằng dữ liệu thay vì hallucination.

---

# 14. Data Architecture

Đây sẽ là một trong những moat lớn nhất của Wayo.

## Layer 1 — Canonical Place

Thông tin cơ bản:

```text
name
coordinates
address
category
opening_hours
price
```

## Layer 2 — Travel Intelligence

Wayo tự xây:

```text
best_time
recommended_duration
crowd_pattern
photo_score
food_score
couple_score
family_score
weather_suitability
```

## Layer 3 — Content

```text
description
tips
what_to_order
what_to_avoid
```

## Layer 4 — Evidence

```text
source
source_url
source_date
last_verified
confidence
```

---

# 15. Data Pipeline

Không nên crawl Internet một cách mù quáng.

Pipeline nên là:

```text
Source
 ↓
Extraction
 ↓
Normalization
 ↓
Deduplication
 ↓
Fact extraction
 ↓
Confidence scoring
 ↓
Human/automatic verification
 ↓
Place database
```

Ví dụ:

```text
Article:
"Top cafe Đà Lạt..."

↓

Extract:

Place: ABC Cafe
best_time: sunset
style: photography
price: 60–120k
```

Luôn lưu provenance.

---

# 16. RAG của Wayo

Wayo không nên dùng RAG đơn giản:

```text
query
 ↓
vector search
 ↓
blog chunks
 ↓
LLM
```

Nên sử dụng **Structured RAG**.

```text
User profile
      ↓
Candidate filtering
      ↓
Structured place DB
      ↓
Vector semantic retrieval
      ↓
Ranking
      ↓
Constraint checking
      ↓
LLM
```

PostgreSQL đảm nhiệm dữ liệu chính.

Vector database chỉ hỗ trợ semantic matching.

---

# 17. Place Ranking

Ví dụ user thích:

```text
couple
quiet
nature
photography
local food
```

Một địa điểm có thể được score:

```text
PlaceScore =
0.30 TasteSimilarity
+ 0.15 GroupSuitability
+ 0.15 BudgetFit
+ 0.10 SeasonFit
+ 0.10 TimeOfDayFit
+ 0.10 Popularity
+ 0.10 LocalUniqueness
```

Sau đó trừ penalty:

```text
- distance_penalty
- crowd_penalty
- weather_penalty
- schedule_penalty
```

---

# 18. Itinerary Engine

Đây là phần quan trọng nhất của toàn hệ thống.

Không nên:

```text
prompt → LLM → itinerary
```

Nên:

```text
Trip Request
      ↓
Preference Parser
      ↓
Candidate Retrieval
      ↓
Candidate Ranking
      ↓
Constraint Planner
      ↓
Route Optimizer
      ↓
Schedule Validator
      ↓
LLM Explanation
      ↓
Final Itinerary
```

---

# 19. Constraint System

## Hard Constraints

Bắt buộc tuân thủ:

```text
opening_hour
closing_hour
trip_start
trip_end
travel_time
meal_time
user_fixed_event
```

## Soft Constraints

Cố gắng tối ưu:

```text
avoid long travel
avoid crowded time
avoid excessive activities
balance food/activity
best photography time
budget
```

Ví dụ:

```text
Cafe A
best_time = sunset

Waterfall B
best_time = morning
distance(A,B)=25km
```

Planner phải biết:

```text
Morning → Waterfall
Afternoon → Cafe
```

không phải ngược lại.

---

# 20. Route Optimization

Có 5 điểm:

```text
Hotel
A
B
C
D
```

Không nên để LLM quyết định thứ tự.

Dùng routing engine:

```text
Distance Matrix

        H    A    B    C    D
H       0   10   20   15   30
A      10    0   12    5   25
...
```

Sau đó tìm sequence phù hợp.

MVP có thể dùng:

- greedy nearest-neighbor;
- Mapbox Directions / Matrix / Optimization;
- OR-Tools khi complexity tăng.

### Khuyến nghị MVP

**Mapbox trước** để triển khai prototype nhanh.

---

# 21. AI Agent Architecture

Wayo nên có một Orchestrator Agent.

```text
                    ┌─────────────────┐
                    │   User Request  │
                    └────────┬────────┘
                             ↓
                   ┌──────────────────┐
                   │ Wayo Orchestrator│
                   └────────┬─────────┘
                            │
       ┌────────────────────┼────────────────────┐
       ↓                    ↓                    ↓
Preference Agent       Place Retriever      Weather Tool
       ↓                    ↓                    ↓
Taste Profile          Candidate Places       Weather
       └────────────────────┬────────────────────┘
                            ↓
                       Place Ranker
                            ↓
                     Itinerary Planner
                            ↓
                       Route Engine
                            ↓
                     Constraint Checker
                            ↓
                      Final Itinerary
```

Tuy nhiên không cần biến tất cả thành LLM agent.

Nguyên tắc:

> **LLM cho reasoning và ngôn ngữ. Code cho deterministic logic.**

---

# 22. Tool của Agent

Agent có thể có các tool:

```text
search_places()

get_place_details()

get_weather()

calculate_route()

get_distance_matrix()

check_opening_hours()

estimate_cost()

get_user_profile()

save_trip()

replace_activity()

optimize_day()
```

Ví dụ user nói:

> “Ngày 2 tôi không muốn đi thác nữa.”

Agent:

```text
1. remove_activity()
2. retrieve alternatives
3. calculate route impact
4. check budget
5. reschedule
6. validate day
7. update itinerary
```

Đây mới thực sự là agentic behavior.

---

# 23. Re-planning

Đây nên là một trong những feature nổi bật của Wayo.

User:

> “Mai trời mưa.”

Agent:

```text
Weather
↓
Identify affected outdoor activities
↓
Retrieve indoor alternatives
↓
Evaluate preference match
↓
Optimize route again
↓
Update schedule
```

Hoặc:

> “Tôi ngủ quên đến 10 giờ.”

Wayo:

```text
Current time = 10:00

Remove impossible activities
↓
Re-score remaining places
↓
Re-optimize route
↓
New itinerary
```

Feature này khác biệt rõ với itinerary generator thông thường.

---

# 24. Tech Stack đề xuất

## Frontend

```text
Next.js
TypeScript
TailwindCSS
shadcn/ui
TanStack Query
Zustand
dnd-kit
Mapbox GL JS
```

### Vì sao Next.js?

- web-first;
- SEO tốt;
- dễ deploy;
- dễ làm share page;
- ecosystem mạnh.

---

# 25. Backend

Khuyến nghị:

```text
FastAPI
Python
Pydantic
SQLAlchemy
```

thay vì Node backend.

Lý do:

Wayo về sau sẽ có nhiều:

```text
AI pipeline
ranking
optimization
embedding
data processing
ML
```

Python thuận tiện hơn.

Kiến trúc:

```text
Next.js
   ↓
FastAPI
   ↓
Service Layer
   ↓
Supabase PostgreSQL
```

---

# 26. Database

Sử dụng:

**Supabase PostgreSQL + pgvector**

MVP chưa cần Milvus.

Postgres + pgvector là đủ.

---

# 27. Database Schema

Các table chính:

```text
users

travel_profiles

trips

trip_members

destinations

places

place_categories

place_tags

place_tag_links

place_sources

place_opening_hours

place_seasonality

place_embeddings

itineraries

itinerary_days

itinerary_items

trip_feedback

user_place_interactions
```

---

# 28. Quan hệ dữ liệu

```text
USER
 │
 ├── TRAVEL_PROFILE
 │
 └── TRIP
       │
       ├── ITINERARY
       │       │
       │       ├── DAY
       │       │    └── ITEM → PLACE
       │       │
       │       └── VERSION
       │
       └── FEEDBACK

PLACE
 │
 ├── TAG
 ├── SOURCE
 ├── OPENING HOURS
 ├── SEASONALITY
 └── EMBEDDING
```

---

# 29. Trip Versioning

Không nên overwrite itinerary.

Lưu:

```text
v1 original

v2 user removed cafe

v3 weather replanning

v4 user changed budget
```

Table:

```text
itinerary_versions

id
trip_id
version
change_reason
created_at
```

Rất hữu ích cho debugging AI.

---

# 30. Weather

Prototype có thể dùng một weather API miễn phí hoặc có free tier.

Wayo không chỉ hiển thị:

> 28°C, 70% rain.

Mà convert weather thành travel decision:

```text
rain_probability > 70%

↓

avoid:
waterfall
viewpoint
outdoor cafe

boost:
museum
indoor cafe
spa
workshop
```

---

# 31. LLM Strategy

Không hard-code sản phẩm vào một model duy nhất.

Tạo abstraction:

```text
LLMProvider

generate()
structured_output()
embedding()
```

Sau này có thể swap:

```text
Gemini
OpenAI
Claude
local model
```

---

# 32. LLM không được phép tạo Place ID

Nguyên tắc quan trọng:

Sai:

```text
LLM:
"Đi Cafe XYZ"
```

Đúng:

```text
Retriever
→ place_id=1241

LLM:
"Buổi chiều ghé {place_1241}"
```

Tên địa điểm phải đến từ database/tool.

Điều này giảm hallucination rất mạnh.

---

# 33. Structured Output

AI nên trả JSON có cấu trúc.

Ví dụ:

```json
{
  "day": 1,
  "activities": [
    {
      "place_id": "place_1241",
      "start_time": "08:00",
      "end_time": "09:30",
      "reason": "..."
    }
  ]
}
```

Không parse itinerary từ prose.

UI render từ structured data.

---

# 34. Frontend Screens

MVP nên có khoảng **7 màn hình chính**.

## Screen 1 — Landing

CTA:

> Plan your trip

Có thể demo itinerary ngay trên landing.

---

## Screen 2 — Taste Onboarding

Visual card:

```text
Who are you travelling with?

❤️ Couple

👥 Friends

👨‍👩‍👧 Family

🎒 Solo
```

---

## Screen 3 — Trip Setup

```text
From
Dates
Number of people
Budget
Destination
```

Destination có option:

> Surprise me

---

## Screen 4 — Destination Recommendation

Ví dụ:

```text
92% MATCH
Đà Lạt

Why it fits you:
✓ cool weather
✓ romantic
✓ cafe culture
✓ photography
✓ fits your budget
```

---

# 35. Screen quan trọng nhất — Trip Workspace

Desktop:

```text
┌──────────────────────────────────────────────┐
│ Wayo                                         │
├───────────────┬──────────────────────────────┤
│               │                              │
│ DAY 1         │                              │
│               │             MAP              │
│ 08:00 Cafe    │                              │
│               │                              │
│ 10:00 Place   │                              │
│               │                              │
│ 12:00 Lunch   │                              │
│               │                              │
├───────────────┴──────────────────────────────┤
│ Ask Wayo...                                  │
└──────────────────────────────────────────────┘
```

Timeline bên trái.

Map bên phải.

AI chat phía dưới hoặc drawer bên cạnh.

---

# 36. Itinerary Item

Mỗi card:

```text
15:00 – 16:30

ABC Cafe

★★★★★ 4.7

~120k/person

📍 8 phút từ điểm trước

✨ Vì sao phù hợp:
View núi + ít đông + hợp gu chụp ảnh của bạn

[Replace] [Delete] [Details]
```

---

# 37. AI Copilot

Người dùng có thể nói:

> Cho ngày 2 nhẹ hơn.

> Thay quán cafe bằng nơi ít người.

> Tôi muốn ăn BBQ tối nay.

> Không đi quá 20 phút giữa các điểm.

> Budget giảm xuống còn 3 triệu.

Agent cập nhật itinerary trực tiếp.

---

# 38. MVP địa lý

Không nên launch toàn Việt Nam ngay.

## Alpha

Chỉ:

**Đà Lạt**

Mục tiêu:

> Làm một destination cực tốt.

Data khoảng:

```text
100–200 quality places
```

Sau đó mở rộng.

## Beta

Có thể thêm:

```text
Đà Nẵng – Hội An

Ninh Bình

Quy Nhơn / Phú Yên
```

## Sau đó

```text
Phú Quốc
Hà Giang
Sa Pa
TP.HCM
Hà Nội
Huế
Nha Trang
```

---

# 39. Tại sao bắt đầu Đà Lạt?

Đà Lạt là testbed phù hợp vì có:

- cafe;
- photography;
- couple travel;
- food;
- nature;
- nhiều POI;
- trip 2–4 ngày;
- route optimization có ý nghĩa;
- weather ảnh hưởng lớn itinerary;
- nhiều style traveler khác nhau.

Một destination nhưng đủ complexity để test toàn hệ thống.

---

# 40. Data Requirement cho Đà Lạt MVP

Khoảng:

```text
150 places
```

chia:

| Category | Số lượng |
|---|---:|
| Cafe | 30 |
| Food | 35 |
| Nature | 25 |
| Attraction | 20 |
| Night | 10 |
| Culture | 10 |
| Local experience | 10 |
| Other | 10 |

Không cần hàng nghìn POI.

**150 POI được enrich kỹ tốt hơn 10.000 POI thô.**

---

# 41. Admin Dashboard

Cần dashboard:

```text
Places

Add
Edit
Disable
Verify
Update source
Update hours
Update tags
```

Có filter:

```text
verified

stale

missing hours

missing coordinates
```

Nếu không có admin tool, data rất nhanh trở thành đống khó quản lý.

---

# 42. Data Freshness

Mỗi record có:

```text
last_verified_at

confidence

status
```

Ví dụ:

```text
verified < 30 days

likely_valid 30–90 days

stale > 90 days
```

Candidate ranking có thể giảm score của dữ liệu stale.

---

# 43. Feedback Loop

Sau mỗi activity:

```text
👍 Loved it

😐 Okay

👎 Not for me
```

Hoặc:

```text
Too crowded

Too expensive

Too far

Loved the vibe
```

Update taste profile.

Ví dụ:

```text
user frequently dislikes crowded places

crowd_tolerance:
0.45 → 0.25
```

Đây là cách personalization trở thành moat theo thời gian.

---

# 44. Learning Loop

```text
Recommendation
       ↓
User action
       ↓
Feedback
       ↓
Profile update
       ↓
Better ranking
       ↓
Better recommendation
```

Càng dùng nhiều → Wayo càng hiểu user.

---

# 45. API Design

Ví dụ backend:

```text
POST /auth

GET /profile
PUT /profile

POST /trips
GET /trips/{id}

POST /destinations/recommend

GET /places/search
GET /places/{id}

POST /itineraries/generate

POST /itineraries/{id}/replan

POST /itineraries/{id}/optimize

POST /itineraries/{id}/activities

DELETE /activities/{id}

POST /feedback
```

---

# 46. Backend Modules

```text
app/

api/

agents/
    orchestrator.py
    planner.py
    replanner.py

services/
    place_service.py
    weather_service.py
    route_service.py
    profile_service.py

ranking/
    destination_ranker.py
    place_ranker.py

planning/
    scheduler.py
    constraints.py
    optimizer.py

rag/
    retrieval.py
    embeddings.py

models/

schemas/

repositories/
```

Điểm quan trọng:

**Không nhét toàn bộ logic vào một prompt khổng lồ.**

---

# 47. Architecture tổng thể

```text
                    ┌─────────────┐
                    │   Next.js   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   FastAPI   │
                    └──────┬──────┘
                           │
       ┌───────────────────┼──────────────────┐
       │                   │                  │
       ▼                   ▼                  ▼
┌─────────────┐     ┌─────────────┐    ┌─────────────┐
│ AI Planner  │     │ Place Engine│    │ Route Engine│
└──────┬──────┘     └──────┬──────┘    └─────┬───────┘
       │                    │                  │
       │                    │                  │
       ▼                    ▼                  ▼
     LLM              PostgreSQL           Mapbox
                         │
                         ▼
                      pgvector
                         │
                         ▼
                  Source / Place Data
```

---

# 48. Cost-conscious Architecture

Prototype có thể gần như không tốn infrastructure:

| Component | MVP |
|---|---|
| Frontend | Vercel |
| Database | Supabase Free |
| Backend | Render/Fly/Railway hoặc local |
| Map | Mapbox free tier |
| Weather | Free / low-cost API |
| Vector | pgvector |
| AI | Free / low-cost model |
| Storage | Supabase |

Không cần ngay:

```text
Kubernetes
Milvus
Kafka
Redis cluster
microservices
GPU
```

Đó là overengineering.

---

# 49. Roadmap thực tế

Nếu làm nghiêm túc, nên dành **8–10 tuần** cho MVP tốt.

## Week 1 — Foundation

Hoàn thành:

```text
Product spec
UI wireframe
Database schema
Repo structure
Auth
Trip CRUD
```

---

## Week 2 — Place Intelligence

Seed:

```text
100–150 Đà Lạt places
```

Build:

```text
place schema
tags
source
admin CRUD
```

---

## Week 3 — Taste Profile

Build:

```text
onboarding

travel profile

preference scoring
```

Output:

```text
User → Taste Vector
```

---

## Week 4 — Retrieval + Ranking

Build:

```text
place retrieval

embedding

filters

place scoring
```

Test:

```text
50 fake personas
```

---

# 50. Week 5 — Itinerary Planner

Build:

```text
candidate selection

time slot allocation

meal logic

activity duration

hard constraints

budget constraints
```

Đây là core week.

---

# 51. Week 6 — Map + Routing

Build:

```text
map

route

distance matrix

route optimization

travel time
```

Planner bắt đầu có itinerary khả thi.

---

# 52. Week 7 — AI Copilot

Implement:

```text
"change cafe"

"make day lighter"

"reduce budget"

"more local food"

"avoid crowded places"
```

Agent phải edit state thật.

Không chỉ trả lời text.

---

# 53. Week 8 — Weather + Replanning

Build:

```text
weather

weather suitability

alternative activity

automatic replanning
```

Demo mạnh:

> “Ngày mai mưa → Wayo tự sửa lịch.”

---

# 54. Week 9 — Polish

Build:

```text
share link

responsive UI

loading state

error handling

analytics

feedback
```

---

# 55. Week 10 — Beta

Khoảng:

```text
30–50 real users
```

Cho họ thực sự dùng để lên chuyến đi.

Quan sát hành vi thực tế.

Không chỉ hỏi:

> “Bạn thấy app hay không?”

---

# 56. Evaluation Framework

Không thể đánh giá AI planner chỉ bằng cảm giác.

Tạo test dataset.

Ví dụ:

```text
50 traveler profiles

×

10 trip configurations

=

500 planning scenarios
```

Kiểm tra:

```text
place validity

opening-hour violation

budget violation

route efficiency

preference match

schedule overload
```

---

# 57. Technical Metrics

Mục tiêu Beta:

| Metric | Target |
|---|---:|
| Valid place | >99% |
| Coordinate present | >99% |
| Opening-hour violation | <2% |
| Impossible schedule | <3% |
| Budget deviation | <10% |
| Planner failure | <2% |

---

# 58. Product Metrics

## Activation

```text
user creates first itinerary
```

Target:

> >60%

## Itinerary Acceptance

Người dùng giữ bao nhiêu activity AI đề xuất?

Ví dụ:

> 70% giữ nguyên

đó là tín hiệu rất tốt.

## Recommendation Acceptance

```text
AI recommends destination

↓

user selects recommendation
```

## Replanning Usage

Bao nhiêu người sử dụng:

> “change this”

## Share Rate

Bao nhiêu trip được share?

---

# 59. North Star Metric

Một North Star Metric hợp lý:

> **% trip mà người dùng thực sự sử dụng itinerary sau khi AI tạo.**

Không phải:

```text
number of messages

number of itineraries generated

number of AI tokens
```

---

# 60. MVP Success Criterion

Sau Beta, nếu 50 người dùng:

```text
>30 tạo itinerary hoàn chỉnh

>20 nói itinerary thực sự hữu ích

>10 dùng để đi thật

>5 quay lại tạo trip khác
```

thì project có tín hiệu tốt.

---

# 61. Monetization chưa cần build ngay

Giai đoạn đầu chỉ cần thiết kế để hỗ trợ tương lai.

## Affiliate

```text
hotel
flight
tour
activity
transport
```

## Premium

Có thể lock:

```text
unlimited trip

advanced optimization

live replanning

offline trip

group collaboration

AI travel memory
```

Nhưng không nên optimize revenue trước product-market fit.

---

# 62. Booking Strategy

MVP chỉ cần:

```text
View Hotel
        ↓
Affiliate Link
        ↓
Partner
```

Không xử lý payment.

Sau này mới tích hợp sâu.

Điều này tránh:

```text
payment compliance

refund

booking status

customer support

inventory sync
```

---

# 63. Moat dài hạn

Moat không phải LLM.

Ai cũng có thể gọi API của các model mạnh.

Wayo cần 4 moat.

## 1. Travel Taste Graph

Hiểu preference user.

## 2. Vietnam Place Intelligence

Dữ liệu enriched riêng.

## 3. Planning Engine

Constraint + routing + itinerary logic.

## 4. Behavioral Data

Biết:

```text
who liked which place

under which context

during what type of trip
```

Đây là dữ liệu rất giá trị.

---

# 64. Moat mạnh nhất về lâu dài

Ví dụ database biết:

> Couple 23–28 tuổi thích photography, budget thấp, đi Đà Lạt vào tháng 11 thường thích A hơn B.

Thông tin này không tồn tại trực tiếp trên Google Maps.

Nếu đủ user:

```text
Traveler Context
       ×
Place
       ×
Season
       ×
Feedback
```

tạo thành:

**Travel Preference Graph.**

Đó mới là moat thật.

---

# 65. Vision Version 2 — Collaborative Planning

4 người đi cùng.

Mỗi người có Taste Profile.

Wayo tìm:

```text
group preference intersection
```

Ví dụ:

```text
A likes nature

B likes cafe

C likes food

D hates walking
```

AI xây itinerary cân bằng cả nhóm.

Đây là feature rất có tiềm năng.

---

# 66. Version 3 — Real Travel Agent

Agent theo dõi chuyến đi:

```text
weather changed

flight delayed

restaurant closed

user behind schedule
```

↓

```text
re-plan automatically
```

Ví dụ:

> “Trời bắt đầu mưa. Wayo đã chuyển điểm ngắm cảnh sang sáng mai và đề xuất một workshop trong nhà gần vị trí hiện tại.”

Đến đây Wayo thực sự khác itinerary generator.

---

# 67. Version 4 — Travel Memory

Wayo nhớ:

```text
Bạn thích homestay yên tĩnh.

Bạn không thích buffet.

Bạn thích cafe view núi.

Bạn thường thức muộn khi đi du lịch.

Bạn không thích lịch trước 8h.
```

Trip sau không phải nhập lại.

Đây chính là:

> Personal Travel Agent.

---

# 68. Biggest Technical Risks

## Data Quality

Đây là risk #1.

Không phải LLM.

Nếu dữ liệu sai:

```text
planner sai
```

## Opening Hours

Opening hours thay đổi thường xuyên.

Cần:

```text
source

confidence

last_verified
```

## Route Planning

Không được dùng straight-line distance.

Phải dùng travel duration.

## Hallucination

LLM không được tự invent place.

## Cost

Không gửi hàng nghìn place vào LLM.

Pipeline:

```text
DB filter

↓

ranking

↓

top 20

↓

LLM
```

---

# 69. UX Risk

Đừng biến Wayo thành ChatGPT clone.

Chat interface chỉ nên là **secondary interface**.

Primary UX phải là:

```text
Map

Timeline

Cards

Drag & Drop

Buttons

Structured controls
```

AI nằm phía sau.

---

# 70. Một User Flow hoàn chỉnh

```text
Landing
 ↓
Create Trip
 ↓
Onboarding
 ↓
Travel Profile
 ↓
Trip constraints
 ↓
Destination suggestions
 ↓
Select destination
 ↓
Generate itinerary
 ↓
Map + Timeline
 ↓
User edits
 ↓
AI replans
 ↓
User confirms
 ↓
Share trip
 ↓
Travel
 ↓
Feedback
 ↓
Taste Profile improves
```

---

# 71. Demo Scenario nên xây

Scenario:

> Couple từ TP.HCM muốn đi Đà Lạt 3N2Đ, 4 triệu/người, thích cafe + chụp ảnh + local food, không thích trekking.

Wayo generate itinerary.

Sau đó user nói:

> “Ngày 2 trời mưa.”

Wayo tự:

```text
identify outdoor places

↓

replace activity

↓

optimize route

↓

update budget

↓

show updated map
```

Demo này thể hiện được:

```text
LLM

RAG

Agents

Recommendation

Constraint solving

Routing

Real-time data

UI
```

rất tốt.

---

# 72. Kiến trúc MVP cuối cùng

```text
USER
 │
 ▼
Next.js UI
 │
 ▼
FastAPI
 │
 ▼
Wayo Orchestrator
 │
 ├── User Profile
 │
 ├── Destination Ranker
 │
 ├── Place Retriever
 │
 ├── Place Ranker
 │
 ├── Weather Tool
 │
 ├── Route Tool
 │
 ├── Constraint Planner
 │
 └── Replanner
 │
 ▼
Supabase PostgreSQL
 │
 ├── users
 ├── profiles
 ├── places
 ├── trips
 ├── itineraries
 └── feedback
 │
 ▼
pgvector
```

---

# 73. Thứ tự build khuyên dùng

Nếu bắt đầu ngay, không nên bắt đầu bằng chatbot.

Thứ tự:

```text
1. Database schema

2. Đà Lạt place dataset

3. Trip Profile

4. Place ranking

5. Itinerary representation

6. Constraint engine

7. Route optimizer

8. LLM integration

9. UI

10. Replanning agent
```

Làm theo thứ tự này thì AI được đặt trên một nền dữ liệu và logic đáng tin.

Làm ngược:

```text
LLM → prompt → UI
```

thì rất nhanh có demo nhưng sau đó khó biến thành sản phẩm thật.

---

# 74. Scope chốt cho Wayo MVP

## Platform

**Web**

## Market

**Vietnam domestic travel**

## Initial Destination

**Đà Lạt**

## Primary Traveler

**Gen Z / Millennials, couple + friend group**

## Core Promise

> Generate a personalized, realistic 2–4 day itinerary in under 2 minutes.

## Core Features

```text
Taste onboarding

Destination / trip configuration

Personalized place ranking

AI itinerary

Route optimization

Map

Timeline editor

AI replanner

Weather-aware alternatives

Budget estimation

Share trip
```

## Không build ở MVP

```text
payment

booking engine

native mobile

social network

video recap
```

---

# 75. Định nghĩa Wayo tốt nhất

## Product Definition

> **Wayo là AI travel planning agent dành cho du lịch Việt Nam, xây lịch trình cá nhân hóa từ sở thích, ngân sách và điều kiện thực tế; sau đó liên tục kiểm tra, tối ưu và điều chỉnh chuyến đi khi nhu cầu hoặc hoàn cảnh thay đổi.**

## Technical Definition

> **Wayo = Recommendation System + Structured RAG + Constraint-based Planner + Routing Engine + LLM Agent.**

Không phải:

> **Wayo = GPT + prompt du lịch.**

---

# 76. Brand Direction

## Name

**Wayo**

## Brand Idea

Tên gợi đến:

- your way;
- way / route / path;
- travel in your own style;
- AI companion đồng hành theo “cách của bạn”.

## Tagline gợi ý

- **Travel your way.**
- **Your trip. Your way.**
- **Plan less. Travel your way.**
- **AI travel, your way.**
- **Every trip, your way.**

## Brand Personality

Wayo nên có cảm giác:

- trẻ;
- hiện đại;
- thân thiện;
- thông minh nhưng không “robotic”;
- tối giản;
- đáng tin;
- thiên lifestyle hơn enterprise.

---

# 77. Kết luận

Hướng xây Wayo nên tập trung vào ba giá trị cốt lõi:

1. **Hiểu gu người dùng**
2. **Tạo lịch trình thực sự khả thi**
3. **Có khả năng tự điều chỉnh khi chuyến đi thay đổi**

MVP tốt nhất không phải là một sản phẩm có thật nhiều tính năng.

MVP tốt nhất là một sản phẩm làm cực tốt lời hứa:

> **“Wayo tạo cho bạn một chuyến đi phù hợp với chính bạn, chứ không phải một lịch trình mẫu giống tất cả mọi người.”**

Nếu làm đúng hướng, Wayo có thể bắt đầu từ một AI trip planner nhỏ cho Đà Lạt và dần phát triển thành một **personal travel agent** hoàn chỉnh cho Việt Nam và sau đó là Đông Nam Á.
