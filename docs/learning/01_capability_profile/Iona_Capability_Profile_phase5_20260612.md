# Iona's Capability Profile — Phase 5 Snapshot (June 12, 2026)

**Phase 5 Focus:** Workflow & Agent Orchestration (All 5 patterns, single agent, multi-agent)  
**Duration:** 3 days (June 10-12, 2026) — learning compressed with production work  
**Overall Progression:** 4.2/5 → 4.6/5

---

## Major Breakthroughs This Phase

### Layer 5: Agent Engineering — 2/5 → **5/5** ✅

**Upgraded from "ready for Phase 5" to "mastery"** after:
- Learned all 5 workflow patterns (Chaining, Routing, Parallelization, Orchestrator-Workers, Evaluator-Optimizer)
- Designed complete 5-step workflow for NomNom (Days 1-2)
- Implemented both WorkflowService and AgentService (Days 3-9)
- Built decision framework (Day 5) — the interview-level judgment skill
- Integrated into production backend (Iteration 14)
- **Critical insight:** The ability to say "don't use agents here" is as valuable as knowing how to build them

**Evidence:**
- Days 1-5 learning artifacts (5 markdown files, fully fleshed)
- `workflow_service.py` (237 lines, runnable, mock-complete)
- `agent_service.py` (300 lines, runnable, agent loop full)
- `05_workflow_vs_agent_decision.md` (decision tree, interview-ready)
- Production integration: `src/llm/workflow/` + `src/api/recommendations.py`

### Layer 6: Multi-Agent Coordination — 0/5 → **4/5** ✅

**Exceeded target (3/5) after:**
- Read Anthropic AND Cognition research (both perspectives)
- Built orchestrator-workers (`tech_comparison_agent`)
- **Benchmark discovery:** Orchestrator-workers 8x faster + 2x cheaper than single agent for decomposable tasks
  - Orchestrator-workers: 10s, $0.023
  - Single agent: 80s, $0.045
  - Root cause: Message history accumulation in agent loop
