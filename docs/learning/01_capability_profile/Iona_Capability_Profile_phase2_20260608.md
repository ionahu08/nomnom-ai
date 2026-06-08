# Iona's LLM Harnessing Capability Profile — Phase 2 Snapshot

**Date:** June 8, 2026 (End of Phase 2)

> This is a historical snapshot of capability progression. See `Iona_Capability_Profile.md` for the forward-looking living profile.

---

## Phase 2 Summary

**What was accomplished:**
- Days 1-2: Output control techniques (prefill, prefill+stop, tool_choice)
- Days 3-5: Eval pipeline (dataset generation, code grading, model-based grading, signal fusion)
- Days 6-7: Code reviews (parser.py, guardrails.py, tools.py, evaluator.py)
- Days 8-9: Capstone comparison (tool_choice vs prefill+stop on 30 edge cases)
- Day 10: Production refactor (tool_choice integration, error message improvements)

**Key metrics:**
- tool_choice success rate: 100% (30/30 edge cases)
- Code-based grading avg: 98.3/100
- Semantic validity: 93.3% (28/30 passed plausibility checks)
- Error messages improved: 8 guardrail messages made Claude-readable

**Duration:** June 5–8, 2026 (4 working days)

---

## Layer-by-Layer Capability at Phase 2 End

### Layer 0: API Mastery
- **Phase 1 → Phase 2:** 4/5 → **4/5** (Stable)
- **Target:** 4/5
- **Status:** MAINTAINED
- **Evidence:**
  - Familiar with tool_use blocks (extraction, parsing)
  - Understand tool_choice parameter (forces structured output)
  - Know multimodal input (image + text, base64 encoding)
  - API knowledge solid, ready for Phase 3 (embedding endpoints)

---

### Layer 1: Prompt Engineering
- **Phase 1 → Phase 2:** 3/5 → **3/5** (Deferred to Phase 3)
- **Target:** 4/5
- **Status:** STABLE, NOT FOCUS OF PHASE 2
- **Evidence:**
  - Understand prompt templating from Phase 1
  - Studied production prompts (analyze_food with cat_style variants)
  - Recognized that prompt optimization is iterative (measure → improve)
  - Deferred detailed prompt engineering to Phase 3+ (after eval pipeline built)

---

### Layer 2: Output Control ⭐ MAJOR PROGRESS
- **Phase 1 → Phase 2:** 1/5 → **4/5** ✅✅✅
- **Target:** 4/5
- **Status:** ON TARGET
- **Evidence:**
  - **Prefill + Stop (Day 1):** Built & tested, understand limitations (95% success rate on easy cases)
  - **tool_choice (Day 2 preview → Days 8-9 intensive):** Built & compared
    - 100% success rate (all 30 edge cases completed)
    - 100% schema validity (structure guaranteed by API)
    - 93.3% semantic validity (passed guardrails)
    - Key insight: tool_choice is production-grade
  - **Comparison:** tool_choice > prefill+stop for structured output
  - **Integration:** Added tool_choice to production ai_service.py
  - **Why it matters:** Structure at API level > application-level parsing

---

### Layer 3: Evaluation Infrastructure ⭐ MAJOR NEW CAPABILITY
- **Phase 1 → Phase 2:** 1/5 → **3/5** ✅✅
- **Target:** 4/5
- **Status:** FOUNDATION STRONG, READY FOR EXPANSION
- **Evidence:**
  - **Code-based grading (Day 4):** Built 3-level validator (JSON, schema, semantic)
    - Deterministic, fast (~1 sec per case), cheap
    - 98.3/100 avg on 30 test cases
    - Catches: missing fields, type mismatches, unrealistic values
  - **Model-based grading (Day 5):** Used Opus as judge
    - Expensive (~$0.10 per case)
    - Rich feedback (strengths, weaknesses, reasoning)
    - Graded quality dimension that code-based can't measure
  - **Signal fusion (Day 5):** Combined code + model scores
    - RecSys pattern: weight structure (40%) + quality (60%)
    - Learned multi-channel scoring for optimization
  - **Staging pipeline (Days 8-9):** Separated fast stage (code) from slow stage (model)
    - 08_capstone: Fast (2 min, cheap) for all cases
    - 09_capstone: Slow (5 min, expensive) for final report
    - Reusable artifacts (intermediate JSON consumed by next stage)
  - **Dataset generation (Day 3):** Used Claude to create 30 edge cases
    - Bulk generation more efficient than hand-writing
    - Covered: blurry photos, ambiguous foods, mixed dishes, unfamiliar items

