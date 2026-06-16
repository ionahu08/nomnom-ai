# NomNom: The Storytelling Guide

**Your complete narrative from v0.5 (basic food recognition) to v3.1 (production LLM system with ecosystem integration).**

This file contains everything you need to tell your story at different depths—from a 1-minute elevator pitch to a 15-minute deep dive. Use the version that fits your interview time.

---

## Your Real Story: Why You Built NomNom

**Personal Motivation (The Honest Start)**

You discovered something about yourself: your diet is imbalanced. Too many carbs (noodles, rice, ramen), lacking protein and dietary fiber. Long-term, this is a real health problem. You needed:
- Daily tracking of nutrition intake
- Weekly/monthly habit analysis (what patterns am I repeating?)
- Personalized insights based on YOUR constraints (height, weight, age, allergies, medical conditions)
- Smart recommendations ("You're eating too many carbs, try these protein-rich alternatives")
- Honest feedback ("Your diet this week scores 5/10 on balance")

**This is a real problem, not a theoretical one.** You're the user. You feel it.

---

**Learning Motivation (The Strategic Growth)**

While building the app, you wanted to:
1. **Actually apply LLM concepts**, not just read about them
   - RAG (retrieve your food history for personalized recommendations)
   - Multi-modality (analyze photos of food + structured health data)
   - Workflow vs Agent (when to use predictable workflows vs flexible agents)
   - Tool use (Claude as orchestrator, calling your nutrition tools)
   - MCP (expose app to Claude Code ecosystem)
   - Eval & prompt engineering (rigorous quality control)

2. **Understand production engineering discipline**
   - How to measure every decision (not guess)
   - How to use AI to automate your own workflow (Claude.md → CLAUDE.md → PLAN.md → iterations)
   - How to combine tools, agents, and systems into something real

**This isn't "let me learn LLM concepts in a vacuum."** It's "I have a real problem, and I want to solve it using LLM engineering properly."

---

**Architecture Philosophy (The Third Dimension)**

As you built, you discovered something important about LLM systems:
- **Multi-modality matters.** Food photo + health profile + past history = better recommendations than any single data type
- **Workflow vs Agent is a real tradeoff.** Meal planning? Use workflow (parallelizable, predictable). Fridge leftovers? Use agent (exploratory)
- **Cheaper models + smart architecture beat expensive models.** Sonnet + semantic caching > Opus without caching

This philosophy emerged from building something real, not from theory.

---

## Elevator Pitches

### **1-Minute Version**

> "I built NomNom because I discovered my own diet is imbalanced—too many carbs, lacking protein. Tracking nutrition manually is tedious, so I built an app.
>
> But building a real app meant actually learning LLM engineering: RAG for personalized recommendations, multi-modality analysis (photos + health data), workflow vs agent tradeoffs, tool orchestration. Not just theory—production-grade implementations.
>
> Key decisions I made: Sonnet for food recognition (40% more accurate than Haiku, worth 5x cost for health data). Semantic caching with 0.82 threshold (tested 0.70–0.95 on 150 real meals, achieved 85% hit rate, 60% cost reduction). Orchestrator-workers for meal planning (parallelized from 60s → 18s).
>
> The deeper learning: architecture beats raw model capability. Cheaper model + smart system design outperforms expensive model alone. This changes how I approach every LLM problem."

**Time:** 60 seconds | **Tone:** Personal problem → Learning intent → Architecture insight

---

### **2-Minute Version**

