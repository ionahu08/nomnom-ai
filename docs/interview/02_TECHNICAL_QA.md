# Technical Deep Dive: Questions, Decisions & Evidence
## Speech-Friendly Edition for Interviews

---

## HOW TO USE THIS DOCUMENT

**This file is designed for spoken delivery in interviews.** Here's how to navigate it:

### **For 2-Minute Technical Answers:**
Use **SECTION A: 5 Core Talking Points** — Pick 1-2 that match the interviewer's question. Each is a complete, self-contained story (2-3 min).

### **For 5-10 Minute Deep Dives:**
Combine a **Core Talking Point** with 1-2 **Technical Decision Stories** (SECTION B) that support it. For example:
- Talking Point 1 (semantic caching) + Decision 8 (threshold tuning) = 5-min story
- Talking Point 2 (cost spike) + Decision 12 (model tiering) = 5-min story

### **For "Tell Me More" Follow-ups:**
Use **SECTION C: 22 Technical Q&As** — These are quick pivots when someone asks a specific question mid-conversation. Each is 1-2 minutes.

### **Delivery Tips:**
- **Pause after key numbers** (0.82, 85%, 60%): Let them land
- **Use "so" and "but here's the thing"** to signal transitions: Sounds natural when spoken
- **Own the struggle**: "I was confused for 2 days" is more credible than just "I fixed it"
- **End with "why it matters"**: Connects the technical detail to business value

---

## SECTION A: 5 Core Talking Points

### **Talking Point 1: Why 0.82? The Semantic Cache Threshold Story**

Okay, so when I first built semantic caching for NomNom, people kept asking this one question: "Why 0.82? That seems arbitrary."

So let me walk you through the actual thought process.

**The problem:** Food items aren't identical. A user might photograph "salmon with rice" one day, then "salmon and vegetables" the next. They're different dishes, but nutritionally, they're extremely similar—both are salmon, carbs, and fiber. If I use traditional caching (like Redis with exact matching), I'd get only a 15% hit rate because "salmon with rice" ≠ "salmon and vegetables" as a string. That's useless.

So I moved to semantic similarity. I embedded meal photos using an embedding model, stored those embeddings in pgvector, and searched using cosine similarity instead of exact matching. Now the cache could say "this new photo is similar to a photo we analyzed 3 days ago—here's the cached result."

But then comes the threshold question. At what similarity score do I say "similar enough"? That's where most people guess. They'll say "I'll use 0.95 to be safe" or "0.80 seems reasonable." I didn't want to guess.

**Here's what I actually did:**

I created a dataset of 150 real meal photos—variety across sushi, pizza, salads, bowls, everything. Then I manually labeled which ones were semantic duplicates (the kinds of meals users actually photograph multiple times).

Then I tested thresholds: 0.70, 0.75, 0.80, 0.82, 0.85, 0.90, 0.95. For each threshold, I measured:
- Hit rate: How often does the cache match?
- False positive rate: How often does it match when it shouldn't?

**Here's what the data showed:**

At 0.95, I got a 40% hit rate. That's just barely better than random. The threshold was too strict.

At 0.82, I got an 85% hit rate with less than 1% false positives. That's the sweet spot.

At 0.70, I got 95% hit rate, but 8% of those were false positives—wrong recommendations. That's a real problem.

**Why 0.82 specifically?** Because the cost of false positives (wrong nutrition advice) is much higher than the cost of false negatives (cache miss, extra API call). So I was willing to accept slightly more false positives to get real cache benefit. And 0.82 gave me 85% hit rate with only 5% false positives. That asymmetric tradeoff is why that specific number matters.

**The production result:** 85% cache hit rate, 60% cost reduction, about $10 per day in savings per thousand users.

**What this signals in an interview:** I didn't just implement semantic caching and hope it worked. I measured on real data, understood the tradeoff between recall and precision, and chose a threshold based on the business problem, not the math. That's the difference between "I know the technique" and "I understand the tradeoff."

**Time:** 2–3 minutes | **Use when:** Asked about caching, thresholds, tradeoffs

---

### **Talking Point 2: The Cost Spike After "Optimization"**

This is one of my favorite stories because it sounds like I made a mistake, but actually it taught me something really important about systems thinking.

**Here's the setup:**

Opus costs $0.12 per request. Sonnet costs $0.04 per request. That's 70% cheaper. So I thought: if we're spending $12 a day on Opus, switching to Sonnet should get us down to $4 a day. Simple math, right?

**What actually happened:** Costs went to $10 a day. Not $4. That was weird.

**So I had to diagnose it.** I tracked three metrics:

First, cost per request: Yes, that went down from $0.12 to $0.04. ✓ That part worked.

Second, daily traffic: Huh. The volume went from 100 requests a day to 250 requests a day. Why did that happen?

Third, accuracy: Sonnet was 96% accurate instead of Opus's 98%. That's only a 2% drop, which is acceptable.

**The root causes:**

Sonnet is 3x faster than Opus. So the user experience improved—faster response time makes people want to use the app more. Higher engagement means higher volume. That's not a bug, that's actually good.

Plus, the slightly lower accuracy meant a few more follow-up questions from users asking for clarification. That also increased volume.

**So I had to make a choice:** I could revert to Opus. Or I could accept the volume increase and optimize the full system.

I chose to keep Sonnet because:

One: The per-request cost is the fundamental metric that scales. Sonnet will always be cheaper at volume than Opus. If I ever get to a million users, Opus becomes catastrophically expensive.

Two: The volume increase isn't a bug—it's a feature. Faster response time creates better UX. I don't want to optimize for latency and then punish myself for success.

Three: I knew semantic caching would fix the volume problem. The real optimization isn't "cheaper model" in isolation—it's "cheaper model plus better caching."

**What I actually implemented:** I added rate limiting (20 requests per user per day), set up monitoring (alert me if daily cost exceeds $15), and built semantic caching.

**Final result:** With Sonnet plus semantic caching, daily cost is now $2. That's an 83% savings from baseline. Better than reverting to Opus would have been.

**The lesson:** Cost, latency, and quality are coupled. You can't optimize one in isolation. The real skill is thinking holistically about the system—understanding how a change in one variable cascades to other variables.

**Time:** 2–3 minutes | **Use when:** Asked about cost, optimization, or learning from mistakes

---

### **Talking Point 3: When Local Optimization Breaks Everything**

The semantic caching threshold is actually a perfect example of this too, because it shows what happens when you optimize for the wrong thing.

**Here's how it went:**

I started with a 0.95 threshold. My logic was: "High confidence in matches. Avoid false positives. Be conservative."

Sounds safe, right?

**But then I realized the problem:** Cache hit rate was only 40%. That's barely useful. I was optimizing for precision (avoiding false positives) when the real constraint was recall (actually matching meals users eat).

When I investigated cache misses, I found things like:
- User photographed "salmon with rice" back in Week 1. Stored in cache.
- User photographs "salmon bowl" (no rice, more vegetables) in Week 2.
- The embeddings are different enough to score 0.87 similarity.
- That's below my 0.95 threshold, so: cache miss.
- We run a full Claude API call to analyze "salmon bowl."
- But nutritionally, these meals are almost identical. We just paid for an API call when we could've reused the cached result.

That's the local optimization problem. I optimized for "avoid false positives" without measuring the cost of the false negatives.

**So I fixed it:**

But lowering the threshold creates a different risk: What if I cache "salmon" for "chicken"? That's a real bug.

I didn't want to just guess a new threshold either. So I:

Tested 150 real meal photos with manual labels for semantic duplicates.

Measured precision and recall at each threshold.

Manually reviewed the borderline cases—about 50 meal pairs that were right on the edge.

Added a regression test: `test_semantic_cache_threshold_tuning` so that if someone changes this in the future, we catch regressions immediately.

**The learning:**

There are no free lunches in matching problems. Lower threshold means more hits but more noise. Higher threshold means fewer hits but higher precision. You have to measure and decide based on your specific domain.

For food tracking, 85% hit rate with 1% false positives is acceptable. The cost of a cache miss (extra API call) is higher than the cost of a false positive (slightly wrong recommendation, but still in the ballpark for nutrition).

But in medicine or finance, you'd want 99% precision even if it meant lower recall. The risk calculation is completely different.

**Time:** 2–3 minutes | **Use when:** Asked about tradeoffs, optimization failures, or decision-making

---

### **Talking Point 4: Orchestrator-Workers and the 67% Latency Reduction**

This pattern changed how I think about parallelization. So when people ask "How did you achieve 67% latency reduction?" this is the core of it.

**First, let me show you the sequential version:**

User uploads a photo. Then Claude analyzes it (2 seconds). Then we do RAG retrieval to get context (1 second). Then Claude generates recommendations (2 seconds). Then we log the cost and metrics (0.5 seconds). Total: 5.5 seconds.

That's actually okay for one request. But when you scale it—when the user has 7 days of meal planning to do—suddenly you're doing this 21 times. That's 60 seconds. At that point, the user has abandoned the app.

**Then I built the parallel version.**

User uploads their weekly planning request. Instead of doing this sequentially, I launch three workers in parallel:
- Worker 1: Analyzes the photo(s) (2 seconds)
- Worker 2: Retrieves RAG context (1 second)
- Worker 3: Logs cost and metrics (0.5 seconds)

These workers don't depend on each other. Worker 2 doesn't need the result from Worker 1. They're independent.

So instead of waiting 5.5 seconds, we wait for the longest task—the photo analysis at 2 seconds. Everything else finishes while we're waiting for that. The orchestrator then gathers the results and formats the response (0.5 seconds).

Total for one iteration: 2.5 seconds instead of 5.5 seconds.

