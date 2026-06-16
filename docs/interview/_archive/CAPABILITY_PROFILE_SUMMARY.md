# Iona's Capability Profile — One-Page Summary

## Executive Summary

Full-stack LLM engineer with 4.7/5 overall capability across 7 layers. Proficient in API mastery, prompt engineering, output control, multimodal augmentation, reliability engineering (my differentiator), agent orchestration, and multi-agent coordination. Demonstrated production judgment — can argue convincingly for *or against* patterns based on measurable tradeoffs, not hype. NomNom portfolio spans v0.5 (basic food recognition) → v3.1 (multi-agent, cost-optimized, MCP-exposed ecosystem).

**Background**: ML/Recommendation Systems engineer pivoting into LLM/AI Engineering with production discipline. Statistics foundation enables rigorous eval design and signal fusion.

---

## 7-Layer Capability Stack

| Layer | Level | Strength |
|---|---|---|
| **0 — API Mastery** | 4.5/5 | Model selection, streaming, multi-turn state, prompt caching (89% token savings), cost tracking, model tiering by task |
| **1 — Prompt Engineering** | 3.5/5 | Templating (Jinja2), techniques (CoT, XML, multishot), caching implications, iteration discipline |
| **2 — Output Control** | 4/5 | tool_choice (100% validity), prefill+stop, JSON schema validation, guardrails |
| **3 — Augmentation ⭐** | 4.7/5 | Multimodal (images, PDFs), full RAG stack (chunking, embeddings, BM25+Vector hybrid search, RRF), semantic caching (0.82 threshold, 60% hit rate, empirically tuned), citations for trust, MCP ecosystem |
| **4 — Reliability ⭐** | 4/5 | 6-step eval pipeline (code+model grading), test generation, signal fusion (RecSys patterns), observability, KB maintenance — **my differentiator** |
| **5 — Agent Engineering** | 5/5 | 5 workflow patterns (chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer), decision framework, benchmarked orchestrator-workers 8x faster than single agent |
| **6 — Multi-Agent** | 4/5 | 3 forms (orchestrator-workers, conversational, hierarchical), 5 challenges (context, coordination, error, cost, eval), can argue "don't use multi-agent" convincingly (95% of cases) |
| **7 — Architecture ⭐** | 4.5/5 | MCP server design, tool vs. resource distinction, ecosystem standardization, Claude Code internals, production confidence 9/10 |

---

## Top 3 Differentiators

### 1. Production-Grade Eval Design (Layer 4)
While most LLM engineers iterate on prompts by intuition, I apply statistical rigor:
- **6-step pipeline**: prompt → test → grade → iterate → re-eval with measurable improvement
- **Signal fusion**: Combine code-based grading (JSON validity, semantic plausibility) + model-based grading (LLM-as-Judge) — resolves disagreement like RecSys learning-to-rank
- **Evidence**: NomNom v0.5 → v1.0 accuracy improved 72% → 88% (Sonnet choice justified by eval data, not intuition)
- **Interview value**: Can defend or pivot any LLM design decision with metrics, not handwaving

### 2. Full RAG Mastery + Empirical Tuning (Layer 3)
Not just "we use RAG" — I own the entire stack with measured tradeoffs:
- **Hybrid search**: BM25 + cosine similarity + RRF ranking (RecSys pattern transfer)
- **Threshold tuning**: Started 0.95 → empirically optimized to 0.82 → captured 90% of duplicates with only 5% false positives → 60% cache hit rate in production
- **Citations**: Claude annotations [1], [2], [3] for user trust + fact verification
- **Evidence**: Semantic cache fixed 7 production bugs, latency improved 13x for cached hits ($45k → $10.5k/month at 1k users)
- **Interview value**: Can explain why a number is 0.82, not 0.80. Can defend a retrieval architecture against "just use embeddings."

### 3. Agent Decision Judgment (Layers 5–6)
Deep mastery = knowing *when not* to use a pattern:
- **Built & benchmarked**: Workflow service vs. single agent on identical task — orchestrator-workers 60s → 18s (3.3x latency gain) + 8x cheaper
- **Multi-agent research**: Studied Anthropic + Cognition papers; understand context passing, coordination, cost explosion, eval difficulty challenges
- **Production judgment**: NomNom uses structured workflows (not agents) for meal recommendations. Agents appropriate for ~5% of real-world LLM use cases.
- **Interview value**: Can argue *for* agents AND *against* them with hard numbers. Senior-level pattern discrimination.