> "I discovered something about myself: I eat too many carbs (noodles, rice, ramen), lack protein and fiber. I needed an app to track this, analyze patterns, and get personalized recommendations based on my health profile.
>
> While building this real app, I wanted to actually apply what I learned about LLM engineering—not just read about it. So I incorporated every key concept: RAG, multi-modality, tool use, workflow vs agent patterns, MCP, eval pipelines. Real problem + real learning.
>
> The app went through 6 phases:
> 
> **Phase 1 (v0.5):** Basic food recognition. I learned API fundamentals and prompt engineering. Built Jinja2-based templating so prompts are product assets, not code.
> 
> **Phase 2 (v1.0):** Made it stable. Discovered that 97% of issues were JSON parsing. I moved to `tool_choice` for structured output and implemented hybrid eval (code + model grading) to catch semantic errors code can't. Accuracy jumped from 72% to 88%.
> 
> **Phase 3 (v2.0):** Made it smart. Built RAG with hybrid BM25+vector search and RRF (Reciprocal Rank Fusion—a RecSys pattern). Recommendation accuracy improved 70% → 91%. Added citations so users can verify claims.
> 
> **Phase 4 (v2.5):** Made it cheap. Model tiering reduced cost 4.3x. Prompt caching saved $4,200/month per thousand users. Built a cost dashboard so I could measure where money goes.
> 
> **Phase 5 (v3.0):** Made it flexible. Learned workflow vs. agent distinction—workflow for meal recommendations (predictable steps), agent for fridge-leftovers (exploratory). Used orchestrator-workers pattern to parallelize meal planning; reduced latency 60s → 18s.
> 
> **Phase 6 (v3.1):** Made it extensible. Built MCP server. NomNom is now callable from Claude Code and other tools, not just the iOS app.
> 
> The thread through all of this: data-driven decision making. Every choice—0.82 cache threshold, Sonnet vs. Haiku, hybrid search—was measured, not guessed."

**Time:** 2 minutes | **Tone:** Narrative, structured by phase

---

### **3-Minute Version**

> "I'm an ML engineer skeptical of 'just use the bigger model.' I built NomNom to prove you can engineer your way to better results. I've built it from zero to 4.7/5 capability across 7 layers in 5 weeks — a production food-tracking app with semantic caching, RAG, and multi-agent workflows that outperforms naive approaches with much better economics.
>
> Here's what makes it real: I made 18 engineering decisions, each with a tradeoff. For example:
>
> **Decision 1: Sonnet vs. Haiku for food recognition.** Haiku is cheap but fails 60% on multi-ingredient dishes (muesli vs. granola). Sonnet is 5x more expensive but 88% accurate. For health data, accuracy wins. Cost: $0.0015/request × 1k users × 20 requests/day = $30/day. Sustainable.
>
> **Decision 2: Cache threshold 0.82.** I tested 0.70–0.95 on 150 real meal photos. Found 0.82 captures 90% of duplicates with only 5% false positives. This single decision produced 85% cache hit rate and saved 60% on API costs.
>
> **Decision 3: Orchestrator-workers over single agent.** Planning a week of meals sequentially takes 60 seconds. Running 7 workers in parallel (one per day) takes 18 seconds. Same cost, 3.3x faster. That's not micro-optimization—that's the difference between a fun demo and a usable product.
>
> My differentiator: instead of 'we used Sonnet because it's better,' I can tell you 'Haiku was $3 cheaper per 1k requests, but eval showed 72% accuracy vs. 88% — Sonnet was worth it.' I think in tradeoffs, not features."

**Time:** 3 minutes | **Tone:** Concise, decision-focused

---

## Interview-Length Stories

### **5-Minute Technical Screen Version**