For 7 days: 60 seconds becomes 18 seconds.

**Here's what the code looks like:**

```python
async def orchestrate(photo):
    # Launch 3 workers in parallel using asyncio.create_task
    analysis_task = asyncio.create_task(worker_analyze_photo(photo))
    rag_task = asyncio.create_task(worker_retrieve_context(user_id))
    cost_task = asyncio.create_task(worker_track_cost(user_id, model))
    
    # Wait for all to complete using gather
    analysis, context, cost = await asyncio.gather(
        analysis_task, rag_task, cost_task
    )
    
    # Orchestrator combines results
    recommendation = claude.generate_recommendation(analysis, context)
    return recommendation
```

The key is: all three tasks run concurrently. Python's asyncio.gather waits for all of them, so you only pay the cost of the slowest one.

**The tradeoffs:**

This is slightly more complex code. You're managing three asyncio tasks at once. Debugging is harder because three things are happening simultaneously, and if one fails, you need to understand the failure mode.

But is it worth it? Absolutely. 60 seconds to 18 seconds isn't micro-optimization. That's the difference between "I started using this app" and "I abandoned it because it's too slow."

**Real-world metrics:**

When I measured this on 100+ real requests, the orchestrator-worker pattern consistently achieved 18-25 second latency, while the sequential approach was 60+ seconds.

**Signal for interviews:**

This shows you understand parallelization patterns. But more importantly, it shows you understand the *when* and *why*. This pattern only works when tasks are independent. If Worker 2 needed the result from Worker 1, parallelization doesn't help—they'd still be sequential.

**Time:** 2–3 minutes | **Use when:** Asked about latency, parallelization, system design

---

### **Talking Point 5: What Actually Surprised Me About LLM Engineering**

When I started this project, I had assumptions about what would be hard. Turned out I was wrong about a lot.

**Surprise 1: Prompts are product assets, not infrastructure code**

I expected the work to be 80% prompt engineering, 20% architecture. Turns out it's the opposite.

Prompts change constantly. A PM wants to try different phrasing. A user asks for a different tone. You want to A/B test the CoT instructions. These changes happen 10x more frequently than changes to the actual code.

But most teams treat prompts like code: hardcoded in Python, requires a code review, requires a redeploy, requires tests, blocks other work.

So early on, I built Jinja2 templating. Prompts live in separate `.j2` files. Variables get injected at runtime. Now a PM can change the prompt, test it immediately, see if it works, deploy it without touching Python.

What I'd do differently: Build this from day one, not week 3. Prompts are product. Treat them like product.

**Surprise 2: 30% of LLM bugs aren't hallucinations**

I came in thinking hallucinations would be the main problem. Claude makes up facts. Users trust the app less. That's what everyone talks about.

But when I tracked actual bugs in Phase 2, I found something surprising: Only 20% of failures were hallucinations. 30% of bugs were parsing errors. The other 50% were schema mismatches—Claude returned the right information but in the wrong format, and the parser crashed.

This happened because I was using prefill+stop: I'd manually insert ` ```json ` at the start of Claude's response and tell it to stop at ` ``` `. This almost works. But with certain prompts, Claude would add extra formatting and mess up my stop token. Then downstream code crashed trying to parse malformed JSON.

Once I moved to `tool_choice="force"` with strict JSON schema, that 30% of bugs vanished. Claude *must* output the exact schema. No wiggle room.

What I'd do differently: Implement structured output validation from day one. Before you build anything else. It prevents a whole category of bugs.

**Surprise 3: Orchestration patterns scale way better than single agents**

I assumed agent loops would be the standard approach—give Claude a tool, let it loop until the answer is ready. That's the "agentic" way, right?

But when I benchmarked, I found: orchestrator-worker parallelization (3 independent workers running in parallel) reduced latency from 60 seconds to 18 seconds. That's 67% improvement. Not micro-optimization—that's fundamental.

And single-agent loops on the same task took 60+ seconds because each step was sequential. "Analyze photo, then retrieve context, then generate recommendation."

The insight: if you know the steps upfront (deterministic), use a workflow with parallelization. Agents are for exploratory tasks where Claude needs flexibility.

What I'd do differently: Model every workload as a DAG (directed acyclic graph) from the start. Identify independent tasks. Parallelize them. Don't serialize just because it's simpler.

**Bonus surprise: Cheaper models plus smart caching beats expensive models**

I expected Opus would be necessary for "hard" problems like food recognition. But Sonnet (70% cheaper) plus semantic caching (85% hit rate) outperforms Opus without caching. It's cheaper AND faster.

Architecture beats raw capability.

**If I rebuilt from scratch:**

1. Start with structured output validation (it prevents 30% of bugs)
2. Build semantic caching from day one, not week 6 (it's the biggest savings)
3. Model workload as a DAG and parallelize (67% latency gain is huge)
4. Implement monitoring (cost, latency, quality) before adding features (you'll know where the real bottleneck is)
5. Keep a prompt changelog (date, version, why it changed) so you can debug prompt-related issues
6. Test on real user data earlier (you'll discover edge cases that don't show up in synthetic tests)

**The meta-lesson:**

LLM engineering is mostly architecture. The "intelligence" part—Claude—is about 10%. The hard work is: caching strategy, parallelization, validation, monitoring, prompt management. That's where the real value is.

**Time:** 2–3 minutes | **Use when:** Asked about lessons learned, surprises, or what you'd do differently

---

## SECTION B: 18 Technical Decision Stories (Condensed Summaries)

**When to use:** Pick 2-3 that best fit the interviewer's interest. Expand any one into a 5-minute story by adding: "So here's why I made that choice..." and "The result was..."

### **Decision 1: Jinja2 Templating Over F-Strings**

**The problem:** Prompts hardcoded in Python blocked iteration. Every change required code review + redeploy.

**The decision:** Separate prompts into `.j2` template files. Variables injected at runtime.

**Why:** Prompts are product assets. Non-engineers can iterate without touching code.

**Outcome:** Iteration time 2 hours → 10 minutes. Code churn reduced 80%.

---

### **Decision 2: Exponential Backoff in Retry Logic**

**The problem:** Transient API failures hammered the API harder, making outages worse.

**The decision:** Exponential backoff (1s → 2s → fail) in `client.py`.

**Why:** Gives Claude API time to recover. Respects rate limits.

**Outcome:** 85% of transient failures recovered. User-facing errors dropped 40%.

---

### **Decision 3: Sonnet Over Haiku/Opus**

**The problem:** Which model for food recognition? Haiku is cheap but inaccurate (60% fail rate). Opus is accurate but unsustainable ($3–4/req).

**The decision:** Sonnet for images, Haiku for JSON extraction, Opus for eval sampling.

**Why:** Food recognition is the core value prop. Wrong nutrition breaks trust. Sonnet at $0.0015/req is sustainable at scale.

**Outcome:** 88% accuracy. $20/month sustainable for 1k users.

---

### **Decision 4: tool_choice For Structured Output**

**The problem:** Prefill+stop was fragile (2.8% of calls produced unparseable JSON).

**The decision:** Migrate to `tool_choice="force"` with strict JSON schema.

**Why:** Schema enforcement. Claude must output exactly the defined structure.

**Outcome:** 97.2% → 100% JSON parse success. Zero downstream parser failures.

---

### **Decision 5: Hybrid Code + Model Grading**

**The problem:** Model-only eval ($0.01 per case × 30 cases = expensive). Code-only eval misses semantic errors.

**The decision:** Hybrid: Code grader (fast, cheap) + Model grader (Opus, 10% sample). Combined score: (code 30% + model 70%).

**Why:** 90% of evals caught by code grading. Only 10% sampled with expensive model grading.

**Outcome:** Eval latency 45s → 8s. Cost $0.30 → $0.04 per run.

---

### **Decision 6: Claude-Readable Error Messages**

**The problem:** When image is too blurry, error was "JSON_VALIDATION_ERROR: missing field 'calories'". Claude had no idea how to fix it.

**The decision:** Rewrite errors for Claude as the reader.

**Example:**
```
OLD: "Invalid JSON: missing field 'calories'"
NEW: "The image is too blurry. Ask user to retake the photo with better lighting."
```

**Why:** Claude reads the error, understands the root cause, can self-correct.

**Outcome:** Error recovery 40% → 85%. Mean retries 4 → 1.2.

---

### **Decision 7: MiniLM-L6-v2 For Embeddings**

**The problem:** OpenAI embeddings (3072-dim, $0.13/1M tokens) vs. local alternatives.

**The decision:** MiniLM-L6-v2 (384-dim, open-source, 95% quality of OpenAI).

**Why:** Cost $0 (local) vs. $50/month. Quality sufficient for nutrition semantics. 8x faster vector ops.

**Outcome:** Embedding latency 2ms. Search latency 15ms (vs. 120ms with larger models).

---

### **Decision 8: Cosine Similarity 0.82 Threshold** *(See Talking Point 1)*

Tested 0.70–0.95 on 150 real meals. Found 0.82 captures 90% of duplicates with 5% false positives.

**Outcome:** 85% cache hit rate, 60% cost savings.

---

### **Decision 9: Hybrid Search (BM25 + Vector + RRF)**

**The problem:** Vector search alone misses exact matches. BM25 alone misses synonyms.

**The decision:** BM25 index + Vector index + RRF (Reciprocal Rank Fusion) ranking.

**Why:** Best of both worlds. BM25 handles exact matches, vector handles semantic similarity.

**Outcome:** Recall improved 78% (vector) → 91% (hybrid).

---

### **Decision 10: Contextual Retrieval For RAG Chunks**

**The problem:** "Apple: 52 cal, 13g carbs" is ambiguous in isolation. Per 100g? Per apple?

**The decision:** Add context before embedding: "A medium apple (182g) provides 52 calories, 13g carbs. Source: USDA."

**Why:** Reduces ambiguity. Improves recall by 15–20% (per Anthropic research).

**Outcome:** Retrieval accuracy 82% → 94%.

---

### **Decision 11: Citations (RAG Anti-Hallucination)**

**The problem:** Recommendation says "apple has potassium [source?]". Is this a hallucination?

**The decision:** Enable citations. Claude annotates each fact with source.

**Why:** Builds trust. Users can verify. Essential for health data.

**Outcome:** User trust 3.2/5 → 4.6/5. Support questions dropped 80%.

---

### **Decision 12: Model Tiering By Task Type**

**The problem:** Using Sonnet for everything costs $1.50/user/day (unsustainable).

**The decision:** 
- Image recognition → Sonnet ($0.0015/req)
- JSON extraction → Haiku ($0.0001/req)
- Eval → Opus ($0.01/req, rare)

**Why:** Cost optimization where it matters. Food recognition accuracy critical. JSON already validated.

**Outcome:** $1.50 → $0.35 per user per day (4.3x reduction). Accuracy maintained at 88%.

---

### **Decision 13: Prompt Caching For System Prompts**

**The problem:** Every request sends same 400-token system prompt. 72,400 tokens/hour redundant.

**The decision:** Mark system prompt as `cache_control: {"type": "ephemeral"}`. Cache for 1 hour.

**Why:** First call pays full cost. Subsequent calls (within 1 hour) pay 90% less.

**Outcome:** 89% savings on system prompt tokens. $50/month savings per 1k users.

---

### **Decision 14: Cost Tracking & Dashboard**

**The problem:** No visibility into spend. "Can we afford 1k users?" was a guess.

**The decision:** Structured logging in `logger.py`. Per-call: tokens, latency, model, cost.

**Why:** Business insight. Data-driven decisions. Discovered RAG = 60% of spend.

**Outcome:** Full cost visibility. Guided Phase 3 optimization decisions.

---

### **Decision 15: Workflow For Meal Recommendation (Not Single Agent)**

**The problem:** "Recommend 600-cal lunch" could use flexible agent or fixed workflow.

**The decision:** Workflow. Fixed steps: Extract constraints → Retrieve → Evaluate → Rank.

**Why:** Predictable, testable, debuggable. No self-loop cost.

**Outcome:** Latency 4.2s (agent) → 2.1s (workflow). Cost $0.008 → $0.004.

---

### **Decision 16: Orchestrator-Workers For Weekly Planning** *(See Talking Point 4)*

7 days × 3 meals = 21 calls. Sequential: 60s. Parallel: 18s.

**Outcome:** 3.3x latency improvement, same cost.

---

### **Decision 17: MCP Server (Not Just REST API)**

**The problem:** NomNom locked in iOS + REST API. High friction for other tools.

**The decision:** Build MCP (Model Context Protocol) server. Anthropic's standard for LLM tools.

**Why:** Standardization. Other LLMs speak MCP natively.

**Outcome:** Integration time: 30min (REST) → 2min (MCP).

---

### **Decision 18: MCP Tools vs. Resources Distinction**

**The problem:** Unclear when to use tools (reactive) vs. resources (proactive).

**The decision:**
- Tools: `analyze_food_image`, `lookup_nutrition`, `recommend_meal` (Claude initiates)
- Resources: `nomnom://foods/{id}`, `nomnom://history` (client reads)

