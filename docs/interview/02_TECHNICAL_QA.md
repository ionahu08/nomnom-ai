# Technical Deep Dive: Questions, Decisions & Evidence

**Your complete guide to answering technical questions, telling decision stories, and explaining design choices.**

This document contains:
- **5 Core Talking Points** (2-3 min each) — Foundational stories you'll reference repeatedly
- **18 Technical Decision Stories** (3-5 min each) — Organized by phase, use as interview anecdotes
- **22 Technical Q&As** (2-3 min each) — Organized by layer, answer expected questions
- **Quick Reference** — Key metrics, red flags, rapid-fire answers

---

## SECTION A: 5 Core Talking Points

These are your go-to stories. Master these first. You'll reference them in almost every interview.

### **Talking Point 1: Semantic Caching & Threshold Tuning (0.82)**

**When they ask:** "Walk me through your caching approach" / "Why 0.82? Seems arbitrary."

**Your answer:**

"The problem: food items aren't identical. 'Salmon bowl,' 'salmon with rice,' 'salmon & vegetables' are different dishes but nutritionally similar. Redis with exact matching has 15% hit rate—useless.

I needed semantic similarity. So I embedded meal photos, stored embeddings in pgvector, and searched by cosine similarity.

**But what threshold?** Not arbitrary. Empirical.

**The process:**
1. Created dataset of 150 real meal photos (variety: sushi, pizza, salads, bowls)
2. Manually labeled semantic duplicates
3. Tested thresholds: 0.70, 0.75, 0.80, 0.82, 0.85, 0.90, 0.95
4. Measured hit rate and false positives for each

**Results:**
- 0.95: 40% hit rate (too strict)
- 0.82: 85% hit rate, <1% false positives (sweet spot)
- 0.70: 95% hit rate, 8% false positives (too loose)

**Why 0.82?** Captures 90% of duplicates with only 5% false positives. False negative (cache miss) costs extra API call. False positive (wrong answer) breaks trust. Asymmetric cost, so I accepted slightly more false positives to get real cache benefit.

**Production result:** 85% hit rate, 60% cost reduction, $10/day savings per thousand users.

**Interview signal:** I didn't guess. I measured on real data and chose based on tradeoffs."

**Time:** 2–3 minutes

---

### **Talking Point 2: Cost Spike After Optimization**

**When they ask:** "Your costs went UP after switching to Sonnet. Walk me through that."

**Your answer:**

"Right. This is a good example of optimizing one variable in isolation and breaking something else.

**The setup:** Opus cost $0.12/request. Sonnet is $0.04/request (70% cheaper). I switched expecting daily costs to drop from $12 → $4.

**What actually happened:** Daily costs went to $10. Why?

I diagnosed by tracking three metrics:
1. **Cost per request:** $0.12 → $0.04 ✓ (as expected)
2. **Daily traffic:** 100 requests → 250 requests (unexpected)
3. **Accuracy:** 98% → 96% (acceptable 2% drop)

**Root causes:**
- Faster response time (Sonnet is 3x faster) → improved UX → more user engagement → higher volume
- Slightly lower accuracy → more follow-up calls for clarification

**The decision:** I could revert to Opus. But I chose to keep Sonnet because:
1. Per-request cost is the fundamental metric that scales (Sonnet will always be cheaper at scale)
2. The volume increase isn't a bug—it's a feature (faster response = better UX)
3. Semantic caching would fix the volume problem

**What I did:** Added rate limiting (20 requests/user/day) + monitoring (alert if daily cost > $15) + semantic caching.

**Final result:** With Sonnet + semantic caching, daily cost is now $2 (83% savings). Better than reverting to Opus would have been.

**Lesson:** Don't optimize for one variable in isolation. Cost + latency + quality are coupled. Measure holistically."

**Time:** 2–3 minutes

---

### **Talking Point 3: Local Optimization Breaking Things**

**When they ask:** "Tell me about a time when optimization backfired" / "Give me an example of a decision that had unintended consequences."

**Your answer:**

"The semantic caching threshold is a perfect example.

**Initial approach:** I set threshold at 0.95 (high confidence in similarity, avoid false positives). Seemed safe.

**The problem:** Cache hit rate was only 40%. Not good enough.

