# Phases — Iteration 05: Backend Features

## Phase 8: Dashboard, Cat Mood, Weekly Recaps

### 8.1: Cat Mood Calculation (Rules-Based)

- [ ] Create `src/services/cat_service.py`:
  - `calculate_mood(profile, today_intake)` → (mood, status_line)
  - Rules: perfect macros → "proud", over 120% cal → "judging", under 50% → "worried", etc.
  - 5 moods: happy, proud, judging, worried, conflicted, sleeping
  - Generate funny status line per mood
- [ ] Create `src/models/cat_state.py` — id, user_id, mood, status_line, last_updated
- [ ] Alembic migration
- [ ] Create `tests/unit/services/test_cat_service.py`

### 8.2: Dashboard Endpoint

- [ ] Create `src/schemas/dashboard.py` — MacroProgress, DashboardResponse
- [ ] Create `src/api/dashboard.py`:
  - GET `/api/v1/dashboard/today`
  - Return: date, total_meals, total_calories, macro_progress, cat_mood, meals list
- [ ] Create `tests/integration/test_dashboard.py`

### 8.3: Weekly Recap Generation

- [ ] Create `src/models/weekly_recap.py` — id, user_id, week_start, week_end, narrative, avg_calories, best_day, worst_day, most_eaten_category, total_meals_logged, actionable_nudge, stats_json, created_at
- [ ] Create `src/llm/prompts/weekly_recap.j2` — recap prompt template
- [ ] Create `src/services/recap_service.py`:
  - `get_week_stats(db, user_id, week_start)` → summarize the week
  - `generate_recap(db, user_id, week_stats, profile)` → call Sonnet, save to DB
  - `get_latest_recap(db, user_id)` → get most recent
- [ ] Alembic migration
- [ ] Create `tests/integration/test_recap_service.py`

### 8.4: Weekly Recaps API

- [ ] Create `src/schemas/weekly_recap.py` — WeeklyRecapResponse
- [ ] Create `src/api/weekly_recaps.py`:
  - GET `/api/v1/recaps/` — list all (paginated, newest first)
  - GET `/api/v1/recaps/{recap_id}` — get one
  - POST `/api/v1/recaps/generate` — manually trigger (debug)
- [ ] Create `tests/integration/test_weekly_recaps.py`

### 8.5: Scheduler (Sunday Job)

- [ ] Add `apscheduler` to pyproject.toml
- [ ] Create `src/services/scheduler.py`:
  - `initialize_scheduler()` — set up APScheduler with CronTrigger (Sun 00:00)
  - `recap_job(db)` — async job that loops users, generates recaps
  - `should_generate_recap(user_id)` — check if user logged food this week
- [ ] Wire into `src/app.py` startup event
- [ ] Create `tests/unit/services/test_scheduler.py`

### 8.6: Cat API

- [ ] Create `src/schemas/cat_state.py` — CatStateResponse
- [ ] Create `src/api/cat.py`:
  - GET `/api/v1/cat/state` → current mood + status line
- [ ] Create `tests/integration/test_cat.py`

### 8.7: Final Integration

- [ ] Alembic migration for all new models
- [ ] Create `tests/integration/test_backend_complete.py` — full flow test

---

## Success Criteria

- [x] Cat mood calculation (5 moods + status line)
- [x] Dashboard endpoint returns today's progress + cat mood
- [x] Weekly recap generation (AI narrative + nudge)
- [x] Scheduler runs every Sunday at midnight
- [x] Weekly recaps API (list, get, trigger)
- [x] Cat API endpoint
- [x] All models + migrations created
- [x] All tests pass
- [x] Backend is feature-complete ✅
