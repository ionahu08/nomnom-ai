import Foundation

class ProfileService {
    private let api = APIClient.shared

    func getProfile() async throws -> UserProfile {
        return try await api.get(path: "/api/v1/profile")
    }

    func updateProfile(_ profile: UserProfile) async throws -> UserProfile {
        return try await api.post(path: "/api/v1/profile", body: profile)
    }
}