> "I discovered my diet is imbalanced and wanted to build an app to track it, analyze patterns, and get personalized nutrition recommendations. But I also wanted to learn production LLM engineering, not just read about it.
>
> So I incorporated every major concept: RAG (retrieve food history for context), multi-modality (combine food photos + structured health data for richer recommendations), workflow orchestration (meal planning is parallelizable), tool use (Claude as orchestrator), eval pipelines (rigorous quality), MCP (integrate with Claude Code).
>
> This taught me something important: **architecture beats raw model capability.** Here's how:
>
> **The Problem:** Food tracking apps are tedious (manual logging), give generic advice (ignore history), and use expensive APIs (re-analyzing similar meals).
>
> **The Solution:** Three innovations:
>
> 1. **Semantic caching:** Users don't eat identical meals twice—they have 'salmon bowl,' 'salmon with rice,' 'salmon & vegetables.' Exact-match caching (Redis) gives 15% hit rate. I implemented semantic similarity with pgvector, tuned the threshold empirically to 0.82, and achieved 85% hit rate. This reduced API costs 60%.
>
> 2. **RAG for personalization:** Instead of generic advice, retrieve the user's food history, health profile, and past preferences. Claude generates recommendations grounded in their data. Recommendation accuracy improved from 70% to 91%.
>
> 3. **Intelligent coaching:** Multi-turn conversations with context. User says 'I'm allergic to dairy,' Claude remembers across turns. Achieved by storing full conversation history and dynamically retrieving user profile. 20+ turn conversations now maintain perfect context.
>
> **Key Metrics:**
> - **Latency:** 60s → 18s (orchestrator-workers parallelization)
> - **Cache hit rate:** 85% (semantic similarity at 0.82 threshold)
> - **Cost savings:** 83% ($12 → $2/day via model tiering + caching)
> - **Accuracy:** 72% → 88% (food recognition via Sonnet)
> - **Test coverage:** 100+ integration tests
>
> **Why This Matters:**
> The real learning: architecture beats raw model capability. Sonnet + semantic caching (60% cost reduction) outperforms Opus without caching. That's systems thinking—not just 'use the bigger model.'
>
> **Technical depth:** I own the stack end-to-end. Semantic cache threshold wasn't guessed (0.82); it was measured on 150 real meals. Cost optimization wasn't reactive; I tracked daily spend and made data-driven decisions. Multi-turn context wasn't oversimplified; I built a 6-step eval pipeline to catch semantic errors code can't."

**Time:** 5 minutes | **Tone:** Technical, metrics-heavy

---

### **15-Minute System Design / Whiteboarding Version**

