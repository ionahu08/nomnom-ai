# Phase 5 Day 2: Workflow Design — "What Should I Eat?"

**User Story:** "I'm on a weight-loss diet; recommend a 600-calorie lunch that fits my allergies (peanut, dairy)."

**Pattern:** Routing (entry) + Prompt Chaining (5 sequential steps)

---

## Workflow Overview

This workflow answers "what should I eat?" questions. It's **deterministic** — we know the steps upfront.

```
User Input
    ↓
Step 1: Extract Constraints (Haiku)
    ├─ calorie_target: 600
    ├─ allergies: [peanut, dairy]
    ├─ preferences: [weight-loss, quick]
    └─ meal_type: lunch
    ↓
Step 2: Search RAG (deterministic, no LLM)
    ├─ Query: "weight loss lunch 600 cal no peanut dairy"
    ├─ Hybrid search (BM25 + vector)
    └─ Return top 10 candidates
    ↓
Step 3: Generate Candidate Menus (Sonnet)
    ├─ Input: constraints + top 10 foods
    ├─ Output: 3 diverse menu options
    └─ Each: dish + serving + calories
    ↓
Step 4: Validate Against Constraints (Opus)
    ├─ Check: calories in range?
    ├─ Check: allergies absent?
    ├─ Check: preferences met?
    └─ Output: validation + confidence score
    ↓
Step 5: Rank & Explain (Sonnet)
    ├─ Input: validated menus
    ├─ Output: top choice + why + alternatives
    └─ Include: nutrition breakdown + prep instructions
    ↓
User Gets: Recommendation + explanation
```

---

## Step-by-Step Design

### Step 1: Extract Constraints (Model: Haiku)

**Purpose:** Parse unstructured user input into structured requirements.

**Input:**
```
User: "I'm on a weight-loss diet; recommend a 600-calorie lunch that fits my allergies (peanut, dairy)."
```

**Prompt:**
```
You are a dietary requirements parser. Extract constraints from the user request.

Return ONLY valid JSON (no markdown):
{
  "calorie_target": <int>,
  "calorie_tolerance": <int>,
  "allergies": [<string>, ...],
  "restrictions": [<string>, ...],
  "preferences": [<string>, ...],
  "meal_type": <string>
}

User request: "{user_input}"
```

**Output Example:**
```json
{
  "calorie_target": 600,
  "calorie_tolerance": 50,
  "allergies": ["peanut", "dairy"],
  "restrictions": [],
  "preferences": ["weight-loss", "quick"],
  "meal_type": "lunch"
}
```

**Why Haiku?**
- Simple classification task (extract and bucket)
- No creativity or deep reasoning needed
- Save cost on straightforward parsing

**Success Criteria:**
- Valid JSON output
- All constraints captured
- No hallucinations

---

### Step 2: Search RAG (No LLM needed)

**Purpose:** Retrieve foods matching constraints using deterministic search.

**Algorithm:**
1. Build BM25 query: "weight loss 600 calories lunch no peanut no dairy"
2. Vector search: embed constraints, find similar foods
3. Hybrid fusion: RRF merge BM25 + vector top results
4. Return: top 10 with full nutrition data

**Why No LLM?**
- Deterministic retrieval is faster and cheaper
- Constraints can be enforced perfectly via SQL/vector filters
- No need for LLM flexibility here

**Output:**
```json
[
  {
    "food_name": "Grilled Chicken Breast",
    "calories": 165,
    "protein_g": 31,
    "carbs_g": 0,
    "fat_g": 3.6,
    "allergens": [],
    "prep_time_min": 15
  },
  ...
]
```

---

### Step 3: Generate Candidate Menus (Model: Sonnet)

**Purpose:** Create 3 diverse, appealing meal recommendations from the candidate foods.

**Input:**
- Constraints (from Step 1)
- Top 10 candidates (from Step 2)

**Prompt:**
```
You are a meal recommendation specialist. Given dietary constraints and candidate foods,
generate 3 diverse lunch menus.

Constraints:
- Calorie target: 600 ± 50
- Allergies: {{allergies}}
- Preferences: {{preferences}}

Available foods:
{{candidates_json}}

Generate 3 menus. Each should:
1. Total 550–650 calories
2. Include main + side + beverage (or logical combination)
3. Be diverse (different cuisines)
4. Use ONLY foods from the list

Return ONLY valid JSON array (no markdown):
[
  {
    "menu_name": <string>,
    "dishes": [
      {"food": <string>, "serving_size": <string>, "calories": <int>}
    ],
    "total_calories": <int>,
    "prep_time_minutes": <int>,
    "appeal_reason": <string>
  }
]
```

