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

## SECTION F: RAG, Agents, Prompt Engineering & Tools (20 Q&As)

**When to use:** LLM-focused interviews, "Tell me about your RAG system," or deep technical dives on prompting and agents.

**Context from NomNom:** Your RAG achieves 91% recall. Your prompts are templated for iteration. Your agents orchestrated for speed. Your tools are discoverable via MCP. This section shows the *depth* of your LLM engineering.

---

### **RAG Deep Dive (6 Q&As)**

### **Q39: How do you evaluate RAG quality? What metrics matter?**

RAG quality has three dimensions, and you can't just measure one:

**Dimension 1: Retrieval Quality**

Does the RAG find the right documents? Measure with **Recall@K**:
```
Recall@5 = (# relevant docs in top 5) / (# total relevant docs)
```

If a user asks "How much protein should I eat?" and the relevant info is in position 7, you have 0% Recall@5.

In NomNom, I measure this against a ground-truth dataset:
- 50 user questions
- Manual labels: "Here are the 2-3 relevant knowledge base entries for this question"
- Run RAG retrieval
- Measure: Did those entries appear in top-5?

I track this as a metric. If Recall@5 drops below 85%, I know the retrieval is degrading.

**Dimension 2: Generation Quality**

Does Claude generate *good* responses using the retrieved context? This is harder to measure, but I use:

**Faithfulness:** Does the response stay grounded in the retrieved context, or does it hallucinate?

```python
# Measure: Does the response cite the sources?
# Does it contradict the retrieved docs?
# Example:
Retrieved: "Protein needs are 0.8g per kg of body weight"
Response: "You need 1.2g per kg"  ← Contradiction! Faithfulness = 0%
```

**Relevance:** Is the response actually addressing the user's question?

```python
# Measure: Does a model-based evaluator think the response is relevant?
# Prompt Claude: "User asked X. Response is Y. Is Y relevant to X?"
# Score: 0-1
```

**Dimension 3: User Satisfaction**

At scale, the gold standard: **Do users think the recommendations are good?**

I track this with a simple metric:
```
user_feedback_score = (num positive corrections) / (num corrections)
```

If a user accepts 95% of recommendations without correction, that's good.

**In practice for NomNom:**

I built a dashboard tracking:
- Recall@5: 91% (good—finding relevant docs)
- Hallucination rate: <5% (good—Claude stays grounded)
- User correction rate: <5% (good—recommendations are trusted)

**What I do when metrics drop:**

If Recall@5 drops to 80%, I investigate:
1. Did the knowledge base change?
2. Did the embeddings degrade? (retrain with fresher data)
3. Did the query understanding get worse? (maybe the user asking differently)

**Time:** 2–3 minutes | **Use when:** Asked "How do you know if RAG is working?" or "What metrics matter?"

---

### **Q40: Tell me about your hybrid search approach. Why BM25 + vector + RRF instead of pure vector search?**

Pure vector search (similarity-based) is beautiful but flawed. Pure BM25 (keyword-based) is reliable but brittle. I combined them.

**Pure Vector Search Problems:**

```
User query: "How much protein?"
Vector embedding: [0.2, 0.5, ..., 0.1]  (semantic meaning)

Retrieved doc: "Protein is an amino acid"
Vector embedding: [0.2, 0.5, ..., 0.1]  (looks similar)

Retrieved doc: "My protein powder tastes good"
Vector embedding: [0.3, 0.4, ..., 0.2]  (also similar?)

Problem: Semantic similarity doesn't distinguish "protein as a nutrient" 
from "protein powder as a product."
```

**Pure BM25 Problems:**

```
User query: "How much protein?"
BM25 matches: "protein" (exact match)

Retrieved: "My protein powder tastes good"  ← Irrelevant, but has the word
Not retrieved: "Amino acids..." (semantically relevant, but no exact match)
```

**Hybrid Search Solution:**

1. **Run both searches in parallel:**
   ```python
   bm25_results = search_bm25("How much protein?")
   vector_results = search_vector(embedding)
   ```

2. **Rank each result set separately:**
   - BM25 returns: [doc5 (score=8.5), doc2 (score=7.2), doc9 (score=6.1)]
   - Vector returns: [doc5 (score=0.89), doc12 (score=0.87), doc2 (score=0.85)]

3. **Merge using Reciprocal Rank Fusion (RRF):**
   ```python
   rrf_score = 1/(k + rank_from_bm25) + 1/(k + rank_from_vector)
   # k is typically 60
   
   # Example:
   doc5: 1/(60+1) + 1/(60+1) = 0.0330  ← appears in both, high score
   doc2: 1/(60+2) + 1/(60+3) = 0.0319
   doc12: 1/(60+3) = 0.0159  ← only in vector, lower score
   ```

**Result in NomNom:**

| Metric | BM25 Only | Vector Only | Hybrid (RRF) |
|--------|-----------|-------------|--------------|
| Recall@5 | 82% | 78% | 91% |
| Precision@5 | 80% | 75% | 89% |
| Time | 50ms | 200ms | 220ms |

Hybrid wins on relevance (91% recall) with minimal latency penalty (+20ms).

**Why RRF instead of averaging scores?**

Because BM25 scores (0-100) and vector scores (0-1) are on different scales. RRF normalizes them by converting to ranks, then combining ranks. This prevents one modality from dominating the other.

**Time:** 2–3 minutes | **Use when:** Asked "How do you improve RAG?" or "Vector vs BM25?"

---

### **Q41: Tell me about a RAG failure mode you encountered.**

Real example from NomNom: **Stale Knowledge Problem**

**The Failure:**

Week 1: I load the knowledge base with nutrition facts:
```
"The daily protein target is 0.8g per kg of body weight"
```

Week 8: Nutrition science evolves. New studies suggest 1.0g per kg for active users. But the knowledge base still has the old value.

User asks: "How much protein do I need?"
Claude retrieves the stale doc and responds with outdated advice.

**Root Cause:**

Knowledge bases don't auto-update. You have to maintain them. I didn't.

**How I Fixed It:**

1. **Add a "last verified" timestamp to each doc:**
   ```python
   class KnowledgeDoc(Base):
       id: int
       content: str
       source: str
       created_at: datetime
       last_verified_at: datetime  # <-- NEW
       is_deprecated: bool = False
   ```

2. **Mark docs as deprecated, don't delete:**
   ```python
   # Old doc
   doc.is_deprecated = True
   doc.last_verified_at = None
   
   # New doc
   new_doc = KnowledgeDoc(
       content="New guidance...",
       last_verified_at=datetime.now()
   )
   ```

3. **During retrieval, deprioritize stale docs:**
   ```python
   # When retrieving, exclude docs older than 6 months
   results = search(...).filter(
       last_verified_at > datetime.now() - timedelta(days=180)
   )
   ```

4. **Add a verification process:**
   Every 3 months, I manually review top-20 knowledge docs. For each, I verify:
   - "Is this still true?"
   - "Is there newer information?"
   - If yes, update `last_verified_at`

**Lesson:**

RAG systems need maintenance. Knowledge degrades. Plan for it.

**Other RAG failures:**

- **Context confusion:** Retrieved doc is relevant to the *topic* but not the *question* (e.g., retrieved "history of protein research" when user asked "how much should I eat?")
- **Missing context:** Retrieved doc answers 80% of the question, user has to infer the other 20%
- **Citation errors:** Response cites a doc that doesn't support the claim (hallucinated citations)

**Time:** 2–3 minutes | **Use when:** Asked "How do you debug RAG?" or "What can go wrong?"

---

### **Q42: How do you structure knowledge base chunks for RAG? What's your chunking strategy?**

Chunking is a **hidden lever** that nobody talks about, but it massively impacts RAG quality.

**Problem: The Goldilocks Zone**

Chunks too small (100 tokens):
```
Chunk 1: "Protein is an essential macronutrient"
Chunk 2: "found in eggs, meat, fish, and legumes"
Chunk 3: "The daily requirement is 0.8g per kg"

User asks: "What should I eat for protein?"
Retrieved: Chunk 2 (relevant, but incomplete—missing the "why" from Chunk 1)
```

Chunks too large (2000 tokens):
```
Chunk 1: [Entire article: history of protein, requirements, sources, 
          cooking methods, recipes, etc.]

User asks: "How much protein?"
Retrieved: Entire article (lots of noise—cooking methods aren't relevant)
Claude has to filter through irrelevant information.
```

**My Strategy: Semantic Chunking**

Instead of arbitrary token windows, I chunk on **semantic boundaries**:

