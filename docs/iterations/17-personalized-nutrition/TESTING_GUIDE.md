# Iteration 17 Testing Guide — Settings Screen

## Pre-Testing Checklist

- [ ] Backend server running
- [ ] iOS app built and running on device/simulator
- [ ] User is logged in (has valid JWT token)

---

## Part 1: Start the Backend Server

### Option A: From Terminal

```bash
cd /Users/ionahu/sources/NomNom/NomNom-Backend

# Activate virtual environment (if using one)
source .venv/bin/activate

# Run the FastAPI server
python -m uvicorn src.app:create_app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     NomNom backend starting up
```

### Option B: Using uvicorn directly

```bash
cd /Users/ionahu/sources/NomNom/NomNom-Backend
uvicorn src.app:create_app --reload --port 8000
```

**Note:** If you get `ModuleNotFoundError: No module named 'pgvector'`, the server will still start but database operations may fail. This is okay for frontend testing.

---

## Part 2: Update iOS App Configuration (if needed)

If your iOS app is pointing to a different backend URL, update it:

1. **Find the API configuration** in the iOS app (usually in `Core/Services/APIClient.swift` or similar)
2. **Update the base URL** to match your running backend:
   ```swift
   let baseURL = "http://localhost:8000"  // or your actual server IP
   ```

---

## Part 3: Test the Settings Screen

### Test 1: Load Existing Profile

**Steps:**
1. Launch the NomNom iOS app
2. Navigate to **Settings** tab
3. **Expected Result:** Settings screen loads with existing profile data
   - Health Profile section appears
   - Medical Information section appears
   - Cat Style section appears
   - Nutrition Goals section appears (existing)

### Test 2: Edit Health Profile Fields

**Steps:**
1. In Settings, find the **Health Profile** section
2. Edit each field:
   - **Goal:** Change to "Lose Weight" (should update target calories)
   - **Age:** Change to 28
   - **Race:** Enter "Asian" (optional)
   - **Height:** Enter 175
   - **Weight:** Enter 75

**Expected Result:**
- Fields accept input
- No crashes
- (Targets section below may update if backend is recalculating)

### Test 3: Test Goal Selection

**Steps:**
1. In **Health Profile**, find the **Goal** picker
2. Switch between goals:
   - Maintain Weight
   - Lose Weight
   - Gain Muscle
   - Shape Figure

**Expected Result:**
- Goal changes in the UI
- (If backend is running, you should see different calorie targets calculated)

### Test 4: Add Medical Information

**Steps:**
1. Tap **"Allergies & Conditions"** link in Medical Information section
2. **On MedicalInfoView:**
   - Type "Peanuts" in Allergies field → tap + button
   - Type "Shellfish" in Allergies field → tap + button
   - Type "Pre-diabetes" in Medical Conditions field → tap + button
   - Type "Metformin" in Medications field → tap + button
   - Type "Knee surgery" in Surgeries field → tap + button

3. Tap "Done" to return to Settings

**Expected Result:**
- Each item appears as a chip/tag below the textfield
- Items can be deleted by tapping the X button
- Back button returns to Settings
- Checkmark appears next to "Allergies & Conditions" link indicating data was added

### Test 5: Save Profile and Verify Backend Response

**Steps:**
1. Tap **Save** button (top right)
2. Watch for one of these outcomes:

**Expected Result A (Backend running, database working):**
- Green "Saved!" message appears briefly
- No errors
- (Restart app) Profile data persists

**Expected Result B (Backend running, database issue):**
- Error message like "Failed to save profile: Server error"
- This means the backend needs database setup

**Expected Result C (Backend not running):**
- Error like "Failed to save profile: Connection refused"
- Instructions to start backend above

### Test 6: Verify Backend Response (with curl)

If backend is running, test the API directly:

```bash
# Get profile (using your JWT token)
curl -X GET http://localhost:8000/api/v1/profile/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "age": 28,
  "gender": "male",
  "race": "Asian",
  "height_cm": 175.0,
  "weight_kg": 75.0,
  "activity_level": "moderate",
  "goal": "lose_weight",
  "cat_style": "sassy",
  "allergies": ["Peanuts", "Shellfish"],
  "dietary_restrictions": null,
  "cuisine_preferences": null,
  "medical_conditions": ["Pre-diabetes"],
  "surgeries": ["Knee surgery"],
  "medications": ["Metformin"],
  "calorie_target": null,
  "protein_target": null,
  "carb_target": null,
  "fat_target": null,
  "notification_enabled": true,
  "targets": {
    "calorie_target": 2240,
    "protein_target": 168,
    "carb_target": 224,
    "fat_target": 75
  }
}
```

