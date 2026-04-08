# Iteration 09 — Food Diary (Calendar View)

## Goal

Replace the "Today" tab with a **Food Diary**: a calendar-based history browser that shows food logs by date. Users want to answer "what did I eat last Tuesday?" — the diary provides a month-at-a-glance view with thumbnail badges for logged meals, and tapping a date reveals the full log list for that day.

## What's Built (Prerequisites)

- Backend: auth, food log CRUD, LLM analysis, semantic caching
- iOS: auth, camera capture, food log submission, settings
- Database: food_log table with logged_at timestamp
- API contract: `/api/v1/food-logs/today` returns FoodLogResponse[]

## What We're Building

1. **Backend Endpoints** — Date-parameterized queries:
   - `GET /api/v1/food-logs/by-date?date=YYYY-MM-DD` → FoodLogResponse[]
   - `GET /api/v1/food-logs/calendar-summary?start=YYYY-MM-DD&end=YYYY-MM-DD` → DayCalendarSummary[]

2. **iOS Calendar View** — Diary tab (replaces Today):
   - Vertical scroll through Jan 2026 → current month
   - 7-column grid per month (Sun–Sat)
   - Days with logs show first photo as 40×40 circular thumbnail badge
   - Days without logs show just date number
   - Tap a date → logs section below updates

3. **Default Selection** — Auto-navigate to last logged date, not today

## Success Criteria

- [ ] Backend: `/by-date` endpoint returns logs for a specific date
- [ ] Backend: `/calendar-summary` endpoint returns per-day metadata (count, photo_paths)
- [ ] Backend: Date validation (YYYY-MM-DD format) with 400 errors
- [ ] iOS: Food Diary tab visible with "calendar" icon
- [ ] iOS: Calendar renders Jan 2026 through current month
- [ ] iOS: Days with logs show photo thumbnail badge
- [ ] iOS: App opens to last date with logs (not today)
- [ ] iOS: Tap a date → logs update below
- [ ] iOS: Swipe-to-delete → both list and calendar badges update
- [ ] All tests pass (backend + existing iOS)

## Resume Skills

- Date range filtering (SQL datetime boundaries)
- Calendar UI with grid layout (SwiftUI LazyVGrid)
- Image lazy-loading in collection views (async/await)
- State management across dependent views (selectedDate cascades)
- Pagination-less infinite scroll (month-by-month)
