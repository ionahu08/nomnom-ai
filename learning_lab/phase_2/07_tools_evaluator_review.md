# Day 7 Code Review: tools.py + evaluator.py

**Date:** June 8, 2026  
**Files reviewed:**
- `NomNom-Backend/src/llm/tools.py` (88 lines)
- `NomNom-Backend/src/llm/evaluator.py` (158 lines)

**Context:** 
- **tools.py:** Tool schema definitions for tool_choice forced output
- **evaluator.py:** Accuracy tracking via user corrections (Layer 4 differentiator)

---

## Table of Contents

- [Part 1: tools.py Analysis](#part-1-toolspy-analysis)
  - [What It Does](#what-it-does)
  - [Schema Design](#schema-design)
  - [How It Works with tool_choice](#how-it-works-with-tool_choice)

- [Part 2: evaluator.py Analysis](#part-2-evaluatorpy-analysis)
  - [Current State: What's Implemented](#current-state-whats-implemented)
  - [Current State: What's Stubbed (TODO)](#current-state-whats-stubbed-todo)
  - [The Gap: What Production Needs](#the-gap-what-production-needs)
  - [Why This Matters (Layer 4 Differentiator)](#why-this-matters-layer-4-differentiator)

- [Part 3: Key Recommendations](#part-3-key-recommendations)
  - [tools.py Recommendations](#toolspy-recommendations)
  - [evaluator.py Recommendations](#evaluatorpy-recommendations)

- [Key Insights](#key-insights)
  - [What Surprised Me](#what-surprised-me)
  - [evaluator.py as Your Differentiator](#evaluatorpy-as-your-differentiator)
  - [Production-Readiness Assessment](#production-readiness-assessment)

- [Summary](#summary)

---

## Part 1: tools.py Analysis

### What It Does

**Extremely simple: Defines the JSON schema that Claude MUST use.**

tools.py has exactly ONE data structure:

```python
ANALYZE_FOOD_TOOL = {
    "name": "analyze_food",
    "input_schema": {
        "properties": {
            "food_name": {...},
            "calories": {...},
            "protein_g": {...},
            ...
        },
        "required": [all fields]
    }
}
```

**That's it.** No execution logic, no tool dispatch, no error handling. Just schema.

When combined with `tool_choice="force_analyze_food"`, Claude is forced to return data in exactly this shape.

### Schema Design

**The schema enforces structure:**
- ✅ All required fields present (no missing data)
- ✅ Correct types (calories is integer, not string)
- ✅ Field descriptions guide Claude

**But it doesn't enforce plausibility:**
- ❌ Can't prevent calories=500000 (tool schema doesn't validate ranges)
- ❌ Can't prevent empty strings (type is string, any string works)

**That's why guardrails.py exists** — tools.py guarantees structure, guardrails validate plausibility.

### How It Works with tool_choice

**Flow:**
```
Prompt Claude with tools=[ANALYZE_FOOD_TOOL] + tool_choice="force_analyze_food"
    ↓
Claude MUST call analyze_food tool
    ↓
Claude provides exactly these fields (guaranteed by schema)
    ↓
parser.py extracts + Pydantic validates
    ↓
guardrails.py checks plausibility
```

**Key insight:** tools.py is the **first line of defense** (structure). guardrails.py is the **second line** (plausibility).

---

## Part 2: evaluator.py Analysis

### Current State: What's Implemented

**Two classes:**

1. **EvaluationMetrics** — In-memory counter
   - `record_analysis()` — increment total_analyses
   - `record_correction()` — increment total_corrections
   - `accuracy_rate` — calculate: 1 - (corrections / analyses)
   
   **Reality:** Just counters. Doesn't persist anywhere.

2. **Evaluator** — Static methods that mostly log
   - `record_correction()` — logs correction to console
   - `get_accuracy_rate()` — returns hardcoded `1.0` (always "perfect")
   - `get_evaluation_context()` — translates correction_rate to readable string

   **Reality:** Logging exists, but database integration doesn't.

### Current State: What's Stubbed (TODO)

**Lines 132-139: The TODO comment shows what SHOULD happen:**

```python
# TODO: Implement with database query
# SELECT COUNT(CASE WHEN is_user_corrected THEN 1 END) as corrections,
#        COUNT(*) as total
# FROM food_logs
# WHERE created_at > NOW() - INTERVAL days
#   AND (model = ? OR ? IS NULL)
#   AND (user_id = ? OR ? IS NULL)
return 1.0  # Stub: always returns perfect accuracy
```

**What's missing:**
- ❌ No database queries
- ❌ No food_logs table integration
- ❌ No is_user_corrected flag tracking
- ❌ No per-model accuracy tracking
- ❌ No per-food-type accuracy tracking
- ❌ No time-window filtering (days parameter exists but unused)

### The Gap: What Production Needs

**To make evaluator.py production-grade:**

1. **Database schema changes:**
   - Add `is_user_corrected` boolean to food_logs table
   - Add corrections table: (user_id, food_log_id, original_value, corrected_value, model_used)

2. **Implement actual queries:**
   - Count corrections per model
   - Count corrections per user
   - Count corrections per food category
   - Filter by date range (last 7 days, 30 days, etc.)

3. **Connect to API endpoints:**
   - When user edits a food log, trigger `Evaluator.record_correction()`
   - Expose `/api/v1/accuracy?model=claude-haiku&days=30` endpoint for dashboards

4. **Add missing metrics:**
   - Accuracy per model (Haiku vs Sonnet vs Opus)
   - Accuracy per food type (salads vs fast food vs desserts)
   - Accuracy per user (some users correct more than others)
   - Trending (is accuracy improving over time?)

### Why This Matters (Layer 4 Differentiator)

**This is YOUR Layer 4 differentiator: Reliability Engineering.**

Most LLM engineers iterate on prompts by gut feeling. You should be different:

> "I use production correction data to measure accuracy. Last month, Haiku was 92% accurate on salads but only 78% on Asian food. So I retrained the salad prompt and now it's 96%."

That narrative comes from **evaluator.py**. But it's not built yet.

**Current state:** Evaluator exists as skeleton. No real data collection, no real insights.

---

## Part 3: Key Recommendations

### tools.py Recommendations

**#1: Add field validation hints in descriptions** (Low priority)
- **Current:** `"calories": {"type": "integer", "description": "Estimated calories (0-5000)"}`
- **Proposal:** Add examples or constraints in description to guide Claude
- **Why:** tool schema doesn't validate ranges; descriptions can nudge Claude toward plausible values
- **Impact:** Slight improvement in first-pass accuracy (reduces guardrails failures)

**#2: Consider additional tools** (Future planning)
- **Current:** Only `analyze_food` tool defined
- **Proposal:** In Phase 3, add tools for: `lookup_nutrition_db`, `parse_nutrition_label`, `recommend_meal`
- **Why:** Multi-tool agent loops (Phase 3 learning) need more tools
- **Impact:** Enables more complex workflows later

### evaluator.py Recommendations

**#1: Implement database queries** (CRITICAL for Layer 4)
- **Current:** Stub returning `1.0` (always perfect accuracy)
- **Proposal:** Implement the TODO comment — actual SQL queries against food_logs
- **Why:** Without this, you have zero production data on accuracy. Cannot measure reliability.
- **Impact:** Foundation for all Layer 4 work. No data = no differentiator.
- **Timeline:** Should be done before Days 8-9 capstone; needed for Days 10+ production work

**#2: Add is_user_corrected flag to food_logs schema** (CRITICAL)
- **Current:** No flag to mark corrections
- **Proposal:** Add migration: `ALTER TABLE food_logs ADD COLUMN is_user_corrected BOOLEAN DEFAULT FALSE`
- **Why:** Can't track corrections without marking them
- **Impact:** Required prerequisite for #1

**#3: Create corrections table** (CRITICAL)
- **Current:** Correction data not stored anywhere
- **Proposal:** New table: `corrections(id, user_id, food_log_id, original_food_name, corrected_food_name, model_used, created_at)`
- **Why:** Need historical record of what went wrong and why
- **Impact:** Enables detailed analysis (per model, per food type, per user)

**#4: Implement per-model accuracy tracking** (HIGH priority)
- **Current:** No distinction between models
- **Proposal:** Track which model made each analysis; measure accuracy per model
- **Why:** Different models have different accuracy profiles (Haiku vs Sonnet)
- **Impact:** Can identify which model is best for which use case

**#5: Add per-food-type accuracy** (MEDIUM priority)
- **Current:** No categorization
- **Proposal:** Group corrections by food_category (salads, fast food, desserts, etc.)
- **Why:** Some food types are harder to analyze
- **Impact:** Can optimize prompts per category

**#6: Expose accuracy via API endpoint** (MEDIUM priority)
- **Current:** No way to fetch accuracy metrics
- **Proposal:** Add `/api/v1/metrics/accuracy?model=...&days=...&food_category=...`
- **Why:** Can display accuracy in dashboards, show users how reliable the system is
- **Impact:** Transparency + data for decision-making

---

## Key Insights

### What Surprised Me

1. **tools.py is remarkably simple**
   - Expected: Complex tool dispatch logic
   - Reality: Just schema definition (88 lines, mostly JSON)
   - Implication: tool_choice does the heavy lifting; we just define the shape

2. **evaluator.py is a skeleton, not a system**
   - Expected: Production-grade accuracy tracking
   - Reality: Logging exists, but database integration is 100% stubbed (TODO comments)
   - Implication: No production data on accuracy exists yet. You're starting from zero.

3. **This is YOUR Layer 4 differentiator waiting to be built**
   - Phase 1-7 roadmap mentions evaluator exists
   - But it's not actually implemented
   - Opportunity: You can build this properly from scratch in Phase 2/3

### evaluator.py as Your Differentiator

**Why this matters for interviews:**

Most candidates: "I use prompts to improve accuracy"  
You: "I use production correction data to measure accuracy by model and food type. Here's the pipeline..."

The second story is infinitely more credible. It requires:
1. Collecting correction data (evaluator.py)
2. Measuring accuracy (SQL queries)
3. Acting on insights (prompt improvements based on data)

**Current gap:** evaluator.py has skeleton but no substance. This is your opportunity to build it properly.

### Production-Readiness Assessment

| Component | Status | Blockers |
|-----------|--------|----------|
| tools.py schema | ✅ Complete | None |
| evaluator.py logging | ⚠️ Partial | Needs DB integration |
| evaluator.py queries | ❌ Stubbed | Needs schema changes + implementation |
| Per-model tracking | ❌ Missing | Needs query implementation |
| Per-food-type tracking | ❌ Missing | Needs query implementation |
| Accuracy API endpoint | ❌ Missing | Needs query implementation |

**Verdict:** tools.py is production-ready. evaluator.py is 10% implemented (logging only).

---

## Summary

**tools.py:** ✅ Simple but solid
- Just schema definition (no execution logic)
- Guarantees structure via tool_choice
- Works perfectly with parser.py + guardrails.py pipeline
- Could improve: add constraint hints to field descriptions (guides Claude)

**evaluator.py:** ❌ Skeleton only (0% database integration)
- Logging exists but doesn't persist
- Queries are stubbed with TODO comments
- No per-model, per-food-type, or per-user tracking
- **This is your Layer 4 differentiator — waiting to be built**

**Critical path for Layer 4:**
1. Add `is_user_corrected` flag to food_logs
2. Create corrections table
3. Implement `get_accuracy_rate()` queries
4. Track per model + per food type
5. Expose via API endpoint

**Days 8-9 capstone will use current evaluator.py (test-time).**  
**Days 10+ production work should implement real evaluator.py (production-time).**

---

**Day 7 review complete. Ready for Days 8-9: Build capstone with tool_choice + full eval pipeline.**
