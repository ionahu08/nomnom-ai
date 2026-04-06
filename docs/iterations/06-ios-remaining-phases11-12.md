# NomNom — Iteration 06: iOS Complete — Dashboard, Timeline, Recaps & Onboarding

**Phases:** Phases 11-12 (full plan)

**Goal:** Complete the iOS app with dashboard, timeline, weekly recaps, onboarding, and settings screens.

**Resume Skills:** SwiftUI advanced patterns, streaming data handling, multi-screen navigation

---

## What's Built

- iOS: login, camera, food logging (S3-S4)
- Backend: fully complete with all features

## What We're Building

**Complete the iOS app:**
- Dashboard: today's macro progress bars, cat mood + status line, quick add button
- Timeline: scrollable photo grid of all past meals, grouped by date
- Weekly Recap: detail screen for past recaps with stats
- Onboarding: multi-step flow (profile info, dietary preferences, cat style selection)
- Settings: profile editing, preference management, logout

---

## Phase 11: iOS Dashboard

### 11.1.A: Add Dashboard models

Create/update `NomNom-iOS/NomNom/Core/Models/Dashboard.swift`:
```swift
// Models:
// - MacroProgress: current, target, percentage
// - Dashboard: date, total_meals, total_calories, macro_progress, cat_mood, meals
// - CatState: mood, status_line
// - CatMood enum: happy, proud, judging, worried, conflicted, sleeping
```

Files to create/update:
- `NomNom-iOS/NomNom/Core/Models/Dashboard.swift`

### 11.1.B: Create reusable components

Create the UI building blocks:

Files to create:
- `NomNom-iOS/NomNom/Core/Components/MacroProgressBar.swift` — horizontal progress bar for each macro
  - Shows: label, current/target, percentage, color (protein=green, carbs=orange, fat=red, calories=blue)
  - Filled width = percentage (clamped to 100%)
  - Shows over/under: "120%" if over, "50%" if under

- `NomNom-iOS/NomNom/Core/Components/CatView.swift` — the cat emoji + mood expression
  - Props: mood (happy, proud, judging, worried, conflicted, sleeping)
  - Renders cat with mood-specific emoji + animation
  - Optional: tappable to see status_line in a tooltip

- `NomNom-iOS/NomNom/Core/Components/PhotoGridItem.swift` — thumbnail for food photo
  - Props: FoodLog, image data
  - Shows: photo thumbnail, food name, calories
  - Tappable: navigates to food detail

### 11.1.C: Create DashboardViewModel

Create `NomNom-iOS/NomNom/Features/Dashboard/DashboardViewModel.swift`:
```swift
@MainActor
class DashboardViewModel: ObservableObject {
    @Published var dashboard: Dashboard?
    @Published var isLoading = false
    @Published var errorMessage: String?

    func loadDashboard() async {
        isLoading = true
        do {
            dashboard = try await api.get(path: "/api/v1/dashboard/today")
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }

    func refreshDashboard() async {
        await loadDashboard()
    }
}
```

Files to create:
- `NomNom-iOS/NomNom/Features/Dashboard/DashboardViewModel.swift`

### 11.1.D: Create DashboardView

Create `NomNom-iOS/NomNom/Features/Dashboard/DashboardView.swift`:
```swift
struct DashboardView: View {
    @StateObject private var viewModel = DashboardViewModel()

    var body: some View {
        NavigationStack {
            ZStack {
                NomNomColors.background.ignoresSafeArea()

                if let dashboard = viewModel.dashboard {
                    ScrollView {
                        VStack(spacing: 20) {
                            // Header: cat mood
                            VStack {
                                CatView(mood: dashboard.cat_mood.mood)
                                Text(dashboard.cat_mood.status_line)
                                    .font(.body)
                                    .multilineTextAlignment(.center)
                            }
                            .padding()

                            // Macro progress bars
                            MacroProgressBar(label: "Calories", current: dashboard.macro_progress.calories.current, target: dashboard.macro_progress.calories.target, color: .blue)
                            MacroProgressBar(label: "Protein", current: dashboard.macro_progress.protein.current, target: dashboard.macro_progress.protein.target, color: .green)
                            MacroProgressBar(label: "Carbs", current: dashboard.macro_progress.carbs.current, target: dashboard.macro_progress.carbs.target, color: .orange)
                            MacroProgressBar(label: "Fat", current: dashboard.macro_progress.fat.current, target: dashboard.macro_progress.fat.target, color: .red)

                            // Today's meals
                            if dashboard.meals.isEmpty {
                                Text("No meals logged yet. Tap camera to add!")
                                    .font(.body)
                                    .foregroundColor(NomNomColors.textSecondary)
                            } else {
                                VStack(alignment: .leading) {
                                    Text("Today's Meals")
                                        .font(.headline)
                                    ForEach(dashboard.meals) { meal in
                                        FoodLogCard(foodLog: meal)
                                    }
                                }
                            }

                            Spacer()
                        }
                        .padding()
                    }
                } else if viewModel.isLoading {
                    ProgressView()
                } else {
                    Text("Error loading dashboard")
                        .foregroundColor(NomNomColors.danger)
                }
            }
            .navigationTitle("Today")
            .navigationBarTitleDisplayMode(.inline)
            .onAppear { Task { await viewModel.loadDashboard() } }
            .refreshable { await viewModel.refreshDashboard() }
        }
    }
}
```

