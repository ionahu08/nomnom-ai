# CLAUDE.md — NomNom

This file is the entry point for AI-assisted development on this project.
It is automatically loaded into context when working with Claude Code.
**Keep this file concise** — reference detailed docs instead of duplicating content here.

## Project Overview

**NomNom** is an AI-powered food tracking app with a roasting cat personality. Users photograph meals, the LLM analyzes nutritional content and delivers witty commentary, and the cat learns user preferences over time via semantic caching and RAG. Built with Python/FastAPI backend and SwiftUI iOS app.

## Dual Purpose (As of June 2026)

This codebase serves two parallel tracks:

1. **Production product** — iOS app continuing toward launch (currently Iteration 16 MCP complete)
2. **LLM Harnessing learning journey** — ✅ COMPLETE (May 12–June 13, 2026). Iona is now a full-stack LLM engineer with 4.7/5 capability across 7 layers.

Iteration work continues in `docs/iterations/`. Learning journey complete; retrospectives and capability profiles track progression in `docs/learning/`.

## System Context

```
iOS App (SwiftUI) ──▶ NomNom-Backend (FastAPI) ──▶ PostgreSQL + pgvector
                            │
                    ┌───────┼───────┐
                    ▼       ▼       ▼
                  LLM    Cache    Embeddings
               (Claude) (Semantic) (MiniLM)
```

## Current Iteration

**Iteration 19: AI Nutrition Insights & Food Recommendations** — 🚀 STARTING (June 16, 2026)
See `docs/iterations/19-nutrition-insights-agent/` for plan and progress.

**What's Being Built:**
- Backend: New `/nutrition/insights` endpoint that analyzes past food intake (1d/1w/1m)
- LLM Agent: Claude-powered analysis of nutrition gaps + personalized food recommendations
- iOS: Replace static sections with interactive AI insights card
- UX: Remove consistency bar, daily targets, top foods; add conversational feedback
- Features: Personalized recommendations based on health profile, allergies, medical conditions, past eating habits

---

## Completed Iterations

**Iteration 18: Weekly Nutrition Summary** — ✅ COMPLETE (June 15, 2026)
See `docs/iterations/18-weekly-nutrition-summary/` for plan, phases, and summary.

**What Was Built:**
- Backend: Analytics API with multi-period support (week/month/6-month)
- iOS: Insight tab with period selector, line charts for calories & macros
- UI: Period-aware x-axis labels (days/dates/months), Y-axis with values
- Features: Date navigation, consistency tracking, top foods ranking

**Key Stats:**
- 9 critical bugs found and fixed
- 14 commits across backend/iOS/documentation
- Bugs: period mapping, timezone handling, schema mismatches (all resolved)
- Tests: 25+ test cases verified, all passing

**See BUGLOG.md for:**
- Complete list of 9 bugs with root causes
- Prevention strategies for each bug type
- Detailed explanations of timezone, schema, and date calculation issues

---

**Iteration 17: Personalized Nutrition Profile** — ✅ COMPLETE (June 13–14, 2026)
See `docs/iterations/17-personalized-nutrition/` for details.

**Completed:**
- Backend: Health profile API, nutrition calculations (Mifflin-St Jeor, TDEE, macro splits), all endpoints tested (6/6 passing)
- iOS: Complete Settings screen with health data input, Food Diary integration with daily targets
- Key fixes: JSON field type corrections, test fixture isolation, removed auto-profile creation during registration

**Completed Iterations Summary (11–16):** ✅ All documented with PLAN/PHASES/BUGLOG/SUMMARY
- Iteration 11: Eval pipeline (test → grade → iterate) — SUMMARY.md added June 14
- Iteration 12: Semantic cache production (pgvector, 0.82 threshold)
- Iteration 13: Cost & latency optimization (Sonnet routing, cache pricing)
- Iteration 14: Meal recommendation workflow (orchestrator-workers, 8x latency gain) — PHASES/BUGLOG/SUMMARY added June 14
- Iteration 15: Fridge/leftovers agent (PLAN only, not implemented)
- Iteration 16: MCP server + Claude Code integration (3 tools, ecosystem standardization) — PHASES/BUGLOG added June 14

