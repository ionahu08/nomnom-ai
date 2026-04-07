import Foundation

@MainActor
class SettingsViewModel: ObservableObject {
    @Published var profile: UserProfile?
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var savedSuccessfully = false

    private let profileService = ProfileService()
    private let authService: AuthService

    init(authService: AuthService) {
        self.authService = authService
    }

    func loadProfile() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            profile = try await profileService.getProfile()
        } catch {
            errorMessage = "Failed to load profile: \(error.localizedDescription)"
        }
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
