import SwiftUI

struct ContentView: View {
    @EnvironmentObject var authService: AuthService

    var body: some View {
        TabView {
            CameraView()
                .tabItem {
                    Image(systemName: "camera.fill")
                    Text("Camera")
                }

            TodayView()
                .tabItem {
                    Image(systemName: "list.bullet")
                    Text("Today")
                }
        }
        .tint(NomNomColors.primary)
    }
}
