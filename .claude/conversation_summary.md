# NomNom — Conversation Summary

Date: 2026-04-05

---

## 1. Explored Teacher's Repo (NexoraCombo)

Walked through the teacher's Nexora project to understand how it's built:

- **Nexora-Backend/** — Python 3.12 + FastAPI + SQLAlchemy 2.0 + PostgreSQL
  - Layered architecture: api/ -> services/ -> models/ -> database
  - LLM agent with ReAct loop and 12 tools
  - 3 agent personas: chat, execution, proactive advisor
  - JWT auth, Alembic migrations, async throughout

- **Nexora/** — Swift + SwiftUI (iOS 17+)
  - MVVM pattern: each screen has a View + ViewModel
  - APIClient talks to backend over REST
  - KeychainService for secure storage

Key takeaway: frontend (what users see) + backend (the brain) + API (shared language connecting them).

---

## 2. Designed the NomNom App

Originally named "MealCat", renamed to "NomNom".

A food tracking app with an AI cat that roasts your food choices.

**5 Screens:**

1. **Camera** — snap food photo, AI returns macros + funny roast, cat reacts
2. **Dashboard** — 4 progress bars (calories, protein, carbs, fat), cat mood, "What should I eat?" button
3. **Timeline** — scrollable photo grid of past meals by date, tap for details
4. **Weekly Recap** — AI-generated funny summary every Sunday with stats and nudge
5. **Settings** — pick cat style, set dietary preferences, profile info

---

## 3. Tech Stack Decisions

- **Backend:** Python 3.12 + FastAPI + SQLAlchemy 2.0 + PostgreSQL + pgvector
- **Frontend:** Swift + SwiftUI (iOS 17+) + MVVM
- **AI Models:**
  - Claude Haiku — food photo analysis + roasts (cheap, fast, runs often)
  - Claude Sonnet — weekly recaps + meal recommendations (better writing, runs rarely)
- **Anthropic Python SDK** used directly (not litellm)
- Follow teacher's Nexora patterns for auth, API structure, iOS networking

---

## 4. Added AI/MLE Resume Skills

The user is targeting MLE / AI Engineer roles, so the project was expanded to cover 12 resume-worthy skills:

1. Multimodal AI (vision)
2. RAG (retrieval-augmented generation)
3. Embeddings & Vector Search (pgvector)
4. Prompt Engineering (Jinja2 templates, personas, few-shot)
5. Structured Output (Anthropic tool_use)
6. Streaming (SSE)
7. LLM Harness Engineering (retries, fallbacks, timeouts, token budgets, model routing)
8. Output Parsing & Validation (Pydantic + retry on bad output)
9. Model Evaluation (accuracy from user corrections)
10. Cost Optimization (model tiering, semantic caching)
11. AI Observability (token/latency/cost logging)
12. Guardrails (output validation, rate limiting, fallback handling)

---

## 5. LLM Harness (src/llm/)

A dedicated folder for all AI orchestration — the key differentiator for the resume:

- **client.py** — Anthropic SDK wrapper with retry (2x exponential backoff), timeout (10s Haiku / 30s Sonnet), fallback to other model
- **router.py** — routes tasks to the right model (Haiku for photos, Sonnet for writing)
- **prompts/** — Jinja2 templates for each AI task + cat personas
- **tools.py** — Anthropic tool_use schemas for structured output
- **parser.py** — Pydantic validation of AI output + retry on failure
- **cache.py** — semantic cache using pgvector embeddings (skip API call if similar food seen before)
- **guardrails.py** — sanity checks (calories 0-5000, food name not empty, etc.)
- **rate_limiter.py** — per-user call limits (30 analyze/hr, 10 recommend/hr)
- **logger.py** — logs every AI call to ai_call_logs table
- **evaluator.py** — tracks accuracy from user corrections

---

## 6. Database Tables

7 tables total:
- users, user_profiles — account + body stats + preferences
- food_logs — meals with photo, macros, roast, embedding vector
- cat_states — cat mood + status line
- weekly_recaps — Sunday summaries
- nutrition_kb — nutrition knowledge base for RAG
- ai_call_logs — every AI call logged (observability)

---

## 7. Build Order (12 Phases)

| Phase | What |
|-------|------|
| 1 | Project setup, database, auth, user profile |
| 2 | Food log CRUD + photo storage |
| 3 | LLM harness: client, router, prompts, tools, parser |
| 4 | AI photo analysis (Haiku) via harness |
| 5 | Guardrails, caching, logging, rate limiting, evaluation |
| 6 | Embeddings + vector search + nutrition KB |
| 7 | RAG-powered recommendations (Sonnet) + streaming |
| 8 | Dashboard + cat mood + weekly recaps + scheduler |
| 9 | iOS app - foundation + auth |
| 10 | iOS - camera + food logging (with streaming) |
| 11 | iOS - dashboard |
| 12 | iOS - timeline, recaps, onboarding, settings |

---

## Key Files

- Full plan: `/Users/ionahu/sources/NomNom/docs/PLAN.md`
- Learning notes: `/Users/ionahu/sources/NomNom/docs/NOTES.md`
- Claude Code notes: `/Users/ionahu/sources/NomNom/docs/ClaudeCodeNotes.md`
- Teacher's repo (reference): `/Users/ionahu/sources/NexoraCombo/`

---

## Next Step

Ready to start building Phase 1 (project setup, database, auth, user profile).
