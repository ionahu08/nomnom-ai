# Technical Q&A: NomNom Deep Dive

**Purpose:** High-frequency technical questions from interviews, with tested answers grounded in NomNom experience.

**Format per answer:**
- Direct answer (1–2 sentences)
- Evidence from NomNom (concrete example)
- Why this matters (business/engineering context)
- Optional: What I'd do differently now

---

## Layer 0: API Mastery & Cost

### Q1: How do you handle transient failures in LLM API calls?

**Answer:**
Implement exponential backoff with a small retry count (2–3). Wait 1s, then 2s, then fail. Don't hammer the API during outages.

**NomNom Evidence:**
In Phase 1, I built `client.py` with exponential backoff. Result: 85% of transient failures recovered without user seeing an error. Avoided "wasting" retries on truly broken inputs.

**Why it matters:**
Retry logic is the difference between "feels like an API outage" (user perspective) and "briefly slow" (actual reality). Users don't distinguish; they just know if it works.

**Reflection:**
I'd add jitter (random 0–500ms per retry) to avoid thundering herd if multiple clients retry in sync. But for single-user app, exponential backoff alone was sufficient.

---

### Q2: How do you optimize LLM costs without sacrificing quality?

**Answer:**
Don't optimize cost blindly. Measure where money goes, then decide what to sacrifice. Use model tiering: cheap models for simple tasks, expensive for high-stakes ones.

**NomNom Evidence:**
Phase 4: I implemented model tiering. Haiku for JSON extraction ($0.0001/req), Sonnet for food recognition ($0.0015/req), Opus for eval (rare). Result: 4.3x cost reduction while maintaining 88% accuracy on food recognition. Daily cost per user: $1.50 → $0.35.

**Why it matters:**
Costs are a first-class constraint in LLM products. At 1k users, $1.50/day becomes $45k/month—unsustainable. Without tiering, you can't scale.

**The tradeoff:**
Why Sonnet for food images, not Haiku? Haiku fails 60% on multi-ingredient dishes (muesli vs. granola). For health data, accuracy matters more than cost. This is a deliberate choice, not a "we couldn't afford better."

---

### Q3: Tell me about prompt caching. When does it help?

**Answer:**
Prompt caching reuses expensive static content (system prompts, tool schemas). First call pays full cost; next 180 calls (1-hour TTL) pay 90% less per cached token. Helps when: same system prompt × many requests.

**NomNom Evidence:**
Phase 4: Our system prompt (nutritionist role + tool schema) = 400 tokens. Sent in every food recognition call. With caching:
- Uncached: 400 × 181 calls/hour = 72,400 tokens/hour
- Cached: 400 (creation) + 40 × 180 (reads) = 7,600 tokens/hour
- Result: 89% token savings = $50/month per 1k users

**When it doesn't help:**
If your system prompt changes frequently (more than hourly), the entire cache invalidates. Not worth it.

**Practical note:**
Min 1024 cached tokens. Small caches don't pay off. Our 400-token prompt barely qualifies—we'd see more savings if we cached the RAG knowledge base too.

---

### Q4: How do you track LLM costs in a real application?

**Answer:**
Log per-call: tokens (input, output, cache-read), latency, model, cost. Query to answer "Which feature costs most?" and "Can we afford N users?"

**NomNom Evidence:**
Phase 4: Built cost dashboard. Queries:
- Daily spend: `SUM(cost_usd) WHERE DATE = TODAY`
- By feature: `GROUP BY task_type`
- P95 latency: `PERCENTILE(latency_ms, 95)`

Discovery: RAG accounts for 60% of spend. This data-driven insight (vs. guessing) led to Phase 3 optimization.

**Why it matters:**
Without visibility, you're flying blind. "Are we profitable?" becomes a guess. With data, you make real decisions.

**What I'd do differently:**
Add cost per user, not just total. And track cache hit rate explicitly—it's the most cost-effective optimization available.

---

## Layer 1: Prompt Engineering

### Q5: How do you design prompts for iteration?

