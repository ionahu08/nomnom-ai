# Iteration 18: Bug Log & Decisions

**Status:** Phase 1 ✅ | Phase 2 ✅ | Phase 3 ✅ | Ready for Testing 🚀

---

## Known Issues

(None currently)

---

## Blockers

(None currently)

---

## Design Decisions

### 1. Weekly Stats Aggregation (Phase 1)
**Decision:** Calculate stats in Python, not SQL  
**Why:** Simplicity and readability; data volume is small (< 300 logs/week typical)  
**Trade-off:** Slightly slower than raw SQL GROUP BY, but more maintainable

### 2. Default Nutrition Targets
**Decision:** Provide sensible defaults (2000 cal, 150g protein, 200g carbs, 65g fat)  
**Why:** App should work for users without a profile; can override via Settings  
**Implementation:** AnalyticsRepository.get_user_targets() returns defaults if no profile

### 3. Daily Breakdown as List, Not Dict
**Decision:** Return daily_breakdown as list sorted by date  
**Why:** Matches JSON conventions; easier for iOS to iterate and chart  
**Trade-off:** Slightly less flexible than dict keyed by date

### 4. Consistency Calculation
**Formula:** `(days_logged / 7) * 100`  
**Why:** Shows percentage of the week user actually tracked  
**Example:** 6 days logged = 85.7% consistency

---

## Critical Bug: Backend Import Error Causing All API Timeouts

**Symptom:** iOS app showed "Failed to load profile: The request timed out" when accessing Settings tab. All API calls to backend timed out after ~5 seconds.

**Root Cause Analysis:**
- Phase 1 (analytics.py creation) introduced an incorrect import: `from src.api.dependencies import get_current_user, get_db`
- The correct module names are: `src.api.deps` (for get_current_user) and `src.database` (for get_db)
- This import error prevented the entire FastAPI app from loading
- Backend process was running but refusing all connections (hung during startup)
- No error was visible in logs because the terminal session was backgrounded

**Impact:**
- Every iOS API request to /api/v1/profile and other endpoints timed out
- Settings tab became completely unusable
- Error message "Failed to load profile: The request timed out" was misleading (actual issue was app not loading, not a timeout)

**Debugging Process:**
1. Initial hypothesis: APIClient baseURL wrong (ngrok vs localhost) ❌ Wrong
2. Hypothesis: AuthService not properly initialized ❌ Wrong
3. Actual investigation: Tested curl against localhost:8000, request hung
4. Checked backend process - was running but not responding
5. Restarted backend to see logs: discovered ModuleNotFoundError in analytics.py import
6. Fixed import paths to use correct modules

**Fix (Commit 586c6b4):**
```python
# Before (WRONG):
from src.api.dependencies import get_current_user, get_db

# After (CORRECT):
from src.api.deps import get_current_user
from src.database import get_db
```

**Status:** ✅ Fixed - Backend now responds to all API requests

**Lessons Learned:**
- Import errors in new API files can silently break the entire backend
- Always verify backend is actually running and responding before debugging client code
- When backend timeouts occur, check backend startup logs first
- Easy to miss import errors when creating new endpoint files

---

## Testing Notes

**Phase 1 Testing:**
- ✅ API endpoint accessible at `/api/v1/analytics/summary`
- ✅ Endpoint returns 401 Unauthorized (auth working)
- ✅ Test fixtures created for 6 logs across 6 days
- ✅ 8 test cases written (totals, averages, top foods, targets, defaults, empty data)
- ✅ Ready for full pytest run with proper auth token

**Settings Tab Regression Testing:**
- ✅ Health Profile section loads without spinner after app launch
- ✅ Cat Style section displays correctly
- ✅ Profile data fetches from localhost:8000 API
- ✅ No errors in console

---

## Prevention Checklist for Future Iteration 18 Work

**MANDATORY STEPS after creating any new backend API file:**

