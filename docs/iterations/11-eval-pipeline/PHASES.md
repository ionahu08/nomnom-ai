# Iteration 11: Implementation Phases

**Overview:** Building and validating production eval pipeline (Days 1-10 of Phase 2)

---

## Phase 1: Foundation — Output Control Techniques (Days 1-2)

**Goal:** Learn three ways to force structured output

### Prefill Assistant (Day 1)
```python
# Prefix Claude's response to guide output
messages = [
    {"role": "user", "content": prompt},
    {"role": "assistant", "content": '{"food_name": "'},  # Prefill
]
response = client.messages.create(messages=messages)
# Result: Claude completes the JSON
```

**Lesson:** Works for text, but Claude can still go off-track (missing fields, type mismatches).

### Prefill + Stop (Day 1)
```python
messages = [
    {"role": "user", "content": prompt},
    {"role": "assistant", "content": '```json\n{'},  # Prefill
]
response = client.messages.create(
    messages=messages,
    stop_sequences=['```']  # Stop at closing fence
)
# Result: JSON extracted and parsed
```

**Lesson:** Better than prefill alone, but still requires JSON parsing (markdown handling, error recovery).

### Tool Choice (Day 2 preview)
```python
response = client.messages.create(
    messages=messages,
    tools=[ANALYZE_FOOD_TOOL],
    tool_choice={"type": "tool", "name": "analyze_food"}  # FORCE tool
)
# Result: tool_use block with guaranteed structure
```

**Lesson:** Safest option — structure enforced at API level, no parsing needed.

---

## Phase 2: Dataset + Grading (Days 3-5)

**Goal:** Build eval infrastructure and grading systems

### Day 3: Dataset Generation
```python
# Use Claude to generate 30 challenging food descriptions
# Edge cases: blurry photos, ambiguous items, mixed dishes, unfamiliar foods
test_cases = await generate_test_cases(num_cases=30)
# Result: generated_dataset.json (reusable test data)
```

**Lesson:** Use Claude to bulk-generate edge cases. More efficient than hand-writing.

### Day 4: Code-Based Grading
```python
# Three-level validation (no LLM calls needed)
class NutritionGrader:
    - Level 1: JSON validity (can Python parse it?)
    - Level 2: Schema validity (all required fields? correct types?)
    - Level 3: Semantic validity (plausible nutrition values?)

# Results: 98.3/100 avg on 30 cases
```

**Lesson:** Code-based grading is fast, cheap, deterministic. Use for all cases.

### Day 5: Model-Based Grading
```python
# Use Opus (stronger judge) to evaluate quality
async def grade_with_opus(food_description, claude_output):
    # Opus assesses: food identification, calorie plausibility, macro consistency
    # Returns: score (0-10) + strengths/weaknesses
    
# Signal fusion: combine code + model scores
final_score = (code_score * 0.4) + (model_score * 0.6)
```

**Lesson:** Model-based grading is expensive, but rich. Use sparingly on samples.

---

## Phase 3: Code Review (Days 6-7)

**Goal:** Understand production validation layers

### Day 6: parser.py + guardrails.py Review

**parser.py (154 lines):**
- Extract tool_use block from Claude's response
- Validate with Pydantic (field-level type checking)
- No auto-retry (improvement opportunity)

**guardrails.py (141 lines):**
- Calorie validation (0-5000 kcal)
- Macro validation (0-500g each)
- Empty field checks
- Macro-calorie consistency check
- Toxicity phrase detection

**Recommendation:** Improve error messages for Claude readability (needed for retry loops).

### Day 7: tools.py + evaluator.py Review

**tools.py (88 lines):**
- Simple: Just ANALYZE_FOOD_TOOL schema definition
- Enforces structure via JSON Schema
- Works with tool_choice to guarantee Claude uses the tool

**evaluator.py (158 lines):**
- 90% stubbed — skeleton only
- Current: In-memory counters + console logging
- Missing: Database integration, per-model tracking, API endpoints
- Purpose: Layer 4 differentiator (reliability engineering)

**Recommendation:** Implement after capstone (needs database schema changes).

---

## Phase 4: Capstone Comparison (Days 8-9)

**Goal:** Compare output control techniques at scale

### Day 8: v1.0 Tool Choice
```python
# Run v1.0 on all 30 edge cases
# Tool Choice approach:
response = await client.messages.create(
    messages=messages,
    tools=[ANALYZE_FOOD_TOOL],
    tool_choice={"type": "tool", "name": "analyze_food"}  # FORCE
)

# Results:
# - Success rate: 100% (all 30 completed)
# - Schema valid: 100% (all had correct structure)
# - Semantic valid: 93.3% (28/30 passed plausibility)
# - Average score: 98.3/100
```

### Day 9: Comparison + Model Grading
```python
# Run Opus on sample of v1.0 results for quality assessment
# Generate comprehensive comparison report:
# - v0.5 (prefill+stop): 95% success rate, 9.4/10 avg (5 easy cases)
# - v1.0 (tool_choice): 100% success rate, 98.3/100 avg (30 hard cases)

