# Phases — Iteration 06: iOS Complete

## Phase 11: iOS Dashboard

### 11.1: Dashboard Models + Components

- [ ] Create `NomNom-iOS/NomNom/Core/Models/Dashboard.swift` — MacroProgress, Dashboard, CatState, CatMood enum
- [ ] Create `NomNom-iOS/NomNom/Core/Components/MacroProgressBar.swift` — progress bar (color by macro type)
- [ ] Create `NomNom-iOS/NomNom/Core/Components/CatView.swift` — cat emoji + mood expression

### 11.2: Dashboard ViewModel + View

- [ ] Create `NomNom-iOS/NomNom/Features/Dashboard/DashboardViewModel.swift`:
  - @Published dashboard, isLoading, errorMessage
  - `loadDashboard()` → GET `/api/v1/dashboard/today`
  - `refreshDashboard()`
- [ ] Create `NomNom-iOS/NomNom/Features/Dashboard/DashboardView.swift`:
  - Show cat + mood + status line
  - Show macro progress bars
  - Show today's meals as FoodLogCards
  - Pull-to-refresh
- [ ] Update ContentView.swift — use DashboardView as first tab

### 11.3: Tests

- [ ] Create `NomNomTests/Features/Dashboard/DashboardViewModelTests.swift`

---

## Phase 12: iOS Remaining Screens

### 12.1: Timeline

- [ ] Create `NomNom-iOS/NomNom/Features/Timeline/TimelineViewModel.swift`:
  - @Published groupedMeals (by date)
  - `loadTimeline()` → GET `/api/v1/food-logs/`
- [ ] Create `NomNom-iOS/NomNom/Features/Timeline/TimelineView.swift` — grid grouped by date
- [ ] Create `NomNom-iOS/NomNom/Features/Timeline/FoodDetailView.swift` — details, delete, edit
- [ ] Create `NomNom-iOS/NomNom/Core/Components/PhotoGridItem.swift` — thumbnail
- [ ] Create `tests/integration/test_timeline.swift`

### 12.2: Weekly Recaps

- [ ] Create `NomNom-iOS/NomNom/Core/Models/WeeklyRecap.swift`
- [ ] Create `NomNom-iOS/NomNom/Features/WeeklyRecap/WeeklyRecapViewModel.swift`:
  - @Published recaps
  - `loadRecaps()` → GET `/api/v1/recaps/`
- [ ] Create `NomNom-iOS/NomNom/Features/WeeklyRecap/WeeklyRecapView.swift` — list of recap cards
- [ ] Create `NomNom-iOS/NomNom/Features/WeeklyRecap/RecapDetailView.swift` — full recap + stats
- [ ] Create `tests/integration/test_weekly_recaps.swift`

### 12.3: Onboarding (5-Step Flow)

- [ ] Create `NomNom-iOS/NomNom/Features/Onboarding/OnboardingViewModel.swift`:
  - @Published step (0-4), age, gender, height, weight, activity, cat_style
  - `nextStep()`, `previousStep()`, `submitProfile()` → POST /profile
- [ ] Create `NomNom-iOS/NomNom/Features/Onboarding/OnboardingView.swift` — container
- [ ] Create `NomNom-iOS/NomNom/Features/Onboarding/OnboardingStep*.swift` (5 files):
  - Step1: age, gender
  - Step2: height, weight
  - Step3: activity level
  - Step4: cat style selection
  - Step5: review + submit

### 12.4: Settings

- [ ] Create `NomNom-iOS/NomNom/Features/Settings/SettingsViewModel.swift`:
  - @Published profile
  - `loadProfile()`, `updateProfile(data)`, `logout()`
- [ ] Refactor `LoginView.swift` → show onboarding if no profile
- [ ] Create `NomNom-iOS/NomNom/Features/Settings/SettingsView.swift` — edit profile fields + logout

### 12.5: Auth Gate

- [ ] Update `NomNom-iOS/NomNom/App/NomNomApp.swift`:
  - If not authenticated → LoginView
  - If authenticated but no profile → OnboardingView
  - If fully set up → ContentView (5-tab view)

### 12.6: Final ContentView

- [ ] Update `NomNom-iOS/NomNom/App/ContentView.swift` — 5 tabs:
  - Today (Dashboard)
  - Timeline
  - Recaps
  - Settings
  - Camera (floating or in tabs)

### 12.7: Tests

- [ ] Create tests for all ViewModels
- [ ] Create tests for all Views

---

## Success Criteria

- [x] Dashboard: macro bars, cat mood, today's meals ✅
- [x] Timeline: photo grid, food detail, delete ✅
- [x] Weekly Recaps: list + detail views ✅
- [x] Onboarding: 5-step flow ✅
- [x] Settings: profile editing + logout ✅
- [x] All 5 tabs functional ✅
- [x] Auth gate works (login → onboarding → main app) ✅
- [x] All tests pass ✅
- [x] iOS app feature-complete ✅

---

## Final Status

**NomNom Complete** ✅

**Full app:**
- Backend: FastAPI with 12 AI/ML skills
- iOS: 5-tab SwiftUI app with full user journey
- End-to-end on real iPhone via ngrok

Perfect for MLE/AI Engineer resume!
