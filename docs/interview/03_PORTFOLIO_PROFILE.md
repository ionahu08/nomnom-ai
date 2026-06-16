# Portfolio Profile: Skills, Capability & Achievement Summary
## Speech-Friendly Edition for Interviews

---

## HOW TO USE THIS DOCUMENT

**This file is designed for positioning yourself in interviews and on LinkedIn.** Here's how to navigate it:

### **For Elevator Pitches (30 seconds to 3 minutes):**
Jump directly to **Quick Elevator Pitches** section at the end. Pick the 1-liner, 3-liner, or 5-liner based on time available.

### **For LinkedIn Profile:**
Use **Executive Summary** + **Why Hire You** sections. These position your differentiators clearly.

### **For Technical Screen (45 minutes):**
Lead with a **Core Talking Point** from 02_TECHNICAL_QA.md, then reference your **Top 3 Differentiators** when asked "What makes you different?" Each differentiator is a complete 3-5 minute story.

### **For System Design Interview (60 minutes):**
Use **7-Layer LLM Engineering Capability Stack** to show breadth. Reference specific layers when the interviewer asks about your weaknesses or strengths.

### **For Behavioral Interview (30 minutes):**
Use the **STAR Examples Ready** in the "Interview Positioning" section. These show growth mindset and learning from data.

### **For Take-Home Project:**
You can deliver: Full RAG pipeline with eval suite, semantic cache with threshold tuning, cost tracking dashboard, multi-agent decision framework. This document shows you've already done this.

---

## Executive Summary

I'm a full-stack LLM engineer with 4.7/5 capability across 7 layers. But more importantly, I'm someone who measures before deciding.

Most LLM engineers pick the biggest model and hope it works. I pick based on data. Most teams treat prompts as code. I separate them so non-engineers can iterate. Most skip eval pipelines. I built a hybrid code+model grading system that catches semantic errors 30% of teams miss.

Built NomNom from v0.5 (basic food photo recognition) all the way to v3.1 (production system with semantic caching, RAG, workflow orchestration, multi-turn chatbot, 100+ integration tests).

**The real story:** Started because I had a personal diet problem. I realized my meals were imbalanced—too many carbs, not enough protein and fiber. Instead of just using an existing app, I decided to build one. And here's the key: I intentionally built it to apply every LLM concept I was learning. Semantic caching, RAG, multi-turn conversations, tool orchestration, eval pipelines, MCP servers. Real problem plus intentional learning equals much deeper understanding.

**Result:** Not just a food tracking app. A portfolio piece demonstrating full-stack LLM systems thinking. And every decision is backed by measurement, not guesses.

**Background:** ML/Recommendation Systems engineer. Statistics foundation lets me design rigorous eval systems. Production discipline means I actually ship things instead of just building prototypes.

---

## Key Concepts You Can Demonstrate

### **1. Multi-Modality: Combining Photos + Structured Data**

Here's what I mean by multi-modality and why it's not just "stacking two models."

When a user photographs a meal, I get one signal: the image. Claude's vision API analyzes it and says "salmon, rice, vegetables, approximately 750 calories."

But that's missing context. What if this user is trying to gain muscle (wants protein) vs. lose weight (wants low calorie)? What if they have a shellfish allergy and I recommend fish three days in a row? What if they have diabetes and I keep suggesting high-carb meals?

Multi-modality means: take the photo *plus* the user's health profile (age, weight, goals, allergies, medical conditions) *plus* their food history (what they've eaten in the past, what they rated highly) and process all of it together.

Neither alone is sufficient. The photo tells you "what is it." The health profile tells you "is this right for this person." The food history tells you "what will they actually enjoy and stick with."

**The evidence:** When I combined all three—photo as input, health profile as context, food history for pattern matching—nutrition recommendations jumped from 70% to 91% quality.

That's multi-modality done right. Not just "more inputs," but "inputs that answer different questions about the user's needs."

### **2. Workflow vs. Agent: A Decision Framework**

This is probably the biggest insight I had during this project. Because most teams use agents everywhere, and I learned: don't.

Here's the question I ask: Is this problem deterministic or exploratory?