**Answer:**
Separate prompts from code. Use templating (Jinja2). Version-control prompts independently. This lets product teams iterate without engineering.

**NomNom Evidence:**
Phase 1: Implemented Jinja2 templating. Result: Prompt iteration time 2 hours → 10 minutes. Code churn reduced 80%. Non-engineers could now test prompt variants.

**Why it matters:**
Prompts change 10x more frequently than code. If you embed them in code, you're coupling the two. Every prompt change becomes a code review + deploy + retest cycle.

**Prompt design principle:**
Use these techniques in order of impact:
1. System prompt (role + context)
2. Examples (multishot)
3. Structure (XML tags)
4. Reasoning (Chain of Thought)
5. Advanced (prefill, stop sequences)

For NomNom food recognition: system prompt defines "nutritionist" role, multishot examples show good analyses, XML tags structure output, CoT breaks down the reasoning.

---

### Q6: How do you handle ambiguous or malformed user input in prompts?

**Answer:**
Design error messages for Claude to read, not humans. Tell Claude what's wrong and how to fix it. This enables self-correction.

**NomNom Evidence:**
Phase 2: User takes blurry photo. 

Old error: `JSON_VALIDATION_ERROR: missing field 'calories'` — Claude has no idea what to do.

New error: `Image is too blurry. Ask user to retake the photo with better lighting.`

Result: Error recovery rate 40% → 85%. Claude now understands the problem and suggests a fix.

**Why it matters:**
Error messages are part of the control loop. If Claude doesn't understand the error, it loops. If it does, it can self-correct.

---

## Layer 2: Output Control

### Q7: Prefill+stop vs. tool_choice—when to use each?

**Answer:**
Prefill+stop is simple but fragile (prompt injection, hallucination). tool_choice enforces schema strictly. Use tool_choice when correctness matters more than simplicity.

**NomNom Evidence:**
Phase 2: Migrated from prefill+stop to tool_choice for nutrition JSON.

| Metric | Prefill+Stop | tool_choice |
|--------|---|---|
| JSON parse success | 97.2% | 100% |
| Vulnerability to injection | Yes | No |
| Claude control | Loose | Strict |
| Latency | Faster | Slightly slower |

Result: 100% valid JSON, no parse errors, immunity to prompt injection.

**Tradeoff:**
Prefill+stop is slightly faster and simpler. If your use case allows 2–3% errors, it's fine. For health data (NomNom), errors break trust—use tool_choice.

---

## Layer 3: Augmentation & RAG

### Q8: How do you tune a semantic cache threshold?

**Answer:**
Measure empirically. Collect 100 real requests, manually label semantic duplicates, plot cosine similarity distribution, find the sweet spot.

**NomNom Evidence:**
Phase 3: Tuned cache threshold to 0.82.

- Below 0.82: 30% false positives (wrong cached answer given to user) → Trust destroyed
- At 0.82: 5% false positives, 90% of true duplicates caught
- Above 0.95: 0% false positives, but 40% cache misses → Redundant API calls

Result: 60% cache hit rate, 5% false positive rate, sustainable tradeoff.

**Why guessing fails:**
Without data, I'd have guessed 0.95 (conservative, safe). That leaves 40% cache misses. With measurement, I captured 90% of value with 5% risk.

---

### Q9: Vector search vs. BM25 vs. hybrid—which one?

**Answer:**
Hybrid (vector + BM25 + RRF). Vector catches synonyms; BM25 catches exact matches. Each alone fails 20–30% of the time. Combined: 91% recall.

**NomNom Evidence:**
Phase 3: Built meal recommendation RAG.

| Strategy | Recall@5 | Precision@1 | Why It Fails |
|----------|----------|----------|---|
| Vector only | 78% | 60% | Misses exact matches ("apple" vs "apple_id") |
| BM25 only | 82% | 55% | Misses synonyms ("meal replacement" vs "shake") |
| Hybrid (RRF) | 91% | 75% | Best of both |

