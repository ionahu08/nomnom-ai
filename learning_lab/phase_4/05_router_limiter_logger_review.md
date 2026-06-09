# Phase 4 Day 3: Code Review — router.py, rate_limiter.py, logger.py

**Goal:** Understand the current state of NomNom's LLM infrastructure before optimizations on Day 5.

**Context:** These three files form the backbone of request routing, rate limiting, and observability. Reviewing them identifies what works, what's broken, and what needs to be fixed.

---

## Executive Summary

| File | Status | Critical Issues | Fixable on Day 5 |
|------|--------|------------------|------------------|
| `router.py` | Functional | ❌ ANALYZE_FOOD assigned to Haiku (should be Sonnet) | ✅ Yes (1 line) |
| `rate_limiter.py` | Incomplete | 🚨 check_limit() is a stub (always returns True) | ⚠️ Partial (needs Redis) |
| `logger.py` | Mostly functional | 🔴 estimate_cost() ignores cache pricing | ✅ Yes (add cache token handling) |

**Key Finding:** Cost tracking is fundamentally broken. Cache hits are over-reported by 10–20× because the logger doesn't apply cache-read discounts.

---

## File 1: router.py

**Location:** `NomNom-Backend/src/llm/router.py` (98 lines)

**Purpose:** Maps task types to models. Decides which Claude model to use for each NomNom task.

### Architecture

```
TaskType (enum)           TASK_ROUTES (dict)        ModelRoute (class)
├─ ANALYZE_FOOD    →      Router config        ├─ primary_model
├─ RECOMMEND_MEAL  →      ├─ Haiku            ├─ fallback_model
└─ WEEKLY_RECAP    →      ├─ Sonnet           ├─ max_tokens
                           └─ Sonnet           └─ temperature

Entry point: get_route(task_type) → ModelRoute
```

### Core Functions

| Function | Purpose | Lines |
|----------|---------|-------|
| `get_route(task_type)` | Main lookup: returns ModelRoute config | 69–85 |
| `get_model_for_task(task_type)` | Convenience: returns just model name string | 88–91 |
| `get_temperature_for_task(task_type)` | Convenience: returns just temperature | 94–97 |

### Issues Found

#### ❌ Issue 1: ANALYZE_FOOD assigned to Haiku (WRONG)
- **Location:** Line 51
- **Current:** `primary_model="claude-haiku-4-5-20251001"`
- **Should be:** `primary_model="claude-sonnet-4-20250514"`
- **Why it's wrong:**
  - Food photo analysis requires **multimodal vision** + **reasoning** (estimate portions, identify ingredients, calculate nutrition)
  - Haiku's vision is weaker than Sonnet's on ambiguous/complex dishes
  - Weak vision → wrong calorie estimates → user distrust → churn
- **Cost impact:** Saves $0.004/call ($120/month at 1000 daily requests) but costs users' trust
- **Day 1 learning:** You already identified this in `02_model_tiering.md` — the decision framework says "multimodal? YES → Sonnet required"
- **Day 5 action:** Change primary_model to Sonnet

#### ⚠️ Issue 2: fallback_model declared but never used
- **Location:** Line 52
- **Current:** `fallback_model="claude-sonnet-4-20250514"` exists but has no enforcement logic
- **Problem:** When would fallback activate? After N failures? Rate limited? Undefined.
- **Impact:** Dead code—callers don't know it exists, and even if they did, they can't invoke it
- **Day 5 action:** Either implement fallback logic (in client.py harness) or document why fallback is disabled

#### 🟡 Issue 3: No model name validation
- **Location:** Lines 50–65
- **Problem:** Model names are just strings, no validation against real Claude models
- **Risk:** Typo like `"claude-haiku-4-5-20250513"` (wrong date) would silently succeed, fail at API call time
- **Better:** Validate model name format or query Anthropic API for valid models
- **Day 5 action:** Optional—add basic format validation or raise error on unknown models

---

## File 2: rate_limiter.py

**Location:** `NomNom-Backend/src/llm/rate_limiter.py` (86 lines)

**Purpose:** Prevents per-user API call abuse. Enforces rate limits per task type (e.g., "max 30 food analyses/hour").

### Architecture