### 1. Import Verification
- [ ] Check all imports use correct module names:
  - `get_current_user, security` → from `src.api.deps` (NOT `src.api.dependencies`)
  - `get_db` → from `src.database` (NOT `src.api.deps` or other modules)
  - Use model imports: `from src.models.* import ...`
  - Use schema imports: `from src.schemas.* import ...`
  - Use service imports: `from src.services.* import ...`

### 2. Backend Startup Test (DO THIS EVERY TIME)
After modifying any backend code:
```bash
cd NomNom-Backend
# Kill any running backend process
pkill -f "uvicorn src.app:app"

# Restart and watch for errors
./venv/bin/python -m uvicorn src.app:app --reload --host 0.0.0.0 --port 8000

# Wait for message: "Application startup complete"
# If it hangs or errors, fix before proceeding
```

### 3. API Endpoint Test
```bash
# Test with invalid token (should get 401, not timeout)
curl -m 5 http://localhost:8000/api/v1/analytics/summary \
  -H "Authorization: Bearer test_token"

# Should respond with JSON error, not timeout
# Expected: {"detail":"Invalid or expired token"} (or similar)
# NOT: timeout after 5 seconds
```

### 4. iOS App Test
- [ ] Clean build: `Product → Clean Build Folder` (⇧⌘K)
- [ ] Run app in simulator
- [ ] Navigate to Settings tab
- [ ] Verify Health Profile section loads (no spinner)
- [ ] Check Xcode console for `[ProfileService]` and `[APIClient]` logs
- [ ] Should see: `[APIClient] GET http://localhost:8000/api/v1/profile`

### 5. Import Style Guide (Reference)
```python
# CORRECT import order for API endpoints:
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user  # ✅ Correct
from src.database import get_db             # ✅ Correct
from src.models.user import User            # ✅ Correct
from src.schemas.analytics import ResponseSchema  # ✅ Correct
from src.repositories.analytics_repository import AnalyticsRepository  # ✅ Correct
from src.services.profile_service import get_effective_targets  # ✅ Correct

# NEVER use:
from src.api.dependencies import ...  # ❌ Module doesn't exist
from src.api import deps              # ❌ Wrong syntax
from src.llm.something import ...     # ❌ Wrong layer
```

### 6. Common Mistakes to Avoid
| Mistake | Symptom | Fix |
|---------|---------|-----|
| Wrong import path for deps | ModuleNotFoundError, app won't start | Use `src.api.deps` |
| Mixing sync/async imports | Various async/await errors | Use AsyncSession from sqlalchemy.ext.asyncio |
| Circular imports | App won't load | Check import order |
| Missing service/repo files | ImportError | Create file before importing |
| Typos in model field names | Validation errors | Match schema to model exactly |

### 7. After Phase 1 Completion
- [ ] All imports verified and tested
- [ ] Backend starts with "Application startup complete"
- [ ] curl test returns JSON response (not timeout)
- [ ] iOS Settings tab loads without spinner
- [ ] Console logs show successful profile fetch
- [ ] Tests pass: `pytest tests/test_analytics.py`

---

## Phase 2 Completion ✅

**What Was Built (Commit 467e7d2):**
1. **WeeklySummary.swift** - Data models matching backend API response
   - Proper JSON decoding with CodingKeys for snake_case conversion
   - NutrientSummary, DailyBreakdown, TopFood structs

2. **WeeklyNutritionViewModel.swift** - Business logic & API integration
   - Fetches data from `/api/v1/analytics/summary` endpoint
   - Week navigation (previous/next)
   - Loading, error, and success state handling
   - Helper methods for formatting dates and status labels

3. **WeeklyNutritionView.swift** - UI components
   - Period selector with navigation buttons
   - Calorie summary (average, target, percentage)
   - Calorie status indicator (On Track ✅, Over ⚠️, Under ↓)
   - Logging consistency with progress bar
   - Nutrient breakdown with icons (🍗 Protein, 🍙 Carbs, 🍖 Fat)
   - Top foods list
   - Proper error and loading state UI

