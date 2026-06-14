# Iteration 18: Enhanced Food Diary Visualization

**Duration:** 4 days  
**Start Date:** 2026-06-14  
**Status:** 🚀 Starting

---

## Goal

Replace plain text nutrition displays with modern, intuitive progress visualizations on the Food Diary screen. Users should instantly see how close they are to their daily nutritional goals via visual indicators.

---

## What's Already Built

✅ **Iteration 17 — Personalized Nutrition Profile**
- Backend: Health profile API with personalized calorie/macro targets
- iOS: Settings screen to input health data and set goals
- Dynamic calculation: Targets adjust based on age, weight, activity, goal
- API: Food Diary can fetch daily targets via profile endpoint

✅ **Food Diary Screen (Current State)**
- Lists food entries for the day
- Shows summary: Total calories, protein, carbs, fat (as plain text)
- No visual progress indication

---

## What We're Building

### 1. **Progress Bar Component** (for P/C/F)
- Horizontal progress bar for each macro (Protein, Carbs, Fat)
- Shows: consumed / target (e.g., "45g / 150g")
- Color changes based on progress:
  - Green: 0-100% (on track)
  - Yellow: 100-110% (slightly over, acceptable)
  - Red: 110%+ (significantly over)
- Width represents percentage of daily goal consumed

### 2. **Circular Progress** (for Calories)
- Center of Food Diary summary
- Large, prominent circular progress indicator
- Shows: consumed / target calories (e.g., "1450 / 2000 kcal")
- Same color coding (green/yellow/red)
- Percentage displayed in center of circle

### 3. **Layout**
```
┌─────────────────────────────┐
│  Food Diary — June 14       │
├─────────────────────────────┤
│                             │
│        ╭─────────╮          │
│       ╱   1450   ╲         │
│      │  / 2000   │         │  ← Calories (Circle)
│       ╲   kcal   ╱         │
│        ╰─────────╯          │
│                             │
├─────────────────────────────┤
│ Protein:  ▓▓▓▓░░ 45/150g   │  ← Progress Bars
│ Carbs:    ▓▓▓░░░ 120/200g  │
│ Fat:      ▓▓▓▓▓░ 55/65g    │
├─────────────────────────────┤
│ [Food entries list below]   │
└─────────────────────────────┘
```

---

## Success Criteria

✅ Progress bars display correctly for all macros  
✅ Circular progress shows correct percentage for calories  
✅ Colors change based on consumption level (green/yellow/red)  
✅ All animations smooth and responsive  
✅ Handles edge cases: 0 targets, 0 consumption, >100% consumption  
✅ Displays on device without crashing  
✅ Percentages update when food entries change  
✅ Works on all screen sizes (iPhone SE to Max)

---

## Technical Details

### Data Flow
```
Food Diary View
    ↓
ProfileService.getProfile() → fetches daily targets
    ↓
Sum food log entries → daily totals (calories, macros)
    ↓
FoodDiaryViewModel
    ↓
Calculate percentages
    ↓
Render circles + bars
```

### Files to Modify
- `NomNom-iOS/NomNom/Features/FoodDiary/FoodDiaryView.swift` — Main view
- `NomNom-iOS/NomNom/Features/FoodDiary/FoodDiaryViewModel.swift` — Add percentage calculations
- `NomNom-iOS/NomNom/Core/Components/ProgressCircle.swift` — **NEW** circular progress component
- `NomNom-iOS/NomNom/Core/Components/NutritionProgressBar.swift` — **NEW** macro progress bar component

### New Components Needed

**1. ProgressCircle.swift**
```swift
struct ProgressCircle: View {
    let consumed: Int
    let target: Int
    let label: String
    
    var percentage: Double { ... }
    var color: Color { ... }  // green/yellow/red based on %
    var body: some View { ... }
}
```

**2. NutritionProgressBar.swift**
```swift
struct NutritionProgressBar: View {
    let nutrient: String     // "Protein", "Carbs", "Fat"
    let consumed: Double
    let target: Double
    let unit: String         // "g"
    
    var percentage: Double { ... }
    var color: Color { ... }
    var body: some View { ... }
}
```

---

## Resume Skills

- **SwiftUI:** Custom shapes (circles), progress indicators, animations
- **Data Binding:** Real-time updates when food entries change
- **Color Design:** Semantic color coding (health states)
- **Responsive Layout:** Adapting to different screen sizes
- **Component Reusability:** Progress components used multiple places

---

## Notes

- Use `Canvas` for circle drawing (or `Circle.trim()` + `stroke()`)
- Consider using `@Published` in ViewModel to trigger re-renders
- Test on actual device — simulators sometimes render shadows/gradients differently
- Animation: Use `.animation(.easeInOut, value: percentage)` for smooth transitions

