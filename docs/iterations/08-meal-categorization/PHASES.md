# Phases — Iteration 08: Meal Categorization

Detailed step-by-step breakdown of implementation.

---

## Phase 1: Database Schema — Add meal_type Column

**Files**: `NomNom-Backend/src/models/food_log.py`, Alembic migration

### Step 1.1: Update FoodLog Model

In `src/models/food_log.py`, add column after `cat_roast`:

```python
meal_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
```

**Why**: String(20) is enough for "breakfast", "lunch", "dinner", "snack". Nullable allows backward compatibility.

### Step 1.2: Generate and Run Migration

```bash
cd NomNom-Backend
alembic revision --autogenerate -m "add meal_type to food_logs"
```

Verify the generated migration file includes:
```python
op.add_column('food_logs', sa.Column('meal_type', sa.String(20), nullable=True))
```

Then run:
```bash
alembic upgrade head
```

**Test**: Query database to confirm column exists:
```sql
\d food_logs
```

---

## Phase 2: Backend Schemas — Update Pydantic Models

**File**: `NomNom-Backend/src/schemas/food_log.py`

### Step 2.1: FoodLogCreate

Add after `cuisine_origin`:
```python
meal_type: str | None = None
```

### Step 2.2: FoodLogUpdate

Add after `food_name` or at the end:
```python
meal_type: str | None = None
```

**Why**: Allow users to correct meal type via PATCH (optional for now).

### Step 2.3: FoodLogResponse

Add after `cuisine_origin`:
```python
meal_type: str | None
```

**Test**: Run pytest to confirm schema validation still works.

---

## Phase 3: Backend Service — Verify Field Mapping

**File**: `NomNom-Backend/src/services/food_log_service.py`

### Step 3.1: Check create_food_log()

Read the function to confirm it maps all fields from `data` (FoodLogCreate) to the FoodLog model. The pattern should be:

```python
async def create_food_log(db, user_id, data: FoodLogCreate):
    food_log = FoodLog(
        user_id=user_id,
        photo_path=data.photo_path,
        food_name=data.food_name,
        calories=data.calories,
        # ... other fields ...
        meal_type=data.meal_type,  # ← Ensure this line exists or add it
    )
    db.add(food_log)
    await db.commit()
    await db.refresh(food_log)
    return food_log
```

**Action**: If `meal_type=data.meal_type` is missing, add it.

---

## Phase 4: Backend API — Update PATCH Endpoint

**File**: `NomNom-Backend/src/api/food_logs.py`

### Step 4.1: Update update_food_log()

In the PATCH handler, after updating `food_name`, add:

```python
if data.meal_type is not None:
    food_log.meal_type = data.meal_type
```

**Example**:
```python
@router.patch("/{log_id}", response_model=FoodLogResponse)
async def update_food_log(log_id: int, data: FoodLogUpdate, ...):
    # ... find food_log ...
    food_log.food_name = data.food_name
    if data.meal_type is not None:
        food_log.meal_type = data.meal_type
    await db.commit()
    await db.refresh(food_log)
    return food_log
```

**Test**: Manual test via curl or iOS app.

---

## Phase 5: iOS Models — Add mealType Field

**File**: `NomNom-iOS/NomNom/Core/Models/FoodLog.swift`

### Step 5.1: Update FoodLogCreate

Add to struct:
```swift
let mealType: String?
```

Add to CodingKeys:
```swift
case mealType = "meal_type"
```

### Step 5.2: Update FoodLogResponse

Add to struct:
```swift
let mealType: String?
```

Add to CodingKeys:
```swift
case mealType = "meal_type"
```

**Example**:
```swift
struct FoodLogCreate: Codable {
    let photoPath: String
    let foodName: String
    let calories: Int
    let proteinG: Double
    let carbsG: Double
    let fatG: Double
    let foodCategory: String?
    let cuisineOrigin: String?
    let catRoast: String
    let mealType: String?  // ← NEW

    enum CodingKeys: String, CodingKey {
        case photoPath = "photo_path"
        case foodName = "food_name"
        case calories
        case proteinG = "protein_g"
        case carbsG = "carbs_g"
        case fatG = "fat_g"
        case foodCategory = "food_category"
        case cuisineOrigin = "cuisine_origin"
        case catRoast = "cat_roast"
        case mealType = "meal_type"  // ← NEW
    }
}
```

