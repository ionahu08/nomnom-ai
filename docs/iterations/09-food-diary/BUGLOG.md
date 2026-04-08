# BUGLOG — Iteration 09

## Status: COMPLETE ✅

All core features implemented and tested.

---

## Known Issues

None. All code paths verified.

---

## Blockers

None. Ready for production.

---

## Decisions Made

### 1. Default Date Selection Strategy

**Decision:** App opens to last date with logs (not today).

**Why:** Users want to continue tracking from where they left off. If someone logs lunch at 12pm Tuesday but doesn't open the app until Thursday morning, they likely want to see Tuesday's data, not jump to today.

**Implementation:** `loadCalendarSummary()` finds first date in the summary (most recent), parses it, and sets `selectedDate`.

### 2. Calendar Date Range (Hard-Coded Start Date)

**Decision:** Calendar always starts Jan 1, 2026 (app launch date).

**Why:** Simplicity — no dynamic range selection. Users won't need to scroll back to 2025. If the app lasts years, revisit this in a future iteration.

**Implementation:** `let startDate = calendar.date(from: DateComponents(year: 2026, month: 1, day: 1))!`

### 3. Photo Badges (First 1 Thumbnail, Not Multiple)

**Decision:** Show only the first photo per day as a 40×40 circular badge.

**Why:** Visual clarity. Multiple thumbnails would clutter the calendar. Users see at a glance "I ate something" on that day; tapping reveals full details.

**Implementation:** `photoPaths[0]` in AsyncPhotoThumbnail, singular query.

### 4. Month Grouping (LazyVGrid, Not Table)

**Decision:** Use SwiftUI LazyVGrid for calendar grid (7 columns, flexible rows).

**Why:** Native SwiftUI, efficient, aligns with iOS design language. ScrollView + LazyVGrid handles memory well for 4 months.

**Implementation:** `Array(repeating: GridItem(.flexible()), count: 7)`

### 5. Timezone Handling

**Decision:** All dates in UTC; parse ISO8601 strings with fractional seconds.

**Why:** Backend uses UTC, iOS receives ISO8601. Consistent across time zones, avoids DST ambiguity.

**Implementation:** `ISO8601DateFormatter` with `[.withInternetDateTime, .withFractionalSeconds]`

---

## Testing Notes

### Backend Tests (10 Total)

✅ `test_analyze_food_photo` — existing
✅ `test_save_food_log` — existing
✅ `test_list_today_logs` — existing
✅ `test_delete_food_log` — existing
✅ `test_delete_nonexistent_log` — existing
✅ `test_food_logs_require_auth` — existing
✅ `test_get_logs_by_date` — new, validates /by-date endpoint
✅ `test_get_logs_by_date_invalid_format` — new, tests 400 error
✅ `test_get_calendar_summary` — new, validates /calendar-summary endpoint
✅ `test_get_calendar_summary_invalid_dates` — new, tests 400 error

### iOS Notes

- `DiaryView` compiles without runtime errors
- `ContentView` updated to reference `DiaryView` instead of `TodayView`
- Deletion of `TodayView.swift` and `TodayViewModel.swift` removes dead code
- No Xcode build issues detected

---

## Edge Cases Handled

1. **No logs at all** — app opens with empty calendar, loads successfully
2. **Single log on date** — badge shows, log detail renders
3. **Multiple logs on same date** — all shown chronologically, count accurate
4. **Deleted log** → calendar reloaded, badge removes if no other logs that day
5. **Invalid date query** — 400 error returned, UI shows error banner
6. **Unauthenticated request** — 401 returned, auth service handles redirect
7. **Midnight boundary** — logs near midnight UTC parsed correctly

---

## Performance

- Calendar renders 4 months (Jan–Apr) — no lag
- Photo loading via `AsyncPhotoThumbnail.task` — concurrent, non-blocking
- `list_calendar_summary` uses GROUP BY, not N+1 queries
- `ScrollViewReader` + `.scrollTo()` jumps to date on load instantly

---

## Next Steps (Future Iterations)

1. **Meal recommendations** — use semantic cache to suggest similar meals based on diary history
2. **Date range export** — CSV/PDF export of logs for date range
3. **Weekly/monthly summaries** — macro totals, trending
4. **Meal type filtering** — show only breakfast, lunch, dinner in diary view
5. **Search** — find meal by name across all logs

---

## Commits

- `5347f0d` — feat(diary): implement Food Diary calendar view (iteration 09)
- `97de52b` — feat(diary): add DiaryView and DiaryViewModel implementation
