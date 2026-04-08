import SwiftUI

struct TodayView: View {
    @StateObject private var viewModel = TodayViewModel()
    @State private var showRecommendation = false

    var body: some View {
        NavigationStack {
            ZStack {
                NomNomColors.background.ignoresSafeArea()

                VStack {
                    // Error message (if any)
                    if let error = viewModel.errorMessage {
                        HStack {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .foregroundColor(NomNomColors.danger)
                            Text(error)
                                .font(.caption)
                                .foregroundColor(NomNomColors.danger)
                            Spacer()
                            Button(action: { viewModel.errorMessage = nil }) {
                                Image(systemName: "xmark")
                                    .foregroundColor(NomNomColors.danger)
                            }
                        }
                        .padding()
                        .background(NomNomColors.danger.opacity(0.1))
                        .cornerRadius(8)
                        .padding(16)
                    }

                    if viewModel.isLoading && viewModel.logs.isEmpty {
                        ProgressView()
                            .tint(NomNomColors.primary)
                    } else if viewModel.logs.isEmpty {
                        emptyState
                    } else {
                        logsList
                    }
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
            .sheet(isPresented: $showRecommendation) {
                recommendationModal
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

                // Food log cards (chronological order)
                ForEach(viewModel.logs) { log in
                    VStack(alignment: .leading, spacing: 8) {
                        Text(formatTime(log.loggedAt))
                            .font(.caption)
                            .foregroundColor(NomNomColors.textSecondary)
                            .padding(.horizontal, 16)

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

        return VStack(spacing: 12) {
            HStack {
                Text("\(viewModel.logs.count) meal\(viewModel.logs.count == 1 ? "" : "s") today")
                    .font(.subheadline)
                    .foregroundColor(NomNomColors.textSecondary)

                Spacer()

                Button(action: {
                    Task {
                        await viewModel.loadRecommendation()
                        showRecommendation = true
                    }
                }) {
                    HStack(spacing: 6) {
                        if viewModel.isLoadingRecommendation {
                            ProgressView()
                                .tint(NomNomColors.primary)
                                .scaleEffect(0.8)
                        } else {
                            Image(systemName: "sparkles")
                        }
                        Text("What to eat?")
                            .font(.subheadline.bold())
                    }
                    .foregroundColor(NomNomColors.primary)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(NomNomColors.primary.opacity(0.1))
                    .cornerRadius(8)
                }
                .disabled(viewModel.isLoadingRecommendation)
            }

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

    private func formatTime(_ isoString: String) -> String {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        guard let date = formatter.date(from: isoString) else { return isoString }

        let timeFormatter = DateFormatter()
        timeFormatter.dateFormat = "h:mm a"
        return timeFormatter.string(from: date)
    }

    // MARK: - Recommendation modal

    private var recommendationModal: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    if let recommendation = viewModel.recommendation {
                        Text(recommendation)
                            .font(.body)
                            .foregroundColor(NomNomColors.textPrimary)
                            .padding()
                            .background(NomNomColors.surface)
                            .cornerRadius(12)

                        HStack(spacing: 8) {
                            Image(systemName: "book.fill")
                                .foregroundColor(NomNomColors.primary.opacity(0.6))
                            Text("Based on \(viewModel.recommendationKBEntries) nutrition tip\(viewModel.recommendationKBEntries == 1 ? "" : "s")")
                                .font(.caption)
                                .foregroundColor(NomNomColors.textSecondary)
                        }
                        .padding(.horizontal)
                    } else if viewModel.isLoadingRecommendation {
                        VStack(spacing: 12) {
                            ProgressView()
                                .tint(NomNomColors.primary)
                                .scaleEffect(1.2)
                            Text("Getting a suggestion...")
                                .foregroundColor(NomNomColors.textSecondary)
                        }
                        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .center)
                    }
                }
                .padding(16)
            }
            .navigationTitle("What to Eat Next")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") { showRecommendation = false }
                        .foregroundColor(NomNomColors.primary)
                }
            }
        }
    }
}
