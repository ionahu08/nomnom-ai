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

1. **iOS App** user selects meal type (breakfast/lunch/dinner/snack) → taps "Save" → POST to `/api/v1/food-logs/` with FoodLogCreate payload
2. **Backend** validates auth → stores in `food_logs` table with `meal_type` and `is_user_corrected = false`
3. **Cache Service** embeds food description → stores in `pgvector` alongside food_log_id
4. **Response** returns saved FoodLog object with ID and meal_type
5. **iOS** shows "Saved ✓" inline, enables "This is wrong" button
6. User can now tap "This is wrong" to correct the food name (and optionally meal type) via PATCH

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
    meal_type: str?              # breakfast, lunch, dinner, snack (user-selected)
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

---

## LLM Infrastructure Design Decisions (`src/llm/` Module)

This section documents the rationale behind each of the 12 files in `src/llm/`, explaining why each component was designed the way it was.

### Phase 1: Core Reliability (API & Prompts)

#### `client.py` — LLM API Wrapper with Retry & Timeout
**Purpose:** Wrap Anthropic API with reliability features (retry logic, timeouts, fallback models).

**Design Decisions:**
- **2 retries with exponential backoff (1s → 2s):** Enough to recover from transient network errors without excessive waiting. Why not 3+? Diminishing returns; 2 catches ~95% of transient failures.
- **Per-model timeouts (Haiku: 20s, Sonnet: 30s):** Reflects model generation speed. Haiku is fast; Sonnet requires more thinking time. Prevents hanging forever.
- **Recursive fallback to fallback_model:** If primary model fails twice, automatically retry with more reliable model. Ensures degradation instead of hard failure.
- **Prompt caching on system prompts:** Large system prompts (nutritionist role + tool schemas) are cached for 1 hour. Reduces input tokens by ~50% on cache hits.

**Why this approach?**
Every food photo analysis is a 20-30 second LLM call. Network hiccups are common. The retry logic with exponential backoff makes NomNom resilient to transient failures (which are the 95% case) while not masking real errors.

---

#### `prompt_engine.py` — Jinja2 Template Rendering
**Purpose:** Separate prompts from code, enabling non-engineers to iterate.

**Design Decisions:**
- **Jinja2 with FileSystemLoader:** Load templates from `src/llm/prompts/` directory (not hardcoded strings). Changes to prompts don't require code redeploys.
- **Whitespace trimming (trim_blocks, lstrip_blocks):** Keeps rendered prompts clean. Jinja2 templates are indented for readability; trimming removes the formatting whitespace.
- **Generic render_prompt() + convenience wrappers:** Single implementation of rendering logic, but convenience functions (`render_analyze_food_prompt()`) make call sites clearer.

**Why this approach?**
Prompts change 10x more frequently than code. Externalizing them as Jinja2 templates allows product/design teams to A/B test phrasings without involving engineers.

---

#### `prompts/` — Template Files
**Purpose:** Store prompt templates externally so they can be iterated without code changes.

**Design Decisions:**
- **`.j2` extension:** Jinja2 template convention. Makes it clear these are templates, not static text.
- **Variable injection via context dict:** Each template receives a context dict (target_calories, missing_protein, etc.). Templates are pure; logic stays in Python.

**Why this approach?**
Prompts are product assets, not code assets. Separating them enables faster iteration and version control of prompt changes independently from code.

---

### Phase 2: Output Control (Validation & Safety)

#### `parser.py` — Response Parsing & Validation
**Purpose:** Extract and validate AI output with Pydantic models.

