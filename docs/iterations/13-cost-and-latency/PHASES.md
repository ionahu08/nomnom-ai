# Implementation Phases — Iteration 13

---

## Phase 1: Fix router.py (Model Tiering)

**File:** `NomNom-Backend/src/llm/router.py`

**Change:** Line 51 — Route ANALYZE_FOOD to Sonnet instead of Haiku

**Before:**
```python
TaskType.ANALYZE_FOOD: ModelRoute(
    primary_model="claude-haiku-4-5-20251001",
    fallback_model="claude-sonnet-4-20250514",
    max_tokens=500,
    temperature=0.7,
),
```

**After:**
```python
TaskType.ANALYZE_FOOD: ModelRoute(
    primary_model="claude-sonnet-4-20250514",
    fallback_model=None,  # Optional: remove unused fallback
    max_tokens=500,
    temperature=0.7,
),
```

**Rationale:**
- Food photo analysis requires multimodal vision + reasoning
- Haiku's vision is weaker on ambiguous/complex dishes
- Sonnet provides 4× better accuracy for the cost of ~4× more money
- Weak vision → wrong calorie estimates → user churn → worse business outcome
- $3.96/day extra (Sonnet vs Haiku) << lifetime value of keeping a user

**Testing:**
- Verify router still loads without error
- Check that get_model_for_task(TaskType.ANALYZE_FOOD) returns "claude-sonnet-4-20250514"
- Run existing tests: `pytest tests/unit/llm/test_router.py`

---

## Phase 2: Fix logger.py — Add Cache Token Pricing

**File:** `NomNom-Backend/src/llm/logger.py`

**Change:** Lines 38-63 — Update estimate_cost() to handle cache tokens

**Before:**
```python
@staticmethod
def estimate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """Estimate API cost for an LLM call."""
    if model not in AICallLogger.PRICING:
        logger.warning(f"Unknown model for pricing: {model}")
        return 0.0

    pricing = AICallLogger.PRICING[model]
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    total_cost = input_cost + output_cost

    return round(total_cost, 6)
```

**After:**
```python
@staticmethod
def estimate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_creation_tokens: int = 0,
    cache_read_tokens: int = 0,
) -> float:
    """Estimate API cost for an LLM call, including cache token pricing."""
    if model not in AICallLogger.PRICING:
        logger.warning(f"Unknown model for pricing: {model}")
        return 0.0

    pricing = AICallLogger.PRICING[model]
    
    # Regular tokens
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    
    # Cache tokens (if applicable)
    # cache_creation: 25% premium (higher cost to store)
    # cache_read: 90% discount (cheaper to reuse)
    cache_creation_cost = (cache_creation_tokens / 1_000_000) * pricing.get("cache_creation", pricing["input"] * 1.25)
    cache_read_cost = (cache_read_tokens / 1_000_000) * pricing.get("cache_read", pricing["input"] * 0.10)
    
    total_cost = input_cost + output_cost + cache_creation_cost + cache_read_cost

    return round(total_cost, 6)
```

**Also update the call in log_call() (line 118):**

**Before:**
```python
estimated_cost = AICallLogger.estimate_cost(model, input_tokens, output_tokens)
```

**After:**
```python
cache_creation = getattr(response.usage, "cache_creation_input_tokens", 0) if response else 0
cache_read = getattr(response.usage, "cache_read_input_tokens", 0) if response else 0

estimated_cost = AICallLogger.estimate_cost(
    model, 
    input_tokens, 
    output_tokens,
    cache_creation_tokens=cache_creation,
    cache_read_tokens=cache_read,
)
```

**Rationale:**
- Without cache pricing, cost tracking is 10-20× wrong on cache hits
- Example: 2000 cached tokens on Haiku
  - Real cost: $0.00016 (cache_read at 90% discount)
  - Reported cost: $0.0016 (regular input pricing)
  - Error: 10× overestimate!
- Accurate cost tracking is essential for optimization decisions

**Testing:**
- Unit test: `estimate_cost()` with cache tokens should be ~90% cheaper
- Manual test: Run 06_baseline_measurement.py, verify image_recognition costs don't show cache hits (expect 0%)
- Regression test: Non-cache calls should have same cost as before

---

## Phase 3: Add Opus Pricing (logger.py)

**File:** `NomNom-Backend/src/llm/logger.py`

**Change:** Lines 26-35 — Add Opus to PRICING dict

**Before:**
```python
PRICING = {
    "claude-haiku-4-5-20251001": {
        "input": 0.80,
        "output": 4.00,
    },
    "claude-sonnet-4-20250514": {
        "input": 3.00,
        "output": 15.00,
    },
}
```

**After:**
```python
PRICING = {
    "claude-haiku-4-5-20251001": {
        "input": 0.80,
        "output": 4.00,
        "cache_creation": 1.00,
        "cache_read": 0.08,
    },
    "claude-sonnet-4-20250514": {
        "input": 3.00,
        "output": 15.00,
        "cache_creation": 3.75,
        "cache_read": 0.30,
    },
    "claude-opus-4-7": {
        "input": 15.00,
        "output": 75.00,
        "cache_creation": 18.75,
        "cache_read": 1.50,
    },
}
```

**Rationale:**
- Opus pricing is missing; can't log Opus calls
- Cache pricing should be in PRICING dict for future use
- Make pricing centralized and maintainable

**Testing:**
- Verify estimate_cost() works for Opus models
- No change to existing Haiku/Sonnet costs

---

## Phase 4: Improve Error Handling (logger.py)

**File:** `NomNom-Backend/src/llm/logger.py`

**Change:** Line 56 — Raise exception instead of silent return

**Before:**
```python
if model not in AICallLogger.PRICING:
    logger.warning(f"Unknown model for pricing: {model}")
    return 0.0
```

**After:**
```python
if model not in AICallLogger.PRICING:
    raise ValueError(f"Unknown model for pricing: {model}. Add to PRICING dict.")
```

**Rationale:**
- Silent 0.0 hides bugs (typos in model names)
- Fail fast: errors should surface immediately, not hide in logs
- Easier to debug: exception traceback shows exactly where the problem is

**Testing:**
- Unit test: Verify exception raised for unknown model
- No impact on known models (Haiku, Sonnet, Opus)

---

## Integration Testing

After all changes:

1. **Run unit tests:**
   ```bash
   pytest tests/unit/llm/test_router.py
   pytest tests/unit/llm/test_logger.py
   ```

2. **Run integration tests:**
   ```bash
   pytest tests/integration/
   ```

3. **Manual baseline comparison:**
   ```bash
   python learning_lab/phase_4/06_baseline_measurement.py
   ```
   Compare output to baseline captured earlier.

4. **Verify no regressions:**
   - Existing AI service calls still work
   - Cost calculations for Haiku/Sonnet unchanged (except cache)
   - Rate limiting still compiles (even though check_limit() is stub)

---

## Rollback Plan

If something breaks:

1. **For router.py:** Git revert the 1-line change to restore Haiku
2. **For logger.py:** Restore estimate_cost() signature, remove cache parameters
3. **For PRICING:** Remove Opus entry
4. **Commit:** `git commit -m "revert(iteration-13): restore router and logger before changes"`

---

## Documentation After Completion

- [ ] Create BUGLOG.md (issues found)
- [ ] Create SUMMARY.md (before/after numbers, lessons learned)
- [ ] Update CLAUDE.md with Phase 4 completion status
- [ ] Create phase retrospective: docs/learning/03_phase_retrospectives/phase_4_retro.md
- [ ] Update capability profile snapshot
