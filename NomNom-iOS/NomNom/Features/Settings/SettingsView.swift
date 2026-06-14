import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var authService: AuthService
    @StateObject private var viewModel: SettingsViewModel

    init() {
        _viewModel = StateObject(wrappedValue: SettingsViewModel(authService: AuthService()))
    }

    var body: some View {
        NavigationStack {
            Form {
                // Health Profile Section
                Section("Health Profile") {
                    if let profile = viewModel.profile {
                        HStack {
                            Text("Goal")
                            Spacer()
                            Picker("", selection: Binding(
                                get: { profile.goal ?? "maintain" },
                                set: { viewModel.profile?.goal = $0 }
                            )) {
                                Text("Maintain Weight").tag("maintain")
                                Text("Lose Weight").tag("lose_weight")
                                Text("Gain Muscle").tag("gain_muscle")
                                Text("Shape Figure").tag("shape_figure")
                            }
                            .pickerStyle(.segmented)
                        }

                        HStack {
                            Text("Age")
                            Spacer()
                            TextField("Age", value: Binding(
                                get: { profile.age ?? 0 },
                                set: { viewModel.profile?.age = $0 }
                            ), format: .number)
                            .frame(width: 60)
                            .keyboardType(.numberPad)
                            .textFieldStyle(.roundedBorder)
                        }

                        HStack {
                            Text("Race")
                            Spacer()
                            TextField("Optional", text: Binding(
                                get: { profile.race ?? "" },
                                set: { viewModel.profile?.race = $0.isEmpty ? nil : $0 }
                            ))
                            .textFieldStyle(.roundedBorder)
                        }

                        HStack {
                            Text("Height (cm)")
                            Spacer()
                            TextField("Height", value: Binding(
                                get: { profile.heightCm ?? 0 },
                                set: { viewModel.profile?.heightCm = $0 }
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
                                set: { viewModel.profile?.weightKg = $0 }
                            ), format: .number)
                            .frame(width: 80)
                            .keyboardType(.decimalPad)
                            .textFieldStyle(.roundedBorder)
                        }
                    } else if viewModel.isLoading {
                        ProgressView()
                    }
                }

                // Medical Information Section
                Section("Medical Information (Optional)") {
                    if let profile = viewModel.profile {
                        NavigationLink(destination: MedicalInfoView(profile: Binding(
                            get: { profile },
                            set: { viewModel.profile = $0 }
                        ))) {
                            HStack {
                                Text("Allergies & Conditions")
                                Spacer()
                                if !(profile.allergies?.isEmpty ?? true) || !(profile.medicalConditions?.isEmpty ?? true) {
                                    Image(systemName: "checkmark.circle.fill")
                                        .foregroundColor(.green)
                                }
                                Image(systemName: "chevron.right")
                                    .foregroundColor(.gray)
                            }
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
                            Image(systemName: "arrowtriangleright.turn.counterclockwise")
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
                await viewModel.loadProfile()
            }
        }
    }
}

#Preview {
    SettingsView()
}
