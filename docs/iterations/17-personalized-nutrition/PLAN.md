# Iteration 17: Personalized Nutrition Profile

**Goal:** Enable users to set personal health information (age, weight, goals, medical history) and use it to calculate personalized daily calorie and macronutrient recommendations shown on the Food Diary screen.

**Duration:** 5–7 days

**Business Value:** Transform NomNom from generic calorie tracking to personalized nutrition guidance based on individual characteristics and goals.

---

## Goals

- [ ] Build new Settings screen section: "Health Profile"
- [ ] Collect comprehensive user data (anthropometric, demographic, medical, goal-based)
- [ ] Store data securely in backend
- [ ] Implement calorie & macronutrient calculation (Harris-Benedict, Mifflin-St Jeor, goal-based adjustment)
- [ ] Display personalized daily targets on Food Diary screen
- [ ] Add visual feedback (progress toward daily goals)
- [ ] Persist data across sessions

---

## What Already Exists

**Backend (NomNom-Backend/src/):**
- User authentication & JWT token handling
- PostgreSQL database with user profiles
- Food log API (`POST /api/v1/food-logs/analyze`)
- Claude API integration for food analysis
- Semantic caching for food data

**iOS App (NomNom-iOS/NomNom/):**
- Settings view with basic profile section
- Food Diary screen showing daily logs
- SwiftUI components (Form, NavigationLink, etc.)
- API client for backend communication

**Data Models:**
- User model (id, email, created_at, etc.)
- FoodLog model (food_name, calories, macros, timestamp)

---

## What We're Building (Iteration 17)

### Part 1: Backend — User Health Profile API

**1A. Database Schema Extension**

**New table: `user_health_profile`**
```
id (UUID, PK)
user_id (UUID, FK → users)
age (int, years)
gender (ENUM: male/female/other)
race (TEXT, nullable)
height_cm (float)
weight_kg (float)
goal (ENUM: lose_weight/maintain/gain_muscle/shape_figure)
activity_level (ENUM: sedentary/light/moderate/active/very_active)
allergies (JSON list)
medical_conditions (JSON list, e.g., [diabetes, hypertension])
surgeries (JSON list, e.g., [gastric_bypass, knee_replacement])
medications (JSON list)
daily_calorie_target (int, calculated)
daily_protein_g (int, calculated)
daily_carbs_g (int, calculated)
daily_fat_g (int, calculated)
created_at (timestamp)
updated_at (timestamp)
```

**Migration:** `NomNom-Backend/alembic/versions/YYYYMMDD_add_health_profile.py`

**1B. FastAPI Endpoints**

**Endpoint 1: `POST /api/v1/user/health-profile`**
```json
{
  "age": 30,
  "gender": "male",
  "race": "Asian",
  "height_cm": 175.0,
  "weight_kg": 75.0,
  "goal": "lose_weight",
  "activity_level": "moderate",
  "allergies": ["peanuts", "shellfish"],
  "medical_conditions": ["pre_diabetes"],
  "surgeries": [],
  "medications": ["metformin"]
}
```

