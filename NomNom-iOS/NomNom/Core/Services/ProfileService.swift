import Foundation

class ProfileService {
    private let api = APIClient.shared

    func getProfile() async throws -> UserProfile {
        do {
            return try await api.get(path: "/api/v1/profile")
        } catch APIError.serverError(404) {
            return createDefaultProfile()
        }
    }

    func updateProfile(_ profile: UserProfile) async throws -> UserProfile {
        do {
            return try await api.patch(path: "/api/v1/profile", body: profile)
        } catch APIError.serverError(404) {
            return try await api.post(path: "/api/v1/profile", body: profile)
        } catch let error as APIError {
            print("ProfileService.updateProfile error: \(error)")
            throw error
        }
    }

    private func createDefaultProfile() -> UserProfile {
        return UserProfile(
            age: 25,
            gender: "other",
            heightCm: 170,
            weightKg: 70,
            activityLevel: "moderate",
            goal: "maintain",
            calorieTarget: 2000,
            proteinTarget: 150,
            carbTarget: 200,
            fatTarget: 65,
            catStyle: "sassy",
            dietaryRestrictions: nil,
            allergies: nil,
            cuisinePreferences: nil,
            medicalConditions: nil,
            surgeries: nil,
            medications: nil
        )
    }
}
