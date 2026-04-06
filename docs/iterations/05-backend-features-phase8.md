# NomNom — Iteration 05: Backend Features — Dashboard, Cat Mood & Weekly Recaps

**Phase:** Phase 8 (full plan)

**Goal:** Complete the backend by adding dashboard endpoints, cat mood calculation, weekly recap generation, and the Sunday recap scheduler.

**Resume Skills:** LLM integration, async scheduling, data aggregation

---

## What's Built

- LLM harness with structured output
- Food photo analysis with guardrails + caching + logging
- Rate limiting + accuracy tracking
- Embeddings + vector search + RAG recommendations with streaming
- iOS camera + food logging

## What We're Building

**Complete the backend:**
- Dashboard: today's macro progress, cat mood, status line
- Cat mood calculation: rules-based (no AI) — reacts to user's nutrition intake
- Weekly recaps: Sunday automation — AI generates funny recap narratives
- Scheduler: APScheduler runs Sunday recap job for all users

---

## Phase 8.1: Cat Mood Calculation

### 8.1.A: Cat mood rules (no AI)

No AI calls needed — just if/else logic based on daily macros.

```
Mood determination:
- If all macros 80-110% of target → "proud"
- If calories > 120% of target → "judging"
- If calories < 50% of target → "worried"
- If good protein but junk food category → "conflicted"
- If no food logged today → "sleeping"
- Default → "happy"

Status line examples:
- Proud: "3 meals down, and your macros are *perfect*"
- Judging: "2000 calories and it's only noon 😼"
- Worried: "You've only eaten 600 calories... are you okay?"
- Conflicted: "Your protein is good but... pizza?"
- Sleeping: "Zzz... feed me when you eat something"
```

### 8.1.B: Create CatState model

Create `src/models/cat_state.py`:
```python
# SQLAlchemy model:
# - id (PK)
# - user_id (FK, unique)
# - mood (str) — "happy", "proud", "judging", "worried", "conflicted", "sleeping"
# - status_line (text) — narrative status from the cat
# - last_updated (datetime)
```

Update `src/models/__init__.py`:
- Import CatState

### 8.1.C: Create cat_service.py

Create `src/services/cat_service.py`:
```python
# What it does:
# - Calculate cat mood based on daily intake vs targets
# - Generate status line

# Key function:
# - calculate_mood(
#     db: AsyncSession,
#     user_id: int,
#     profile: UserProfile,
#     today_intake: dict  # {calories, protein, carbs, fat}
#   ) -> tuple[str, str]
#     Returns (mood, status_line)
#     Example: ("proud", "All macros perfect today! 🎉")
# - update_cat_state(db: AsyncSession, user_id: int, mood: str, status_line: str) -> CatState
#     Save to database
```

Files to create:
- `src/services/cat_service.py` — mood calculation

### 8.1.D: Create alembic migration

Commands:
```bash
uv run alembic revision --autogenerate -m "add cat_states table"
uv run alembic upgrade head
```

### 8.1.E: Test cat mood logic

Files to create:
- `tests/unit/services/test_cat_service.py` — test mood calculation for all 5 moods

Commands:
- `uv run pytest tests/unit/services/test_cat_service.py -v`

---

## Phase 8.2: Dashboard Endpoint

### 8.2.A: Create dashboard schemas

Update `src/schemas/dashboard.py`:
```python
# Schemas:
# - MacroProgress — current intake, target, percentage
# - DashboardResponse:
#   - date (today's date)
#   - total_meals (count)
#   - total_calories
#   - macro_progress: {calories, protein, carbs, fat}
#   - cat_mood (mood, status_line)
#   - meals (list of today's food logs)
```

Files to create/update:
- `src/schemas/dashboard.py` — dashboard response schemas

### 8.2.B: Create dashboard endpoint

Create `src/api/dashboard.py`:
```python
# Endpoint:
# GET /api/v1/dashboard/today

# Flow:
# 1. Get user's profile (targets)
# 2. Get today's food logs
# 3. Sum calories + macros
# 4. Calculate progress percentages
# 5. Calculate cat mood
# 6. Return all as DashboardResponse
```

