# Phase 4 Day 5: Production Changes — Quick Reference

**Goal:** Apply the fixes identified in the code review (05_router_limiter_logger_review.md) to production files.

**Timeline:**
1. Make changes to router.py and logger.py
2. Run tests to verify no regressions
3. Re-run 06_baseline_measurement.py to capture AFTER metrics
4. Compare BEFORE and AFTER to show impact

**Note:** See docs/iterations/13-cost-and-latency/PHASES.md for detailed implementation guide.

---

## CRITICAL FIX 1: router.py — Route ANALYZE_FOOD to Sonnet

**File:** `NomNom-Backend/src/llm/router.py`

**Location:** Line 51 (inside TASK_ROUTES dict)

**Why:** Food analysis requires multimodal vision. Haiku is too weak for ambiguous dishes. Weak vision → wrong calories → user churn.

**Change:**

```diff
  TaskType.ANALYZE_FOOD: ModelRoute(
-     primary_model="claude-haiku-4-5-20251001",
+     primary_model="claude-sonnet-4-20250514",
      fallback_model="claude-sonnet-4-20250514",
      max_tokens=500,
      temperature=0.7,
  ),
```

**Impact:**
- Cost per image_recognition request: $0.000810 → $0.003240 (~4× more)
- Quality: Better at analyzing complex/ambiguous dishes
- Calorie accuracy: Fewer wrong estimates = higher user trust

**Verification:**
```bash
python -c "from src.llm.router import get_model_for_task, TaskType; print(get_model_for_task(TaskType.ANALYZE_FOOD))"
# Should print: claude-sonnet-4-20250514
```

---

## CRITICAL FIX 2: logger.py — Add Cache Token Pricing

**File:** `NomNom-Backend/src/llm/logger.py`

**Location:** Lines 38-63 (estimate_cost method) + Line 118 (log_call method)

**Why:** Cache hits cost 90% less than regular input tokens. Current code ignores cache tokens, over-reporting cost by 10-20× on cache hits.

### Step 2a: Update estimate_cost() signature and logic

**Current (lines 37-63):**
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

**Replace with:**
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
    
    # Regular input/output tokens
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    
    # Cache tokens use separate pricing (25% premium to create, 90% discount to read)
    cache_creation_cost = (cache_creation_tokens / 1_000_000) * pricing.get("cache_creation", pricing["input"] * 1.25)
    cache_read_cost = (cache_read_tokens / 1_000_000) * pricing.get("cache_read", pricing["input"] * 0.10)
    
    total_cost = input_cost + output_cost + cache_creation_cost + cache_read_cost

    return round(total_cost, 6)
```

### Step 2b: Update the call to estimate_cost() in log_call()

**Current (line 118):**
```python
estimated_cost = AICallLogger.estimate_cost(model, input_tokens, output_tokens)
```

**Replace with:**
```python
# Extract cache tokens from response
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

**Impact:**
- Cost tracking now accurate on cache hits
- Cache hit shows ~90% cost reduction (correct)
- Budget forecasts now reliable

**Example:**
- Request with 2000 cached tokens (Haiku)
- Old cost reporting: $0.0016 (treating as regular input)
- New cost reporting: $0.00016 (correct cache_read pricing)
- Error fixed: 10× overestimate eliminated

---

## HIGH PRIORITY FIX 3: logger.py — Add Opus Pricing

**File:** `NomNom-Backend/src/llm/logger.py`

**Location:** Lines 26-35 (PRICING dict)

**Why:** Opus pricing missing. Can't log Opus calls. Cache pricing should be explicit in dict.

**Current:**
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

**Add:**
```python
PRICING = {
    "claude-haiku-4-5-20251001": {
        "input": 0.80,
        "output": 4.00,
        "cache_creation": 1.00,      # 25% premium
        "cache_read": 0.08,          # 90% discount
    },
    "claude-sonnet-4-20250514": {
        "input": 3.00,
        "output": 15.00,
        "cache_creation": 3.75,      # 25% premium
        "cache_read": 0.30,          # 90% discount
    },
    "claude-opus-4-7": {
        "input": 15.00,
        "output": 75.00,
        "cache_creation": 18.75,     # 25% premium
        "cache_read": 1.50,          # 90% discount
    },
}
```

**Impact:**
- Opus calls can now be logged with correct pricing
- Cache pricing explicit in dict (better maintainability)

---

## MEDIUM PRIORITY FIX 4: logger.py — Better Error Handling

**File:** `NomNom-Backend/src/llm/logger.py`

**Location:** Line 54-56 (inside estimate_cost method)

**Why:** Silent 0.0 return hides bugs (typos in model names). Better to fail fast.

**Current:**
```python
if model not in AICallLogger.PRICING:
    logger.warning(f"Unknown model for pricing: {model}")
    return 0.0
```

**Replace with:**
```python
if model not in AICallLogger.PRICING:
    raise ValueError(f"Unknown model for pricing: {model}. Add to PRICING dict.")
```

**Impact:**
- Catches typos immediately (e.g., "claude-sonnet-4-20250515" typo won't silently return $0)
- Stack trace shows exactly where the problem is
- Prevents silent cost tracking errors

---

## Testing Checklist

After making changes:

- [ ] **Unit tests pass:**
  ```bash
  pytest tests/unit/llm/test_router.py -v
  pytest tests/unit/llm/test_logger.py -v
  ```

- [ ] **Integration tests pass:**
  ```bash
  pytest tests/integration/ -v
  ```

- [ ] **Manual verification:**
  ```bash
  # Test router fix
  python -c "from src.llm.router import get_model_for_task, TaskType; print(get_model_for_task(TaskType.ANALYZE_FOOD))"
  # Should print: claude-sonnet-4-20250514
  
  # Test logger cost calculation
  python -c "from src.llm.logger import AICallLogger; print(AICallLogger.estimate_cost('claude-haiku-4-5-20251001', 1000, 100, cache_read_tokens=2000))"
  # Should print small cost (~$0.00016 for cache_read)
  ```

- [ ] **Re-run baseline measurement:**
  ```bash
  cd learning_lab/phase_4
  python 06_baseline_measurement.py > after_baseline.txt
  ```
  Compare to earlier baseline output.

---

## Expected Before/After Changes

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| image_recognition avg cost | $0.000810 | ~$0.003240 | +4× (Haiku→Sonnet) |
| json_extraction avg cost | $0.000408 | $0.000408 | No change (stays Haiku) |
| rag_answer avg cost | $0.004007 | $0.004007 | No change (stays Sonnet) |
| **Daily forecast (1000 req)** | **$1.47** | **~$3.50-4.50** | Depends on request mix |
| Cache hit cost accuracy | 10-20× wrong | Accurate | Fixed (cache pricing) |

---

## Summary

**Quick win fixes:**
1. ✅ router.py: 1 line change (Haiku → Sonnet for ANALYZE_FOOD)
2. ✅ logger.py: Add cache token parameters to estimate_cost()
3. ✅ logger.py: Add Opus pricing
4. ✅ logger.py: Better error handling

**Total impact:**
- Image recognition quality improves (better vision)
- Cost tracking becomes accurate (cache pricing fixed)
- System ready for future Opus integration
- Faster debugging (exceptions instead of silent failures)

**Next steps:**
1. Apply changes to production files
2. Run tests
3. Re-run 06_baseline_measurement.py
4. Document before/after in SUMMARY.md
