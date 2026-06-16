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

## Phase 2: LLM Nutrition Agent (Days 2-3) ✅ COMPLETE

**Goal:** Create Claude-powered agent that analyzes nutrition data and generates personalized recommendations.

**Status:** COMPLETE

### Files Created

1. **`src/llm/nutrition_agent.py`** (NEW)
   - `NutritionAgent` class with Claude API integration
   - `analyze_and_recommend()` method that:
     - Takes multi-period nutrition data + health profile
     - Calls Claude API with customized system prompt
     - Parses JSON response into structured analysis
     - Returns NutritionAnalysis object
   - Helper methods:
     - `_get_system_prompt()` — Build personalized system prompt based on user's goal and constraints
     - `_build_context()` — Format nutrition data for Claude
     - `_parse_response()` — Parse Claude's JSON response
     - `_get_goal_context()` — Convert goal codes to human-readable text

2. **`src/api/nutrition_insights.py`** (MODIFIED)
   - Added import: `from src.llm.nutrition_agent import get_nutrition_agent`
   - Updated endpoint to call agent: `analysis = await agent.analyze_and_recommend(periods, health_profile)`
   - Now returns populated `analysis` field instead of `null`
   - Added error handling if agent fails (returns None)

### Implementation Details

**Agent Prompt Design:**
- System prompt is customized per user based on their goal (lean_out, gain_muscle, maintain, lose_weight)
- Instructs Claude to:
  - Analyze past 1d/1w/1m eating patterns
  - Identify what they're doing well (strengths)
  - Identify nutrient gaps
  - Recommend 3-5 specific foods for improvement
  - NEVER recommend foods matching allergies or medical conflicts
  - Base recommendations on foods they've already logged
  - Connect recommendations to their specific goal

**Response Format (JSON):**
```json
{
  "summary": "One or two sentences about their overall nutrition status",
  "strengths": [
    "Thing they're doing well #1",
    "Thing they're doing well #2"
  ],
  "gaps": [
    "Nutrient gap #1",
    "Nutrient gap #2"
  ],
  "recommendations": [
    {
      "nutrient": "Iron-rich foods",
      "foods": ["Spinach", "Lean beef", "Fortified cereals"],
      "reasoning": "Why this matters for their goal"
    }
  ]
}
```

**Key Features:**
- Uses Claude Opus 4.7 for best reasoning quality (nutrition analysis is complex)
- Limits output to 1024 tokens (~350-400 words)
- Handles JSON parsing robustness (extracts from markdown if needed)
- Logs errors and returns None gracefully if LLM call fails
- Singleton agent pattern for efficient reuse

### Testing Notes

- Endpoint now takes ~1-2s longer (LLM call time)
- If Claude fails, endpoint still returns data (with analysis=None)
- All user constraints (allergies, conditions) properly passed to prompt
- Response is deterministic JSON (not streaming)
- Respects ANTHROPIC_API_KEY environment variable

### Cost Estimate

- Per call: ~200-300 input tokens, ~100-150 output tokens
- Claude Opus pricing: ~$3/MTok input, ~$15/MTok output
- Estimated cost per call: ~$0.001-$0.002 (roughly $0.0015 average)

---

## Phase 3: iOS Insight Tab Redesign (Days 3-4) ✅ COMPLETE

**Goal:** Update iOS Insight tab to display new AI insights card instead of static sections.

**Status:** COMPLETE

### Files Created

1. **`NutritionInsightsCard.swift`** (NEW)
   - Standalone component for displaying nutrition insights
   - Displays:
     - Summary text (1-2 sentences about nutrition status)
     - "What You're Doing Well" section (strengths with star icons)
     - "Areas to Improve" section (gaps with warning icons)
     - "Recommendations" section with expandable cards
   - Each recommendation shows:
     - Nutrient category
     - Suggested foods
     - Reasoning (expandable)
   - Visual design:
     - Orange lightbulb icon for the card title
     - Green checkmark icons for strengths
     - Orange warning icons for gaps
     - Green fork/knife icon for recommendations
     - Expandable recommendation cards with smooth animations

### Files Modified

1. **`WeeklyNutritionView.swift`** (MODIFIED)
   - Removed: Logging Consistency progress bar section
   - Removed: Daily Targets section (Protein/Carbs/Fat with emoji)
   - Removed: Top Foods section
   - Added: NutritionInsightsCard display (between charts and end)
   - Updated: .task block to load nutrition insights
   - Kept: 4 line charts (Calories, Protein, Carbs, Fat) with target reference lines

2. **`WeeklyNutritionViewModel.swift`** (MODIFIED)
   - Added: @Published var nutritionInsights: NutritionInsights?
   - Added: loadNutritionInsights() async method
   - Added: New data models (NutritionInsightsResponse, NutritionInsights, RecommendationItem)
   - Models defined in ViewModel for easy sharing across views

### UI Layout

New Insight Tab Structure:
```
┌─────────────────────────────┐
│ Period Selector [W][M][6M]  │
├─────────────────────────────┤
│ Date Navigation             │
├─────────────────────────────┤
│ Calories Line Chart         │
│ Protein Line Chart          │
│ Carbs Line Chart            │
│ Fat Line Chart              │
├─────────────────────────────┤
│ 💡 Your Nutrition Insights  │
│                             │
│ [Summary text]              │
│                             │
│ ✅ What You're Doing Well   │
│ • Item 1                    │
│ • Item 2                    │
│                             │
│ ⚠️  Areas to Improve        │
│ • Gap 1                     │
│ • Gap 2                     │
│                             │
│ 🍴 Recommendations          │
│ [Expandable cards]          │
└─────────────────────────────┘
```

### Removed Sections

1. ✂️ **Logging Consistency** — Progress bar showing days logged
2. ✂️ **Daily Targets** — Protein/Carbs/Fat summary cards with emoji
3. ✂️ **Top Foods** — List of most-eaten foods during period

These were replaced with intelligent AI-generated insights.

### API Integration

- Endpoint called: `GET /api/v1/nutrition/insights`
- Called after `loadWeeklySummary()` completes
- Gracefully handles failures (insights optional, summary required)
- Loading state not shown (happens in background, insights populate when ready)

### Testing Notes

- Card displays correctly when insights are loaded
- Card hidden if insights are nil (API failure)
- Expandable recommendations work with smooth animations
- All 3 period types (week/month/6m) fetch fresh insights
- Changing periods re-fetches insights

### Performance

- Insights load asynchronously in background
- Does not block UI while fetching (~1-2 seconds)
- Graceful degradation if LLM fails

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
| c197491 | feat(iter19-phase1): Create nutrition insights endpoint and schemas |
| 8689855 | feat(iter19-phase2): Add LLM nutrition agent with Claude analysis |
| TBD | feat(iter19-phase3): Add iOS nutrition insights card and remove old sections |

