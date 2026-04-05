import Foundation
import SwiftUI

@MainActor
class AuthService: ObservableObject {
    @Published var isAuthenticated = false
    @Published var errorMessage: String?

    private let api = APIClient.shared
    private let tokenKey = "nomnom_auth_token"
    private let emailKey = "nomnom_user_email"

    init() {
        if let token = KeychainService.load(key: tokenKey) {
            api.setToken(token)
            isAuthenticated = true
        }
        api.onUnauthorized = { [weak self] in
            self?.logout()
        }
    }

    func register(email: String, password: String) async {
        do {
            let response: TokenResponse = try await api.post(
                path: "/api/v1/auth/register",
                body: AuthRequest(email: email, password: password)
            )
            saveToken(response.accessToken, email: email)
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func login(email: String, password: String) async {
        do {
            let response: TokenResponse = try await api.post(
                path: "/api/v1/auth/login",
                body: AuthRequest(email: email, password: password)
            )
            saveToken(response.accessToken, email: email)
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func logout() {
        KeychainService.delete(key: tokenKey)
        UserDefaults.standard.removeObject(forKey: emailKey)
        api.setToken(nil)
        isAuthenticated = false
    }

    private func saveToken(_ token: String, email: String) {
        KeychainService.save(key: tokenKey, value: token)
        UserDefaults.standard.set(email, forKey: emailKey)
        api.setToken(token)
        isAuthenticated = true
        errorMessage = nil
    }
}