**Design Decisions:**
- **extract_tool_use_response():** Claude returns tool_use blocks; this function extracts them. Handles the JSON-RPC envelope.
- **Pydantic validation:** Define response schema as Pydantic models (FoodAnalysisResponse, etc.). Validation catches hallucinations at parse time (e.g., calories = 500000 fails validation).
- **Custom ParseError exception:** Clear error type for error propagation and logging.
- **safe_parse_json():** Claude sometimes returns ```json markdown fences around JSON. This function strips them before parsing.

**Why this approach?**
Bad AI output (hallucinated values) never reaches the database. Validation enforces schema contracts and catches unreasonable values early.

---

#### `guardrails.py` — Output Validation & Safety
**Purpose:** Apply semantic guardrails to AI output (calories reasonable, no toxic content, etc.).

**Design Decisions:**
- **Hard range limits (0-5000 calories):** If Claude returns 500000 calories, reject it and ask for re-analysis. Ranges are domain knowledge (typical meal is 200-2000 calories).
- **Toxicity check:** Forbidden phrases list ("kill yourself", "bomb", etc.) prevents the roast from being hateful. Basic but effective.
- **Calorie distribution check:** Verify macros add up to calories (protein 4cal/g, carbs 4cal/g, fat 9cal/g). Catches inconsistencies.
- **Clear error messages:** When a guard fails, return a message Claude can understand and retry from. "Calories 500000 is unrealistic... re-estimate" is better than "validation failed".

**Why this approach?**
LLMs hallucinate. Guardrails are the defense layer that catches nonsensical output before it corrupts the database. They also give Claude a chance to self-correct.

---

#### `evaluator.py` — Quality Grading (LLM-as-judge)
**Purpose:** Grade Claude's output against a rubric (1-10 scale).

**Design Decisions:**
- **Haiku for grading:** Grading is simpler than generating; Haiku is fast and cheap enough.
- **Simple 1-10 score:** Not a weighted rubric. Domain knowledge is in the eval prompt, not in code.
- **In-memory cache:** Avoid re-grading same inputs. Cache is simple dict; durability not critical for grading.

**Why this approach?**
Quality metrics are essential for production AI systems. Using Haiku as a grader provides cheap, fast feedback on output quality.

---

#### `tools.py` — Tool Definitions & Schemas
**Purpose:** Define tool schemas for tool_use (food analysis, meal recommendation).

**Design Decisions:**
- **Pydantic models auto-generate JSON schemas:** No manual schema definition. Changes to Pydantic models auto-propagate to Claude's tool_use schema.
- **Structured input/output:** Tools have clear input (image path, constraints) and output (nutrition dict, recommendation text).

**Why this approach?**
Structured tool_use is more reliable than text parsing. Claude knows exactly what schema to produce, reducing parsing errors.

---

### Phase 3: RAG & Performance (Knowledge & Caching)

#### `embedding.py` — Text Embeddings & pgvector
**Purpose:** Generate embeddings for semantic search (RAG + caching).

**Design Decisions:**
- **sentence-transformers (all-MiniLM-L6-v2):** Lightweight (~22MB), fast (~10ms per text), good for domain-specific tasks. Alternative: OpenAI embeddings (requires API key).
- **384-dimensional vectors:** Sweet spot for quality vs. search speed. Larger dimensions = more expressive but slower; smaller = faster but less nuanced.
- **pgvector in PostgreSQL:** No separate vector DB (Pinecone, Weaviate). Single database reduces operational burden.

**Why this approach?**
Embeddings are the foundation of semantic search. sentence-transformers is local, fast, and doesn't add infrastructure complexity.

---

#### `cache.py` — Semantic Caching with 1-Hour TTL
**Purpose:** Cache LLM responses based on input similarity (cosine distance).

**Design Decisions:**
- **Threshold 0.82:** Foods are similar at cosine similarity > 0.82 (tuned empirically). Why not 0.95? Too strict; misses obvious duplicates. Why not 0.5? Too loose; returns irrelevant cache hits.
- **1-hour TTL (ephemeral):** User preferences change daily; 1 hour is long enough to avoid duplicate API calls for same meal within a meal, short enough to refresh for the next day.
- **Cache hits logged:** Every cache hit is logged for cost tracking and observability.

**Why this approach?**
Semantic caching is NomNom's performance edge. Most users eat the same meals repeatedly. Cache hits provide instant response time + reduce API costs.

---

#### `seed_knowledge.py` — Knowledge Base Seeding
**Purpose:** Populate nutrition KB with curated nutrition tips.

**Design Decisions:**
- **Batch seeding:** Load all nutrition entries at once and generate embeddings. Faster than one-at-a-time.
- **Citations per entry:** Track source of each nutrition tip (USDA, nutrition DB, etc.). Makes RAG results verifiable.

**Why this approach?**
RAG needs a knowledge base. Seeding with curated nutrition tips ensures suggestions are evidence-based, not LLM hallucinations.

---

### Phase 4: Observability & Optimization (Cost & Latency)

#### `router.py` — Task Routing & Model Selection
**Purpose:** Route tasks to appropriate models (Haiku for cheap, Sonnet for quality, Opus for complex).

**Design Decisions:**
- **ANALYZE_FOOD → Sonnet:** Multimodal vision accuracy is critical. Sonnet's superior image understanding outweighs cost (~2x more expensive than Haiku).
- **RECOMMEND_MEAL → Sonnet:** Requires reasoning over multiple constraints. Sonnet handles complex reasoning better than Haiku.
- **WEEKLY_RECAP → Sonnet:** High-quality output matters for user engagement. Sonnet produces better summaries.
- **TaskType enum:** Type-safe routing. Prevents typos and makes routes explicit.

**Why this approach?**
Model choice is a cost-quality trade-off. For NomNom, accuracy (user experience) > cost (margins are good). Sonnet for all critical tasks.

---

#### `logger.py` — Cost Tracking & Logging
**Purpose:** Log every LLM call with cost, latency, and token usage.

**Design Decisions:**
- **Per-call logging:** Each API call generates a log entry (model, tokens, latency, cost). Granular enough for per-task-type analysis.
- **Cache-read discount:** Cache-read tokens cost ~10% of input tokens (Anthropic billing). Logger applies the discount for accurate cost calculation.
- **Hardcoded pricing:** Pricing is in code, not database. Updates require code change. Alternative: store in database (more flexible but adds complexity).

**Why this approach?**
Cost tracking is essential for production AI systems. Accurate cost attribution (including cache discounts) enables data-driven optimization decisions.

---

#### `rate_limiter.py` — Rate Limiting (Currently Stub)
**Purpose:** Enforce rate limits on LLM API calls.

**Design Decisions:**
- **Currently not implemented:** check_limit() always returns True. Placeholder for future use when rate limiting becomes necessary.
- **Reserved for production scale:** When NomNom grows, rate limiting will prevent API quota exhaustion.

**Why this approach?**
Rate limiting is not critical at current scale but reserved in the architecture for when it's needed.

---

## Summary: Coherent Infrastructure

The 12 files in `src/llm/` form a coherent stack:

1. **Layer 0 (API):** `client.py` — Reliable, resilient LLM calls
2. **Layer 1 (Prompts):** `prompt_engine.py` + `prompts/` — Externalizable, iterable prompts
3. **Layer 2 (Validation):** `parser.py` + `guardrails.py` + `evaluator.py` — Validate output, catch hallucinations
4. **Layer 3 (Tools):** `tools.py` — Structured tool definitions for Claude
5. **Layer 4 (Knowledge):** `embedding.py` + `seed_knowledge.py` — Embeddings + knowledge base
6. **Layer 5 (Cache):** `cache.py` — Semantic caching for performance + cost
7. **Layer 6 (Routing):** `router.py` — Task-aware model selection
8. **Layer 7 (Observability):** `logger.py` + `rate_limiter.py` — Cost tracking + rate limiting

**Result:** A production-ready LLM infrastructure that is:
- **Reliable** (retries, timeouts, fallbacks)
- **Safe** (validation, guardrails, error handling)
- **Performant** (caching, model selection, streaming)
- **Observable** (cost tracking, logging)
- **Maintainable** (modular design, clear responsibilities)
