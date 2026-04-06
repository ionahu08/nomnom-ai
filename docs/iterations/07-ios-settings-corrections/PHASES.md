# Phases — Iteration 07: iOS Settings, Corrections & Recommendations

## Phase 13: Profile Models & Services

### 13.1: UserProfile Model

- [ ] Create `NomNom-iOS/NomNom/Core/Models/UserProfile.swift`:
  - `UserProfile: Codable` with fields: age, gender, heightCm, weightKg, activityLevel, calorieTarget, proteinTarget, carbTarget, fatTarget, catStyle, dietaryRestrictions, allergies, cuisinePreferences
  - CodingKeys enum for snake_case mapping

### 13.2: Profile Service

- [ ] Create `NomNom-iOS/NomNom/Core/Services/ProfileService.swift`:
  - `getProfile() async throws -> UserProfile`
  - `updateProfile(_ profile: UserProfile) async throws -> UserProfile`
  - Calls `GET /api/v1/profile` and `PUT /api/v1/profile`

### 13.3: Recommendation Service

- [ ] Create `NomNom-iOS/NomNom/Core/Services/RecommendationService.swift`:
  - `MealRecommendation: Codable` with recommendation: String, kbEntriesUsed: Int
  - `getMealRecommendation() async throws -> MealRecommendation`
  - Calls `GET /api/v1/recommendations/meal`

---

## Phase 14: Settings Screen

### 14.1: SettingsViewModel

- [ ] Create `NomNom-iOS/NomNom/Features/Settings/SettingsViewModel.swift`:
  - @Published profile: UserProfile?
  - @Published isLoading, errorMessage, savedSuccessfully
  - `loadProfile() async` — calls ProfileService.getProfile()
  - `saveProfile() async` — calls ProfileService.updateProfile()
  - `logout()` — calls AuthService.shared.logout()
  - Call `.task { await loadProfile() }` on view appear

### 14.2: SettingsView

- [ ] Create `NomNom-iOS/NomNom/Features/Settings/SettingsView.swift`:
  - Section: "Cat Style" — Picker with options (Sassy, Grumpy, Wholesome, Concerned, Neutral)
  - Section: "Nutrition Goals" — Steppers/TextFields for calorie, protein, carb, fat targets
  - Section: "Account" — Red Logout button (prominent)
  - Save button at bottom (disabled while isLoading)
  - Shows errorMessage if present
  - Shows "Saved ✓" inline after successful save

Files to create:
- `NomNom-iOS/NomNom/Features/Settings/SettingsViewModel.swift`
- `NomNom-iOS/NomNom/Features/Settings/SettingsView.swift`

---

## Phase 15: Add Settings Tab to Navigation

### 15.1: Update ContentView

- [ ] Edit `NomNom-iOS/NomNom/App/ContentView.swift`:
  - Add third tab with `SettingsView()`
  - Tab label: "Settings" with systemImage: "gearshape.fill"
  - Tabs now: Camera, Today, Settings

---

## Phase 16: Fix Food Correction UX Bug

### 16.1: CameraViewModel State Machine Fix

- [ ] Edit `NomNom-iOS/NomNom/Features/Camera/CameraViewModel.swift`:
  - Remove the `.alert("Saved!")` that triggers immediately after save
  - Change logic: after `saveLog()` completes, show result screen but **don't** reset state
  - Add new state property: `showResultScreen: Bool` (shows after save completes)
  - Keep all state live until user explicitly dismisses (taps "Done")

Files to edit:
- `NomNom-iOS/NomNom/Features/Camera/CameraViewModel.swift`

### 16.2: CameraView Result Screen Fix

- [ ] Edit `NomNom-iOS/NomNom/Features/Camera/CameraView.swift`:
  - Remove the `.alert("Saved!")` modifier
  - Show result screen with inline "Saved ✓" label (green text, checkmark icon)
  - Keep "This is wrong" button visible at bottom (now reachable!)
  - Keep "Done" button (closes and resets state)

Verify:
```
1. Take photo → Upload → Analyze → Save
2. Result screen shows "Saved ✓"
3. "This is wrong" button is clickable
4. Tap "This is wrong" → correction sheet appears (existing logic)
5. PATCH succeeds → sheet closes → state resets
```

---

## Phase 17: Wire Recommendations Endpoint

### 17.1: TodayViewModel Additions

- [ ] Edit `NomNom-iOS/NomNom/Features/Dashboard/TodayViewModel.swift`:
  - Add @Published recommendation: String?
  - Add @Published isLoadingRecommendation: Bool
  - Add `loadRecommendation() async` — calls RecommendationService.getMealRecommendation()

### 17.2: TodayView Additions

- [ ] Edit `NomNom-iOS/NomNom/Features/Dashboard/TodayView.swift`:
  - Add "What should I eat next?" button in summary card header area
  - Tapping button calls `Task { await viewModel.loadRecommendation() }`
  - Show loading spinner while `isLoadingRecommendation`
  - Modal sheet shows recommendation text when loaded
  - Inline error display if recommendation load fails

Verify:
```
1. Tap "What should I eat?" button
2. Loading spinner appears
3. API call succeeds
4. Recommendation modal shows with text from backend
5. Close modal → state resets
```

---

## Phase 18: Error Display in Today View

### 18.1: Error Message Display

- [ ] Edit `NomNom-iOS/NomNom/Features/Dashboard/TodayView.swift`:
  - Add error banner at top if `viewModel.errorMessage != nil`
  - Dismiss button (X) to clear error
  - Red background, readable text

---

## Success Criteria

- [ ] Settings tab visible and functional ✅
- [ ] Cat style picker works ✅
- [ ] Macro goal inputs save to backend ✅
- [ ] Logout button works ✅
- [ ] Food correction button reachable after save ✅
- [ ] Correction PATCH succeeds ✅
- [ ] "What to eat?" button shows recommendations ✅
- [ ] Errors displayed in Today view ✅
- [ ] All tabs functional (Camera, Today, Settings) ✅

---

## Next

Iteration 08: Dashboard completion (progress bars, cat mood) OR Streaming/optimization features.