```
LIMITS (dict)                RateLimiter (class)
├─ analyze_food: 30/hr  →   ├─ check_limit()      [STUB]
├─ recommend_meal: 10/hr →  ├─ get_limit()        [OK]
└─ weekly_recap: 5/hr   →   ├─ get_limit_message()[OK]
DEFAULT: 100/hr              └─ logger             [UNUSED]

Entry point: check_limit(user_id, task_type) → bool or raises exception
```

### Core Functions

| Function | Purpose | Lines | Status |
|----------|---------|-------|--------|
| `check_limit(user_id, task_type)` | Check if user exceeded hourly quota | 42–74 | 🚨 STUB |
| `get_limit(task_type)` | Return limit for task type | 77–79 | ✅ OK |
| `get_limit_message(task_type)` | Return user-friendly error message | 82–85 | ✅ OK |

### Issues Found

#### 🚨 Issue 1: check_limit() is a complete stub
- **Location:** Lines 42–74
- **Current:** Always returns `True` (no enforcement)
  ```python
  # TODO: Implement with Redis when integrated
  # ... commented Redis code ...
  return True  # ← Always passes!
  ```
- **Impact:** ZERO rate limiting. Users can make unlimited API calls.
- **Risk scenario:** User writes a loop that calls API 5000×/hour → costs $2000+ in minutes, no protection
- **Commented code shows intended behavior:**
  1. Query Redis for call count in last hour
  2. Increment counter
  3. Set expiry to 1 hour
  4. Raise RateLimitExceeded if limit exceeded
- **Day 5 action:** Implement with Redis (requires Redis setup) OR use database counter as fallback

#### 🟠 Issue 2: RateLimitExceeded carries no metadata
- **Location:** Lines 24–27
- **Current:**
  ```python
  class RateLimitExceeded(Exception):
      pass
  ```
- **Problem:** Exception is empty. When caught, callers can't tell users:
  - "Come back in X seconds" (no retry_after)
  - "You have N calls left" (no current_count)
  - "Your limit is M per hour" (no limit)
- **Better:**
  ```python
  class RateLimitExceeded(Exception):
      def __init__(self, message, retry_after=None, limit=None, current_count=None):
          self.retry_after = retry_after
          self.limit = limit
          self.current_count = current_count
          super().__init__(message)
  ```
- **Day 5 action:** Add metadata fields to exception, propagate from check_limit()

#### 🟡 Issue 3: logger imported but never used
- **Location:** Line 21
- **Current:** `logger = logging.getLogger(__name__)` (declared, never called)
- **Missing observability:**
  - No log when user hits rate limit
  - No log for suspicious activity (approaching limit)
  - Can't diagnose rate limit abuse
- **Day 5 action:** Add logging calls:
  - `logger.warning()` when limit exceeded
  - `logger.info()` when approaching 80% of limit

#### 🟡 Issue 4: task_type is raw str, should be enum
- **Location:** Line 45
- **Current:** `task_type: str`
- **Inconsistency:** router.py uses `TaskType` enum, rate_limiter uses string
- **Risk:** Typo like `"analyse_food"` (British spelling) would silently fall through to DEFAULT_LIMIT (100) instead of enforcing 30
- **Better:** Import TaskType enum and use `task_type: TaskType`
- **Day 5 action:** Update signature and validation logic

---

## File 3: logger.py

**Location:** `NomNom-Backend/src/llm/logger.py` (164 lines)

**Purpose:** Logs every AI API call for cost tracking, latency monitoring, and observability.

### Architecture

```
PRICING (dict)               AICallLogger (class)        TimerContext (manager)
├─ Haiku: [input, output]  ├─ estimate_cost()          ├─ __enter__()
├─ Sonnet: [input, output] ├─ extract_token_usage()    ├─ __exit__()
└─ Opus: [MISSING!]        ├─ log_call()               └─ elapsed_ms
                            └─ logger (unused)

Entry point: log_call(...) → dict (ready for DB write)
```

### Core Functions

| Function | Purpose | Lines | Status |
|----------|---------|-------|--------|
| `estimate_cost(model, input_tokens, output_tokens)` | Calculate USD cost from tokens | 37–63 | 🔴 BROKEN |
| `extract_token_usage(response)` | Pull tokens from API response | 66–83 | ✅ OK |
| `log_call(...)` | Create complete log entry | 85–143 | ⚠️ PARTIAL |
| `TimerContext` | Measure latency with `with` statement | 146–163 | ✅ OK |