Files to create:
- `src/api/dashboard.py` — dashboard endpoint

Update `src/app.py`:
- Register dashboard router

### 8.2.C: Test dashboard endpoint

Files to create:
- `tests/integration/test_dashboard.py` — test GET /today (with food logs, mocked)

Commands:
- `uv run pytest tests/integration/test_dashboard.py -v`

---

## Phase 8.3: Weekly Recap Generation

### 8.3.A: WeeklyRecap model

Create `src/models/weekly_recap.py`:
```python
# SQLAlchemy model:
# - id (PK)
# - user_id (FK)
# - week_start (date) — Monday of that week
# - week_end (date) — Sunday of that week
# - narrative (text) — the funny AI recap story
# - avg_calories (int)
# - best_day (str) — "Monday", "Tuesday", etc.
# - worst_day (str) — day with worst macros
# - most_eaten_category (str) — "fast food", "salad", etc.
# - total_meals_logged (int)
# - actionable_nudge (text) — AI suggestion for next week
# - stats_json (JSON) — extra stats
# - created_at (datetime)
```

Files to create:
- `src/models/weekly_recap.py` — WeeklyRecap model

Update `src/models/__init__.py`:
- Import WeeklyRecap

### 8.3.B: Recap service

Create `src/services/recap_service.py`:
```python
# What it does:
# - Aggregate a week's food logs
# - Calculate stats (avg calories, best/worst days, most eaten category)
# - Call Sonnet to generate funny narrative + actionable nudge
# - Save to database

# Key functions:
# - get_week_stats(db: AsyncSession, user_id: int, week_start: date) -> dict
#     Summarize the week: daily totals, categories, macros
# - generate_recap(
#     db: AsyncSession,
#     user_id: int,
#     week_stats: dict,
#     profile: UserProfile
#   ) -> WeeklyRecap
#     Call Sonnet with weekly_recap.j2 template
#     Parse response (narrative, actionable_nudge)
#     Save to database
#     Return WeeklyRecap
# - get_latest_recap(db: AsyncSession, user_id: int) -> WeeklyRecap | None
#     Get most recent recap for user
```

Files to create:
- `src/services/recap_service.py` — recap generation

### 8.3.C: Create weekly_recap.j2 template

Create `src/llm/prompts/weekly_recap.j2`:
```jinja2
You are a sassy nutrition advisor cat. Create a funny, insightful recap of the user's week.

Week: {{ week_start }} to {{ week_end }}

Stats:
- Total meals logged: {{ total_meals }}
- Average daily calories: {{ avg_calories }}
- Best day: {{ best_day }} ({{ best_day_calories }} cal)
- Worst day: {{ worst_day }} ({{ worst_day_calories }} cal)
- Most eaten category: {{ most_eaten_category }}

User profile:
- Daily calorie target: {{ target_calories }}
- Dietary preferences: {{ preferences }}

Food log summary (by day):
{% for day in daily_logs %}
{{ day.name }}: {{ day.meals_count }} meals, {{ day.calories }} cal, {{ day.protein }}g protein
{% endfor %}

Write a funny 3-4 sentence recap in the style of {{ cat_style }}, 
then give an actionable nudge for next week (1-2 sentences).

Format your response as JSON:
{
  "narrative": "Your recap story here",
  "actionable_nudge": "Here's what to focus on next week"
}
```

---

### 8.3.D: Test recap generation

Files to create:
- `tests/integration/test_recap_service.py` — test generate_recap (mocked Sonnet)

Commands:
- `uv run pytest tests/integration/test_recap_service.py -v`

---

## Phase 8.4: Weekly Recaps API

### 8.4.A: Create schemas

Create `src/schemas/weekly_recap.py`:
```python
# Schemas:
# - WeeklyRecapResponse — what the API returns
```

Files to create/update:
- `src/schemas/weekly_recap.py` — recap schemas

### 8.4.B: Create endpoints

Create `src/api/weekly_recaps.py`:
```python
# Endpoints:
# GET /api/v1/recaps/ — list all past recaps (paginated, newest first)
# GET /api/v1/recaps/{recap_id} — get one recap
# POST /api/v1/recaps/generate — manually trigger recap (debug)
```