Files to create/update:
- `NomNom-iOS/NomNom/Features/Dashboard/DashboardView.swift`
- Update `NomNom-iOS/NomNom/App/ContentView.swift` — replace "Today's Log" tab with DashboardView

### 11.1.E: Test dashboard

Files to create:
- `NomNomTests/Features/Dashboard/DashboardViewModelTests.swift` — test loadDashboard (mocked API)

Commands:
- `xcodebuild test -scheme NomNom` — run tests

---

## Phase 12: iOS Remaining Screens

### 12.1.A: Timeline Screen

Timeline = scrollable grid of all food photos, grouped by date.

Create models:
- Update `NomNom-iOS/NomNom/Core/Models/FoodLog.swift` — ensure date grouping support

Create components:
- `NomNom-iOS/NomNom/Core/Components/PhotoGridItem.swift` — already created above

Create view models:
- `NomNom-iOS/NomNom/Features/Timeline/TimelineViewModel.swift`
  ```swift
  @MainActor
  class TimelineViewModel: ObservableObject {
      @Published var groupedMeals: [DateGroup] = []  // grouped by date
      @Published var isLoading = false
      @Published var errorMessage: String?

      func loadTimeline() async {
          isLoading = true
          do {
              let meals: [FoodLog] = try await api.get(path: "/api/v1/food-logs/")
              groupedMeals = groupByDate(meals)
          } catch {
              errorMessage = error.localizedDescription
          }
          isLoading = false
      }
  }
  ```

Create views:
- `NomNom-iOS/NomNom/Features/Timeline/TimelineView.swift` — grid layout with date groups
- `NomNom-iOS/NomNom/Features/Timeline/FoodDetailView.swift` — detail screen for one meal
  - Props: FoodLog
  - Shows: photo (large), name, macros, category, cuisine, logged time
  - Actions: edit portion, delete meal

Files to create:
- `NomNom-iOS/NomNom/Features/Timeline/TimelineViewModel.swift`
- `NomNom-iOS/NomNom/Features/Timeline/TimelineView.swift`
- `NomNom-iOS/NomNom/Features/Timeline/FoodDetailView.swift`

### 12.1.B: Weekly Recaps Screen

Show past weekly recaps with a card-based interface.

Create view models:
- `NomNom-iOS/NomNom/Features/WeeklyRecap/WeeklyRecapViewModel.swift`
  ```swift
  @MainActor
  class WeeklyRecapViewModel: ObservableObject {
      @Published var recaps: [WeeklyRecap] = []
      @Published var isLoading = false

      func loadRecaps() async {
          isLoading = true
          do {
              recaps = try await api.get(path: "/api/v1/recaps/")
          } catch {
              // handle error
          }
          isLoading = false
      }
  }
  ```

Create models:
- `NomNom-iOS/NomNom/Core/Models/WeeklyRecap.swift`

Create views:
- `NomNom-iOS/NomNom/Features/WeeklyRecap/WeeklyRecapView.swift` — list of recap cards
- `NomNom-iOS/NomNom/Features/WeeklyRecap/RecapDetailView.swift` — detail view for one recap
  - Shows: week date range, narrative, stats (avg calories, best/worst days), actionable nudge

Files to create:
- `NomNom-iOS/NomNom/Core/Models/WeeklyRecap.swift`
- `NomNom-iOS/NomNom/Features/WeeklyRecap/WeeklyRecapViewModel.swift`
- `NomNom-iOS/NomNom/Features/WeeklyRecap/WeeklyRecapView.swift`
- `NomNom-iOS/NomNom/Features/WeeklyRecap/RecapDetailView.swift`

### 12.1.C: Onboarding Flow

Multi-step screen for profile setup on first launch.

Create view models:
- `NomNom-iOS/NomNom/Features/Onboarding/OnboardingViewModel.swift`
  ```swift
  @MainActor
  class OnboardingViewModel: ObservableObject {
      @Published var step = 0  // 0-4
      @Published var age = 25
      @Published var gender = "other"
      @Published var heightCm = 170
      @Published var weightKg = 70
      @Published var activityLevel = "moderate"
      @Published var catStyle = "sassy"
      @Published var isSubmitting = false

      func nextStep() { step += 1 }
      func previousStep() { step = max(0, step - 1) }

      func submitProfile() async {
          isSubmitting = true
          do {
              try await api.post(path: "/api/v1/profile/", body: profileData)
              // Mark onboarding complete
          } catch {
              // handle error
          }
          isSubmitting = false
      }
  }
  ```

