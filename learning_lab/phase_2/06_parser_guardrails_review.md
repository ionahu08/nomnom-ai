# Day 6 Code Review: parser.py + guardrails.py

**Date:** June 7, 2026  
**Files reviewed:**
- `NomNom-Backend/src/llm/parser.py` (154 lines)
- `NomNom-Backend/src/llm/guardrails.py` (141 lines)

**Context:** These files implement the two-stage validation system:
1. Parser: Extract & validate structure (Pydantic)
2. Guardrails: Validate business logic (ranges, content safety)

---

## Part 1: parser.py Analysis

### What It Does

Parser extracts and validates Claude's tool_use response. Two main functions:

1. **extract_tool_use_response()** — Finds `tool_use` block in Claude's response
2. **validate_and_parse()** — Validates extracted data against Pydantic schema
3. **safe_parse_json()** — Legacy fallback for text-based JSON (markdown fences)

### What It Handles That json.loads() Doesn't

parser.py handles **three things** that naked `json.loads()` can't:

1. **Extracts tool_use block from Claude's Message object**
   - `json.loads()` only parses strings
   - `parser.py` finds the `tool_use` block in Claude's Message object (structured data, not text)

2. **Strips markdown code fences**
   - `json.loads("```json\n{...}```")` → FAILS (invalid JSON syntax)
   - `parser.py` strips the fences first, then parses

3. **Validates structure with Pydantic**
   - `json.loads('{"food_name": "pizza"}')` → returns dict with no validation (missing required fields!)
   - `parser.py` checks required fields are present + correct types

**Example:**
```python
# naked json.loads() accepts this:
data = json.loads('{"food_name": "pizza"}')
# Returns: {"food_name": "pizza"}
# ❌ Missing "calories", "protein_g", etc. — no error!

# parser.py rejects it:
validated = validate_and_parse(data, FoodAnalysisResponse)
# ❌ ValidationError: "calories" field required
```

### Edge Cases It Might Miss

**Question:** What could go wrong that parser.py doesn't catch?

parser.py has several edge case vulnerabilities:

1. **Multiple tool_use blocks → Only returns first one**
   - Risk: If Claude returns multiple tool_use blocks, we ignore the rest
   - Impact: Unlikely but possible if Claude misunderstands the request

2. **No content blocks at all → Will crash with ParseError**
   - Risk: If response has no `content`, `extract_tool_use_response()` raises ParseError
   - Impact: Not graceful; propagates up and could crash the app

3. **No auto-retry on Pydantic validation failure**
   - Risk: If Pydantic validation fails, error propagates immediately
   - Impact: One small validation error kills the request (no recovery mechanism)
   - Potential fix: Could add retry loop (call Claude again, ask to fix)

4. **Malformed tool_use.input before Pydantic validation**
   - Risk: `tool_use.input` could be corrupted/incomplete, Pydantic sees garbage
   - Impact: Cryptic validation errors instead of clear failures

### Can tool_choice Replace It?

**Short answer:** tool_choice can replace **safe_parse_json()**, but NOT the entire parser.py.

**Detailed breakdown:**

**What tool_choice does:**
```python
# Define a tool with schema
tools = [{
    "name": "analyze_food",
    "schema": {...Pydantic model...}
}]

# Force Claude to use it
response = client.messages.create(
    ...,
    tools=tools,
    tool_choice="force_analyze_food"  # Claude MUST use this tool
)
```

When Claude is forced to use a tool:
- ✅ No markdown code fences (Claude returns structured tool_use, not text)
- ✅ Structure guaranteed by tool schema (equivalent to Pydantic)
- ❌ Still need `extract_tool_use_response()` to pull data from tool_use block
- ❌ Still need Pydantic validation for field-level type checking

**Verdict:**

```
Before (Phase 1):
  safe_parse_json() → handles markdown → Pydantic validation

After (Phase 2, with tool_choice):
  ✅ safe_parse_json() no longer needed (tool_choice eliminates markdown)
  ✅ Tool schema reduces Pydantic validation burden
  ❌ extract_tool_use_response() still needed (pull from Message object)
  ❌ Pydantic still useful (custom validation logic beyond schema)
```

**Bottom line:** tool_choice simplifies parser.py but doesn't eliminate it. We still need extraction + validation layers.

---

## Part 2: guardrails.py Analysis

### Full Inventory of Validation Rules