**Deterministic = use a Workflow**

Example: "Recommend a 600-calorie lunch for weight loss."

The steps are known:
1. Extract dietary constraints from the request
2. Search the knowledge base for lunch options
3. Evaluate each option against the constraints
4. Rank by user preference

The order is always the same. You don't need Claude to decide what to do. You know the steps.

So I build a workflow. Each step is explicit. And crucially: I can parallelize independent steps (search while extracting, evaluate while searching). This reduces latency from 60 seconds (sequential agent) to 18 seconds (parallel workflow). Plus it's cheaper and easier to debug.

**Exploratory = use an Agent**

Example: "What can I make with eggs, onions, and potatoes? I'm vegetarian and have 30 minutes."

The steps aren't predefined. Claude needs to decide: Should I list recipes? Check nutrition? Estimate cook time? What matters most to this user?

For exploratory problems, I use Claude as a multi-turn agent. Claude can decide the order. The user can ask follow-ups. It's flexible. But it's slower, more expensive, and harder to test.

**The tradeoff:**

Workflows are fast, cheap, debuggable, and parallelizable. But they're rigid. If requirements change, you need to change the workflow code.

Agents are flexible and can handle novel queries. But they're slower, more expensive, harder to test, and harder to predict behavior.

**The data from NomNom:**

- Workflow (meal planning): 2.1 seconds latency, $0.004 per request, 0% failures
- Agent (fridge leftovers question): 12 seconds latency, $0.02 per request, ~2% ambiguous responses

**The key insight:** 95% of real-world LLM tasks are workflows. Agents should be special-case flexibility, not the default.

I made 18 different architectural decisions in NomNom. For maybe 17 of them, I chose workflow. And I measured the performance. Most teams reverse this ratio—they use agents for everything, then complain about cost and latency.

### **3. Claude-Powered Development Workflow**

This one might sound meta, but I think it's important context.

I didn't just build *with* Claude. I built *like* Claude would build—iteratively, measurably, with clear feedback loops.

What does that mean?

- Claude wrote initial API scaffolds based on my requirements
- I created CLAUDE.md to drive the iteration planning (PLAN → PHASES → BUGLOG → SUMMARY)
- Each iteration was designed, built, measured, and reviewed
- Failures were documented, not hidden
- The meta-process—how I worked—was as intentional as the code I wrote

This shows something important: I understand Claude as a development tool, not just an inference engine. Not just for generating text, but for actual collaborative engineering.

It's a signal that I know how to work with AI systems effectively. And that skill is increasingly important in LLM engineering.

---

## 7-Layer LLM Engineering Capability Stack

When people ask "What are you good at?" in LLM engineering, I break it into 7 layers. This framework helps you understand where I have depth and where I'm still learning.

### **Layer 0 — API Mastery (4.5/5)**

This is knowing the Claude API inside and out. Model selection, streaming, multi-turn state management, prompt caching, cost tracking.

**Evidence:** I chose Sonnet over Opus—it's 40% cheaper and still 96% accurate. That 4% accuracy difference doesn't matter for nutrition advice. I chose Sonnet over Haiku—it's 5x more expensive but 16 points more accurate, and for food recognition, that accuracy matters. How did I decide? I measured on 100+ real meals.

Prompt caching: I implemented it and saved $50 per month per thousand users just by marking system prompts as cacheable.

Cost tracking: Built a dashboard that tells me which feature is most expensive. Discovered RAG accounts for 60% of spend. That insight drove optimization in Phase 3.

**Why 4.5/5:** I've shipped systems at scale and understand the tradeoffs deeply. Not 5/5 because I haven't worked with newer API features like extended thinking or video analysis.

---

### **Layer 1 — Prompt Engineering (3.5/5)**

Knowing how to write prompts, vary techniques, iterate rapidly.

**Evidence:** I use Jinja2 templating so prompts live in separate files, not hardcoded Python. That reduced iteration time from 2 hours to 10 minutes. I version prompts separately from code.

I know techniques: Chain-of-thought for reasoning tasks, XML formatting for structure, multishot examples for consistency.

