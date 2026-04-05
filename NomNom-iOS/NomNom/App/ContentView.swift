import SwiftUI

struct ContentView: View {
    @EnvironmentObject var authService: AuthService

    var body: some View {
        TabView {
            Text("Camera - Coming in S4")
                .foregroundColor(NomNomColors.textPrimary)
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(NomNomColors.background)
                .tabItem {
                    Image(systemName: "camera.fill")
                    Text("Camera")
                }

            Text("Today - Coming in S4")
                .foregroundColor(NomNomColors.textPrimary)
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(NomNomColors.background)
                .tabItem {
                    Image(systemName: "list.bullet")
                    Text("Today")
                }
        }
        .tint(NomNomColors.primary)
    }
}
