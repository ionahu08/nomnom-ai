import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var authService: AuthService
    @StateObject private var viewModel: SettingsViewModel

    @State private var newAllergy = ""
    @State private var newCondition = ""
    @State private var customAllergy = ""
    @State private var customCondition = ""
    @State private var selectedYear = Calendar.current.component(.year, from: Date())
    @State private var selectedMonth = Calendar.current.component(.month, from: Date())
    @State private var selectedDay = Calendar.current.component(.day, from: Date())

    init() {
        _viewModel = StateObject(wrappedValue: SettingsViewModel(authService: AuthService()))
    }

    var body: some View {
        ZStack {
            NavigationStack {
                Form {

                // Health Profile Section
                Section("Health Profile") {
                    if let profile = viewModel.profile {
                        let goals = [
                            ("maintain", "Maintain"),
                            ("lean_out", "Lean Out"),
                            ("gain_muscle", "Gain Muscle"),
                            ("lose_weight", "Lose Weight")
                        ]

                        Picker("Goal", selection: Binding(
                            get: { profile.goal ?? "maintain" },
                            set: {
                                viewModel.profile?.goal = $0
                                Task {
                                    await viewModel.updateMacroTargets()
                                }
                            }
                        )) {
                            ForEach(goals, id: \.0) { value, label in
                                Text(label).tag(value)
                            }
                        }

                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Text("Birth Date")
                                Spacer()
                                if let age = profile.age {
                                    Text("\(age) years old")
                                        .foregroundColor(.secondary)
                                }
                            }

                            HStack(spacing: 8) {
                                VStack(alignment: .center, spacing: 4) {
                                    Text("Year").font(.caption2).foregroundColor(.secondary)
                                    Picker("Year", selection: Binding(
                                        get: { selectedYear },
                                        set: { newYear in
                                            selectedYear = newYear
                                            updateAgeFromDatePickers()
                                        }
                                    )) {
                                        ForEach((1920...Calendar.current.component(.year, from: Date())), id: \.self) { year in
                                            Text(String(year)).tag(year)
                                        }
                                    }
                                    .pickerStyle(.wheel)
                                    .frame(height: 100)
                                }

                                VStack(alignment: .center, spacing: 4) {
                                    Text("Month").font(.caption2).foregroundColor(.secondary)
                                    Picker("Month", selection: Binding(
                                        get: { selectedMonth },
                                        set: { newMonth in
                                            selectedMonth = newMonth
                                            updateAgeFromDatePickers()
                                        }
                                    )) {
                                        ForEach(1...12, id: \.self) { month in
                                            Text(String(format: "%02d", month)).tag(month)
                                        }
                                    }
                                    .pickerStyle(.wheel)
                                    .frame(height: 100)
                                }

                                VStack(alignment: .center, spacing: 4) {
                                    Text("Day").font(.caption2).foregroundColor(.secondary)
                                    Picker("Day", selection: Binding(
                                        get: { selectedDay },
                                        set: { newDay in
                                            let maxDay = daysInMonth(selectedMonth, year: selectedYear)
                                            selectedDay = min(newDay, maxDay)
                                            updateAgeFromDatePickers()
                                        }
                                    )) {
                                        ForEach(1...daysInMonth(selectedMonth, year: selectedYear), id: \.self) { day in
                                            Text(String(format: "%02d", day)).tag(day)
                                        }
                                    }
                                    .pickerStyle(.wheel)
                                    .frame(height: 100)
                                }
                            }
                        }

                        HStack {
                            Text("Height (cm)")
                            Spacer()
                            TextField("Height", value: Binding(
                                get: { profile.heightCm ?? 0 },
                                set: {
                                    viewModel.profile?.heightCm = $0
                                    Task {
                                        await viewModel.updateMacroTargets()
                                    }
                                }
                            ), format: .number)
                            .frame(width: 80)
                            .keyboardType(.decimalPad)
                            .textFieldStyle(.roundedBorder)
                        }

                        HStack {
                            Text("Weight (kg)")
                            Spacer()
                            TextField("Weight", value: Binding(
                                get: { profile.weightKg ?? 0 },
                                set: {
                                    viewModel.profile?.weightKg = $0
                                    Task {
                                        await viewModel.updateMacroTargets()
                                    }
                                }
                            ), format: .number)
                            .frame(width: 80)
                            .keyboardType(.decimalPad)
                            .textFieldStyle(.roundedBorder)
                        }
                    } else if viewModel.isLoading {
                        ProgressView()
                    }
                }

                // Medical Information Section - Allergies
                Section("Allergies") {
                    let commonAllergies = ["Peanuts", "Tree Nuts", "Shellfish", "Fish", "Milk", "Eggs", "Wheat", "Soy", "Sesame", "Mustard", "Other"]

                    if let allergies = viewModel.profile?.allergies, !allergies.isEmpty {
                        ForEach(allergies, id: \.self) { allergy in
                            HStack {
                                Text(allergy)
                                Spacer()
                                Button(action: {
                                    viewModel.profile?.allergies?.removeAll { $0 == allergy }
                                }) {
                                    Image(systemName: "xmark.circle.fill")
                                        .foregroundColor(.red)
                                }
                            }
                        }
                    }

                    Picker("Add allergy", selection: $newAllergy) {
                        Text("Select allergy").tag("")
                        ForEach(commonAllergies, id: \.self) { allergy in
                            Text(allergy).tag(allergy)
                        }
                    }
                    .onChange(of: newAllergy) { newValue in
                        if newValue == "Other" {
                            customAllergy = ""
                        } else if !newValue.isEmpty {
                            addAllergy()
                            newAllergy = ""
                        }
                    }

                    if newAllergy == "Other" {
                        HStack {
                            TextField("Enter allergy", text: $customAllergy)
                                .textFieldStyle(.roundedBorder)
                            Button("Add") {
                                if !customAllergy.isEmpty {
                                    addAllergy(custom: customAllergy)
                                    customAllergy = ""
                                    newAllergy = ""
                                }
                            }
                            .disabled(customAllergy.trimmingCharacters(in: .whitespaces).isEmpty)
                        }
                    }
                }

                // Medical Information Section - Conditions
                Section("Medical Conditions") {
                    let commonConditions = ["Diabetes", "Hypertension", "Heart Disease", "Asthma", "COPD", "Arthritis", "Thyroid Disease", "Kidney Disease", "Liver Disease", "Cancer", "Other"]

                    if let conditions = viewModel.profile?.medicalConditions, !conditions.isEmpty {
                        ForEach(conditions, id: \.self) { condition in
                            HStack {
                                Text(condition)
                                Spacer()
                                Button(action: {
                                    viewModel.profile?.medicalConditions?.removeAll { $0 == condition }
                                }) {
                                    Image(systemName: "xmark.circle.fill")
                                        .foregroundColor(.red)
                                }
                            }
                        }
                    }

                    Picker("Add condition", selection: $newCondition) {
                        Text("Select condition").tag("")
                        ForEach(commonConditions, id: \.self) { condition in
                            Text(condition).tag(condition)
                        }
                    }
                    .onChange(of: newCondition) { newValue in
                        if newValue == "Other" {
                            customCondition = ""
                        } else if !newValue.isEmpty {
                            addCondition()
                            newCondition = ""
                        }
                    }

                    if newCondition == "Other" {
                        HStack {
                            TextField("Enter condition", text: $customCondition)
                                .textFieldStyle(.roundedBorder)
                            Button("Add") {
                                if !customCondition.isEmpty {
                                    addCondition(custom: customCondition)
                                    customCondition = ""
                                    newCondition = ""
                                }
                            }
                            .disabled(customCondition.trimmingCharacters(in: .whitespaces).isEmpty)
                        }
                    }
                }

                // Cat Style Section
                Section("Cat Style") {
                    if let profile = viewModel.profile {
                        Picker("Choose your cat", selection: Binding(
                            get: { profile.catStyle ?? "sassy" },
                            set: { viewModel.profile?.catStyle = $0 }
                        )) {
                            Text("Sassy").tag("sassy")
                            Text("Grumpy").tag("grumpy")
                            Text("Wholesome").tag("wholesome")
                            Text("Concerned").tag("concerned")
                            Text("Neutral").tag("neutral")
                        }
                    } else if viewModel.isLoading {
                        ProgressView()
                    }
                }

                // Nutrition Goals Section
                Section("Nutrition Goals") {
                    if let profile = viewModel.profile {
                        HStack {
                            Text("Daily Calories")
                            Spacer()
                            TextField("Calories", value: Binding(
                                get: { profile.calorieTarget ?? 2000 },
                                set: { viewModel.profile?.calorieTarget = $0 }
                            ), format: .number)
                            .frame(width: 80)
                            .textFieldStyle(.roundedBorder)
                        }

                        HStack {
                            Text("Protein (g)")
                            Spacer()
                            TextField("Protein", value: Binding(
                                get: { profile.proteinTarget ?? 150 },
                                set: { viewModel.profile?.proteinTarget = $0 }
                            ), format: .number)
                            .frame(width: 80)
                            .textFieldStyle(.roundedBorder)
                        }

                        HStack {
                            Text("Carbs (g)")
                            Spacer()
                            TextField("Carbs", value: Binding(
                                get: { profile.carbTarget ?? 200 },
                                set: { viewModel.profile?.carbTarget = $0 }
                            ), format: .number)
                            .frame(width: 80)
                            .textFieldStyle(.roundedBorder)
                        }

                        HStack {
                            Text("Fat (g)")
                            Spacer()
                            TextField("Fat", value: Binding(
                                get: { profile.fatTarget ?? 65 },
                                set: { viewModel.profile?.fatTarget = $0 }
                            ), format: .number)
                            .frame(width: 80)
                            .textFieldStyle(.roundedBorder)
                        }
                    }
                }

                // Error Message
                if let error = viewModel.errorMessage {
                    Section {
                        Text(error)
                            .foregroundColor(.red)
                            .font(.caption)
                    }
                }

                // Account Section
                Section("Account") {
                    Button(role: .destructive) {
                        authService.logout()
                    } label: {
                        HStack {
                            Image(systemName: "arrow.backward.circle")
                            Text("Logout")
                                .frame(maxWidth: .infinity, alignment: .center)
                        }
                    }
                }
            }
            .navigationTitle("Settings")
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") {
                        Task {
                            await viewModel.saveProfile()
                        }
                    }
                    .disabled(viewModel.isLoading || viewModel.profile == nil)
                }
            }
            .task {
                viewModel.setAuthService(authService)
                await viewModel.loadProfile()
                // Initialize date pickers from profile age
                if let age = viewModel.profile?.age {
                    let birthDate = Calendar.current.date(byAdding: .year, value: -age, to: Date())!
                    selectedYear = Calendar.current.component(.year, from: birthDate)
                    selectedMonth = Calendar.current.component(.month, from: birthDate)
                    selectedDay = Calendar.current.component(.day, from: birthDate)
                }
            }
            }

            // Centered Toast Notification
            if viewModel.savedSuccessfully {
                VStack {
                    HStack(spacing: 12) {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.system(size: 24))
                            .foregroundColor(.white)
                        Text("Profile saved successfully!")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.white)
                    }
                    .padding(.horizontal, 24)
                    .padding(.vertical, 16)
                    .background(Color.green)
                    .cornerRadius(12)
                    .shadow(radius: 8)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .center)
                .transition(.scale.combined(with: .opacity))
            }
        }
    }

    private func daysInMonth(_ month: Int, year: Int) -> Int {
        let calendar = Calendar.current
        var dateComponents = DateComponents()
        dateComponents.year = year
        dateComponents.month = month
        dateComponents.day = 1

        guard let date = calendar.date(from: dateComponents) else { return 31 }
        guard let range = calendar.range(of: .day, in: .month, for: date) else { return 31 }
        return range.count
    }

    private func updateAgeFromDatePickers() {
        var dateComponents = DateComponents()
        dateComponents.year = selectedYear
        dateComponents.month = selectedMonth
        dateComponents.day = selectedDay

        if let birthDate = Calendar.current.date(from: dateComponents) {
            let age = Calendar.current.dateComponents([.year], from: birthDate, to: Date()).year ?? 0
            viewModel.profile?.age = max(1, age)
            Task {
                await viewModel.updateMacroTargets()
            }
        }
    }

    private func addAllergy(custom: String? = nil) {
        let value = custom ?? newAllergy
        let trimmed = value.trimmingCharacters(in: .whitespaces)
        if !trimmed.isEmpty {
            if viewModel.profile?.allergies == nil {
                viewModel.profile?.allergies = []
            }
            viewModel.profile?.allergies?.append(trimmed)
            newAllergy = ""
        }
    }

    private func addCondition(custom: String? = nil) {
        let value = custom ?? newCondition
        let trimmed = value.trimmingCharacters(in: .whitespaces)
        if !trimmed.isEmpty {
            if viewModel.profile?.medicalConditions == nil {
                viewModel.profile?.medicalConditions = []
            }
            viewModel.profile?.medicalConditions?.append(trimmed)
            newCondition = ""
        }
    }
}

#Preview {
    SettingsView()
}
