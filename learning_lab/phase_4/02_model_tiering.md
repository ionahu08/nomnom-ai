# Phase 4 Day 1 (Afternoon): Model Tiering Decision Framework

**Goal:** Write the rationale for NomNom's task → model mapping.  
**Why this matters:** Choosing the wrong model = 5–20× cost difference with no quality benefit.  
A junior LLM engineer picks Opus by default. A senior picks the *cheapest model that's good enough*.

===============================================================================
LEARNING Q&A — Test Your Understanding
===============================================================================

Q1: Summarize nutritional content of a food photo. Use Haiku or Sonnet? Why?
A1: Sonnet. Involves two YES answers: (1) multimodal data (photo) requires vision,
    (2) summary requires reasoning (understanding ingredients, portion, nutrition).
    Haiku fails on both. Sonnet is required.

Q2: Why is ANALYZE_FOOD currently assigned to Haiku a BUG? Use the 3 questions.
A2: Three decision questions all point to Sonnet:
    (1) Requires vision? YES (food photo) → Sonnet/Opus required
    (2) Requires reasoning? YES (analyze, judge portion/ingredients) → Sonnet/Opus
    (3) Structurally simple? NO (not a schema fill)
    Result: Questions 1 & 2 are YES → Sonnet needed, not Haiku.

Q3: Why use Opus for eval grader when it runs offline? Doesn't latency matter?
A3: Correct — latency doesn't matter for offline/batch work. That's the point!
    When users aren't waiting, prioritize quality over speed. Eval grader needs
    deep judgment to catch subtle hallucinations. Worth the slow speed + high cost
    because accuracy matters more than latency.

Q4: Cost difference: Haiku $43/month vs Sonnet $162/month ($120/month delta).
    Why is this extra $120/month justified for ANALYZE_FOOD?
A4: Business ROI calculation:
    - Haiku's weak vision → wrong calorie estimates
    - Wrong calories → users lose trust → churn
    - Cost of losing one user (lifetime value) >> $120/month
    - So $120/month is cheap insurance against churn & trust loss
    This is about protecting the product's core promise (accurate nutrition),
    not just optimizing cost.

Q5: Why use Haiku for test dataset generation, not Sonnet?
A5: Three reasons:
    (1) Structurally simple task (enumeration, list-making, not judgment)
    (2) Haiku output is "diverse enough" for eval purposes — you need varied
        examples, not high-quality judgment
    (3) Cost savings: ~20× cheaper than Sonnet with no quality loss for this use
    Key insight: quality bar matters — this task doesn't need Sonnet quality.

KEY TAKEAWAY:
Model selection = Technical requirements (vision? reasoning?) + Cost-benefit
analysis (what's the ROI?) + Quality bar per task (how good does it need to be?).

===============================================================================

## The Decision Framework

Before assigning a model, answer three questions:

1. **Does this task require vision/multimodal?** → Needs Sonnet or above
2. **Does this task require deep reasoning or judgment?** → Needs Sonnet or Opus
3. **Is the task structurally simple (schema fill, extraction, formatting)?** → Haiku is fine

If the answer to all three is "no, no, yes" → Haiku.  
If the answer includes "yes" to #1 or #2 → Sonnet.  
If the task is a high-stakes evaluation or complex advice → Opus.

---

## NomNom Task → Model Decision Table

| Task | Model | Why |
|---|---|---|
| Food image recognition | **Sonnet** | Multimodal input requires vision capability. Haiku's visual reasoning is weaker on ambiguous dishes, mixed plates, unusual angles. Accuracy here directly affects user trust — a wrong calorie estimate is worse than a slow response. |
| JSON structure extraction | **Haiku** | Input is already structured text (parsed food name). Output is a fixed schema. No reasoning required. Haiku handles this perfectly and costs ~20× less than Opus. |
| Nutrition knowledge RAG answer | **Sonnet** | Must synthesize retrieved chunks from USDA knowledge base + user context into a coherent, nutritionally accurate answer. Requires reasoning across multiple sources. Haiku misses nuance (e.g., bioavailability, cooking method impact). |
| Complex dietary advice (v3+) | **Opus** | High-stakes personalized guidance (allergy interaction, medical diet constraints). Wrong advice has real harm potential. Opus's deeper reasoning is worth the cost for users who've opted into this feature. |
| Eval grader | **Opus** | LLM-as-judge requires deep judgment: understanding nuance in nutrition claims, evaluating calibration of confidence levels, spotting subtle hallucinations. This runs offline — cost matters less than quality. |
| Test dataset generation | **Haiku** | Generate 30 challenging food descriptions for eval. The task is creative enumeration, not quality judgment. Haiku is fast and diverse enough. Saves ~20× vs. Sonnet for large batch generation. |

---

## Current NomNom Router vs. This Table

**`NomNom-Backend/src/llm/router.py` current assignments:**

| TaskType | Assigned Model | Correct? |
|---|---|---|
| `ANALYZE_FOOD` | **Haiku** | ❌ Food image analysis needs vision → **should be Sonnet** |
| `RECOMMEND_MEAL` | Sonnet | ✅ RAG synthesis = reasoning required |
| `WEEKLY_RECAP` | Sonnet | ✅ Multi-day pattern synthesis |

**Day 5 fix:** change `ANALYZE_FOOD` primary model from `claude-haiku-4-5` to `claude-sonnet-4-5`.

---

## When to Upgrade vs. Downgrade

**Upgrade (→ more powerful model) when:**
- Task involves multimodal input
- Output affects user health/safety decisions
- Task requires synthesizing multiple sources
- Eval/grading that requires deep judgment

**Downgrade (→ cheaper model) when:**
- Input is already structured text
- Output is a fixed schema fill
- Task runs in batch (not user-facing latency)
- You can verify correctness cheaply (code-based grader)

---

## Cost Reference (per 1M tokens, as of 2025)

| Model | Input | Output | Cache Read |
|---|---|---|---|
| claude-haiku-4-5 | $0.80 | $4.00 | $0.08 |
| claude-sonnet-4-5 | $3.00 | $15.00 | $0.30 |
| claude-opus-4-7 | $15.00 | $75.00 | $1.50 |

**Sonnet costs ~4× more than Haiku per input token.**  
**Opus costs ~5× more than Sonnet per input token.**

For `ANALYZE_FOOD` — a typical request is ~800 input tokens + ~200 output tokens:
- Haiku:  $0.80×0.0008 + $4.00×0.0002 = **$0.00144**
- Sonnet: $3.00×0.0008 + $15.00×0.0002 = **$0.00540**

At 1,000 requests/day: Haiku = $1.44/day, Sonnet = $5.40/day.  
**Question:** Is the vision quality improvement worth $3.96/day?  
**Answer:** Yes, because misidentified food = bad calorie counts = user churn.

---

## Interview Answer: "Why did you pick Haiku for X?"

Bad: "It's cheaper."

Good: "I mapped each NomNom task to the cheapest model that preserves accuracy for that task's quality bar. JSON extraction from pre-parsed text is structurally simple — Haiku handles it perfectly, and the output is machine-verified by our guardrails layer anyway. Image recognition, by contrast, directly affects calorie accuracy which is the product's core promise, so Sonnet's multimodal capability is worth the 4× cost premium there."

---

## Next Steps

- Day 3: Review `router.py` — verify assignments against this table
- Day 5: Fix `ANALYZE_FOOD` routing to Sonnet, document the change with this rationale
