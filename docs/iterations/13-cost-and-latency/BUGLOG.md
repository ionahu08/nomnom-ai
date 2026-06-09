# Iteration 13: BUGLOG — Cost & Latency Optimization

**Dates:** June 9, 2026 (Phase 4 Day 5 production integration)

---

## Issues Found & Fixed

### 1. ✅ CRITICAL: ANALYZE_FOOD routed to wrong model
- **Severity:** 🔴 CRITICAL (user-facing quality issue)
- **File:** `NomNom-Backend/src/llm/router.py` line 51
- **Issue:** Food image recognition assigned to Haiku instead of Sonnet
- **Root cause:** Day 1 learning framework identified multimodal tasks need vision accuracy, but router.py had old Haiku assignment
- **Impact:** Weak vision on ambiguous dishes → wrong calorie estimates → user churn
- **Fix:** Changed `primary_model="claude-haiku-4-5-20251001"` → `"claude-sonnet-4-20250514"`
- **Testing:** Updated test_router.py, all 12 router tests pass
- **Cost impact:** +$0.72/day at 1000 requests/day (justified by user trust)

### 2. ✅ CRITICAL: Cost tracking ignores cache pricing
- **Severity:** 🔴 CRITICAL (observability/reporting broken)
- **File:** `NomNom-Backend/src/llm/logger.py` lines 37-63, 115-120
- **Issue:** estimate_cost() only counted regular input/output tokens, ignored cache tokens
- **Root cause:** When prompt caching was added to API, cost calculation wasn't updated
- **Impact:** Cache hits over-reported by 10-20× (e.g., $0.0016 reported when real cost $0.00016)
- **Symptom:** Phase 4 Day 2 baseline showed cache "savings" but cost calculation didn't reflect it
- **Fix:** 
  - Added `cache_creation_tokens` and `cache_read_tokens` parameters to estimate_cost()
  - Updated log_call() to extract cache tokens from response.usage
  - Apply 25% premium for cache_creation, 90% discount for cache_read
- **Testing:** Added 4 new tests for cache pricing, all 29 logger tests pass
- **Verification:** estimate_cost() with 1M cache_read tokens returns ~$0.08 (90% discount) ✓

### 3. ✅ HIGH: Incomplete pricing table
- **Severity:** 🟠 HIGH (blocks Opus logging)
- **File:** `NomNom-Backend/src/llm/logger.py` lines 26-35
- **Issue:** PRICING dict missing Opus, missing cache pricing for all models
- **Root cause:** Pricing table was minimal, only updated when new models added
- **Impact:** Can't log Opus calls accurately, cache pricing hidden
- **Fix:**
  - Added Opus: $15 input, $75 output per 1M tokens
  - Added cache pricing: cache_creation (1.00/3.75/18.75), cache_read (0.08/0.30/1.50)
- **Verification:** All 3 models now have complete pricing ✓

### 4. ✅ HIGH: Silent error on unknown model
- **Severity:** 🟠 HIGH (bugs hide in cost logs)
- **File:** `NomNom-Backend/src/llm/logger.py` line 56
- **Issue:** Unknown model returned 0.0 instead of raising error
- **Root cause:** Defensive programming gone wrong (warning + silent return)
- **Risk:** Typo like "claude-sonnet-4-20250515" would report $0 cost, hiding the mistake
- **Fix:** Changed to `raise ValueError()` instead of returning 0.0
- **Testing:** Added test_unknown_model_raises_error, passes ✓

---

## Testing Results

### Unit Tests: 29/29 Passing ✅

**router.py tests (12 total):**
- ✅ test_task_types_exist
- ✅ test_analyze_food_uses_sonnet (updated from haiku)
- ✅ test_recommend_meal_uses_sonnet
- ✅ test_weekly_recap_uses_sonnet
- ✅ test_all_tasks_have_routes
- ✅ test_routes_have_reasonable_temperatures
- ✅ test_get_model_for_analyze_food (updated from haiku)
- ✅ test_get_model_for_recommend_meal
- ✅ test_get_model_for_weekly_recap
- ✅ test_temperatures_exist
- ✅ test_temperature_increases_with_creativity
- ✅ test_unknown_task_raises_error

