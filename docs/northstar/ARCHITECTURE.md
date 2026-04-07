# Architecture — NomNom

System design, component interactions, and data flow for the NomNom app.

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     NomNom iOS App (SwiftUI)                │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Camera     │  │   Today      │  │   Settings   │     │
│  │              │  │              │  │              │     │
│  │ • Photo      │  │ • Food logs  │  │ • Cat style  │     │
│  │ • LLM        │  │ • Macros     │  │ • Targets    │     │
│  │ • Save       │  │ • Recommend  │  │ • Logout     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│           │               │                  │              │
│           └───────────────┴──────────────────┘              │
│                      │                                      │
│                 APIClient                                   │
│            (Auth + HTTP methods)                            │
│                      │                                      │
└──────────────────────┼──────────────────────────────────────┘
                       │ HTTPS (ngrok tunnel)
                       │ https://ngrok-url.ngrok-free.dev
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           NomNom-Backend (Python/FastAPI)                   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │                 API Routes                         │   │
│  │                                                    │   │
│  │  POST   /api/v1/auth/login           → Auth       │   │
│  │  POST   /api/v1/auth/register        → Auth       │   │
│  │  POST   /api/v1/food-logs/analyze    → AI Service │   │
│  │  POST   /api/v1/food-logs/           → Save       │   │
│  │  PATCH  /api/v1/food-logs/{id}       → Correct    │   │
│  │  GET    /api/v1/food-logs/today      → List       │   │
│  │  GET    /api/v1/profile              → Get        │   │
│  │  PUT    /api/v1/profile              → Update     │   │
│  │  GET    /api/v1/recommendations/meal → RAG        │   │
│  └────────────────────────────────────────────────────┘   │
│           │                                │               │
│           ▼                                ▼               │
│  ┌──────────────────────┐  ┌────────────────────────┐    │
│  │   AI Service         │  │   Service Layer        │    │
│  │                      │  │                        │    │
│  │ • Orchestrate LLM    │  │ • Food log CRUD        │    │
│  │ • Parse response     │  │ • Profile CRUD         │    │
│  │ • Apply guardrails   │  │ • Auth + JWT           │    │
│  │ • Retry + timeout    │  │                        │    │
│  └──────────────────────┘  └────────────────────────┘    │
│           │                                │               │
│    ┌──────┴─────┐                         │               │
│    ▼            ▼                         │               │
│  ┌──────────┐  ┌─────────────┐           ▼               │
│  │  Claude  │  │ Cache + RAG │  ┌──────────────────┐    │
│  │   API    │  │             │  │  PostgreSQL      │    │
│  │          │  │ • Semantic  │  │                  │    │
│  │          │  │   cache     │  │ • users          │    │
│  │          │  │ • pgvector  │  │ • food_logs      │    │
│  │          │  │ • KB search │  │ • user_profiles  │    │
│  └──────────┘  └─────────────┘  │ • embeddings     │    │
│                        │          └──────────────────┘    │
│                        ▼                                   │
│              ┌──────────────────┐                         │
│              │ Embeddings       │                         │
│              │ (sentence-       │                         │
│              │  transformers)   │                         │
│              └──────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## Request Flow: Analyze Food Photo

1. **iOS App** captures photo → compresses → sends multipart POST to `/api/v1/food-logs/analyze`
2. **APIClient** attaches Authorization header (JWT)
3. **Backend** validates auth token → saves photo to disk
4. **AI Service** sends image to Claude with system prompt
5. **LLM** returns JSON-structured food analysis (name, calories, macros, roast)
6. **Cache** generates embedding of food description → checks pgvector for similar cached analyses
7. **Response** returned to iOS (food name, calories, macros, cat roast, photo path)
8. **iOS** displays result with photo, lets user "Save" or "Retake"

## Request Flow: Save Food Log

1. **iOS App** user taps "Save" → POST to `/api/v1/food-logs/` with FoodLogCreate payload
2. **Backend** validates auth → stores in `food_logs` table with `is_user_corrected = false`
3. **Cache Service** embeds food description → stores in `pgvector` alongside food_log_id
4. **Response** returns saved FoodLog object with ID
5. **iOS** shows "Saved ✓" inline, enables "This is wrong" button
6. User can now tap "This is wrong" to correct the food name via PATCH

## Request Flow: Get Today's Logs

1. **iOS App** pulls down to refresh or loads Today tab
2. **Backend** queries `SELECT * FROM food_logs WHERE user_id = ? AND DATE(logged_at) = TODAY`
3. **Response** returns array of FoodLogResponse objects
4. **iOS** displays as cards with thumbnail, macros, roast, delete button

## Request Flow: Get Meal Recommendation