**Response:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "age": 30,
  "daily_calorie_target": 2000,
  "daily_protein_g": 150,
  "daily_carbs_g": 200,
  "daily_fat_g": 65,
  "created_at": "2026-06-13T10:00:00Z"
}
```

**Endpoint 2: `GET /api/v1/user/health-profile`**
- Retrieves current health profile
- Returns calculated daily targets

**Endpoint 3: `PATCH /api/v1/user/health-profile`**
- Updates health profile
- Recalculates targets

**1C. Calculation Engine**

**File:** `NomNom-Backend/src/services/nutrition_service.py`

**Functions:**

1. **`calculate_bmr(age, gender, weight_kg, height_cm) → float`**
   - Mifflin-St Jeor formula (more accurate than Harris-Benedict)
   - Returns Basal Metabolic Rate (kcal/day)

2. **`calculate_tdee(bmr, activity_level) → float`**
   - Total Daily Energy Expenditure = BMR × activity_multiplier
   - Multipliers: sedentary=1.2, light=1.375, moderate=1.55, active=1.725, very_active=1.9

3. **`adjust_tdee_by_goal(tdee, goal, weight_kg) → float`**
   - lose_weight: tdee × 0.85 (500 kcal deficit, ~0.5kg/week loss)
   - maintain: tdee × 1.0
   - gain_muscle: tdee × 1.1 (250 kcal surplus)
   - shape_figure: tdee × 0.95 (250 kcal deficit, preserve muscle)

4. **`calculate_macros(adjusted_tdee, goal) → dict`**
   - lose_weight: protein 30%, carbs 40%, fat 30%
   - maintain: protein 25%, carbs 50%, fat 25%
   - gain_muscle: protein 35%, carbs 45%, fat 20%
   - shape_figure: protein 35%, carbs 40%, fat 25%
   - Returns: {protein_g, carbs_g, fat_g}

5. **`validate_health_profile(profile_data) → List[str]`**
   - Validates age (18–120), weight (30–300kg), height (100–250cm)
   - Checks for internal consistency
   - Returns validation errors (empty list = valid)

---

### Part 2: iOS Frontend — Settings Screen Extension

**2A. New SwiftUI View: `HealthProfileView`**

**File:** `NomNom-iOS/NomNom/Features/Settings/HealthProfileView.swift`

**Sections:**
1. **Basic Information**
   - Age (Stepper, 18–120)
   - Gender (Picker: Male/Female/Other)
   - Race (TextField, optional)

2. **Anthropometric Data**
   - Height (Segmented: cm / inches, TextField)
   - Weight (Segmented: kg / lbs, TextField)
   - Visual: BMI indicator (underweight/normal/overweight/obese)

3. **Fitness Goals**
   - Goal (Picker: Lose Weight / Maintain / Gain Muscle / Shape Figure)
   - Activity Level (Picker: Sedentary / Light / Moderate / Active / Very Active)
   - Visual: Target calorie display (updated in real-time as inputs change)

4. **Medical Information** (Expandable Section)
   - Allergies (Multi-select TextField with chips)
   - Medical Conditions (Multi-select with common options: Diabetes, Hypertension, Celiac, etc.)
   - Surgeries (Multi-select with common options)
   - Medications (Multi-select TextField)
   - Note: "This helps NomNom provide safer, personalized recommendations"

5. **Summary Card**
   - Shows calculated daily targets in real-time
   - "Daily Target: 2,000 kcal | Protein: 150g | Carbs: 200g | Fat: 65g"
   - Color-coded goal (green if reasonable, yellow if aggressive, red if extreme)

**2B. Form Validation**
- Real-time validation (age, weight, height ranges)
- Error messages inline
- Save button disabled until form is valid

**2C. Data Persistence**
- Save button → POST `/api/v1/user/health-profile`
- Loading state during save
- Success/error alert
- Stored locally in UserDefaults for offline access (synced with backend)

---

### Part 3: iOS Frontend — Food Diary Integration

**3A. Update `FoodDiaryView`**

**File:** `NomNom-iOS/NomNom/Features/FoodDiary/FoodDiaryView.swift`

**Changes:**
1. Add daily summary header:
   ```
   Today's Nutrition
   Calories: 1,450 / 2,000 kcal (72%)
   Protein: 85g / 150g (57%)
   Carbs: 155g / 200g (78%)
   Fat: 48g / 65g (74%)
   ```

2. Visual progress bars (color-coded):
   - Green: 0–90% of target
   - Yellow: 90–110% of target
   - Red: >110% of target

3. Display allergies/medical warnings:
   - If user has allergies and log contains allergen → ⚠️ "Contains peanuts"
   - If medical condition (e.g., diabetes) and log has high sugar → Info banner

**3B. API Changes**
- Modify `GET /api/v1/food-logs/daily-summary` to include user targets
- Response includes: actual_calories, target_calories, percentages, warnings

---

### Part 4: Data Validation & Error Handling

**Backend Validation:**
- Age: 18–120
- Height: 100–250 cm
- Weight: 30–300 kg
- BMI sanity check (warn if <15 or >50)
- Activity level must match goal (don't allow sedentary + gain_muscle)

**Frontend Validation:**
- Same as above, with inline error messages
- Prevent submission if invalid

**Privacy & Security:**
- Health data encrypted at rest
- HIPAA-adjacent considerations (allergies, medical history)
- Only user can view their own health profile
- No logging of sensitive data

---

## Success Criteria

### Part 1 (Backend): Nutrition Service
- [ ] Database migration runs without errors
- [ ] Health profile table created with all fields
- [ ] All calculation functions implemented (BMR, TDEE, macros)
- [ ] Unit tests pass (test_calculate_bmr, test_calculate_tdee, etc.)
- [ ] Validation function catches edge cases
- [ ] All 3 endpoints (POST, GET, PATCH) work correctly
- [ ] API returns correct daily targets for 10 test cases

### Part 2 (iOS): Settings Screen
- [ ] `HealthProfileView` renders without errors
- [ ] All 5 sections display correctly (Basic, Anthropometric, Goals, Medical, Summary)
- [ ] Real-time calculation updates as user types
- [ ] Form validation works (error messages appear)
- [ ] Save button sends correct JSON to backend
- [ ] Success alert shown after save
- [ ] Data persists across app launches

### Part 3 (iOS): Food Diary Integration
- [ ] Daily summary header displays with progress bars
- [ ] Progress bars color-code correctly (green/yellow/red)
- [ ] Allergy warnings appear when relevant
- [ ] Medical condition warnings appear when relevant
- [ ] `GET /api/v1/food-logs/daily-summary` returns targets

### Part 4 (Testing & Documentation)
- [ ] All unit tests passing (backend + iOS)
- [ ] Integration test: Create user → Enter health profile → Log food → See daily summary
- [ ] Documentation updated (API docs, user guide)
- [ ] Iteration summary created

---

## Technical Details

### Calculation Examples

**Example 1: 30-year-old male, 175cm, 75kg, goal = lose_weight, activity = moderate**
1. BMR = 10(75) + 6.25(175) - 5(30) + 5 = 1,700 kcal
2. TDEE = 1,700 × 1.55 = 2,635 kcal
3. Adjusted for weight loss = 2,635 × 0.85 = 2,240 kcal
4. Macros (lose_weight: 30/40/30):
   - Protein: 2,240 × 0.30 / 4 = 168g
   - Carbs: 2,240 × 0.40 / 4 = 224g
   - Fat: 2,240 × 0.30 / 9 = 75g

**Example 2: Same person, goal = gain_muscle**
1. BMR = 1,700 kcal (same)
2. TDEE = 2,635 kcal (same)
3. Adjusted for muscle gain = 2,635 × 1.1 = 2,899 kcal
4. Macros (gain_muscle: 35/45/20):
   - Protein: 2,899 × 0.35 / 4 = 254g
   - Carbs: 2,899 × 0.45 / 4 = 326g
   - Fat: 2,899 × 0.20 / 9 = 64g

### UI Mockup (Text)

**Settings → Health Profile:**
```
┌─────────────────────────────────────────────────┐
│ HEALTH PROFILE                           [Edit] │
├─────────────────────────────────────────────────┤
│ Age: [30                                    ▲▼] │
│ Gender: [Male          ▼] Race: [Asian     ] │
├─────────────────────────────────────────────────┤
│ Height: [175 cm / 5'9"  ▼]                    │
│ Weight: [75 kg / 165 lbs ▼]                    │
│ BMI: 24.5 (Normal)                            │
├─────────────────────────────────────────────────┤
│ Goal: [Lose Weight ▼]                         │
│ Activity: [Moderate ▼]                        │
├─────────────────────────────────────────────────┤
│ ▼ Medical Information (Optional)                │
│   Allergies: [Peanuts] [Shellfish] [+]         │
│   Conditions: [Pre-diabetes] [+]                │
│   Surgeries: [+]                              │
│   Medications: [Metformin] [+]                 │
├─────────────────────────────────────────────────┤
│ DAILY TARGETS                                  │
│ 🔥 2,240 kcal                                  │
│ 🥩 168g Protein                                │
│ 🍞 224g Carbs                                  │
│ 🧈 75g Fat                                     │
├─────────────────────────────────────────────────┤
│                        [Save] [Cancel]         │
└─────────────────────────────────────────────────┘
```

**Food Diary (Daily Summary):**
```
┌─────────────────────────────────────────────────┐
│ TODAY'S NUTRITION                              │
├─────────────────────────────────────────────────┤
│ Calories: 1,450 / 2,240 kcal (64%) ████░░░░░  │
│ Protein: 85g / 168g (51%)      ███░░░░░░░░  │
│ Carbs: 155g / 224g (69%)       ██████░░░░░  │
│ Fat: 48g / 75g (64%)           █████░░░░░░  │
├─────────────────────────────────────────────────┤
│ ⚠️ WARNING: Salad contains peanuts (allergy)  │
├─────────────────────────────────────────────────┤
│ [Food Log Item 1]                              │
│ [Food Log Item 2]                              │
│ [+ Add Food]                                   │
└─────────────────────────────────────────────────┘
```

---

## Resume Skills

This iteration demonstrates:

1. **Full-Stack Nutrition Science**
   - Basal metabolic rate calculation (Mifflin-St Jeor)
   - Macronutrient distribution based on goals
   - Activity-level adjustment logic

2. **Backend Engineering**
   - Database schema design (health profile table)
   - API design (CRUD endpoints)
   - Input validation and error handling
   - Calculation service architecture

3. **iOS Development**
   - Complex form with multiple input types (Stepper, Picker, TextField, Multi-select)
   - Real-time calculation and UI updates
   - Data persistence (UserDefaults + API)
   - SwiftUI state management

4. **Data Integration**
   - Combining user health data with food logs
   - Calculating derived metrics (progress toward goals)
   - Displaying personalized recommendations

5. **User Experience**
   - Progressive disclosure (medical info optional, initially collapsed)
   - Real-time feedback (daily targets update as user enters data)
   - Contextual warnings (allergies, medical conditions)
   - Visual progress indication (bars, percentages, color coding)

---

## Files to Create/Modify

### Backend

**New Files:**
- `NomNom-Backend/src/services/nutrition_service.py` (calculations)
- `NomNom-Backend/src/schemas/health_profile.py` (Pydantic models)
- `NomNom-Backend/src/models/health_profile.py` (SQLAlchemy ORM)
- `NomNom-Backend/alembic/versions/20260613_add_health_profile.py` (migration)
- `NomNom-Backend/tests/services/test_nutrition_service.py` (unit tests)
- `NomNom-Backend/tests/api/test_health_profile.py` (integration tests)

**Modified Files:**
- `NomNom-Backend/src/api/user.py` (add health profile endpoints)
- `NomNom-Backend/src/api/food_logs.py` (update daily summary endpoint)
- `NomNom-Backend/src/models/user.py` (add relationship to health_profile)

### iOS

**New Files:**
- `NomNom-iOS/NomNom/Features/Settings/HealthProfileView.swift`
- `NomNom-iOS/NomNom/Features/Settings/Components/HealthInfoSection.swift`
- `NomNom-iOS/NomNom/Features/Settings/Components/MedicalInfoSection.swift`
- `NomNom-iOS/NomNom/Core/Models/HealthProfile.swift` (Codable struct)
- `NomNom-iOS/NomNom/Core/Services/NutritionService.swift` (client-side calculation)

**Modified Files:**
- `NomNom-iOS/NomNom/Features/Settings/SettingsView.swift` (add health profile button)
- `NomNom-iOS/NomNom/Features/FoodDiary/FoodDiaryView.swift` (show daily summary)
- `NomNom-iOS/NomNom/Core/Services/APIClient.swift` (add health profile endpoints)

### Documentation

**New Files:**
- `docs/iterations/17-personalized-nutrition/PLAN.md` (this file)
- `docs/iterations/17-personalized-nutrition/PHASES.md` (detailed day-by-day breakdown)
- `docs/iterations/17-personalized-nutrition/BUGLOG.md` (issues discovered during dev)
- `docs/iterations/17-personalized-nutrition/SUMMARY.md` (retrospective at iteration end)

---

## Next Steps

1. **Approve PLAN.md** — Confirm direction and scope
2. **Create PHASES.md** — Break down into Day 1–5 implementation steps
3. **Day 1:** Backend setup (models, schemas, migration, calculation service)
4. **Day 2:** Backend APIs (endpoints, validation, testing)
5. **Day 3:** iOS Settings screen (form layout, validation, real-time updates)
6. **Day 4:** iOS Food Diary integration (daily summary, progress bars, warnings)
7. **Day 5:** Testing, documentation, refinement

---

## References

- Mifflin-St Jeor Formula: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2820057/
- TDEE Calculation: https://www.health-calc.com/diet/energy-expenditure-formula
- Macronutrient Distribution: https://www.eatthismuch.com/
- NomNom Food Diary: `docs/iterations/09-food-diary/`
- NomNom Settings: `docs/iterations/07-ios-settings-corrections/`
