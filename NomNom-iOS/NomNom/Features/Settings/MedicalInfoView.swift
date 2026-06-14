import SwiftUI

struct MedicalInfoView: View {
    @Binding var profile: UserProfile
    @Environment(\.dismiss) var dismiss

    @State private var newAllergy = ""
    @State private var newCondition = ""
    @State private var newSurgery = ""
    @State private var newMedication = ""

    var body: some View {
        NavigationStack {
            Form {
                // MARK: - Allergies
                Section("Allergies") {
                    if let allergies = profile.allergies, !allergies.isEmpty {
                        ForEach(allergies, id: \.self) { allergy in
                            HStack {
                                Text(allergy)
                                Spacer()
                                Button(action: {
                                    profile.allergies?.removeAll { $0 == allergy }
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
                    if let conditions = profile.medicalConditions, !conditions.isEmpty {
                        ForEach(conditions, id: \.self) { condition in
                            HStack {
                                Text(condition)
                                Spacer()
                                Button(action: {
                                    profile.medicalConditions?.removeAll { $0 == condition }
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
                    if let surgeries = profile.surgeries, !surgeries.isEmpty {
                        ForEach(surgeries, id: \.self) { surgery in
                            HStack {
                                Text(surgery)
                                Spacer()
                                Button(action: {
                                    profile.surgeries?.removeAll { $0 == surgery }
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
                    if let medications = profile.medications, !medications.isEmpty {
                        ForEach(medications, id: \.self) { medication in
                            HStack {
                                Text(medication)
                                Spacer()
                                Button(action: {
                                    profile.medications?.removeAll { $0 == medication }
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
    }

    private func addAllergy() {
        let trimmed = newAllergy.trimmingCharacters(in: .whitespaces)
        if !trimmed.isEmpty {
            if profile.allergies == nil {
                profile.allergies = []
            }
            profile.allergies?.append(trimmed)
            newAllergy = ""
        }
    }

    private func addCondition() {
        let trimmed = newCondition.trimmingCharacters(in: .whitespaces)
        if !trimmed.isEmpty {
            if profile.medicalConditions == nil {
                profile.medicalConditions = []
            }
            profile.medicalConditions?.append(trimmed)
            newCondition = ""
        }
    }

    private func addSurgery() {
        let trimmed = newSurgery.trimmingCharacters(in: .whitespaces)
        if !trimmed.isEmpty {
            if profile.surgeries == nil {
                profile.surgeries = []
            }
            profile.surgeries?.append(trimmed)
            newSurgery = ""
        }
    }

    private func addMedication() {
        let trimmed = newMedication.trimmingCharacters(in: .whitespaces)
        if !trimmed.isEmpty {
            if profile.medications == nil {
                profile.medications = []
            }
            profile.medications?.append(trimmed)
            newMedication = ""
        }
    }
}

#Preview {
    MedicalInfoView(profile: .constant(UserProfile(
        allergies: ["Peanuts", "Shellfish"],
        medicalConditions: ["Pre-diabetes"]
    )))
}
