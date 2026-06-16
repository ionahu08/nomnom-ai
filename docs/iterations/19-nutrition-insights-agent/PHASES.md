# Iteration 19: Implementation Phases

---

## Phase 1: Backend Nutrition Insights API (Days 1-2) ✅ COMPLETE

**Goal:** Build the `/api/v1/nutrition/insights` endpoint that returns multi-period nutrition data and health profile.

**Status:** COMPLETE

### Files Created

1. **`src/schemas/nutrition_insights.py`** (NEW)
   - Pydantic models for request/response validation
   - Data classes:
     - `NutrientData` — total, target, percentage for each nutrient
     - `PeriodData` — 1 day, 1 week, 1 month summaries
     - `HealthProfile` — user goals, allergies, medical conditions, targets
     - `NutritionAnalysis` — summary, strengths, gaps, recommendations (Phase 2)
     - `NutritionInsightsResponse` — complete response structure

2. **`src/api/nutrition_insights.py`** (NEW)
   - FastAPI router with single endpoint: `GET /api/v1/nutrition/insights`
   - Fetches multi-period data (1d, 1w, 1m) in one call
   - Aggregates stats using existing AnalyticsRepository
   - Extracts health profile from user.profile
   - Returns structured response ready for Phase 2 LLM analysis

3. **`src/app.py`** (MODIFIED)
   - Added import: `from src.api.nutrition_insights import router as nutrition_insights_router`
   - Added to router list: `app.include_router(nutrition_insights_router)`

### Implementation Details

**Endpoint:** `GET /api/v1/nutrition/insights`

**Request:**
- Authentication: Bearer token (via `get_current_user` dependency)
- No query parameters needed (uses current date)

**Response Structure:**
```json
{
  "periods": {
    "day": {
      "start_date": "2026-06-15",
      "end_date": "2026-06-16",
      "calories": { "total": 1950, "target": 2000, "percentage": 97.5 },
      "protein": { "total": 125, "target": 150, "percentage": 83.3 },
      "carbs": { "total": 210, "target": 200, "percentage": 105 },
      "fat": { "total": 65, "target": 65, "percentage": 100 },
      "foods": [ "Chicken breast", "Rice", ... ]
    },
    "week": { ... },
    "month": { ... }
  },
  "health_profile": {
    "age": 28,
    "goal": "lean_out",
    "height_cm": 175,
    "weight_kg": 75,
    "allergies": ["peanuts", "shellfish"],
    "medical_conditions": ["hypertension"],
    "calorie_target": 2000,
    "protein_target": 150,
    "carb_target": 200,
    "fat_target": 65
  },
  "analysis": null  // Will be populated in Phase 2
}
```

**Key Design Choices:**
1. Fetches all 3 periods at once (more efficient than 3 separate requests)
2. Reuses existing `AnalyticsRepository` methods
3. Extracts top 20 unique foods from food logs
4. Returns structured data ready for LLM processing
5. Analysis field is `null` until Phase 2

### Testing Notes

- Endpoint requires valid auth token
- Returns 401 if token invalid/expired
- Returns structured data for all users (populated based on their food logs)
- Empty periods (no logs) still return nutrition structure with zeros
- Health profile can be partial (many fields are optional in DB)

---

## Phase 2: LLM Nutrition Agent (Days 2-3) 🚧 PENDING

**Goal:** Create Claude-powered agent that analyzes nutrition data and generates personalized recommendations.

**Placeholder:** Will be filled in during Phase 2

---

## Phase 3: iOS Insight Tab Redesign (Days 3-4) 🚧 PENDING

**Goal:** Update iOS Insight tab to display new AI insights card instead of static sections.

**Placeholder:** Will be filled in during Phase 3

---

## Architecture: Data Flow

```
iOS App
    ↓
APIClient.get(/api/v1/nutrition/insights)
    ↓
FastAPI: nutrition_insights.get_nutrition_insights()
    ├─ Fetch 3-period summary using AnalyticsRepository
    ├─ Calculate stats (total, target, percentage) for each nutrient
    ├─ Extract unique foods from food logs
    └─ Fetch user health profile
    
    ↓
Return NutritionInsightsResponse with:
    ├─ periods: day/week/month data
    ├─ health_profile: goals, allergies, conditions, targets
    └─ analysis: null (for Phase 2)
    
    ↓ [Phase 2: LLM Processing]
    
Response back to iOS
    ↓
iOS NutritionInsightsCard renders data
```

---

## Commits

| Hash | Message |
|------|---------|
| TBD | Phase 1: Create nutrition insights endpoint and schemas |

