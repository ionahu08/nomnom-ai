import SwiftUI

struct InsightsView: View {
    @StateObject private var viewModel = InsightsViewModel()

    var body: some View {
        NavigationStack {
            ZStack {
                LinearGradient(
                    colors: [
                        Color(red: 0.09, green: 0.07, blue: 0.13),
                        Color(red: 0.14, green: 0.09, blue: 0.07),
                    ],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()

                VStack(spacing: 16) {
                    if viewModel.isLoading {
                        ProgressView()
                            .tint(NomNomColors.primary)
                            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .center)
                    } else if let errorMessage = viewModel.errorMessage {
                        VStack(spacing: 12) {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .font(.title)
                                .foregroundColor(NomNomColors.danger)
                            Text(errorMessage)
                                .font(.body)
                                .foregroundColor(NomNomColors.textSecondary)
                                .multilineTextAlignment(.center)
                        }
                        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .center)
                        .padding()
                    } else {
                        ScrollView {
                            VStack(spacing: 20) {
                                // Coming soon placeholder
                                VStack(spacing: 16) {
                                    Text("🔮")
                                        .font(.system(size: 48))
                                    Text("Insights Coming Soon")
                                        .font(.headline)
                                        .foregroundColor(NomNomColors.textPrimary)
                                    Text("AI-powered analysis of your eating patterns")
                                        .font(.caption)
                                        .foregroundColor(NomNomColors.textSecondary)
                                }
                                .frame(maxWidth: .infinity)
                                .padding(24)
                                .background(NomNomColors.surface)
                                .cornerRadius(16)
                                .padding(16)
                            }
                        }
                    }
                }
            }
            .navigationTitle("📊 Insights")
            .navigationBarTitleDisplayMode(.inline)
            .toolbarColorScheme(.dark, for: .navigationBar)
        }
        .task {
            await viewModel.loadInsights()
        }
    }
}

#Preview {
    InsightsView()
        .environmentObject(AuthService())
}
