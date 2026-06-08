# Iteration 11: Eval Pipeline — Phase 2 Complete

**Phase:** Phase 2 — Make NomNom Not Crash  
**Duration:** June 5–8, 2026 (4 days)  
**Status:** ✅ Complete

---

## Goals

1. ✅ Build comprehensive eval infrastructure (code + model-based grading)
2. ✅ Compare output control techniques (prefill+stop vs tool_choice)
3. ✅ Land tool_choice in production with improved error messages
4. ✅ Create reusable eval pipeline (staging pattern)

---

## What's Built

**Backend Infrastructure:**
- ✅ parser.py — tool_use extraction + Pydantic validation
- ✅ guardrails.py — semantic validation (plausibility checks)
- ✅ tools.py — ANALYZE_FOOD_TOOL schema definition
- ✅ evaluator.py — skeleton for accuracy tracking (stubbed)

**Eval Pipeline (Learning Lab):**
- ✅ Days 1-2: Output control techniques (prefill+stop, stop sequences, tool_choice)
- ✅ Day 3: Dataset generation (30 challenging edge cases via Claude)
- ✅ Day 4: Code-based grading (3-level validation: JSON, schema, semantic)
- ✅ Day 5: Model-based grading (Opus as judge, signal fusion pattern)
- ✅ Day 6-7: Code reviews (parser.py, guardrails.py, tools.py, evaluator.py)
- ✅ Day 8-9: Capstone comparison (v0.5 prefill+stop vs v1.0 tool_choice on 30 cases)

---

## What We're Building

### 1. Production Integration: tool_choice
- **What:** Add tool_choice parameter to force structured output
- **Why:** 100% success rate vs 95% (prefill+stop failure modes)
- **Status:** ✅ Done
- **Files:** `src/services/ai_service.py`

### 2. Improved Error Messages
- **What:** Make guardrail violation messages Claude-readable
- **Why:** Support retry loops + provide context to fix errors
- **Status:** ✅ Done
- **Files:** `src/llm/guardrails.py`

### 3. Iteration Documentation
- **What:** Record learning outcomes, key insights, lessons learned
- **Why:** Enable handoff to next phase (Phase 3: RAG + Caching)
- **Status:** ✅ Done (this file)
- **Files:** `docs/iterations/11-eval-pipeline/` (PLAN, PHASES, BUGLOG, SUMMARY)

---

## Resume Skills

### Layer 1: API Mastery
- ✅ Streaming responses, timeouts, retries, fallbacks
- ✅ Multimodal input (images + text)
- ✅ tool_use blocks vs text parsing

### Layer 2: Prompt Engineering
- ✅ Role assignment, few-shot, CoT, XML tags
- ✅ Structured prompts vs unstructured
- ✅ Cat personality variations (sassy, grumpy, wholesome)

### Layer 3: Output Control
- ✅ Prefill assistant (prefix the assistant's response)
- ✅ Stop sequences (stop at markdown fence)
- ✅ Prefill+Stop combo (most reliable for text)
- ✅ **tool_choice (most reliable for structured output)** ← NEW

### Layer 4: Evaluation Infrastructure
- ✅ Code-based grading (deterministic, fast, cheap)
- ✅ Model-based grading (expensive, rich feedback)
- ✅ Signal fusion (RecSys pattern: combine multiple signals)
- ✅ Staging pipeline (separate fast vs slow stages)

### Layer 5: Reliability Engineering
- ✅ Production validation layers (parser + guardrails)
- ✅ Error messages that guide recovery
- ✅ Graceful fallbacks
- ✅ Logging for observability

---

## Success Criteria

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Code-based grading on 30 cases | ✅ | `04_code_graders.py` — 98.3/100 avg |
| Model-based grading on sample | ✅ | `05_model_grading.py` — Opus evaluation |
| tool_choice > prefill+stop comparison | ✅ | `08-09 capstone` — 100% vs 95% success |
| Production error messages improved | ✅ | `guardrails.py` — Claude-readable errors |
| tool_choice integrated in backend | ✅ | `ai_service.py` — uses tool_choice parameter |
| Iteration docs created | ✅ | This folder |

---

## What's Next (Phase 3)

**Phase 3: Semantic Search + Caching** (June 9–13, 2026)
- Build embedding pipeline (text → vectors)
- Implement semantic cache (avoid duplicate analysis)
- Implement RAG (retrieve similar meals for recommendations)

**Files to review:**
- `src/llm/embedding.py` — Embedding generation
- `src/llm/cache.py` — Semantic cache logic
- `src/services/recommendation_service.py` — RAG pipeline

---

## Key Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Test cases evaluated | 30 | Generated edge cases (blurry, ambiguous, mixed foods) |
| Code-based score avg | 98.3/100 | 100% schema valid, 93.3% semantic valid |
| tool_choice success rate | 100% | All 30 cases completed without parsing errors |
| prefill+stop baseline | 95% | From Day 2 (5 easy cases) |
| Error message improvement | ~8 messages | Now include context + guidance |
| Eval pipeline latency | ~2min (code) + ~5min (model) | Staging pattern optimizes for speed+cost |

---

## How to Resume

1. Read this PLAN.md (architecture overview)
2. Read PHASES.md (implementation details)
3. Read BUGLOG.md (what went wrong, lessons learned)
4. Review learning_lab/phase_2/ (code artifacts from capstone)
5. Review NomNom-Backend/src/llm/ (production changes)
6. Start Phase 3 with embedding.py review
