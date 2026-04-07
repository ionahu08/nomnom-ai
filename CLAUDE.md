# CLAUDE.md — NomNom

This file is the entry point for AI-assisted development on this project.
It is automatically loaded into context when working with Claude Code.
**Keep this file concise** — reference detailed docs instead of duplicating content here.

## Project Overview

**NomNom** is an AI-powered food tracking app with a roasting cat personality. Users photograph meals, the LLM analyzes nutritional content and delivers witty commentary, and the cat learns user preferences over time via semantic caching and RAG. Built with Python/FastAPI backend and SwiftUI iOS app.

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

**Iteration 07: iOS Settings, Corrections & Recommendations** — In Progress 🚧
See `docs/iterations/07-ios-settings-corrections/PLAN.md` and `PHASES.md`.

## Key Docs

| Path | Purpose |
|---|---|
| `docs/northstar/FEATURES.md` | Complete feature inventory with status |
| `docs/northstar/ARCHITECTURE.md` | System diagram, API design, data model |
| `docs/CHANGELOG.md` | Chronological development history |
| `docs/iterations/` | Per-iteration PLAN.md, PHASES.md, SUMMARY.md, BUGLOG.md |
| `.claude/rules/dev-rules.md` | Standards and conventions |
| `.claude/rules/dev-workflow.md` | Iteration workflow and process |

## Rules

Development rules live in `.claude/rules/`:
- `dev-rules.md` — standards, commit protocol, testing, code quality
- `dev-workflow.md` — iteration workflow, documentation updates
