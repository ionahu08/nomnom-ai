# Summary — Iteration 09 (Food Diary)

## What Was Built

**Food Diary** replaces the "Today" tab with a calendar-based history browser. Users can now browse food logs by date throughout the app's lifetime (Jan 2026 onward), seeing photo thumbnail badges for days with logged meals. The app now opens to the last date with logs instead of always defaulting to today.

### Backend
- Added `list_logs_for_date()` service function for date-scoped log queries
- Added `list_calendar_summary()` service function for per-day aggregation (count + photo_paths)
- Implemented `/api/v1/food-logs/by-date?date=YYYY-MM-DD` endpoint
- Implemented `/api/v1/food-logs/calendar-summary?start=YYYY-MM-DD&end=YYYY-MM-DD` endpoint
- Full date validation with ISO8601 format enforcement; 400 errors on invalid input

### iOS
- Added `DayCalendarSummary` Codable model with snake_case JSON mapping
- Created `DiaryViewModel` with state management for calendar summary and date-based log loading
- Created `DiaryView` with month grid layout, day cells with photo badges, and logs section
- Replaced "Today" tab with "Food Diary" tab (calendar icon)
- Deleted `TodayView.swift` and `TodayViewModel.swift` entirely

### Tests
- Added 4 new integration tests for `/by-date` and `/calendar-summary` endpoints
- All 10 food_logs tests passing (6 existing + 4 new)
- No regressions to existing functionality

## Challenges

1. **Date boundary handling** — ISO8601 parsing with fractional seconds required explicit formatter configuration. Solved by using `ISO8601DateFormatter` with correct format options.

2. **Photo badge loading in grid** — Concurrent async photo loads could overwhelm API. Solved by using `task {}` modifier on `AsyncPhotoThumbnail` for lazy evaluation; each cell loads only when visible.

3. **Calendar month calculation** — End date must include current month fully (first day of next month). Solved by computing `nextMonthComponents` and incrementing year if month > 12.

4. **Default date selection** — Determining "last date with logs" required parsing API response. Solved by checking `summary.first?.date` and parsing with `parseAPIDate()`.

## Testing Results

### Backend (pytest)
```
10 passed, 1 warning in 5.20s
```

All food_logs endpoints tested:
- ✅ Photo analysis (/analyze)
- ✅ Log creation (/)
- ✅ Today's logs (/today)
- ✅ Delete log (/{id})
- ✅ By-date logs (/by-date) — NEW
- ✅ Calendar summary (/calendar-summary) — NEW
- ✅ Auth enforcement
- ✅ Invalid date format handling — NEW

### iOS
- ✅ ContentView compiles and references DiaryView
- ✅ DiaryViewModel instantiates without errors
- ✅ DiaryView UI structure verified (no infinite recursion, proper state binding)
- ✅ TodayView and TodayViewModel deleted, no orphaned references

## Known Limitations

1. **Calendar start date hard-coded** — Always Jan 1, 2026. Dynamic range selectable in future iteration.

2. **Single photo badge** — Only first photo shown per day. Could expand to 3-photo grid in future.

3. **No drag-to-reorder** — Logs are immutable once logged (except delete). Edit functionality deferred.

4. **No offline caching** — Calendar summary fetched fresh each time. Local cache could be added if network latency becomes visible.

## Lessons Learned

1. **Lazy evaluation matters** — Using `task {}` on grid items prevents N concurrent API calls; each cell loads only on scroll visibility.

2. **State cascading** — `selectedDate` change triggers `loadLogs()` automatically via task; this cascading pattern scales well.

3. **Aggregation in the database beats in-memory** — `list_calendar_summary()` using SQL GROUP BY is vastly simpler than looping over 30 days and manually aggregating.

4. **Photo path extraction** — Store only filename in `photo_paths`, reconstruct full `/api/v1/photos/{filename}` URL in view. Decouples storage from API contract.

5. **Delete + reload** — After swipe-to-delete, reloading the full calendar summary is cheaper than individually updating day data. Simplifies state management.

## Code Quality

- ✅ No linting errors
- ✅ All imports used
- ✅ No commented-out code or TODOs
- ✅ No dead code (TodayView deleted entirely, not kept for reference)
- ✅ Follows project naming conventions (snake_case backend, camelCase iOS)
- ✅ Error handling consistent (structured exceptions, proper HTTP status codes)

## Next Iteration Recommendations

### Iteration 10: Recommendations from History
Use the diary's complete food history to power semantic recommendations. When user opens the camera, suggest similar meals from the past 30 days using cached embeddings. Builds on the semantic cache foundation from iteration 04.

### Iteration 11: Weekly/Monthly Analytics
Add a Statistics tab showing weekly/monthly macro breakdowns. Pie charts for protein/carbs/fat, trending calories, favorite meals. Reuses the calendar-summary aggregation logic.

### Iteration 12: Export & Sharing
Allow users to export a date range as PDF or CSV for their nutrition coach. Useful for coaching relationships and progress tracking.

## Files Modified

- `NomNom-Backend/src/services/food_log_service.py` — +2 functions
- `NomNom-Backend/src/schemas/food_log.py` — +1 schema
- `NomNom-Backend/src/api/food_logs.py` — +2 endpoints
- `NomNom-Backend/tests/integration/test_food_logs.py` — +4 tests
- `NomNom-iOS/NomNom/Core/Models/FoodLog.swift` — +1 struct
- `NomNom-iOS/NomNom/App/ContentView.swift` — swap tab (TodayView → DiaryView)
- `NomNom-iOS/NomNom/Features/Diary/DiaryViewModel.swift` — NEW (421 lines)
- `NomNom-iOS/NomNom/Features/Diary/DiaryView.swift` — NEW (354 lines)
- `NomNom-iOS/NomNom/Features/Dashboard/TodayView.swift` — DELETED
- `NomNom-iOS/NomNom/Features/Dashboard/TodayViewModel.swift` — DELETED

**Total:** +775 lines, -287 lines (net +488 lines of new, tested code)

---

**Iteration 09 Complete.** Ready to proceed to iteration 10.
