# NomNom — Iteration 03: Guardrails, Observability & Cost Optimization

**Phase:** Phase 5 (full plan)

**Goal:** Add safety guardrails, semantic caching, AI call logging, rate limiting, and accuracy tracking.

**Resume Skills:** Guardrails, Cost Optimization, AI Observability, Model Evaluation

---

## What's Built

- LLM harness with retry, fallback, structured output
- Food photo analysis via Haiku (via harness)
- iOS camera + food logging

## What We're Building

**Production safety layer:**
- Guardrails: validate AI output (calories, protein, food name sanity)
- Semantic cache: reuse results for similar food photos (save API costs)
- AI call logging: track every AI call (model, tokens, latency, cost)
- Rate limiting: per-user call limits (prevent abuse)
- Accuracy tracking: measure how often AI gets food wrong (from user corrections)
- AI stats endpoints: expose observability metrics to the app

## Phases

### Phase 5.1: Guardrails

Validate AI output before it reaches users.

#### 5.1.A: Create `src/llm/guardrails.py`

```python
# What it does:
# - Validates AI output sanity
# - Calorie range: 0-5000 (no meal is 10k calories)
# - Macros: 0-500g each (protein, carbs, fat)
# - Food name: non-empty, under 200 chars, no harmful content
# - Roast: non-empty, under 500 chars, no harmful content

# Key functions:
# - validate_food_analysis(analysis: dict) -> tuple[bool, str | None]
#     Returns (is_valid, error_reason)
#     Example: (False, "calories out of range: 6000")
# - sanitize_food_analysis(analysis: dict) -> dict
#     Clamps values to safe ranges
#     Example: clamped_calories = min(analysis['calories'], 5000)
```

Files to create:
- `src/llm/guardrails.py` — output validation + clamping

#### 5.1.B: Test guardrails

Files to create:
- `tests/unit/llm/test_guardrails.py` — test calorie range, macro range, food name validation

Commands:
- `uv run pytest tests/unit/llm/test_guardrails.py -v`

---

### Phase 5.2: Semantic Caching

Cache results for similar food photos to save API costs.

#### 5.2.A: Create `src/llm/cache.py`

```python
# What it does:
# - Before calling Haiku, check if we've seen this food before
# - Generate embedding of the food photo description
# - Search food_logs table for embeddings with cosine similarity > 0.95
# - If found: return cached result (no API call)
# - If not found: call Haiku, save embedding, return result

# Note: Embeddings table (pgvector) is built in Phase 6.
# For now, this is a stub that always calls the API.
# Phase 6 enables pgvector and this becomes functional.

# Key functions:
# - get_cached_analysis(photo_description: str) -> FoodAnalysisResponse | None
#     Search for similar past results
#     Return first match with similarity > 0.95
# - cache_analysis(photo_description: str, analysis: FoodAnalysisResponse, embedding: list[float])
#     Store embedding + result for future lookups
```

Files to create:
- `src/llm/cache.py` — semantic cache lookup (stub for now, real impl in Phase 6)

#### 5.2.B: Test cache lookup

Files to create:
- `tests/unit/llm/test_cache.py` — test cache hit/miss (mocked)

Commands:
- `uv run pytest tests/unit/llm/test_cache.py -v`

---

### Phase 5.3: AI Call Logging

Log every AI call for observability and cost tracking.

#### 5.3.A: Add AiCallLog model

Update `src/models/`:
- Create `src/models/ai_call_log.py`:
  ```python
  # SQLAlchemy model:
  # - id (PK)
  # - user_id (FK to users, nullable)
  # - model (str) — "claude-haiku-4-5-20251001"
  # - task_type (str) — "analyze_food", "recommend_meal", "weekly_recap"
  # - input_tokens (int)
  # - output_tokens (int)
  # - latency_ms (int)
  # - estimated_cost (float) — calculated from token prices
  # - success (bool)
  # - error_message (text, nullable)
  # - cached (bool) — was a cached result used?
  # - created_at (datetime)
  ```
- Update `src/models/__init__.py` — add AiCallLog

#### 5.3.B: Create alembic migration

Commands:
- `uv run alembic revision --autogenerate -m "add ai_call_logs table"`
- `uv run alembic upgrade head`

#### 5.3.C: Create `src/llm/logger.py`

```python
# What it does:
# - Logs every AI call to ai_call_logs table
# - Calculates cost from token prices:
#   - Haiku: $0.80 / 1M input, $4 / 1M output
#   - Sonnet: $3 / 1M input, $15 / 1M output
# - Async: doesn't block the main request

# Key functions:
# - log_ai_call(
#     db: AsyncSession,
#     user_id: int,
#     model: str,
#     task_type: str,
#     input_tokens: int,
#     output_tokens: int,
#     latency_ms: int,
#     success: bool,
#     error_message: str | None = None,
#     cached: bool = False
#   ) -> AiCallLog
#     Calculate cost and insert row
```

Files to create:
- `src/llm/logger.py` — AI call logging

#### 5.3.D: Wire logging into LLMClient

