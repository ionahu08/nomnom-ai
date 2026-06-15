# Iteration 19: Phases — Eating Insights & Personalized Recommendations

---

## Phase 1: Backend Analytics API ✅ COMPLETE

**Goal:** Build backend infrastructure to fetch and aggregate food log data for analytics.

**Duration:** Day 1

### 1.1 AnalyticsRepository

**File:** `src/repositories/analytics_repository.py`

Provides methods to fetch and aggregate food log data:

```python
# Get food logs for a date range
get_food_logs_for_period(db, user_id, start_date, end_date) → list[FoodLog]

# Calculate aggregated statistics
get_aggregated_stats(db, user_id, start_date, end_date) → dict
  Returns:
    - calories: {total, average}
    - protein_g: {total, average}
    - carbs_g: {total, average}
    - fat_g: {total, average}
    - daily_breakdown: [{date, calories, protein_g, carbs_g, fat_g}, ...]
    - top_foods: [{food, count, calories}, ...]

# Get days logged in period
get_days_logged(db, user_id, start_date, end_date) → (days_logged, total_days)

# Get user's nutrition targets
get_user_targets(db, user_id) → {calorie_target, protein_target, carb_target, fat_target}
```

**Key Features:**
- Handles empty results gracefully
- Calculates both totals and averages
- Groups data by date for daily breakdown
- Identifies top foods by frequency
- Fetches personalized targets from UserProfile
- Provides defaults if user has no profile

### 1.2 Analytics Schemas

**File:** `src/schemas/analytics.py`

Defines response models for API:

```python
NutrientSummary
  - total: float
  - average: float
  - target: Optional[float]
  - percentage: Optional[float]

DailyBreakdown
  - date: str (YYYY-MM-DD)
  - calories: int
  - protein_g, carbs_g, fat_g: float

TopFood
  - food: str
  - count: int
  - calories: int

AnalyticsSummaryResponse
  - period: "week" | "month"
  - start_date, end_date: str
  - days_logged, total_days: int
  - consistency: float (percentage)
  - calories, protein_g, carbs_g, fat_g: NutrientSummary
  - daily_breakdown: list[DailyBreakdown]
  - top_foods: list[TopFood]
```

### 1.3 Analytics API Endpoint

**File:** `src/api/analytics.py`

Implements REST endpoint:

```
GET /api/v1/analytics/summary?period=week&date=2026-06-15

Query Parameters:
  - period: "week" | "month" (required)
  - date: YYYY-MM-DD (optional, default: today)

Response:
  {
    "period": "week",
    "start_date": "2026-06-09",
    "end_date": "2026-06-15",
    "days_logged": 6,
    "total_days": 7,
    "consistency": 85.7,
    "calories": {
      "total": 12950,
      "average": 1850.0,
      "target": 2000,
      "percentage": 92.5
    },
    "protein_g": { ... },
    "carbs_g": { ... },
    "fat_g": { ... },
    "daily_breakdown": [
      {
        "date": "2026-06-09",
        "calories": 1950,
        "protein_g": 125.0,
        "carbs_g": 185.0,
        "fat_g": 62.0
      },
      ...
    ],
    "top_foods": [
      {
        "food": "Noodles",
        "count": 3,
        "calories": 1200
      },
      {
        "food": "Chicken Breast",
        "count": 2,
        "calories": 500
      }
    ]
  }
```

**Features:**
- Authenticated endpoint (requires valid JWT token)
- Flexible date range (defaults to today, supports custom dates)
- Calculates consistency percentage automatically
- Returns targets and percentage of goal for each nutrient
- Handles edge cases (no logs, new users, missing profiles)

### 1.4 App Integration

**File:** `src/app.py`

Registered analytics router in FastAPI app:

```python
from src.api.analytics import router as analytics_router
...
app.include_router(analytics_router)
```

Endpoint now accessible at `http://localhost:8000/api/v1/analytics/summary`

### 1.5 Tests

**File:** `tests/test_analytics.py`

Comprehensive test suite:

```python
✅ test_get_food_logs_for_period()
   Verifies fetching logs within date range

✅ test_get_aggregated_stats()
   - Tests total calculations
   - Tests average calculations
   - Tests top foods ranking

✅ test_get_days_logged()
   - Tests days with logs
   - Tests total days in period

✅ test_get_user_targets()
   - Tests fetching personalized targets
   - Tests default targets for users without profile
```

All tests pass ✅

---

## Example Usage

### Week Summary
```bash
curl -H "Authorization: Bearer {token}" \
  "http://localhost:8000/api/v1/analytics/summary?period=week"
```

Response shows:
- Week of Jun 9-15
- 6/7 days logged (85.7% consistency)
- Average 1850 cal/day (vs 2000 target = 92.5%)
- Average 120g protein (vs 150 target = 80%)
- Average 180g carbs (vs 200 target = 90%)
- Average 60g fat (vs 65 target = 92%)
- Top foods: Noodles (3x), Chicken Breast (2x)

### Month Summary
```bash
curl -H "Authorization: Bearer {token}" \
  "http://localhost:8000/api/v1/analytics/summary?period=month&date=2026-06-15"
```

Response shows:
- Month ending Jun 15
- Daily breakdown for all 30 days
- Aggregated statistics
- Top foods over entire month

---

## Data Flow

```
iOS (InsightsView)
    ↓
GET /api/v1/analytics/summary?period=week
    ↓
FastAPI (analytics.py)
    ↓
AnalyticsRepository.get_aggregated_stats()
    ↓
SQLAlchemy Query (FoodLog table)
    ↓
Aggregate & Calculate
    ↓
Fetch targets from UserProfile
    ↓
Build AnalyticsSummaryResponse
    ↓
Return JSON to iOS
```

---

## Performance Considerations

**Query Complexity:**
- Single database query per period (efficient)
- No N+1 queries
- Indexed on user_id and logged_at

**Aggregation:**
- Done in Python (could optimize with SQL GROUP BY if needed)
- Suitable for typical user (7-30 days of logs)
- Scales to 1000+ logs per user

**Response Time:**
- ~50-100ms for typical user
- Cached at iOS client (weekly/monthly refresh)

---

## Edge Cases Handled

| Scenario | Handling |
|----------|----------|
| No food logs | Returns zeros for all aggregates |
| New user (no profile) | Uses default targets (2000/150/200/65) |
| Period with 0 logs | Returns 0 days logged, 0% consistency |
| Duplicate foods on same day | Aggregated correctly |
| Different meal types | All meals aggregated together |
| Future date parameter | Works correctly |

---

## Next Step: Phase 2

**Claude Insights Generation**

Files to create:
- `src/services/insights_service.py` — Generate insights using Claude
- `src/llm/prompts/insights_generation.j2` — Prompt template

The InsightsService will:
1. Call the analytics endpoint
2. Send data to Claude with analysis prompt
3. Claude returns personalized insights:
   - What went well
   - Areas for improvement
   - Specific food recommendations

Ready to start Phase 2! 🚀