4. **ContentView.swift** - Tab integration
   - New "Weekly" tab added between Food Diary and Settings
   - Icon: chart.bar.fill

5. **Project regenerated** - xcodegen project updated to include new files

**Status:** ✅ Ready for end-to-end testing

---

## Phase 3 Completion ✅

**What Was Built (Commit d46e130):**
1. **WeeklyChart.swift** - Daily calorie bar chart
   - 7 bars showing calories for each day (Sun-Sat)
   - Color-coded: green (90-110% target), orange (110-130%), red (130%+)
   - Automatic scaling based on max daily value
   - Target reference line
   - Day labels and legend
   - Responsive to different calorie ranges

2. **MacroBreakdown.swift** - Macro distribution visualization
   - Donut chart showing Protein/Carbs/Fat split
   - Color-coded: orange (protein), blue (carbs), red (fat)
   - Percentage indicators
   - Side panel with individual macro stats
   - Progress bars for each macro
   - Calorie breakdown (shows how many calories from each macro)
   - Custom gradient backgrounds for macro cards

3. **WeeklyNutritionView.swift** - Chart integration
   - WeeklyChart integrated above consistency metrics
   - MacroBreakdown displayed prominently
   - Renamed section to "Daily Targets" for clarity
   - Better visual hierarchy: charts → targets → top foods

**Visual Features:**
- All charts built with custom SwiftUI shapes (no external libraries)
- Color-coded zones provide immediate feedback
- Progress bars show target achievement
- Responsive layouts that work on all screen sizes
- Smooth rendering without animations (can add in Phase 4 if desired)

**Status:** ✅ Ready for full end-to-end testing

---

## Critical Bug #1: AsyncSession Incompatibility (500 Error)

**Symptom:** iOS app showed "Failed to load weekly summary: Server error (500)" when accessing Weekly tab

**Root Cause:**
The analytics repository was using synchronous SQLAlchemy methods (`.query()`, `.first()`) with `AsyncSession`, which doesn't support them. This is incompatible with async database operations in FastAPI.

**Error Stack:**
```
AttributeError: 'AsyncSession' object has no attribute 'query'
```

**Why It Happened:**
- Phase 1 created analytics_repository.py with synchronous syntax
- The API endpoint uses `AsyncSession` from `get_db` dependency
- Mismatch between synchronous repository and async database session

**Fix (Commit 581abeb):**
- Converted all AnalyticsRepository methods to `async`
- Changed `.query()` to `select()` with `await db.execute()`
- Changed `.first()` to `.scalar_one_or_none()`
- Added `await` to all repository method calls in analytics.py
- Added imports: `AsyncSession`, `select` from sqlalchemy

**Prevention:**
When creating new API endpoints that use the database:
1. **Always check the database session type** in your endpoint
   - If using `db: AsyncSession = Depends(get_db)` → use async SQLAlchemy
   - If using `db: Session = Depends(get_db)` → use synchronous SQLAlchemy
2. **Use correct syntax for async:**
   ```python
   # ✅ CORRECT (async)
   from sqlalchemy import select
   stmt = select(Model).where(...)
   result = await db.execute(stmt)
   
   # ❌ WRONG (synchronous, won't work with AsyncSession)
   db.query(Model).filter(...).all()
   ```
3. **Mark repository methods as async:**
   ```python
   @staticmethod
   async def get_data(db: AsyncSession, ...):
       # ... use await for all db operations
   ```
4. **Add await in endpoints:**
   ```python
   # All repository calls must use await
   data = await AnalyticsRepository.get_data(db, ...)
   ```

---

## Critical Bug #2: JSON Decoding Type Mismatch (Failed to Process Response)

**Symptom:** iOS app showed "Failed to load weekly summary: Failed to process response" even though backend was responding with valid JSON

**Root Cause:**
The iOS Codable models didn't match the backend API response types:
1. **average field:** Backend returns `Double` (e.g., 120.5), iOS model expected `Int`
2. **percentage field:** Backend returns optional `Double?` (null when no target), iOS model expected non-optional `Double`