RRF formula: `score = Σ(1 / (k + rank_in_channel))`. Treats each channel equally, merges gracefully.

**Why this works:**
It's a RecSys pattern I brought from my background. Multi-channel recall + fusion is proven. Don't use weighted fusion (requires tuning); RRF is parameter-free.

---

### Q10: How do you structure RAG knowledge for production?

**Answer:**
Chunk by meaning, not just size. Add context before embedding ("A medium apple (182g)..."). Enable citations so users verify claims. For health data, citations are non-negotiable.

**NomNom Evidence:**
Phase 3:

**Before:** Raw chunk: "Apple: 52 cal, 13g carbs"  
**Issue:** Ambiguous. Per 100g? Per apple?

**After:** "A medium apple (182g) provides 52 calories, 13g carbs. Source: USDA."  
**Result:** Retrieval accuracy 82% → 94%

Citations matter: User reads "apple has potassium" and sees the source. Builds trust. In health data, this is essential.

---

## Layer 4: Reliability & Evaluation

### Q11: How do you build an evaluation pipeline?

**Answer:**
6-step workflow: (1) Write prompt, (2) Create test dataset, (3) Run inference, (4) Grade results, (5) Compute metrics, (6) Iterate.

**NomNom Evidence:**
Phase 2: Built eval pipeline with 30-photo test set.

- Code grader: JSON validity + numeric plausibility
- Model grader (Opus): Semantic accuracy
- Combined score: `(code_score × 0.3) + (model_score × 0.7)`

Result: 30 test cases, ~15 min to run, clear metrics per prompt variant.

**Grading philosophy:**
- Code grader: Fast, cheap, catches format errors
- Model grader: Slow, expensive, catches semantic errors
- Combine both: You get coverage + efficiency

Cost: $0.04/eval run (vs. $0.30 if only using Opus). This enables rapid iteration.

---

### Q12: How do you measure if your LLM output is getting better?

**Answer:**
Define metrics before experimenting. For accuracy: accuracy@k (top-k correctness). For cost: cost per successful call. For latency: P50/P95. Measure before/after.

**NomNom Evidence:**
Phase 2 → Phase 3: Food accuracy improved 72% → 88%.

| Metric | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|
| Accuracy | 72% | 88% | 88% |
| JSON validity | 97.2% | 100% | 100% |
| Eval cost/run | N/A | $0.04 | $0.04 |
| Recommendation recall | — | 70% | 91% |

Each phase added a dimension. Without pre-defined metrics, I wouldn't know what improved.

---

## Layer 5: Agent Design

### Q13: When should you use workflow vs. a single agent?

**Answer:**
**Workflow:** Steps are known upfront, sequence is fixed, deterministic.  
**Agent:** Steps are exploratory, Claude decides order, unpredictable.

**NomNom Evidence:**
Phase 5 had two use cases:

*1. "Recommend 600-cal lunch for weight-loss diet"*
- Steps known: Extract constraints → RAG retrieve → Evaluate options → Rank
- Workflow was better: 2.1s latency, $0.004 cost, fully debuggable

*2. "What should I make with eggs, onions, potatoes?"*
- Steps unknown: Maybe list recipes → Maybe check nutrition → Maybe estimate cook time
- Agent was better: Claude self-composed calls, handled open-ended exploration

**Why it matters:**
Workflow is faster, cheaper, debuggable. Agent is flexible, exploratory. Pick the right tool for the problem.

**Common mistake:**
Using agent for everything. "We'll let Claude figure it out." Agents are slower and more expensive. Use them only when you need them.

---

### Q14: Explain the orchestrator-workers pattern.

**Answer:**
Orchestrator (Sonnet) decomposes a task into subtasks. Workers (Sonnet/Haiku) execute subtasks in parallel. Aggregator compiles results. Use when: 3+ independent subtasks.

**NomNom Evidence:**
Phase 5: Weekly meal planning.