```python
# Original document
"""
## Protein Requirements

Protein is essential for muscle growth.

The daily requirement is:
- Sedentary: 0.8g per kg
- Active: 1.0g per kg
- Athletes: 1.2g per kg

## Sources of Protein

Best sources:
- Animal: eggs, meat, fish
- Plant: beans, lentils, tofu
"""

# Chunked semantically:
Chunk 1: "Protein is essential... [requirement details]"
Chunk 2: "Best sources: [Animal/plant sources]"
```

Each chunk is one coherent idea, typically 200-500 tokens.

**In code:**

```python
class DocumentChunker:
    def chunk_by_semantic_boundaries(self, text):
        # Split on headers (##, ###)
        chunks = []
        current_chunk = ""
        
        for line in text.split("\n"):
            if line.startswith("##") and current_chunk:
                chunks.append(current_chunk)
                current_chunk = line
            else:
                current_chunk += "\n" + line
        
        return chunks
```

**Validation: Measure Quality**

For each chunk, I ask: "Can Claude answer a question with just this chunk?"

```python
for chunk in chunks:
    # Ask Claude: "What's the key question this chunk answers?"
    key_question = claude.generate(f"Summarize the key question: {chunk}")
    
    # Can a typical user question be answered by this chunk alone?
    if len(key_question) < 10:  # Too generic
        flag_as_too_small(chunk)
    
    if len(chunk) > 1000:  # Probably too large
        flag_as_too_large(chunk)
```

**Time:** 2–3 minutes | **Use when:** Asked "How do you prepare data for RAG?" or "Chunking strategy?"

---

### **Q43: How do you handle RAG for multi-turn conversations? Does context from turn 1 affect turn 3?**

This is where RAG gets complex. In a multi-turn conversation:

```
Turn 1: User: "I'm 80kg and active"
Turn 2: User: "How much protein?"
Turn 3: User: "Is that enough?"
```

For turn 3, "that" refers to the protein amount from turn 2. But turn 3 doesn't explicitly say "protein." How does RAG know?

**Naive Approach (Wrong):**

```python
def chat_turn_3(user_message="Is that enough?"):
    # Search RAG for "Is that enough?"
    # Embedding of "Is that enough?" doesn't match knowledge docs
    # Returns nothing relevant
    # Claude: "I don't know what you're referring to"
```

**Better Approach: Expand Query with Conversation Context**

```python
def chat_with_context(user_message, conversation_history):
    # 1. Re-construct the full context from prior turns
    full_context = "\n".join([
        f"Turn {i+1}: User: {msg['content']}"
        for i, msg in enumerate(conversation_history)
    ])
    
    # 2. Expand the query with context
    expanded_query = f"""
    {full_context}
    
    Current question: {user_message}
    """
    
    # 3. Search RAG with the expanded query
    relevant_docs = rag.search(expanded_query)
    
    # 4. Pass both the conversation history and docs to Claude
    response = claude.generate(
        system="You are a nutrition coach.",
        context_docs=relevant_docs,
        messages=[
            {"role": "user", "content": msg["content"]}
            for msg in conversation_history
        ] + [
            {"role": "user", "content": user_message}
        ]
    )
```

**In NomNom Specifically:**

The `/nutrition/chat` endpoint does this:

```python
@app.post("/nutrition/chat")
async def nutrition_chat(user_id: int, message: str):
    # 1. Fetch conversation history
    history = db.query(NutritionChat).filter(
        NutritionChat.user_id == user_id
    ).order_by(NutritionChat.timestamp.desc()).limit(10)
    
    # 2. Build expanded query
    prior_messages = [h.message for h in history]
    expanded_query = "\n".join(prior_messages) + "\n" + message
    
    # 3. RAG retrieval
    relevant_docs = rag_service.search(expanded_query)
    
    # 4. Generate response
    response = claude_api.messages.create(
        model="claude-3.5-sonnet",
        system=get_system_prompt(user_profile),
        messages=[
            {"role": "user", "content": f"Context: {doc}\n\n{message}"}
            for doc in relevant_docs
        ] + conversation_messages
    )
    
    # 5. Store in history
    db.create(NutritionChat(
        user_id=user_id,
        message=message,
        is_user_message=True
    ))
    db.create(NutritionChat(
        user_id=user_id,
        message=response.content,
        is_user_message=False
    ))
```

**Gotchas:**

1. **Conversation length explosion** — Keep only last 10 messages, else token budget explodes
2. **Stale context** — If user said "I'm 80kg" in turn 1, does it still apply in turn 5? (Probably yes, but you need to track this)
3. **Context confusion** — If prior turns mention multiple foods, which one does "that" refer to? Claude usually figures it out, but sometimes misses.

**Time:** 2–3 minutes | **Use when:** Asked "How do you handle conversations?" or "Multi-turn RAG?"

---

### **Q44: Walk me through your prompt A/B testing methodology. How do you measure which prompt is better?**

This is the process I learned in Phase 1 and refined iteratively:

**Setup: Define Success Metric**

Before writing any prompt, I define what "better" means. Not subjective. Measurable.

Examples:
- **Nutrition prompt:** "How many recommended foods does the user accept without correction?"
- **Analysis prompt:** "Does Claude identify all macronutrient gaps in the user's diet?"
- **Chat prompt:** "Does Claude avoid recommending foods the user is allergic to?"

**Test Design: 30-50 examples**

I create a test set:
```python
test_set = [
    {
        "input": "I logged: eggs, rice, spinach",
        "expected_output_contains": ["protein", "calcium"],
        "should_not_contain": ["carbs are bad"]
    },
    ...
]
```

**Variant A: Current Prompt**

```
You are a nutrition coach. Analyze the user's meal and provide:
1. Calorie estimate
2. Macronutrient breakdown
3. One health recommendation
```

**Variant B: Improved Prompt**

```
You are a nutrition coach specializing in personalized health. Analyze the user's meal and provide:
1. Calorie estimate (with confidence range)
2. Macronutrient breakdown
3. Key nutrients in this meal (calcium, iron, etc.)
4. One personalized health recommendation based on the user's health profile
```

**Run Both Variants**

```python
for test_case in test_set:
    # Variant A
    response_a = claude.messages.create(
        model="claude-3.5-sonnet",
        system=PROMPT_A,
        messages=[{"role": "user", "content": test_case["input"]}]
    )
    
    # Variant B
    response_b = claude.messages.create(
        model="claude-3.5-sonnet",
        system=PROMPT_B,
        messages=[{"role": "user", "content": test_case["input"]}]
    )
    
    # Score each response
    score_a = evaluate(response_a, test_case)
    score_b = evaluate(response_b, test_case)
    
    results.append({
        "test": test_case["input"],
        "variant_a_score": score_a,
        "variant_b_score": score_b
    })
```

**Scoring: Model-Based or Rule-Based**

Option 1: **Rule-based** (fast, deterministic)
```python
def evaluate(response, test_case):
    score = 0
    for keyword in test_case["expected_output_contains"]:
        if keyword in response.lower():
            score += 1
    for bad_keyword in test_case["should_not_contain"]:
        if bad_keyword in response.lower():
            score -= 1
    return score
```

Option 2: **Model-based** (expensive, nuanced)
```python
def evaluate(response, test_case):
    evaluation = claude.messages.create(
        model="claude-3.5-sonnet",
        system="You are an evaluation expert. Score this response 1-10.",
        messages=[{"role": "user", "content": f"""
        Expected: {test_case['expected_output']}
        Actual: {response}
        Score: [1-10]
        """}]
    )
    return extract_score(evaluation.content)
```

I use rule-based for fast iteration, then model-based for final validation.

**Results Summary**

```
Prompt A (current):
  Average score: 7.2/10
  Consistency: 68% (6 of 9 examples good)
  Cost: $0.04 per call

Prompt B (variant):
  Average score: 8.1/10
  Consistency: 78% (8 of 10 examples good)
  Cost: $0.04 per call

Winner: Variant B (+0.9 points, +10% consistency, same cost)
```

**Deploy**

In PHASES.md or BUGLOG.md, I document:
```
Prompt A/B test completed:
- Test set: 50 nutrition analysis examples
- Metric: Expected macronutrient coverage
- Variant A: 7.2/10 (current)
- Variant B: 8.1/10 (new)
- Decision: Deploy Variant B
```

**Multi-variate testing**

If I'm testing multiple dimensions:
- Temperature (0.5, 0.7, 1.0)
- Phrasing ("Analyze", "Break down", "Evaluate")
- Detail level (brief, medium, detailed)

I don't test all combinations (3 × 3 × 3 = 27 variants). Instead, I test one variable at a time:
1. Fix temp at 0.7, test phrasing → pick winner
2. Fix phrasing, test detail level → pick winner

**Time:** 2–3 minutes | **Use when:** Asked "How do you optimize prompts?" or "A/B testing?"

---

### **Q45: Tell me about few-shot vs zero-shot prompting. When do you use each?**