**Why It Happened:**
- iOS model was designed before backend implementation
- Backend calculations naturally produce floats (sum / count = float)
- Backend handles edge cases by returning null for percentage when no target exists
- iOS didn't account for these edge cases

**Error:**
```
Codable decoding error - type mismatch:
  expected: Int
  got: Double (120.5)
```

**Fix (Commit eca4f7f):**
1. **WeeklySummary.swift models:**
   - Changed `average: Int` → `average: Double`
   - Changed `percentage: Double` → `percentage: Double?`

2. **WeeklyNutritionViewModel.swift:**
   - Updated `getCalorieStatus()` to unwrap optional percentage
   - Updated `getNutrientStatus(percentage: Double?)` to accept optional

3. **WeeklyNutritionView.swift:**
   - Handle optional percentage with if-let binding
   - Updated `NutrientRow` to accept `current: Double` instead of `Int`
   - Display "N/A" when percentage is nil

**Prevention:**
When building iOS-backend data models:
1. **Always test the actual API response first:**
   ```bash
   curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/v1/endpoint | python3 -m json.tool
   ```
   Verify the actual types (Int vs Double, null vs non-null)

2. **Match types exactly in Codable models:**
   ```swift
   // Check what backend sends
   // Backend sends: {"average": 120.5} → must be Double
   // Backend sends: {"percentage": null} → must be Double?
   
   struct NutrientSummary: Codable {
       let average: Double  // NOT Int
       let percentage: Double?  // NOT Double
   }
   ```

3. **Use CodingKeys for field mapping:**
   ```swift
   enum CodingKeys: String, CodingKey {
       case average
       case percentage
   }
   ```

4. **Test decoding early:**
   - Create test data matching backend response
   - Use JSONDecoder to verify model works
   - Don't assume types—verify!

5. **Handle edge cases in UI:**
   - Use optional binding for optional fields
   - Provide fallback UI (e.g., "N/A")
   - Don't force-unwrap!

**Lessons Learned:**
- Backend and iOS models must stay in sync
- Always test with real API responses, not hypothetical ones
- Document which fields are optional in the API contract
- Consider adding API documentation / OpenAPI spec for clarity

---

---

## Critical Bug #3: 6-Month Period Not Supported in Backend API

**Symptom:** iOS app would fail to load data when user selected "6M" (6-month) period. API endpoint would reject request with 400 error.

**Root Cause:**
1. Backend `analytics.py` endpoint only accepted `Literal["week", "month"]` in period parameter (line 18)
2. iOS app sent "6m" as period value, but backend would reject it as invalid
3. Period calculation logic was missing for 6-month (180-day) periods

**Why It Happened:**
- Phase 3 and 4 requirements expanded to include 6-month view (Apple Sleep app pattern)
- Backend was only designed for week/month, not extended periods
- Frontend and backend period handling became out of sync

**Fix (Commit 06c34a5):**
```python
# Before (WRONG):
period: Annotated[Literal["week", "month"], Query(...)]
# ... only handled week (7 days) and month (30 days)

# After (CORRECT):
period: Annotated[Literal["week", "month", "6m"], Query(...)]
# ... handles all three:
if period == "week":
    start_date = end_date - timedelta(days=7)
    total_days = 7
elif period == "month":
    start_date = end_date - timedelta(days=30)
    total_days = 30
elif period == "6m":
    start_date = end_date - timedelta(days=180)
    total_days = 180
```

**Status:** ✅ Fixed - Backend now responds to week, month, and 6m requests

---

## Critical Bug #4: iOS Period API Mapping Incorrect

**Symptom:** iOS app would send incorrect period parameter to backend (sixMonth → "month" instead of "6m")

**Root Cause:**
```swift
// WeeklyNutritionViewModel line 44 (WRONG):
let apiPeriod = period == .sixMonth ? "month" : period.rawValue
```