**Why:** Clarity. Resources avoid unnecessary LLM calls.

**Outcome:** Clear mental model for developers.

---

## SECTION C: 22 Technical Q&As

**These are quick pivots for follow-up questions. Each is 1-2 minutes spoken.**

### **Q1: How do you handle transient failures in LLM API calls?**

Exponential backoff with small retry count (2–3). Wait 1s, then 2s, then fail. Don't hammer the API during outages.

I built this in `client.py` in Phase 1. Result: 85% of transient failures recovered without the user seeing an error.

The principle: Retry logic is the difference between "feels like an outage" and "briefly slow."

---

### **Q2: How do you optimize LLM costs without sacrificing quality?**

Don't optimize blindly. Measure where money goes. Use model tiering: cheap for simple tasks, expensive for high-stakes.

I tiered by task: Haiku for JSON ($0.0001/req), Sonnet for images ($0.0015/req), Opus for eval (rare). Result: 4.3x cost reduction, 88% accuracy maintained.

Constraint thinking: At 1k users, $1.50/day = $45k/month (unsustainable). That's a hard constraint.

---

### **Q3: Tell me about prompt caching. When does it help?**

Reuses expensive static content (system prompts, tool schemas). First call pays full cost. Next 180 calls (1-hour TTL) pay 90% less per cached token.

Example: System prompt (400 tokens) × 181 calls/hour = 72,400 tokens/hour uncached → 7,600 cached (89% savings = $50/month per 1k users).

When it doesn't help: System prompt changes hourly (cache invalidates).

---

### **Q4: How do you track LLM costs?**

Log per-call: tokens (input, output, cache-read), latency, model, cost. Query to answer "Which feature costs most?" and "Can we afford N users?"

Discovery: RAG accounts for 60% of spend. This data-driven insight led to Phase 3 optimization.

Without visibility, "Are we profitable?" is a guess.

---

### **Q5: How do you design prompts for iteration?**

Separate prompts from code. Use templating (Jinja2). Version-control prompts independently. Non-engineers can iterate without touching Python.

Jinja2 templating: Prompt iteration time 2 hours → 10 minutes. Code churn reduced 80%.

Principle: Prompts are product assets (change 10x more frequently than code).

---

### **Q6: How do you handle ambiguous or malformed user input?**

Design error messages for Claude to read, not humans. Tell Claude what's wrong and how to fix it. Enables self-correction.

Example: Blurry photo. Old error: "JSON_VALIDATION_ERROR: missing field 'calories'". New error: "Image is too blurry. Ask user to retake with better lighting." Result: Error recovery 40% → 85%.

Insight: Error messages are part of the control loop.

---

### **Q7: Prefill+stop vs. tool_choice—when to use each?**

Prefill+stop is simple but fragile (prompt injection, hallucination). tool_choice enforces schema strictly. Use tool_choice when correctness matters.

Migrated in Phase 2. JSON parse success 97.2% → 100%. No injection vulnerabilities.

For health data, tool_choice is non-negotiable.

---

### **Q8: How do you tune a semantic cache threshold?**

Measure empirically. Collect 100+ real requests, manually label semantic duplicates, plot cosine similarity, find sweet spot.

I tested 0.70–0.95 on 150 real meals. Found 0.82 captures 90% of duplicates with 5% false positives.

Without data, I'd have guessed 0.95 (conservative). That leaves 40% cache misses. With measurement, captured 90% of value with 5% risk.

---

### **Q9: Vector search vs. BM25 vs. hybrid—which one?**

Hybrid (vector + BM25 + RRF). Vector catches synonyms. BM25 catches exact matches. Each alone fails 20–30% of the time. Combined: 91% recall.

Why RRF? It's a RecSys pattern. Parameter-free. No tuning needed.

---

### **Q10: How do you structure RAG knowledge?**

Chunk by meaning, not size. Add context before embedding. Enable citations.

Example: "A medium apple (182g) provides 52 calories..." instead of "Apple: 52 cal."

Citations build user trust (3.2/5 → 4.6/5). Health data needs verification.

---

### **Q11: How do you build an evaluation pipeline?**

6-step: (1) Write prompt, (2) Create test dataset, (3) Run inference, (4) Grade results, (5) Compute metrics, (6) Iterate.

I use hybrid grading: Code grader (fast, cheap) + Model grader (Opus, sampled). Combined score.

Cost: $0.04/eval run (vs. $0.30 if model-only). Grading philosophy: Code for format, Model for semantics.

---

### **Q12: How do you measure if output is getting better?**

Define metrics before experimenting. For accuracy: accuracy@k. For cost: cost per successful call. For latency: P50/P95. Measure before/after.

Phase 2→3: Food accuracy 72%→88%, JSON validity 97.2%→100%, Recommendation recall 70%→91%. Each phase adds a dimension.

---

### **Q13: When should you use workflow vs. single agent?**

Workflow: Steps known upfront, sequence fixed, deterministic.  
Agent: Steps exploratory, Claude decides order, unpredictable.

Evidence: "Recommend 600-cal lunch" → Workflow (2.1s, $0.004). "What's in my fridge?" → Agent (flexible).

Common mistake: using agents for everything.

---

### **Q14: Explain orchestrator-workers pattern.**

Orchestrator decomposes task into subtasks. Workers execute in parallel (asyncio.gather). Aggregator compiles results.

Weekly meal planning: 60s (sequential) → 18s (parallel). Same cost (21 calls), 3.3x faster latency.

Use when: 3+ independent subtasks. If sequential, workflow is simpler.

---

### **Q15: How do you handle errors in agent loops?**

Errors should be informative (Claude-readable), retryable, bounded (max 3 retries per tool).

Claude-readable error: "Image too blurry. Ask user to retake." Claude retries with better input.

Without good errors: infinite loops. With them: 85% recovery rate.

---

### **Q16: When NOT to use multi-agent?**

Don't use if:
1. Single agent solves it (one call → done)
2. Steps are sequential, not parallel
3. You haven't measured that agents help
4. Cost explosion outweighs benefits

Multi-agent is 5–10x more expensive. Make sure complexity justifies it.

Signal: "We measured, it wasn't worth it, we used workflow" shows judgment.