### Issues Found

#### 🔴 Issue 1: estimate_cost() ignores cache pricing (CRITICAL)
- **Location:** Lines 37–63
- **Current:** Only calculates from `input_tokens` and `output_tokens`
  ```python
  input_cost = (input_tokens / 1_000_000) * pricing["input"]
  output_cost = (output_tokens / 1_000_000) * pricing["output"]
  ```
- **Missing:** Cache token types:
  - `cache_creation_input_tokens` (25% premium vs regular input)
  - `cache_read_input_tokens` (90% discount vs regular input)
- **Impact:** Cost reporting is 10–20× WRONG on cache hits
  - **Example:** Cache hit with 2000 cached tokens (Haiku)
    - Real cost: 2000 × $0.08 / 1M = **$0.00016**
    - Reported cost: 2000 × $0.80 / 1M = **$0.0016** (10× overestimate!)
- **Day 4 baseline issue:** When you measured cache effectiveness (Experiment 5), cache hits were over-reported
- **Day 5 action:** Update estimate_cost() to handle cache token types with correct pricing

#### 🟠 Issue 2: cached param recorded but not used in cost
- **Location:** Line 94
- **Current:** `cached: bool` parameter exists, stored in log_entry (line 130), but never applied to cost
- **Problem:** You pass `cached=True` to log_call(), but cost still uses regular input token pricing
- **Better:** Pass actual cache token counts instead of boolean:
  ```python
  cache_creation_tokens: int = 0,
  cache_read_tokens: int = 0,
  ```
  Then apply correct pricing in estimate_cost()
- **Day 5 action:** Refactor to pass token counts, not boolean

#### 🟠 Issue 3: Pricing hardcoded, incomplete
- **Location:** Lines 26–35
- **Current:** Only Haiku and Sonnet. Missing:
  - Opus ($15 input, $75 output)
  - Cache creation tokens pricing (25% premium)
  - Cache read tokens pricing (90% discount)
- **Why bad:**
  - Anthropic changes pricing quarterly → edit code every time
  - No way to A/B test pricing changes
  - Duplication: also in learning_lab/phase_4/04_cost_tracking.py
- **Better:** Load from config:
  ```python
  PRICING = load_config("pricing.yaml")  # Updated without code change
  ```
- **Day 5 action:** At minimum, add Opus. Consider moving to config file.

#### 🟠 Issue 4: Silently returns 0.0 for unknown model
- **Location:** Line 56
- **Current:**
  ```python
  if model not in AICallLogger.PRICING:
      logger.warning(f"Unknown model for pricing: {model}")
      return 0.0
  ```
- **Risk:** Typo like `"claude-sonnet-4-20250515"` (wrong date) returns $0.00, hides the mistake
- **Impact:** Cost dashboard shows zero cost for unknown models, making it impossible to debug
- **Better:** Raise exception instead of silent return
  ```python
  if model not in AICallLogger.PRICING:
      raise ValueError(f"Unknown model for pricing: {model}")
  ```
- **Day 5 action:** Change to raise exception (fail fast, easier to debug)

#### 🟡 Issue 5: No database persistence
- **Location:** Line 143
- **Current:** `log_call()` returns dict, but doesn't save to database
- **Problem:** Caller must manually persist to `ai_call_logs` table—easy to forget, inconsistent
- **Better:** Move DB write into the function:
  ```python
  db_entry = AICallLog(**log_entry)
  db.session.add(db_entry)
  db.session.commit()
  return db_entry.id
  ```
- **Day 5 action:** Move DB persistence into logger (single source of truth)

---

## Summary Table: Issues by Severity

