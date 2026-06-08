# Day 6 Code Review: parser.py + guardrails.py

**Date:** June 7, 2026  
**Files reviewed:**
- `NomNom-Backend/src/llm/parser.py` (154 lines)
- `NomNom-Backend/src/llm/guardrails.py` (141 lines)

**Context:** Two-stage validation system:
1. **Parser:** Extract & validate structure (tool_use → Pydantic)
2. **Guardrails:** Validate business logic (ranges, content safety)

---

## Table of Contents

- [Part 1: parser.py Analysis](#part-1-parserpy-analysis)
  - [What It Does & What It Handles](#what-it-does--what-it-handles)
  - [Edge Cases It Might Miss](#edge-cases-it-might-miss)
  - [tool_choice Relationship](#tool_choice-relationship)

- [Part 2: guardrails.py Analysis](#part-2-guardrailspy-analysis)
  - [Validation Rules Inventory](#validation-rules-inventory)
  - [Error Messages Assessment](#error-messages-assessment)

- [Part 3: Key Recommendations](#part-3-key-recommendations)
  - [parser.py Improvements](#parserpy-improvements)
  - [guardrails.py Improvements](#guardrailspy-improvements)

- [Key Insights](#key-insights)
  - [What Surprised Me](#what-surprised-me)
  - [Connection to Phase 1 Learning](#connection-to-phase-1-learning)
  - [What's Missing](#whats-missing)

- [Execution Context](#execution-context)
- [Summary](#summary)

---

## Part 1: parser.py Analysis

### What It Does & What It Handles

**Parser extracts and validates Claude's tool_use response.**

**Three capabilities that `json.loads()` can't do:**

1. **Extracts tool_use block** — Finds `tool_use` in Claude's Message object (not just string parsing)
2. **Strips markdown fences** — Removes ```json...``` before parsing (legacy fallback)
3. **Pydantic validation** — Checks required fields + correct types (json.loads ignores this)

**Example:**
```python
# json.loads accepts incomplete data:
json.loads('{"food_name": "pizza"}')  # ✅ Returns dict, no error

# parser.py enforces completeness:
validate_and_parse(data, FoodAnalysisResponse)  # ❌ Error: "calories" required
```

### Edge Cases It Might Miss

1. **Multiple tool_use blocks** → Returns only first one (unclear which is correct)
2. **No content blocks** → Crashes with ParseError (not graceful)
3. **No auto-retry on validation failure** → One error kills entire request (no recovery)
4. **Malformed tool_use.input** → Pydantic gets garbage, cryptic error messages

### tool_choice Relationship

**Can tool_choice replace parser.py?** Partially.

**tool_choice eliminates:**
- ✅ `safe_parse_json()` (markdown handling) — tool schema guarantees structure
- ✅ Some Pydantic burden — tool schema acts like schema definition

**tool_choice still requires:**
- ❌ `extract_tool_use_response()` — need to pull data from Message object
- ❌ Pydantic validation — field-level checking + custom logic

**Verdict:** tool_choice simplifies parser but doesn't eliminate it.

---

## Part 2: guardrails.py Analysis

### Validation Rules Inventory

| Rule | Range | Justification | Status |
|------|-------|---|---|
| Calories | 0-5000 kcal | LLMs hallucinate (e.g., 500,000). Single meal realistically ≤ 5000. | ✅ Justified |
| Protein | 0-500g | Realistic max ~150g. 500g is buffer for edge cases. | ⚠️ Speculative (buffer too large) |
| Carbs | 0-500g | Realistic max ~300g. 500g is reasonable buffer. | ⚠️ Speculative but acceptable |
| Fat | 0-500g | Realistic max ~100g. 500g is extreme overkill. | ⚠️ Speculative (buffer too large) |
| Food name | 1-200 chars | Prevents empty strings (common LLM failure). | ✅ Justified |
| Cat roast | 1-500 chars | Prevents empty comments. 500 chars ≈ 2-3 sentences. | ⚠️ Speculative but harmless |
| Toxicity | Forbidden phrases | Safety guardrail (edge case, unlikely to trigger). | ⚠️ Speculative but cost-free |
| Macro consistency | `cal ≤ (p×4 + c×4 + f×9) × 1.2` | Sanity check: macros align with calories. Soft warning only. | ✅ Justified |

**Summary:**
- **Justified rules:** Calories, empty fields, macro consistency
- **Speculative rules:** Protein/fat/carb max values are too generous; could be tightened

### Error Messages Assessment

**Current:** `"Calories 500000 out of range [0, 5000]"`

**Assessment:** PARTIALLY Claude-readable
- ✅ Clear what failed
- ❌ No context on *why* this range exists
- ❌ No guidance on how to fix

**Improvement needed (especially for retry loops in Days 8-9):**

Current → Improved:
```python
f"Calories {cal} out of range [0, 5000]"
# ↓
f"Calories: {cal} kcal (realistic: 200-1000 kcal). Please re-estimate."
```

---

## Part 3: Key Recommendations

### parser.py Improvements

**#1: Add auto-retry on validation failure** (High priority)
- **Current:** ParseError raised immediately; request dies
- **Proposal:** Optional retry loop — call Claude again with error details
- **Why:** Improves success rate without breaking existing code
- **Impact:** Needed for Phase 2 Days 8-9 retry mechanism

**#2: Better error messages in ParseError**
- **Current:** Generic ("Failed to validate food analysis response")
- **Proposal:** Include Pydantic error details (which field, why it failed)
- **Why:** Aids debugging and future retry logic
- **Impact:** Small effort, big improvement to observability

### guardrails.py Improvements

**#1: Tighten macro ranges** (Medium priority)
- **Current:** PROTEIN_MAX=500, FAT_MAX=500
- **Proposal:** PROTEIN_MAX=300, FAT_MAX=200
- **Why:** Current buffers too generous; catches more hallucinations
- **Impact:** May reject rare edge cases, improves signal-to-noise

**#2: Improve error messages for Claude-readability** (High priority for Days 8-9)
- Current error messages need context (why range exists, what Claude should aim for)
- Essential when implementing retry loop

**#3: Add logging for guardrail violations** (Medium priority)
- **Current:** Only logs when validation passes
- **Proposal:** Also log failures (which rules trigger, how often)
- **Why:** Data-driven tuning; understand what actually matters in production
- **Impact:** Enables optimization based on real failure modes

**#4: Monitor toxicity phrases** (Low priority)
- Unlikely to trigger, but keep for safety belt
- Add logging to measure if it ever fires
- Review after 1 month of production data

---

## Key Insights

### What Surprised Me

1. **Parser is simpler than expected**
   - Thought: Complex JSON parsing logic
   - Reality: Mostly extraction + Pydantic delegation
   - Key complexity in `safe_parse_json()` — eliminated by tool_choice in Phase 2

2. **Guardrails are mostly speculative**
   - Thought: Rules justified by real failure data
   - Reality: Some justified (calories, empty fields); others are "just in case"
   - Implication: Could tighten ranges significantly without breaking legitimate meals

3. **Error messages are production-unready**
   - Current messages work for logs
   - But if Claude needs to self-correct (retry loop coming in Days 8-9), they need context
   - Preparing error messages now = faster Days 8-9 implementation

### Connection to Phase 1 Learning

- **parser.py uses tool_use extraction** (Day 5 learning: tool_choice pattern)
- **guardrails.py is pure code-based validation** (Day 4 learning: code grader)
- **Together implement production grading:** Code-based only (fast, deterministic)
- **Complement to eval grading (Days 4-5):** Production is protection layer; eval measures quality

### What's Missing

1. **Auto-retry mechanism** — If guardrails fail, no recovery. Phase 2 Days 8-9 will add this.
2. **Production data** — Have test data (Day 3-4), but not real usage metrics. Need to monitor failures in production.
3. **Granular logging** — Which guardrails trigger most? Current logs don't answer this.

---

## Execution Context

**When do these files run?**

**Production (every user action):**
```
User photo → Claude API → parser.py (extract) → guardrails.py (validate) → ✅ Save or ❌ Reject
```

**Evaluation (Days 4-5):**
```
Test case → Claude → parser + guardrails → code grader → model grader → Score
```

**Key difference:** Same code, different purposes. Production = protection. Eval = measurement.

---

## Summary

**parser.py:** ✅ Solid extraction + validation layer
- Handles tool_use extraction, markdown stripping, Pydantic validation
- Edge cases: no retry, multiple tool_use blocks, crashes on missing content
- Will be simplified (not eliminated) by tool_choice in Phase 2
- **Next step:** Add optional retry mechanism

**guardrails.py:** ✅ Good safety net, but over-generous
- Justified rules: calories, empty fields, macro consistency
- Speculative rules: protein/fat/carb maxes (500g is extreme buffer)
- Error messages functional but not Claude-friendly
- **Next steps:** Tighten macro ranges, improve error messages, add violation logging

**Together:** Production-grade code-based grading (deterministic, fast, no LLM calls). Foundation for retry loops in Phase 2 Days 8-9.

---

**Day 6 complete. Ready for Day 7: tools.py + evaluator.py review.**