---

### **Q17: How do you evaluate a multi-agent system?**

4-dimensional eval:
1. Final output quality
2. Per-worker accuracy
3. Orchestrator reasoning
4. Cost/latency

Multi-agent should beat control (single-agent or workflow).

---

### **Q18: Tell me about a design tradeoff you made.**

Pick one: Sonnet vs. Haiku for food recognition.

Haiku: $0.0003/req, 72% accuracy. Sonnet: $0.0015/req, 88% accuracy. Cost multiplier: 5x. Accuracy gain: 16 points.

I chose Sonnet. Food recognition is core value prop. Wrong nutrition breaks trust. 16-point accuracy gain justifies 5x cost for health data.

Reflection: I didn't optimize for "cheapest." I optimized for "cheapest while maintaining core quality."

---

### **Q19: How would you approach building this differently today?**

Three things:

1. **Cost tracking from Day 1** (not Phase 4): Measure what's expensive early.

2. **More user testing:** I tuned cache threshold empirically from logs. With real users, I'd discover more edge cases.

3. **Streaming from Phase 1:** "Analyzing..." UI is expected now. Added late; better to have from start.

Showing you'd do things differently proves you're learning, not defensive.

---

### **Q20: How do you know when to stop optimizing?**

Stop when:
1. Bottleneck is no longer your system
2. Cost is acceptable relative to revenue/users
3. Further optimization requires architectural change (high risk, low reward)

Evidence: Phase 4 achieved 4.3x cost reduction. Could fine-tune embedding model (MiniLM) for nutrition domain. Cost: 2 weeks. Expected improvement: 5–10% faster search. Value: $200/month. Decision: Stop.

---

### **Q21: How would you redesign NomNom to handle 100k users?**

Three changes:

1. **Caching layer (Redis):** Cache recommendation results, not just prompts. TTL: 24h. Hit rate: 30–50%.

2. **Batch processing:** Group eval and fine-tuning into daily batch jobs (not real-time).

3. **Fallback to cheaper models:** When latency > 2s, fall back to Haiku. Accept 5% accuracy loss for speed.

Current bottleneck: Cost at 100k users = $3M/month. With above: ~$300k/month (90% savings).

---

### **Q22: How would you add personalization to NomNom?**

Three layers:

1. **Simple:** Per-user preferences (diet type, allergies) → Include in prompt. Cost: 0.

2. **Moderate:** Per-user RAG context. Cache user's past meals; retrieve similar ones. Cost: +10%.

3. **Advanced:** Fine-tune Claude on user preferences. Cost: +$100/user (one-time). Value: 10–15% accuracy gain.

NomNom today: Layer 1 built. Layer 2 could be added in Phase 6. Layer 3 expensive; only if revenue supports it.

---

## SECTION D: LLM Harnessing Process & Development Methodology (10 Q&As)

**When to use:** Interviews ask "Walk me through your development process" or "How did you stay organized?" These answers differentiate you by showing not just technical depth, but systematic thinking and iteration discipline.

---

### **Q23: Walk me through your development process. How do you organize a big project?**

Great question. I use a standardized iteration workflow that I developed specifically for AI-assisted development. It's designed to work seamlessly whether I'm writing code or having Claude help.

**The structure:**

Every feature or major work unit gets a dedicated folder: `docs/iterations/{number}-{slug}/`. Inside that folder, four documents:

1. **PLAN.md** — Goals, success criteria, what's built vs. what we're building
2. **PHASES.md** — Detailed implementation steps, code examples, file references
3. **BUGLOG.md** — Known issues, blockers, decisions, updated *during* the iteration
4. **SUMMARY.md** — Retrospective created at the end

**Here's why this matters:**

When you're working with AI, context gets lost between sessions. If I stop mid-way through Iteration 15, I need to remember: what was blocking me? What did I discover about the schema? What edge case did I find in testing?

BUGLOG.md is the lifeline. It's not just "here's a list of bugs." It's:
- Daily discoveries (today I realized X)
- Decisions made (why I chose Y over Z)
- Testing notes (edge case found: empty food list crashes parser)
- Blockers (waiting on database migration before continuing)

When I come back to the project, I read PLAN + BUGLOG and I'm immediately caught up.

**Real example from my project:**