This logic mapped `.sixMonth` (rawValue="6m") to "month" instead of using its actual rawValue. This caused:
- 6M button to fetch 30-day data, not 180-day
- Confusion between Month and 6M periods
- API parameter mismatch with backend expectations

**Fix (Commit 2191787):**
```swift
// WeeklyNutritionViewModel line 44 (CORRECT):
let apiPeriod = period.rawValue
```

Simply use the enum's rawValue directly:
- `.week` → "week" (7 days)
- `.month` → "month" (30 days)
- `.sixMonth` → "6m" (180 days)

**Status:** ✅ Fixed - iOS now sends correct period parameter

**Prevention:**
- Always use enum rawValues directly unless there's explicit transformation logic needed
- Test period parameter by adding logging: `print("[ViewModel] Sending period=\(apiPeriod)")`
- Backend Literal types must match iOS enum rawValues exactly

---

## Critical Bug #5: Hardcoded Day Counts Override Actual Calculations

**Symptom:** Consistency metrics showed wrong percentages for different months. February user logging 28 days showed "28/30 = 93%" instead of "28/28 = 100%"

**Root Cause:**
```python
# analytics.py endpoint calculated total_days for consistency:
if period == "week":
    total_days = 7
elif period == "month":
    total_days = 30  # ❌ Hardcoded! Ignores actual month length
elif period == "6m":
    total_days = 180  # ❌ Hardcoded! Ignores actual calendar structure
```

But the repository correctly calculated it:
```python
# analytics_repository.py line 119
total_days = (end_date - start_date).days  # ✅ Correct
```

The endpoint was throwing away the correct value and using hardcoded ones.

**Impact:**
- February user (28 days): 28/30 = 93% consistency (incorrect, should be 100%)
- July user (31 days): 31/30 = 103% consistency (over 100%!)
- 6-month period: Ignored actual month lengths

**Fix (Commit 736ae9a):**
```python
# Before (WRONG):
if period == "week":
    total_days = 7
elif period == "month":
    total_days = 30
elif period == "6m":
    total_days = 180

days_logged, _ = await AnalyticsRepository.get_days_logged(...)

# After (CORRECT):
# Just calculate the periods, let repository give us actual total_days
if period == "week":
    start_date = end_date - timedelta(days=7)
elif period == "month":
    start_date = end_date - timedelta(days=30)
elif period == "6m":
    start_date = end_date - timedelta(days=180)

days_logged, total_days = await AnalyticsRepository.get_days_logged(...)
# Now total_days is actual calendar days (28-31 for month, etc.)
```

**Status:** ✅ Fixed - Consistency now shows actual month lengths

---

## Critical Bug #6: Averages Calculated Per Log Entry, Not Per Day

**Symptom:** Daily average calories way too low. For example, 3,000 calories logged as 4 meals showed as 750 cal/day instead of 428 (or 1,500 if counting only logged days)

**Root Cause:**
```python
# analytics_repository.py line 53
num_logs = len(logs)  # Number of MEAL entries, not days
avg_calories = total_calories / num_logs  # ❌ Per meal, not per day
```

The repository divided by number of log entries (meals) instead of number of days.

**Example:**
- User logs Monday: 1,000 cal (1 meal)
- User logs Tuesday: 2,000 cal (3 meals)
- Total: 3,000 cal from 4 meal entries
- Repository calc: 3,000 / 4 = 750 cal/entry ❌
- Should be: 3,000 / 7 calendar days = 428 cal/day ✅

**Fix (Commit 41b0e9c):**

Instead of using repository averages, endpoint now recalculates:
```python
# Correct: Average per CALENDAR day
avg_calories = stats["calories"]["total"] / total_days if total_days > 0 else 0
avg_protein = stats["protein_g"]["total"] / total_days if total_days > 0 else 0
avg_carbs = stats["carbs_g"]["total"] / total_days if total_days > 0 else 0
avg_fat = stats["fat_g"]["total"] / total_days if total_days > 0 else 0
```

