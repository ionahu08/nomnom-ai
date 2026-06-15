# Iteration 19: Eating Insights & Personalized Recommendations

**Duration:** 5 days  
**Start Date:** 2026-06-15  
**Status:** 🚀 Planning

---

## Goal

Create an **Insights** tab that analyzes user eating patterns, identifies habits/shortcomings, and provides personalized weekly/monthly recommendations using Claude AI to generate intelligent insights.

---

## What's Already Built

✅ **Iteration 17 — Personalized Nutrition Profile**
- Health profile API with personalized daily targets
- TDEE calculations, macro splits
- Settings screen to input health data

✅ **Iteration 18 — Food Diary Visualization**
- Food Diary screen with real-time nutrition tracking
- Daily calorie and macro progress displays
- Food log data in database

✅ **Food Log Data**
- `food_logs` table with calories, protein, carbs, fat per entry
- Historical data available for analysis

---

## What We're Building

### 1. **Insights Tab (iOS)**
- New tab inserted between Food Diary and Settings
- Toggle between Weekly and Monthly views
- Display aggregated nutrition data
- Show analysis and recommendations

### 2. **Analytics Backend API**
- Endpoint: `GET /api/v1/analytics/summary?period=week|month`
- Returns:
  - Aggregated calories, protein, carbs, fat
  - Comparison to targets
  - Daily averages
  - Consistency metrics (days logged)

### 3. **Insights Generation (Claude)**
- Analyze eating patterns
- Detect habits and shortcomings
- Generate weekly/monthly summary
- Provide food recommendations

### 4. **Insights Service**
- Fetch food logs for period
- Calculate aggregated statistics
- Call Claude to generate insights
- Format recommendations

---

## Feature Breakdown

### Screen 1: Insights Tab UI
```
┌─────────────────────────────┐
│ 📊 Insights                 │
├─────────────────────────────┤
│ [Weekly] [Monthly]          │  ← Toggle
├─────────────────────────────┤
│                             │
│ SUMMARY (Week of Jun 9-15)  │
│ ─────────────────────────   │
│ Avg Calories: 1850 / 2000   │
│ Avg Protein:  120g / 150g   │
│ Avg Carbs:    180g / 200g   │
│ Avg Fat:      60g / 65g     │
│                             │
│ Consistency: 6/7 days       │
│ logged                       │
├─────────────────────────────┤
│ 💡 INSIGHTS & RECOMMENDATIONS
│                             │
│ What Went Well:             │
│ ✅ Consistent logging       │
│ ✅ Met calorie targets      │
│ ✅ Good protein intake      │
│                             │
│ Areas for Improvement:      │
│ ⚠️  Low in fiber            │
│ ⚠️  Too many simple carbs   │
│    (noodles 5/7 days)       │
│                             │
│ Recommendation:             │
│ Add more whole grains.      │
│ Try: Brown rice, quinoa,    │
│ whole wheat pasta           │
│                             │
└─────────────────────────────┘
```

### Data Flow
```
Food Diary (past 7/30 days)
    ↓
Analytics Backend
    ↓
Aggregate stats (sum, avg, consistency)
    ↓
Claude Insight Generation
    ├─ Analyze patterns
    ├─ Compare to targets
    ├─ Identify habits
    └─ Generate recommendations
    ↓
iOS Insights Screen
    ↓
Display formatted insights + recommendations
```

---

## Success Criteria

- ✅ Insights tab displays between Diary and Settings
- ✅ Toggle between Weekly and Monthly views works
- ✅ Summary statistics calculated correctly
- ✅ Claude generates personalized insights (what went well, areas for improvement)
- ✅ Food recommendations include specific foods rich in lacking nutrients
- ✅ Handles edge cases (not enough data, no logs, new users)
- ✅ Loading states and error handling
- ✅ Responsive on all iPhone sizes

---

## Technical Architecture

### Backend Changes
**New API Endpoint:**
```
GET /api/v1/analytics/summary
Query params:
  - period: "week" | "month"
  - date: ISO date (end date of period, default: today)

Response:
{
  "period": "week",
  "start_date": "2026-06-09",
  "end_date": "2026-06-15",
  "days_logged": 6,
  "total_days": 7,
  "aggregated": {
    "calories": {
      "total": 12950,
      "average": 1850,
      "target": 2000,
      "percentage": 92.5
    },
    "protein": {
      "total": 840,
      "average": 120,
      "target": 150,
      "percentage": 80
    },
    "carbs": {
      "total": 1260,
      "average": 180,
      "target": 200,
      "percentage": 90
    },
    "fat": {
      "total": 420,
      "average": 60,
      "target": 65,
      "percentage": 92
    }
  },
  "daily_breakdown": [
    { "date": "2026-06-09", "calories": 1950, "protein": 125, ... },
    ...
  ],
  "top_foods": [
    { "food": "Chicken Breast", "count": 4, "calories": 800 },
    { "food": "Noodles", "count": 5, "calories": 1200 },
    ...
  ]
}
```

**New Service Layer:**
- `InsightsService` — Fetch analytics + call Claude
- `AnalyticsRepository` — Query food logs, aggregate data