**Output Example:**
```json
[
  {
    "menu_name": "Asian Stir-Fry Bowl",
    "dishes": [
      {"food": "Brown Rice", "serving_size": "0.5 cup", "calories": 110},
      {"food": "Grilled Chicken Breast", "serving_size": "4 oz", "calories": 160},
      {"food": "Mixed Vegetables", "serving_size": "2 cups", "calories": 150},
      {"food": "Sesame Oil", "serving_size": "1 tbsp", "calories": 120}
    ],
    "total_calories": 540,
    "prep_time_minutes": 20,
    "appeal_reason": "Lean protein, high volume for satiety"
  },
  {...},
  {...}
]
```

**Why Sonnet?**
- Needs creativity (3 diverse, appealing menus)
- Needs reasoning (calorie math, nutrition balance)
- Good speed/quality balance

**Success Criteria:**
- 3 menus generated
- Each within calorie range
- Diverse cuisines
- Valid JSON

---

### Step 4: Validate Against Constraints (Model: Opus)

**Purpose:** Verify each menu meets constraints. **Safety-critical** — allergies especially.

**Input:**
- Original constraints (from Step 1)
- 3 candidate menus (from Step 3)

**Prompt:**
```
You are a dietitian reviewer. Validate each menu against the user's constraints.

Constraints:
- Calorie target: {{calorie_target}} ± {{tolerance}}
- Allergies: {{allergies}}
- Preferences: {{preferences}}

Menus:
{{menus_json}}

For EACH menu, check:
1. Calories within range?
2. NO allergens present?
3. Preferences satisfied?
4. Any other concerns?

Return ONLY valid JSON:
[
  {
    "menu_name": <string>,
    "passes_validation": <bool>,
    "issues": [<string>, ...],
    "confidence_score": <float 0-1>,
    "explanation": <string>
  }
]
```

**Output Example:**
```json
[
  {
    "menu_name": "Asian Stir-Fry Bowl",
    "passes_validation": true,
    "issues": [],
    "confidence_score": 0.95,
    "explanation": "Calories 540 (target 600±50). No allergens. High vegetable volume supports satiety."
  },
  {
    "menu_name": "Greek Salad with Feta",
    "passes_validation": false,
    "issues": ["Contains dairy (feta) — user allergic to dairy"],
    "confidence_score": 0.99,
    "explanation": "FAILS: Feta cheese present. User explicitly allergic to dairy."
  }
]
```

**Why Opus?**
- Critical judgment — allergen safety is non-negotiable
- Worth the cost: wrong validation = potential allergic reaction
- Deep reasoning beats speed here

**Success Criteria:**
- All validation checks completed
- Allergies flagged correctly
- Confidence scores assigned
- Issues listed for failed menus

**Error Handling:**
If fewer than 2 menus pass validation:
- Adjust RAG search (remove problematic categories)
- Return to Step 3 (regenerate menus)
- Max 2 iterations to avoid infinite loops

---

### Step 5: Rank & Explain (Model: Sonnet)

**Purpose:** Present the best option with clear, actionable explanation.

**Input:**
- All validated menus (from Step 4)
- Confidence scores

**Prompt:**
```
The user asked for a 600-calorie weight-loss lunch. Here are the validated options:
{{validated_menus}}

Select the top recommendation. Explain:
1. Why it's best for their constraints
2. Detailed nutrition breakdown
3. How to prepare it
4. Runner-up alternative

Return ONLY valid JSON:
{
  "top_recommendation": <string>,
  "rationale": <string>,
  "nutrition_breakdown": {
    "calories": <int>,
    "protein_g": <float>,
    "carbs_g": <float>,
    "fat_g": <float>
  },
  "preparation_steps": [<string>, ...],
  "runner_up": <string>,
  "roasting_cat_commentary": <string>
}
```

**Output Example:**
```json
{
  "top_recommendation": "Asian Stir-Fry Bowl",
  "rationale": "Perfect match: exactly 540 calories (target 600±50), zero allergens, high fiber and protein for satiety on weight loss.",
  "nutrition_breakdown": {
    "calories": 540,
    "protein_g": 35,
    "carbs_g": 45,
    "fat_g": 12
  },
  "preparation_steps": [
    "Cook brown rice (20 min)",
    "Grill chicken breast (15 min)",
    "Stir-fry vegetables with sesame oil (10 min)",
    "Combine in bowl"
  ],
  "runner_up": "Mediterranean Chickpea Wrap",
  "roasting_cat_commentary": "Finally, a human with taste. This bowl screams satiety without sacrificing flavor. My whiskers approve. 🐱"
}
```