```
Orchestrator (Sonnet) decomposes:
  "Plan my week" → [Monday meals, Tuesday meals, ..., Sunday meals]

Workers (Sonnet) execute in parallel (asyncio.gather):
  Worker 1: Generate Monday meals
  Worker 2: Generate Tuesday meals
  ...
  Worker 7: Generate Sunday meals

Aggregator (Python):
  Compile 21 meals into weekly plan
```

Result: 60s (sequential) → 18s (parallel). Cost same (21 calls), latency 3.3x better.

**When to use:**
3+ subtasks, each independent, parallelizable. If tasks are sequential, workflow is simpler.

**Context passing:**
Each worker gets only its sub-prompt, not the full user input. This keeps context windows manageable.

---

### Q15: How do you handle errors in an agent loop?

**Answer:**
Errors should be informative (Claude-readable), retryable, and bounded (max 3 retries per tool). Let Claude self-correct if the error is actionable.

**NomNom Evidence:**
Phase 5 agent:

```python
for attempt in range(3):
    try:
        result = call_tool(tool_name, input)
        if result.success:
            return result
    except ToolError as e:
        # Error message tells Claude how to fix it
        messages.append(ToolErrorMessage(
            tool_use_id=tool_use.id,
            content=f"Tool failed: {e.reason}. Try: {e.suggestion}"
        ))
        # Claude retries with better input
        continue
```

Without good error messages, loops become infinite retries. With them, Claude self-corrects 85% of the time.

---

## Layer 6: Multi-Agent Coordination

### Q16: When NOT to use multi-agent?

**Answer:**
Don't use multi-agent if:
1. Single agent solves it (one call → done)
2. Steps are sequential, not parallel
3. You haven't measured that agents help
4. Cost explosion outweighs benefits

Multi-agent is 5–10x more expensive. Make sure the complexity justifies it.

**NomNom Evidence:**
Phase 5: I built a side project (`tech_comparison_agent`) using orchestrator-workers. Compared it to a workflow version.

| Metric | Workflow | Multi-Agent |
|--------|----------|------------|
| Latency | 45s | 18s |
| Cost | $0.08 | $0.08 |
| Debuggability | High | Low |
| Implementation | Simple | Complex |

Result: Same cost, latency better, but complexity much higher. For this task, workflow was actually better. I only used multi-agent because it was educationally interesting (Phase 5 goal).

**Interview signal:**
Saying "we built multi-agent" is not impressive. Saying "we measured, it wasn't worth it, we used workflow instead" shows real judgment.

---

### Q17: How do you evaluate a multi-agent system?

**Answer:**
4-dimensional eval: (1) Final output quality, (2) Per-worker accuracy, (3) Orchestrator reasoning, (4) Cost/latency. Multi-agent should beat the control (single-agent or workflow).

**NomNom Evidence:**
Phase 5 side project eval:

```
4-dimensional eval of tech_comparison_agent:

1. Final report quality: Opus model-based grader
   Score: 8.2/10 (expert panel: 8.5/10)

2. Individual worker quality:
   Worker 1 (Performance): 85% accuracy vs. ground truth
   Worker 2 (Ecosystem): 92% accuracy
   Worker 3 (Deployment): 78% accuracy

3. Orchestrator reasoning:
   Decomposition appropriate? Yes
   Task split sensible? Yes
   Context preserved? Yes

4. Cost/latency:
   Multi-agent: $0.08, 18s
   Workflow control: $0.08, 45s
   Single agent: $0.10, 60s
```

Result: Multi-agent wins on latency, same cost as workflow. But complexity higher. For interview: "Here's the tradeoff I measured."

---

## Design Decision Questions

### Q18: Tell me about a design tradeoff you made.