### Claude Integration

**Prompt Template:**
```
You are a nutrition coach analyzing eating patterns.

User's Target Nutrition:
- Daily Calories: 2000
- Protein: 150g
- Carbs: 200g
- Fat: 65g

Weekly Summary (Jun 9-15):
- Average Calories: 1850 / 2000 (92.5%)
- Average Protein: 120 / 150g (80%)
- Average Carbs: 180 / 200g (90%)
- Average Fat: 60 / 65g (92%)
- Days Logged: 6/7

Top Foods This Week:
- Chicken Breast (4x) - 800 cal
- Noodles (5x) - 1200 cal
- Broccoli (3x) - 150 cal

Analyze this eating pattern and provide:
1. What went well (2-3 positive observations)
2. Areas for improvement (2-3 shortcomings)
3. Specific nutrient recommendations
4. Food suggestions to address deficiencies

Format as conversational, encouraging summary.
```

### iOS Changes

**New Views:**
- `InsightsView` — Main tab view
- `SummaryCard` — Statistics display
- `InsightsPanel` — Claude-generated recommendations
- `PeriodToggle` — Week/Month selector

**New ViewModels:**
- `InsightsViewModel` — Fetch data, manage state
- Analytics API client

**Tab Navigation:**
- Update `ContentView` to include Insights tab between Diary and Settings

---

## Phase Breakdown

### Phase 1: Backend Analytics API (Day 1)
- Create `AnalyticsRepository` to fetch and aggregate food logs
- Implement `/api/v1/analytics/summary` endpoint
- Test with sample data

### Phase 2: Insights Generation (Day 2)
- Create `InsightsService` 
- Integrate Claude for insight generation
- Test prompt with various eating patterns

### Phase 3: iOS UI (Days 3-4)
- Create `InsightsView` and sub-components
- Integrate `InsightsViewModel` with API client
- Add tab navigation
- Implement Weekly/Monthly toggle
- Add loading states and error handling

### Phase 4: Testing & Polish (Day 5)
- Test on device (visual appearance, responsiveness)
- Edge case testing (no data, new users)
- Performance optimization
- Light/Dark mode verification

---

## Files to Create

**Backend:**
- `src/repositories/analytics_repository.py`
- `src/services/insights_service.py`
- `src/api/analytics.py` (new endpoint)
- `src/llm/prompts/insights_generation.j2` (prompt template)

**iOS:**
- `NomNom-iOS/NomNom/Features/Insights/InsightsView.swift`
- `NomNom-iOS/NomNom/Features/Insights/InsightsViewModel.swift`
- `NomNom-iOS/NomNom/Core/Components/SummaryCard.swift`
- `NomNom-iOS/NomNom/Core/Components/InsightsPanel.swift`
- `NomNom-iOS/NomNom/Core/Services/InsightsAPIClient.swift`

**Documentation:**
- `docs/iterations/19-eating-insights/PLAN.md` (this file)
- `docs/iterations/19-eating-insights/PHASES.md`
- `docs/iterations/19-eating-insights/BUGLOG.md`
- `docs/iterations/19-eating-insights/SUMMARY.md`

---

## Resume Skills

- **Backend:** RESTful API design, data aggregation, time-series analysis
- **LLM:** Prompt engineering for analysis + recommendations
- **iOS:** New tab navigation, loading states, responsive layouts
- **Analytics:** Calculate trends, identify patterns, generate insights
- **Product Design:** User-focused recommendations, accessibility

---

## Notes

- Consider caching insights (recompute once per day)
- Handle case where user has <7 days of logs
- Edge case: New user with no food logs (show onboarding message)
- Use same color scheme for macro charts as Food Diary
- Insights should be encouraging (positive framing + actionable advice)

---

## Success Gates (End of Phase 4)

- ✅ Backend analytics API returns correct aggregated data
- ✅ Claude generates meaningful insights (not generic)
- ✅ Insights tab displays properly in tab bar
- ✅ Toggle between Weekly/Monthly works smoothly
- ✅ Food recommendations are specific and nutritionally sound
- ✅ Tested on 2+ device sizes
- ✅ No crashes or UI glitches
- ✅ Handles edge cases gracefully

---

## Interview Talking Point

"I built an Insights tab that analyzes user eating patterns and provides personalized recommendations. The system:

1. **Aggregates nutrition data** — Calculates weekly/monthly calories and macro totals, averages, and consistency
2. **Detects eating habits** — Identifies patterns like 'eating noodles 5 days in a row = high carbs, low protein'
3. **Uses Claude to generate insights** — Analyzes the data and writes a personalized summary
4. **Recommends specific foods** — Suggests foods rich in lacking nutrients

**Key insight:** Insights are most valuable when they're specific and personalized. Instead of 'eat more protein,' we tell users 'you're low on protein because you're eating noodles too often — try chicken breast, eggs, or Greek yogurt instead.'

**Architecture:** Food logs → analytics API → Claude → formatted recommendations → iOS display. The Claude integration makes insights conversational and encouraging rather than clinical."

