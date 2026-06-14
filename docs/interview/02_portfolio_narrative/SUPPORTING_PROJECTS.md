# Supporting Projects — Beyond NomNom

## Overview

Alongside the core NomNom journey (v0.5 → v3.1), I've built two supporting projects that demonstrate specific LLM engineering patterns in isolation:

1. **tech_comparison_agent** — Multi-agent orchestration benchmark (Phase 5)
2. **Future Phase 7 projects** — Extension work if continuing the learning journey

---

## Project 1: tech_comparison_agent (Phase 5)

### Why I Built It

During Phase 5 (Agent Engineering), I needed to understand the **orchestrator-workers pattern** in isolation before integrating it into NomNom's meal recommendation workflow. I built a dedicated multi-agent system to compare PyTorch vs. TensorFlow architecture, design, and performance characteristics.

### What It Does

**Input**: Comparison task → "Compare PyTorch and TensorFlow architecture and performance"

**Architecture**: 
- **Orchestrator**: Decides what needs to be compared (task decomposition)
- **4 Workers** (parallel execution):
  1. Architecture worker: "Summarize PyTorch's core architecture"
  2. Design worker: "Summarize TensorFlow's core design philosophy"
  3. Performance worker: "Compare execution speed and memory usage"
  4. Integration worker: "Compare ease of integration with LLM ecosystems"
- **Synthesis**: Orchestrator collects results, synthesizes into unified comparison

### Key Learning (The Core Evidence)

Built two versions and benchmarked them:

| Approach | Latency | Cost | Notes |
|---|---|---|---|
| **Orchestrator-Workers** (parallel execution) | 10 seconds | $0.023 | 4 workers in parallel; fast synthesis |
| **Single Agent** (sequential task) | 80 seconds | $0.045 | Single agentic loop; hits token limits on synthesis; token explosion from multi-turn history |

**Impact**: Orchestrator-workers is **8x faster and 2x cheaper** for parallelizable tasks.

**Key insight**: The architectural choice (orchestrator-workers vs. single agent) is driven by whether subtasks are *independent*. If they are, parallelize. If they're *sequential and tightly coupled*, use workflow or single agent.

### Why It Matters for Interviews

✅ **Demonstrates mastery**: Can architect a multi-agent system from first principles  
✅ **Quantified tradeoff**: Not "agents are good" but "agents are right for this task, wrong for others"  
✅ **Decision framework**: Shows I can make the "which pattern?" judgment with evidence  
✅ **Parallelization insight**: Understands that cost+latency benefit only comes if tasks are truly independent  

### Code Location
`learning_lab/phase_5/tech_comparison_agent/` (directory with full implementation, benchmarks, results)

### Interview Narrative

> "In Phase 5, I learned 5 orchestration patterns. To understand when orchestrator-workers actually wins, I built a dedicated multi-agent system that compares PyTorch vs. TensorFlow. I ran both approaches on the same task: orchestrator-workers with 4 parallel workers, and a single agentic loop. The results were clear: orchestrator-workers was 8x faster (10s vs. 80s) and 2x cheaper ($0.023 vs. $0.045). But here's the insight — it only works because the 4 subtasks were *independent*. If they needed to feed information to each other sequentially, the single agent would win. This taught me that pattern selection isn't about 'orchestrator-workers is better' — it's about 'understand your task structure first.'"

---

## Project 2: Job-Search Multi-Agent (Phase 7 Option A)

### Concept (Planned)

If continuing into Phase 7, the next major project will be a **Job-Search Multi-Agent System** — a practical extension that applies NomNom patterns to a real-world problem.

### Why Phase 7 Matters

Phases 1–6 completed the **learning journey** (API → Prompts → Output → Augmentation → Reliability → Agents → Architecture). Phase 7 is about **applying** those patterns to a new domain (job search) to prove they transfer.

### System Design

**Orchestrator**: Job search planner (decompose into subtasks)

**4 Workers** (parallel execution):
1. **Job Search Worker**: Find relevant openings from job boards + RSS feeds
2. **JD Analysis Worker**: Parse requirements, seniority, skills, compensation
3. **Resume Tailoring Worker**: Customize resume to match each JD
4. **Cover Letter Worker**: Write targeted cover letter with specific examples

