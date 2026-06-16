# NomNom Portfolio Story: From v0.5 to v3.1

**Timeline:** May 17 — June 13, 2026 (4 weeks + 1 week learning → Phase 7)  
**Language:** Python/FastAPI (backend), SwiftUI (iOS)  
**Core Tech:** Claude API, pgvector, LLM orchestration, MCP

---

## Quick Versions (Use in Interviews)

### 2-Minute Elevator Pitch

> "I built NomNom, an AI nutrition app, from v0.5 to v3.1 in 4 weeks. The challenge: make it accurate, affordable, and extensible. I made 18 key engineering decisions—each one had a measurable outcome. For example, I chose Sonnet for food recognition (not Haiku) because accuracy matters for health data; the 40% quality improvement justified 5x cost increase. I implemented semantic caching to reduce API costs by 60%, model tiering to optimize by task, and RAG with hybrid search to improve recommendations from 70% accuracy to 91%. By the end, I had a fully functional app, a working MCP server, and deep understanding of every design choice I made."

### 5-Minute Technical Screen

> "I built NomNom as a learning project to master LLM engineering. It went through 6 phases:
> 
> **Phase 1 (v0.5):** Basic food recognition. I learned API fundamentals and prompt engineering. Built Jinja2-based templating so prompts are product assets, not code.
> 
> **Phase 2 (v1.0):** Made it stable. Discovered that 97% of issues were JSON parsing. I moved to `tool_choice` for structured output and implemented hybrid eval (code + model grading) to catch semantic errors code can't.
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

### 15-Minute Deep Dive

See "Full Story" section below.

---

## Full Story

### Phase 0: Context & My Mission (May 10–17)

**背景/痛点 (Context):**
NomNom v0.4 exists but was built with heavy AI assistance. I can use the app, but can't defend *why* each design choice was made. I don't truly own the architecture—I'm a user of my own code, not its engineer.

**我的角色 (My Role):**
Architect and rebuild NomNom from the ground up, phase by phase. Own every design decision from first principles. Transform understanding from 0/5 to 4+/5 across all 7 layers of LLM engineering.

**采取的核心措施 (Key Actions):**
Design a 10-week structured learning plan (Phases 1–6) where:
1. Learn one capability layer
2. Apply it immediately to NomNom
3. Refactor production code
4. Measure outcomes quantitatively

**量化结果 (Measurable Outcome):**
- v0.4 → v3.1 in 4 production weeks
- 18 documented design decisions with data backing each
- 4.7/5 capability across all 7 LLM engineering layers

---

### Phase 1: API Mastery & Prompt Engineering (May 17–31)

**背景/痛点 (Context):**
Early NomNom hardcodes prompts directly in Python code. Every prompt iteration requires code change → deploy → retest. A/B testing takes 2 hours per variant. Product is locked behind engineering cycles.

**我的角色 (My Role):**
Full-stack owner of prompt infrastructure. Responsible for enabling fast iteration while maintaining quality.

**采取的核心措施 (Key Actions):**
1. Implement Jinja2-based prompt templating system
2. Extract prompts into separate `.j2` template files (not Python strings)
3. Build runtime variable injection layer
4. Make prompts version-controlled separately from code

**量化结果 (Measurable Outcome):**
- Prompt iteration time: 2 hours → 10 minutes (12x faster)
- Code churn: 80% reduction (fewer commits touching prompt content)
- Food recognition baseline: 72% accuracy with multimodal prompts
- **Interview signal:** "Prompts are product assets, not infrastructure code. Separate them."

**v0.5 Deliverable:**
- Working food recognition pipeline with modular prompts
- 15 learning notebooks covering API fundamentals and prompt techniques (CoT, XML, multishot)

---

### Phase 2: Output Control & Reliability (June 5–8)

**背景/痛点 (Context):**
Phase 1 uses prefill+stop for JSON output. It works but is fragile:
- 2.8% of calls produce unparseable JSON (due to prompt injection or hallucination)
- Parser errors only caught *after* Claude returns bad data
- Users see cryptic "JSON_VALIDATION_ERROR" with no guidance on how to fix it
- No systematic way to catch semantic errors (e.g., "apple" recognized as "apricot")

