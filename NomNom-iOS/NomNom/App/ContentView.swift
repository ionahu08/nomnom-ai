import SwiftUI

struct ContentView: View {
    @EnvironmentObject var authService: AuthService
    @State private var selectedTab = 0
    private let tabs = ["Camera", "Food Diary", "Insight", "Settings"]

    var body: some View {
        ZStack {
            TabView(selection: $selectedTab) {
                CameraView()
                    .tag(0)
                    .tabItem {
                        Image(systemName: "camera.fill")
                        Text("Camera")
                    }

                DiaryView()
                    .tag(1)
                    .tabItem {
                        Image(systemName: "calendar")
                        Text("Food Diary")
                    }

                WeeklyNutritionView()
                    .tag(2)
                    .tabItem {
                        Image(systemName: "chart.bar.fill")
                        Text("Insight")
                    }

                SettingsView()
                    .tag(3)
                    .tabItem {
                        Image(systemName: "gearshape.fill")
                        Text("Settings")
                    }
            }
            .tint(NomNomColors.primary)
            .gesture(swipeGesture())
        }
    }

    private func swipeGesture() -> some Gesture {
        DragGesture()
            .onEnded { value in
                let horizontalDistance = value.translation.width
                let verticalDistance = value.translation.height

                if abs(horizontalDistance) > abs(verticalDistance) {
                    if horizontalDistance < -50 {
                        withAnimation {
                            if selectedTab < tabs.count - 1 {
                                selectedTab += 1
                            }
                        }
                    } else if horizontalDistance > 50 {
                        withAnimation {
                            if selectedTab > 0 {
                                selectedTab -= 1
                            }
                        }
                    }
                }
            }
    }
}