**Documentation Status:** All iterations 11–16 now have complete standard documentation (PLAN.md → PHASES.md → BUGLOG.md → SUMMARY.md), enabling seamless handoff between sessions.

**Paused:** Phase 7 Job-Search Multi-Agent (Option A) — Can resume after Iteration 17.


## Current Learning Phase

**Phase 1** ✅ COMPLETE (May 17–June 4, 2026)
- 15 Jupyter notebooks: API fundamentals, prompt engineering, output control, augmentation, agents
- 3 project directories: MCP server, Claude Code labs, hooks
- 2 deep code reviews: client.py (reliability patterns), prompt_engine.py (templating)
- Capstone: NomNom v0.5 sandbox script with experimentation
- **Key insight:** Prompts are product assets (10x change frequency vs. code)

**Phase 1 retrospectives:** 
- `docs/learning/03_phase_retrospectives/phase_0_retro.md`
- `docs/learning/03_phase_retrospectives/phase_1_retro.md`

**Phase 2** ✅ COMPLETE (June 5–8, 2026)
- Focus: parser.py, guardrails.py, evaluator.py, tools.py
- Goal: Output control + structured output validation + guardrails
- **Outcome:** tool_choice integrated, eval pipeline built (30 edge cases), error messages improved
- **Key metrics:** 100% tool_choice success rate, 98.3/100 avg code score, 93.3% semantic validity
- **Iteration docs:** `docs/iterations/11-eval-pipeline/`
- **Retrospective:** `docs/learning/03_phase_retrospectives/phase_2_retro.md`

**Phase 3** ✅ COMPLETE (June 9–8, 2026)
- Focus: embedding.py, cache.py, seed_knowledge.py, recommendation_service.py
- Goal: Build RAG pipeline + semantic cache for meal recommendations
- **Outcome:** Days 1-9 learning (naive RAG → hybrid search → citations), Day 10 production integration
- **Key metrics:** Threshold tuned 0.95 → 0.82, 7 bugs fixed, 5 files updated, 4 commits
- **Iteration docs:** `docs/iterations/12-semantic-cache-production/`
- **Retrospective:** `docs/learning/03_phase_retrospectives/phase_3_retro.md`

**Phase 4** ✅ COMPLETE (June 10, 2026): Cost & Latency Optimization
- Focus: router.py, rate_limiter.py, logger.py
- **Outcome:** 4 critical bugs fixed, cost tracking accurate, all tests passing
- **Key metrics:** ANALYZE_FOOD→Sonnet (quality), cache pricing fixed (accuracy), 29/29 tests ✓
- **Daily cost:** $1.45 → $2.17 (Sonnet for better food vision), offset by Phase 5 caching
- **Iteration docs:** `docs/iterations/13-cost-and-latency/`
- **Retrospective:** `docs/learning/03_phase_retrospectives/phase_4_retro.md`

**Phase 5** ✅ COMPLETE (June 10-12, 2026): Workflow & Agent Orchestration
- Focus: Learn 5 orchestration patterns, decide when to use each, production integration
- **Outcome:** 5 patterns mastered (chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer), 2 services built (workflow + agent), orchestrator-workers proven 8x faster than single agent, production integrated into meal recommendation workflow
- **Key metrics:** Layer 4 (Agents & Workflows) → 5/5, latency 60s → 20-25s (67% reduction), all tests passing
- **Iteration docs:** `docs/iterations/14-meal-recommendation-workflow/`
- **Retrospective:** `docs/learning/03_phase_retrospectives/phase_5_retro.md`