| Rule | Check | Min | Max | Reason |
|------|-------|-----|-----|--------|
| Calories | 0-5000 kcal | 0 | 5000 | Catch hallucinations (e.g., 500,000 kcal). Single meal realistically never exceeds 5000. |
| Protein | 0-500g | 0 | 500g | Max realistic protein in one meal is ~100-150g (5 chicken breasts). 500g is buffer for edge cases. |
| Carbs | 0-500g | 0 | 500g | Max realistic carbs in one meal is ~200-300g (2-3 cups rice). 500g is generous buffer. |
| Fat | 0-500g | 0 | 500g | Max realistic fat in one meal is ~50-100g. 500g is extreme buffer (unlikely Claude exceeds this). |
| Food name | 1-200 chars | 1 | 200 | Prevents empty strings (Claude common failure). 200 chars is generous limit. |
| Cat roast | 1-500 chars | 1 | 500 | Prevents empty comments. 500 chars is 2-3 sentences (typical roast length). |
| Toxicity | Forbidden phrases | — | — | Safety guardrail: prevents hateful/harmful output even if Claude accidentally generates it. |
| Macro consistency | `calories ≤ (protein*4 + carbs*4 + fat*9) * 1.2` | — | — | Sanity check: macros should roughly account for total calories. 1.2x margin allows estimation variance. |

### Which Rules Are Justified? Which Feel Speculative?

**Justified by real failure modes (High confidence):**

1. **Calories range (0-5000)** ✅ JUSTIFIED
   - LLMs commonly hallucinate absurd numbers (e.g., 500,000 kcal)
   - You saw this in Day 3-4 eval: some edge cases triggered semantic violations
   - Real risk, worth catching

2. **Food name empty** ✅ JUSTIFIED
   - Empty strings are common LLM failures when given ambiguous input
   - You saw this in Day 4-5: Claude returns empty/null fields on hard cases
   - Real risk

3. **Macro consistency check** ✅ JUSTIFIED (soft warning only)
   - Catches obvious math errors (calories way higher than macros can explain)
   - Doesn't hard-fail; just warns
   - Low friction, high signal

---

**Speculative (no hard evidence, but reasonable precautions):**

1. **Protein max 500g** ⚠️ SPECULATIVE
   - Realistic max: ~150g per meal
   - 500g buffer seems excessive
   - Unlikely Claude ever exceeds 500g
   - **Recommendation:** Lower to 300g (catches more hallucinations, realistic buffer)

2. **Fat max 500g** ⚠️ SPECULATIVE
   - Realistic max: ~100g per meal
   - 500g is extreme overkill
   - **Recommendation:** Lower to 200g

3. **Carbs max 500g** ⚠️ SLIGHTLY SPECULATIVE
   - Realistic max: ~300g per meal
   - 500g is reasonable but generous
   - **Recommendation:** Keep as-is (500g still reasonable)