**Why?** I manually reviewed failed cache lookups. Found:
- User photographed 'salmon with rice' (stored in cache)
- User photographed 'salmon bowl' (no rice, more vegetables)
- Embeddings differed enough to score 0.87 (below 0.95 threshold)
- Cache miss → full API call → cost

But nutritionally, they're almost identical. Both are salmon + carbs + fiber.

**The fix:** Lower the threshold to 0.82.

But lowering threshold risks false positives: what if I cache 'salmon' for 'chicken'? That's a real bug.

**How I validated it:**
- Tested 150 real meal photos
- Measured precision/recall at each threshold
- Manually reviewed borderline cases (50 pairs)
- Added regression test: `test_semantic_cache_threshold_tuning`

**The learning:** There are no free lunches. Lower threshold = more hits but more noise. Higher threshold = fewer hits but higher precision. You have to measure and choose based on your domain.

For food, 85% hit rate with 1% false positives is acceptable. For medicine or finance, you'd want 99% precision even if it meant lower recall."

**Time:** 2–3 minutes

---

### **Talking Point 4: Orchestrator-Workers Pattern & Latency Reduction**

**When they ask:** "How did you achieve 67% latency reduction?" / "Tell me about the orchestrator-worker pattern."

**Your answer:**

"This pattern parallelizes independent tasks. Reduced latency from 60s → 25s (67% improvement).

**Sequential version (v1):**
```
User uploads photo
  ↓ Claude analyzes photo (2s)
  ↓ RAG retrieves context (1s)
  ↓ Claude generates recommendations (2s)
  ↓ Log cost & metrics (0.5s)
Total: 5.5s
```

**Parallel version (v2) with orchestrator-workers:**
```
User uploads photo
  ├─ Worker 1: Claude analyzes photo (2s)
  ├─ Worker 2: RAG retrieves context (1s)
  ├─ Worker 3: Log cost & metrics (0.5s)
  └─ All complete in: 2s (bottleneck)
Orchestrator: Gather results, format response (0.5s)
Total: 2.5s
```

