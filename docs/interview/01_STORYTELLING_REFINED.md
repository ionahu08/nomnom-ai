# NomNom: Refined Story (Certified Claude Architect Edition)

## The Opening

I built NomNom for two reasons: solve my own diet imbalance, and test a hypothesis about LLM engineering.

**The personal problem:** My diet was imbalanced—too many carbs (noodles, rice, ramen), not enough protein and fiber. I needed an app to track it and get personalized recommendations based on my health profile.

**The technical hypothesis:** Most LLM teams assume bigger models solve hard problems. They use Claude Opus for everything. But as a newly certified Anthropic Claude Architect, I wanted to test something different: Can deliberate system design—smart routing, orchestration, caching—achieve cost and latency that match or beat the naive approach?

NomNom became my testbed.

---

## The 6 Phases

### **Phase 1: Prompt Engineering – From Code to Templates**

**Problem:** Early on, I realized prompts were locked in code. Every time I wanted to iterate on a prompt, I needed to redeploy the entire app. I was spending 2 hours per iteration cycle.

**Decision:** I separated prompts from code. Instead of hardcoded strings, I created a prompt templating system using Jinja2. This let me version and test prompts independently.

**Why:** Prompts change 10x faster than code. They shouldn't require code deploys.

**Tradeoff:** Slightly more infrastructure (template system, versioning), but dramatically faster iteration.

**Result:** Iteration time dropped from 2 hours to 10 minutes. 12x speedup.

**Lesson:** Prompts are product assets, not code. Treat them like you'd treat a design system or configuration—separate, versioned, tested independently.

---

### **Phase 2: Output Reliability – System Design Over Prompting**

**Problem:** My system was producing incorrect outputs. I spent days trying better prompts, better instructions, better examples. I was convinced Claude was hallucinating.

**Decision:** I measured my actual failures. Out of 100 errors:
- 97 were JSON parsing bugs (malformed output)
- 3 were actual hallucinations

The problem wasn't the model. It was system design.

So I added: prompt templating with structured outputs (Pydantic validation), strict guardrails (validation + retry logic), and tool use (Claude outputs JSON directly, not text that I parse).

**Why:** A robust system beats trying to out-prompt the problem.

**Tradeoff:** More code complexity, but vastly more reliability.

**Result:** Accuracy jumped from 72% to 88%. Success rate on 10K+ API calls: near-100%. Parsing failures dropped to near-zero.

**Lesson:** Don't blame the model. Fix the system. 97% of LLM failures are system design, not hallucination.

---

### **Phase 3: Semantic Caching – Measurement Beats Intuition**

**Problem:** Users log similar meals (salmon bowl, salmon with rice). With exact-match caching (Redis), I got only 15% hit rate. That's useless.

**Decision:** I moved to semantic caching. I embedded meal photos using embeddings, stored them in pgvector, and searched using vector similarity + BM25 hybrid search instead of exact matching.

But then came the threshold question: at what similarity score do I say "similar enough"?

I tested thresholds (0.70, 0.75, 0.80, 0.82, 0.85, 0.90, 0.95) on 150 real meal photos. For each, I measured hit rate and false positive rate.

**Result:** 0.82 was optimal. 85% cache hit rate with only 1% false positives.

Why 0.82? Because the cost of false positives (wrong nutrition advice) is much higher than false negatives (cache miss). I was willing to accept slightly lower precision for higher recall.

**Why:** Testing on real data beats guessing. Every decision validated.

**Tradeoff:** High recall (85% hit rate) vs. low false positives (1%). Chose to optimize for impact, not mathematical perfection.

**Result:** 85% cache hit rate. 60% reduction in redundant LLM calls. Cuts costs significantly.

**Lesson:** Measurement wins. I initially thought 0.95 would be "safe." Real data proved me wrong. 0.82 is the number.

---

### **Phase 4: Cost Optimization – Task-Based Model Routing**

**Problem:** The system worked great but was expensive. Every meal analysis used Sonnet (the expensive model). I needed to make this economically sustainable.

**Decision:** Instead of one model for everything, I routed by task complexity:
- Haiku for lightweight extraction: "What's in the photo?" Fast, cheap, 90%+ accurate for this job.
- Sonnet for complex reasoning: "Personalized nutrition analysis." Only use when you need the power.
- Added prompt caching so I wasn't resending the same system prompt every single time.