**Why Sonnet?**
- Synthesis task (combine multiple signals into clear explanation)
- Natural language generation (not critical judgment)
- Good speed/quality for user-facing explanation

**Success Criteria:**
- Top choice is clear
- Rationale is compelling
- Prep steps are actionable
- NomNom personality shines

---

## Model Assignment Summary

| Step | Task | Model | Cost Impact | Why |
|------|------|-------|-------------|-----|
| 1 | Extract constraints | Haiku | Low | Simple classification |
| 2 | Search RAG | — | None | Deterministic, no LLM |
| 3 | Generate menus | Sonnet | Medium | Creativity + reasoning |
| 4 | Validate (safety-critical) | Opus | High | Deep judgment, allergen safety |
| 5 | Rank & explain | Sonnet | Medium | Synthesis + naturalness |
| **Total** | | | **~$0.008/request** | Haiku + 2×Sonnet + 1×Opus |

---

## Error Handling

**If Step 3 returns invalid JSON:**
- Re-run with stricter prompt
- Use tool_choice to force structured output if needed
- Max 2 retries, then return error

**If Step 4: fewer than 2 menus pass:**
- Adjust Step 2 RAG search (exclude problematic food categories)
- Return to Step 3 (regenerate with new candidates)
- Max 2 iterations of the loop

**If user constraints are impossible:**
- Detect in Step 4: "No foods match these constraints"
- Return to user: "Your constraint (e.g., 200 cal + high protein) is impossible for a full meal. Try relaxing X."

---

## Integration Point: NomNom API

**Endpoint:** `POST /api/recommendations/meal`

**Request:**
```json
{
  "user_input": "I'm on a weight-loss diet; recommend a 600-calorie lunch that fits my allergies (peanut, dairy).",
  "user_id": 42
}
```

**Response:**
```json
{
  "top_recommendation": "Asian Stir-Fry Bowl",
  "rationale": "Perfect match: exactly 540 calories, zero allergens, high protein for satiety.",
  "nutrition_breakdown": { ... },
  "preparation_steps": [ ... ],
  "runner_up": "Mediterranean Chickpea Wrap",
  "roasting_cat_commentary": "Finally, a human with taste. This bowl has my whisker-wiggling approval. 🐱"
}
```

**Cost Logging:**
- Log each step's cost separately
- Step 1 cost (Haiku extraction)
- Step 3 cost (Sonnet generation)
- Step 4 cost (Opus validation)
- Step 5 cost (Sonnet ranking)
- Total cost per request

---

## Design Decisions & Rationale

**Q: Why is this a workflow and not an agent?**

A: Steps are predetermined. Extract → Search → Generate → Validate → Rank. Claude doesn't need to decide the order or what to do next. If the task were "I have ingredients, make something," that would be an agent (unpredictable path).

**Q: Why Haiku for Step 1 but Opus for Step 4?**

A: Different stakes. Step 1 is mechanical extraction — Haiku is fine. Step 4 is safety-critical (allergies) — Opus's deeper judgment is worth the cost.

**Q: Why not use one LLM call to do all 5 steps?**

A: **Control and cost.** Breaking into steps lets us:
- Use cheap models (Haiku) where they work
- Use expensive models (Opus) only for critical judgment
- Inspect and debug each step independently
- Reuse steps (e.g., validate step can be reused for other workflows)

**Q: What if Step 3 generates menus but Step 4 rejects them all?**

A: We loop. Adjust RAG search to exclude problematic categories, regenerate menus. Max 2 iterations prevents infinite loops. If still failing after 2 loops, return "no valid options" to user.

**Q: Why deterministic search instead of LLM retrieval?**

A: Speed and cost. "Find foods with < 600 calories, no peanut, no dairy" is a perfect constraint-enforcement task. LLM adds no value, just latency and cost.

---

## Interview Talking Points

**Q: Walk through your meal recommendation workflow.**

A: [Describe the 5 steps above, emphasizing why each step uses its model and why we break into steps.]

**Q: How do you handle the case where validation fails?**

A: We loop. If fewer than 2 menus pass validation, we adjust the RAG search (e.g., "exclude Greek salads"), regenerate menus, and re-validate. Max 2 iterations to prevent infinite loops. If still failing, we return "no valid options found; try relaxing constraints."

**Q: Why didn't you use an agent here?**

A: Steps are predetermined. Extract → Search → Generate → Validate → Rank. The order doesn't change based on intermediate results. An agent would add complexity without benefit. If the task were more open-ended ("I have these ingredients, create something"), I'd use an agent.

---

**Status:** ✅ Day 2 Complete  
**Next:** Day 3 — Implement this workflow in code