Update `src/llm/client.py`:
- Import logger
- After each API call: log to database
- Pass latency, token counts, model name, task type

#### 5.3.E: Test logging

Files to create:
- `tests/integration/test_ai_logging.py` — test log_ai_call inserts correctly

Commands:
- `uv run pytest tests/integration/test_ai_logging.py -v`

---

### Phase 5.4: Rate Limiting

Prevent abuse and runaway costs.

#### 5.4.A: Create `src/llm/rate_limiter.py`

```python
# What it does:
# - Per-user rate limiting via Redis (or in-memory for now)
# - Limits:
#   - 30 analyze calls per hour
#   - 10 recommendation calls per hour
# - Returns 429 Too Many Requests if exceeded

# Key functions:
# - check_rate_limit(user_id: int, task_type: str) -> bool
#     Returns True if within limit
# - increment_call_count(user_id: int, task_type: str)
#     Increment counter
```

Files to create:
- `src/llm/rate_limiter.py` — per-user rate limiting (in-memory for now)

#### 5.4.B: Wire rate limiting into API

Update `src/api/food_logs.py`:
- Before calling analyze: check rate limit
- If exceeded: return 429 with message "Too many requests. Limit: 30/hour"

#### 5.4.C: Test rate limiter

Files to create:
- `tests/unit/llm/test_rate_limiter.py` — test increment, check limit, reset

Commands:
- `uv run pytest tests/unit/llm/test_rate_limiter.py -v`

---

### Phase 5.5: Accuracy Tracking

Measure model quality from user corrections.

#### 5.5.A: Create evaluator

Update `src/models/food_log.py`:
- Add `is_user_corrected` (bool) column to FoodLog
- Add `ai_raw_response` (JSON) column to store what the AI said

Alembic migration:
- `uv run alembic revision --autogenerate -m "add food_log columns for eval"`
- `uv run alembic upgrade head`

#### 5.5.B: Create `src/llm/evaluator.py`

```python
# What it does:
# - Track user corrections to measure AI accuracy
# - When user PATCHes a food log: compare original AI output vs user's corrected values
# - Calculate correction rate: how often AI got food name wrong

# Key functions:
# - record_correction(
#     db: AsyncSession,
#     food_log: FoodLog,
#     corrected_data: dict
#   )
#     Store what the user changed
# - get_accuracy_metrics(db: AsyncSession, user_id: int) -> dict
#     Return: total_logs, corrected_count, accuracy_percentage
```

Files to create:
- `src/llm/evaluator.py` — correction tracking

#### 5.5.C: Wire evaluator into PATCH endpoint

Update `src/api/food_logs.py`:
- When user PATCHes a food log: call evaluator.record_correction()

---

### Phase 5.6: AI Stats Endpoints

Expose observability metrics via API.

#### 5.6.A: Create `src/schemas/ai_stats.py`

```python
# Pydantic schemas:
# - AiCallLogResponse — one call log entry
# - AiStatsSummary — total calls, tokens, cost, avg latency (date-filterable)
# - AiAccuracy — food ID accuracy rate, total corrections
# - CacheHitRate — % of calls that used cached results
```

Files to create:
- `src/schemas/ai_stats.py` — response schemas

#### 5.6.B: Create `src/api/ai_stats.py`

```python
# Endpoints:
# - GET /api/v1/ai-stats/summary?start_date=2026-01-01&end_date=2026-01-31
#     Return total calls, tokens, cost, avg latency
# - GET /api/v1/ai-stats/accuracy
#     Return accuracy percentage from user corrections
# - GET /api/v1/ai-stats/cache-hit-rate
#     Return % of calls that used cache
```

Files to create:
- `src/api/ai_stats.py` — stats endpoints

#### 5.6.C: Test AI stats

Files to create:
- `tests/integration/test_ai_stats.py` — test /summary, /accuracy, /cache-hit-rate endpoints

Commands:
- `uv run pytest tests/integration/test_ai_stats.py -v`

---

### Phase 5.7: Integration

Wire everything together.

#### 5.7.A: Update food_logs.py API endpoint

Update `src/api/food_logs.py` POST /analyze:
1. Check rate limit (rate_limiter.py)
2. Check cache (cache.py) — returns if hit
3. Call LLMClient.create_message_with_retry()
4. Validate guardrails (guardrails.py)
5. Log call (logger.py)
6. Return result

#### 5.7.B: Integration test

Files to create:
- `tests/integration/test_analyze_with_guardrails.py` — full flow with mocked Anthropic

Commands:
- `uv run pytest tests/integration/ -v` — all integration tests pass

---

## Success Criteria

- [x] Guardrails validate all AI output
- [x] Cache lookup (stub, functional in Phase 6)
- [x] Every AI call logged to database
- [x] Rate limiting prevents abuse
- [x] Accuracy tracking from user corrections
- [x] AI stats endpoints expose metrics
- [x] All unit + integration tests pass
- [x] No AI calls reach users without going through guardrails

## Next After Phase 5

Phase 6 enables pgvector and makes semantic caching functional. Phase 7 adds RAG recommendations with streaming.