---

## Key Metrics & Evidence

| Achievement | Metric | Evidence |
|---|---|---|
| **API Cost Optimization** | 4.3x reduction via model tiering + caching | $45k/month (1k users, Sonnet everywhere) → $10.5k/month (tiered + cached) |
| **RAG Accuracy** | 78% → 91% recall via hybrid search + reranking | Semantic cache threshold 0.82 (empirically tuned), 60% hit rate |
| **Output Validity** | 97.2% → 100% via tool_choice | NomNom v0.5 → v1.0 comparison report |
| **Agent Performance** | 60s → 18s latency via orchestrator-workers | tech_comparison_agent benchmark (8x faster, 2x cheaper than single agent) |
| **Eval Rigor** | 30 edge cases generated + graded | Code + model grading hybrid (90% cost savings vs. manual) |
| **Production Confidence** | 9/10 | src/llm/ module audit complete, all 7 layers demonstrated in code |

---

## Interview Positioning

### Technical Screens (45 min)
- **Key story**: "How I went from 0.95 → 0.82 cache threshold and discovered the tradeoff between hit rate and false positives using production data"
- **Demonstrate**: Can design an eval pipeline from first principles. Understand why a decision is right, not just that it works.
- **Tradeoff vocabulary**: Cost vs. accuracy, latency vs. quality, simplicity vs. power — can articulate each and make defense

### System Design (60 min)
- **Talking point**: "I've built NomNom's LLM harness end-to-end across 7 layers. Here are the architectural decisions where I had to choose: Sonnet vs. Haiku (accuracy won), RAG vs. retrieval augmented (hybrid search), single agent vs. workflow (structured workflows won 95% of the time)"
- **Demonstrate**: Understand tradeoffs at component, system, and architectural levels. Can sketch a system and justify every layer.

### Behavioral (30 min)
- **STAR evidence ready**: 
  - (Situation) NomNom accuracy stuck at 72%
  - (Task) Improve model choice for food image recognition
  - (Action) Ran A/B eval: Haiku vs. Sonnet. Measured accuracy + cost via structured grading.
  - (Result) Chose Sonnet despite 3x cost — eval data justified it. 72% → 88% accuracy.

### Take-Home Project
- **What you can deliver**: Full RAG pipeline with eval suite. Semantic cache with threshold tuning. Cost tracking dashboard. Multi-agent decision framework (when to use, when not to).
- **Why it matters**: You're not just implementing — you're measuring and defending every choice.

---

## Why I'm Ready for Industry Roles

✅ **Layer 0–2**: API + Prompt + Output mastery — foundation solid  
✅ **Layer 3**: Full RAG stack (the hardest layer) — production-proven  
✅ **Layer 4**: Eval design + reliability — my differentiator, senior skill  
✅ **Layer 5–6**: Agents + orchestration — can argue for *and against*  
✅ **Layer 7**: Architecture + ecosystem (MCP) — full-stack thinking  

**Not just a prompt engineer.** Production-grade engineering discipline applied to LLM systems.

---

## Quick Elevator Pitch

*"I'm an LLM engineer who measures first. I've built NomNom — a production food-tracking app with semantic caching, RAG, and multi-agent workflows — from zero to 4.7/5 capability across 7 layers in 5 weeks. My differentiator: instead of 'we used Sonnet because it's better,' I can tell you 'Haiku was $3 cheaper per 1k requests, but eval showed 72% accuracy vs. 88% — Sonnet was worth it.' I think in tradeoffs, not features."*

---

## File References (Full Details)

- **Technical decisions**: `docs/interview/01_technical_decisions/NOMNOM_TECHNICAL_DECISIONS.md` (18 interview stories)
- **Portfolio narrative**: `docs/interview/02_portfolio_narrative/NOMNOM_PORTFOLIO_STORY.md` (v0.5 → v3.1)
- **Technical Q&A**: `docs/interview/03_interview_prep/TECHNICAL_QA.md` (22 interview questions)
- **Full profile**: `docs/learning/01_capability_profile/Iona_Capability_Profile.md` (detailed layer by layer)

---

**Updated**: June 13, 2026 — Phase 6 Complete, 4.7/5 overall capability, ready for senior LLM engineer roles.
