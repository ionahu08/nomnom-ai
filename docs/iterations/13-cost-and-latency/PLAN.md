# Iteration 13: Cost & Latency Optimization

**Dates:** June 10, 2026 (Phase 4 Day 5 production integration)

**Goal:** Fix cost tracking and model routing to optimize NomNom's API spending while maintaining quality.

---

## What's Built (Prerequisites)

- ✅ Phase 3 complete: RAG pipeline + semantic cache + citations working
- ✅ Learning phase 4 complete: Prompt caching, model tiering, streaming, cost tracking concepts learned
- ✅ Code review completed: router.py, rate_limiter.py, logger.py analyzed
- ✅ Baseline measurement: 20 representative requests measured (BEFORE snapshot)

---

## What We're Building

### Feature 1: Fix Model Tiering (router.py)
- **Issue:** ANALYZE_FOOD routed to Haiku (wrong, needs multimodal vision accuracy)
- **Fix:** Route ANALYZE_FOOD to Sonnet instead
- **Impact:** Cost increases per request, but quality improves (fewer wrong calorie estimates)

### Feature 2: Fix Cost Tracking (logger.py)
- **Issue:** estimate_cost() ignores cache_read_tokens, over-reports cost by 10-20× on cache hits
- **Fix:** Add cache token types to cost calculation with correct pricing
- **Impact:** Cost dashboard now shows accurate numbers, cache savings visible

### Feature 3: Add Missing Model Pricing (logger.py)
- **Issue:** Opus pricing missing from PRICING dict; can't log Opus calls
- **Fix:** Add Opus pricing ($15 input, $75 output per 1M tokens)
- **Impact:** Enables future use of Opus for high-stakes tasks

---

## Success Criteria

- [ ] router.py: ANALYZE_FOOD uses Sonnet (claude-sonnet-4-20250514)
- [ ] logger.py: estimate_cost() accepts cache_creation_tokens and cache_read_tokens
- [ ] logger.py: Cost calculation applies correct cache pricing (25% premium, 90% discount)
- [ ] logger.py: Opus pricing added to PRICING dict
- [ ] logger.py: Silent 0.0 return changed to raise exception on unknown model
- [ ] Baseline re-measurement: image_recognition now costs ~5× more (Sonnet)
- [ ] Baseline re-measurement: Cache pricing fixes enable accurate cost reporting
- [ ] All tests pass
- [ ] No regressions in existing functionality

---

## Resume Skills (What This Iteration Teaches)

| Skill | What You'll Do |
|-------|----------------|
| **Cost Engineering** | Apply tiering decisions from Day 1 into production code |
| **Debugging Data** | Track down why cost reports were inaccurate (cache pricing bug) |
| **Before/After Analysis** | Measure impact of changes using baseline script |
| **Production Workflow** | Fix real bugs in backend code, test changes, document |

---

## Files to Change

| File | Change | Severity |
|------|--------|----------|
| `NomNom-Backend/src/llm/router.py` | Line 51: Haiku → Sonnet for ANALYZE_FOOD | 🔴 CRITICAL |
| `NomNom-Backend/src/llm/logger.py` | Lines 38-63: Add cache token pricing | 🔴 CRITICAL |
| `NomNom-Backend/src/llm/logger.py` | Lines 26-35: Add Opus pricing | 🟠 HIGH |
| `NomNom-Backend/src/llm/logger.py` | Line 56: Raise exception instead of return 0.0 | 🟡 MEDIUM |

---

## Testing Plan

1. **Unit tests:** Verify estimate_cost() with cache tokens
2. **Manual test:** Re-run 06_baseline_measurement.py
   - Before: Average cost $0.001469/request, image_recognition $0.000810
   - After: Average cost higher (Sonnet), cache hits show correct pricing
3. **Integration test:** Verify existing tests still pass
4. **Regression test:** No changes to non-Sonnet model routing

---

## Out of Scope (Phase 5+)

- ❌ Implement rate_limiter.py check_limit() (needs Redis)
- ❌ Implement prompt caching in client.py (separate feature)
- ❌ Add monitoring dashboard (separate feature)
- ❌ Performance optimization beyond model tiering

---

## Documentation Updates

After this iteration:
- [ ] Create SUMMARY.md with before/after numbers
- [ ] Document cache pricing formula in logger.py
- [ ] Update router.py comments with tiering rationale
- [ ] Add BUGLOG.md documenting issues found