Iteration 18 (Weekly Nutrition Summary) had 9 bugs. Each one is documented in BUGLOG.md with:
- What went wrong (timezone handling bug)
- Root cause (naive date math didn't account for DST)
- How I fixed it (used timezone-aware datetime)
- How I prevented recurrence (regression test added)

This prevented re-discovering the same bug in Iteration 19.

**Time:** 2–3 minutes | **Use when:** Asked about organization, workflow, how you stay sane on big projects

---

### **Q24: How do you use Claude Code in your workflow?**

Claude Code is integrated directly into my iteration process. I use it for two distinct purposes: exploration and execution.

**Exploration phase (Days 1-3 of iteration):**

I write out the PLAN.md in plain language: "We need a semantic cache with pgvector. The constraint is: how do we avoid false positives? Here's what I know about the domain..."

Then I ask Claude to help me think through the approach:
- "What are the trade-offs between BM25 and vector search for meal embeddings?"
- "Walk me through threshold tuning. What's the standard methodology?"
- "Show me examples of semantic cache false positives in production systems"

Claude helps me *design* the solution before I code it.

**Execution phase (Days 4-10):**

I work in Claude Code where I can:
- Read code files
- Run tests
- Make edits with full context
- Commit with disciplined messages

The key is: I'm driving the work. I write the BUGLOG.md entries. I decide what gets tested. Claude is the intelligent pair programmer who helps me move faster.

**How I stay in control:**

Before every commit, I:
1. Review `git diff` (Claude doesn't commit anything I haven't seen)
2. Run the test suite (`pytest tests/`)
3. Write a clear commit message (Conventional Commits style)

This prevents the "AI wrote code I don't understand" problem.

**Real workflow from Iteration 12 (Semantic Caching):**

Day 1: Me in PLAN.md — "Goal: 85% cache hit rate with <5% false positives"
Day 2: Claude helps me think through threshold tuning methodology
Day 3: I build a test dataset with Claude's help (150 real meal photos + labels)
Days 4-6: Claude helps me implement the embedding pipeline (reading pgvector docs, writing queries)
Days 7-9: Testing phase—I run the threshold tests, Claude helps me analyze the results
Day 10: I commit, write SUMMARY.md, move to next iteration

**The skill:** Not delegating thinking to AI, but using AI to move faster on the things I've already decided to do.

**Time:** 2–3 minutes | **Use when:** Asked how you work with AI tools, or if they ask about code quality/control

---

### **Q25: You mention "PLAN, PHASES, BUGLOG, SUMMARY"—explain this structure and why it works for AI-assisted development.**

This is the core of how I stay organized with AI. Let me break down each document and its purpose.

**PLAN.md (Specification)**

This is the contract. It answers:
- What problem are we solving?
- What's already built (prerequisites)?
- What are we building (1-5 features max)?
- What's success? (Checkboxes: all tests pass, no regressions, X metric achieved)
- What skills/patterns are we learning?

Example from Iteration 14 (Meal Recommendation Workflow):
```
Goal: Replace single-agent meal planning with orchestrator-workers pattern
Success Criteria:
- [ ] Latency reduced from 60s → <25s
- [ ] All meal plans return valid JSON
- [ ] No regressions in recommendation accuracy (>90%)
```

Why this matters for AI: Claude reads this and knows exactly what "done" means. No scope creep. No "oh, maybe we should also add X feature."

**PHASES.md (Implementation Breakdown)**

Detailed steps. Code examples. Links to source files.

Example:
```
Phase 1: Build the orchestrator
- Receives planning request (user wants 7-day meal plan)
- Spawns N parallel workers (one per day)
- Uses asyncio.gather to wait for all workers

Here's the pattern:
  orchestrator_task = asyncio.create_task(orchestrate(planning_request))

Phase 2: Implement each worker
- Worker accepts: date + constraints
- Returns: meal recommendation for that date
```

Why this matters for AI: It's the "how." When Claude Code reads this, it knows the pattern to implement before writing code. Prevents "write me a meal planner" → Claude writes something that doesn't fit your architecture.

**BUGLOG.md (Living Document)**

Updated daily/weekly during the iteration. Not just bugs—also:
- Discoveries ("Realized pgvector doesn't have built-in pagination—need to fetch all and sort in code")
- Decisions ("Chose Sonnet over Haiku because of accuracy gap on ambiguous foods like sushi")
- Testing notes ("Edge case: empty food log crashes the analytics endpoint")
- Blockers ("Waiting on database migration before I can test RAG")

This is the handoff document. When I pause, the next developer (or next session of me) reads this and gets caught up in minutes, not hours.

Real example from Iteration 18 (Weekly Summary):
```
## Testing Notes
- Timezone bug found: naive date math breaks at DST boundary
- Fix: Use timezone-aware datetime objects
- Regression test added: test_analytics_handles_dst_transitions

## Next Session
- Cosmos to implement monthly analytics (similar pattern)
- Watch out for: leap seconds? (probably not relevant, but check)
```

**SUMMARY.md (Retrospective)**

Created at iteration end. Captures:
- What was built (1-2 paragraphs)
- Challenges (what was harder than expected?)
- Testing results (coverage, regressions?)
- Lessons learned (patterns that worked well)
- Next steps (what should come next?)

Example from Iteration 12:
```
## Lessons Learned
1. Threshold tuning on real data beats guessing
   - Started with 0.95 (safe), got 40% cache hit
   - Tested 8 thresholds on 150 meals
   - Found 0.82 = 85% hit + 5% false positives
   - Improved cost savings by 60%

2. RecSys ranking algorithm > simple similarity sorting
   - Hybrid search (BM25 + vector) better than either alone
   - Result: 91% recommendation accuracy vs 78% vector-only

## Next Iteration
Phase 4 should focus on cost optimization. We're now stable; time to optimize per-request cost.
```

**Why this structure works for AI-assisted development:**

1. **PLAN gives Claude constraints** — It knows what "done" is. Prevents rabbit holes.
2. **PHASES gives Claude patterns** — It understands the architecture before coding. Code quality goes up.
3. **BUGLOG prevents re-discovery** — Next session doesn't re-debug timezone bugs. Massive time saver.
4. **SUMMARY creates institutional memory** — Why did I choose 0.82? It's documented. Future me remembers the reasoning.

**Time:** 3–4 minutes | **Use when:** Asked about process, organization, how you'd handle bigger projects

---

### **Q26: How do you generate test cases when working with AI? Tell me about your testing strategy.**

This is where the discipline really shows. I use three layers of testing, and Claude helps at each layer.

**Layer 1: Unit Tests (Behavior Tests)**

I define what the function should do:
```python
def test_semantic_cache_threshold_0_82():
    """Cache hit rate at 0.82 threshold should be ~85% with <1% false positives"""
    # Setup: 150 real meal photos
    # Threshold: 0.82
    # Expect: 85% hit rate, minimal false positives
```

Claude helps me:
1. Identify edge cases (what could go wrong?)
2. Build test fixtures (realistic meal data)
3. Assert on metrics (not just "did it crash?" but "did it achieve the target?")

Real example from Iteration 12:
```python
def test_semantic_cache_threshold_tuning():
    """Test that 0.82 achieves 85% hit rate on real meal data"""
    meals = load_real_meal_dataset(150)
    threshold_0_82 = SemantialCache(threshold=0.82)
    
    hit_rate = measure_hit_rate(threshold_0_82, meals)
    false_positive_rate = measure_false_positives(threshold_0_82, meals)
    
    assert hit_rate > 0.80, f"Expected 85%, got {hit_rate}"
    assert false_positive_rate < 0.05, f"Too many false positives: {false_positive_rate}"
```

**Layer 2: Integration Tests (End-to-End Tests)**

Does the whole system work? Photo upload → analysis → caching → recommendation.

```python
def test_meal_recommendation_flow():
    """Full flow: upload photo → analyze → cache → recommend"""
    photo = upload_meal_photo(path="sushi_bowl.jpg")
    
    # First call: no cache hit
    analysis_1 = analyze_food(photo)
    assert analysis_1.calories > 0
    
    # Second call: cache hit (similar photo)
    photo_similar = upload_meal_photo(path="sushi_bowl_variant.jpg")
    analysis_2 = analyze_food(photo_similar)
    
    # Should be cached result (mostly identical nutrition)
    assert analysis_1.protein_g ≈ analysis_2.protein_g
```

Claude helps me:
- Think through the dependencies (what needs to exist first?)
- Handle async/await properly (the code works with real async I/O)
- Mock external services (Claude API, database, etc.)

**Layer 3: Regression Tests (Prevent Re-breaking)**

Whenever I discover a bug, I add a test that reproduces it, fix it, then verify the test passes.

Real example from Iteration 18 (timezone bug):
```python
def test_analytics_handles_dst_transitions():
    """Bug: DST transition breaks date math. Verify it's fixed."""
    # DST transition: March 10, 2024
    date_before_dst = datetime(2024, 3, 10, 1, 0, 0, tzinfo=UTC)
    date_after_dst = datetime(2024, 3, 10, 4, 0, 0, tzinfo=UTC)
    
    analytics = calculate_weekly_summary(start_date=date_before_dst)
    
    # Should handle timezone-aware datetime correctly
    assert len(analytics) == 7  # Full week, no missing days
```

**Measurement-driven testing:**

When I add a feature, I define metrics upfront:
- Cache hit rate (target: 85%)
- Accuracy (target: >88%)
- Latency (target: <25s)
- Cost per request (target: <$0.10)

Then I write tests that measure these metrics, not just "does it work?"

**Why Claude helps here:**

I describe the business constraint ("users abandon the app if latency > 30s"), and Claude helps me translate that to a test:
```python
def test_meal_planning_latency():
    """Latency constraint: users abandon if response > 30s"""
    start = time.time()
    recommendation = get_meal_plan(user_id=1, days=7)
    elapsed = time.time() - start
    
    assert elapsed < 30.0, f"Latency too high: {elapsed}s"
```

**Iteration 11 (Eval Pipeline) was my deepest testing work:**

I built a systematic evaluation pipeline with 30+ test cases. Claude helped me:
1. Define what "good" output looks like (JSON valid? semantically correct? useful?)
2. Build a hybrid grading system (code for cheap checks, model for expensive checks)
3. Track improvement over time (did my changes make outputs better or worse?)

**Time:** 2–3 minutes | **Use when:** Asked about testing strategy, quality assurance, or how you ensure your code actually works

---

### **Q27: Tell me about your quality gates. How do you know when a feature is "done"?**

I have five quality gates that every feature must pass before it's considered complete. This is from CLAUDE.md / dev-rules.md, and it's critical for maintaining code quality at scale.

**Gate 1: Correctness**
- Does the code do what was requested?
- Are edge cases handled?
- Are there any regressions?

**Gate 2: Tests**
- Are there tests for new features?
- Do all existing tests pass?
- Is there a regression test for any bugs I fixed?

For example, when I fixed the timezone bug in Iteration 18, I added `test_analytics_handles_dst_transitions` and verified it failed before my fix, passed after.

**Gate 3: Code Quality**
- No linting errors (using ruff)
- No TODO comments without context
- No dead code
- No unused imports

I actually delete unused code instead of leaving it "for reference." This sounds strict, but it prevents the codebase from becoming a graveyard.

**Gate 4: Security**
- No secrets in the code
- User input validated at system boundaries
- Dependencies from trusted sources

For iOS, this means JWT tokens go in Keychain, not UserDefaults. For the backend, it means password resets use cryptographically secure tokens.

**Gate 5: Documentation**
- Does BUGLOG.md capture what I learned?
- Does SUMMARY.md explain decisions?
- Is the README up-to-date?

**Concrete example: Iteration 12 (Semantic Caching)**

Before I marked it "done":
- Gate 1: Cache achieves 85% hit rate (measured on 150 real meals) ✓
- Gate 2: 100+ integration tests, all passing ✓
- Gate 3: `ruff check src/ && ruff format src/` — clean ✓
- Gate 4: pgvector credentials in .env, not hardcoded ✓
- Gate 5: BUGLOG documents why 0.82 threshold, SUMMARY explains the tradeoff ✓

Only then did I commit and mark the iteration complete.

**Why this matters in interviews:**

Most engineers say "I shipped the feature." You're saying "I shipped the feature AND verified quality across 5 dimensions." That's the difference between junior and senior thinking.

**Time:** 2–3 minutes | **Use when:** Asked about quality, testing, or code standards

---

### **Q28: Tell me about a time you got stuck. How did you debug it with Claude?**

Great question. This is where the tool actually shines. Real example: Iteration 14 (Meal Recommendation Workflow).

**The problem:**

I'd implemented the orchestrator-workers pattern. All three workers (analyze photo, retrieve RAG context, log cost) were supposed to run in parallel. But when I tested it, latency was only slightly better than the sequential version. Something was wrong.

**Initial debug (wrong approach):**

I thought maybe asyncio wasn't actually running things in parallel. So I added print statements:
```python
async def worker_analyze(photo):
    print("Starting analysis")
    # ... 2 seconds of work
    print("Finished analysis")
```

Ran it. Saw the prints. Looked like parallelism. But still slow.

**Where I got stuck:**

The metrics looked wrong. If three tasks run in parallel, I should pay the cost of the longest task. But I was measuring 55 seconds for a 7-day plan (7 parallel iterations × 8 seconds each). That's sequential behavior, not parallel.

**Claude's help:**

I showed Claude the orchestrator code and said "This should be parallel, but it's running sequentially. Where's the bug?"

Claude helped me think through:
1. Are the tasks actually independent? (Worker 2 needs Worker 1's output? No, all independent.)
2. Are they actually launching in parallel? (Let me trace the asyncio code... yes, using create_task.)
3. Is there a semaphore or lock blocking them? (Check the database connection pool... ah!)

**The bug:**

SQLAlchemy's connection pool had `pool_size=1` by default. All three workers were waiting for a single database connection. They weren't actually parallel—they were queued on the database.

**The fix:**

```python
pool = create_engine(
    db_url,
    poolclass=NullPool,  # <-- Changed this
    # ... other options
)
```

With a proper connection pool, all three workers could hit the database simultaneously. Latency dropped from 60 seconds to 18 seconds.

**What I learned:**

When you're stuck, think layered:
1. Is the *logic* correct? (Yes, workers are independent)
2. Is the *orchestration* correct? (Yes, asyncio.gather works)
3. Is the *infrastructure* a bottleneck? (Ah! Database connection pool)

Claude helped me move through these layers systematically instead of just guessing.

**How I documented this:**

BUGLOG.md for Iteration 14:
```
## Blocker: Orchestrator not actually parallelizing
- Measured latency: still 60s (should be ~18s)
- Diagnosis: SQLAlchemy connection pool had pool_size=1
- Root cause: Sequential database access, not parallel
- Fix: Created separate connection pool for async workers
- Result: Latency 60s → 18s ✓
- Regression test: test_orchestrator_workers_parallelize
```

**Time:** 2–3 minutes | **Use when:** Asked about debugging, problem-solving, learning from mistakes

---

### **Q29: How do you handle iteration when working with AI? Does your approach to prompting change between exploration and execution?**

Yes, dramatically. I've learned to use different prompting strategies for different phases.

**Exploration Phase Prompting (Discovery):**

Here I want Claude to help me think, not write code yet. My prompts are open-ended:

"I need to build semantic caching for meal embeddings. The tradeoff I'm thinking about is: should I use pgvector or a simpler in-memory solution? What are the pros and cons? What would you do, and why?"

I'm not asking for code. I'm asking for reasoning. Claude helps me:
- Think through the implications (pgvector is durable, but overhead)
- Consider edge cases (what if the database goes down?)
- Anticipate future constraints (will this scale to 100k users?)

**Execution Phase Prompting (Building):**

Now I'm specific and detailed:

"I've decided to use pgvector with a 0.82 similarity threshold. Here's the design:
1. Embed meal photos using sentence-transformers/MiniLM-L6
2. Store embeddings in pgvector
3. Query using cosine similarity
4. Cache hit if similarity > 0.82

Show me:
- The SQLAlchemy model for storing embeddings
- The query to find similar embeddings
- Error handling if pgvector is unavailable

Use this pattern: [I reference existing code from the repo]"

Now Claude has a blueprint. It's not "write me a caching system." It's "implement step 1 following this exact pattern."

**Testing Phase Prompting (Validation):**

"I need to measure the quality of this cache at different thresholds. Can you:
1. Generate a test function that measures hit rate and false positive rate
2. Load real meal photo embeddings (I have 150 samples)
3. Test thresholds 0.70, 0.75, 0.80, 0.82, 0.85, 0.90, 0.95
4. Return a table: threshold → hit rate → false positive rate

Use the pytest framework."

This is directing Claude to a specific task, not asking for open-ended help.

**Why this three-phase approach matters:**

- **Exploration:** Claude helps you *think*, not code prematurely
- **Execution:** Claude helps you *build faster*, not invent architecture
- **Testing:** Claude helps you *measure*, not guess

If I skip exploration and go straight to execution, Claude codes something that doesn't fit my system. If I don't test, I ship something that's broken.

**Real example from Iteration 13 (Cost Optimization):**

Exploration phase: "I'm paying $1.50/user/day. The major costs are: food analysis (photo → Claude vision), RAG retrieval (embedding + vector search), and logging. Which is the bottleneck? How would you optimize?"

Claude analyzed all three. Helped me realize RAG was 60% of the cost, not food analysis.

Execution phase: "Let's optimize RAG retrieval. Instead of full vector search, implement hybrid: BM25 for exact matches + vector for semantic similarity + RRF (reciprocal rank fusion) to combine. Here's the BM25 schema... implement the query."

Testing phase: "Measure recall at each strategy: pure vector, pure BM25, hybrid. Also measure latency. Here's the data... which one wins?"

Result: Hybrid search achieved 91% recall vs 78% vector-only. And it was *faster*.

**How I communicate this to future me (or next developer):**

PHASES.md captures the approach:
```
Phase 3: Cost Optimization (Exploration)
- Identified: RAG accounts for 60% of cost (not food analysis)
- Decision: Optimize RAG retrieval, not model selection

Phase 4: Cost Optimization (Execution)
- Implemented: Hybrid search (BM25 + vector + RRF)
- Pattern: [link to code example]

Phase 5: Cost Optimization (Validation)
- Measured: 91% recall (vs 78% vector-only)
- Latency: 200ms (acceptable)
```

**Time:** 2–3 minutes | **Use when:** Asked about working with AI, iteration philosophy, or how you think about building features

---

### **Q30: You mention "Iteration 20" and "20 phases"—how do you structure long-running projects? How do you avoid getting lost?**

This is the big-picture organization. I've now shipped 20 iterations over ~4 months. Here's how I keep it coherent.

**Iteration = One Feature**

Each iteration is one logical unit of work. Not "month's worth of work" but "one problem solved."

Examples:
- Iteration 11: Build evaluation pipeline (so I can measure if outputs are good)
- Iteration 12: Implement semantic caching (solve the "redundant API calls" problem)
- Iteration 13: Cost optimization (solve the "too expensive" problem)
- Iteration 14: Orchestrator-workers pattern (solve the "too slow" problem)

Each iteration is 3-10 days of work, not weeks.

**Dependencies are explicit:**

Before I start Iteration 12, I check: "Do I have Iteration 11 (evaluation)? Yes—now I can measure cache quality."

This prevents scope creep. I can't start Iteration 14 (orchestration) until I have Iteration 12 (caching) and Iteration 13 (cost control). Linear dependency chain.

**CLAUDE.md is the north star:**

Every session, I read CLAUDE.md. It tells me:
- What iteration am I on?
- What's completed (11-19)?
- What's in progress (20)?
- What's paused (21, job search agent)?

Real state of the project, always up-to-date.

**BUGLOG.md prevents "lost context" between sessions:**

If I don't touch the project for 2 weeks, I read:
1. CLAUDE.md (which iteration am I on?)
2. BUGLOG.md from the current iteration (what was blocking me?)

5 minutes later, I'm caught up.

**Iteration folder structure prevents chaos:**

```
docs/iterations/
  11-eval-pipeline/
    PLAN.md
    PHASES.md
    BUGLOG.md
    SUMMARY.md
  12-semantic-cache-production/
    PLAN.md
    PHASES.md
    BUGLOG.md
    SUMMARY.md
  13-cost-and-latency/
    ...
```

Not a giant mess of files. Each iteration is self-contained.

**Lessons learned at scale (20 iterations):**

1. **Small iterations > big features** — Iteration 12 took 6 days. If I'd tried to do "all caching, all optimization, all orchestration" in one go, it would take 30 days and I'd be lost.

2. **Document *during*, not after** — BUGLOG.md written daily. Not "write it at the end" (it's too late, you've forgotten the details).

3. **Explicit dependencies prevent backtracking** — Before starting Iteration 14, I checked: "Does Iteration 12 (caching) work? Yes." No surprises mid-way.

4. **SUMMARY.md captures "why," not just "what"** — "Why did I choose 0.82 threshold?" is in SUMMARY.md. Future me doesn't re-debate the decision.

**Time:** 2–3 minutes | **Use when:** Asked about managing complexity, long-term projects, or how you'd structure something bigger

---

### **Q31: You completed a 10-week structured learning journey (6 phases). How did you measure learning progress? How do you know you got better?**

This is my favorite question because it shows the rigor behind the project.

**Measurement Framework:**

I tracked progress on two axes: **knowledge** and **capability**.

**Knowledge (Concepts Learned):**

Phase 1: API design, prompt engineering, output control  
Phase 2: Output validation, evaluation pipelines  
Phase 3: RAG, semantic search, embeddings  
Phase 4: Cost optimization, model selection  
Phase 5: Agents, workflows, orchestration patterns  
Phase 6: MCP servers, ecosystem integration  

For each concept, I asked: "Can I explain this to someone?" If not, I didn't move on.

**Capability (Production Implementation):**

But knowing a concept ≠ ability to use it. So I measured: "Can I implement this in production? Does it work?"

Examples:
- Phase 2: "Can I build an evaluation pipeline that catches 90% of bad outputs?" (Measured: 98.3% caught ✓)
- Phase 3: "Can I tune a semantic cache threshold from 40% hit rate to 85%?" (Measured: achieved 85% ✓)
- Phase 5: "Can I parallelize meal planning from 60s to <25s?" (Measured: achieved 18s ✓)

**Structured Assessment:**

I created a "7-layer LLM engineering capability profile" tracking seven areas:

| Layer | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 | Phase 6 |
|-------|---------|---------|---------|---------|---------|---------|
| Prompt Eng | 3/5 | 4/5 | 4/5 | 4/5 | 4.5/5 | 4.5/5 |
| Output Control | 2/5 | 5/5 | 5/5 | 5/5 | 5/5 | 5/5 |
| Augmentation | 2/5 | 2/5 | 4/5 | 4.5/5 | 4.5/5 | 4.5/5 |
| Reliability | 2/5 | 3/5 | 4/5 | 4.5/5 | 5/5 | 5/5 |
| Agents | 1/5 | 1/5 | 2/5 | 2.5/5 | 5/5 | 4.5/5 |
| Optimization | 1/5 | 1/5 | 1.5/5 | 4/5 | 4/5 | 4.5/5 |
| Ecosystem | 1/5 | 1/5 | 1.5/5 | 2/5 | 3/5 | 4.5/5 |

This is in `docs/learning/01_capability_profile/`. Not a guess, but *evidence-based* assessment.

**End-of-Phase Retrospectives:**

At the end of each phase, I wrote a retrospective:
- What did I learn?
- What surprised me?
- What would I do differently?
- What's the next bottleneck?

Example from Phase 5 (Agents) retrospective:
```
Before: I thought agents would be the default pattern.
After: Agents are 5% of problems. Workflows are 95%.
Surprise: Orchestrator-workers gave 3.3x latency improvement.
Next: Build multi-agent coordination patterns.
```

**Metrics that proved progress:**

- **Phase 2:** JSON parse success 97.2% → 100%
- **Phase 3:** Cache hit rate 40% → 85%
- **Phase 4:** Daily cost $12 → $2 (83% savings)
- **Phase 5:** Latency 60s → 18s (67% improvement)
- **Phase 6:** Integration time 30min → 2min (15x faster)

These are objective. Not "I learned agents" but "I can now parallelize meal planning 3.3x faster using the right pattern."

**Why this matters:**

Most people say "I took a course on LLM engineering." I say "I implemented RAG on production data, tuned it to 91% recall, and documented every decision." That's credible proof of learning.

**Time:** 2–3 minutes | **Use when:** Asked about learning, growth, or how you assess your own skills

---

### **Q32: How do you use git and commit discipline in a learning context? Why does every commit have a message?**

This is where the rigor really shows. Commits aren't just "save work." They're documentation.

**Commit Message Format:**

I follow Conventional Commits:
```
feat(semantic-cache): implement 0.82 threshold tuning

When a user uploads similar meal photos, return cached analysis
instead of re-analyzing. Threshold 0.82 achieves 85% cache hit
with minimal false positives (1%).

Measured on 150 real meal photos using cosine similarity search.
Added regression test: test_semantic_cache_threshold_tuning.

Closes #42
```

**Why every detail matters:**

1. **Type (feat/fix/docs)** — Is this a new feature or a bug fix?
2. **Scope (semantic-cache)** — What part of the system?
3. **Subject (implement 0.82 threshold tuning)** — What did I do?
4. **Body (Why this matters, how it was measured)** — Why should future me care?
5. **Closing issue (Closes #42)** — Trace to the work item

**Real benefit:**

One year later, I want to know: "Why did I choose 0.82?" I can `git log --grep="0.82"` and find the commit. The message tells me:
- I tested on 150 real meals
- 0.82 hit 85% cache with 1% false positives
- I added a regression test

Future me knows the *reasoning*, not just the code.

**What NOT to commit:**

- ❌ "wip" (work in progress—incomplete)
- ❌ "fixes" (no context)
- ❌ Multiple unrelated changes in one commit
- ❌ Failing tests (every commit should pass tests)

**Atomic commits:**

Each commit is one logical change. If I:
1. Add semantic caching
2. Fix a timezone bug
3. Add monitoring

Those are *three* commits, not one. This allows me to:
- Understand one change at a time
- Revert one change if needed (rollback the cache but keep the timezone fix)
- Trace bugs to the specific commit that introduced them

**Learning context:**

Because I'm iterating rapidly, clean commits are *critical*. Otherwise:
- Day 7: "Why does the cache not work?" I read the commit messages and understand the evolution
- Day 10: "Let's revert the old threshold tuning and start fresh" — I can cleanly revert commits 3-5
- Week 3: "What did I learn in Phase 3?" — I read Phase 3 commits and see the story

**Real example from Iteration 12:**

```
Commit 1: feat(embedding): add MiniLM-L6 embeddings for meal photos
Commit 2: feat(pgvector): create embedding store in PostgreSQL
Commit 3: feat(semantic-cache): implement threshold search
Commit 4: test(semantic-cache): measure hit rate at different thresholds
Commit 5: fix(semantic-cache): false positives at threshold 0.95, retune to 0.82
Commit 6: docs(iteration-12): add SUMMARY.md with findings
```

Reading these commits in order tells the *story* of how I built semantic caching. Not just the code, but the *thinking*.

**Time:** 2–3 minutes | **Use when:** Asked about code discipline, collaboration, or how you keep projects maintainable

---

## SECTION E: Frontend, Database & iOS Architecture (6 Q&As)

**When to use:** Full-stack interviews, "Tell me about your iOS app" questions, or when asked about architecture decisions beyond just the LLM backend.

**Note on framing "LLM-assisted iOS":** Your iOS implementation was done with Claude's help. Don't hide this—own it. Frame it as: "I accelerated iOS development using AI pair programming, which let me focus on architecture and UX rather than boilerplate. The result is clean, well-structured code that follows iOS best practices."

---

### **Q33: Walk me through your iOS architecture. Why MVVM? How does it handle the backend integration?**

I use MVVM (Model-View-ViewModel) with SwiftUI and dependency injection. Here's the structure:

**Layer 1: Models (M)**
```
Core/Models/
  - FoodLog.swift (Codable structs matching backend schemas)
  - UserProfile.swift
  - Auth.swift
```

These are lightweight, just Codable structs that mirror the API responses. No business logic here.

**Layer 2: Services (where the real work happens)**
```
Core/Services/
  - APIClient.swift (HTTP communication, error handling, token management)
  - AuthService.swift (@StateObject, manages login state and Keychain storage)
  - PhotoCaptureService.swift (iOS camera + photo library integration)
  - ProfileService.swift (CRUD for user profile)
  - RecommendationService.swift (Calls /recommendations endpoint)
```

Each service is a single responsibility. AuthService doesn't know how to take photos. PhotoCaptureService doesn't handle API calls.

**Layer 3: ViewModels (V-M)**
```
Features/Insights/
  - InsightsViewModel.swift (@MainActor ObservableObject with @Published properties)
  - InsightsView.swift (SwiftUI, observes the ViewModel)
```

The ViewModel is the "glue":
- Calls services (e.g., `RecommendationService.getRecommendations()`)
- Publishes state (@Published) that the View observes
- Handles async work (async/await)
- Format data for display (e.g., "12.5g" from 12.54g)

**Real example:**

```swift
@MainActor
class InsightsViewModel: ObservableObject {
    @Published var isLoading = false
    @Published var insights: InsightsResponse?
    @Published var errorMessage: String?
    
    private let api = APIClient.shared
    
    func loadInsights() async {
        isLoading = true
        errorMessage = nil
        
        do {
            insights = try await api.request("GET", path: "/nutrition/insights")
            isLoading = false
        } catch let error as APIError {
            errorMessage = error.errorDescription
            isLoading = false
        }
    }
}
```

When `loadInsights()` is called, the View automatically updates because `@Published` changes trigger re-render.

**Why MVVM?**

1. **Separation of concerns** — View logic ≠ business logic ≠ networking logic
2. **Testability** — Can test ViewModels without a UI
3. **Reusability** — Two views can share the same ViewModel
4. **SwiftUI native** — ObservableObject + @Published is designed for MVVM

**Dependency Injection:**

At app launch:
```swift
@main
struct NomNomApp: App {
    @StateObject private var authService = AuthService()
    
    var body: some Scene {
        WindowGroup {
            if authService.isAuthenticated {
                ContentView()
                    .environmentObject(authService)  // <-- injected into view hierarchy
            } else {
                LoginView()
                    .environmentObject(authService)
            }
        }
    }
}
```

Every view in the app can access `@EnvironmentObject var authService: AuthService` without passing it explicitly.

**Backend Integration:**

All network calls go through APIClient:
```swift
class APIClient {
    static let shared = APIClient()
    var token: String?  // JWT token from Keychain
    
    func request<T: Decodable>(...) async throws -> T {
        // Add Authorization header with token
        // Encode request body
        // Decode response
        // Handle errors (401 → onUnauthorized callback)
    }
}
```

When the user logs in:
1. AuthService calls `APIClient.request("POST", path: "/auth/login", body: credentials)`
2. Backend returns JWT token
3. AuthService stores token in Keychain
4. AuthService sets `APIClient.setToken(token)`
5. All subsequent requests include `Authorization: Bearer {token}`

**Time:** 2–3 minutes | **Use when:** Asked about iOS architecture, or how you structured a full-stack app

---

### **Q34: Walk me through your database schema. Why did you design it this way?**

The schema is designed to support three core features: food tracking, personalization, and LLM caching.

**Core Tables:**

**Users table**
```sql
id (PK)
email (unique, indexed)
hashed_password
created_at
```

Simple, minimal. Email is the natural key for login.

**UserProfile table**
```sql
id (PK)
user_id (FK to users, unique) ← one-to-one relationship
age, gender, height_cm, weight_kg
activity_level, goal
allergies (JSON), dietary_restrictions (JSON), medical_conditions (JSON)
calorie_target, protein_target, carb_target, fat_target
notification_enabled
created_at, updated_at
```

**Why separate from Users?**

Users table is for authentication (email, password). UserProfile is for health data. Clear separation. Also, a user *might* not have filled out their profile yet (nullable), so separating makes that explicit.

**Why JSON for allergies/restrictions?**

Because they're flexible lists. A user might have 0 allergies or 10. SQL arrays are one option, but JSON is more portable (easier to serialize to API responses). I chose JSON.

**FoodLog table** (the core of the app)
```sql
id (PK)
user_id (FK to users, indexed)
photo_path (string)
food_name, calories, protein_g, carbs_g, fat_g
food_category, cuisine_origin, meal_type
cat_roast (the AI's witty comment)
ai_raw_response (JSON, for debugging)
embedding (pgvector, for semantic cache)
is_user_corrected (boolean, for evaluating AI accuracy)
logged_at (when user ate it, timezone-aware)
created_at
```

**Key decisions:**

1. **embedding column (pgvector)** — This is how semantic caching works. When a new photo comes in, I embed it, search for similar embeddings in this column, and return cached results. Crucial for the 85% cache hit rate.

2. **ai_raw_response (JSON)** — I store the raw Claude response for debugging. If recommendation accuracy drops, I can inspect what Claude actually returned.

3. **is_user_corrected** — I track corrections because that's my evaluation signal. If Claude said "200 calories" but the user corrected it to "350 calories," that's valuable data for measuring accuracy.

4. **logged_at (timezone-aware)** — This was a critical bug in Iteration 18. If I use naive datetimes, DST transitions break date arithmetic. Now it's timezone-aware, so "what did I eat today?" works correctly even across DST boundaries.

**NutritionChat table** (for multi-turn conversations)
```sql
id (PK)
user_id (FK to users, indexed)
message (text, could be user or AI)
is_user_message (boolean)
timestamp
```

Simple thread. Users can have multiple conversations, each conversation has multiple messages.

**Indexes:**

```sql
CREATE INDEX idx_food_logs_user_id ON food_logs(user_id);
CREATE INDEX idx_food_logs_logged_at ON food_logs(logged_at);
CREATE INDEX idx_users_email ON users(email);
```

Why these? Queries are typically:
- "Get all food logs for user X" (indexed by user_id)
- "Get food logs from the last 7 days" (indexed by logged_at)
- "Find user by email at login" (indexed by email)

**Why pgvector for embeddings?**

pgvector is a PostgreSQL extension that natively supports vector operations (cosine similarity, L2 distance). Alternatives:
- Redis (fast but ephemeral, not durable)
- Elasticsearch (powerful but overkill for this use case)
- pgvector (native to Postgres, ACID guarantees, indexed fast enough for our scale)

**Scalability notes:**

At 100k users × 3 meals/day = 300k food logs/day. Indexes keep queries fast. Embedding vectors are 384-dimensional (MiniLM-L6 model), stored as `vector(384)` in pgvector.

**Time:** 2–3 minutes | **Use when:** Asked about database design, schema decisions, or how you handle large datasets

---

### **Q35: Tell me about authentication. How do you store the JWT token securely on iOS?**

Short answer: JWT tokens go in **iOS Keychain**, not UserDefaults or local files.

**Why not UserDefaults?**

UserDefaults is plaintext on disk. If a phone is stolen or an attacker gains file system access, they can read the token. That's a security violation.

**How Keychain works:**

iOS Keychain is an encrypted key-value store. The OS encrypts the data at rest. Only your app can decrypt it (the app is tied to a code-signing identity).

**Implementation:**

```swift
class KeychainService {
    static let shared = KeychainService()
    
    func saveToken(_ token: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: "nomnom_token",
            kSecValueData as String: token.data(using: .utf8)!
        ]
        
        SecItemDelete(query as CFDictionary)
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else {
            throw KeychainError.saveFailed
        }
    }
    
    func getToken() throws -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: "nomnom_token",
            kSecReturnData as String: true
        ]
        
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        
        guard status == errSecSuccess else {
            if status == errSecItemNotFound { return nil }
            throw KeychainError.retrieveFailed
        }
        
        guard let data = result as? Data,
              let token = String(data: data, encoding: .utf8) else {
            throw KeychainError.decodingFailed
        }
        
        return token
    }
}
```

**AuthService integration:**

```swift
@MainActor
class AuthService: ObservableObject {
    @Published var isAuthenticated = false
    private let keychain = KeychainService.shared
    
    func login(email: String, password: String) async throws {
        let response: LoginResponse = try await APIClient.shared.request(
            "POST", path: "/auth/login",
            body: LoginRequest(email: email, password: password)
        )
        
        try keychain.saveToken(response.token)
        APIClient.shared.setToken(response.token)
        self.isAuthenticated = true
    }
    
    func restoreSession() {
        if let token = try? keychain.getToken() {
            APIClient.shared.setToken(token)
            self.isAuthenticated = true
        }
    }
}
```

**Token expiry:**

When a 401 response comes back:
```swift
case 401:
    self.onUnauthorized?()  // Notify app to go to login
    throw APIError.unauthorized
```

**Security best practices:**

✅ Token in Keychain (encrypted)  
✅ HTTPS only (no HTTP)  
✅ Token in Authorization header (not in body)  
✅ Clear token on logout  
✅ Handle 401 gracefully (re-auth)  

**Time:** 2–3 minutes | **Use when:** Asked about security, authentication, or sensitive data on mobile

---

### **Q36: Tell me about a mobile-specific challenge you solved.**

Real example: **Photo upload with retry logic and progress tracking.**

**The Problem:**

Users on bad networks were losing photos. Uploads would fail and get stuck.

**Root causes:**

1. **Network unreliability** — 4G → WiFi handoff interrupted uploads
2. **Large payloads** — Photos are 2-3MB, slow networks take 10-30s
3. **No retry** — One failure = total loss

**Solution: Exponential backoff retry**

```swift
func uploadPhoto(_ imageData: Data) async throws {
    let maxRetries = 3
    var delayMillis = 100
    var lastError: Error?
    
    for attempt in 1...maxRetries {
        do {
            return try await APIClient.shared.upload(
                path: "/food/analyze", imageData: imageData
            )
        } catch let error as URLError where error.isNetworkError {
            lastError = error
            if attempt < maxRetries {
                let delaySeconds = Double(delayMillis) / 1000.0
                try await Task.sleep(seconds: delaySeconds)
                delayMillis *= 2
            }
        }
    }
    
    throw lastError ?? APIError.networkError(...)
}
```

Delays: 0 → 100ms → 200ms (gives server time to recover, not hammering)

**Progress tracking:**

```swift
@Published var uploadProgress: Double = 0.0

func captureAndAnalyze(_ image: UIImage) async {
    uploadProgress = 0.5  // 50% while uploading
    let response = try await uploadPhoto(imageData)
    uploadProgress = 1.0
}
```

**Other challenges:**

1. **Memory on large galleries** — Lazy loading + thumbnails
2. **Background interrupted work** — Save state, restore on reopen
3. **Keyboard stickiness** — `UIApplication.shared.sendAction(#selector(UIResponder.resignFirstResponder), ...)`

**Time:** 2–3 minutes | **Use when:** Asked about debugging, resilience, or mobile-specific problems

---

### **Q37: How do you keep iOS and backend data in sync?**

Short answer: **Remote Source of Truth (backend) with Local Caching**

Backend is always the source of truth. iOS caches for offline access, but backend wins on conflicts.

**Pattern: Request → Cache → Display**

```swift
func loadFoodLogs() async {
    do {
        // 1. Request from backend (source of truth)
        foodLogs = try await APIClient.shared.request("GET", path: "/food/logs?limit=30")
        
        // 2. Cache locally (for offline access)
        CoreDataManager.shared.save(foodLogs)
        
    } catch {
        // 3. If request fails, load from local cache
        foodLogs = CoreDataManager.shared.fetchFoodLogs()
    }
}
```

**Local caching options:**

- **UserDefaults** — Simple, but limited for large datasets
- **Core Data** — Full database, relationships, indexing, predicates
- **SQLite** — Lightweight, fast, ACID guarantees

I chose **Core Data** because I need relationships and indexing.

**Conflict resolution: Backend wins**

```swift
func syncFoodLogs() async {
    let remoteLogs = try await APIClient.shared.request(...)
    CoreDataManager.shared.deleteAll()
    CoreDataManager.shared.save(remoteLogs)
}
```

Or merge strategically:

```swift
let merged = remoteLogs.map { remote in
    local.first { $0.id == remote.id } ?? remote
}
// Prefer remote version if newer, else keep local
```

**Offline behavior:**

- User logs meal → Save locally immediately (user sees it)
- Sync to backend → If offline, retry when network returns
- Mark synced when successful

**Time:** 2–3 minutes | **Use when:** Asked about data persistence, offline support, or syncing

---

### **Q38: You built the iOS app with LLM assistance (Claude Code). How do you communicate that in interviews?**

**The straightforward answer:**

"I used Claude Code as an intelligent pair programmer. The architecture, design decisions, and quality standards came from me. Claude helped me accelerate implementation—handling boilerplate, suggesting patterns, debugging—so I could focus on architecture and UX.

The result is clean, well-structured code that follows iOS best practices. I understand the codebase entirely."

**Why this is a strength:**

1. **Productivity** — Shipped 5 iOS features in 4 weeks (faster than solo developer)
2. **Code quality** — Claude suggested patterns I might have missed
3. **Practical skill** — Using AI tools effectively is increasingly valuable
4. **No black box** — I can explain every decision

**How to demonstrate understanding:**

- Explain *why* you chose MVVM (Q33)
- Walk through Keychain implementation (Q35)
- Discuss trade-offs ("Core Data vs. SQLite because...")
- Debug a hypothetical iOS bug

If you can do all that, interviewers will be confident you own the work.

**Red flags (what NOT to say):**

❌ "I don't understand the iOS code"  
❌ "Claude wrote the frontend, I just did backend"  
❌ "I copied code without understanding it"  

**What TO say:**

✅ "I architected with MVVM. Claude helped me implement faster."  
✅ "I debugged the photo upload retry logic."  
✅ "I understand the full iOS stack: SwiftUI, async/await, Keychain, URLSession, Core Data."  

**Context:**

Professionals use Copilot and ChatGPT all the time. The bar is: "Can you maintain, debug, extend this code?" If yes, it doesn't matter how it was initially written.

**Time:** 1–2 minutes | **Use when:** Asked "How did you build the iOS app?" or if there's any skepticism about understanding/quality

---

| Metric | Value | Why It Matters |
|--------|-------|---|
| **Cache Hit Rate** | 85% | Reduces redundant API calls; fundamental to cost savings |
| **Cost Reduction** | 83% | $12/day → $2/day (Sonnet + caching) |
| **Latency Improvement** | 67% | 60s → 18s (orchestrator-workers) |
| **Accuracy** | 88% | Food recognition (Sonnet choice justified) |
| **Threshold (0.82)** | Sweet spot | 85% recall, 5% false positives (empirically measured) |
| **RAG Recall** | 91% | Hybrid search beats pure vector (78%) or BM25 (82%) |
| **JSON Success Rate** | 100% | tool_choice improvement (97.2% → 100%) |
| **Eval Cost** | $0.04/run | Hybrid grading vs. $0.30 model-only |

---

**Last Updated:** June 16, 2026  
**Status:** Ready for interviews  
**Use this for:** Technical screening, system design, follow-up depth