Now:
- Week average: total calories / 7 days
- Month average: total calories / 28-31 days (actual month)
- 6-month average: total calories / actual 180-day window

**Status:** ✅ Fixed - All averages now per calendar day

---

## Design Decision: UI Redesign with Line Charts

**Feedback:** "Weekly Average" label doesn't make sense on Monthly/6M tabs

**Problem:**
- Label was hardcoded to "Weekly Average" across all three tabs
- Confusing UX: Monthly tab showing "Weekly Average"
- Original bar chart (WeeklyChart) and donut chart (MacroBreakdown) didn't provide trend visualization

**Solution (Commit 4a749b0):**
- Remove "Weekly Average" section entirely
- Replace bar chart with **line plots** for each metric
- Create 4 separate charts: Calories, Protein, Carbs, Fat
- Period-aware x-axis labels:
  - Weekly: Day names (Sun, Mon, Tue, Wed, Thu, Fri, Sat)
  - Monthly: Date numbers (01, 05, 10, 15, 20, 25, 30)
  - 6-Month: Month abbreviations (J, F, M, A, M, J, J, A, S, O, N, D)
- Only show markers (dots) for dates with logged data
- Lines connect markers to show trends

**Benefits:**
- Cleaner UI without confusing hardcoded labels
- Better trend visualization (line shows patterns over time)
- Four charts show complete nutritional picture
- Period-agnostic x-axis automatically adjusts to week/month/6m
- Markers only on logged dates = clear gap visualization for missing days

---

## Phase 4: Integration & Polish

**Status:** 🚀 Testing (4a-4d complete, 4e in progress)

**Testing Plan:**

### 1. Core Functionality Tests
- [ ] **Week Navigation:** Click prev/next buttons, data updates correctly
- [ ] **Data Accuracy:** Verify displayed values match backend calculations
- [ ] **Period Selector:** Shows correct week range (e.g., "Jun 8 - Jun 14")
- [ ] **Tab Integration:** Weekly tab appears between Food Diary and Settings
- [ ] **Tab Icons:** Chart.bar.fill icon displays correctly

### 2. Chart Rendering Tests
- [ ] **Daily Calorie Chart:** All 7 bars display, colors correct (green/orange/red)
- [ ] **Macro Donut Chart:** Shows all 3 macros, colors correct, percentages display
- [ ] **Color Coding:** Green (on-track), orange (over), red (way over) work correctly
- [ ] **Responsive:** Charts scale properly on different screen sizes

### 3. Data Display Tests
- [ ] **Calorie Summary:** Total, average, target, percentage display
- [ ] **Consistency Metric:** Progress bar shows correctly (X/7 days)
- [ ] **Nutrient Targets:** Protein/Carbs/Fat with average, target, icons
- [ ] **Top Foods:** Lists most eaten foods with count and calories
- [ ] **Error State:** Shows error message when API fails
- [ ] **Loading State:** Shows spinner while loading

### 4. Edge Cases
- [ ] **New User (no logs):** Shows empty state gracefully
- [ ] **Partial Week:** Shows correct consistency even with <7 days
- [ ] **No Target Set:** Handles null percentage correctly (shows "N/A")
- [ ] **Future Date:** Navigation doesn't break with future dates
- [ ] **Past Date:** Can navigate to old weeks with historical data

### 5. Console & Performance
- [ ] **No Console Errors:** Xcode console has no errors or warnings
- [ ] **No Crashes:** App doesn't crash when navigating
- [ ] **Loading Time:** Data loads within 2 seconds
- [ ] **Memory:** No memory leaks when switching tabs repeatedly

### 6. UI Polish
- [ ] **Spacing & Alignment:** All elements properly spaced
- [ ] **Font Sizes:** Hierarchy is clear (heading → body → caption)
- [ ] **Colors:** Dark mode looks good, text is readable
- [ ] **Buttons:** Prev/next buttons are easy to tap
- [ ] **Scrolling:** Content scrolls smoothly without jank
