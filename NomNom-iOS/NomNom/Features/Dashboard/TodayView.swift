import SwiftUI

struct TodayView: View {
    @StateObject private var viewModel = TodayViewModel()

    var body: some View {
        NavigationStack {
            ZStack {
                NomNomColors.background.ignoresSafeArea()

                if viewModel.isLoading && viewModel.logs.isEmpty {
                    ProgressView()
                        .tint(NomNomColors.primary)
                } else if viewModel.logs.isEmpty {
                    emptyState
                } else {
                    logsList
                }
            }
            .navigationTitle("Today")
            .navigationBarTitleDisplayMode(.inline)
            .toolbarColorScheme(.dark, for: .navigationBar)
            .task {
                await viewModel.loadTodayLogs()
            }
            .refreshable {
                await viewModel.loadTodayLogs()
            }
        }
    }

    // MARK: - Empty state

    private var emptyState: some View {
        VStack(spacing: 16) {
            Text("😴")
                .font(.system(size: 64))

            Text("No food logged today")
                .font(.headline)
                .foregroundColor(NomNomColors.textPrimary)

            Text("Take a photo of your food\nand the cat will judge it")
                .font(.body)
                .foregroundColor(NomNomColors.textSecondary)
                .multilineTextAlignment(.center)
        }
    }

    // MARK: - Logs list

    private var logsList: some View {
        ScrollView {
            VStack(spacing: 8) {
                // Today's summary
                todaySummary
                    .padding(.horizontal, 16)
                    .padding(.top, 8)

                // Food log cards
                ForEach(viewModel.logs) { log in
                    FoodLogCard(log: log)
                        .padding(.horizontal, 16)
                        .swipeActions(edge: .trailing) {
                            Button(role: .destructive) {
                                Task { await viewModel.deleteLog(id: log.id) }
                            } label: {
                                Label("Delete", systemImage: "trash")
                            }
                        }
                }
            }
            .padding(.bottom, 16)
        }
    }

    // MARK: - Summary

    private var todaySummary: some View {
        let totalCals = viewModel.logs.reduce(0) { $0 + $1.calories }
        let totalProtein = viewModel.logs.reduce(0.0) { $0 + $1.proteinG }
        let totalCarbs = viewModel.logs.reduce(0.0) { $0 + $1.carbsG }
        let totalFat = viewModel.logs.reduce(0.0) { $0 + $1.fatG }

        return VStack(spacing: 8) {
            Text("\(viewModel.logs.count) meal\(viewModel.logs.count == 1 ? "" : "s") today")
                .font(.subheadline)
                .foregroundColor(NomNomColors.textSecondary)

            HStack(spacing: 16) {
                summaryItem(value: "\(totalCals)", label: "kcal", color: NomNomColors.primary)
                summaryItem(value: String(format: "%.0f", totalProtein), label: "protein", color: NomNomColors.success)
                summaryItem(value: String(format: "%.0f", totalCarbs), label: "carbs", color: NomNomColors.warning)
                summaryItem(value: String(format: "%.0f", totalFat), label: "fat", color: NomNomColors.danger)
            }
        }
        .padding()
        .background(NomNomColors.surface)
        .cornerRadius(16)
    }

    private func summaryItem(value: String, label: String, color: Color) -> some View {
        VStack(spacing: 2) {
            Text(value)
                .font(.headline)
                .foregroundColor(color)
            Text(label)
                .font(.caption2)
                .foregroundColor(NomNomColors.textSecondary)
        }
        .frame(maxWidth: .infinity)
    }
}
