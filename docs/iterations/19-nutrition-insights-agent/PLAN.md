# Iteration 19: AI Nutrition Insights & Food Recommendations

**Dates:** June 16-22, 2026 (est.)  
**Status:** PLANNING  
**Goal:** Replace static nutrition summary with an intelligent AI agent that analyzes user's past eating patterns and provides personalized food recommendations based on health profile, allergies, and medical conditions.

---

## Executive Summary

Currently the Insight tab displays raw nutrition data (charts, consistency, targets, top foods). This iteration replaces the static sections with a conversational AI agent that:

1. **Analyzes** past 1 day, 1 week, and 1 month food intake
2. **Evaluates** nutrient gaps (what the user had enough of, what they lacked)
3. **Recommends** specific foods to eat more based on:
   - Past eating preferences (what they've logged before)
   - Health goals (lean out, gain muscle, maintain, lose weight)
   - Medical history (allergies, conditions)
   - Macro/micro nutrient targets
4. **Explains** findings in conversational language

**Outcome:** Users get actionable, personalized nutrition guidance instead of static charts.

---

## What's Being Built

### Phase 1: Backend Nutrition Insights API (Days 1-2)

**New Endpoint:** `GET /api/v1/nutrition/insights`

Parameters:
- `period` (optional, default "week"): "day" | "week" | "month"
- Returns aggregated data for all three periods (1d, 1w, 1m) at once

Response structure:
```json
{
  "periods": {
    "day": {
      "start_date": "2026-06-15",
      "end_date": "2026-06-16",
      "calories": {"total": 1950, "target": 2000, "percentage": 97.5},
      "protein": {"total": 125, "target": 150, "percentage": 83.3},
      "carbs": {"total": 210, "target": 200, "percentage": 105},
      "fat": {"total": 65, "target": 65, "percentage": 100},
      "foods": ["Chicken breast", "Rice", "Broccoli", ...]
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
  "analysis": {
    "summary": "You're doing great with protein this week, but carbs are running 10% high.",
    "strengths": ["Consistent protein intake", "Good variety of vegetables"],
    "gaps": ["Low iron-rich foods", "Missing omega-3 sources"],
    "recommendations": [
      {
        "nutrient": "Iron",
        "foods": ["Spinach", "Lean beef", "Fortified cereals"],
        "reasoning": "You've logged almost no iron-rich foods this week, consider adding one spinach-based meal"
      }
    ]
  }
}
```

**Data Flow:**
1. Fetch analytics data for 1 day, 1 week, 1 month (reuse existing `/summary` endpoint)
2. Fetch user health profile
3. Call Claude API with:
   - All three period summaries
   - Health profile + allergies + conditions
   - Food logs from each period
   - User's macro/micro targets
4. Parse Claude's response into structured recommendations
5. Return to iOS

### Phase 2: LLM Agent (Nutrition Analysis & Recommendations) (Days 2-3)

**Component:** `NomNomBackend/src/llm/nutrition_agent.py` (new)

Responsibilities:
- Takes nutrition data (periods, health profile, food logs)
- Calls Claude API with system prompt designed for nutrition analysis
- Extracts and structures the response
- Returns: summary, strengths, gaps, specific food recommendations

**System Prompt Design:**
```
You are a nutritionist assistant for a food tracking app. Analyze the user's 
eating patterns and provide personalized feedback.

For each recommendation:
- What nutrient/food category is missing?
- Why it matters for their goal (e.g., "lean_out")
- 2-3 specific foods they haven't tried yet based on their past logs
- How to integrate into meals (e.g., "Add a handful of spinach to breakfast")

Consider:
- User's goal (lean_out, gain_muscle, maintain, lose_weight)
- Allergies and medical conditions (skip these foods entirely)
- Past 1-month eating history (recommend foods they've shown they like)
- All three periods (day, week, month trends)

Output format: JSON with summary, strengths, gaps, recommendations array
```

**Key Design Choices:**
1. **Always return structured JSON** — allows iOS to display recommendations reliably
2. **Personalize to past eating** — don't recommend foods they've never logged
3. **Respect constraints** — never suggest foods matching their allergies or conflicting with conditions
4. **Focus on gaps** — identify what's missing, not what they're doing right
5. **Connect to goals** — explain why each recommendation matters for *their* goal

### Phase 3: iOS Insight Tab Redesign (Days 3-4)

**Changes to WeeklyNutritionView:**

1. **Remove sections:**
   - Logging Consistency progress bar (currently at top)
   - Daily Targets card (Protein/Carbs/Fat with emoji)
   - Top Foods section (currently at bottom)

2. **Add AI Insights Component** (new, between Calories chart and removed sections)
   
   **Location:** Right after the 4 line charts (Calories, Protein, Carbs, Fat)
   
   **Component:** `NutritionInsightsCard.swift`
   
   **States:**
   - Loading: "Analyzing your nutrition..." with spinner
   - Error: "Failed to load insights"
   - Ready: Display summary + recommendations
   
   **Layout:**
   ```
   ┌─────────────────────────────┐
   │ 💡 Your Nutrition Insights  │
   ├─────────────────────────────┤
   │ Summary (1-2 sentences)     │
   │                             │
   │ 💪 What You're Doing Well   │
   │ • Consistent protein intake │
   │ • Good vegetable variety    │
   │                             │
   │ ⚠️  Gaps to Address         │
   │ • Low iron-rich foods       │
   │ • Missing omega-3 sources   │
   │                             │
   │ 🍎 Recommendations          │
   │ [Expandable cards per rec]  │
   │ • Add spinach to breakfast  │
   │ • Try salmon for omega-3    │
   └─────────────────────────────┘
   ```

3. **Updated ViewModel Logic:**
   - `loadNutritionInsights()` → calls new `/nutrition/insights` endpoint
   - Stores insights in `@Published var insights: NutritionInsights?`
   - Handles loading/error states
   - Fetches automatically when period changes (or on demand)

---

## Prerequisite Work (Already Complete)

✅ Iteration 18: Analytics API returns multi-period data  
✅ User profiles store health data (allergies, conditions, goals)  
✅ Phase 6: MCP server exists (could extend this, but API endpoint is simpler)  
✅ Claude API integration proven (existing calls in ai_service.py)  

---

## Success Criteria

- [ ] Backend `/nutrition/insights` endpoint returns structured recommendations
- [ ] iOS renders insights card with loading/error/ready states
- [ ] Recommendations are personalized (past foods, health profile respected)
- [ ] Allergies and medical conditions excluded from food suggestions
- [ ] App shows insights for day/week/month views
- [ ] Removed sections (consistency, targets, top foods) no longer visible
- [ ] All existing tests pass; no regressions
- [ ] Insight card appears within 2 seconds (P95 latency < 3s)
- [ ] Claude call respects token budget (under $0.10/call typical)

---

## Scope & Out of Scope

### In Scope
- AI agent for nutrition analysis
- Personalized food recommendations
- Respect health constraints (allergies, conditions)
- Clean UI card with loading states
- Integration with existing analytics data

### Out of Scope (Future Iterations)
- Recipe generation ("How do I cook salmon?")
- Meal plan builder (multi-day planning)
- Supplement recommendations (pharmaceutical-level guidance)
- Store/barcode integration (buying links)
- Social features (share recommendations)

---

## Architecture: Data Flow

```
iOS Insight Tab
    ↓
[Period Changes OR View Loads]
    ↓
WeeklyNutritionViewModel.loadNutritionInsights()
    ↓
APIClient.get(/api/v1/nutrition/insights?period=week)
    ↓
FastAPI Analytics Endpoint
    ├─ Fetch 3-period summary (1d, 1w, 1m)
    ├─ Fetch user health profile
    ├─ Fetch food logs for each period
    └─ Call LLM Agent
    
LLM Agent (nutrition_agent.py)
    ├─ Claude system prompt: "You are a nutritionist..."
    ├─ Input: All period data + health profile + food logs
    └─ Output: {summary, strengths, gaps, recommendations}
    
FastAPI → iOS
    ↓
NutritionInsightsCard renders:
├─ Summary text
├─ Strengths bullets
├─ Gaps bullets
└─ Recommendations (expandable cards)
```

---

## Estimated Effort

| Phase | Duration | Status |
|-------|----------|--------|
| Backend API | 1.5 days | Pending |
| LLM Agent | 1.5 days | Pending |
| iOS UI + Integration | 1.5 days | Pending |
| Testing + Polish | 1 day | Pending |
| **Total** | **5-6 days** | - |

---

## File Changes Summary

### Backend (New/Modified)

| File | Type | Purpose |
|------|------|---------|
| `src/api/nutrition_insights.py` | NEW | FastAPI endpoint for /nutrition/insights |
| `src/llm/nutrition_agent.py` | NEW | Claude-powered analysis + recommendations |
| `src/schemas/nutrition_insights.py` | NEW | Pydantic models for request/response |

### iOS (New/Modified)

| File | Type | Purpose |
|------|------|---------|
| `NomNomInsightsCard.swift` | NEW | Card UI for insights + recommendations |
| `NomNomInsightsViewModel.swift` | MODIFY | Add loadNutritionInsights() method |
| `WeeklyNutritionView.swift` | MODIFY | Remove consistency/targets/topFoods, add card |

---

## Questions for Review

1. **Streaming vs. Batch?** Return all insights at once, or stream recommendations as they're generated?
   - Suggested: Batch (simpler, faster for 3-4 recommendations)

2. **Cache Insights?** Should insights be cached and reused until food logs change?
   - Suggested: No cache (insights should be fresh, but add cache if latency becomes issue)

3. **Per-recommendation Details?** Should each recommendation be expandable with more explanation?
   - Suggested: Yes, use collapsible sections to keep UI clean

4. **Tone/Personality?** Should the agent's voice match the cat personality?
   - Suggested: Use user's selected cat style in system prompt (e.g., "Be sassy but helpful" for sassy cat)

---

## Testing Strategy

### Backend Tests
- [ ] `/nutrition/insights` returns valid JSON structure
- [ ] Respects user privacy (only returns own data)
- [ ] Handles missing health profile gracefully
- [ ] Recommendations don't include allergens
- [ ] Response includes all 3 periods (day/week/month)

### iOS Tests
- [ ] Card loads and displays when data arrives
- [ ] Loading state shows spinner
- [ ] Error state displays error message
- [ ] Period changes trigger new insights fetch
- [ ] Removed sections are gone (consistency, targets, top foods)

### Integration Tests
- [ ] Analytics endpoint → Insights endpoint happy path
- [ ] Claude API call succeeds with valid prompt
- [ ] Token usage is reasonable (<500 tokens typical)
- [ ] End-to-end latency acceptable (<3 seconds P95)

---

## Next Steps

1. **Design review:** Confirm plan with team/user
2. **Phase 1 kickoff:** Build backend endpoint + schemas
3. **Phase 2 kickoff:** Build LLM agent with system prompt
4. **Phase 3 kickoff:** Build iOS UI components
5. **Integration & testing:** Connect everything, verify success criteria
6. **Documentation:** PHASES.md, BUGLOG.md, SUMMARY.md on completion

---

**Ready to start Phase 1?**