**Test**: Xcode build passes (Codable auto-validates).

---

## Phase 6: CameraViewModel — Add State

**File**: `NomNom-iOS/NomNom/Features/Camera/CameraViewModel.swift`

### Step 6.1: Add selectedMealType State

After existing @Published properties:
```swift
@Published var selectedMealType: String = "breakfast"
```

### Step 6.2: Include in saveLog()

In the `saveLog()` function where `FoodLogCreate` is constructed, add:
```swift
let logData = FoodLogCreate(
    photoPath: analysis.photoPath,
    foodName: analysis.foodName,
    calories: analysis.calories,
    proteinG: analysis.proteinG,
    carbsG: analysis.carbsG,
    fatG: analysis.fatG,
    foodCategory: analysis.foodCategory,
    cuisineOrigin: analysis.cuisineOrigin,
    catRoast: analysis.catRoast,
    mealType: selectedMealType  // ← NEW
)
```

### Step 6.3: Reset in reset()

In the `reset()` function, add:
```swift
selectedMealType = "breakfast"
```

**Test**: Build + run simulator.

---

## Phase 7: CameraView — Add Meal Picker UI

**File**: `NomNom-iOS/NomNom/Features/Camera/CameraView.swift`

### Step 7.1: Add Picker in analysisResultView

Between the food info card and the Save/Retake HStack, add:

```swift
// Meal type picker (before save)
if !viewModel.savedSuccessfully {
    Picker("Meal Type", selection: $viewModel.selectedMealType) {
        Text("Breakfast").tag("breakfast")
        Text("Lunch").tag("lunch")
        Text("Dinner").tag("dinner")
        Text("Snack").tag("snack")
    }
    .pickerStyle(.segmented)
    .padding(.horizontal, 16)
    .padding(.top, 16)
}
```

**Placement**: After line ~124 (after food info card, before Save/Retake buttons).

**Test**: Camera view displays segmented picker with 4 options. Tapping options updates state.

---

## Phase 8: TodayView — Group Logs by Meal Category

**File**: `NomNom-iOS/NomNom/Features/Dashboard/TodayView.swift`

### Step 8.1: Replace ForEach with Grouped Sections

Current structure (rough):
```swift
ForEach(viewModel.logs) { log in
    FoodLogCard(log: log, ...)
}
```

Replace with:
```swift
let mealOrder = ["breakfast", "lunch", "dinner", "snack"]
let grouped = Dictionary(grouping: viewModel.logs, by: { $0.mealType?.lowercased() ?? "other" })

ForEach(mealOrder, id: \.self) { mealType in
    if let logsForMeal = grouped[mealType], !logsForMeal.isEmpty {
        Section(header: Text(mealType.capitalized).font(.headline)) {
            ForEach(logsForMeal) { log in
                FoodLogCard(log: log, ...)
            }
        }
    }
}

// Show uncategorized logs at the bottom
if let others = grouped["other"], !others.isEmpty {
    Section(header: Text("Other").font(.headline)) {
        ForEach(others) { log in
            FoodLogCard(log: log, ...)
        }
    }
}
```

### Step 8.2: Preserve Daily Summary

Keep the existing daily summary card (total calories, macros) at the top — it should NOT be grouped, showing totals across all meals.

**Test**: 
- Take 3 photos, tag as Breakfast, Lunch, Dinner
- In Today tab, verify logs appear under correct section headers
- Log with no meal_type should appear under "Other"
- Daily summary still shows aggregate macros

---

## Testing Checklist

- [ ] Backend migration runs: `alembic upgrade head`
- [ ] Schema validation: `pytest tests/` — all pass
- [ ] Manual API test: POST with `meal_type: "breakfast"` → log created with meal_type
- [ ] Manual API test: GET /api/v1/food-logs/today → response includes meal_type
- [ ] iOS: Xcode build succeeds
- [ ] iOS: Camera view shows segmented picker
- [ ] iOS: Save with different meal types → logs saved
- [ ] iOS: Today tab groups logs under Breakfast/Lunch/Dinner/Snack
- [ ] iOS: Empty sections skipped
- [ ] iOS: Daily summary still shows correct totals

---

**Last Updated**: 2026-04-08
