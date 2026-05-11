# Iona's LLM Harnessing Capability Profile

> **Purpose**: Track my LLM engineering capabilities across 7 layers from Phase 0 to Phase 6+.
> **Use cases**: Interview narratives, LinkedIn/resume positioning, personal progress tracking.
> **Update cadence**: End of each Phase. Add evidence (project, eval report, code) as I earn it.
>
> **Background**: ML/MLE engineer with statistics foundation and Recommendation Systems experience. Pivoting into LLM/AI Engineering.
> **Starting point (Phase 0)**: New to LLM API. Have used ChatGPT but never called the API.
>
> **Start date**: May 10, 2026
> **Target completion**: July 26, 2026 (end of Phase 6, Week 10)

---

## How to Read This

- **Current**: My honest self-assessment right now. Update at the end of each Phase.
- **Target**: Where I want to be by end of plan. Set in Phase 0; rarely change.
- **Evidence**: Specific project, code, or artifact that proves the level. Required for any score ≥ 3.
- **Scoring rubric**:
  - **0/5** — Never touched it
  - **1/5** — Heard of it, can roughly explain
  - **2/5** — Done it once with hand-holding (tutorial-level)
  - **3/5** — Can do it independently for standard cases
  - **4/5** — Can do it well, can teach others, can debug others' work
  - **5/5** — Deep mastery — can defend design decisions, knows tradeoffs, can innovate

---

## Layer 0: API Mastery

**What's in this layer**: API messages structure, model selection (Opus/Sonnet/Haiku), parameters (temperature, max_tokens, stop_sequences), `stop_reason` field, streaming events, multi-turn conversation management, prompt caching, cost tracking, model tiering decisions.

- **Current**: 0/5 (never made an API call)
- **Target**: 4/5
- **Why this target**: Foundation skill — needs to be solid but doesn't need to be a differentiator. 4/5 is "I can write any API call from memory and debug others' API code."
- **Phase progression**:
  - Phase 1 → 3/5 (Quickstart + multi-turn + streaming working)
  - Phase 4 → 4/5 (prompt caching + model tiering verified with cost data)
- **Evidence**: _(empty — fill as Phases complete)_

---

## Layer 1: Prompt Engineering

**What's in this layer**: Clear & direct prompts, multishot examples, Chain of Thought, XML tags, system prompts/roles, prefill response, prompt chaining.

- **Current**: 0/5
- **Target**: 4/5
- **Why this target**: Universal foundation. Every project uses it. 4/5 = "I can stack techniques deliberately and explain why each one matters." Not 5/5 because pure prompt engineering is increasingly commoditized — it's no longer enough to be a differentiator on its own.
- **Phase progression**:
  - Phase 1 → 3/5 (NomNom v0.5 uses at least 4 techniques)
  - Phase 2 → 4/5 (combined with eval — I can measure prompt impact, not just write prompts)
- **Evidence**: _(empty)_

---

## Layer 2: Output Control

**What's in this layer**: Stop sequences, prefill + stop combo for structured output, `tool_choice` forced structured output.

- **Current**: 0/5
- **Target**: 4/5
- **Why this target**: Critical "make LLM behave like a function" skill. 4/5 = "I know when to use prefill vs tool_choice and can defend the choice."
- **Phase progression**:
  - Phase 2 → 4/5 (NomNom v1.0 outputs 100% valid JSON via tool_choice)
- **Evidence**: _(empty)_

---

## Layer 3: Augmentation ⭐ (NomNom's main battlefield)

**What's in this layer**: Tool use (basics + multi-tool + error handling), image multimodal, PDF support, citations, RAG full stack (chunking, embeddings, vector search, BM25, hybrid search, RRF, reranking, contextual retrieval), built-in tools (web search, text editor, code execution), MCP (tools + resources + prompts), batch tool.

- **Current**: 0/5
- **Target**: **5/5** ⭐
- **Why this target**: This is NomNom's main battlefield — multimodal food recognition, nutrition label PDF parsing, RAG over a nutrition knowledge base, citations for trust. By Phase 6, NomNom touches every concept in this layer. **Bonus**: my RecSys background may transfer well to the RAG sub-domain (hybrid search ≡ multi-channel recall, reranking ≡ learning-to-rank) — I'll know if this transfer is real when I get to Phase 3.
- **Phase progression**:
  - Phase 1 → 2/5 (multimodal image recognition)
  - Phase 2 → 3/5 (tool use basics + error handling)
  - Phase 3 → 5/5 (full RAG stack + PDF + citations — saturated)
  - Phase 6 → 5/5 maintained (MCP layer added)
- **Evidence**: _(empty)_

---

## Layer 4: Reliability Engineering ⭐ (My differentiator)

**What's in this layer**: 6-step eval workflow, test dataset generation, code-based grading, model-based grading (LLM-as-judge), combined grading, multi-agent eval.