- Articulated 5 engineering challenges (context passing is #1)
- Made confident "don't use multi-agent for NomNom" decision

**Evidence:**
- Days 6-8 learning artifacts (concepts, challenges, research findings)
- `tech_comparison_agent/` (orchestrator-workers implementation)
- `08_multi_agent_eval.md` (benchmark report with real numbers)
- Can defend both for AND against multi-agent in an interview

---

## Current Capability Table

| Layer | Start (Phase 4) | End (Phase 5) | Target | Status |
|---|---|---|---|---|
| **0 — API Mastery** | 4.5/5 | 4.5/5 | 4/5 | ✅ Met (stable) |
| **1 — Prompt Engineering** | 3.5/5 | 3.5/5 | 4/5 | ✅ On track |
| **2 — Output Control** | 4/5 | 4/5 | 4/5 | ✅ Met |
| **3 — Augmentation ⭐** | 4.5/5 | 4.5/5 | 5/5 | ✅ Strong |
| **4 — Reliability ⭐** | 4/5 | 4/5 | 5/5 | ✅ Differentiator |
| **5 — Agent Engineering** | 2/5 | **5/5** ✅ | 4/5 | ✅✅ Exceeded |
| **6 — Multi-Agent** | 0/5 | **4/5** ✅ | 3/5 | ✅✅ Exceeded |
| **Overall** | 4.2/5 | **4.6/5** | — | ✅ Major jump |

---

## Key Discoveries

### Discovery 1: Orchestrator-Workers Beats Single Agent (8x difference)

Tested both patterns on same task (PyTorch vs. TensorFlow comparison):

```
Orchestrator-Workers (Day 7):
  Latency: 10s
  Cost: $0.023
  Structure: Predictable (3 workers, all complete)
  
Single Agent (Day 8):
  Latency: 80s
  Cost: $0.045
  Structure: Variable (hit token limit at ~8 searches)
```

**Root cause:** Message history explosion in agent loop.
- Loop 1: ~200 tokens
- Loop 2: ~400 tokens (previous + new searches)
- Loop 3: ~600+ tokens (all accumulated) → runs out of context

**Key insight:** Orchestrator isolation prevents this. Each worker only sees its sub-task.

### Discovery 2: Workflows are Default (95% of cases)

Not just opinion — confirmed by both Anthropic and Cognition research:
- Fixed steps = predictable cost + latency
- Easy to debug (inspect each step independently)
- Easier to test (known outputs)
- Route between workflow types for different requests

### Discovery 3: The 5% Multi-Agent Exception

Multi-agent is worth considering when ALL of these are true:
1. Task doesn't decompose into predetermined steps
2. Single agent has been tried and failed
3. Subtasks are independent (no coordination needed)
4. Quality can be evaluated clearly
5. Cost improvement justifies complexity
6. Team has 2+ people (solo + multi-agent = nightmare)

NomNom fails on criterion 1 (meal recommendations have predetermined steps) and criterion 3 (no independent decomposition for single recommendations).

---

## Production Impact

**Iteration 14 (parallel to learning):**
- Implemented meal recommendation workflow in production
- Added intent router (routing.py)
- Added use_workflow parameter to API
- iOS tested full device (ngrok tunnel, network debugging)
- Latency: 60s → 20-25s (67% reduction)

**Code written:**
- 1000+ lines of learning artifacts
- 200+ lines of production integration
- Both runnable (learning code has main() functions for testing)

---

## What's Left for Phases 6-7

**Phase 6 (starting June 13):** MCP Servers — Expose NomNom patterns to Claude itself

**Phase 7 (optional):** Extension projects based on time

---

## Interview Talking Points (Phase 5)

**Q: Describe the difference between workflows and agents.**

A: Workflows have predetermined steps. Extract → Search → Generate → Validate → Rank. The order doesn't change. Agents are flexible: Claude decides what to do based on intermediate results.

When to use each: Workflows for 95% of tasks (predictable cost/latency). Agents only when you don't know the steps upfront AND Claude genuinely needs autonomy to respond to results.

**Q: You studied orchestrator-workers vs. single agent. What did you find?**

A: Orchestrator-workers was 8x faster and 2x cheaper on a research comparison task. The key insight: as a single agent loops and accumulates search results, its message history explodes exponentially. Each subsequent API call processes more context, slowing down.

Orchestrator-workers avoids this by isolating worker contexts. Each worker only sees its subtask, not others' results. This enables parallelization (10 workers in ~5s, not 500s).

**Q: When would you use multi-agent?**

A: Rarely. I'd start with a single agent with more tools. Only if that fails, I'd consider orchestrator-workers — BUT only if the task naturally decomposes into independent subtasks with no coordination needed. Most tasks don't.

For NomNom specifically: Structured meal recommendations don't decompose (always extract → search → generate → validate → rank), so multi-agent adds complexity without benefit. Workflows are the right choice.

---

## Files Modified/Created

**Learning artifacts:**
- `learning_lab/phase_5/01_5_patterns.md` ✅
- `learning_lab/phase_5/02_workflow_design.md` ✅
- `learning_lab/phase_5/03_workflow_sandbox.py` ✅
- `learning_lab/phase_5/04_agent_sandbox.py` ✅
- `learning_lab/phase_5/04_single_agent.md` ✅
- `learning_lab/phase_5/05_workflow_vs_agent_decision.md` ✅
- `learning_lab/phase_5/06_multi_agent_concepts.md` ✅
- `learning_lab/phase_5/08_multi_agent_eval.md` ✅
- `learning_lab/phase_5/09_service_comparison.md` ✅
- `learning_lab/phase_5/10_nomnom_integration.md` ✅ (NEW)
- `learning_lab/phase_5/workflow_service.py` ✅ (runnable)
- `learning_lab/phase_5/agent_service.py` ✅ (runnable)
- `learning_lab/phase_5/tech_comparison_agent/` ✅

**Documentation:**
- `docs/learning/03_phase_retrospectives/phase_5_retro.md` ✅ (NEW)
- `docs/learning/01_capability_profile/Iona_Capability_Profile.md` ✅ (UPDATED)
- `docs/learning/01_capability_profile/Iona_Capability_Profile_phase5_20260612.md` ✅ (NEW, this file)

**Production code (Iteration 14):**
- `src/llm/workflow/routing.py` ✅
- `src/llm/workflow/meal_recommendation_workflow.py` ✅
- `src/services/workflow_recommendation_service.py` ✅
- `src/api/recommendations.py` ✅ (modified)
- `docs/iterations/14-meal-recommendation-workflow/` ✅

---

## Readiness Assessment for Phase 6

**Layer 5 (Agent Engineering):** 5/5 — Ready to apply patterns in new contexts  
**Layer 6 (Multi-Agent):** 4/5 — Ready to explain tradeoffs, evaluate when justified  
**Overall:** 4.6/5 — Equipped for MCP server design (Phase 6)

**Skill transfer for Phase 6:** Building MCP servers is about exposing LLM-accessible tools/resources. The orchestration and routing patterns from Phase 5 apply directly: how to route requests, when to parallelize, how to handle tool responses.

---

**Date:** June 12, 2026  
**Phase Status:** ✅ Complete  
**Next:** Phase 6 — MCP Servers (June 13+)