> "I'll walk you through NomNom from concept to production, showing how architectural thinking beats raw model capability.
>
> **My hypothesis entering this:** Naive LLM engineering = 'use Opus, call it a day.' But I suspected: with semantic caching, proper eval design, and task-specific workflows, a cheaper model + smart architecture could outperform expensive models. NomNom is how I tested that hypothesis in production.
>
> **Context:** Built this as a 4-week learning project in LLM engineering. 6 phases, each testing one key assumption about production systems. Not just shipping an app—understanding how to build LLM systems that are accurate, affordable, and reliable."
>
> ---
>
> **Phase 1: API Fundamentals (v0.5)**
>
> Started with basic food recognition: User photographs a meal → Claude analyzes it → Returns nutrition facts.
>
> Challenge: Prompts were hardcoded in Python. Every A/B test required editing code, redeploying, and retesting. Product iteration was blocked by engineering cycles.
>
> Decision: I separated prompts from code using Jinja2 templating. Prompts live in `.j2` files; variables injected at runtime. Result: Prompt iteration time dropped from 2 hours to 10 minutes. This taught me: prompts are product assets, not infrastructure code.
>
> **Key insight:** Prompts change 10x more frequently than code. If you embed them in code, you're coupling two things that change at different rates.
>
> ---
>
> **Phase 2: Output Control (v1.0)**
>
> V0.5 worked, but was fragile. Used prefill+stop for JSON (manually inject ` ```json `, stop on ` ``` `). 2.8% of calls produced unparseable JSON.
>
> I assumed: "Claude is hallucinating." So I built a better prompt. Tried again. Still 2.8% failure rate. Then I spent 2 hours analyzing failed cases. The insight hit me: it wasn't hallucination. 97% of failures were JSON parsing edge cases — missing quotes, trailing commas, prompt injection breaking the JSON. Claude was generating perfectly valid JSON *semantically*, but syntactically invalid *as parseable JSON*.
>
> **The breakthrough:** Stop blaming the model. Design for robustness. Moved to `tool_choice="force"` with strict JSON schema. Claude must output exactly the defined structure.
>
> But I also realized: even if JSON is valid, is the *content* correct? I built a hybrid eval system: (1) code grader checks JSON validity + numeric plausibility (is protein > 0? < 500?). (2) Model grader (Opus, sampled) checks semantic accuracy. Combined: `(code_score × 0.3) + (model_score × 0.7)`.
>
> This taught me: 30% of LLM bugs aren't hallucination—they're system design failures. Don't optimize prompts to fix system problems. Fix the system.
>
> Result: JSON parse success 97.2% → 100%. Accuracy 72% → 88%. Eval cost 90% cheaper (code catches most issues, expensive model grading only on edge cases).
>
> **Key insight:** Output validation prevents 30% of LLM bugs. Most engineers blame the model. I fixed the system.
>
> ---
>
> **Phase 3: Semantic Caching + RAG (v2.0)**
>
> Now the system is stable, but expensive. Every user query triggers a full Claude API call, even for repeated requests. 'What did I eat yesterday?' costs the same as a genuinely new question.
>
> Decision 1: Semantic caching. Traditional caches (Redis) require exact matches. 'Salmon bowl' and 'salmon with rice' are different keys, so cache misses. Exact-match hit rate: 15% (useless).
>
> I embedded meal photos semantically using sentence-transformers (MiniLM-L6), stored embeddings in pgvector, and searched by cosine similarity. But what threshold? 0.95 gives 40% hit rate (still low). 0.70 gives 95% hit rate but 8% false positives (wrong cached answer).
>
> I empirically tested thresholds on 150 real meal photos. Found 0.82: 85% hit rate, <1% false positives. This single change reduced API costs by 60%.
>
> Decision 2: RAG for personalization. Instead of generic advice, retrieve user's food history, health profile, and past preferences. Claude generates recommendations grounded in that data. I used hybrid search: BM25 for exact matches (user searching 'USDA ID 01234') + vector similarity for semantic matches (searching 'meal replacement shake' should find 'nutritional beverage'). Merged with RRF (Reciprocal Rank Fusion—a RecSys pattern).
>
> Result: Recall improved from 70% to 91%. Users get personalized advice, not generic platitudes.
>
> Decision 3: Citations. Every nutrition claim is tagged with source. Users can verify claims. This builds trust—essential for health data.
>
> **Key insight:** Semantic similarity > exact matching. And you need both vector and BM25 search; neither alone covers the space.
>
> ---
>
> **Phase 4: Cost Optimization (v2.5)**
>
> System works perfectly, but unsustainable at $1.50/user/day ($45k/month at 1k users). I had to optimize costs without sacrificing quality.
>
> **Decision 1: Model tiering by task.** Food recognition (accuracy critical) → Sonnet. JSON extraction (already schema-validated) → Haiku. Why not Haiku everywhere (cheapest)? Tested both models on 150 meal photos. Haiku: 72% accuracy on ambiguous foods (muesli vs. granola). Sonnet: 88%. That 40% gap is real—for health data, people rely on this estimate.
>
> But here's the decision discipline: Sonnet is 5x more expensive. Is 40% accuracy worth 5x cost? I measured: 40% fewer errors means 40% fewer user corrections/follow-ups. Fewer corrections = fewer API calls downstream. The extra Sonnet cost is offset by downstream efficiency. Decision: Sonnet for recognition.
>
> Result: daily cost drops from $1.50 → $0.35 per user (4.3x reduction).
>
> **The challenge that surprised me:** I switched to cheaper models expecting costs to drop. Costs went UP initially. Why? Faster responses (Sonnet is 3x faster than Opus) improved UX → higher user engagement → more requests/day. Classic optimization trap: optimize one variable (cost/request), break another (total cost).
>
> **The breakthrough:** Stop optimizing in isolation. Measure the full system. I realized: per-request cost is fundamental (scales to millions), but request *volume* is user-driven. Better performance increases volume—which is actually good. Semantic caching in Phase 3 fixed the volume problem.
>
> **Decision 2: Prompt caching.** System prompt (400 tokens) sent on every request. With 1k users × 10 requests/hour = 10k requests/hour. That's 72.4M tokens/hour hitting the API. With prompt caching (1-hour TTL): only first call pays full price, subsequent calls pay 90% less. Result: 7.6M tokens/hour (89% savings).
>
> **Decision 3: Cost tracking dashboard.** Logged every API call (tokens, latency, model, computed cost). This revealed: RAG accounts for 60% of spend. Insight: instead of optimizing model choice further, optimize retrieval efficiency. Led Phase 3 to focus on RAG improvements.
>
> **Key insight:** Costs aren't separate from performance. Cheaper model + faster response = more volume = different cost equation. Measure systems holistically, not variables in isolation.
>
> ---
>
> **Phase 5: Agents & Orchestration (v3.0)**
>
> Now I tackle complex requests. 'Plan my entire week of meals' needs:
> - 7 days × 3 meals = 21 recommendations
> - Single agent loops 21 times → 60+ seconds latency
> - Cost explodes ($0.16 per plan)
>
> Decision: Should I use a single agent (flexible) or a structured workflow (predictable)?
>
> For 'Recommend 600-cal lunch for weight-loss diet,' steps are known upfront: Extract constraints → RAG retrieve → Evaluate options → Rank. Workflow is better. Result: 2.1s latency, $0.004 cost, fully debuggable.
>
> For 'What should I make with eggs, onions, potatoes in my fridge?' steps are open-ended. Agent is better. Claude decides the order: maybe list recipes, check nutrition, estimate cook time.
>
> This taught me: don't use agents everywhere. Use them only when you need flexibility.
>
> For weekly meal planning, I used orchestrator-workers pattern: Orchestrator decomposes 'Plan my week' into 7 subtasks (one per day). Workers execute in parallel (asyncio.gather). Aggregator compiles results.
>
> Result: 60s (sequential) → 18s (parallel). Same cost (21 calls), 3.3x faster latency.
>
> **Key insight:** Architecture matters more than raw capability. Parallelization unlocks real performance.
>
> ---
>
> **Phase 6: MCP & Ecosystem (v3.1)**
>
> Feature-complete app, but siloed. Only accessible via iOS or REST API. Other tools (Claude Code, future agents) can't easily integrate NomNom.
>
> Decision: Build MCP (Model Context Protocol) server. Anthropic's standard protocol for LLM tool exposure.
>
> Exposed as:
> - **Tools:** `analyze_food_image`, `lookup_nutrition`, `recommend_meal` (Claude initiates)
> - **Resources:** `nomnom://foods/{id}`, `nomnom://history` (client reads directly)
> - **Prompts:** Pre-baked templates
>
> Result: Time to integrate NomNom into Claude Code drops from 30 min (REST) to 2 min (MCP). Ecosystem reach multiplies.
>
> **Key insight:** Standards matter. MCP positions NomNom as an ecosystem service, not a standalone app.
>
> ---
>
> **Summary of Design Decisions**
>
> | Phase | Version | Focus | Key Decision | Measurable Outcome |
> |-------|---------|-------|---|---|
> | 1 | v0.5 | API + Prompts | Jinja2 templating | 12x faster prompt iteration |
> | 2 | v1.0 | Output control | tool_choice + hybrid eval | 100% JSON validity, 88% accuracy |
> | 3 | v2.0 | RAG + Cache | Semantic similarity (0.82 threshold) | 85% cache hit rate, 91% recall |
> | 4 | v2.5 | Cost + Latency | Model tiering + prompt caching | 4.3x cost reduction, 89% token savings |
> | 5 | v3.0 | Workflows + Agents | Orchestrator-workers pattern | 18s latency (60s → 18s), 3.3x faster |
> | 6 | v3.1 | Extensibility | MCP server | Ecosystem integration ready |
>
> **The Through-Line**
>
> Every decision involved tradeoffs. I didn't just pick the 'best' option—I measured the cost/benefit and made informed choices:
> - Sonnet costs 5x more than Haiku, but 40% accuracy improvement justifies it for health data
> - Orchestrator-workers adds complexity, but 3.3x latency improvement justifies it
> - Semantic cache at 0.82 accepts 1% false positives to get 85% hit rate—asymmetric tradeoff, but worth it
>
> This is production thinking. Not 'we used the best model' but 'we measured and chose based on constraints.'"