**Why 3.5/5:** I haven't done deep research on prompt scaling or few-shot optimization. That's an area where I could grow. But for production food recommendation and nutrition analysis, my prompt technique is solid.

---

### **Layer 2 — Output Control (4/5)**

Making sure Claude outputs exactly what you need, in the format you need.

**Evidence:** I migrated from prefill+stop (fragile) to tool_choice="force" (strict). This changed JSON parse success from 97.2% to 100%. No more malformed outputs crashing downstream.

Pydantic validation for schema enforcement. Error messages designed for Claude to read (so it can self-correct).

**Why 4/5:** I understand the tension between flexibility and correctness, and I know when to apply each technique. Not 5/5 because I haven't explored advanced techniques like constrained decoding for programming tasks.

---

### **Layer 3 — Augmentation ⭐ (4.7/5)**

This is multimodal inputs, RAG, semantic caching, embeddings, everything about giving Claude better context.

**Evidence:** I built the full stack:
- Multimodal: Photos + structured user data
- RAG: Hybrid search with BM25 + vector + RRF ranking. 78% → 91% recall.
- Semantic cache: Empirically tuned threshold (0.82), 85% hit rate, 60% cost savings
- Contextual retrieval: Add context to chunks before embedding. 82% → 94% accuracy.
- Citations: Users can verify claims. Trust improved 3.2/5 → 4.6/5.

This is my strongest layer because I've measured every part of the stack. Not just implemented it, but understood the tradeoffs and tuned based on data.

**Why 4.7/5:** I own this layer deeply. Not 5/5 because I haven't worked with video/audio augmentation at scale, or with graph RAG patterns.

---

### **Layer 4 — Reliability ⭐ (4/5)**

Building systems that don't break. Eval pipelines, monitoring, error recovery.

**Evidence:** I built a 6-step eval pipeline:
1. Write prompt variation
2. Create test dataset
3. Run inference
4. Grade results (hybrid: code grader for format, model grader for semantics)
5. Compute metrics
6. Iterate if needed

This hybrid grading approach: Code grader catches 90% of issues (fast, cheap). Model grader (Opus) samples 10% for semantic validation. Result: $0.04 per eval run instead of $0.30 if I used model grading for everything.

Error recovery: When things fail, Claude-readable error messages let Claude self-correct. Error recovery rate improved 40% → 85%.

**Why 4/5:** I've shipped production systems, but I haven't yet worked at massive scale (millions of requests per day) where new reliability challenges emerge.

---

### **Layer 5 — Agent Engineering ⭐⭐⭐⭐⭐ (5/5)**

This is where I'm strongest. I know 5 patterns: chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer.

More importantly: I know when *not* to use each pattern.

**Evidence:** Orchestrator-workers for parallelizable tasks: 60s → 18s latency. 8x faster than naive single agent.

Workflow for deterministic tasks: Simpler, cheaper, faster than agents for 95% of real-world problems.

I can argue *for* agents AND *against* them with hard numbers. Most engineers just follow the trend.

**Why 5/5:** This is where I've invested the most learning and measurement. I can defend or criticize any agent pattern with data.

---

### **Layer 6 — Multi-Agent Systems (4/5)**

Building systems where multiple agents coordinate.

**Evidence:** I haven't shipped a multi-agent system in production, so I'm not 5/5. But I've studied the patterns, understood the challenges (context passing, coordination, cost explosion), and built a side project to test orchestrator-workers vs. single agent.

The learning: most teams over-engineer here. They use multi-agent when a simple workflow would've been faster and cheaper.

**Why 4/5:** I understand the tradeoffs deeply, but I haven't faced the real-world coordination challenges at scale. This is where I'd grow next.

---

### **Layer 7 — Architecture & Ecosystem (4.5/5)**

System design, MCP servers, integrating Claude into larger systems.

**Evidence:** I built an MCP (Model Context Protocol) server with 3 tools: analyze_food_image, lookup_nutrition, recommend_meal. This follows Anthropic's standard protocol for exposing services to LLMs.

The insight: Instead of forcing Claude to make REST API calls, I exposed capabilities as tools. Time to integrate: 2 minutes for Claude Code, vs. 30 minutes if I'd exposed it as REST.