**Key observations:**
- ✅ `goal`: "lose_weight" (as set)
- ✅ `targets.calorie_target`: 2240 (should be ~15% below TDEE)
- ✅ `targets.protein_target`: 168g (30% of adjusted calories ÷ 4 kcal/g)
- ✅ `targets.carb_target`: 224g (40% of adjusted calories ÷ 4 kcal/g)
- ✅ `targets.fat_target`: 75g (30% of adjusted calories ÷ 9 kcal/g)
- ✅ `allergies`: ["Peanuts", "Shellfish"] (as added)
- ✅ `medical_conditions`: ["Pre-diabetes"] (as added)

---

## Part 4: Test Different Goals

Repeat Test 5 for each goal and verify calorie targets change:

### Goal: "Lose Weight"
Expected targets (for 30y, 175cm, 75kg, moderate activity):
- TDEE base: ~2600 kcal
- Adjusted: 2600 × 0.85 = **2210 kcal**
- Protein: ~166g, Carbs: ~221g, Fat: ~74g

### Goal: "Maintain"
Expected targets:
- TDEE base: ~2600 kcal
- Adjusted: 2600 × 1.0 = **2600 kcal**
- Protein: ~162g, Carbs: ~325g, Fat: ~72g

### Goal: "Gain Muscle"
Expected targets:
- TDEE base: ~2600 kcal
- Adjusted: 2600 × 1.1 = **2860 kcal**
- Protein: ~252g, Carbs: ~322g, Fat: ~64g

### Goal: "Shape Figure"
Expected targets:
- TDEE base: ~2600 kcal
- Adjusted: 2600 × 0.95 = **2470 kcal**
- Protein: ~216g, Carbs: ~247g, Fat: ~68g

---

## Part 5: Edge Cases & Error Handling

### Test: Invalid Age
- Try entering age 15 or 150
- **Expected:** Should still save (frontend doesn't validate yet, backend will)

### Test: Empty Medical Fields
- Clear all medical information
- Save
- **Expected:** Medical arrays should be empty or null in response

### Test: Very Large Values
- Height: 500cm
- Weight: 500kg
- **Expected:** Should still calculate (no frontend validation), backend may flag as suspicious

### Test: Concurrent Edits
- Change Age, Goal, Weight all at once
- Tap Save
- **Expected:** All changes should be saved together

---

## Troubleshooting

### "Failed to load profile: Server error (404)"
**Cause:** Backend is not running or profile endpoint is down
**Fix:** 
1. Start backend server (see Part 1)
2. Verify `GET /api/v1/profile/` endpoint is working

### "Failed to save profile: Connection refused"
**Cause:** Backend is not running or wrong URL
**Fix:**
1. Start backend server
2. Check iOS app's API configuration (base URL)

### "Failed to save profile: Server error (500)"
**Cause:** Database issue or missing migration
**Fix:**
1. Check backend logs for specific error
2. Run database migration: `alembic upgrade head`

### Settings load but medical info is missing
**Cause:** iOS model doesn't have the fields yet
**Fix:**
1. Verify `UserProfile.swift` has `medicalConditions`, `surgeries`, `medications`
2. Verify CodingKeys are correct
3. Rebuild iOS app

### Goal picker doesn't appear
**Cause:** SettingsView not updated with new Health Profile section
**Fix:**
1. Verify latest version of `SettingsView.swift` is compiled
2. Rebuild iOS app

---

## Success Criteria

✅ **Settings screen loads without crashing**
✅ **Health Profile section appears with Goal, Age, Race, Height, Weight**
✅ **Medical Information section appears with link to add allergies/conditions**
✅ **Can edit all fields without crashes**
✅ **Medical info can be added and removed inline**
✅ **Save button sends data to backend**
✅ **Backend response includes calculated targets based on goal**
✅ **Goal selection changes calorie target (if backend working)**

---

## Next Steps (If Everything Works)

1. Celebrate! The Settings screen is fully functional ✨
2. Proceed to **Part 4: Food Diary Integration** to display daily targets on the Food Diary screen
3. Add visual progress bars and allergy warnings

---

## Quick Reference: Expected Macro Splits by Goal

| Goal | Protein | Carbs | Fat | TDEE Multiplier |
|------|---------|-------|-----|-----------------|
| Lose Weight | 30% | 40% | 30% | × 0.85 |
| Maintain | 25% | 50% | 25% | × 1.0 |
| Gain Muscle | 35% | 45% | 20% | × 1.1 |
| Shape Figure | 35% | 40% | 25% | × 0.95 |

---

## Debugging Commands

### Check backend is running:
```bash
curl http://localhost:8000/health
```

### Check profile endpoint:
```bash
curl http://localhost:8000/api/v1/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Check backend logs for errors:
```bash
# In the terminal where you ran uvicorn, look for ERROR or EXCEPTION lines
```

---

**Testing Status:** Ready to begin! Start with Part 1 above.