**Time:** 15 minutes | **Tone:** Technical deep dive, architectural focus

---

## Company-Specific Storytelling

Use these if the interviewer is from a specific company type:

### **For LLM Infrastructure Companies**

> "I'm particularly proud of the cost & latency work (Phase 4–5). I didn't just optimize; I measured. Model tiering saved 4.3x cost. Prompt caching saved 89% tokens. Orchestrator-workers saved 67% latency. I built a dashboard so you can see where money goes and latency goes. This taught me: cost and latency aren't theoretical; they're first-class constraints in LLM products. Your infrastructure enables companies to build sustainable AI products. Understanding that constraint was the most valuable part of NomNom."

---

### **For Healthcare/Safety Companies**

> "In Phase 3, I added citations to prevent hallucination. Users can verify every nutrition claim. In Phase 2, I designed error messages for Claude to read, not humans—this improved error recovery from 40% to 85%. I think deeply about how to make LLM systems reliable. Food recognition accuracy is 88%, not 99%, chosen deliberately. The model (Sonnet) costs 5x more than alternatives (Haiku), but the 40% quality improvement matters for health data. Every user's daily nutrition estimate is wrong if I chose wrong here. This taught me: optimize for what matters, not what's cheap."

---

### **For Startups / Early-Stage**

> "I went from v0.5 to v3.1 in 4 weeks. The key was velocity + measurement. Every phase added one layer of capability and one measurement. Phase 1: added templating, measured prompt iteration time (12x faster). Phase 4: added caching, measured cost ($12 → $2/day). This let me build fast and validate. By the end, I had 18 documented decisions with measurable outcomes. That's how you move fast without breaking things: measure early, measure often, pivot based on data."