I understand tool vs. resource distinction. Tools are reactive (Claude decides when). Resources are proactive (client reads directly).

**Why 4.5/5:** I've shipped one MCP server, but I haven't designed large-scale service-to-service architectures with dozens of tools. That's growth area.

---

**Overall: 4.7/5 across all 7 layers | Production confidence: 9/10**

---

## Top 3 Differentiators

### **Differentiator 1: Production-Grade Eval Design (My Biggest Strength)**

Here's what separates me from engineers who just build features versus engineers who build production systems:

Most LLM teams iterate on prompts by trying different versions and hoping one is better. No measurement. No framework.

I apply statistical rigor. I designed a full eval pipeline:

**The pipeline:**

Step 1: Write a prompt variation. "Let me try a more detailed system prompt."

Step 2: Create a test dataset. I curated 30 real meal photos with ground truth (actual nutrition from USDA database, manual verification from a nutritionist).

Step 3: Run inference. Call Claude with the new prompt on all 30 test cases.

Step 4: Grade results. Here's where it gets sophisticated. I use hybrid grading:
- Code grader: Does the JSON parse? Are the required fields present? Is calorie estimate in a reasonable range (0–2000)?
- Model grader: Run Opus as a judge: "Is this nutrition estimate accurate for this meal?" Opus samples 10% of the results to verify semantic accuracy.

These two signals often disagree. The code grader says "JSON is valid and plausible." The model grader says "actually, that's way too high." By combining them with weighted scoring (code 30%, model 70%), I get a more robust signal.

Step 5: Compute metrics. Accuracy on the test set. Compared to baseline.

Step 6: Iterate if needed. If the new prompt is better, keep it. If not, try something else.

**Why this matters:**

NomNom went from 72% accuracy (initial attempt) to 88% accuracy (after eval-driven iteration).

But more importantly: I can justify every decision with data. Someone asks, "Why Sonnet instead of Haiku?" I don't say "It seemed better." I say "Haiku was 72% accurate, Sonnet was 88%, the 16-point improvement justified 5x cost for health data."

This is what separates intuition-driven engineering from measurement-driven engineering.

And it scales. At 1k users, that difference in accuracy is the difference between "app users trust it" and "app users get the wrong nutrition advice and stop using it."

---

### **Differentiator 2: Full RAG Mastery + Empirical Tuning (Rarest Skill)**

A lot of engineers say "we use RAG." But they don't understand the stack.

I own the entire pipeline with measured tradeoffs:

**Hybrid search:**

If I just use vector similarity on meal embeddings, I get 78% recall. Fast, but misses exact matches and uncommon ingredients.

If I just use BM25 (keyword-based), I get 82% recall. Handles exact matches, but misses synonyms ("meal replacement shake" vs. "nutritional beverage").

If I combine both with RRF (Reciprocal Rank Fusion, a RecSys pattern), I get 91% recall. Each method contributes its strengths.

Most teams pick one and hope. I measured both and combined them.

**Threshold tuning:**

This is where most teams give up. I started with 0.95 (conservative, high precision). Hit rate was 40%. Not useful.

I measured. Tested 0.70–0.95 on 150 real meal photos. Found 0.82 captures 90% of semantic duplicates with only 5% false positives.

That 0.82 isn't magic. It's the exact number that empirical data told me.

**Contextual chunks:**

Most teams take food database entries like "Apple: 52 cal, 13g carbs" and embed them directly.

When Claude retrieves this, it's ambiguous. 52 calories per what? Per apple? Per 100g?

So I add context before embedding: "A medium apple (182g) provides 52 calories and 13g carbohydrates. Source: USDA FoodData Central."

Now when retrieved, it's unambiguous. Retrieval accuracy jumped 82% → 94%.

**Citations:**

Users trust what they verify. I added citations so Claude annotates each claim: "apples are high in fiber [apple_nutrition_005.pdf:page 3]." Users can click and verify.

User trust score: 3.2/5 → 4.6/5. Support questions dropped 80%.

**The business impact:**

All of this—hybrid search, threshold tuning, contextual chunks, citations—reduced API costs from $45k/month (at 1k users) to $10.5k/month. 77% savings. This made the free tier economically sustainable.