4. **Food name max 200 chars** ⚠️ SPECULATIVE
   - Unlikely Claude generates 200+ char food names
   - But it's a reasonable safety bound
   - **Recommendation:** Keep as-is (doesn't hurt)

5. **Toxicity phrases list** ⚠️ SPECULATIVE
   - "kill yourself", "bomb", "terrorist" are extreme edge cases
   - Claude *very unlikely* to generate these in a food roast
   - But cost of checking is negligible
   - **Recommendation:** Keep as safety belt, but don't expect it to trigger

6. **Cat roast max 500 chars** ⚠️ SPECULATIVE
   - Roasts are typically 1-2 sentences (~100-200 chars)
   - 500 char limit is generous
   - **Recommendation:** Could lower to 300, but not critical

### Are Error Messages "Claude-Readable"?

**Question:** If a guardrail fails, can Claude read the error and self-correct?

**Current error messages:**
```python
raise GuardrailViolation(
    f"Calories {analysis.calories} out of range [0, 5000]"
)
raise GuardrailViolation(
    f"Protein {macro_value}g out of range [0, 500]"
)
```

**Assessment: PARTIALLY Claude-readable**

✅ **What works:**
- Clear what failed: "Calories 500000 out of range [0, 5000]"
- Claude understands the constraint: must be between 0 and 5000
- If we show this error + ask to retry, Claude can likely fix it

❌ **What could be better:**
- No explanation of *why* this range exists
- No instruction for Claude on how to fix it
- Generic format doesn't guide Claude toward plausible values

**Improved error messages:**

```python
# Current (okay but sparse):
f"Calories {analysis.calories} out of range [0, 5000]"

# Improved (Claude-friendly):
f"Calories must be 0-5000 kcal for a single serving. You estimated {analysis.calories} kcal, which is out of range. Please re-estimate a realistic serving size."

# Current (sparse):
f"Protein {analysis.protein_g}g out of range [0, 500]"

# Improved:
f"Protein must be 0-500g per serving. You estimated {analysis.protein_g}g. For reference, typical meals have 10-50g protein. Please re-estimate."
```

**Recommendations:**

1. **Add context** — explain why the range exists
2. **Add guidance** — give Claude a target range to aim for (e.g., "typical meals have 10-50g")
3. **Make actionable** — tell Claude what to do: "Please re-estimate"

**For retry loop (Phase 2 Days 8-9):**
If we add a retry mechanism (call Claude again on guardrail failure), better error messages are critical. Claude needs to understand what went wrong and how to fix it.

---

## Part 3: Changes I'd Make

### Improvements to parser.py

**Issue 1: No auto-retry on validation failure**
- **Current:** If Pydantic validation fails, ParseError is raised immediately
- **Proposal:** Add optional retry loop: `parse_with_retry(response, model, max_retries=2)`
  - On validation failure, could call Claude again: "Your previous response failed validation. Please fix: [error]. Try again."
- **Why:** Makes system more resilient. One bad response doesn't kill the request.
- **Cost/Benefit:** Adds complexity + API calls, but improves success rate

**Issue 2: Better error messages in ParseError**
- **Current:** Generic error messages ("Failed to validate food analysis response")
- **Proposal:** Include specific Pydantic error details in ParseError message
- **Why:** Helps debugging; shows exactly which field failed and why
- **Impact:** Small change, big improvement to observability

---

### Improvements to guardrails.py

**Issue 1: Tighten macro ranges (reduce speculative buffer)**
- **Current:** PROTEIN_MAX=500, FAT_MAX=500
- **Proposal:** 
  ```python
  PROTEIN_MAX = 300  # Reduced from 500 (realistic max ~150g)
  FAT_MAX = 200      # Reduced from 500 (realistic max ~100g)
  CARBS_MAX = 400    # Keep generous (realistic max ~300g)
  ```
- **Why:** Catches more hallucinations without rejecting valid meals. Current buffers are too generous.
- **Impact:** May reject edge cases, but improves signal-to-noise ratio

**Issue 2: Improve error messages for Claude-readability**
- **Current:**
  ```python
  raise GuardrailViolation(f"Calories {calories} out of range [0, 5000]")
  ```
- **Proposal:**
  ```python
  raise GuardrailViolation(
      f"Calories invalid: {calories} kcal. "
      f"Must be 0-5000 kcal for a single meal. "
      f"(Typical meals: 200-1000 kcal)"
  )
  ```
- **Why:** If we implement retry loop (Phase 2 Days 8-9), Claude needs context to fix errors
- **Impact:** Better user experience, enables self-correction loop

**Issue 3: Add logging for guardrail violations**
- **Current:** Only logs when validation passes (line 128-134)
- **Proposal:** Also log when guardrails fail with violation details
  ```python
  except GuardrailViolation as e:
      logger.warning(f"Guardrail violation: {e}", extra={"food_name": analysis.food_name})
      raise
  ```
- **Why:** Can measure which guardrails trigger most often (data-driven tuning)
- **Impact:** Enables future optimization based on real failure modes

**Issue 4: Consider toxicity check necessity**
- **Current:** Forbids 6 phrases in cat roast
- **Proposal:** Keep for now (low cost), but monitor if it ever triggers
- **Why:** Unlikely to prevent actual harm, but doesn't hurt
- **Action:** Log whenever a phrase is detected, review after 1 month of data

---

## Key Insights

### What Surprised Me

1. **Parser is lighter than expected**
   - Thought it would be complex JSON parsing
   - Reality: mostly just extraction + Pydantic delegation
   - Key complexity is in safe_parse_json() (markdown handling) — will be eliminated by tool_choice

2. **Guardrails are mostly speculative**
   - Expected hard data on what Claude actually violates
   - Reality: some rules (calories, empty strings) are justified; others are "just in case"
   - Suggests: guardrail ranges could be tightened without missing real failures

3. **Error messages assume perfect understanding**
   - Current messages work for logs/monitoring
   - But if Claude needs to self-correct (retry loop), messages need context
   - Preparing for Phase 2 Days 8-9 means improving messages now

### Connection to Phase 1 Learning

**Parser.py:**
- Uses `tool_use` extraction (related to Day 5 learning: tool_choice pattern)
- Validates with Pydantic (similar structure to how Pydantic defines schemas)
- Will be simplified in Phase 2 when we force tool_choice

**Guardrails.py:**
- Pure code-based validation (directly uses Day 4 learning: code grader)
- Implements numeric plausibility checks (like code grader's semantic level)
- Complements model-based grading (Day 5): code grader catches structure, model grader catches quality

**Together:**
- Production implements code-based grading (fast, deterministic)
- Eval (Day 4-5 learning) implements model-based grading (expensive, rich feedback)
- Production doesn't use model grading (would be too slow); eval doesn't need code grading (LLM handles structure)

### What's Missing

1. **Auto-retry mechanism**
   - If guardrails fail, we just error out
   - Could call Claude again with error feedback
   - Would increase success rate but add latency/cost

2. **Observability on failures**
   - Guardrails log when pass, but less detail on failures
   - Should log which rules trigger most often
   - Could guide future tuning of ranges

3. **Production performance data**
   - We have test data (Day 3-4), but not production data
   - Don't know which guardrails actually matter in real usage
   - Suggests: monitor failures, adjust ranges based on real data

4. **Integration with retry loop**
   - Parser + Guardrails raise errors, but no retry mechanism
   - Phase 2 Days 8-9 will likely add retry (call Claude again on failure)
   - Should design error messages now for that use case

---

## Execution Context

**When do parser.py and guardrails.py run?**

**1. Production (Every User Action):**
```
User uploads photo
    ↓
App calls Claude API
    ↓
Claude returns response with tool_use
    ↓
parser.py executes ← extracts tool_use, validates Pydantic schema
    ↓
guardrails.py executes ← checks calories, macros, food name, toxicity
    ↓
✅ All checks pass → Data saved to database
❌ Any check fails → Reject, return error to user
```

**2. Evaluation (Days 4-5 Testing):**
```
Load 30 test cases (Day 3 dataset)
    ↓
For each test case:
    Call Claude with food description
    ↓
    parser.py executes ← extract + validate
    ↓
    guardrails.py executes ← check business logic
    ↓
    code grader (Day 4) ← score JSON/schema/semantics
    ↓
    model grader (Day 5) ← Opus judges quality
    ↓
Save results to eval_report.md
```

**Key Insight:**
Same code (`parser.py` + `guardrails.py`), but different purposes:
- **Production:** Protection layer — prevent bad data from reaching database
- **Evaluation:** Foundation for quality measurement — combined with code + model graders to generate scores

This separation is intentional: production prioritizes speed/safety (code-based checks only), while eval prioritizes accuracy (code + model checks).

---

## Summary

**parser.py verdict:** ✅ Solid extraction + validation layer
- Handles three things json.loads() can't (tool_use extraction, markdown stripping, Pydantic validation)
- Has edge cases (no retry, multiple tool_use blocks, no graceful degradation)
- safe_parse_json() is legacy code (will be eliminated by tool_choice in Phase 2)
- Recommendation: Add optional retry on validation failure

**guardrails.py verdict:** ✅ Good safety net, but could be optimized
- Justified rules: calories, empty fields, macro consistency
- Speculative rules: protein/fat/carb maxes are too generous (500g is extreme)
- Error messages are functional but not Claude-friendly (need context for retry loop)
- Recommendations: Tighten macro ranges, improve error messages, add logging

**Together:** Implement production-grade code-based grading
- Deterministic, fast, no LLM calls
- Complements model-based grading (used only for eval, not production)
- Foundation for retry loops in Phase 2 Days 8-9

---

## Transition to Phase 2 Days 6-9

**Day 6 complete:** Code review of parser.py + guardrails.py ✅

**Day 7 (next):** Code review of tools.py + evaluator.py
- tools.py: How tool use is defined and dispatched
- evaluator.py: Grading approach (code-based vs. model-based vs. hybrid)

**Days 8-9 (capstone):** Build eval pipeline + v0 vs v1 comparison
- Integrate tool_choice (replace prefill+stop)
- Run full 30-case eval with code + model grading
- Generate comparison report showing improvement

**Day 10:** Production refactor
- Land tool_choice in src/llm/
- Improve error messages in guardrails
- Create iteration folder (docs/iterations/11-eval-pipeline/)