1. **iOS App** user taps "What should I eat?" → GET `/api/v1/recommendations/meal`
2. **Backend** RAG service queries `nutrition_kb` table for top-K nutrition tips via pgvector
3. **AI Service** injects KB entries as context to Claude prompt: "Based on these nutrition tips, suggest a meal"
4. **Claude** returns meal suggestion text
5. **Response** includes recommendation text + count of KB entries used
6. **iOS** displays in modal sheet

## Data Model

### Users Table
```python
class User(Base):
    __tablename__ = "users"
    id: int (PK)
    email: str (unique)
    hashed_password: str
    created_at: datetime
```

### User Profiles Table
```python
class UserProfile(Base):
    __tablename__ = "user_profiles"
    id: int (PK)
    user_id: int (FK → users)
    age: int?
    gender: str?
    height_cm: float?
    weight_kg: float?
    activity_level: str?
    cat_style: str?              # sassy, grumpy, wholesome, etc.
    calorie_target: int?
    protein_target: int?
    carb_target: int?
    fat_target: int?
    dietary_restrictions: list?
    allergies: list?
    cuisine_preferences: list?
```

### Food Logs Table
```python
class FoodLog(Base):
    __tablename__ = "food_logs"
    id: int (PK)
    user_id: int (FK → users)
    photo_path: str
    food_name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    food_category: str?
    cuisine_origin: str?
    cat_roast: str
    ai_raw_response: dict?       # Full Claude response (for audit)
    embedding: Vector(384)       # pgvector for semantic cache
    is_user_corrected: bool      # User edited the food name?
    logged_at: datetime          # When user ate it
    created_at: datetime         # When we logged it
```

### Nutrition KB Table
```python
class NutritionKBEntry(Base):
    __tablename__ = "nutrition_kb"
    id: int (PK)
    content: str                 # Nutrition tip text
    embedding: Vector(384)       # pgvector for RAG search
    category: str?               # macros, hydration, timing, etc.
    created_at: datetime
```

## Authentication Flow

1. **Registration:** POST `/api/v1/auth/register` with email + password
   - Hash password, store user in DB
   - Return JWT access token
   - iOS saves token to Keychain

2. **Login:** POST `/api/v1/auth/login` with email + password
   - Verify password, return JWT token
   - iOS saves token to Keychain

3. **Subsequent Requests:** All API requests include `Authorization: Bearer {JWT}`
   - `get_current_user` dependency validates JWT
   - Returns User object for downstream use
   - On 401 (expired/invalid), iOS logs out user and redirects to LoginView

## LLM Harness

The `AIService` orchestrates all LLM calls with:
- **Retry logic** — exponential backoff (2^attempt seconds)
- **Timeouts** — 30-second hard timeout per request
- **Fallback models** — if Claude fails, try Haiku first, then text-davinci
- **Structured output** — tool_use for JSON-validated responses
- **Error guardrails** — semantic validation of food data (calories reasonable, macros > 0, etc.)
- **Logging** — every call logged with tokens, latency, errors

## Semantic Cache & RAG

### Semantic Cache
When a user photographs food:
1. Generate embedding of food description (name + category)
2. Query pgvector table for similar embeddings (cosine distance < 0.15)
3. If hit found, return cached analysis instead of calling Claude
4. Reduces latency + API costs for repeat meals

### RAG for Recommendations
When user asks "What should I eat?":
1. Query `nutrition_kb` embeddings for top-5 entries (cosine distance)
2. Concatenate KB entries as context in system prompt
3. Claude returns personalized meal suggestion grounded in nutrition tips
4. Response includes count of KB entries used (for transparency)

## External Services

| Service | Purpose | Endpoint |
|---------|---------|----------|
| Claude API | LLM analysis + recommendations | api.anthropic.com/v1/messages |
| Sentence-Transformers | Text embeddings | Local model (all-MiniLM-L6-v2) |
| ngrok | Public tunnel to localhost | ngrok-url.ngrok-free.dev |
| PostgreSQL | Primary database | localhost:5432 |
| pgvector | Vector similarity search | Extension on PostgreSQL |

## Key Architectural Decisions

### Why Semantic Cache?
- Food logs are repetitive (user eats same meals repeatedly)
- LLM analysis is deterministic for same input
- Cache hits provide instant feedback + save API costs
- Embedding-based similarity allows fuzzy matching ("chicken breast" ≈ "grilled chicken")

### Why RAG for Recommendations?
- LLM alone produces generic suggestions
- Seeding with user-curated nutrition KB makes suggestions evidence-based
- Transparent: users see which tips informed the suggestion
- Extensible: add more KB entries as we grow nutrition library

### Why pgvector Over External Vector DB?
- Single database reduces operational complexity
- PostgreSQL is already required for auth + logs
- pgvector is battle-tested, fast enough for this scale
- No additional infrastructure cost

### iOS Keychain for Auth Token
- Secure storage of JWT (encrypted at rest by OS)
- Auto-deleted if user logs out
- Survives app restart
- Credentials never logged or exposed in network traffic