**Output**: Ranked list of jobs with resume + cover letter ready to submit

### Technical Challenges (Why It's Interesting)

| Challenge | NomNom Pattern | How It Transfers |
|---|---|---|
| Structured output from workers | tool_choice (Layer 2) | Each worker outputs JSON schema (JD fields, resume sections, letter paragraphs) |
| Quality evaluation | Eval pipeline (Layer 4) | Grade each worker's output: relevance, completeness, tone matching |
| Reliable orchestration | Workflow patterns (Layer 5) | Orchestrator handles worker failures, re-runs with fallback logic |
| Cost control | Model tiering (Layer 0) | Lightweight models (Haiku) for parsing, Sonnet for creative content (cover letters) |
| Caching for speed | Semantic cache (Layer 3) | Cache parsed job descriptions, resume chunks, company profiles across runs |

### Why It's Perfect for Phase 7

✅ Proves patterns *transfer* to new domain  
✅ Solves a real problem (job search is hard)  
✅ Demonstrates all 7 layers in a new context  
✅ Interview gold: "I didn't just learn patterns in isolation; I applied them to build something useful"  
✅ Potential product: Could be useful as a standalone tool  

### Estimated Scope

**Duration**: 3–5 days  
**Deliverables**:
- `learning_lab/phase_7/job_search_agent/` (implementation)
- Eval suite comparing manual vs. AI-generated resume + cover letters
- Cost/latency baseline vs. optimization (Phase 7 Option B: cost engineering)
- `docs/iterations/17-job-search-agent/SUMMARY.md` (retrospective)

### Interview Narrative (If Built)

> "Phases 1–6 taught me the 7-layer LLM engineering stack through NomNom. Phase 7 was about asking: 'Do these patterns actually transfer?' So I built a job-search multi-agent system. Same architecture: orchestrator-workers decomposing into parallelizable tasks, eval pipeline for quality, semantic caching for speed, model tiering for cost. Different domain. Same principles. What I discovered: [results from Phase 7]. Here's why this matters for your company: [company-specific insight]."

---

## Lessons Learned Across Supporting Projects

### From tech_comparison_agent
- Parallelizable tasks (independent subtasks) → orchestrator-workers wins
- Non-parallelizable tasks (sequential, tightly coupled) → workflow or single agent wins
- Cost + latency improvements only emerge if architecture matches task structure
- Benchmarking is non-negotiable — intuition is wrong 95% of the time

### From Job-Search Multi-Agent (If Built)
- Patterns from Phase 1–6 transfer to new domains
- Not every task needs agents — understand your task first
- Quality gates (eval + testing) scale across agents
- Cost optimization is easier when you *measure* first

---

## Why These Projects Matter for Interviews

| Interviewer Question | How Supporting Projects Answer It |
|---|---|
| "Can you show me an example of multi-agent architecture?" | tech_comparison_agent: orchestrator-workers with benchmarks |
| "How do you decide between patterns?" | Both projects: evidence-driven decision framework, not hype |
| "Do your patterns transfer to other domains?" | Phase 7 job-search: same stack, different problem, same principles |
| "What's your biggest learning from this journey?" | tech_comparison_agent: Task structure determines architecture; don't use agents everywhere |
| "What would you build next?" | Phase 7 job-search (if built): Real-world application of NomNom patterns |

---

## File References

- **tech_comparison_agent implementation**: `learning_lab/phase_5/tech_comparison_agent/`
- **tech_comparison_agent results**: `learning_lab/phase_5/tech_comparison_agent/benchmark_report.md` (latency, cost, analysis)
- **Phase 5 retrospective** (context for tech_comparison_agent): `docs/learning/03_phase_retrospectives/phase_5_retro.md`
- **NomNom main portfolio**: `docs/interview/02_portfolio_narrative/NOMNOM_PORTFOLIO_STORY.md`
- **Technical decisions** (includes Phase 5 agent patterns): `docs/interview/01_technical_decisions/NOMNOM_TECHNICAL_DECISIONS.md`

---

## Summary

**tech_comparison_agent** proves I can architect multi-agent systems with measurable evidence.

**Phase 7 job-search agent** (optional) proves patterns transfer and scale.

Together, they show the full journey: Learn → Apply → Measure → Transfer → Build Real Things.
