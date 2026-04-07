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
                        viewModel.logout()
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