**Answer:**
(Pick one from NomNom; here's Sonnet vs. Haiku example)

**Tradeoff:** Food recognition accuracy vs. cost.

**Data:**
- Haiku: $0.0003/req, 72% accuracy
- Sonnet: $0.0015/req, 88% accuracy
- Cost multiplier: 5x
- Accuracy gain: 16 points (22% relative improvement)

**My decision:** Sonnet

**Reasoning:**
1. Food recognition is the core value prop. Wrong nutrition breaks trust permanently.
2. At 1k users × 20 calls/day: Haiku = $6/day, Sonnet = $30/day. Both sustainable (not Opus at $300/day).
3. 16-point accuracy gain justifies 5x cost for health data.

**Reflection:**
I didn't optimize for "cheapest." I optimized for "cheapest while maintaining core quality." That's the real skill.

---

### Q19: How would you approach building this system differently today?

**Answer:**
Three things I'd change:

1. **Cost tracking from Day 1** (not Phase 4): Measure what's expensive early. Phase 4 came late; I could've optimized sooner.

2. **More user testing:** I tuned cache threshold (0.82) empirically, but only from logs. With real users, I'd discover more edge cases.

3. **Streaming from Phase 1:** "Analyzing... Querying... Generating..." UI is expected now. I added it late (Phase 5). Better to have from the start.

**Why this matters in interviews:**
Showing you'd do things differently proves you're learning. You're not defensive; you're reflective. Hiring teams value that.

---

### Q20: How do you know when to stop optimizing?

**Answer:**
Stop when: (1) bottleneck is no longer your system, (2) cost is acceptable relative to revenue/users, (3) further optimization requires architectural change (high risk, low reward).

**NomNom Evidence:**
Phase 4: Achieved 4.3x cost reduction. Could I have optimized further?

- Option: Fine-tune embedding model (MiniLM) for nutrition domain
- Cost to implement: 2 weeks
- Expected improvement: 5–10% faster search
- Value: Marginal ($200/month saved at 1k users)

**Decision:** Stop. 4.3x reduction is huge. Micro-optimizations don't pay off.

**When to resume:**
If I scale to 10k users and cost becomes a real business problem again, revisit.

---

## System Design Questions

### Q21: How would you redesign NomNom to handle 100k users?

**Answer:**
Three changes:

1. **Caching layer (Redis):** Cache not just prompts, but entire recommendation results. TTL: 24h. Hit rate: 30–50%.

2. **Batch processing:** Group eval and fine-tuning into daily batch jobs (not real-time).

3. **Fallback to cheaper models:** When latency > 2s, fall back to Haiku instead of Sonnet. Accept 5% accuracy loss for speed.

**Current bottleneck:**
Cost. At 100k users, current model (Sonnet everywhere) = $3M/month. Unsustainable. With above: ~$300k/month (90% savings).

---

### Q22: How would you add personalization to NomNom?

**Answer:**
Three layers:

1. **Simple:** Per-user preferences (diet type, allergies) → Include in prompt. Cost: 0 (prompt templating already done).

2. **Moderate:** Per-user RAG context. Cache user's past meals; retrieve similar ones for recommendations. Cost: +10% (more RAG queries).

3. **Advanced:** Fine-tune Claude on user's preferences. Cost: +$100/user (one-time). Value: 10–15% accuracy gain on recommendations.

**NomNom today:**
Layer 1 is built. Layer 2 could be added in Phase 6 (part of orchestrator-workers). Layer 3 is expensive; only if revenue supports it.

---

## Follow-Up Questions to Ask Interviewer

1. **For LLM infra companies:** "How do you balance latency vs. cost in your products? What's your policy?"

2. **For healthcare companies:** "How strict are your accuracy requirements? What's the cost of a missed diagnosis vs. a false positive?"

3. **For startups:** "Do you measure LLM costs as a % of revenue? What's sustainable?"

4. **For AI safety companies:** "What's your stance on multi-agent systems? Are there use cases you avoid?"

---

## Summary

**If they ask...** pick the relevant Q from this doc and adapt the answer to their context.

**Example:**
Interviewer: "How would you optimize this LLM product?"

You: "I'd start by measuring. On NomNom, I implemented cost tracking in Phase 4, which revealed RAG accounted for 60% of spend. That guided my optimization strategy. So first question: what's your biggest cost driver?"

This shows: data-driven thinking, measurement-first mindset, ability to teach what you learned.