Files to create:
- `src/api/weekly_recaps.py` — recaps endpoints

Update `src/app.py`:
- Register weekly_recaps router

### 8.4.C: Test recap endpoints

Files to create:
- `tests/integration/test_weekly_recaps.py` — test GET /, GET /{id}, POST /generate

Commands:
- `uv run pytest tests/integration/test_weekly_recaps.py -v`

---

## Phase 8.5: Scheduler (Sunday Recap Job)

### 8.5.A: Install APScheduler

Update `pyproject.toml`:
- Add dependency: `apscheduler`

### 8.5.B: Create scheduler

Create `src/services/scheduler.py`:
```python
# What it does:
# - Set up APScheduler with CronTrigger
# - Every Sunday at 00:00 UTC:
#   - Loop through all users who logged food that week
#   - Call recap_service.generate_recap() for each
#   - Handle errors gracefully (log, don't crash)

# Key functions:
# - initialize_scheduler()
#     Create scheduler, add job, start it
# - recap_job(db: AsyncSession)
#     Async job that runs every Sunday
#     Loop users, generate recaps
# - should_generate_recap(user_id: int, this_week: bool) -> bool
#     Check if user has new food logs this week
```

Files to create:
- `src/services/scheduler.py` — APScheduler setup + job

### 8.5.C: Wire scheduler into app startup

Update `src/app.py`:
- In `create_app()` startup event: call `scheduler.initialize_scheduler()`

### 8.5.D: Test scheduler

Files to create:
- `tests/unit/services/test_scheduler.py` — test job logic (mocked)

Commands:
- `uv run pytest tests/unit/services/test_scheduler.py -v`

---

## Phase 8.6: Cat API endpoint

### 8.6.A: Create schemas

Create `src/schemas/cat_state.py`:
```python
# Schema:
# - CatStateResponse — mood, status_line
```

Files to create/update:
- `src/schemas/cat_state.py` — cat schemas

### 8.6.B: Create endpoint

Create `src/api/cat.py`:
```python
# Endpoint:
# GET /api/v1/cat/state
# 
# Return current cat mood + status line
```

Files to create:
- `src/api/cat.py` — cat endpoint

Update `src/app.py`:
- Register cat router

### 8.6.C: Test cat endpoint

Files to create:
- `tests/integration/test_cat.py` — test GET /state

Commands:
- `uv run pytest tests/integration/test_cat.py -v`

---

## Phase 8.7: Alembic migration + integration

Create one final migration for all new models:

Commands:
```bash
uv run alembic revision --autogenerate -m "add cat_states and weekly_recaps tables"
uv run alembic upgrade head
```

Verify:
```bash
psql -d nomnom -c "\dt" | grep -E "cat_states|weekly_recaps"
```

---

## Phase 8.8: Integration test

Files to create:
- `tests/integration/test_backend_complete.py` — full flow: food log → cat mood → dashboard → recap

Commands:
- `uv run pytest tests/integration/ -v` — all tests pass

---

## Success Criteria

- [x] Cat mood calculation (5 moods + status line)
- [x] Dashboard endpoint returns today's progress + cat mood
- [x] Weekly recap generation (AI narrative + nudge)
- [x] Scheduler runs every Sunday at midnight
- [x] Weekly recaps API (list, get, manual trigger)
- [x] Cat API endpoint
- [x] All models + migrations created
- [x] All tests pass
- [x] Backend is feature-complete

## Next After Phase 8

Backend is done! Move to iOS (Phases 11-12):
- Dashboard screen with progress bars + cat
- Timeline of food photos
- Weekly recap details screen
- Onboarding flow
- Settings screen

## Backend Complete ✅

You now have a fully functional AI-powered food tracking backend with:
- Multimodal AI (Haiku vision)
- LLM harness (retry, fallback, structured output)
- Prompt engineering (Jinja2 templates, personas)
- Guardrails + cost optimization
- Observability (logging, rate limiting, accuracy tracking)
- Embeddings + vector search (pgvector)
- RAG recommendations with streaming
- Weekly recaps with NLP
- Async scheduler
