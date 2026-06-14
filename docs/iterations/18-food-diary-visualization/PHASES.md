# Iteration 18: Phases — Enhanced Food Diary Visualization

---

## Phase 1: Component Foundation (Day 1)

**Goal:** Build reusable progress components with proper color logic.

### 1.1 Create ProgressCircle Component

**File:** `NomNom-iOS/NomNom/Core/Components/ProgressCircle.swift`

```swift
struct ProgressCircle: View {
    let consumed: Int
    let target: Int
    let label: String
    
    var percentage: Double {
        guard target > 0 else { return 0 }
        return Double(consumed) / Double(target)
    }
    
    var color: Color {
        if percentage <= 1.0 {
            return .green
        } else if percentage <= 1.1 {
            return .yellow
        } else {
            return .red
        }
    }
    
    var body: some View {
        VStack(spacing: 8) {
            ZStack {
                Circle()
                    .stroke(Color.gray.opacity(0.3), lineWidth: 12)
                
                Circle()
                    .trim(from: 0, to: min(percentage, 1.0))
                    .stroke(color, style: StrokeStyle(lineWidth: 12, lineCap: .round))
                    .rotationEffect(.degrees(-90))
                
                VStack(spacing: 4) {
                    Text("\(Int(percentage * 100))%")
                        .font(.system(size: 28, weight: .semibold))
                        .foregroundColor(.primary)
                    
                    Text("\(consumed) / \(target) kcal")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .frame(height: 180)
            
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .animation(.easeInOut(duration: 0.3), value: percentage)
    }
}
```

**Testing checklist:**
- [ ] Displays 0–100% green
- [ ] Displays 100–110% yellow
- [ ] Displays 110%+ red
- [ ] Shows correct numbers (consumed/target)
- [ ] Circle fills smoothly on data change

### 1.2 Create NutritionProgressBar Component

**File:** `NomNom-iOS/NomNom/Core/Components/NutritionProgressBar.swift`

```swift
struct NutritionProgressBar: View {
    let nutrient: String          // "Protein", "Carbs", "Fat"
    let consumed: Double
    let target: Double
    let unit: String              // "g"
    
    var percentage: Double {
        guard target > 0 else { return 0 }
        return consumed / target
    }
    
    var color: Color {
        if percentage <= 1.0 {
            return .green
        } else if percentage <= 1.1 {
            return .yellow
        } else {
            return .red
        }
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(nutrient)
                    .font(.subheadline)
                    .foregroundColor(.primary)
                Spacer()
                Text("\(Int(consumed))/\(Int(target))\(unit)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 6)
                        .fill(Color.gray.opacity(0.2))
                    
                    RoundedRectangle(cornerRadius: 6)
                        .fill(color)
                        .frame(width: geometry.size.width * min(percentage, 1.0))
                }
            }
            .frame(height: 8)
        }
        .animation(.easeInOut(duration: 0.3), value: percentage)
    }
}
```

**Testing checklist:**
- [ ] Shows nutrient name + consumed/target
- [ ] Bar fills proportional to percentage
- [ ] Color coding works (green/yellow/red)
- [ ] Handles 0 target gracefully

---

## Phase 2: View Integration (Day 2)

**Goal:** Connect components to Food Diary screen with real data.

### 2.1 Update FoodDiaryViewModel

**File:** `NomNom-iOS/NomNom/Features/FoodDiary/FoodDiaryViewModel.swift`

**Add properties:**
```swift
@Published var calorieTarget: Int = 2000
@Published var proteinTarget: Double = 150
@Published var carbTarget: Double = 200
@Published var fatTarget: Double = 65

var totalCalories: Int { ... }  // sum from foodLogs
var totalProtein: Double { ... }
var totalCarbs: Double { ... }
var totalFat: Double { ... }
```

**Add method:**
```swift
func loadDailyTargets() async {
    do {
        let profile = try await ProfileService().getProfile()
        await MainActor.run {
            self.calorieTarget = profile.calorieTarget ?? 2000
            self.proteinTarget = Double(profile.proteinTarget ?? 150)
            self.carbTarget = Double(profile.carbTarget ?? 200)
            self.fatTarget = Double(profile.fatTarget ?? 65)
        }
    } catch {
        print("Failed to load targets: \(error)")
    }
}
```