**Phase 6** ✅ COMPLETE (June 13, 2026): MCP Servers & Claude-as-a-Tool
- Focus: Expose NomNom patterns to Claude via MCP server design
- **Outcome:** Built functional MCP server with 3 tools (recommend_meal, analyze_food_image, lookup_nutrition), integrated with Claude Code ecosystem, studied Claude internals as industrial reference
- **Key metrics:** Layer 7 (Architecture & Standardization) → 4.5/5 (NEW), Layer 3 (Augmentation) → 4.7/5, overall 4.6→4.7/5, production confidence 9/10
- **Iteration docs:** `docs/iterations/16-mcp-server/`
- **Retrospective:** `docs/learning/03_phase_retrospectives/phase_6_retro.md`
- **Capability snapshot:** `docs/learning/01_capability_profile/Iona_Capability_Profile_phase6_20260613.md`


## Key Docs

| Path | Purpose |
|---|---|
| `docs/northstar/FEATURES.md` | Complete feature inventory with status |
| `docs/northstar/ARCHITECTURE.md` | System diagram, API design, data model |
| `docs/CHANGELOG.md` | Chronological development history |
| `docs/iterations/` | Per-iteration PLAN.md, PHASES.md, SUMMARY.md, BUGLOG.md |
| `docs/learning/00_roadmap/roadmap_main_nomnom.md` | 10-week LLM Harnessing learning plan |
| `docs/learning/01_capability_profile/Iona_Capability_Profile.md` | Iona's skill level tracking across 7 layers |
| `docs/learning/05_learning_notes/` | Deep concept notes (API, agents, LLM OS, production) |
| `learning_lab/` | Sandbox for Phase 1-6 hands-on concept practice (separate from production code) |
| `.claude/rules/dev-rules.md` | Standards and conventions |
| `.claude/rules/dev-workflow.md` | Iteration workflow and process |
| 🗂️ `.claude/rules/repo-navigation-quick-ref.md` | Repository structure overview (auto-loaded every session) |
| 🗂️ `docs/REPO_STRUCTURE.md` | Detailed folder references, dependencies, and navigation strategies |

## Rules

Development standards and references live in `.claude/rules/`:
- `dev-rules.md` — standards, commit protocol, testing, code quality
- `dev-workflow.md` — iteration workflow, documentation updates
- `phase-handoff-checklist.md` — mandatory steps for Phase 1-6 learning completions (retrospectives, capability profiles, roadmap, CLAUDE.md updates)
- `repo-navigation-quick-ref.md` — repository structure overview (auto-loaded every session)
- `ios_app_icon_troubleshooting.md` — iOS app icon debugging checklist




## Learning Journey Context (Completed May 12–June 13, 2026)

**Note:** The 10-week LLM Harnessing learning journey is now complete. Iona has achieved 4.7/5 overall capability across 7 layers and is ready for senior LLM engineer roles. This section documents how AI assistance was tailored during the active learning phases (0–6).

During the learning journey, AI assistance behavior was adapted by code location:

### `NomNom-Backend/src/llm/` and `learning_lab/`

Iona is intentionally learning the mechanics of LLM engineering here.

- **Explain, don't just write.** When asked to write or refactor code in these paths, walk through the design choices line by line.
- **Defer authorship to Iona when concepts are being learned.** Offer review and feedback over autocompletion.
- **Surface decisions, not just code.** When suggesting changes, name the design choices (e.g., "we could use prefill+stop here, or tool_choice — here's the tradeoff").

### Phase-aware focus areas

Different Phases focus on different files (see roadmap for details):

- **Phase 1** (Week 1–2): `client.py`, `prompt_engine.py`, `prompts/`
- **Phase 2** (Week 3–4): `parser.py`, `guardrails.py`, `evaluator.py`, `tools.py`
- **Phase 3** (Week 5–6): `embedding.py`, `cache.py`, `seed_knowledge.py`
- **Phase 4** (Week 7): `router.py`, `rate_limiter.py`, `logger.py`
- **Phase 5** (Week 8–9): new `workflow/` or `agent/` patterns
- **Phase 6** (Week 10): MCP server exposure

### Other code paths (iOS, DB migrations, FastAPI routes, tests)

Normal AI assistance applies — Iona's learning focus is LLM, not full-stack rewrite.