| Severity | File | Issue | Day 5 Action |
|----------|------|-------|--------------|
| 🔴 CRITICAL | logger.py | estimate_cost() ignores cache pricing | Add cache_creation_tokens, cache_read_tokens to pricing calc |
| 🔴 CRITICAL | router.py | ANALYZE_FOOD routed to Haiku (should be Sonnet) | Change primary_model to Sonnet (1 line) |
| 🚨 BLOCKER | rate_limiter.py | check_limit() is a stub (always returns True) | Implement with Redis or database counter |
| 🟠 HIGH | logger.py | Pricing incomplete (missing Opus, cache pricing) | Add Opus pricing, cache token pricing |
| 🟠 HIGH | rate_limiter.py | RateLimitExceeded has no metadata | Add retry_after, limit, current_count fields |
| 🟡 MEDIUM | rate_limiter.py | logger imported but never used | Add logging calls for observability |
| 🟡 MEDIUM | rate_limiter.py | task_type should be TaskType enum, not str | Import enum, update signature |
| 🟡 MEDIUM | logger.py | Silent 0.0 return on unknown model | Raise exception instead (fail fast) |
| 🟡 MEDIUM | logger.py | No database persistence in logger | Move DB write into log_call() |
| 🟡 MEDIUM | router.py | fallback_model declared but never used | Document or implement fallback logic |

---

## Recommended Day 5 Priority

### Tier 1 (Must Fix)
1. **logger.py:** Add cache token pricing to estimate_cost() — cost tracking is broken without this
2. **router.py:** Change ANALYZE_FOOD to Sonnet — this is what Day 1 learning taught

### Tier 2 (Should Fix)
3. **logger.py:** Add Opus pricing — can't log Opus calls accurately without this
4. **logger.py:** Change 0.0 return to exception — fail fast, easier debugging

### Tier 3 (Nice to Have)
5. **rate_limiter.py:** Implement check_limit() with Redis — requires Redis setup
6. **rate_limiter.py:** Add metadata to RateLimitExceeded — improve error messaging
7. **rate_limiter.py:** Update task_type to enum — consistency

---

## Key Insights

1. **Cost tracking is the linchpin:** Everything else builds on accurate cost reporting. The logger's cache pricing bug breaks Phase 4's entire optimization story.

2. **Model tiering was correct:** Day 1 decision framework identified the ANALYZE_FOOD→Haiku bug. Day 5 implements the fix.

3. **Rate limiting is incomplete:** The stub with Redis comments suggests this was "build later" work. Day 5 must either implement it or document why it's disabled.

4. **Pricing is a living document:** Hardcoding it causes maintenance churn. Moving to config pays off immediately.

---

## Q&A — Test Your Understanding

**Q1:** Why is cost tracking broken when cache_read_tokens aren't counted in estimate_cost()?

**A:** Because cache reads cost 90% LESS than regular input tokens. When you ignore cache_read_tokens, you report the cost as if they were regular input tokens, over-reporting by 10–20×. Example: 2000 cached tokens at Haiku costs $0.00016 real (cache_read discount) but you report $0.0016 (regular input pricing). This breaks your cost forecasts and makes caching look less valuable than it actually is.

**Q2:** What would happen if you called check_limit() in production today and a user hit the rate limit?

**A:** Nothing. check_limit() always returns True, so no limit is enforced. The user would make unlimited API calls, potentially costing you $1000s before you noticed the spike.

**Q3:** Why is the "fallback_model" field in router.py bad design if it's never used?

**A:** Dead code confuses future developers. They see fallback_model and think it's implemented, so they assume API calls will retry on failure. Then when a failure happens and no retry occurs, they waste hours debugging. Better to delete the field or implement the fallback logic.

**Q4:** If you wanted to move pricing out of hardcoded dict to a config file, what would change in estimate_cost()?

**A:** The function itself wouldn't change—it would still look up pricing[model] and calculate the same way. Only the source of PRICING would change from `PRICING = {...}` (hardcoded) to `PRICING = load_yaml("pricing.yaml")` (loaded from file). The function's logic is independent of where pricing comes from.

**Q5:** Why does extract_token_usage() use hasattr() instead of direct attribute access?

**A:** Defensive programming. Some API responses might be missing usage fields or might have failures. Using hasattr() prevents crashes and returns sensible defaults (0, 0) instead of raising AttributeError. This is good practice for external API handling where you can't control the response shape.

---

## Next Steps (After Day 5 Fixes)

After implementing Day 5 changes:
1. Re-run 04_cost_tracking.py to verify cache pricing is now accurate
2. Verify ANALYZE_FOOD calls use Sonnet (check response.model in logs)
3. Create cost dashboard script showing before/after cost difference
4. Measure cache hit rate in production (should be 40%+ on system prompts)
5. Monitor ai_call_logs table for any unknown models (should be zero)