Create views:
- `NomNom-iOS/NomNom/Features/Onboarding/OnboardingView.swift` — container that shows step-based screens
- `NomNom-iOS/NomNom/Features/Onboarding/OnboardingStep1View.swift` — age, gender
- `NomNom-iOS/NomNom/Features/Onboarding/OnboardingStep2View.swift` — height, weight
- `NomNom-iOS/NomNom/Features/Onboarding/OnboardingStep3View.swift` — activity level
- `NomNom-iOS/NomNom/Features/Onboarding/OnboardingStep4View.swift` — cat style selection
- `NomNom-iOS/NomNom/Features/Onboarding/OnboardingStep5View.swift` — review + submit

Files to create:
- `NomNom-iOS/NomNom/Features/Onboarding/OnboardingViewModel.swift`
- `NomNom-iOS/NomNom/Features/Onboarding/OnboardingView.swift`
- `NomNom-iOS/NomNom/Features/Onboarding/OnboardingStep*.swift` (5 files)

Update `NomNom-iOS/NomNom/Features/Settings/LoginView.swift`:
- After successful login, check if profile exists
- If not: show OnboardingView
- If yes: navigate to main app

### 12.1.D: Settings Screen

Manage profile, preferences, cat style, logout.

Create view models:
- `NomNom-iOS/NomNom/Features/Settings/SettingsViewModel.swift`
  ```swift
  @MainActor
  class SettingsViewModel: ObservableObject {
      @Published var profile: UserProfile?
      @Published var isLoading = false

      func loadProfile() async { ... }
      func updateProfile(data: UserProfileUpdate) async { ... }
      func logout() { ... }
  }
  ```

Create views:
- `NomNom-iOS/NomNom/Features/Settings/SettingsView.swift` — list of editable profile fields + logout
  - Fields: age, gender, height, weight, activity level, cat style, allergies, dietary restrictions
  - Actions: save changes, logout

Files to create:
- `NomNom-iOS/NomNom/Features/Settings/SettingsViewModel.swift`
- `NomNom-iOS/NomNom/Features/Settings/SettingsView.swift` (refactor current LoginView)

### 12.1.E: Update ContentView with all tabs

Update `NomNom-iOS/NomNom/App/ContentView.swift`:
```swift
struct ContentView: View {
    var body: some View {
        TabView {
            DashboardView()
                .tabItem { Label("Today", systemImage: "house.fill") }

            TimelineView()
                .tabItem { Label("Timeline", systemImage: "photo.on.rectangle") }

            WeeklyRecapView()
                .tabItem { Label("Recaps", systemImage: "chart.bar.fill") }

            SettingsView()
                .tabItem { Label("Settings", systemImage: "gear") }
        }
    }
}
```

Update `NomNom-iOS/NomNom/App/NomNomApp.swift`:
- Gate: if not authenticated → LoginView
- If authenticated but no profile → OnboardingView
- If fully set up → ContentView (5-tab interface)

### 12.1.F: Test all new screens

Files to create:
- `NomNomTests/Features/Timeline/TimelineViewModelTests.swift`
- `NomNomTests/Features/WeeklyRecap/WeeklyRecapViewModelTests.swift`
- `NomNomTests/Features/Onboarding/OnboardingViewModelTests.swift`
- `NomNomTests/Features/Settings/SettingsViewModelTests.swift`

Commands:
- `xcodebuild test -scheme NomNom` — all tests pass

---

## Success Criteria

- [x] Dashboard: macro progress bars, cat mood, today's meals
- [x] Timeline: photo grid grouped by date, food detail view
- [x] Weekly Recaps: list + detail views
- [x] Onboarding: 5-step flow for first-time users
- [x] Settings: profile editing + logout
- [x] All 5 tabs functional (Today, Timeline, Recaps, Settings, Camera)
- [x] Auth gate works (login → onboarding → main app)
- [x] All tests pass
- [x] iOS app is feature-complete

## Final Status

**NomNom Complete** ✅

**Full app:**
- Backend: FastAPI with 12 AI/ML skills demonstrated
- iOS: 5-tab SwiftUI app with full user journey
- Working end-to-end on real iPhone (via ngrok)

**What you've built:**
1. Multimodal AI (Haiku vision)
2. LLM Harness Engineering (retry, fallback, structured output)
3. Prompt Engineering (Jinja2 templates, personas)
4. Guardrails + Cost Optimization
5. AI Observability (logging, rate limiting, accuracy tracking)
6. Embeddings & Vector Search (pgvector)
7. RAG (Retrieval-Augmented Generation)
8. Streaming (Server-Sent Events)
9. Async Scheduling (APScheduler)
10. Full SwiftUI app with MVVM + async/await

Perfect for MLE/AI Engineer resume.
