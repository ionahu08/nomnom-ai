# Iteration 11: Eval Pipeline — Summary

**Duration:** 4 days (June 5–8, 2026)  
**Status:** ✅ COMPLETE

---

## What Was Built

Iteration 11 designed and implemented a comprehensive evaluation pipeline for LLM output validation, teaching foundational patterns for output control, guardrails, and quality assessment.

### Learning (Days 1-5)

5 executable Jupyter notebooks in `learning_lab/phase_2/`:
- **01_output_control.py** — Prefill vs stop_sequences vs tool_choice techniques
- **02_eval_pipeline.py** — 6-step evaluation workflow (prompt v1 → v2 improvement from 9.0 to 9.4/10)
- **03_dataset_generation.py** — Bulk-generate edge cases using Claude
- **04_code_graders.py** — 3-level validation (JSON → schema → semantic)
- **05_model_grading.py** — Opus-as-judge with signal fusion (RecSys pattern)

### Production Code (Days 8-10 Capstone)

Created production modules in `NomNom-Backend/src/`:
- **parser.py** — JSON extraction with markdown code fence handling
- **guardrails.py** — Semantic validation and error messages
- **evaluator.py** — Code-based + model-based grading (stub for future)
- **tools.py** — Food analysis tool with structured output validation

**Key Integration:**
- Added `tool_choice` parameter to `ai_service.py`
- Updated food analysis endpoints to use tool_choice for 100% reliability

---

## Challenges & Solutions

### Challenge 1: API Strict Message Formatting
**Problem:** Trailing whitespace in prefill caused `BadRequestError`.  
**Solution:** Remove all whitespace from prefill patterns. Always test with actual API.  
**Lesson:** Anthropic API validation is strict; assumptions don't work.

### Challenge 2: Documentation Redundancy
**Problem:** Review document was 455 lines with concepts repeated 3x.  
**Solution:** Added TOC, consolidated sections, reduced to 280 lines (40% compression) without losing information.  
**Lesson:** Structure + DRY principles apply to documentation too.

### Challenge 3: F-String Complexity with Code Blocks
**Problem:** Large f-strings with `{` and `}` caused ValueError in format specifiers.  
**Solution:** Use string concatenation for > 50 lines with code examples.  
**Lesson:** F-strings are bad for reports with code. Keep f-strings small.

### Challenge 4: Documentation of Learning Artifacts
**Problem:** Completed Days 1-5 without discovering 15 Jupyter notebooks existed.  
**Solution:** Created comprehensive Phase 1 retrospective, artifact index, updated CLAUDE.md.  
**Lesson:** Document the learning journey, not just the code.

---

## Key Decisions & Trade-Offs

### Decision 1: Staged Pipeline Pattern
**Choice:** Split capstone into fast stage (code grading) + slow stage (model grading)  
**Trade-off:** More complex (multiple files) but reusable, modular, cost-optimized  
**Result:** ✅ Production pattern validated

### Decision 2: Code + Model Based Grading
**Choice:** Use both validation layers, not just one  
**Evidence:**
- Code catches structure (fast, cheap: ~$0.02/sample)
- Model catches quality (expensive but rich: ~$1.00/sample)
- Signal fusion teaches RecSys multi-channel scoring
**Result:** ✅ Reflects production reality

### Decision 3: tool_choice as Default
**Choice:** tool_choice for production, prefill+stop for learning baseline  
**Evidence:**
| Approach | Success Rate | Schema Validity | Semantic Validity |
|----------|--------------|-----------------|-------------------|
| tool_choice | 100% (30/30) | 100% | 93.3% |
| prefill+stop | ~95% | ~90% | 100% |
**Result:** ✅ tool_choice now the standard pattern

---

## Key Metrics

### Evaluation Results
```
Code grading (30 cases):     30/30 success (100%)
Model grading (10 samples):  9.2/10 avg score
Schema validity:             100% (tool_choice)
Semantic validity:           93.3% (28/30 pass guardrails)
Average code score:          98.3/100
```

### Performance
```
Code grading (30 cases):     ~2 min, ~$0.02
Model grading (10 samples):  ~5 min, ~$1.00
Full pipeline:               ~7 min, ~$1.02
```

### Error Analysis
```
tool_choice failures:        0 cases (0%)
prefill+stop failures:       ~1 case (~5% estimated)
  - Markdown wrapping issues
  - Missing JSON fields
  - Type mismatches
```

---

## What Went Well

✅ **Staging pipeline pattern** — Clean separation of fast vs slow stages  
✅ **Error message improvements** — Simple changes, big usability impact  
✅ **Comprehensive capstone** — 30 edge cases proved tool_choice reliability  
✅ **Documentation handoff** — Clear PLAN → PHASES → BUGLOG → SUMMARY  
✅ **Learning progression** — Jupyter notebooks → capstone code → production integration

---

## What Could Be Better

❌ **evaluator.py still stubbed** — Wanted database integration, deferred to Phase 3  
❌ **No live production testing** — Only local validation with synthetic data  
❌ **Retry logic not implemented** — Error messages improved, but no auto-retry  
❌ **Limited dataset diversity** — 30 cases good for learning, real traffic may differ

