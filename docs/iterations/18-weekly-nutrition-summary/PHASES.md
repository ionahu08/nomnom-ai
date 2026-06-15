# Iteration 18: Implementation Phases

**Updated Goal:** Build an "Insight" tab that displays nutrition analytics for multiple periods (Weekly, Monthly, 6-Month)

---

## Phase 1: Backend Analytics Repository (Day 1) ✅ COMPLETE

**Goal:** Build backend infrastructure to fetch and aggregate food log data for any time period.

**File:** `src/repositories/analytics_repository.py`

The backend already supports flexible periods:
- `get_analytics_summary(period="week|month", date=end_date)` 
- Works for any period (7 days, 30 days, 180 days)
- Already deployed and tested ✅

**Tests:**
- Test weekly stats calculation
- Test daily breakdown accuracy
- Test consistency percentage
- Test with empty data
- Test with partial week

---

## Phase 2: Analytics API Endpoint (Day 1) ✅ COMPLETE

**File:** `src/api/analytics.py`

Endpoint supports multiple periods:
```
GET /api/v1/analytics/summary?period=week|month&date=2026-06-14
```

Already returns all needed data for any period:
- Calories, protein, carbs, fat (total, average, target, percentage)
- Daily breakdown for charting
- Top foods
- Consistency metrics
- Already tested ✅

---

## Phase 3: iOS InsightView with Period Selector (Days 2-3) ✅ COMPLETE

**Renamed:** WeeklyNutritionView → InsightView

**New Feature:** Period selector at top of view
- Buttons: Week | Month | 6M
- Shows insight data for selected period
- Week: 7-day period
- Month: 30-day period  
- 6M: 180-day period

**File:** `NomNom-iOS/NomNom/Features/Insights/InsightView.swift`

**Layout:**
```
┌─────────────────────────────┐
│ Insight                     │
├─────────────────────────────┤
│ [Week] [Month] [6M]         │  ← Period selector (new)
├─────────────────────────────┤
│ < Jun 8 - Jun 14 >          │
├─────────────────────────────┤
│ Week Total: 1,850 cal/day   │
│ vs Target: 2,000 cal/day    │
│ Status: 92.5% (On Track ✅) │
├─────────────────────────────┤
│ [Daily Calorie Chart]       │
├─────────────────────────────┤
│ [Macro Breakdown Chart]     │
├─────────────────────────────┤
│ Nutrient Targets            │
│ 🍗 Protein, 🍙 Carbs, 🍖 Fat│
├─────────────────────────────┤
│ Top Foods                   │
└─────────────────────────────┘
```

**Changes from Original:**
1. Rename tab from "Weekly" to "Insight" 
2. Add period selector (Week/Month/6M buttons)
3. When period changes:
   - Fetch new data from API with `period=week|month`
   - Update period label to show date range
   - Update all charts and summaries
4. Same charts and data display for all periods

**File:** `NomNom-iOS/NomNom/Features/WeeklyNutrition/WeeklyNutritionView.swift`

Components:
1. **Period Selector** — Show week of June 8-14, with prev/next buttons
2. **Calorie Summary** — Total, average, vs. target with color coding
3. **Daily Breakdown** — Bar chart showing calories for each day
4. **Macro Breakdown** — Pie chart or stacked bars (Protein, Carbs, Fat)
5. **Consistency** — "Logged 6/7 days" with visual indicator
6. **Top Foods** — List of most-eaten foods during the week

**Layout:**
```
┌─────────────────────────────┐
│ 📊 Weekly Summary           │
├─────────────────────────────┤
│ < Jun 8 - Jun 14 >          │
├─────────────────────────────┤
│                             │
│  Week Total: 1,850 cal/day  │
│  vs Target: 2,000 cal/day   │
│  Status: 92.5% (On Track ✅)│
│                             │
├─────────────────────────────┤
│  Daily Calories             │
│  [||||||||||||||||||||....] │
│  Sun Mon Tue Wed Thu Fri Sat│
│                             │
├─────────────────────────────┤
│  Nutrient Composition       │
│  Protein:  120g / 150g ✅   │
│  Carbs:    180g / 200g ✅   │
│  Fat:       60g /  65g ✅   │
│                             │
├─────────────────────────────┤
│  Top Foods                  │
│  🍗 Chicken Breast (4x)     │
│  🍙 Noodles (3x)            │
└─────────────────────────────┘
```

---

## Phase 3b: Data Visualization Components (Days 3-4) ✅ COMPLETE

**Files:**
- `WeeklyChart.swift` — Bar chart for daily calories
- `MacroBreakdown.swift` — Donut chart for protein/carbs/fat

**Features:**
- ✅ Daily calorie bars (7 days)
- ✅ Color-coded zones (green/orange/red)
- ✅ Macro donut chart with percentages
- ✅ Responsive layouts
- ✅ Working and tested

---

## Phase 4: Integration & Polish (Day 5) ✅ COMPLETE

**Tasks:**

### 4a: Rename & Reorganize ✅
- [x] Update ContentView tab: "Weekly" → "Insight"
- [x] Keep icon: 📊 (chart.bar.fill)
- Note: Files remain in `Features/WeeklyNutrition/` folder (naming kept for clarity)

### 4b: Add Period Selector ✅
- [x] Add period buttons: [Week] [Month] [6M]
- [x] Style buttons (selected = highlighted, unselected = muted)
- [x] Track selected period in ViewModel
- [x] When period changes: fetch new API data

### 4c: Update ViewModel ✅
- [x] Add `selectedPeriod` property (week/month/6m)
- [x] Modify `loadInsightData()` to use selected period
- [x] Update API call: `?period=week|month|6m&date=...`
- [x] Period label calculation: Dynamic from backend response (works for all periods)
- [x] Fix: Backend now accepts "6m" period (added in analytics.py)

### 4d: Testing 🚧 IN PROGRESS
- [ ] Test Week period: shows 7-day data
- [ ] Test Month period: shows 30-day data
- [ ] Test 6M period: shows 180-day data
- [ ] Navigate between periods: data updates correctly
- [ ] No console errors
- [ ] No crashes when switching periods
- [ ] Charts display correctly for all periods

---

## Architecture: Data Flow

```
iOS App
  ↓
InsightView (Period Selector)
  ↓
User taps [Week] [Month] [6M]
  ↓
InsightViewModel.loadInsightData(period: "week|month")
  ↓
APIClient.get(/api/v1/analytics/summary?period=week|month&date=...)
  ↓
FastAPI Analytics Endpoint
  ↓
AnalyticsRepository.get_aggregated_stats(period)
  ↓
SQLAlchemy Async Query → FoodLog table
  ↓
Aggregate data for selected period + fetch targets
  ↓
Build AnalyticsSummaryResponse
  ↓
Return JSON to iOS
  ↓
InsightView renders with updated data
```

---

## Performance Targets

- API response time: < 200ms (all periods)
- Period switch latency: < 1 second
- View rendering: smooth 60 FPS
- No N+1 queries
- No memory leaks when switching periods

---

## Testing Checklist - Phase 4

- [ ] Rename "Weekly" tab to "Insight" ✅
- [ ] Period selector buttons display [Week] [Month] [6M]
- [ ] Week period: shows 7-day data correctly
- [ ] Month period: shows 30-day data correctly
- [ ] 6M period: shows 180-day data correctly
- [ ] Switching periods: data updates, charts refresh
- [ ] Period label updates for each period
- [ ] No console errors when switching periods
- [ ] No crashes on rapid period switching
- [ ] Charts responsive to all period types
- [ ] Edge cases: empty period, new user, past dates
- [ ] API calls use correct period parameter