This is a fundamental tradeoff I learned and use constantly.

**Zero-Shot: No Examples**

```
System prompt: "You are a nutrition coach. Analyze this meal:"
User: "I ate eggs and toast"

Claude responds based on general knowledge.
No examples shown, so lower prediction power but faster.
```

**Few-Shot: With Examples**

```
System prompt: "You are a nutrition coach. Analyze meals like this:

Example 1:
Meal: "Salmon with broccoli"
Analysis: "High protein (25g), good omega-3s, low carb (8g)..."

Example 2:
Meal: "Rice and beans"
Analysis: "Complete protein (15g), moderate carbs (45g)..."

Now analyze: I ate eggs and toast"

Claude sees the pattern and mimics the style.
```

**When Zero-Shot Is Better:**

1. **The task is simple and unambiguous**
   - Summarize this text
   - Extract dates from this document
   - Classify this food as healthy/unhealthy
   Claude can do this without examples.

2. **You want to reduce latency/cost**
   Each example adds tokens. Few-shot costs more.

3. **Examples might confuse the model**
   If the task is "be creative," examples limit creativity.

**When Few-Shot Is Better:**

1. **The task needs a specific format**
   ```
   Zero-shot: "Analyze this meal"
   Response: Long paragraph, inconsistent format
   
   Few-shot: Show 2-3 examples with exact format (JSON, bullet points)
   Response: Consistent format, predictable
   ```

2. **The task has subtle patterns**
   ```
   Zero-shot: "Is this allergy-safe?"
   Response: Might miss cross-contamination risks
   
   Few-shot: Show 3 examples of what counts as unsafe
   Response: Catches subtle risks the examples covered
   ```

3. **Output quality matters more than cost**
   If accuracy is critical (health advice), few-shot is worth the extra tokens.

**In NomNom:**

**Nutrition Analysis**: Few-shot
```
System: "Analyze meals in this exact format:
{name}: calories, protein_g, carbs_g, fat_g, key_nutrients
Example: Salmon with broccoli: 400, 25, 8, 20, omega-3/B12"

Result: Consistent JSON-like format every time
```

**Health Profile Intake**: Zero-shot
```
System: "Ask the user about their age, weight, activity level"
User: "I'm 30, weigh 75kg, and I work out 4x/week"
Claude: Extracts correctly without examples
```

**Constraint Checking** (allergies): Few-shot
```
System: "Check if the recommendation is safe for this user's constraints:
User: Shellfish allergy, vegetarian
Example safe: Salmon with beans (no shellfish, vegetarian)
Example unsafe: Shrimp pasta (shellfish!)

Recommend: ___"

Result: Never recommends shellfish
```

**Cost vs Quality Trade-off:**

| Task | Zero-Shot | Few-Shot | My Choice |
|------|-----------|----------|-----------|
| Nutrient extraction | 92% accuracy | 97% accuracy | Few-shot |
| Format consistency | 60% | 95% | Few-shot |
| Creative recommendations | 85% | 80% (constrained) | Zero-shot |
| Constraint checking | 88% | 99% | Few-shot |

**Time:** 2–3 minutes | **Use when:** Asked "Zero vs few-shot?" or "When do you use examples?"

---

### **Q46: Tell me about chain-of-thought prompting. Do you use it? When?**

Chain-of-thought (CoT) is powerful but expensive. I use it strategically.

**What is CoT?**

Instead of:
```
Q: "The user is 80kg, active. How much protein?"
A: "100g"
```

With CoT:
```
Q: "The user is 80kg, active. How much protein?

Let's think step by step:
1. Active users need 1.0-1.2g per kg of body weight
2. 80kg × 1.1g = 88g
3. Round up for safety: 100g"
A: "100g"
```

The model shows its reasoning. Two benefits:

1. **Better accuracy** — The model reasons through the problem instead of guessing
2. **Explainability** — User sees *why*, not just the answer

**Cost Trade-off:**