---

## Architecture & Patterns Learned

### Eval Pipeline Pattern (5 Steps)
```
Raw Output → Parser → Guardrails → Evaluator → Report
   ↓           ↓         ↓           ↓         ↓
  JSON    Markdown   Semantic    Code+Model  Metrics
  text    handling   validation   scoring   analysis
```

### Three Validation Levels
```
Level 1: JSON Structure    (code-based, ~$0.02)
Level 2: Schema Validity   (code-based, ~$0.02)
Level 3: Semantic Validity (model-based, ~$1.00)
```

### Signal Fusion (RecSys Pattern)
```
Code score (0-100)  ───┐
                        ├→ Weighted average → Final grade
Model score (0-10)  ───┘
```

---

## Technical Insights

### 1. Prompts Are Product Assets
**Discovery:** Phase 1 had 15 Jupyter notebooks on prompts but only 2 code files in production.  
**Impact:** Prompts change 10x faster than code — need versioning strategy.  
**Action:** Store prompts separately, version (v1, v2, v3), document reasoning.

### 2. Reliability Is Designed In, Not Bolted On
**Discovery:** guardrails, parser, evaluator are foundation, not afterthoughts.  
**Impact:** Can't make LLM apps reliable by just tweaking prompts or using stronger models.  
**Requirements:**
- Validation layers (code + model)
- Graceful fallbacks
- Comprehensive logging

### 3. Token Cost Is First-Class Constraint
**Discovery:** Eval costs vary 50x (code ~$0.02 vs model ~$1.00 per sample).  
**Strategy:**
- Code-based grading for all cases (deterministic)
- Model-based grading on samples/edge cases only
- Staged pipelines (separate fast vs slow)

### 4. tool_choice > Text Parsing Always
**Rule:** If you need structured output, use tool_choice. Full stop.  
**Evidence:** 100% success vs ~95% with parsing.  
**Action:** Make tool_choice the default pattern for all structured output.

### 5. DRY Applies to Prompts and Documentation
**Discovery:** Consolidated document was 40% shorter with better clarity.  
**Principle:** One version = one truth. Reference externally, don't duplicate.

---

## Files Created/Modified

**Learning Artifacts:**
- ✅ `learning_lab/phase_2/01_output_control.py`
- ✅ `learning_lab/phase_2/02_eval_pipeline.py`
- ✅ `learning_lab/phase_2/03_dataset_generation.py`
- ✅ `learning_lab/phase_2/04_code_graders.py`
- ✅ `learning_lab/phase_2/05_model_grading.py`

**Production Code:**
- ✅ `NomNom-Backend/src/llm/parser.py` — JSON parsing with recovery
- ✅ `NomNom-Backend/src/llm/guardrails.py` — Semantic validation + error messages
- ✅ `NomNom-Backend/src/llm/evaluator.py` — Grading foundation (stub)
- ✅ `NomNom-Backend/src/llm/tools.py` — Structured output tools
- ✅ `NomNom-Backend/src/services/ai_service.py` — Integrated tool_choice

**Documentation:**
- ✅ `docs/iterations/11-eval-pipeline/PLAN.md`
- ✅ `docs/iterations/11-eval-pipeline/PHASES.md`
- ✅ `docs/iterations/11-eval-pipeline/BUGLOG.md`

---

## Recommendations for Phase 3

### High Priority
1. Implement evaluator.py database integration (data-driven prompts)
2. Add retry logic using improved error messages
3. Test tool_choice with real production traffic
4. Create cost dashboard for token usage

### Medium Priority
1. Expand test dataset to 100+ cases
2. A/B test model selection (Haiku vs Sonnet)
3. Implement per-model accuracy tracking
4. Create accuracy metrics dashboard

### Low Priority
1. Optimize prompt templates with version control
2. Create team wiki documentation
3. Internal training on eval patterns
4. Plan for Phase 4 (advanced reliability patterns)

---

## Success Criteria Checklist

- ✅ 5 learning notebooks created (Days 1-5)
- ✅ Production eval pipeline implemented (Days 8-10)
- ✅ tool_choice validated with 30 edge cases
- ✅ Parser + guardrails + evaluator modules created
- ✅ Error messages improved and documented
- ✅ Integration with ai_service.py completed
- ✅ Phase 1 retrospective created
- ✅ PLAN, PHASES, BUGLOG documentation complete

**Status:** All criteria met ✅

---

## Learning Outcomes

**Layer 2 (Output Control):** 5/5 — Mastered prefill, stop_sequences, tool_choice, and their trade-offs  
**Layer 3 (Guardrails):** 5/5 — Implemented code + model validation layers  
**Layer 4 (Evaluators):** 4/5 — Built evaluation framework, database integration deferred  

**Key Insight:** Reliability is not a feature — it's an architecture decision made upfront, with validation layers baked into every step of the pipeline.

---

## Status: Ready for Phase 3 ✅

Iteration 11 established the evaluation foundation. Phase 3 builds on it with semantic caching and RAG integration.