**我的角色 (My Role):**
Architect output control strategy and build evaluation system. Responsible for 100% output validity and measurable accuracy improvement.

**采取的核心措施 (Key Actions):**

*1. Implement tool_choice for Schema Enforcement*
- Migrate from prefill+stop to `tool_choice="force"` with strict JSON schema
- Claude must output exactly the defined structure; no variations possible
- Rewrite error messages to be Claude-readable: "Image too blurry; ask user to retake"

*2. Build Hybrid Eval System (Code + Model)*
- Code grader: Validate required fields, numeric plausibility (fast, cheap)
- Model grader (Opus): Evaluate semantic accuracy on sampled results only
- Combine scores via weighted average (RecSys-inspired multi-channel fusion)

**量化结果 (Measurable Outcome):**

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| JSON parse success | 97.2% | 100% | +2.8 points |
| Error recovery rate | 40% | 85% | +45 points |
| Eval cost per run | $0.30 | $0.04 | 90% savings |
| Eval latency | 45s | 8s | 5.6x faster |
| Error detection rate | — | 93% | Catches semantic errors |
| Food accuracy | 72% | 88% | +16 points |

**v1.0 Deliverable:**
- 100% valid JSON output guarantee (schema-enforced)
- Production-grade eval pipeline (28/30 test cases passed)
- 88% food recognition accuracy
- **Capability milestone:** Layer 2 (Output Control) and Layer 4 (Reliability) both 4/5

---

### Phase 3: RAG & Semantic Cache (June 9–18)

**背景/痛点 (Context):**
Every user query triggers a full Claude API call, even for repeated requests. "What did I eat yesterday?" costs the same as a new query with identical meaning. No knowledge base integration means recommendations lack personalization and grounding.

**我的角色 (My Role):**
Build knowledge retrieval system and caching infrastructure. Responsible for:
1. Reducing redundant API calls via intelligent caching
2. Grounding recommendations in verified nutrition data
3. Maintaining accuracy while reducing cost

**采取的核心措施 (Key Actions):**

*1. Semantic Cache with Data-Driven Threshold*
- Embed user requests; compare cosine similarity to cached requests
- Empirical tuning: Measured 100 real queries, manually labeled semantic duplicates
- Identified optimal threshold: 0.82 (captures 90% duplicates with 5% false positives)

*2. Hybrid Search System (BM25 + Vector + RRF)*
- Problem: Pure vector search misses exact matches ("USDA ID 01234")
- Solution: Combine BM25 (lexical) + Vector (semantic) via RRF (Reciprocal Rank Fusion)
- Applied RecSys multi-channel recall pattern

*3. Enable Citations for Verification*
- Tag every nutrition claim with source document
- Allows users to verify recommendations
- Essential for health data credibility

**量化结果 (Measurable Outcome):**

| Metric | Phase 2 | Phase 3 | Improvement |
|--------|---------|---------|------------|
| Cache hit rate | 0% | 60% | — |
| API call reduction | baseline | 40% | — |
| Hit latency | 2000ms | 150ms | 13x faster |
| Recall@5 | 70% | 91% | +21 points |
| Precision@1 | 60% | 75% | +15 points |
| User trust score | 3.2/5 | 4.6/5 | +44% |
| Recommendation accuracy | 70% | 91% | +21 points |

**v2.0 Deliverable:**
- Production RAG pipeline with hybrid search (91% recall)
- Semantic cache reducing costs 40% and latencies 13x
- Citations system enabling trust
- **Capability milestone:** Layer 3 (Augmentation) now 5/5

---

### Phase 4: Cost & Latency Optimization (June 10)

**背景/痛点 (Context):**
NomNom feature-rich but economically unsustainable: using Sonnet for every task costs $1.50/user/day. At 1k users: $1,500/day, $45k/month. Business cannot support this cost structure. Need to optimize without sacrificing core quality (food recognition accuracy).

**我的角色 (My Role):**
Lead cost optimization initiative. Responsible for:
1. Reducing daily operational cost by 4x
2. Maintaining food recognition accuracy (the core value proposition)
3. Building observability to prevent cost regression

**采取的核心措施 (Key Actions):**

