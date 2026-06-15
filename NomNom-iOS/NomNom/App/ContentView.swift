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

            DiaryView()
                .tabItem {
                    Image(systemName: "calendar")
                    Text("Food Diary")
                }

            WeeklyNutritionView()
                .tabItem {
                    Image(systemName: "chart.bar.fill")
                    Text("Weekly")
                }

            SettingsView()
                .tabItem {
                    Image(systemName: "gearshape.fill")
                    Text("Settings")
                }
        }
        .tint(NomNomColors.primary)
    }
}