**Why this works:** Workers are independent (don't need results from each other). Bottleneck is longest task (photo analysis, 2s). Other workers finish before bottleneck (no idle time).

**Implementation:**
```python
async def orchestrate(photo):
    # Launch 3 workers in parallel
    analysis_task = asyncio.create_task(worker_analyze_photo(photo))
    rag_task = asyncio.create_task(worker_retrieve_context(user_id))
    cost_task = asyncio.create_task(worker_track_cost(user_id, model))
    
    # Wait for all to complete
    analysis, context, cost = await asyncio.gather(
        analysis_task, rag_task, cost_task
    )
    
    # Orchestrator: combine results
    recommendation = claude.generate_recommendation(analysis, context)
    return recommendation
```

**Tradeoffs:**
- Slightly more complex (asyncio, error handling)
- Harder to debug (three things running at once)
- Worth it: 2.5x faster response

**Real-world result:**
- v1 (sequential): 60s average
- v2 (orchestrated): 25s average
- Measured on 100+ real requests

**Interview signal:** This isn't micro-optimization. 60s → 25s is the difference between 'user abandoned the app' and 'user engaged.'"

**Time:** 2–3 minutes

---

### **Talking Point 5: LLM Engineering Surprises**

**When they ask:** "What surprised you about LLM engineering?" / "What would you do differently?"

**Your answer:**

"Three surprises:

**Surprise 1: Prompts are product assets, not code**

I expected LLM engineering to be 80% prompt, 20% architecture. It's the opposite. Prompts change 10x more frequently than code. You need versioning, testing, A/B evaluation for prompts like you do for features.

What I'd do: Build a prompt testing framework from day one. Track versions, measure quality metrics, iterate quickly. Currently I have `prompt_engine.py` that handles templating, but I'd add a full eval pipeline earlier.

**Surprise 2: Output validation prevents 30% of bugs**

I expected hallucinations and reasoning errors to dominate. But 30% of bugs were actually parsing/schema mismatches. User asks 'what should I eat?' → Claude returns random JSON → code crashes.

What I'd do: Implement structured output validation before any other optimization. Use Pydantic schemas, add guardrails, reject malformed outputs early. I did this in Phase 2, but I'd start with it, not add it later.

**Surprise 3: Orchestration patterns scale way better than single agents**

I expected agent loops to be 'good enough.' But orchestrator-worker parallelization (3 workers in parallel) reduced latency from 60s to 25s (67% improvement). That's not micro-optimization—it's fundamental.

What I'd do: Model your workload as a DAG (directed acyclic graph) from the start. Identify independent tasks and parallelize them. Don't serialize just because it's simpler.

**Bonus surprise: Cheaper models + smart caching beats expensive models**

I expected Opus would be required for 'smart' food recommendations. But Sonnet (70% cheaper) + semantic caching (85% hit rate) outperforms Opus without caching. Architecture beats raw capability.

**If I rebuilt from scratch:**
1. Start with structured output validation (Phase 2 work)
2. Build semantic caching from day one, not week 6
3. Model workload as a DAG and parallelize
4. Implement monitoring (cost, latency, quality) before features
5. Keep a prompt changelog (date, version, why changed)
6. Test on real user data earlier

**The meta-lesson:** LLM engineering is mostly architecture. The 'intelligence' part (Claude) is 10%. The hard work is caching, parallelization, validation, monitoring."

**Time:** 2–3 minutes

---

## SECTION B: 18 Technical Decision Stories

Each decision story follows: **Problem | Decision | Why This | Alternatives | Outcome**

These are ready-to-use 3–5 minute interview anecdotes. Pick 3–5 most relevant to the company.

### **Decision 1: Jinja2 Templating Over F-Strings**

Early NomNom hardcoded prompts in Python strings. When we wanted to A/B test different prompt phrasings, we had to edit code, redeploy, and re-test. Product iteration was blocked by engineering cycles.

**Decision:** Implement Jinja2-based prompt templating. Prompts live in separate `.j2` files. Variables injected at runtime.

**Why:** Prompts are product assets, not infrastructure code. Enables non-engineers (PMs) to iterate without touching Python. Prompt changes tracked separately from code.

**Alternatives considered:**
- F-strings: Simplest, but tight coupling. Every prompt change requires code review + redeploy.
- Python string templates: Middle ground, less readable than Jinja2.
- Database-backed prompts: More flexible, but adds latency + operational complexity.

**Outcome:** Prompt iteration time 2 hours → 10 minutes. Code churn reduced 80%.

---

### **Decision 2: Exponential Backoff in Retry Logic**

Sonnet calls sometimes fail transiently (rate limits, brief API outages). Hard-coded retries without backoff hammered the API, worsening the problem.

**Decision:** Implement exponential backoff (1s, then 2s, then fail) in `client.py`.

**Why:** Gives Claude API time to recover. Respects the API. Exponential growth ensures we're not retrying too aggressively.

**Alternatives:**
- No retry: Users see every transient failure (bad UX)
- Constant backoff (1s each): Doesn't address congestion
- Exponential capped at 4s+: Overkill for this use case

**Outcome:** 85% of transient failures recovered without user seeing error. User-facing errors reduced 40% during maintenance.

---

### **Decision 3: Model Choice — Sonnet Over Haiku/Opus**

Which Claude model for food image recognition?
- Haiku: Fast, cheap, but misses multi-ingredient dishes (60% fail rate)
- Sonnet: Balanced cost/quality, strong on multimodal
- Opus: Best quality, but $3–4 per request (unsustainable)

**Decision:** Sonnet for food recognition. Haiku for JSON extraction. Opus for eval (rare).

**Why:** Food recognition is core value prop. One wrong nutrition estimate erodes trust permanently. Cost: Sonnet ($0.0015/request) × 1k users × 20 requests/day = $30/day (sustainable).

**Tradeoff:** 40% accuracy improvement (Haiku 72% → Sonnet 88%) justifies 5x cost increase for health data.

**Outcome:** 88% accuracy maintained. Monthly API cost sustainable ($20/month).

---

### **Decision 4: tool_choice For Structured Output**

Phase 1 used prefill+stop (manually inject ` ```json `, stop on ` ``` `). Fragile: 2.8% of calls produce unparseable JSON.

**Decision:** Migrate to `tool_choice="force"` with strict JSON schema.

**Why:** Schema enforcement. Claude must output exactly the defined structure. Error clarity—tool validation happens before user sees it.

**Alternatives:**
- Prefill+stop (status quo): Works but fragile; 2–3% failures
- Regex validation: Silent failures; user gets wrong nutrition data
- LLM re-trying on fail: Adds latency, costs double

**Outcome:** JSON parse success 97.2% → 100%. User trust: "Nutrition data is always valid."

---

### **Decision 5: Hybrid Grading (Code + Model)**

How to grade food recognition accuracy?
- Code-only: Fast, cheap, but misses semantic errors ("apple" vs. "apricot")
- Model-only: Expensive ($0.01 per grade) × 30 test cases = $0.30 per eval run

**Decision:** Hybrid eval: Code grader (fast, cheap) + Model grader (Opus, on sample). Combined score: `(code_score × 0.3) + (model_score × 0.7)`.

**Why:** Cost efficiency. 90% of evals caught by code grading; only 10% sampled with expensive model grading. Accuracy: model grader catches semantic errors code can't.

**Outcome:** Eval latency 45s → 8s. Eval cost $0.30 → $0.04 per run. Detection rate: 93% on test set.

---

### **Decision 6: Claude-Readable Error Messages**

When food recognition fails (blurry photo), error was: `"JSON_VALIDATION_ERROR: missing field 'calories'"`. Claude has no idea how to fix it. Loops infinitely.

**Decision:** Rewrite error messages for Claude as the reader.

**Example:**
```
OLD: "Invalid JSON: missing field 'calories'"
NEW: "The food recognition failed because the image is too blurry. 
      Please ask the user to retake the photo with better lighting."
```

**Why:** Claude reads error, understands root cause, can self-correct. Error becomes actionable feedback, not just a code.

**Outcome:** Error recovery rate 40% → 85%. Mean time to resolution: 4 retries → 1.2 retries.

---

### **Decision 7: MiniLM-L6-v2 For Embeddings**

Which embedding model?
- OpenAI text-embedding-3-large: 3072-dim, highest quality, $0.13 per 1M tokens
- MiniLM-L6-v2: 384-dim, 50x cheaper, 95% quality of OpenAI
- BGE-base: 768-dim, balance of cost/quality

**Decision:** MiniLM-L6-v2.

**Why:** Cost ($0 open-source vs. $0.13 per 1M tokens). Quality: 384-dim captures nutrition semantics well. Latency: 8x faster vector operations. Control: run locally; no vendor lock-in.

**Outcome:** Embedding latency 2ms. Search latency 15ms (vs. 120ms with 3072-dim). Cost: $0 (local) vs. $50/month at 1k users.

---

### **Decision 8: Cosine Similarity 0.82 Threshold**

(See Talking Point 1 above for full explanation)

**Short version:** Tested 0.70–0.95 on 150 real meal photos. Found 0.82 captures 90% of duplicates with 5% false positives. Not arbitrary—measured.

**Outcome:** Cache hit rate 85%, cost savings 60%.

---

### **Decision 9: Hybrid Search (BM25 + Vector + RRF)**

Pure vector search fails on exact matches ("USDA food database entry 01234"). Pure BM25 misses synonyms ("meal replacement shake" vs. "nutritional beverage").

**Decision:** Hybrid search: BM25 index + Vector index + RRF (Reciprocal Rank Fusion).

**Why:** Best of both. Exact matches handled by BM25, semantic by vector. RRF is a RecSys pattern I brought from my background.

**Outcome:** Recall improved from 78% (vector) / 82% (BM25) to 91% (hybrid).

---

### **Decision 10: Contextual Retrieval For RAG Chunks**

Nutrition database chunks are short ("Apple: 52 cal, 13g carbs"). When retrieved in isolation, ambiguous. Per 100g? Per apple?

**Decision:** Add context via LLM before embedding.

**Example:**
```
OLD: "Apple: 52 cal, 13g carbs"
NEW: "A medium apple (182g) provides 52 calories, 13g carbs. 
      Source: USDA FoodData Central."
```

**Why:** Reduces ambiguity. Improves recall (Anthropic study showed 15–20% lift). Min cost: LLM adds context once during indexing, not per search.

**Outcome:** Retrieval accuracy 82% → 94%.

---

### **Decision 11: Citations (RAG Anti-Hallucination)**

NomNom recommends "Eat an apple (50 cal, high in potassium)". Where did "high in potassium" come from? Hallucination?

**Decision:** Enable citations. Claude annotates each fact with source: "apple has potassium [apple_nutrition_005.pdf:page 3]"

**Why:** Builds trust. Users can verify claims. Essential for health data (legal requirement in some jurisdictions).

**Outcome:** User trust score 3.2/5 → 4.6/5. Support questions reduced 80%.

---

### **Decision 12: Model Tiering By Task Type**

Calling Claude for everything costs $1.50/user/day (unsustainable for free app).

**Decision:** Tiering by task:
- Food image recognition → Sonnet ($0.0015/req)
- JSON extraction → Haiku ($0.0001/req, already validated)
- Meal recommendation → Sonnet ($0.0015/req)
- Eval grading → Opus ($0.01/req, rare)

**Why:** Cost optimization where it matters. Food recognition accuracy critical (keep Sonnet). JSON already schema-validated (use cheap Haiku).

**Outcome:** Daily cost per user $1.50 → $0.35 (4.3x reduction). Accuracy maintained at 88%.

---

### **Decision 13: Prompt Caching For System Prompts**

Every food analysis call sends same system prompt (400 tokens). That's 72,400 tokens/hour, all redundant.

**Decision:** Prompt caching: Mark system prompt as `cache_control: {"type": "ephemeral"}`. Cache for 1 hour.

**Why:** First call pays full cost; subsequent calls (within 1 hour) pay 90% less. Math: 72,400 tokens uncached → 7,600 tokens cached (89% savings).

**Outcome:** $50/month savings per 1k users.

---

### **Decision 14: Cost Tracking & Dashboard**

No visibility into spend. "Can we afford 1k users?" was a guess.

**Decision:** Structured logging in `logger.py`. Per-call: tokens, latency, model, cost. Dashboard: daily spend, cost by feature, P95 latency.

**Why:** Business insight. Data-driven decisions. Discovered: RAG accounts for 60% of spend. That insight guided Phase 3 optimization.

**Outcome:** Full cost visibility. Caught Sonnet cost spike early (diagnosed root cause: behavioral, not technical).

---

### **Decision 15: Workflow For Meal Recommendation (Not Single Agent)**

User: "Recommend 600-cal lunch for weight-loss diet."

Could use:
- Single agent: Flexible, Claude decides order
- Workflow: Fixed steps, deterministic

**Decision:** Workflow. Steps known upfront: Extract constraints → RAG retrieve → Evaluate options → Rank.

**Why:** Predictable, testable, debuggable. Cost: no self-loop. When recommendation is wrong, I know which step failed.

**Outcome:** Latency 4.2s (agent) → 2.1s (workflow). Cost $0.008 → $0.004.

---

### **Decision 16: Orchestrator-Workers For Weekly Planning**

(See Talking Point 4 above for full explanation)

**Short version:** 7 days × 3 meals = 21 calls. Sequential: 60s. Parallel (orchestrator-workers): 18s.

**Outcome:** 3.3x latency improvement, same cost.

---

### **Decision 17: MCP Server (Not Just REST API)**

NomNom is useful, but trapped in iOS + REST API. High friction for other tools.

**Decision:** Build MCP (Model Context Protocol) server. Anthropic's standard protocol for LLM tool exposure.

**Why:** Standardization. Claude, other LLMs speak MCP natively. Ecosystem play: NomNom becomes a service, not just an app.

**Outcome:** Time to integrate NomNom into Claude Code: 30min (REST) → 2min (MCP).

---

### **Decision 18: MCP Tools vs. Resources Distinction**

MCP offers tools (reactive: Claude decides when) and resources (proactive: client reads directly).

**Decision:**
- Tools: `analyze_food_image`, `lookup_nutrition`, `recommend_meal` (Claude initiates)
- Resources: `nomnom://foods/{id}`, `nomnom://history` (client reads)

**Why:** Clarity. Resources avoid unnecessary LLM calls. Developers know which to use.

**Outcome:** Clear mental model of "reactive" vs. "proactive."

---

## SECTION C: 22 Technical Q&As

Organized by layer. Each answer is 2–3 minutes of talking.

### **Q1: How do you handle transient failures in LLM API calls?**

Implement exponential backoff with small retry count (2–3). Wait 1s, then 2s, then fail. Don't hammer the API during outages.

**Evidence:** In Phase 1, I built `client.py` with exponential backoff. Result: 85% of transient failures recovered without user seeing error.

**Why it matters:** Retry logic is the difference between "feels like an outage" and "briefly slow."

---

### **Q2: How do you optimize LLM costs without sacrificing quality?**

Don't optimize blindly. Measure where money goes, then decide what to sacrifice. Use model tiering: cheap for simple tasks, expensive for high-stakes.

**Evidence:** Phase 4: Model tiering. Haiku for JSON ($0.0001/req), Sonnet for images ($0.0015/req), Opus for eval (rare). Result: 4.3x cost reduction, 88% accuracy maintained.

**Why it matters:** Costs are first-class constraint. At 1k users, $1.50/day = $45k/month (unsustainable).

---

### **Q3: Tell me about prompt caching. When does it help?**

Reuses expensive static content (system prompts, tool schemas). First call pays full cost; next 180 calls (1-hour TTL) pay 90% less per cached token. Helps when: same system prompt × many requests.

**Evidence:** Phase 4: System prompt (400 tokens) × 181 calls/hour. Uncached: 72,400 tokens/hour. Cached: 7,600 tokens/hour (89% savings = $50/month per 1k users).

**When it doesn't help:** System prompt changes frequently (more than hourly). Entire cache invalidates.

---

### **Q4: How do you track LLM costs?**

Log per-call: tokens (input, output, cache-read), latency, model, cost. Query to answer "Which feature costs most?" and "Can we afford N users?"

**Evidence:** Phase 4: Built cost dashboard. Discovery: RAG accounts for 60% of spend. This data-driven insight led to Phase 3 optimization.

**Why it matters:** Without visibility, "Are we profitable?" is a guess.

---

### **Q5: How do you design prompts for iteration?**

Separate prompts from code. Use templating (Jinja2). Version-control prompts independently. Non-engineers can iterate without touching Python.

**Evidence:** Phase 1: Jinja2 templating. Prompt iteration time 2 hours → 10 minutes. Code churn reduced 80%.

**Why it matters:** Prompts change 10x more frequently than code.

---

### **Q6: How do you handle ambiguous or malformed user input?**

Design error messages for Claude to read, not humans. Tell Claude what's wrong and how to fix it. Enables self-correction.

**Evidence:** Phase 2: Blurry photo. Old error: "JSON_VALIDATION_ERROR: missing field 'calories'". New error: "Image is too blurry. Ask user to retake with better lighting." Result: Error recovery 40% → 85%.

**Why it matters:** Error messages are part of the control loop.

---

### **Q7: Prefill+stop vs. tool_choice—when to use each?**

Prefill+stop is simple but fragile (prompt injection, hallucination). tool_choice enforces schema strictly. Use tool_choice when correctness matters.

**Evidence:** Phase 2: Migrated to tool_choice. JSON parse success 97.2% → 100%. No prompt injection vulnerabilities.

**Tradeoff:** tool_choice slightly slower, but worth it for health data.

---

### **Q8: How do you tune a semantic cache threshold?**

Measure empirically. Collect 100+ real requests, manually label semantic duplicates, plot cosine similarity, find sweet spot.

**Evidence:** Phase 3: Tested 0.70–0.95 on 150 real meals. Found 0.82 captures 90% of duplicates with 5% false positives.

**Why guessing fails:** Without data, I'd have guessed 0.95 (conservative). That leaves 40% cache misses. With measurement, captured 90% of value with 5% risk.

---

### **Q9: Vector search vs. BM25 vs. hybrid—which one?**

Hybrid (vector + BM25 + RRF). Vector catches synonyms; BM25 catches exact matches. Each alone fails 20–30% of the time. Combined: 91% recall.

**Evidence:** Phase 3: Recall@5: Vector 78% → BM25 82% → Hybrid 91%. Precision@1: Vector 60% → BM25 55% → Hybrid 75%.

**Why RRF?** It's a RecSys pattern. Parameter-free (no tuning needed).

---

### **Q10: How do you structure RAG knowledge?**

Chunk by meaning, not size. Add context before embedding ("A medium apple (182g)..."). Enable citations so users verify claims.

**Evidence:** Phase 3: Retrieval accuracy 82% (raw chunks) → 94% (contextual). Citations build user trust (3.2/5 → 4.6/5).

**Why it matters:** Health data needs verification. Citations are non-negotiable.

---

### **Q11: How do you build an evaluation pipeline?**

6-step: (1) Write prompt, (2) Create test dataset, (3) Run inference, (4) Grade results, (5) Compute metrics, (6) Iterate.

**Evidence:** Phase 2: 30-photo test set. Code grader (fast, cheap) + Model grader (Opus, sampled) + Combined score. Cost: $0.04/eval run (vs. $0.30 if only Opus).

**Grading philosophy:** Code grader for format, Model grader for semantics. Combine both for coverage + efficiency.

---

### **Q12: How do you measure if output is getting better?**

Define metrics before experimenting. For accuracy: accuracy@k. For cost: cost per successful call. For latency: P50/P95. Measure before/after.

**Evidence:** Phase 2→3: Food accuracy 72%→88%. JSON validity 97.2%→100%. Recommendation recall 70%→91%. Each phase added a dimension.

---

### **Q13: When should you use workflow vs. single agent?**

**Workflow:** Steps known upfront, sequence fixed, deterministic.  
**Agent:** Steps exploratory, Claude decides order, unpredictable.

**Evidence:** Phase 5: "Recommend 600-cal lunch" → Workflow (2.1s, $0.004). "What's in my fridge?" → Agent (flexible). Common mistake: using agents for everything.

---

### **Q14: Explain orchestrator-workers pattern.**

Orchestrator decomposes task into subtasks. Workers execute in parallel (asyncio.gather). Aggregator compiles results. Use when: 3+ independent subtasks.

**Evidence:** Phase 5: Weekly meal planning. 60s (sequential) → 18s (parallel). Same cost (21 calls), 3.3x faster latency.

**When to use:** 3+ independent subtasks. If sequential, workflow is simpler.

---

### **Q15: How do you handle errors in agent loops?**

Errors should be informative (Claude-readable), retryable, bounded (max 3 retries per tool). Let Claude self-correct if actionable.

**Evidence:** Phase 5 agent: Error message tells Claude how to fix it. Claude retries with better input. Without good errors: infinite loops. With them: 85% recovery rate.

---

### **Q16: When NOT to use multi-agent?**

Don't use if:
1. Single agent solves it (one call → done)
2. Steps are sequential, not parallel
3. You haven't measured that agents help
4. Cost explosion outweighs benefits

Multi-agent is 5–10x more expensive. Make sure complexity justifies it.

**Evidence:** Side project: orchestrator-workers vs. workflow. Workflow was simpler and just as fast for that task.

**Interview signal:** Saying "we built multi-agent" is not impressive. Saying "we measured, it wasn't worth it, we used workflow" shows judgment.

---

### **Q17: How do you evaluate a multi-agent system?**

4-dimensional eval:
1. Final output quality
2. Per-worker accuracy
3. Orchestrator reasoning
4. Cost/latency

Multi-agent should beat control (single-agent or workflow).

**Evidence:** Side project eval: Final report 8.2/10 (vs. expert 8.5/10). Worker accuracy 78–92%. Orchestrator decomposition appropriate. Cost/latency: tied with workflow, but more complex.

---

### **Q18: Tell me about a design tradeoff you made.**

(Pick one; here's Sonnet vs. Haiku)

**Tradeoff:** Accuracy vs. cost.

**Data:**
- Haiku: $0.0003/req, 72% accuracy
- Sonnet: $0.0015/req, 88% accuracy
- Cost multiplier: 5x
- Accuracy gain: 16 points

**My decision:** Sonnet

**Reasoning:** Food recognition is core value prop. Wrong nutrition breaks trust. At 1k users: Haiku $6/day, Sonnet $30/day. Both sustainable (not Opus $300/day). 16-point accuracy gain justifies 5x cost for health data.

**Reflection:** I didn't optimize for "cheapest." I optimized for "cheapest while maintaining core quality." That's the real skill.

---

### **Q19: How would you approach building this differently today?**

Three things:

1. **Cost tracking from Day 1** (not Phase 4): Measure what's expensive early. Phase 4 came late; could've optimized sooner.

2. **More user testing:** I tuned cache threshold empirically from logs. With real users, I'd discover more edge cases.

3. **Streaming from Phase 1:** "Analyzing... Querying..." UI is expected now. Added late; better to have from start.

**Why it matters:** Showing you'd do things differently proves you're learning, not defensive.

---

### **Q20: How do you know when to stop optimizing?**

Stop when:
1. Bottleneck is no longer your system
2. Cost is acceptable relative to revenue/users
3. Further optimization requires architectural change (high risk, low reward)

**Evidence:** Phase 4: Achieved 4.3x cost reduction. Could fine-tune embedding model (MiniLM) for nutrition domain. Cost: 2 weeks. Expected improvement: 5–10% faster search. Value: $200/month saved. Decision: Stop. Not worth it.

**When to resume:** If I scale to 10k users and cost becomes real problem again, revisit.

---

### **Q21: How would you redesign NomNom to handle 100k users?**

Three changes:

1. **Caching layer (Redis):** Cache not just prompts, entire recommendation results. TTL: 24h. Hit rate: 30–50%.

2. **Batch processing:** Group eval and fine-tuning into daily batch jobs (not real-time).

3. **Fallback to cheaper models:** When latency > 2s, fall back to Haiku. Accept 5% accuracy loss for speed.

**Current bottleneck:** Cost. Sonnet everywhere = $3M/month at 100k users. Unsustainable. With above: ~$300k/month (90% savings).

---

### **Q22: How would you add personalization to NomNom?**

Three layers:

1. **Simple:** Per-user preferences (diet type, allergies) → Include in prompt. Cost: 0.

2. **Moderate:** Per-user RAG context. Cache user's past meals; retrieve similar ones. Cost: +10%.

3. **Advanced:** Fine-tune Claude on user preferences. Cost: +$100/user (one-time). Value: 10–15% accuracy gain.

**NomNom today:** Layer 1 built. Layer 2 could be added in Phase 6. Layer 3 expensive; only if revenue supports it.

---

## SECTION D: Quick Reference

### **8 Key Metrics to Memorize**

| Metric | Value | Why It Matters |
|--------|-------|---|
| 🚀 **Cache Hit Rate** | **85%** | Most requests return instant results |
| ⚡ **Latency Reduction** | **67%** (60s → 25s) | Difference between abandoned & daily driver |
| 💰 **Cost Savings** | **83%** ($12 → $2/day) | Systems thinking, not just coding |
| 🎯 **Semantic Threshold** | **0.82** | Empirically tuned (0.70–0.95 tested) |
| 📸 **Meal Dataset** | **150 photos** | Validation sample size |
| ✅ **Integration Tests** | **100+** | Production-ready code |
| 📉 **Accuracy Drop (Sonnet)** | **2%** (98% → 96%) | Acceptable for speed/cost |
| ❌ **False Positive Rate** | **<1%** | Caching is reliable |

---

### **Red Flags: What NOT to Say**

❌ "It's just a food tracking app"  
✅ "It's a case study in LLM production engineering"

❌ "Semantic caching was complicated"  
✅ "Semantic caching solved the right problem (similarity vs. exact match)"

❌ "I couldn't figure out why costs spiked"  
✅ "I diagnosed the cost spike, understood it was behavioral (good sign), and mitigated with caching"

❌ "My code is perfect"  
✅ "I found 25+ bugs through systematic testing and fixed them all"

❌ "I would do it the same way again"  
✅ "With hindsight, I'd start semantic caching and monitoring on day 1, not later"

---

### **Confidence Checklist**

Before interview, verify:

- [ ] Can recite 60-second pitch without notes?
- [ ] Can recall all 8 metrics instantly?
- [ ] Can explain semantic caching in 2 minutes?
- [ ] Can explain cost spike story (shows diagnosis)?
- [ ] Can walk through orchestrator-worker pattern?
- [ ] Can point to code files (GitHub evidence)?
- [ ] Can answer "What surprised you?" (shows reflection)?
- [ ] Can answer "What would you do differently?" (shows maturity)?

**If yes to 6+:** You're ready.

---

**Last Updated:** June 16, 2026  
**Status:** Ready for technical interviews  
**Use this for:** Deep-dive questions, technical screens, design interviews