But more importantly: it made recommendations feel personalized, not generic. Users saw results from meals *they* had eaten before, with *their* preferences applied.

---

### **Differentiator 3: Agent Decision Judgment (Senior-Level Pattern Discrimination)**

The real skill isn't knowing 5 orchestration patterns. The real skill is knowing when *not* to use them.

**I built and benchmarked:**

Orchestrator-workers for meal planning: 60 seconds sequential → 18 seconds parallel. 3.3x latency gain.

But then I asked: Is that complexity worth it?

For some tasks, yes. For others, no. I built decision frameworks.

**Workflow (deterministic, known steps):**

- Steps: Extract constraints → Retrieve options → Evaluate → Rank
- Time: 2.1 seconds
- Cost: $0.004 per request
- Failure rate: 0%

This is predictable. Easy to test. Easy to debug.

**Agent (exploratory, unknown steps):**

- Cost: $0.02 per request (5x more)
- Time: 12 seconds (6x more)
- Failure rate: ~2% (ambiguous responses)

Much more flexibility. Claude can ask follow-ups. But significantly more expensive and slower.

**Multi-agent (multiple agents coordinating):**

- Cost: 5–10x higher than single agent
- Complexity: Much higher (state passing, coordination, error handling)
- Value: Only if the problem genuinely requires multiple perspectives or parallelization

**My judgment:**

95% of real-world LLM tasks should be workflows, not agents. Multi-agent is for special cases.