---

### Layer 4: Reliability Engineering ⭐ MAJOR PROGRESS
- **Phase 1 → Phase 2:** 2/5 → **4/5** ✅✅✅
- **Target:** 5/5 (My differentiator)
- **Status:** STRONG PROGRESS, NEARLY AT TARGET
- **Evidence:**
  - **Production validation layers (Days 6-7 code review):**
    - parser.py: tool_use extraction + Pydantic validation
    - guardrails.py: Semantic validation (plausibility checks)
    - guardrails.py: Toxicity detection
    - Understanding: These layers protect database from bad LLM output
  - **Improved error messages (Day 10):**
    - Before: "Calories 500000 out of range [0, 5000]"
    - After: "Calories: 500000 kcal is unrealistic (typical: 50-2000). Re-estimate."
    - Impact: Errors guide Claude toward correction (supports retry loops)
    - 8 messages improved with context + guidance
  - **Graceful fallbacks:**
    - Reviewed fallback strategy in ai_service.py
    - Understand: Better to return "Unknown Food" than crash
  - **Comprehensive logging:**
    - Reviewed logging in parser, guardrails, ai_service
    - Understand: Observability is critical for production
  - **Data-driven approach:**
    - Built eval pipeline to measure accuracy
    - Recognize: evaluator.py is stub, next priority for Layer 4

---

### Layer 3b: Augmentation (Embeddings + Caching)
- **Phase 1 → Phase 2:** 1/5 → **1/5** (Not in Phase 2 scope)
- **Target:** 5/5
- **Status:** DEFERRED TO PHASE 3
- **Notes:** Intentionally deferred. Will implement embedding.py + cache.py in Phase 3 (June 9+)

---

### Layer 5: Agent Engineering
- **Phase 1 → Phase 2:** 1/5 → **1/5** (Not in Phase 2 scope)
- **Target:** 4/5
- **Status:** MAINTAINED, DEFERRED TO PHASE 5
- **Notes:** Foundational concepts understood, implementation deferred to Phase 5 (week 8-9)

---

### Layer 6: Multi-Agent Coordination
- **Phase 1 → Phase 2:** 0/5 → **0/5** (Not in scope)
- **Target:** 3/5
- **Status:** NOT STARTED
- **Notes:** Deferred to Phase 5 (week 8-9)

---

## Key Insights from Phase 2

### 1. tool_choice is production-grade
- 100% success on 30 diverse edge cases (vs 95% prefill+stop on 5 easy cases)
- Structure enforced at API level (not application code)
- Simpler implementation: no markdown parsing, no JSON recovery logic
- **Takeaway:** Use tool_choice for all structured output. Always.

### 2. Evaluation is a process, not a single test
- Code-based grading: Fast feedback (use always)
- Model-based grading: Deep feedback (use sparingly on samples)
- Staging pipeline pattern: Separate fast vs slow stages, reusable artifacts
- Signal fusion: Combine multiple signals for richer understanding
- **Takeaway:** Build measurement infrastructure early. Measure → iterate → improve.

### 3. Error messages are part of reliability engineering
- Generic errors: "out of range"
- Helpful errors: "unrealistic, typical range X–Y, re-estimate"
- Good errors support retry loops and guide user/model recovery
- **Takeaway:** Error messages are a product feature, not just logs.

### 4. Evaluation infrastructure enables data-driven optimization
- evaluator.py exists but is 90% stubbed (current: logging only)
- Missing: Database integration, per-model tracking, API endpoints
- Without it: Can't do "I use production data to optimize prompts"
- With it: Can say "Haiku 92% accurate on salads, 78% on Asian food → optimized prompt → 96%"
- **Takeaway:** evaluator.py is next priority (Phase 3 or Phase 3.5).

