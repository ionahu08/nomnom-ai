import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var authService: AuthService
    @StateObject private var viewModel: SettingsViewModel

    @State private var newAllergy = ""
    @State private var newCondition = ""

    init() {
        _viewModel = StateObject(wrappedValue: SettingsViewModel(authService: AuthService()))
    }

    var body: some View {
        NavigationStack {
            Form {
                // Health Profile Section
                Section("Health Profile") {
                    if let profile = viewModel.profile {
                        let goals = [
                            ("maintain", "Maintain Weight"),
                            ("lose_weight", "Lose Weight"),
                            ("gain_muscle", "Gain Muscle"),
                            ("shape_figure", "Shape Figure")
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

                        HStack {
                            Text("Age")
                            Spacer()
                            TextField("Age", value: Binding(
                                get: { profile.age ?? 0 },
                                set: {
                                    viewModel.profile?.age = $0
                                    Task {
                                        await viewModel.updateMacroTargets()
                                    }
                                }
                            ), format: .number)
                            .frame(width: 60)
                            .keyboardType(.numberPad)
                            .textFieldStyle(.roundedBorder)
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
                    let commonAllergies = ["Peanuts", "Tree Nuts", "Shellfish", "Fish", "Milk", "Eggs", "Wheat", "Soy", "Sesame", "Mustard"]

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
                        if !newValue.isEmpty {
                            addAllergy()
                        }
                    }
                }

                // Medical Information Section - Conditions
                Section("Medical Conditions") {
                    let commonConditions = ["Diabetes", "Hypertension", "Heart Disease", "Asthma", "COPD", "Arthritis", "Thyroid Disease", "Kidney Disease", "Liver Disease", "Cancer"]

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
                        if !newValue.isEmpty {
                            addCondition()
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

                // Save Status
                if viewModel.savedSuccessfully {
                    Section {
                        HStack {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.green)
                            Text("Saved!")
                                .foregroundColor(.green)
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
            }
        }
    }

    private func addAllergy() {
        let trimmed = newAllergy.trimmingCharacters(in: .whitespaces)
        if !trimmed.isEmpty {
            if viewModel.profile?.allergies == nil {
                viewModel.profile?.allergies = []
            }
            viewModel.profile?.allergies?.append(trimmed)
            newAllergy = ""
        }
    }

    private func addCondition() {
        let trimmed = newCondition.trimmingCharacters(in: .whitespaces)
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