*1. Implement Model Tiering by Task*
- Food image recognition → Sonnet ($0.0015/req, multimodal accuracy critical)
- JSON extraction → Haiku ($0.0001/req, already schema-validated)
- Meal recommendation → Sonnet ($0.0015/req, reasoning required)
- Eval grading → Opus ($0.01/req, used sparingly)

Tradeoff analysis: Haiku fails on 60% of multi-ingredient dishes (muesli vs. granola). For health data, accuracy matters more than cost. The 40% quality improvement justifies 15x cost increase.

*2. Deploy Prompt Caching*
- Identify static content: 400-token system prompt (nutritionist role + tool schema) sent in every request
- Cache for 1 hour (ephemeral); subsequent calls pay 90% less per token
- Math: Uncached 72,400 tokens/hour → Cached 7,600 tokens/hour (89% savings)

*3. Build Cost Tracking Dashboard*
- Log per-call metrics: tokens, latency, model, computed cost
- Query capabilities: "Daily spend," "Cost by feature," "P95 latency"
- Enable data-driven optimization decisions

**量化结果 (Measurable Outcome):**

| Metric | Before | After | Improvement |
|--------|--------|-------|------------|
| Daily cost per user | $1.50 | $0.35 | 4.3x reduction |
| Monthly cost @ 1k users | $45k | $10.5k | 76% savings |
| Input token cost/user/day | $0.20 | $0.06 | 70% reduction |
| Cache hit rate | 0% | 90% | — |
| Food accuracy | 88% | 88% | Maintained |
| Unit economics | Unsustainable | Viable | — |

**v2.5 Deliverable:**
- Sustainable cost model ($10.5k/month for 1k users)
- Full cost visibility (daily spend by feature, cost drivers identified)
- Model tiering maintaining accuracy while reducing cost 4.3x
- **Capability milestone:** Layer 0 (API) advanced now 4/5

---

### Phase 5: Workflow & Multi-Agent Orchestration (June 10–12)

**背景/痛点 (Context):**
Simple queries work fine, but complex requests expose limitations:
- "Recommend meals for next week" needs dynamic reasoning → Single agent solution loops 21 times (7 days × 3 meals)
- Latency balloons to 60+ seconds
- Cost explodes due to sequential LLM calls
- Need to distinguish when fixed workflows are better than open-ended agents

**我的角色 (My Role):**
Architect decision framework for agent design. Responsible for:
1. Choosing right orchestration pattern per use case
2. Optimizing latency for complex tasks
3. Teaching when workflow beats agent (and vice versa)

**采取的核心措施 (Key Actions):**

*1. Implement Workflow for Meal Recommendation*
- Insight: "Recommend 600-cal lunch for weight-loss diet" has known, fixed steps
- Pipeline:
  1. Extract constraints (Claude call)
  2. RAG retrieve matching foods (Python, no LLM)
  3. Evaluate each option (Claude call)
  4. Rank and finalize (Python, no LLM)
- Deterministic steps enable auditing and testing

*2. Deploy Orchestrator-Workers Pattern for Weekly Planning*
- Problem: Planning 7 days × 3 meals = 21 sequential LLM calls = 60s latency
- Solution: Orchestrator (Sonnet) spawns 7 workers in parallel, one per day
- Workers run concurrently (asyncio.gather), aggregate results at end
- Applied parallelization for coordination-heavy tasks

*3. Define Decision Framework*
- **Use workflow:** Steps known upfront, predictable sequence, testable
- **Use single agent:** Open-ended exploration, Claude decides path, unpredictable
- **Use orchestrator-workers:** Coordinate 3+ parallel subtasks, aggregate results

**量化结果 (Measurable Outcome):**

| Metric | Single Agent | Workflow | Orchestrator-Workers |
|--------|--------------|----------|-------------------|
| Latency (recommendation) | 4.2s | 2.1s | — |
| Latency (weekly plan) | 60s | — | 18s |
| Cost (recommendation) | $0.008 | $0.004 | — |
| LLM calls (weekly) | 21 sequential | — | 21 parallel |
| Parallelization | None | None | 7x concurrent |
| Debuggability | Low | High | High |