### 5. Staging pipeline pattern is widely applicable
- ML: raw data → preprocessing → training → evaluation
- Image processing: load → resize → filter → compress
- Data warehouses: raw layer → processed → curated
- NomNom eval: code grading → model grading + report
- **Takeaway:** Separate concerns enable reuse and cost optimization.

### 6. Dataset generation at scale is a skill
- Hand-writing 30 test cases: tedious, limited diversity
- Claude-generated dataset: Fast, diverse, edge cases included
- Using Claude to generate eval data teaches about prompt design
- **Takeaway:** Use Claude as tool for generating test data. Specify edge cases clearly.

### 7. Learning progresses as phases compound
- Phase 1: API + prompts (foundation)
- Phase 2: Output control + eval (measurement)
- Phase 3: Embeddings + cache (optimization)
- Phase 4: Reliability infrastructure (robustness)
- Phase 5: Agents (autonomy)
- **Takeaway:** Each phase builds on previous. Can't skip measurement (Phase 2) and jump to optimization (Phase 3).

---

## Readiness Assessment for Phase 3

| Skill | Ready? | Notes |
|-------|--------|-------|
| API fundamentals | ✅ Yes | Solid from Phase 1 + Phase 2 tool_use |
| Tool use patterns | ✅ Yes | Implemented tool_choice, understand extraction |
| Eval infrastructure | ✅ Yes | Built code + model grading, understand staging pipeline |
| Output validation | ✅ Yes | Reviewed parser.py, guardrails.py |
| Error handling | ✅ Yes | Improved error messages, understand fallbacks |
| Embeddings | ⏳ Ready to learn | Next focus in Phase 3 |
| Semantic cache | ⏳ Ready to learn | Next focus in Phase 3 |
| RAG patterns | ⏳ Ready to learn | Next focus in Phase 3 |

---

## Summary: Layer Progression

```
Layer 0 (API):           1/5 ─→ 4/5 ─→ 4/5    [STABLE]
Layer 1 (Prompts):       1/5 ─→ 3/5 ─→ 3/5    [DEFERRED TO PHASE 3+]
Layer 2 (Output):        0/5 ─→ 1/5 ─→ 4/5    [✅ MAJOR PROGRESS]
Layer 3 (Eval):          1/5 ─→ 1/5 ─→ 3/5    [✅ MAJOR NEW CAPABILITY]
Layer 4 (Reliability):   1/5 ─→ 2/5 ─→ 4/5    [✅ MAJOR PROGRESS]
Layer 5 (Agents):        0/5 ─→ 1/5 ─→ 1/5    [DEFERRED]
Layer 6 (Multi-Agent):   0/5 ─→ 0/5 ─→ 0/5    [NOT STARTED]
```

**Strongest areas:** API (4/5), Output Control (4/5), Reliability (4/5)  
**Growth areas ready for Phase 3:** Augmentation (embeddings, caching, RAG)  
**Deferred to later phases:** Agents (5), Multi-Agent (6)

---

## Next Steps (Phase 3 & Beyond)

### Immediate (Phase 3: Semantic Search + Caching)
1. Review embedding.py — text → vectors
2. Review cache.py — semantic cache to avoid duplicate analysis
3. Review recommendation_service.py — RAG pipeline for meal suggestions
4. Implement semantic cache integration with food log analysis

### Short-term (Phase 3.5: evaluator.py Production Implementation)
1. Add `is_user_corrected` flag to food_logs schema
2. Create corrections table for historical analysis
3. Implement database queries in evaluator.py
4. Expose metrics via API endpoint (/api/v1/accuracy)

### Medium-term (Phase 4: Reliability Engineering Patterns)
1. Implement retry loops that use improved error messages
2. Monitor tool_choice success rate in production
3. Build evaluation dashboard (accuracy by model, food type, user)
4. Implement per-model and per-food-type optimization

### Long-term (Phase 5-6: Agents + Multi-Agent)
1. Hand-code agent loops for complex workflows
2. Multi-agent coordination patterns
3. MCP server exposure for extensibility

---

**Phase 2 complete. Ready for Phase 3: Semantic Search + Caching**
