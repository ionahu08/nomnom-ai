# CLAUDE.md — NomNom

This file is the entry point for AI-assisted development on this project.
It is automatically loaded into context when working with Claude Code.
**Keep this file concise** — reference detailed docs instead of duplicating content here.

## Project Overview

**NomNom** is an AI-powered food tracking app with a roasting cat personality. Users photograph meals, the LLM analyzes nutritional content and delivers witty commentary, and the cat learns user preferences over time via semantic caching and RAG. Built with Python/FastAPI backend and SwiftUI iOS app.

## Dual Purpose (As of May 2026)

This codebase serves two parallel tracks:

1. **Production product** — iOS app continuing toward launch (currently Iteration 09 complete)
2. **LLM Harnessing learning journey** — 10-week structured learning by the developer (Iona), May 10–July 26, 2026

Both tracks coexist in this repo. Iteration work continues in `docs/iterations/`. Learning work tracks in `docs/learning/`.

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

**Iteration 09: Food Diary (Calendar View)** — Complete ✅
See `docs/iterations/09-food-diary/SUMMARY.md` for retrospective.

**Next:** Iteration 10 (Recommendations from History) — Planned


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

**Phase 3** (Week 5–6, starting June 9, 2026): Semantic Search + Caching
- Focus: embedding.py, cache.py, seed_knowledge.py, recommendation_service.py
- Goal: Build RAG pipeline + semantic cache for meal recommendations


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

## Rules

Development rules live in `.claude/rules/`:
- `dev-rules.md` — standards, commit protocol, testing, code quality
- `dev-workflow.md` — iteration workflow, documentation updates




## Learning-Aware AI Behavior (Phase 0-6, May–July 2026)

During the 10-week learning journey, AI assistance behavior should adapt by code location:

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