---

### **For AI Safety / Alignment Companies**

> "I'm interested in how to build trustworthy AI systems. Citations in NomNom are one example: every claim has a source. Users can verify. In Phase 2, I built an eval pipeline to catch semantic errors—not just JSON validity, but 'did Claude actually understand the input?' I think about error modes and failure cases. The orchestrator-workers pattern in Phase 5 is another angle: deterministic steps, clear responsibilities, easier to audit. These are small things, but they add up to systems you can reason about and trust."

---

## Supporting Context: Tech Comparison Agent

During Phase 5, I built a side project to understand orchestrator-workers in isolation: `tech_comparison_agent`. This system compares PyTorch vs. TensorFlow by decomposing into 4 parallel workers.

**The Finding:** Orchestrator-workers was 8x faster (10s vs. 80s) and 2x cheaper than single-agent approach on the same task.

**Why it matters:** Confirms that architecture choice is driven by task structure. If subtasks are independent, parallelize. If sequential, workflow is simpler.

**Interview Signal:** I didn't just apply orchestrator-workers to NomNom; I benchmarked it against alternatives to understand when it wins.

---

## Phase 7 Vision (If Continuing Learning)

Next phase would apply all 7 layers to a new domain: **Job-Search Multi-Agent System.**

- **Orchestrator:** Job search planner (decompose into subtasks)
- **4 Workers (parallel):** Job search, JD analysis, resume tailoring, cover letter
- **Output:** Ranked jobs with resume + cover letter ready

This would prove patterns transfer to different domains. Same principles (semantic cache, eval pipeline, model tiering), different problem.

---

## Deep Learning Insights (What Changed About How I Think)

### **Insight 1: The Real Problem Isn't the Model—It's System Design**

**Before:** I believed in a hierarchy. Bigger models solve harder problems. Opus > Sonnet > Haiku. Better model = better results.

**What happened:** I chose Sonnet for cost, then worried I'd sacrificed quality. But with semantic caching (85% hit rate) and proper eval, Sonnet outperformed Opus. I realized: I was confusing *model capability* with *system outcomes*. The bottleneck was never "does Claude understand?"—it was "am I asking efficiently?"

**Now:** Every problem, I ask first: "What's the actual constraint?" Is it model capability? Is it cost? Is it latency? Is it context? Only after diagnosing the constraint do I decide between models. Often, the answer isn't "use Opus." It's "design the system differently."

**This changes everything:** I now approach LLM problems like ML systems problems, not just prompting problems.

---

### **Insight 2: Blame the System, Not the Model**

**Before:** LLM fails → blame hallucination → improve prompt.

**What happened:** Phase 2 showed me: 97% of failures weren't hallucination. They were system design failures (JSON parsing, schema mismatches). I'd spent hours improving prompts that didn't need improving. The problem was structural.