**v3.0 Deliverable:**
- Meal recommendation workflow (2.1s latency, $0.004 cost, highly debuggable)
- Fridge-leftovers agent (open-ended reasoning for inventory-based cooking)
- Weekly meal planning via orchestrator-workers (18s latency, 3.3x faster than sequential)
- Decision framework documented and applicable to future tasks
- **Capability milestone:** Layer 5 (Agent) 5/5, Layer 6 (Multi-agent) 4/5

---

### Phase 6: MCP & Ecosystem Standardization (June 13)

**背景/痛点 (Context):**
NomNom is feature-complete but siloed: only accessible via iOS app or custom REST API. Other tools (Claude Code, future agents, third-party apps) cannot easily integrate NomNom's capabilities. Integration requires custom HTTP client setup, auth management, URL handling. High friction, limited ecosystem reach.

**我的角色 (My Role):**
Architect ecosystem-facing interface. Responsible for:
1. Standardizing NomNom's capability exposure
2. Reducing integration friction
3. Positioning NomNom as a composable service, not just an app

**采取的核心措施 (Key Actions):**

*1. Build MCP (Model Context Protocol) Server*
- Implement Anthropic's standard protocol for LLM tool exposure
- Expose three capability types:
  - **Tools:** `analyze_food_image`, `lookup_nutrition`, `recommend_meal` (reactive—Claude initiates)
  - **Resources:** `nomnom://foods/{id}`, `nomnom://history` (proactive—client reads directly)
  - **Prompts:** `daily_summary` template (pre-baked, reusable)

*2. Enable Ecosystem Integration*
- Register NomNom with Claude Code: `mcp add nomnom`
- Standardized protocol enables future tool integrations

**量化结果 (Measurable Outcome):**

| Metric | Before | After | Improvement |
|--------|--------|-------|------------|
| Integration friction | 5 lines code | 1 line config | 5x simpler |
| Integration time | 30 min | 2 min | 15x faster |
| Ecosystem reach | iOS + REST | iOS + REST + Claude + future | Unlimited |
| Protocol coverage | Custom | MCP standard | Future-proof |

**v3.1 Complete Deliverable:**
- Production app: Food recognition (88%), RAG recommendations (91%), intelligent meal planning
- Cost-optimized infrastructure: 4.3x cost reduction, sustainable unit economics
- Ecosystem standardization: MCP server enabling unlimited integrations
- Complete understanding: 18 design decisions, all measured and defensible
- **Capability milestone:** All 7 layers at 4–5/5 (Layers 3,5: 5/5, others: 4/5)

---

## Journey Summary: Key Milestones

| Phase | Version | Primary Focus | Key Decision | Measurable Outcome |
|-------|---------|---|---|---|
| 1 | v0.5 | API + Prompts | Jinja2 templating | 72% accuracy, 10min prompt iteration |
| 2 | v1.0 | Output control | tool_choice + hybrid eval | 100% valid JSON, 88% accuracy |
| 3 | v2.0 | RAG + Cache | Hybrid search + citations | 91% recall, 60% cache hit rate |
| 4 | v2.5 | Cost + Latency | Model tiering + caching | 4.3x cost reduction, sustainable |
| 5 | v3.0 | Workflows + Agents | Orchestrator-workers | 18s weekly planning, parallel scaling |
| 6 | v3.1 | Extensibility | MCP server | Ecosystem integration ready |

---

## The Learning Thesis

**Why NomNom?**

The project served dual purpose:
1. **Build something real:** Not toy examples, but production-grade decisions
2. **Learn by doing:** Each phase taught a capability stack layer, immediately applied

**Why it worked:**
- Learning targets were concrete: "Make food recognition 88% accurate" (Phase 1–2)
- Decisions had measurable outcomes: "Cache hit rate is 60%, not 30%" (Phase 3)
- Challenges were real: "Can we afford 1k users?" (Phase 4)
- Architecture evolved intelligently: Phase 5's workflow vs. agent decision emerged from Phase 2–4 foundation

**What makes this different:**
- Not just "I built a food app"
- But "I made 18 engineering decisions, each with a tradeoff, each measured"
- And "I understand the architecture at every level—why Jinja2, why 0.82 threshold, why MCP"

---

## Interview Talking Points (Extract From This Story)

### 2-Min Version
*Elevator pitch above*

### 5-Min Version
*Technical screen above*

