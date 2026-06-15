# Iteration 18: Implementation Phases

---

## Phase 1: Backend Analytics Repository (Day 1)

**Goal:** Build backend infrastructure to fetch and aggregate food log data for weekly analysis.

**File:** `src/repositories/analytics_repository.py`

Methods to implement:

```python
class AnalyticsRepository:
    @staticmethod
    def get_food_logs_for_period(db, user_id, start_date, end_date) → list[FoodLog]
        # Fetch all logs between dates
    
    @staticmethod
    def get_weekly_stats(db, user_id, end_date) → dict
        # Calculate stats for 7-day period ending on end_date
        # Returns: {
        #   "calories": {"total": X, "average": Y, "daily": [...]},
        #   "protein_g": {...},
        #   "carbs_g": {...},
        #   "fat_g": {...},
        #   "days_logged": N,
        #   "consistency": percentage,
        #   "top_foods": [...]
        # }
    
    @staticmethod
    def get_daily_breakdown(db, user_id, start_date, end_date) → list[dict]
        # Return daily totals for each day in range
        # [{date, calories, protein_g, carbs_g, fat_g}, ...]
    
    @staticmethod
    def get_user_targets(db, user_id) → dict
        # Fetch personalized targets from UserProfile
```

**Tests:**
- Test weekly stats calculation
- Test daily breakdown accuracy
- Test consistency percentage
- Test with empty data
- Test with partial week

---

## Phase 2: Analytics API Endpoint (Day 1)

**File:** `src/api/analytics.py`

Endpoint:
```
GET /api/v1/analytics/summary?period=week&date=2026-06-14

Response:
{
  "period": "week",
  "start_date": "2026-06-08",
  "end_date": "2026-06-14",
  "days_logged": 6,
  "total_days": 7,
  "consistency": 85.7,
  "calories": {
    "total": 12950,
    "average": 1850,
    "target": 2000,
    "percentage": 92.5
  },
  "protein_g": { "total": 840, "average": 120, "target": 150, "percentage": 80 },
  "carbs_g": { "total": 1260, "average": 180, "target": 200, "percentage": 90 },
  "fat_g": { "total": 420, "average": 60, "target": 65, "percentage": 92 },
  "daily_breakdown": [
    { "date": "2026-06-08", "calories": 1950, "protein_g": 125, "carbs_g": 185, "fat_g": 62 },
    ...
  ],
  "top_foods": [
    { "food": "Chicken Breast", "count": 4, "calories": 1000 },
    { "food": "Noodles", "count": 3, "calories": 1200 }
  ]
}
```

**Features:**
- Authenticated (requires JWT token)
- Flexible date range (end_date defaults to today)
- Automatic target calculation
- Edge case handling

---

## Phase 3: iOS WeeklyNutritionView (Days 2-3)

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

## Phase 4: Data Visualization Components (Days 3-4)

**Files:**
- `WeeklyChart.swift` — Bar/line chart for daily calories
- `MacroBreakdown.swift` — Pie chart for protein/carbs/fat split

**Features:**
- Smooth animations
- Color-coded zones
- Responsive to screen size
- Accessible (VoiceOver support optional)

---

## Phase 5: Integration & Polish (Day 5)

**Modify:** `ContentView.swift`
- Add new tab: WeeklyNutritionView
- Icon: 📊 (chart.bar.fill)
- Position: Between Food Diary and Settings

**Testing:**
- Run on simulator
- Test week navigation
- Verify data matches backend
- Edge cases: new user, no logs, future date
- No crashes, no console errors

---

## Architecture: Data Flow

```
iOS App
  ↓
WeeklyNutritionViewModel.loadWeeklyStats()
  ↓
APIClient.get(/api/v1/analytics/summary?period=week&date=...)
  ↓
FastAPI Analytics Endpoint
  ↓
AnalyticsRepository.get_weekly_stats()
  ↓
SQLAlchemy Query → FoodLog table
  ↓
Aggregate data + fetch targets
  ↓
Build AnalyticsSummaryResponse
  ↓
Return JSON to iOS
  ↓
WeeklyNutritionView renders with data
```

---

## Performance Targets

- API response time: < 200ms
- View rendering: smooth 60 FPS
- No N+1 queries
- No memory leaks with large datasets

---

## Testing Checklist

- [ ] Backend tests pass (8+ test cases)
- [ ] API endpoint returns correct data
- [ ] iOS view renders without errors
- [ ] Week navigation works
- [ ] Edge cases handled (empty week, new user, future date)
- [ ] No console errors
- [ ] Animations smooth
- [ ] Responsive on all screen sizes