### 2.2 Update FoodDiaryView

**File:** `NomNom-iOS/NomNom/Features/FoodDiary/FoodDiaryView.swift`

**Add to summary section (before food list):**
```swift
VStack(spacing: 16) {
    // Calorie Circle
    ProgressCircle(
        consumed: viewModel.totalCalories,
        target: viewModel.calorieTarget,
        label: "Daily Calories"
    )
    
    Divider()
    
    // Macro Bars
    NutritionProgressBar(
        nutrient: "Protein",
        consumed: viewModel.totalProtein,
        target: viewModel.proteinTarget,
        unit: "g"
    )
    
    NutritionProgressBar(
        nutrient: "Carbs",
        consumed: viewModel.totalCarbs,
        target: viewModel.carbTarget,
        unit: "g"
    )
    
    NutritionProgressBar(
        nutrient: "Fat",
        consumed: viewModel.totalFat,
        target: viewModel.fatTarget,
        unit: "g"
    )
}
.padding()
```

**Testing checklist:**
- [ ] ProgressCircle displays at top
- [ ] Three bars display in order
- [ ] Data updates when food entries change
- [ ] Targets load from ProfileService

---

## Phase 3: Polish & Animation (Day 3)

**Goal:** Smooth transitions, responsive layout, visual refinement.

### 3.1 Add Animations

Update both components to use `.animation(.easeInOut(duration: 0.3), value: percentage)` for smooth fills on data change.

### 3.2 Responsive Sizing

**ProgressCircle:**
- Circle size adapts to screen width (max 200pt)
- Text size adjusts for iPhone SE vs Max

**NutritionProgressBar:**
- Min height 12pt, fits in 1 column on all sizes
- Stack to 2 columns if space allows (optional enhancement)

### 3.3 Edge Cases Handled

- **0 target:** Show 0% (no division by zero)
- **0 consumption:** Show 0% with green
- **>100% consumption:** Show full circle/bar + red color
- **Partial consumption:** Smooth animation to percentage

---

## Phase 4: Testing & Refinement (Day 4)

**Goal:** Cross-device verification, edge case validation.

### 4.1 Device Testing

- [ ] iPhone SE (smallest screen)
- [ ] iPhone 14 (standard)
- [ ] iPhone 15 Pro Max (largest screen)
- [ ] Light & Dark modes

### 4.2 Edge Case Testing

- [ ] 0 daily consumption (circle shows 0%, green)
- [ ] 150% consumption (colors turn red, bar maxes out visually)
- [ ] 110% consumption (color yellow, bar filled)
- [ ] 50% consumption (green, half-filled)

### 4.3 Data Refresh Scenarios

- [ ] Add food entry → progress updates immediately
- [ ] Remove food entry → progress updates immediately
- [ ] Change calorie target in Settings → FoodDiary reflects new target
- [ ] Switch between days → progress resets to 0%

---

## Success Gates

**By end of Phase 4:**
- ✅ ProgressCircle displays calories with percentage, color coding, smooth animation
- ✅ NutritionProgressBar displays macros with consumed/target, color coding, smooth animation
- ✅ Both components integrated into FoodDiaryView
- ✅ Data syncs with ProfileService targets
- ✅ All edge cases handled without crashes
- ✅ Tested on 3+ device sizes
- ✅ No console errors or warnings

---

## Technical Notes

- **Color logic:** 0–100% green, 100–110% yellow, 110%+ red
- **Percentage capping:** Circle/bar show 100% filled visually if >100%, but percentage text shows actual value
- **Animation:** Use `.animation(.easeInOut(duration: 0.3), value: percentage)` for smooth transitions
- **ProfileService integration:** Call `loadDailyTargets()` in `.onAppear()` of FoodDiaryView
- **Testing approach:** Start with simulator, confirm on device (shadows/gradients render differently)