- **Current**: 1/5 (statistics/ML background gives a head start on eval thinking)
- **Target**: **5/5** ⭐
- **Why this target**: **This is my chosen differentiator layer.** Most LLM engineers write prompts on intuition; few have the statistical rigor to build a real eval pipeline. My statistics/ML background means I naturally think in terms of metrics, grading rubrics, and signal fusion. By Phase 2 I should already be ahead of the average LLM-engineer candidate here; by Phase 5 I should be a clear standout.
- **Phase progression**:
  - Phase 2 → 4/5 (complete eval pipeline + v0.5 vs v1.0 comparison report)
  - Phase 5 → 5/5 (multi-agent eval design + workflow vs multi-agent A/B experiment)
- **Evidence**: _(empty — but expect the strongest evidence portfolio here)_

---

## Layer 5: Agent Engineering

**What's in this layer**: Hand-coded agent loop, 5 workflow patterns (chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer), single agent implementation, workflow vs agent decision framework, extended thinking, Claude Code internals, Claude Agent SDK.

- **Current**: 0/5
- **Target**: 4/5
- **Why this target**: Strong but not differentiating. 4/5 = "I can hand-write an agent loop, know when to use which pattern, and can defend the workflow-vs-agent decision in an interview." Not 5/5 because I don't intend to build novel agent architectures — I want to be a strong practitioner, not a researcher.
- **Phase progression**:
  - Phase 3 → 3/5 (hand-coded agent loop in NomNom)
  - Phase 5 → 4/5 (5 patterns implemented + workflow vs agent decision framework written)
- **Evidence**: _(empty)_

---

## Layer 6: Multi-Agent Coordination

**What's in this layer**: Three multi-agent forms (orchestrator-workers, conversational, hierarchical), five engineering challenges (context passing, coordination, error propagation, cost explosion, eval difficulty), orchestrator-workers hands-on implementation, multi-agent decision framework, Anthropic's stance + opposing viewpoints (Cognition).

- **Current**: 0/5
- **Target**: 3/5
- **Why this target**: **Intentionally capped at 3/5.** I want to know it well enough to interview confidently — especially the "when NOT to use multi-agent" answer, which is the interview kill question. But NomNom doesn't need multi-agent, and I won't fake-build a multi-agent system just to pad this score. The `tech_comparison_agent` side project in Phase 5 is exactly enough.
- **Phase progression**:
  - Phase 5 → 3/5 (tech_comparison_agent + decision framework + can articulate Anthropic vs Cognition debate)
- **Evidence**: _(empty)_

---

## My Differentiator

_(To be drafted with Claude in Phase 0 — this is the most important section of the entire document.)_

**Draft placeholder** (replace after we work through the differentiator exercise):

> I'm pivoting from ML/MLE into LLM/AI Engineering. My differentiator is not "another prompt engineer" — it's **production-grade engineering discipline applied to LLM systems**.
>
> The two layers where I aim to stand out:
> 1. **Layer 4 (Reliability Engineering)** — my statistics/ML background makes eval design, grader rubrics, and signal fusion feel natural. While many LLM engineers iterate on prompts by gut, I build measurable systems.
> 2. **Layer 3 (Augmentation)** — NomNom is my proving ground for the full RAG + multimodal + citations stack.
>
> NomNom is the vehicle for learning these technologies end-to-end. Where my prior experience (e.g., RecSys patterns transferring to RAG retrieval design) genuinely helps, it'll show up in specific technical decisions — not in my opening line.

---

## Capability Snapshot Table

A quick at-a-glance view. Update at end of each Phase.

| Layer | Current | Target | Status |
|---|---|---|---|
| 0 — API Mastery | 0/5 | 4/5 | Not started |
| 1 — Prompt Engineering | 0/5 | 4/5 | Not started |
| 2 — Output Control | 0/5 | 4/5 | Not started |
| 3 — Augmentation ⭐ | 0/5 | 5/5 | Not started |
| 4 — Reliability ⭐ | 1/5 | 5/5 | Slight head start (statistics/ML background) |
| 5 — Agent Engineering | 0/5 | 4/5 | Not started |
| 6 — Multi-Agent | 0/5 | 3/5 | Not started |

---

## Phase Completion Schedule

| Phase | Week | Target End Date |
|---|---|---|
| Phase 0 (Cognitive map + product definition) | Week 0 | May 17, 2026 |
| Phase 1 (NomNom MVP) | Week 1–2 | May 31, 2026 |
| Phase 2 (Output stabilization + eval) | Week 3–4 | June 14, 2026 |
| Phase 3 (RAG + PDF + citations) | Week 5–6 | June 28, 2026 |
| Phase 4 (Performance + cost) | Week 7 | July 5, 2026 |
| Phase 5 (Workflow + agent + multi-agent) | Week 8–9 | July 19, 2026 |
| Phase 6 (MCP standardization) | Week 10 | July 26, 2026 |
| Phase 7 (Optional: extension projects) | Week 11–12 | August 9, 2026 |

---

## Update Log

- **May 10, 2026**: Initial profile drafted. Set targets and identified Layer 3 + Layer 4 as differentiator focus.
- _(Add an entry at the end of each Phase)_