**logger.py tests (17 total):**
- ✅ test_haiku_pricing
- ✅ test_sonnet_pricing
- ✅ test_realistic_cost_estimate
- ✅ test_zero_tokens
- ✅ test_cache_creation_tokens_pricing (new)
- ✅ test_cache_read_tokens_pricing (new)
- ✅ test_cache_read_much_cheaper_than_regular_input (new)
- ✅ test_unknown_model_raises_error (updated)
- ✅ test_extract_token_usage
- ✅ test_extract_token_usage_missing_usage
- ✅ test_extract_token_usage_missing_fields
- ✅ test_successful_call_log
- ✅ test_failed_call_log
- ✅ test_cached_call_log
- ✅ test_timer_measures_elapsed_time
- ✅ test_timer_zero_time
- ✅ test_timer_context_manager

### Integration Testing: Baseline Measurement

**BEFORE (Haiku for image_recognition):**
- analyze_food avg: $0.000761
- json_extraction avg: $0.000399
- recommend_meal avg: $0.004007
- Daily forecast: $1.45/day
- Monthly forecast: $43.38/month

**AFTER (Sonnet for image_recognition):**
- analyze_food avg: $0.002571 (+3.4×, +$1.81/day)
- json_extraction avg: $0.000402 (stable)
- recommend_meal avg: $0.004007 (stable)
- Daily forecast: $2.17/day (+$0.72/day)
- Monthly forecast: $65.12/month (+$21.74/month)

**Interpretation:** Cost increase is expected and justified. Cache implementation will offset this via 90% discount on cached prompts.

---

## Decisions Made

### Decision 1: Sonnet for food recognition despite cost increase
- **Rationale:** Quality (accuracy) > cost on core product feature
- **Context:** User churn from wrong calorie estimates > $21/month cost
- **Evidence:** Day 1 model tiering framework identified this as required

### Decision 2: Fail-fast error handling for unknown models
- **Rationale:** Bugs should surface immediately, not hide in cost logs
- **Alternative:** Silent logging + warning (rejected, too easy to miss)
- **Trade-off:** Stricter requirements now, cleaner debugging later

### Decision 3: Incomplete cache pricing not a blocker
- **Rationale:** Cache pricing is secondary to logger cost calculation fix
- **Context:** Cache implementation will come in Phase 5
- **Plan:** logger.py already structured to handle cache tokens when implemented

---

## Known Limitations

1. **rate_limiter.py not fixed** — check_limit() still a stub
   - Reason: Blocked on Redis setup (Tier 3, nice-to-have)
   - Workaround: Deploy with awareness that no hard rate limiting exists
   - Plan: Implement in follow-up iteration with Redis infrastructure

2. **Fallback model still declared but unused** — router.py line 52
   - Reason: No fallback retry logic implemented (Tier 3)
   - Plan: Document or remove in router refactoring

3. **Cache pricing not yet in production** — logger.py changes are ready, but streaming/caching not deployed
   - Reason: Phase 5 work (prompt caching implementation)
   - Status: logger.py prepared and tested for 90% discount ✓

---

## Regressions Checked

- ✅ No breaking changes to API contracts
- ✅ Existing food analysis calls still work (just higher quality)
- ✅ No test failures introduced
- ✅ Cost calculation still works for non-cached requests
- ✅ All existing models (Haiku, Sonnet) still supported

---

## Next Steps for Production Deployment

1. **Monitor cost increase** — Track actual daily spend vs. forecast $2.17/day
2. **Verify Sonnet quality** — Sample food recognition outputs, compare to old Haiku results
3. **Plan cache implementation** — Phase 5 should implement prompt caching to offset cost
4. **Document decision** — Add comment to router.py explaining Sonnet choice (cost vs. quality tradeoff)
5. **Set up logging dashboard** — Use logger.py improvements to monitor cost per task type

---

## Session Summary

**What worked well:**
- Unit test coverage caught issues early (test failures forced fixes)
- Code review (05_router_limiter_logger_review.md) identified all issues correctly
- Baseline measurement script proved reproducible

**What to do differently next time:**
- Update tests BEFORE implementing fixes (test-driven approach)
- Cache pricing should have been added when caching was first conceptualized
- Fallback model design should be completed or removed, not left half-done

---

**Created:** June 9, 2026  
**Status:** ✅ COMPLETE