### 15-Min Version
*Full story above*

### Company-Specific Versions

**For an LLM infra company:**
> "I'm particularly proud of the cost & latency work (Phase 4). I didn't just optimize; I measured. Model tiering saved 4.3x cost. Prompt caching saved 89% tokens. I built a dashboard so you can see where money goes. This taught me: cost isn't theoretical; it's a first-class constraint in LLM products."

**For an AI safety company:**
> "In Phase 3, I added citations to prevent hallucination. Users can verify every nutrition claim. In Phase 2, I designed error messages for Claude to read, not humans—this improved error recovery from 40% to 85%. I think deeply about how to make LLM systems reliable."

**For a healthcare company:**
> "Food recognition accuracy is 88%. Not 99%, but chosen deliberately. The model (Sonnet) costs 5x more than alternatives (Haiku), but the 40% quality improvement matters for health data. Every user's daily nutrition estimate is wrong if I chose wrong here. This taught me: optimize for what matters, not what's cheap."

**For a startup/scaleup:**
> "I went from v0.5 to v3.1 in 4 weeks. The key was velocity + measurement. Every phase added one layer of capability and one measurement. Phase 1: added templating, measured prompt iteration time. Phase 4: added caching, measured cost. This let me build fast and validate."

---

## What This Demonstrates

**Technical Skills:**
- API mastery (retry logic, streaming, caching)
- Prompt engineering (templating, techniques)
- Output control (tool_choice, structured output)
- RAG (embedding, chunking, hybrid search, citations)
- Reliability engineering (eval pipelines, error handling)
- Agent design (workflows, orchestrator-workers)
- Ecosystem thinking (MCP, extensibility)

**Engineering Judgment:**
- Tradeoff thinking (Sonnet vs. Haiku, accuracy vs. cost)
- Data-driven decisions (0.82 threshold measured, not guessed)
- Measurement orientation (cost dashboard, eval metrics)
- When to apply patterns (workflow for meal recommendation, agent for fridge)

**Communication:**
- Can tell a story (v0.5 → v3.1 arc)
- Can extract lessons (why each decision mattered)
- Can articulate uncertainty (what I'd do differently now)
- Can map to business value (sustainable cost, user trust)

**Learning Velocity:**
- 4 weeks, 10 weeks total learning
- Each phase added depth, not just breadth
- Self-driven: Identified gaps, filled them

---

## Lessons Learned (Retrospective)

### What Went Well
✅ Measurement culture from Day 1 (every decision has numbers)  
✅ Iterative deepening (v0.5 → v3.1, each phase built on previous)  
✅ Real constraints (cost, latency, accuracy—not theoretical)  
✅ Ecosystem thinking early (Phase 6 MCP wasn't forced; natural evolution)

### What I'd Do Differently
⚠️ More A/B testing earlier (Phase 1–2 could have had more prompt variants measured)  
⚠️ Cost tracking from Day 1, not Phase 4 (would have optimized earlier)  
⚠️ User testing would have shown 0.82 threshold works; could have saved time  

### Lessons for Future Projects
💡 **Measurement is not optional:** Every decision should have a measurable outcome  
💡 **Constraints drive innovation:** "Can we afford 1k users?" led to model tiering  
💡 **Patterns emerge, not imposed:** Workflow vs. agent distinction became clear through building, not upfront design  
💡 **Ecosystem matters:** MCP wasn't in the original plan, but added it because future tooling will expect it

---

## What's Next (Phase 7)

**Option A: Job-Search Multi-Agent System**
- Use Orchestrator-Workers pattern from NomNom
- 4 parallel workers: job search, JD analysis, resume tailoring, cover letter
- Measure: keyword match rate, bullet quality, time to application

**Option C: Interview Prep**
- Document technical decisions (done: NOMNOM_TECHNICAL_DECISIONS.md)
- Mock interviews, refine storytelling
- Practice 2–3 NomNom stories for every interview

---

## Final Note

This story is about **one journey:** learning to be an LLM engineer by building something real, measuring everything, and understanding every tradeoff.

The goal isn't to impress interviewers with "I built an app."

The goal is to show: **"I understand how LLM systems work, I can make tradeoffs, I measure to know if I'm right, and I learn fast."**

That's the story.