# Key finding: tool_choice is production-grade
```

**Pipeline Architecture (Staging Pattern):**
```
Dataset (30 cases)
    ↓
[08] Fast Stage — Code-based grading (~2min, cheap)
    ↓
Results JSON (intermediate artifact)
    ↓
[09] Slow Stage — Model-based grading + reporting (~5min, expensive)
    ↓
Comparison Report + Metrics
```

---

## Phase 5: Production Refactor (Day 10)

**Goal:** Land tool_choice in actual backend

### Change 1: Improved Error Messages (guardrails.py)

**Before:**
```
"Calories 500000 out of range [0, 5000]"
"Protein 600g out of range [0, 500]"
```

**After:**
```
"Calories: 500000 kcal is unrealistic (typical range: 50-2000 kcal per meal). Re-estimate this food."
"Protein: 600g is unrealistic (typical range: 0-150g per meal). Re-estimate."
```

**Impact:** Errors now guide Claude toward correction (support for retry loops).

### Change 2: tool_choice Parameter (ai_service.py)

**Before:**
```python
response = await llm_client.create_message_with_retry(
    model=route.primary_model,
    messages=messages,
    tools=tools,  # Tools defined but not forced
    temperature=route.temperature,
)
```

**After:**
```python
response = await llm_client.create_message_with_retry(
    model=route.primary_model,
    messages=messages,
    tools=tools,
    tool_choice={"type": "tool", "name": "analyze_food"},  # FORCE tool use
    temperature=route.temperature,
)
```

**Impact:** Guarantees 100% success rate for structured output.

---

## Production Pipeline Flow

```
User uploads food photo
    ↓
API endpoint: POST /api/v1/food-logs/analyze
    ↓
ai_service.analyze_food_photo()
    ├─ Render system prompt with cat style
    ├─ Encode image as base64
    ├─ Check semantic cache (if DB available)
    ├─ Call LLM with tool_choice=force_analyze_food
    │  └─ Haiku returns: tool_use block (guaranteed structure)
    ├─ parser.parse_response()
    │  └─ Extract tool_use.input (already valid JSON)
    ├─ guardrails.validate()
    │  └─ Check nutrition plausibility
    │  └─ If violation: return helpful error message
    └─ Return FoodAnalysisResponse
    
Response includes:
- food_name, calories, protein_g, carbs_g, fat_g
- food_category, cuisine_origin
- cat_roast (funny comment)
- photo_path
```

---

## Key Insights

1. **tool_choice is production-grade**
   - Enforces structure at API level (not application code)
   - 100% success rate (vs 95% with prefill+stop)
   - Simpler code (no markdown parsing, no recovery logic)

2. **Evaluation is a process, not a test**
   - Code-based: Fast feedback (use always)
   - Model-based: Deep feedback (use sparingly)
   - Staging pipeline: Separate concerns (reusable artifacts)

3. **Error messages are part of reliability**
   - Generic: "out of range"
   - Helpful: "unrealistic, typical range X–Y, re-estimate"
   - Impacts retry success + user experience

4. **Evaluator.py is Layer 4 waiting to be built**
   - Current: Skeleton (logging only)
   - Needed: Database integration, per-model tracking, API endpoints
   - Why: Data-driven prompt optimization (measure → iterate → improve)

---

## Files Modified

```
src/llm/guardrails.py
  - Improved error messages (8 messages made Claude-readable)
  - Added context about typical ranges

src/services/ai_service.py
  - Added tool_choice parameter to force tool use
  - Result: guaranteed structured output

docs/iterations/11-eval-pipeline/
  - PLAN.md (this folder) — goals, success criteria, resume info
  - PHASES.md (this file) — implementation details
  - BUGLOG.md (to be filled during iteration)
  - SUMMARY.md (to be filled at iteration end)
```

---

## Dependency Chain

```
Phase 1 (Week 1–2): API fundamentals, prompt engineering
  ↓ (foundation)
Phase 2 (Week 3–4): Output control + eval infrastructure ← CURRENT
  ├─ Days 1-2: Output control techniques
  ├─ Days 3-5: Dataset + grading systems
  ├─ Days 6-7: Code reviews (parser, guardrails, tools, evaluator)
  ├─ Days 8-9: Capstone (tool_choice comparison)
  └─ Day 10: Production refactor ← NOW HERE
  ↓ (next)
Phase 3 (Week 5–6): Semantic search + caching
  ├─ embedding.py — text → vectors
  ├─ cache.py — semantic cache (avoid duplicate analysis)
  └─ recommendation_service.py — RAG pipeline
```
