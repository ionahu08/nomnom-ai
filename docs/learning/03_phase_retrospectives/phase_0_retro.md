# Phase 0 Retrospective

**Dates**: May 08 – May 11, 2026 (~3 days)
**Status**: ✅ Complete

## What I set out to do

Build a cognitive map for LLM Harnessing and set up a learning structure
inside the real NomNom repo, without writing any LLM code yet.

## What I actually did

### Readings (3 required + 1 bonus)
- ✅ Anthropic — Building Effective Agents
- ✅ Karpathy — LLM OS Concept
- ✅ Chip Huyen — Building LLM Applications for Production
- ✅ Bonus: API Foundations notes (companion deep-dive)

Notes in `docs/learning/05_learning_notes/01-04_*.md`.

### Setup work
- ✅ `docs/learning/` structure built (00_roadmap, 01_capability_profile,
  03_phase_retrospectives, 05_learning_notes)
- ✅ `learning_lab/` sandbox folder created
- ✅ `CLAUDE.md` updated with dual-purpose framing
- ✅ Roadmap restructured to integrate with real `src/llm/` (12 files mapped to Phases)
- ✅ Capability profile drafted with Layer 3/4 as differentiator focus

### Insight I didn't expect at the start

(✏️ Fill in: what surprised you?)
Possible answers:
- Realizing my `src/llm/` already has all the pieces — I just don't understand them
- Discovering that the integration plan (file × Phase mapping) is more valuable
  than a separate "v1 spec" document
- Understanding that "0/5 on every file" is a strength, not a weakness — it's
  honest data to work from

## What I learned (concepts, not code)

### Three mental models I can now use:
1. **LLM Harnessing as a capability stack** — 7 layers from API mastery to multi-agent
2. **Workflow vs. Agent** — the decision tree (single call → workflow → single agent → multi-agent)
3. **LLM as unreliable component** — engineer reliability via retries, fallbacks, eval, guardrails

### Concepts I can explain in 30 seconds:
- What LLM Harnessing is
- Why most "agents" should be workflows
- Why eval is the watershed from "personal project" to "engineering project"

## What I cannot yet do (honest list)

- Write a full API call without consulting docs
- Defend any design choice in `src/llm/client.py` (let alone the other 11 files)
- Distinguish prefill+stop from tool_choice in practice
- Run an eval pipeline

(That's the Phase 1+ work.)

## Capability Profile delta

| Layer | Before Phase 0 | After Phase 0 | Evidence |
|---|---|---|---|
| 0: API Mastery | 0/5 | 1/5 | Notes; reviewed client.py at a reading level |
| 1: Prompt Engineering | 0/5 | 1/5 | Notes; agent patterns paper |
| 2–6 | 0/5 | 0/5 | Untouched — Phase 0 is conceptual only |

## What I'll change going into Phase 1

(✏️ Fill in: any process adjustments?)

Examples:
- Plan to time-box code reviews (don't go down rabbit holes)
- Set explicit "hard mode" days (no Claude Code) before each capstone
- Test the daily commit habit (1 commit per learning day, not just per Phase)

## Next: Phase 1, May 17 onwards

Day 1-2: API Quickstart + first calls
Day 3:   Multi-turn + streaming basics
Day 4:   Multimodal
Day 5:   Prompt engineering docs
Day 6:   ⭐ Review client.py (deepest production-code review of the journey)
Day 7:   ⭐ Review prompt_engine.py + prompts/
Day 8-9: Hand-write NomNom v0.5 (sandbox)
Day 10:  Production refactor → docs/iterations/10-llm-foundation-deepdive/