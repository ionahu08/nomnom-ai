# Iteration 18: Weekly Nutrition Summary

**Duration:** 5 days  
**Status:** 🚀 Starting (June 15, 2026)

---

## Goal

Add a new **"Weekly Summary"** screen between Food Diary and Settings tabs that displays:
- Weekly calorie intake visualization (total, average, vs. target)
- Nutrient composition breakdown (Protein, Carbs, Fat)
- Daily consistency metrics
- Trending/insights about user's eating patterns

---

## What's Already Built

✅ **Iteration 17 — Personalized Nutrition Profile**
- Backend: ProfileService with personalized calorie/macro targets
- iOS: Settings screen with health data input
- Targets based on age, weight, activity, goal

✅ **Iteration 16 — MCP Server**
- Backend infrastructure for food analysis
- API endpoints for food logs and profiles

---

## What We're Building

### 1. **Backend: Weekly Analytics API** (Day 1)
- Endpoint: `GET /api/v1/analytics/summary?period=week&date=YYYY-MM-DD`
- Returns:
  - Weekly total/average calories, protein, carbs, fat
  - Daily breakdown for the week
  - Consistency percentage (days logged / 7)
  - Top foods eaten during the week
  - Comparison vs. user's targets

### 2. **iOS: Weekly Summary Screen** (Days 2-3)
- New tab view: 📊 Weekly Summary (between Diary and Settings)
- Display period selector (current week, last week, etc.)
- Charts/visualizations:
  - Calorie intake over 7 days (bar chart or line chart)
  - Macro composition (pie chart or horizontal bars)
  - Daily streak indicator
  - Achievement badges (e.g., "Stayed under target 5 days")

### 3. **Data Visualization** (Days 4-5)
- Smooth animations when switching weeks
- Color-coded zones (green=on-track, yellow=slightly over, red=significantly over)
- Responsive layout for all screen sizes
- Edge case handling (new user, incomplete weeks, no logs)

---

## Success Criteria

- ✅ Backend analytics endpoint working (tested with curl)
- ✅ iOS tab shows weekly summary data
- ✅ Visualizations render correctly on simulator
- ✅ Week navigation works (prev/next week, pick any week)
- ✅ All tests pass
- ✅ No console errors or crashes

---

## Commit Strategy

- Day 1: Backend analytics repository + API endpoint
- Day 2: iOS SummaryView + ViewModel
- Day 3: Data visualization components
- Day 4-5: Polish, testing, edge cases

---

## Related Files (To Create/Modify)

**Backend:**
- `src/repositories/analytics_repository.py` (NEW)
- `src/api/analytics.py` (NEW)
- `src/schemas/analytics.py` (NEW)
- `tests/test_analytics.py` (NEW)

**iOS:**
- `NomNom-iOS/NomNom/Features/WeeklyNutrition/WeeklyNutritionView.swift` (NEW)
- `NomNom-iOS/NomNom/Features/WeeklyNutrition/WeeklyNutritionViewModel.swift` (NEW)
- `NomNom-iOS/NomNom/Core/Components/WeeklyChart.swift` (NEW)
- `NomNom-iOS/NomNom/Core/Components/MacroBreakdown.swift` (NEW)
- `NomNom-iOS/NomNom/App/ContentView.swift` (MODIFY — add new tab)

---

## Next Iteration (19)

**Eating Insights with Claude**
- Use weekly summary data as input
- Call Claude to generate personalized recommendations
- Display insights: "What went well", "Areas to improve", "Specific actions"
