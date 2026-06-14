import SwiftUI

struct MedicalInfoView: View {
    @ObservedObject var viewModel: SettingsViewModel
    @Environment(\.dismiss) var dismiss

    @State private var newAllergy = ""
    @State private var newCondition = ""
    @State private var newSurgery = ""
    @State private var newMedication = ""

    var body: some View {
        Form {
                // MARK: - Allergies
                Section("Allergies") {
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

                    HStack {
                        TextField("Add allergy...", text: $newAllergy)
                        Button(action: addAllergy) {
                            Image(systemName: "plus.circle.fill")
                                .foregroundColor(.blue)
                        }
                        .disabled(newAllergy.trimmingCharacters(in: .whitespaces).isEmpty)
                    }
                }

                // MARK: - Medical Conditions
                Section("Medical Conditions") {
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

                    HStack {
                        TextField("Add condition...", text: $newCondition)
                        Button(action: addCondition) {
                            Image(systemName: "plus.circle.fill")
                                .foregroundColor(.blue)
                        }
                        .disabled(newCondition.trimmingCharacters(in: .whitespaces).isEmpty)
                    }
                }

                // MARK: - Surgeries
                Section("Past Surgeries") {
                    if let surgeries = viewModel.profile?.surgeries, !surgeries.isEmpty {
                        ForEach(surgeries, id: \.self) { surgery in
                            HStack {
                                Text(surgery)
                                Spacer()
                                Button(action: {
                                    viewModel.profile?.surgeries?.removeAll { $0 == surgery }
                                }) {
                                    Image(systemName: "xmark.circle.fill")
                                        .foregroundColor(.red)
                                }
                            }
                        }
                    }

                    HStack {
                        TextField("Add surgery...", text: $newSurgery)
                        Button(action: addSurgery) {
                            Image(systemName: "plus.circle.fill")
                                .foregroundColor(.blue)
                        }
                        .disabled(newSurgery.trimmingCharacters(in: .whitespaces).isEmpty)
                    }
                }

                // MARK: - Medications
                Section("Current Medications") {
                    if let medications = viewModel.profile?.medications, !medications.isEmpty {
                        ForEach(medications, id: \.self) { medication in
                            HStack {
                                Text(medication)
                                Spacer()
                                Button(action: {
                                    viewModel.profile?.medications?.removeAll { $0 == medication }
                                }) {
                                    Image(systemName: "xmark.circle.fill")
                                        .foregroundColor(.red)
                                }
                            }
                        }
                    }

                    HStack {
                        TextField("Add medication...", text: $newMedication)
                        Button(action: addMedication) {
                            Image(systemName: "plus.circle.fill")
                                .foregroundColor(.blue)
                        }
                        .disabled(newMedication.trimmingCharacters(in: .whitespaces).isEmpty)
                    }
                }

                Section {
                    Text("This information helps NomNom provide safer, more personalized recommendations.")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
            }
            .navigationTitle("Medical Information")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
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

    private func addSurgery() {
        let trimmed = newSurgery.trimmingCharacters(in: .whitespaces)
        if !trimmed.isEmpty {
            if viewModel.profile?.surgeries == nil {
                viewModel.profile?.surgeries = []
            }
            viewModel.profile?.surgeries?.append(trimmed)
            newSurgery = ""
        }
    }

    private func addMedication() {
        let trimmed = newMedication.trimmingCharacters(in: .whitespaces)
        if !trimmed.isEmpty {
            if viewModel.profile?.medications == nil {
                viewModel.profile?.medications = []
            }
            viewModel.profile?.medications?.append(trimmed)
            newMedication = ""
        }
    }
}

// Preview removed - requires full app context to initialize
// Test in Xcode by building and navigating to Settings > Medical Information