**Why:** Not all tasks need the expensive model. Match model capability to task difficulty.

**Tradeoff:** More complex routing logic, but 4.3x cost reduction ($12/user/day → $2.80/user/day) versus Sonnet-only.

**Result:** Same quality (96%+ accuracy maintained), 4.3x cheaper. Sonnet + smart routing beats Opus alone.

**Lesson:** Architecture beats raw capability. The constraint isn't always "we need a smarter model." Often it's "we need a smarter system."

---

### **Phase 5: Latency Optimization – Orchestrator-Worker Pattern**

**Problem:** Even with these optimizations, meal analysis took 60 seconds. Users would start the app, photograph their meal, and then wait a minute for analysis. That kills engagement.

**Decision:** I realized the steps were independent:
1. Extract food items from photo (Haiku)
2. Calculate nutrition (deterministic, no LLM needed)
3. Generate recommendations (Sonnet)

Instead of running sequentially, I parallelized them using an orchestrator-worker pattern: one coordinator, three workers running in parallel. The coordinator waits for all workers to finish, then combines results.

**Why:** Parallelization. Three 20-second tasks in parallel = 20 seconds total, not 60.

**Tradeoff:** More complexity (need coordination logic, error handling across workers). But massive latency win.

**Result:** 60 seconds → 5–15 seconds. 67% latency improvement.

**Lesson:** Not everything needs to be an agent. For structured, known-steps problems, workflows beat sequential agents. Orchestrator-worker pattern is your friend.

---

### **Phase 6: Extensibility – MCP Server**

**Problem:** Other tools wanted to integrate with NomNom. But each integration took hours of work: API design, documentation, testing.

**Decision:** I built an MCP server—Model Context Protocol, Anthropic's standard for exposing tools to LLMs. This let external applications interact with NomNom through a standardized interface.

**Why:** Standardization. If every tool speaks MCP, integration time drops.

**Tradeoff:** Initial investment in MCP design, but long-term flexibility.

**Result:** Integration time: 30 minutes instead of hours. Other LLM applications can now use NomNom as a service.

**Lesson:** Architecture that enables others to build on top is powerful. Think ecosystem, not just your own app.

---

## The Consistent Pattern

Across all 6 phases, one theme emerges: **every decision was data-driven.**

- Phase 1: Measured iteration time (2 hours → 10 minutes)
- Phase 2: Measured failure types (97% parsing, 3% hallucination)
- Phase 3: Tested thresholds on 150 real meals, found 0.82 optimal
- Phase 4: Measured accuracy across models, chose Sonnet + routing
- Phase 5: Measured latency, achieved 5–15s
- Phase 6: Measured integration time, standardized with MCP

That's the real skill in LLM engineering: not just building, but measuring before deciding.

---

## What This Taught Me About LLM Engineering

I entered this project believing: **"Bigger models solve hard problems."**

I finished believing: **"Better systems solve hard problems."**

This shift changed everything. Now when I encounter an LLM problem, I ask:
1. What's the actual constraint? Cost? Latency? Reliability?
2. Can I solve it at the system level (routing, caching, orchestration) before upgrading the model?
3. How would I measure if my solution works?

That lens shift—from "which model is best?" to "what's the system constraint?"—affects every LLM design I do now.

The numbers prove it:
- Sonnet + semantic caching beats Opus alone
- Task-based routing beats one-model-fits-all
- Orchestrator-workers beats sequential agents
- 0.82 threshold beats guessing

This is what being a Certified Claude Architect means to me: not just knowing the tools, but knowing *when* and *why* to use each one. It's about architecture, not heroics.

---

## For Interview Delivery

**2-minute version:** Summarize opening + Phases 1-3 + key numbers (0.82, 85%, 4.3x, 5–15s) + key lesson.

**5-minute version:** Opening + all 6 phases (each 30 seconds) + consistent pattern + lesson.

**15-minute version:** Full narrative as written above.

**Key numbers to emphasize:** 0.82, 85%, 4.3x, 5–15s, 150 real meals, 10K+ API calls, 97% (parsing failures).

**Struggle moments to own:** "I thought it was hallucination... actually JSON." "I thought 0.95 would be safe... real data proved me wrong."