CoT often doubles token usage (you're asking for reasoning):
```
Simple: "Q: ... A: 100g" (100 tokens)
CoT: "Q: ... Let's think... A: 100g" (200 tokens)

2x tokens = 2x cost
```

**When I Use CoT:**

**Use CoT:**
- ✅ Complex reasoning (multi-step math, constraints)
- ✅ Health/safety decisions (want justification)
- ✅ User-facing explanations (explain the recommendation)
- ✅ Quality matters > cost

**Don't Use CoT:**
- ❌ Simple classification (healthy/unhealthy)
- ❌ Extracting facts (What's the calorie count?)
- ❌ Internal batch processing (background jobs)
- ❌ Cost sensitive (high-volume calls)

**In NomNom:**

**CoT Example: Recommend a meal**

User asks: "I'm busy, what should I eat?"
```
System: "Recommend a meal with reasoning.

Step 1: Check user's health profile
- Goals: weight loss, high protein
- Allergies: peanuts
- Preferences: vegetarian

Step 2: Find meals matching all constraints

Step 3: Explain why this meal is good for the user

Meal: [recommendation] because [reasoning]"
```

Result: Longer response, but user understands *why*.

**No-CoT Example: Classify food**

Background task: Categorize logged food
```
System: "Classify this food as breakfast/lunch/dinner/snack"
Input: "eggs and toast"
Output: "breakfast"
```

No need to show reasoning. User doesn't see this call.

**Hybrid Approach:**

Internal call → External call with CoT
```
# Step 1: Fast internal extraction (no CoT)
nutrition = claude_api.messages.create(
    system="Extract calories, protein, carbs, fat",
    messages=[...],
    temperature=0.2  # Deterministic
)

# Step 2: User-facing explanation (with CoT)
if user_wants_explanation:
    explanation = claude_api.messages.create(
        system="Explain why this meal is good. Show your reasoning.",
        messages=[...],
        temperature=0.7  # More natural
    )
```

**Time:** 2–3 minutes | **Use when:** Asked "Chain-of-thought?" or "Reasoning traces?"

---

### **Q47: How do you handle prompt versioning and rollback? What if a prompt update breaks things?**

Prompts are **product assets**, not code. They change constantly. You need versioning.

**Prompt Versioning Strategy:**

```python
class PromptVersion:
    version: int
    slug: str  # e.g., "nutrition_analysis"
    content: str
    active: bool = False
    metadata: dict = {
        "created_at": ...,
        "author": ...,
        "rationale": "Why this version?",
        "test_score": 8.1  # A/B test result
    }
```

**In Database:**

```sql
CREATE TABLE prompt_versions (
    id INT PRIMARY KEY,
    slug VARCHAR(100),  -- nutrition_analysis, health_profile, etc.
    version INT,
    content TEXT,
    active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP,
    rationale TEXT,  -- Why this version was created
    test_score FLOAT,  -- From A/B testing
    INDEX (slug, version)
);
```

**Deployment:**

```python
# Load the active prompt
active_prompt = db.query(PromptVersion).filter(
    PromptVersion.slug == "nutrition_analysis",
    PromptVersion.active == True
).first()

response = claude_api.messages.create(
    system=active_prompt.content,
    messages=[...]
)
```

**Update Process:**

```python
# 1. Test new variant
new_variant = """You are a nutrition coach...improved instructions..."""
test_score = run_a_b_test(new_variant, test_set=50)

# 2. If score is good, create new version
if test_score > current_score:
    new_version = PromptVersion(
        slug="nutrition_analysis",
        version=current_version + 1,
        content=new_variant,
        active=False,  # Don't activate yet
        rationale="Improved clarity on macro targets",
        test_score=test_score
    )
    db.add(new_version)
    db.commit()

# 3. Gradual rollout (optional)
# Deploy to 10% of users first, monitor for issues
# If good, move to 100%
```

**Rollback (If Things Break):**

```python
# Something went wrong. Roll back to previous version.
old_version = db.query(PromptVersion).filter(
    PromptVersion.slug == "nutrition_analysis",
    PromptVersion.version == current_version - 1
).first()

# Activate old version
old_version.active = True
current_version.active = False
db.commit()

# Log the incident
log_rollback(
    slug="nutrition_analysis",
    from_version=current_version,
    to_version=current_version - 1,
    reason="False positive rate spiked to 15%"
)
```

**Monitoring During Rollout:**

I track metrics that would indicate a bad prompt:
- False positive rate (recommending allergens)
- User correction rate (user rejecting recommendations)
- Quality score (A/B test metric)
- Cost per call (didn't expect this to increase)

```python
# After deploying new prompt version
# Monitor for 24 hours
metrics_before = get_metrics(start=-24h, end=-1h)  # Pre-deployment
metrics_after = get_metrics(start=-1h, end=now)    # Post-deployment

if metrics_after["false_positive_rate"] > metrics_before["false_positive_rate"] * 1.2:
    # 20% spike = bad. Rollback.
    trigger_rollback()
```

**Real Example from NomNom:**

Iteration 17 (Personalized Nutrition):
- v1: Generic prompts
- v2: Added user health profile context
  - Test score: 8.1 (good)
  - Deployed to 50% of users → no issues
  - Deployed to 100% → no issues
  - Marked as active
- v3: Later, tried to add recommendation reasoning
  - Test score: 7.9 (worse than v2)
  - Never deployed

**Documentation:**

In BUGLOG.md:
```
Prompt versioning log:
- 2026-06-10: nutrition_analysis v2 deployed (test_score 8.1)
- 2026-06-12: nutrition_analysis v3 tested (test_score 7.9, rejected)
- 2026-06-15: nutrition_analysis v2 stable, no rollbacks needed
```

**Time:** 2–3 minutes | **Use when:** Asked "Prompt management?" or "How do you update prompts?"

---

### **Q48: Tell me about the tradeoff between prompt complexity and model cost.**

Simple prompts = cheaper. Complex prompts = better results. Where's the sweet spot?

**Simple Prompt**

```
"You are a nutrition coach. Analyze this meal and provide protein amount."
```

Cost: ~100 tokens  
Quality: 85% (sometimes misses nuance)  
Latency: ~500ms  

**Complex Prompt**

```
You are an expert nutrition coach specializing in personalized health recommendations.

User Profile:
- Age: 30
- Weight: 80kg
- Activity level: active (workout 4x/week)
- Goals: build muscle
- Allergies: peanuts
- Dietary preferences: vegetarian
- Medical conditions: none

Task: Analyze this meal and provide:
1. Calorie estimate (range, not exact)
2. Protein in grams
3. How this meal aligns with the user's goals
4. One improvement suggestion

Format: JSON with keys: calories_min, calories_max, protein_g, alignment_score, improvement

Remember: Always check for allergen safety before recommending.
```

Cost: ~400 tokens (4x more)  
Quality: 95% (catches nuance, safe recommendations)  
Latency: ~600ms  

**Cost-Benefit Analysis:**

| Metric | Simple | Complex | Delta |
|--------|--------|---------|-------|
| Tokens | 100 | 400 | +300 |
| Cost per call | $0.004 | $0.016 | +300% |
| Daily (1000 calls) | $4 | $16 | +$12 |
| Quality | 85% | 95% | +10% |
| User satisfaction | 78% | 92% | +14% |

**When Simple Is Enough:**

- ✅ Internal batch processing (no user sees it)
- ✅ Pre-filtering (coarse decisions)
- ✅ Cost-sensitive (high volume, low margin)

**When Complex Is Worth It:**

- ✅ User-facing (impacts recommendation quality)
- ✅ Safety-critical (allergies, medical conditions)
- ✅ Quality drives retention (users trust the app)

**My Strategy in NomNom:**

**Simple Prompts (internal):**
```
- Categorize food (breakfast/lunch/dinner)
- Extract calories from image
- Check if meal contains user's allergen
```

**Complex Prompts (user-facing):**
```
- Generate personalized recommendations
- Explain nutritional analysis to user
- Suggest meal improvements
```

**Middle Ground: Hybrid Approach**

```python
# Step 1: Simple extraction (cheap)
nutrition_facts = claude_api.messages.create(
    system="Extract: calories, protein, carbs, fat",
    messages=[...],
    max_tokens=200
)

# Step 2: If user asks for explanation, run complex prompt
if user_wants_explanation:
    explanation = claude_api.messages.create(
        system="Explain why this meal is good based on the user's goals",
        messages=[...]
    )
```

This way: fast + cheap by default, but high-quality when user cares.

**Time:** 2–3 minutes | **Use when:** Asked "Prompt complexity?" or "Cost vs quality?"

---

### **Q49: Tell me about agent failure modes. How do you debug when an agent gets stuck?**

Agents fail in predictable ways. I've learned to recognize and fix them.

**Failure Mode 1: Tool Loop (Agent Can't Decide)**

```
User: "What should I eat for muscle building?"

Agent turn 1: "Let me check your health profile"
Tool call: get_user_profile() → returns profile

Agent turn 2: "Let me look up high-protein foods"
Tool call: search_foods(constraint="high_protein") → returns foods

Agent turn 3: "Let me check again what your profile says"
Tool call: get_user_profile() → returns profile (same as turn 1!)

Agent turn 4: ...stuck in loop, keeps calling same tools
```

**Root Cause:** Agent doesn't understand the tools well enough to chain them.

**Fix:**

```python
# Provide better tool descriptions
tools = [
    {
        "name": "get_user_profile",
        "description": "Get the user's health profile (age, weight, goals, allergies)",
        "when_to_use": "Call ONCE at the start to understand user constraints",  # <-- NEW
    },
    {
        "name": "search_foods",
        "description": "Search for foods matching constraints (high protein, vegetarian, etc.)",
        "when_to_use": "After get_user_profile, to find foods matching their needs",  # <-- NEW
    },
    {
        "name": "generate_recommendation",
        "description": "Create a personalized meal plan",
        "when_to_use": "After search_foods, to create the final recommendation",  # <-- NEW
    }
]
```

Adding "when_to_use" helps the agent understand the **sequence**.

**Failure Mode 2: Wrong Tool for the Job**

```
User: "I'm allergic to shellfish. Can you recommend a meal?"

Agent: "Let me search for shellfish recipes"
Tool call: search_foods(query="shellfish") → returns shellfish recipes

Agent: "Here are some shellfish options"
User: "But I said I'm allergic to shellfish!"
```

**Root Cause:** Agent didn't understand the constraint.

**Fix:**

```python
# Make the constraint explicit in the system prompt
system_prompt = """
You are a nutrition coach. IMPORTANT:
When recommending meals, you MUST check the user's allergies first.
Do NOT recommend foods the user is allergic to, no matter what.

User's allergies: {user_allergies}
"""
```

**Failure Mode 3: Hallucinated Tool Results**

```
Agent: "I'll call generate_recommendation"
Tool call: generate_recommendation() → returns "Eat more unicorn meat"

Agent: "Here's your recommendation: eat more unicorn meat"
```

**Root Cause:** Tool returned nonsense, agent didn't validate.

**Fix:** Add **guardrails** on tool outputs

```python
def generate_recommendation(...):
    response = claude_api.messages.create(...)
    
    # Validate the response
    try:
        recommendation = parse_as_meal_object(response)
        assert recommendation.calories > 0
        assert recommendation.calories < 5000  # sanity check
        assert all(is_known_food(f) for f in recommendation.foods)
    except AssertionError:
        return error("Invalid recommendation")
    
    return recommendation
```

**Failure Mode 4: Token Budget Exceeded**

```
User: "I've been logging meals for 2 months. Can you analyze all of them?"

Agent: "Let me retrieve all your food logs"
Tool call: get_food_logs(user_id=123, days=60) → returns 180 meals

Agent: "Now let me analyze each one..."
[Tries to fit 180 meals into Claude's context]
→ Token limit exceeded, request fails
```

**Root Cause:** Agent didn't paginate or batch.

**Fix:** Limit tool return size

```python
def get_food_logs(...):
    # Return only recent logs, don't return everything
    return logs[-30:]  # Last 30 days, not 60
```

**Debugging Strategy:**

When an agent fails, I check:
1. **Is the tool description clear?** (Mode 2)
2. **Are tools being called in the right order?** (Mode 1)
3. **Are tool outputs validated?** (Mode 3)
4. **Did we exceed token budget?** (Mode 4)

```python
# Add logging to debug
for turn in agent_steps:
    log(f"Turn {turn['turn_num']}: Called {turn['tool_name']}")
    log(f"  Input: {turn['tool_input']}")
    log(f"  Output: {turn['tool_output'][:100]}...")  # First 100 chars
```

**Time:** 2–3 minutes | **Use when:** Asked "Agent failures?" or "Debugging agents?"

---

### **Q50: How do you manage agent state and context windows? What happens to memory across turns?**

Agents have limited memory (context window). In NomNom, I handle this strategically.

**The Problem: Context Window Limits**

Claude 3.5 Sonnet has 200k tokens, but:
- System prompt: ~1k tokens
- User's conversation history: grows unbounded
- Retrieved documents (RAG): variable
- Tools outputs: can be large

```
Turn 1: User asks question → 1k tokens used, 199k remaining
Turn 2: User asks follow-up → 2k used, 198k remaining
Turn 3: ...
Turn 10: 10k used, 190k remaining ← Still fine
Turn 50: 50k used, 150k remaining ← Still ok
Turn 100: 100k used, 100k remaining ← Getting tight
Turn 150: 150k used, 50k remaining ← Dangerously low
```

**Solution 1: Conversation Pruning**

Keep only recent messages:
```python
def manage_conversation_history(conversation, max_messages=20):
    # Keep only the last 20 messages
    # Oldest messages are dropped
    if len(conversation) > max_messages:
        conversation = conversation[-max_messages:]
    
    return conversation
```

In NomNom's `/nutrition/chat`:
```python
# Fetch conversation history
history = db.query(NutritionChat).filter(
    NutritionChat.user_id == user_id
).order_by(NutritionChat.timestamp.desc()).limit(20)  # Only last 20

# Use for context
messages = [
    {"role": "user" if m.is_user_message else "assistant", "content": m.message}
    for m in reversed(history)
]
```

**Solution 2: Conversation Summarization**

Instead of dropping old messages, summarize them:
```python
def summarize_old_conversation(old_messages, max_to_keep=5):
    # Keep recent messages as-is
    recent = old_messages[-max_to_keep:]
    
    # Summarize older messages into one
    if len(old_messages) > max_to_keep:
        old_text = "\n".join([m["content"] for m in old_messages[:-max_to_keep]])
        summary = claude_api.messages.create(
            model="claude-3.5-sonnet",
            system="Summarize this conversation in 2-3 sentences",
            messages=[{"role": "user", "content": old_text}]
        )
        
        return [
            {"role": "user", "content": f"[Summary of earlier conversation]\n{summary.content}"},
            *recent
        ]
    
    return old_messages
```

**Solution 3: Agent State (Separate from Context)**

Context is what Claude sees. State is what the backend tracks:

```python
class ConversationState:
    user_id: int
    health_profile: UserProfile  # ← Not in context, accessed via tool
    allergies: List[str]         # ← Not in context, accessed via tool
    medical_conditions: List[str] # ← Not in context, accessed via tool
    conversation_topics: Set[str] # ← What has the user asked about?
    last_recommendation: str      # ← What did we recommend last time?
```

When the agent needs user info, it calls a tool:
```python
@tool
def get_user_health_profile(user_id: int):
    """Get the user's stored health data (age, weight, goals, allergies)"""
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
```

Claude doesn't store this in its context. It asks for it.

**Monitoring Context Usage:**

```python
def create_message_with_monitoring(system, messages):
    # Count tokens before
    tokens_before = count_tokens(system + str(messages))
    
    response = claude_api.messages.create(
        model="claude-3.5-sonnet",
        system=system,
        messages=messages
    )
    
    # Log for monitoring
    tokens_after = count_tokens(system + str(messages) + response.content)
    
    if tokens_after > 150_000:  # Getting full
        log_warning(f"High token usage: {tokens_after}/200k")
        trigger_conversation_pruning()
    
    return response
```

**Time:** 2–3 minutes | **Use when:** Asked "How do you handle long conversations?" or "Context windows?"

---

### **Q51: How do you design tools so Claude picks the right one? Tool selection strategy?**

When Claude has 10 tools, how do you ensure it calls the right one?

**Problem: Tool Confusion**

```python
tools = [
    {name: "get_user_profile"},
    {name: "get_food_logs"},
    {name: "get_nutrition_targets"},
    {name: "search_foods"},
    {name: "generate_recommendation"},
    {name: "get_user_allergies"},
    {name: "get_meal_history"},
    {name: "calculate_macro_split"},
    {name: "check_allergen_safety"},
    {name: "get_health_conditions"},
]

User: "What should I eat?"
Claude: Calls get_food_logs (retrieves data, not recommendations)
        Then generate_recommendation (works, but inefficient)
```

**Better approach: Clear tool descriptions**

```python
tools = [
    {
        "name": "get_user_profile",
        "description": "Retrieve the user's complete health profile (age, weight, goals, etc)",
        "when_to_call": "FIRST, when you need to understand the user's constraints and preferences",
        "returns": {"age": 30, "weight_kg": 80, "goals": "muscle building", ...}
    },
    {
        "name": "get_food_logs",
        "description": "Get the user's past food logs (what they've eaten)",
        "when_to_call": "When analyzing eating patterns or dietary history",
        "returns": [{"food": "salmon", "date": "2026-06-15", ...}]
    },
    {
        "name": "search_foods",
        "description": "Search the knowledge base for foods matching constraints (high protein, vegetarian, etc)",
        "when_to_call": "When you need to find specific foods that match criteria",
        "example": "search_foods(constraints=['high_protein', 'vegetarian'])"
    },
    {
        "name": "generate_recommendation",
        "description": "Create a personalized meal recommendation based on user profile and preferences",
        "when_to_call": "LAST, after you understand the user's needs. Pass the user profile and constraints",
        "returns": {"meal": "grilled chicken with rice", "reasoning": "high protein for your goals"}
    }
]
```

**Tool Ordering Matters:**

```python
# GOOD: Tools ordered by logical sequence
tools = [
    get_user_profile,      # ← Call first to understand constraints
    get_food_logs,         # ← Optional: understand history
    search_foods,          # ← Use criteria to find options
    generate_recommendation # ← Synthesize into recommendation
]

# BAD: Random order
tools = [
    generate_recommendation,  # ← Claude calls this first, guesses at user profile
    search_foods,
    get_user_profile,       # ← Too late, already generated wrong recommendation
    get_food_logs
]
```

**Tool Descriptions: Be Specific**

```python
# GOOD
{
    "name": "check_allergen_safety",
    "description": "Check if a specific food is safe for the user (checks against their allergies and medical conditions)",
    "parameters": {
        "food_name": "string"
    },
    "return_value": {
        "is_safe": true,
        "allergens": ["shellfish"],
        "medical_concerns": []
    }
}

# BAD
{
    "name": "check_food",
    "description": "Check a food"
}
```

**Tool Batching: Avoid Tool Explosion**

Instead of 10 separate tools:
```python
tools = [
    get_user_profile,
    get_user_constraints,
    get_user_allergies,
    get_user_goals,
    get_user_medical_conditions,
]
```

Combine into one:
```python
tools = [
    get_user_full_profile,  # Returns {profile, constraints, allergies, goals, medical}
]
```

Fewer tools = clearer decision for Claude.

**Tool Success Rate Tracking:**

```python
# Log which tools Claude calls and whether they were useful
for turn in agent_steps:
    if turn["tool_called"]:
        log({
            "tool": turn["tool_name"],
            "success": turn["achieved_goal"],
            "turns_to_goal": turn["turns_needed"]
        })

# If check_allergen_safety has low success rate, improve the description
if success_rate("check_allergen_safety") < 0.8:
    improve_tool_description("check_allergen_safety")
```

**Time:** 2–3 minutes | **Use when:** Asked "How do you guide agent behavior?" or "Tool design?"

---

### **Q52: Tell me about multi-agent coordination. How do multiple agents work together?**

In NomNom, I have different agents for different tasks. They need to work together.

**Example: Recommend a Meal (Multi-Agent)**

User: "I want to build muscle. What should I eat?"

**Agent 1: Health Analyzer**
```
Purpose: Understand the user's constraints
Tool: get_user_profile()
Output: "User goals: muscle building, allergies: peanuts"
```

**Agent 2: Food Searcher**
```
Purpose: Find foods matching constraints
Input: "muscle building, no peanuts"
Tool: search_foods(constraint="high_protein")
Output: "salmon (25g protein), chicken (30g), eggs (6g)"
```

**Agent 3: Recommendation Generator**
```
Purpose: Create the final meal plan
Input: User profile + candidate foods
Tool: generate_recommendation()
Output: "Grilled chicken with rice and broccoli"
```

**Sequential Coordination (Waterfall)**

```
Agent 1 finishes → Pass output to Agent 2
Agent 2 finishes → Pass output to Agent 3
Agent 3 finishes → Return final recommendation
```

**In Code:**

```python
async def coordinate_meal_recommendation(user_id: int):
    # Agent 1: Get user constraints
    profile = await agent_1_health_analyzer(user_id)
    
    # Agent 2: Find foods
    foods = await agent_2_food_searcher(profile.constraints)
    
    # Agent 3: Generate recommendation
    recommendation = await agent_3_recommendation_generator(profile, foods)
    
    return recommendation
```

**Parallel Coordination (Where Possible)**

Some agents don't depend on each other:

```python
async def get_user_context(user_id: int):
    # These can run in parallel (no dependencies)
    profile_task = agent_get_profile(user_id)
    history_task = agent_get_history(user_id)
    allergies_task = agent_get_allergies(user_id)
    
    # Wait for all to finish
    profile, history, allergies = await asyncio.gather(
        profile_task, history_task, allergies_task
    )
    
    return {profile, history, allergies}
```

**Inter-Agent Disagreement (Voting)**

When agents disagree, use voting:

```python
async def recommend_with_consensus(user_id: int):
    # 3 agents independently generate recommendations
    rec1 = await agent_recommendation_style_A(user_id)
    rec2 = await agent_recommendation_style_B(user_id)
    rec3 = await agent_recommendation_style_C(user_id)
    
    # Score each
    scores = [
        evaluate_recommendation(rec1),
        evaluate_recommendation(rec2),
        evaluate_recommendation(rec3),
    ]
    
    # Return the best one
    best_index = scores.index(max(scores))
    return [rec1, rec2, rec3][best_index]
```

**Communication Protocol: Structured Handoffs**

Agents pass data as structured objects, not free-text:

```python
class AgentHandoff:
    agent_name: str
    task: str
    output: dict
    confidence: float
    next_agent_hints: List[str]  # Suggestions for next agent

# Agent 1 output:
AgentHandoff(
    agent_name="health_analyzer",
    task="understand user constraints",
    output={
        "age": 30,
        "goal": "muscle building",
        "allergies": ["peanuts"],
        "activity_level": "active"
    },
    confidence=0.95,
    next_agent_hints=["search for high-protein foods", "avoid peanuts"]
)

# Agent 2 reads this and knows exactly what to do
```

**Time:** 2–3 minutes | **Use when:** Asked "Multiple agents?" or "How do agents coordinate?"

---

### **Q53: How do you debug what an agent is thinking? Reasoning traces?**

When an agent makes a bad decision, how do you understand why?

**Capture Reasoning:**

```python
def call_agent_with_reasoning(system, tools, messages):
    # Request Claude to show its thinking
    response = claude_api.messages.create(
        model="claude-3.5-sonnet",
        system=system,
        tools=tools,
        messages=messages,
        # Budget tokens for thinking
        thinking={
            "type": "enabled",
            "budget_tokens": 10000  # Give Claude thinking space
        }
    )
    
    # Capture the reasoning
    reasoning = response.thinking  # Claude's internal reasoning
    tool_calls = response.tool_calls
    final_output = response.text
    
    return {
        "reasoning": reasoning,
        "tool_calls": tool_calls,
        "output": final_output
    }
```

**Log Tool Call Sequences:**

```python
def debug_agent_trace(agent_result):
    print("=== AGENT TRACE ===")
    print(f"Reasoning: {agent_result['reasoning']}")
    print()
    
    print("Tool calls in order:")
    for i, call in enumerate(agent_result['tool_calls']):
        print(f"  {i+1}. {call.name}({call.arguments})")
        print(f"     Result: {call.result[:100]}...")
    
    print()
    print(f"Final output: {agent_result['output']}")
```

**Example Trace (Good Decision):**

```
=== AGENT TRACE ===
Reasoning: "User wants muscle building recommendation. I need to understand their constraints first."

Tool calls in order:
  1. get_user_profile(user_id=123)
     Result: age=30, weight=80kg, goal=muscle building, allergies=peanuts
  
  2. search_foods(constraint=['high_protein'], exclude=['peanuts'])
     Result: salmon (25g), chicken (30g), eggs (6g)
  
  3. generate_recommendation(profile={...}, foods=[...])
     Result: "Grilled chicken with rice"

Final output: "For muscle building, I recommend grilled chicken with rice and broccoli. It has 30g protein..."
```

**Example Trace (Bad Decision):**

```
=== AGENT TRACE ===
Reasoning: "User wants a meal. Let me recommend something."

Tool calls in order:
  1. search_foods(query="meal")  ← WRONG: didn't get user profile first!
     Result: pizza, pasta, burger, tacos
  
  2. generate_recommendation(foods=[...])  ← WRONG: using foods without knowing user is allergic to gluten!
     Result: "I recommend pasta"

Final output: "Pasta is a great meal choice."
```

**Root Cause:** Agent didn't call `get_user_profile` first.

**Fix:** Improve system prompt:
```python
system_prompt = """
You are a nutrition coach.

IMPORTANT: ALWAYS start by understanding the user's health profile.
1. Call get_user_profile first
2. Then search for foods matching their constraints
3. Finally, generate a personalized recommendation

Do not skip step 1.
"""
```

**Post-Mortem:**

When an agent fails:
```python
if agent_result['output'] is_bad:
    print("Debugging bad decision:")
    print(f"1. Trace: {agent_result['reasoning']}")
    print(f"2. Missing tools: Which tools should have been called?")
    print(f"3. Wrong order: Were tools called in wrong order?")
    print(f"4. Bad input: Were tool parameters correct?")
```

**Time:** 2–3 minutes | **Use when:** Asked "How do you debug agents?" or "Agent reasoning?"

---

### **Q54: Agent vs Workflow—how do you decide which to use?**

This is the most important decision for LLM orchestration.

**Key Difference:**

```
Agent:
  - Decides what to do (agentic reasoning)
  - Flexible, handles unknown steps
  - Slower, more expensive, less predictable

Workflow:
  - Predefined steps, known sequence
  - Fast, cheap, predictable
  - Can't handle surprises
```

**Decision Framework:**

**Use WORKFLOW if:**
- ✅ Steps are known upfront
- ✅ Order is fixed
- ✅ All paths lead to the same result
- ✅ Speed/cost matters

Example: "Analyze a meal photo"
```
Step 1: Extract nutrition facts from photo
Step 2: Store in database
Step 3: Fetch user profile
Step 4: Compare to targets
Step 5: Return analysis
```

The steps are always the same. Workflow is perfect.

**Use AGENT if:**
- ✅ User can ask unpredictable questions
- ✅ Different paths lead to different results
- ✅ Requires reasoning about which tools to call
- ✅ Flexibility is more important than cost

Example: "I'm busy, what should I eat?"
```
User might follow up with:
  - "What about allergies?" (agent should ask profile)
  - "Can you make it vegetarian?" (agent should refine search)
  - "How many calories?" (agent should adjust)
  
The agent figures out what to do next, not the developer.
```

**In NomNom:**

**Workflow: Meal Analysis**
```
Deterministic steps:
1. Extract nutrition from photo
2. Store to database
3. Retrieve user profile
4. Calculate vs targets
5. Return analysis

→ Use Workflow (predictable, fast)
```

**Agent: Nutrition Coaching**
```
Unpredictable user questions:
- "What should I eat?"
- "I'm allergic to shellfish, can you adjust?"
- "Make it high-protein"
- "Can I meal prep this?"

Agent decides which tools to call.
→ Use Agent (flexible)
```

**Hybrid: Start with Workflow, finish with Agent**

```python
async def recommend_meal(user_id, user_request):
    # Workflow: Extract constraints (known steps)
    profile = await workflow_get_profile(user_id)
    history = await workflow_get_history(user_id)
    constraints = extract_constraints(user_request)
    
    # Agent: Reason about recommendation (unpredictable)
    recommendation = await agent_recommend(
        profile=profile,
        history=history,
        constraints=constraints,
        user_question=user_request
    )
    
    return recommendation
```

**Time:** 2–3 minutes | **Use when:** Asked "Agents vs workflows?" or "When to use which?"

---

### **Q55: How do you design tools so they're discoverable? Tool naming and descriptions?**

Claude needs to understand what each tool does and when to use it.

**Bad Tool Design:**

```python
tools = [
    {"name": "f1", "description": "Get data"},
    {"name": "f2", "description": "Search"},
    {"name": "f3", "description": "Generate"},
]

Problem: Claude doesn't know what "f1" does or when to call it.
```

**Good Tool Design:**

```python
tools = [
    {
        "name": "get_user_health_profile",  # ← Exact, descriptive name
        "description": "Retrieve the user's health profile including age, weight, goals, allergies, medical conditions, and dietary preferences",
        "when_to_call": "Call this FIRST when you need to understand the user's constraints",
        "parameters": {
            "user_id": {
                "type": "integer",
                "description": "The user's ID"
            }
        },
        "example_call": {
            "user_id": 123,
            "example_result": {
                "age": 30,
                "weight_kg": 80,
                "goals": ["muscle building"],
                "allergies": ["peanuts"],
                "medical_conditions": []
            }
        }
    },
    {
        "name": "search_foods_by_constraints",  # ← Specific, not just "search"
        "description": "Search for foods matching specific nutritional and dietary constraints (e.g., high protein, vegetarian, low-carb)",
        "when_to_call": "After understanding the user's profile, use this to find specific foods",
        "parameters": {
            "constraints": {
                "type": "array of strings",
                "description": "Constraints like 'high_protein', 'vegetarian', 'gluten_free', 'exclude:shellfish'",
                "example": ["high_protein", "vegetarian"]
            }
        },
        "example_call": {
            "constraints": ["high_protein", "vegetarian"],
            "example_result": ["chickpeas (15g protein)", "tofu (8g protein)", "lentils (9g protein)"]
        }
    }
]
```

**Naming Convention:**

```
BAD:              GOOD:
f1         →      get_user_health_profile
search     →      search_foods_by_constraints
generate   →      generate_personalized_meal_recommendation
check      →      check_allergen_safety_for_food
```

**Description Structure:**

```
{
    "description": "[1-2 sentence overview of what this does]",
    "when_to_call": "[When should Claude call this? Triggers? Prerequisites?]",
    "example_call": "[Concrete example of input and output]"
}
```

**Avoid:**

```python
{
    "name": "foo",
    "description": "Does something"  # ← Too vague!
}
```

**In NomNom's MCP Server:**

```python
TOOLS = [
    MCP_Tool(
        name="analyze_food_image",
        description="Analyze a food photograph and extract nutritional information",
        input_schema={
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "URL of the food image to analyze"
                }
            }
        },
        when_to_call="When a user uploads a food photo"
    ),
    MCP_Tool(
        name="get_user_nutrition_summary",
        description="Get the user's nutrition summary for a date range (daily, weekly, monthly)",
        input_schema={
            "type": "object",
            "properties": {
                "user_id": {"type": "integer"},
                "period": {"type": "string", "enum": ["daily", "weekly", "monthly"]}
            }
        },
        when_to_call="After user asks about their nutrition data"
    )
]
```

**Time:** 2–3 minutes | **Use when:** Asked "Tool design?" or "How do you make Claude use the right tool?"

---

### **Q56: Tell me about MCP (Model Context Protocol). When do you use it vs REST API?**

MCP is Anthropic's standard for exposing tools to Claude. When do you use it vs REST?

**REST API Approach:**

```
iOS App → FastAPI backend → Claude API

Problem: Claude doesn't directly call the backend.
Claude generates text like "call GET /nutrition/analyze"
The iOS app has to parse that and make the call.
Fragile, error-prone.
```

**MCP Approach:**

```
Claude ← Direct tool calls via MCP ← NomNom MCP Server

Claude calls tools directly:
  - analyze_food_image
  - get_user_profile
  - recommend_meal

The app doesn't have to parse Claude's output.
Claude handles the orchestration.
Cleaner, more reliable.
```

**Decision Matrix:**

| Factor | REST API | MCP | Winner |
|--------|----------|-----|--------|
| Simple CRUD endpoints | Good | Overkill | REST |
| Claude needs to call tools | Messy | Perfect | MCP |
| Human-readable output | Good | Harder | REST |
| Agentic orchestration | Messy | Built-in | MCP |
| Mobile client needs the data | Good | Need HTTP anyway | REST |

**In NomNom:**

**REST API Used For:**
- iOS → Backend communication (authentication, data retrieval)
- Example: `GET /nutrition/analytics?period=weekly`

**MCP Used For:**
- Claude → Tool calling (agent orchestration)
- Example: Claude calls `get_user_nutrition_summary` internally

**Real Example: Recommendation Flow**

**Approach 1: REST (Old)**
```
iOS: "Generate a meal recommendation"
Backend: (routes to Claude)
Claude: "I'll call get_user_profile and search_foods"
Claude output: "TOOL_CALL: get_user_profile(user_id=123)"
iOS: Parse output, call API, return result to Claude
[Back and forth, fragile]
```

**Approach 2: MCP (New)**
```
iOS: "Generate a meal recommendation"
Backend: (sets up MCP server with tools)
Backend → Claude via MCP API:
  Available tools: [get_user_profile, search_foods, generate_recommendation]
Claude: Directly calls get_user_profile()
Claude: Directly calls search_foods()
Claude: Directly calls generate_recommendation()
Claude: Returns final recommendation
Backend: Returns to iOS
[Clean, direct, no parsing]
```

**When to Build MCP:**

✅ Do build MCP if:
- Claude needs to decide which tools to call
- You want agentic behavior (agents decide the flow)
- You're building Claude-first applications

❌ Don't build MCP if:
- Simple CRUD endpoints (REST is fine)
- Humans always drive the flow (not Claude)
- You need quick iteration (REST is faster to prototype)

**Time:** 2–3 minutes | **Use when:** Asked "MCP vs REST?" or "When do you use MCP?"

---

### **Q57: How do you handle tool versioning? What if you need to change a tool's behavior?**

Tools change. How do you avoid breaking Claude's tool calls?

**Tool Versioning Strategy:**

```python
class MCP_Tool:
    name: str
    version: str  # ← NEW
    deprecated: bool = False
    replacement: Optional[str] = None
```

**Version 1 (Original):**
```python
{
    "name": "analyze_food_image",
    "version": "v1",
    "parameters": {
        "image_url": "string"
    }
}
```

**Version 2 (Enhanced, Backward Compatible):**
```python
{
    "name": "analyze_food_image",
    "version": "v2",
    "parameters": {
        "image_url": "string",
        "detailed_analysis": "boolean (optional)"  # ← NEW, optional
    }
}
```

Both v1 and v2 exist. Claude can call either. Old calls still work.

**Version 3 (Breaking Change):**
```python
{
    "name": "analyze_food_image",
    "version": "v3",
    "parameters": {
        "image_base64": "string"  # ← CHANGED from image_url!
    }
}
```

**Deprecation Plan:**
1. v3 exists alongside v2
2. Claude prefers v3 (newer)
3. After 2 weeks, v2 marked deprecated
4. After 4 weeks, v2 removed

**Implementation:**

```python
TOOLS = {
    "analyze_food_image": {
        "v1": {
            "deprecated": True,
            "replacement": "analyze_food_image:v2"
        },
        "v2": {
            "deprecated": False,
            "current": True
        }
    }
}

def get_tool(name: str, prefer_version: Optional[str] = None):
    tool_versions = TOOLS[name]
    
    if prefer_version and tool_versions[prefer_version]["current"]:
        return tool_versions[prefer_version]
    
    # Return non-deprecated version
    for version, spec in tool_versions.items():
        if not spec["deprecated"]:
            return spec
```

**Time:** 2–3 minutes | **Use when:** Asked "Tool versioning?" or "Evolving tools?"

---

### **Q58: How do you structure workflows? Sequential vs parallel vs hybrid?**

Workflows can run steps in different orders. Which pattern for which problem?

**Sequential Workflow (Default):**

```
Step 1 → Step 2 → Step 3 → Done

Example: Meal Analysis
  1. Extract nutrition from photo
  2. Fetch user profile
  3. Compare to targets
  4. Return analysis

Reason: Step 2 depends on Step 1's photo.
Step 3 depends on Steps 1 and 2.
Must be sequential.

Latency: 1 + 2 + 3 = 6 seconds
```

**Parallel Workflow:**

```
Step 1 ─┐
        ├─→ Combine → Done
Step 2 ─┤
Step 3 ─┘

Example: Gather User Context
  1. Fetch user profile (async)
  2. Fetch food history (async)
  3. Fetch allergies (async)

Steps are independent.
Run them all at once.

Latency: max(1, 2, 3) = 2 seconds (if each takes 2s)
vs sequential: 6 seconds
```

**Hybrid Workflow (Best):**

```
Phase 1: Parallel
  ├─ Get user profile (async)
  ├─ Get food history (async)
  ├─ Get allergies (async)

Phase 2: Combine Results
  └─ Synthesize into recommendation

Latency: parallel(2s each) + synthesis(1s) = 3 seconds
```

**In Code:**

```python
async def recommend_meal_hybrid(user_id):
    # Phase 1: Parallel (can run together)
    profile, history, allergies = await asyncio.gather(
        get_user_profile(user_id),
        get_food_history(user_id),
        get_user_allergies(user_id)
    )
    
    # Phase 2: Synthesis (depends on phase 1)
    recommendation = await generate_recommendation(
        profile=profile,
        history=history,
        allergies=allergies
    )
    
    return recommendation
```

**Decision Matrix:**

| Workflow Type | When | Example |
|---|---|---|
| Sequential | Steps depend on previous step | Photo → Extract → Analyze → Return |
| Parallel | Steps are independent | Fetch profile, history, allergies all at once |
| Hybrid | Some parallel, then synthesis | Fetch multiple things, then combine |

**Time:** 2–3 minutes | **Use when:** Asked "Workflow structure?" or "Sequential vs parallel?"

---

### **Q59: How do you handle errors in workflows? What if a step fails?**

Workflows are deterministic. But things still fail (API down, timeout, bad data).

**Error Modes:**

1. **Transient error** (API temporarily down)
   → Retry with backoff

2. **Permanent error** (invalid input)
   → Fail the workflow, report to user

3. **Partial error** (one of 3 parallel steps fails)
   → Decide: retry just that step, or fail whole workflow?

**Strategy 1: Retry**

```python
async def step_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await func()
        except TransientError as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # exponential backoff
```

**Strategy 2: Fallback**

```python
async def get_user_profile_with_fallback(user_id):
    try:
        return await get_user_profile(user_id)
    except PermanentError:
        # Return minimal default profile
        return {
            "age": None,
            "weight": None,
            "goals": ["general health"]
        }
```

**Strategy 3: Partial Failure (Parallel Steps)**

```python
async def recommend_with_partial_failure(user_id):
    profile = await get_user_profile(user_id)
    
    # These can fail independently
    history_task = asyncio.create_task(get_food_history(user_id))
    allergies_task = asyncio.create_task(get_user_allergies(user_id))
    
    history = await history_task  # Might fail
    allergies = await allergies_task  # Might fail
    
    # If one failed, use empty default
    history = history or []
    allergies = allergies or []
    
    recommendation = await generate_recommendation(
        profile=profile,
        history=history,
        allergies=allergies
    )
    return recommendation
```

**Error Response to User:**

```python
try:
    recommendation = await recommend_meal(user_id)
    return {"success": True, "recommendation": recommendation}
except CriticalError as e:
    log_error(e)
    return {
        "success": False,
        "error": "Unable to generate recommendation. Please try again."
    }
except PartialError as e:
    log_warning(e)
    return {
        "success": True,
        "recommendation": recommendation,
        "warning": "Generated without access to your food history"
    }
```

**Time:** 2–3 minutes | **Use when:** Asked "Error handling in workflows?" or "What if a step fails?"

---

### **Q60: How do you choose between conditional branching and orchestrating with agents?**

Sometimes workflows split into different paths (if-then-else). When do you keep it in the workflow vs delegate to an agent?

**Example: User Asks for Recommendation**

**Option 1: Conditional Workflow**

```python
async def recommend_meal(user_id, user_request):
    profile = await get_user_profile(user_id)
    
    if "vegetarian" in user_request.lower():
        foods = await search_foods(constraint="vegetarian")
    elif "high protein" in user_request.lower():
        foods = await search_foods(constraint="high_protein")
    else:
        foods = await search_foods(constraint="balanced")
    
    recommendation = await generate_recommendation(profile, foods)
    return recommendation
```

Pros: Fast, predictable
Cons: Hard-coded logic, doesn't scale to new constraint types

**Option 2: Agent**

```python
async def recommend_meal_agentic(user_id, user_request):
    profile = await get_user_profile(user_id)
    
    recommendation = await agent_recommend(
        profile=profile,
        user_request=user_request,
        tools=[
            search_foods_vegetarian,
            search_foods_high_protein,
            search_foods_low_carb,
            search_foods_any,
            generate_recommendation
        ]
    )
    return recommendation
```

Pros: Agent decides which tools to call, flexible
Cons: Slower, less predictable

**Decision Framework:**

Use **Conditional Workflow** if:
✅ Choices are small and known (2-3 options)
✅ Logic is stable (rarely changes)
✅ Speed matters
Example: "User is vegetarian or not?" → 2 branches

Use **Agent** if:
✅ Choices are many or unknown (>3 options)
✅ Logic changes frequently (users ask new things)
✅ Flexibility matters
Example: "User might ask for vegetarian, high-protein, low-carb, dairy-free, ..." → Agent handles it

**Hybrid:**

```python
async def recommend_meal_hybrid(user_id, user_request):
    profile = await get_user_profile(user_id)
    
    # Simple logic: extract top-level constraint
    constraint = extract_primary_constraint(user_request)
    
    if constraint == "unknown":
        # Agent handles complex/multi-faceted requests
        return await agent_recommend(profile, user_request)
    else:
        # Workflow handles simple cases
        foods = await search_foods(constraint=constraint)
        return await generate_recommendation(profile, foods)
```

**Time:** 2–3 minutes | **Use when:** Asked "Branching logic?" or "Conditional workflows?"

---

### **Q61: How do you monitor and debug workflows? Observability?**

When a workflow fails or behaves unexpectedly, how do you understand what happened?

**Trace Logging:**

```python
class WorkflowTrace:
    workflow_id: str
    user_id: int
    steps: List[StepTrace]

class StepTrace:
    step_name: str
    status: "success" | "failed" | "skipped"
    input: dict
    output: dict
    latency_ms: int
    error: Optional[str]
```

**Example Trace:**

```json
{
  "workflow_id": "rec_meal_123",
  "user_id": 456,
  "steps": [
    {
      "step_name": "get_user_profile",
      "status": "success",
      "input": {"user_id": 456},
      "output": {"age": 30, "goals": ["muscle building"]},
      "latency_ms": 45
    },
    {
      "step_name": "search_foods",
      "status": "success",
      "input": {"constraints": ["high_protein", "vegetarian"]},
      "output": ["chickpeas", "tofu", "lentils"],
      "latency_ms": 120
    },
    {
      "step_name": "generate_recommendation",
      "status": "failed",
      "input": {"profile": {...}, "foods": [...]},
      "output": null,
      "error": "Claude API timeout",
      "latency_ms": 30000
    }
  ]
}
```

**Implementation:**

```python
async def recommend_meal_traced(user_id):
    trace = WorkflowTrace(workflow_id=uuid(), user_id=user_id, steps=[])
    
    try:
        start = time.time()
        profile = await get_user_profile(user_id)
        trace.steps.append(StepTrace(
            step_name="get_user_profile",
            status="success",
            input={"user_id": user_id},
            output=profile,
            latency_ms=int((time.time() - start) * 1000)
        ))
    except Exception as e:
        trace.steps.append(StepTrace(
            step_name="get_user_profile",
            status="failed",
            error=str(e)
        ))
        raise
    
    # Log the trace
    log_trace(trace)
    
    return recommendation
```

**Metrics to Track:**

```python
metrics = {
    "total_latency": 165,  # ms
    "step_count": 3,
    "failure_rate": 0.33,  # 1 of 3 steps failed
    "critical_path": ["get_user_profile", "search_foods"],  # Which steps are slowest?
    "bottleneck": "search_foods" (120ms)
}
```

**Time:** 2–3 minutes | **Use when:** Asked "Workflow debugging?" or "Observability?"

---

### **Q62: What's the most common workflow anti-pattern you've encountered?**

Common mistakes when designing workflows.

**Anti-Pattern 1: Sequential When Could Be Parallel**

```python
# WRONG: Sequential
profile = await get_user_profile(user_id)  # 100ms
history = await get_food_history(user_id)  # 100ms
allergies = await get_user_allergies(user_id)  # 100ms
# Total: 300ms
```

```python
# RIGHT: Parallel
profile, history, allergies = await asyncio.gather(
    get_user_profile(user_id),
    get_food_history(user_id),
    get_user_allergies(user_id)
)
# Total: 100ms
```

**Anti-Pattern 2: Hardcoded Branching**

```python
# WRONG: If-else for every constraint type
if "vegetarian" in request:
    constraint = "vegetarian"
elif "high protein" in request:
    constraint = "high_protein"
elif "low carb" in request:
    constraint = "low_carb"
elif "keto" in request:
    constraint = "keto"
elif "paleo" in request:
    constraint = "paleo"
# Now user asks for "dairy-free" and workflow breaks
```

```python
# RIGHT: Let agent decide
recommendation = await agent.call(
    tools=[search_foods, generate_recommendation],
    user_request=user_request
)
# Agent handles any constraint type
```

**Anti-Pattern 3: Not Handling Partial Failures**

```python
# WRONG: If any step fails, entire workflow fails
profile, history, allergies = await asyncio.gather(
    get_user_profile(user_id),
    get_food_history(user_id),
    get_user_allergies(user_id)
)
# If allergies_task fails, entire thing fails

recommendation = await generate_recommendation(profile, history, allergies)
```

```python
# RIGHT: Handle partial failures gracefully
try:
    profile = await get_user_profile(user_id)
except:
    profile = default_profile
    
try:
    history = await get_food_history(user_id)
except:
    history = []
    
try:
    allergies = await get_user_allergies(user_id)
except:
    allergies = []

recommendation = await generate_recommendation(profile, history, allergies)
```

**Anti-Pattern 4: No Observability**

```python
# WRONG: Black box
async def recommend():
    ...
    return recommendation

# If it fails, no way to debug
```

```python
# RIGHT: Traceable
async def recommend():
    trace = WorkflowTrace()
    
    for step in steps:
        try:
            result = await step()
            trace.log_success(step.name, result)
        except Exception as e:
            trace.log_failure(step.name, e)
            raise
    
    log_trace(trace)
    return recommendation

# Failures are debuggable
```

**Time:** 2–3 minutes | **Use when:** Asked "Workflow patterns?" or "Common mistakes?"

---

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
