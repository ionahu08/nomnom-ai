import SwiftUI

@main
struct NomNomApp: App {
    @StateObject private var authService = AuthService()

    var body: some Scene {
        WindowGroup {
            if authService.isAuthenticated {
                ContentView()
                    .environmentObject(authService)
                    .preferredColorScheme(.dark)
            } else {
                LoginView()
                    .environmentObject(authService)
                    .preferredColorScheme(.dark)
            }
        }
    }
}
