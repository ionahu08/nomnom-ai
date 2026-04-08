# Iteration 08 — Meal Categorization

## Goals

Make the Today tab more organized by letting users tag each food entry as **Breakfast**, **Lunch**, **Dinner**, or **Snack**, then display logs grouped by meal category.

## What's Built (Prerequisites)

- Database migrations via Alembic
- Backend FastAPI endpoints for food log CRUD
- iOS models with Codable + CodingKey mapping
- Camera tab with food analysis UI
- Today tab showing flat list of logs

## What We're Building

1. **Database Column**: Add `meal_type` (string, nullable) to `food_logs` table
2. **Backend Schemas**: Add `meal_type` field to FoodLogCreate, FoodLogUpdate, FoodLogResponse
3. **Backend API**: Update PATCH endpoint to allow updating meal type (optional)
4. **iOS Model**: Add `mealType` to FoodLogCreate and FoodLogResponse structs
5. **CameraViewModel**: Add `selectedMealType` state, flow meal_type into POST payload
6. **CameraView**: Add segmented picker (Breakfast/Lunch/Dinner/Snack) before save button
7. **TodayView**: Group logs by meal category with section headers

## Resume Skills

- Alembic migrations (add columns to existing tables)
- Pydantic schema evolution (backward-compatible optional fields)
- SwiftUI segmented picker + state binding
- Dictionary grouping in Swift (group logs by meal_type)
- Section-based list layout in SwiftUI

## Success Criteria

- [ ] Alembic migration runs without error: `alembic upgrade head`
- [ ] Backend POST `/api/v1/food-logs/` accepts and stores `meal_type`
- [ ] Backend GET `/api/v1/food-logs/today` returns logs with `meal_type` populated
- [ ] iOS CameraView shows segmented picker (4 options) before save
- [ ] User can select meal type, tap Save, log is created with correct meal type
- [ ] iOS TodayView groups logs into Breakfast → Lunch → Dinner → Snack sections
- [ ] Empty meal category sections are skipped (not shown)
- [ ] Logs with no meal_type fall under "Other" section
- [ ] Daily summaries still show total macros (not per-meal)
- [ ] All pytest tests pass: `pytest tests/`

---

**Iteration Start**: 2026-04-08  
**Status**: 🚧 In Progress
