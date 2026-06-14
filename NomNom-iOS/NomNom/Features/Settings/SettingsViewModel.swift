import Foundation

@MainActor
class SettingsViewModel: ObservableObject {
    @Published var profile: UserProfile?
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var savedSuccessfully = false

    private let profileService = ProfileService()
    private var authService: AuthService

    init(authService: AuthService) {
        self.authService = authService
    }

    func setAuthService(_ authService: AuthService) {
        self.authService = authService
    }

    func loadProfile() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            profile = try await profileService.getProfile()
            await updateMacroTargets()
        } catch {
            errorMessage = "Failed to load profile: \(error.localizedDescription)"
        }
    }

    func updateMacroTargets() async {
        guard let profile = profile else { return }

        let targets = calculateMacroTargets(
            age: profile.age ?? 25,
            gender: profile.gender ?? "other",
            heightCm: profile.heightCm ?? 170,
            weightKg: profile.weightKg ?? 70,
            activityLevel: profile.activityLevel ?? "moderate",
            goal: profile.goal ?? "maintain"
        )

        self.profile?.calorieTarget = targets.calories
        self.profile?.proteinTarget = targets.protein
        self.profile?.carbTarget = targets.carbs
        self.profile?.fatTarget = targets.fat
    }

    private func calculateMacroTargets(
        age: Int,
        gender: String,
        heightCm: Double,
        weightKg: Double,
        activityLevel: String,
        goal: String
    ) -> (calories: Int, protein: Int, carbs: Int, fat: Int) {
        // Mifflin-St Jeor formula for BMR
        let bmr: Double
        if gender.lowercased() == "male" {
            bmr = 10 * weightKg + 6.25 * heightCm - 5 * Double(age) + 5
        } else {
            bmr = 10 * weightKg + 6.25 * heightCm - 5 * Double(age) - 161
        }

        // Activity level multiplier
        let activityMultiplier: Double
        switch activityLevel.lowercased() {
        case "sedentary": activityMultiplier = 1.2
        case "light": activityMultiplier = 1.375
        case "moderate": activityMultiplier = 1.55
        case "active": activityMultiplier = 1.725
        case "very_active": activityMultiplier = 1.9
        default: activityMultiplier = 1.55
        }

        let tdee = Int(bmr * activityMultiplier)

        // Goal-based adjustment
        let calorieTarget: Int
        switch goal.lowercased() {
        case "lose_weight": calorieTarget = Int(Double(tdee) * 0.85)
        case "gain_muscle": calorieTarget = Int(Double(tdee) * 1.1)
        case "shape_figure": calorieTarget = Int(Double(tdee) * 0.95)
        default: calorieTarget = tdee // maintain
        }

        // Macro splits by goal
        let (proteinPercent, carbPercent, fatPercent): (Double, Double, Double)
        switch goal.lowercased() {
        case "lose_weight":
            (proteinPercent, carbPercent, fatPercent) = (0.30, 0.40, 0.30)
        case "gain_muscle":
            (proteinPercent, carbPercent, fatPercent) = (0.35, 0.45, 0.20)
        case "shape_figure":
            (proteinPercent, carbPercent, fatPercent) = (0.35, 0.40, 0.25)
        default: // maintain
            (proteinPercent, carbPercent, fatPercent) = (0.25, 0.50, 0.25)
        }

        let protein = Int(Double(calorieTarget) * proteinPercent / 4)
        let carbs = Int(Double(calorieTarget) * carbPercent / 4)
        let fat = Int(Double(calorieTarget) * fatPercent / 9)

        return (calorieTarget, protein, carbs, fat)
    }

    func saveProfile() async {
        guard let profile = profile else {
            errorMessage = "No profile to save"
            return
        }

        isLoading = true
        errorMessage = nil
        savedSuccessfully = false
        defer { isLoading = false }

        await updateMacroTargets()

        do {
            self.profile = try await profileService.updateProfile(profile)
            savedSuccessfully = true
            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                self.savedSuccessfully = false
            }
        } catch {
            errorMessage = "Failed to save profile: \(error.localizedDescription)"
        }
    }

    func logout() {
        authService.logout()
    }
}
