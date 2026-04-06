# Phases — Iteration 03: Guardrails, Observability & Cost Optimization

## Overview

Add 5 production safety layers: guardrails, caching, logging, rate limiting, evaluation.

---

## Phase 5.1: Guardrails

Validate AI output before reaching users.

- [ ] Create `src/llm/guardrails.py`:
  - `validate_food_analysis(analysis)` → (is_valid, error_reason)
  - Checks: calories 0-5000, macros 0-500g, non-empty names
  - `sanitize_food_analysis(analysis)` → clamped values
- [ ] Create `tests/unit/llm/test_guardrails.py`

Verify: `uv run pytest tests/unit/llm/test_guardrails.py -v`

---

## Phase 5.2: Semantic Caching

Cache results for similar food photos (save API costs).

- [ ] Create `src/llm/cache.py`:
  - `get_cached_analysis(photo_description)` → search past results with similarity > 95%
  - `cache_analysis(description, analysis, embedding)` → store for future lookups
  - **Note:** Stub for now. Phase 6 enables pgvector and makes it real.
- [ ] Create `tests/unit/llm/test_cache.py`

Verify: `uv run pytest tests/unit/llm/test_cache.py -v`

---

## Phase 5.3: AI Call Logging

Log every AI call for observability and cost tracking.

- [ ] Create `src/models/ai_call_log.py` — SQLAlchemy model:
  - id, user_id, model, task_type, input_tokens, output_tokens, latency_ms, estimated_cost, success, error_message, cached, created_at
- [ ] Alembic migration: `uv run alembic revision --autogenerate -m "add ai_call_logs table"`
- [ ] Create `src/llm/logger.py`:
  - `log_ai_call(db, user_id, model, task_type, input_tokens, output_tokens, latency_ms, success, error_message=None, cached=False)`
  - Calculate cost from token prices (Haiku: $0.80/$4 per 1M, Sonnet: $3/$15 per 1M)
- [ ] Wire logging into `src/llm/client.py` — log after every API call
- [ ] Create `tests/integration/test_ai_logging.py`

Verify: `uv run pytest tests/integration/test_ai_logging.py -v`

---

## Phase 5.4: Rate Limiting

Prevent abuse and runaway costs.

- [ ] Create `src/llm/rate_limiter.py`:
  - `check_rate_limit(user_id, task_type)` → bool
  - Limits: 30 analyze/hour, 10 recommend/hour
  - `increment_call_count(user_id, task_type)`
- [ ] Wire into `src/api/food_logs.py` — check before analyze
- [ ] Create `tests/unit/llm/test_rate_limiter.py`

Verify: `uv run pytest tests/unit/llm/test_rate_limiter.py -v`

---

## Phase 5.5: Accuracy Tracking

Measure Claude's performance from user corrections.

- [ ] Update `src/models/food_log.py`:
  - Add `is_user_corrected` (bool)
  - Add `ai_raw_response` (JSON) — what Claude originally said
- [ ] Alembic migration
- [ ] Create `src/llm/evaluator.py`:
  - `record_correction(food_log, corrected_data)` — save when user edits
  - `get_accuracy_metrics(user_id)` → {total_logs, corrected_count, accuracy_percentage}
- [ ] Wire into PATCH `/food-logs/{log_id}` endpoint
- [ ] Create `tests/unit/llm/test_evaluator.py`

Verify: `uv run pytest tests/unit/llm/test_evaluator.py -v`

---

## Phase 5.6: AI Stats Endpoints

Expose observability metrics.

- [ ] Create `src/schemas/ai_stats.py`:
  - AiStatsSummary, AiAccuracy, CacheHitRate
- [ ] Create `src/api/ai_stats.py`:
  - GET `/api/v1/ai-stats/summary?start_date=&end_date=` → calls, tokens, cost, latency
  - GET `/api/v1/ai-stats/accuracy` → accuracy %, correction count
  - GET `/api/v1/ai-stats/cache-hit-rate` → cache % usage
- [ ] Create `tests/integration/test_ai_stats.py`

Verify: `uv run pytest tests/integration/test_ai_stats.py -v`

---

## Phase 5.7: Integration

Wire everything together.

- [ ] Update POST `/analyze` endpoint:
  - Check rate limit
  - Check cache (return if hit)
  - Call LLMClient with retry/fallback
  - Validate guardrails
  - Log the call
  - Return result
- [ ] Create `tests/integration/test_analyze_with_guardrails.py` — full flow test

Verify: `uv run pytest tests/integration/ -v` — all pass

---

## Success Criteria

- [x] Guardrails validate all output
- [x] Semantic cache works (stub)
- [x] Every call logged with cost
- [x] Rate limiting prevents abuse
- [x] Accuracy tracking from corrections
- [x] Stats endpoints expose metrics
- [x] All tests pass
- [x] No unguarded AI calls