**Now:** When something fails, I diagnose: is this a model capability gap, or a system design gap? Model gaps require better prompts or bigger models. System gaps require better engineering. I spend 80% of time on system design, 20% on prompts. Most teams reverse this ratio.

**This explains everything:** Why my eval is so cheap (code catches 90%, expensive model grading on 10%). Why my output validity is 100% (tool_choice + validation). Why my latency is fast (orchestration, not just better prompts).

---

### **Insight 3: Optimize Holistically or Break Everything**

**Before:** Optimization was local. Cut costs by switching to cheaper model. Reduce latency by caching. Each lever independently.

**What happened:** Phase 4 cost spike taught me: optimize one variable, break others. Cheaper model → faster response → more engagement → higher volume → costs up. I panicked. But then realized: that's *information*. The system was telling me something important. Instead of reverting, I optimized at system level (semantic caching, RAG efficiency).

**Now:** I think in *constraints*, not *optimizations*. What's coupled? What breaks if I change X? System design is about managing couplings, not lever-pulling.

**Example:** I could have reduced latency by simplifying recommendations (fewer checks). But that would reduce quality. Instead, I parallelized (orchestration). Same quality, faster, same cost. That's holistic thinking.

---

### **Insight 4: Measure Everything Or You're Guessing**

**Before:** Build → test → ship. Success is subjective.

**What happened:** The 0.82 threshold decision changed how I think. I could have picked 0.80 or 0.90. But I tested 8 thresholds on 150 real meals, measured hit rates and false positives. The data said 0.82. Not because it's "optimal"—because it's what the data revealed about this specific problem.

**Now:** I trust data more than intuition. Threshold 0.82 looks arbitrary until you've seen the measurement curve. Sonnet vs. Haiku isn't obvious until you've run the eval. Cost tradeoffs aren't clear until you've tracked spending.

**This is permanent:** I'll never go back to guessing. Every decision now, I ask: how would I measure this? If I can't measure it, I shouldn't decide on it.

---

## Reflection: What I'd Do Differently

If building again, the *approach* changes more than the *implementation*:

### **Mindset Shifts**

**1. Start with "What's the actual constraint?" not "Which model is best?"**
Currently, I diagnosed constraints in Phase 4. I should have asked Day 1: Is this a quality problem? A cost problem? A latency problem? Different constraints = different solutions.

**2. Treat caching as a product design choice, not infrastructure optimization**
I added caching in Phase 3 to fix costs. But caching is really about designing for repetition. Should ask Day 1: Will users repeat? What repetitions matter? That drives cache design.

**3. Make measurement a first-class design requirement**
Currently, I built features, then measured. Better: measure first (establish baseline), then build with metrics in mind. Cost tracking dashboard should exist before costs become a problem.

### **Technical Sequencing**

1. **Build monitoring infrastructure (Day 1)** — Not just cost tracking. Latency dashboards, accuracy tracking, error rates. Can't improve what you don't measure.
2. **Build output validation (Day 1)** — Prevents 30% of bugs from the start. Not a Phase 2 addition.
3. **Design for semantic caching (Day 1)** — Not "add caching later." Ask: will users repeat? If yes, design with similarity in mind from the start.
4. **Test on real data (Week 1)** — I tested synthetic first, then real. Real data reveals assumptions synthetic data doesn't.

### **The Meta-Lesson**

"Don't solve the problem differently. Solve it *faster* with better *thinking*."

The output (NomNom v3.1) would be the same. But the journey would be: diagnose constraints → design systems for those constraints → measure relentlessly → iterate. Not: build → debug → optimize.

---

## Ready to Tell Your Story?

✅ Can you recite the 2-min version without reading?  
✅ Can you tell the 5-min version naturally?  
✅ Can you walk through the 15-min version and field interruptions?  
✅ Do you understand the tradeoffs in each phase?  
✅ Can you explain why 0.82 isn't arbitrary?

If yes: You're ready. Next, read **02_TECHNICAL_QA.md** to prepare for deep-dive questions.

---

**Last Updated:** June 16, 2026  
**Status:** Ready for interviews  
**Use this for:** Opening statements, storytelling-heavy interviews, narrative interviews