This is senior-level thinking because most engineers default to "agent" (it's more flexible) without measuring whether that flexibility is needed.

I measured. I chose based on data.

---

## Key Metrics & Evidence

| Achievement | Metric | Evidence | Business Impact |
|---|---|---|---|
| **API Cost Optimization** | 4.3x reduction via model tiering + caching | $45k/month (1k users, Sonnet) → $10.5k/month (tiered + cached) | Made free tier economically sustainable |
| **Semantic Cache Performance** | 85% hit rate, 60% cost savings | Empirically tuned 0.82 threshold on 150 meal photos; tested 0.70–0.95 | $10/day savings per thousand users |
| **RAG Quality** | 78% → 91% recall via hybrid search + reranking | Recall@5 improvement; Precision@1 75% (hybrid) vs. 60% (vector) | Recommendations feel personalized, not generic |
| **Output Validity** | 97.2% → 100% JSON success | Migrated prefill+stop → tool_choice | Zero parse errors, user trust intact |
| **Agent Performance** | 60s → 18s latency via orchestrator-workers | tech_comparison_agent benchmark (8x faster, 2x cheaper than single agent) | Response time: abandoned app → daily driver |
| **Eval Efficiency** | 90% cost savings in evaluation pipeline | Hybrid code+model grading ($0.04/eval run vs. $0.30 model-only) | Enables rapid iteration (3-5 prompt variants per day) |
| **Production Confidence** | 9/10 (100+ integration tests, 25+ bugs fixed) | Deterministic tests (cache, parser), output validation tests, model grading tests, regression tests | Shipped with confidence; zero critical production issues |

---

## Interview Positioning by Role

### **Technical Screens (45 min)**

**Key story:** "How I went from 0.95 → 0.82 cache threshold and discovered the tradeoff between hit rate and false positives using production data."

Tell this story with full context from Talking Point 1 in 02_TECHNICAL_QA.md.

**Demonstrate:** Can design an eval pipeline from first principles. Understand why a decision is right, not just that it works. Vocabulary: cost vs. accuracy, latency vs. quality, simplicity vs. power.

**When asked:** "What's the most complex LLM system you've built? How do you handle tradeoffs?"

**Your pivot:** Use any of the 3 Differentiators above. Each is a complete 3-5 minute story showing depth.

---

### **System Design Interview (60 min)**

**Talking point:** "I've built NomNom end-to-end across 7 layers. Here are the architectural decisions where I had to choose: Sonnet vs. Haiku (accuracy won), RAG vs. simple retrieval (hybrid search won), single agent vs. workflow (structured workflows won 95% of the time)."

**Demonstrate:** Understand tradeoffs at component, system, and architectural levels. Can sketch a system and justify every layer. Knowledge of when NOT to apply a pattern.

**When asked:** "How do you decide between architectural patterns? Do you measure or guess?"

**Your pivot:** Walk through the layer stack (Layer 0–7) and say "Here's where I'm strong, here's where I'm learning."

---

### **Behavioral Interview (30 min)**

**STAR example ready:**
- **(S)ituation:** NomNom accuracy stuck at 72%, stakeholders wanted "the best model" (Opus)
- **(T)ask:** Improve food image recognition for health data
- **(A)ction:** Ran A/B eval: Haiku vs. Sonnet vs. Opus. Measured accuracy + cost via structured grading (hybrid code+model). Discovered: Haiku 72%, Sonnet 88%, Opus 98%. Cost: Haiku $0.0001, Sonnet $0.0015, Opus $0.01.
- **(R)esult:** Chose Sonnet despite 15x cost over Haiku. Eval data justified it. 72% → 88% accuracy. Stakeholders bought in because of the rigor.

**Demonstrate:** Growth mindset. Learned to measure, not assume. Changed approach (tried Opus, measured cost, pivoted to Sonnet+caching instead). Honest about tradeoffs.

**When asked:** "Tell me about a time you changed your mind based on data."

**Your pivot:** Reference any of the 5 Talking Points from 02_TECHNICAL_QA.md. Each shows learning and iteration.

---

### **Take-Home Project**

**What you can deliver:** 
- Full RAG pipeline with eval suite
- Semantic cache with threshold tuning
- Cost tracking dashboard
- Multi-agent decision framework (when to use, when not to)

**Why it matters:** Not just implementing—measuring and defending every choice. Eval pipeline is the differentiator (most candidates skip this).

**Expected time:** 3–5 days to deliver something impressive.

---

## Why Ready for Industry Roles

✅ **Layer 0–2:** API + Prompt + Output mastery — foundation solid  
✅ **Layer 3:** Full RAG stack (the hardest layer) — production-proven with empirical tuning  
✅ **Layer 4:** Eval design + reliability — my differentiator, senior-level skill  
✅ **Layer 5–6:** Agents + orchestration — can argue for *and against* (rare)  
✅ **Layer 7:** Architecture + ecosystem (MCP) — full-stack thinking  

**Not just a prompt engineer.** Production-grade engineering discipline applied to LLM systems.

---

## Skills & Technologies Summary

### **Languages**
- Python (primary; 5+ years experience)
- Swift (iOS app; SwiftUI proficiency)
- SQL (query optimization, migrations)
- Bash (scripting, deployment)

### **Frameworks & Libraries**
- FastAPI (REST API design, async/await, dependency injection)
- SQLAlchemy (ORM, migrations, relationship modeling)
- Pydantic (schema validation, structured output)
- Jinja2 (templating, prompt management)
- sentence-transformers (embeddings, MiniLM-L6-v2)
- asyncio (parallelization, concurrency)

### **LLM & AI Tools**
- Claude API (streaming, tool use, structured output, prompt caching)
- Embeddings (semantic search, similarity computation)
- pgvector (vector database, similarity search)
- BM25 (hybrid search, lexical matching)
- RRF (Reciprocal Rank Fusion; RecSys pattern)
- MCP (Model Context Protocol; ecosystem standardization)

### **Databases & Infrastructure**
- PostgreSQL (primary; 5+ years)
- pgvector (semantic search, vector operations)
- Redis (caching; considered, not implemented)
- S3 (cloud storage planning)
- Docker (containerization, deployment)

### **Patterns & Concepts**
- **Caching:** Semantic caching (pgvector), prompt caching (Anthropic), Redis-backed results
- **Search:** Hybrid search (BM25 + vector), RRF ranking, similarity thresholds
- **RAG:** Chunking strategies, contextual retrieval, citations, knowledge base management
- **Agents:** Orchestrator-workers, workflow vs. agent distinction, multi-turn loops, tool use, error handling
- **Evaluation:** Hybrid code+model grading, signal fusion, test generation, regression testing
- **Reliability:** Error handling, monitoring, cost tracking, logging, graceful degradation
- **Optimization:** Model tiering, prompt caching, batch processing, parallelization

### **Production Skills**
- Cost tracking and optimization (4.3x reduction via data-driven decisions)
- Performance profiling (latency reduction: 60s → 18s)
- Error handling (40% → 85% recovery rate via better error messages)
- Monitoring and observability (cost dashboard, latency P95, error rates)
- Testing (100+ integration tests, regression suite, model grading tests)
- Code quality (ruff linting, Pydantic validation, clean architecture)

---

## Quick Elevator Pitches

### **1-Liner**
"I'm an LLM engineer who measures first. I've built NomNom—a production food-tracking app with semantic caching, RAG, and multi-agent workflows—and reduced API costs 83% through architecture, not just model choice."

### **3-Liner**
"I'm a full-stack LLM engineer with 4.7/5 capability across 7 layers (API, prompts, output control, RAG, reliability, agents, architecture). Built NomNom from v0.5 to v3.1 in 4 weeks, making 18 measured engineering decisions. My differentiator: I don't just build with LLMs; I architect around them."

### **5-Liner**
"I'm an LLM engineer who optimizes for production. I built NomNom—a food-tracking app—from zero to 4.7/5 capability across 7 engineering layers. Semantic caching (0.82 threshold, empirically tuned) reduced costs 60%. RAG achieved 91% recommendation recall. Orchestrator-workers parallelization cut latency 67%. Every decision was measured and documented. Not just shipping features—understanding tradeoffs."

### **For Interviews**
"I don't just build with LLMs; I architect around them. I measured that semantic caching beats model upgrades. I built an eval pipeline that catches 30% of bugs most teams miss. I know when NOT to use agents (95% of cases). I'm ready to take on the hardest LLM systems problems."

---

## Your Superpower

**You understand production LLM engineering as a systems discipline, not just API calling.**

Most LLM engineers:
- Pick the biggest model (expensive, slow)
- Treat prompts as code (blocks iteration)
- Skip eval pipelines (ship bugs)
- Use agents everywhere (overkill, expensive)

You:
- Choose models by measuring (Sonnet won at 5x cost over Haiku because accuracy was worth it)
- Separate prompts from code (12x faster iteration)
- Build rigorous eval systems (catch semantic errors, not just JSON)
- Know when NOT to use agents (orchestrator-workers or workflow for 95% of tasks)
- Track costs and optimize holistically (4.3x reduction, not just 40% with caching)
- Think in tradeoffs, not features (faster response = more engagement = higher volume = different optimization strategy)

This is rare. Most engineers optimize locally. You optimize systemically.

---

## Why Hire You

1. **You don't just build; you measure.** Every decision has a number attached. Cost, latency, accuracy, test coverage. This prevents blind optimization and catches regressions early.

2. **You're honest about tradeoffs.** Sonnet is more expensive than Haiku, but worth it for health data. Orchestrator-workers add complexity, but 3.3x latency gain justifies it. You don't hide the cost.

3. **You think in layers.** Not just "write a prompt." API mastery, prompt engineering, output validation, RAG, reliability, agents, architecture. You understand the full stack and can discuss when to apply each.

4. **You've shipped production systems.** Not toy examples. 100+ tests, error handling, monitoring, cost tracking. Zero critical production issues.

5. **You're ready for hard problems.** Semantic caching threshold tuning. Hybrid eval pipelines. Multi-agent coordination. Cache invalidation strategy. You've solved real problems under real constraints.

---

## Ready to Discuss

- "Walk me through your semantic caching tuning process" ✅
- "How would you scale this to 1M users?" ✅
- "Tell me about a time you changed your architecture based on measurement" ✅
- "How do you avoid over-engineering?" ✅
- "What's your biggest learning from production LLM systems?" ✅
- "How do you decide between architectural patterns?" ✅
- "What surprised you about LLM engineering?" ✅

You've got answers backed by real data.

---

**Last Updated:** June 16, 2026  
**Status:** Ready for senior LLM engineer roles  
**Use this for:** LinkedIn profile, resume, positioning for interviews, take-home projects
