import SwiftUI

struct WeeklyNutritionView: View {
    @StateObject private var viewModel = WeeklyNutritionViewModel()

    var body: some View {
        NavigationStack {
            ZStack {
                ScrollView {
                    VStack(spacing: 20) {
                        // Period Type Selector
                        HStack(spacing: 8) {
                            ForEach(PeriodType.allCases, id: \.self) { period in
                                Button(action: {
                                    Task {
                                        await viewModel.selectPeriod(period)
                                    }
                                }) {
                                    Text(period.label)
                                        .font(.system(.body, design: .default))
                                        .fontWeight(.semibold)
                                }
                                .foregroundColor(viewModel.selectedPeriod == period ? .white : .secondary)
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 8)
                                .background(viewModel.selectedPeriod == period ? Color.blue : Color(.systemGray6))
                                .cornerRadius(8)
                            }
                        }
                        .padding(.horizontal)

                        // Date Navigation
                        HStack(spacing: 12) {
                            Button(action: {
                                Task {
                                    await viewModel.previousPeriod()
                                }
                            }) {
                                Image(systemName: "chevron.left")
                                    .font(.system(size: 16, weight: .semibold))
                            }
                            .foregroundColor(.blue)

                            Text(viewModel.getWeekLabel())
                                .font(.system(.body, design: .default))
                                .frame(maxWidth: .infinity)

                            Button(action: {
                                Task {
                                    await viewModel.nextPeriod()
                                }
                            }) {
                                Image(systemName: "chevron.right")
                                    .font(.system(size: 16, weight: .semibold))
                            }
                            .foregroundColor(viewModel.canGoNext ? .blue : .gray)
                            .disabled(!viewModel.canGoNext)
                        }
                        .padding(.horizontal)
                        .padding(.vertical, 12)
                        .background(Color(.systemGray6))
                        .cornerRadius(8)

                        if let summary = viewModel.summary {
                            // AI Nutrition Insights (before charts)
                            if viewModel.isLoadingInsights {
                                VStack(spacing: 12) {
                                    ProgressView()
                                    Text("Loading your personalized nutrition insights...")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color(.systemGray6))
                                .cornerRadius(12)
                            } else if let insights = viewModel.nutritionInsights {
                                VStack(alignment: .leading, spacing: 16) {
                                    // Title
                                    HStack {
                                        Image(systemName: "lightbulb.fill")
                                            .font(.system(size: 18))
                                            .foregroundColor(.orange)
                                        Text("Your Nutrition Insights")
                                            .font(.headline)
                                    }

                                    // Summary
                                    VStack(alignment: .leading, spacing: 8) {
                                        Text(insights.summary)
                                            .font(.body)
                                            .foregroundColor(.primary)
                                            .lineLimit(5)
                                    }
                                    .padding(12)
                                    .background(Color(.systemGray6))
                                    .cornerRadius(8)

                                    // Strengths
                                    if !insights.strengths.isEmpty {
                                        VStack(alignment: .leading, spacing: 8) {
                                            HStack {
                                                Image(systemName: "checkmark.circle.fill")
                                                    .foregroundColor(.green)
                                                    .font(.system(size: 14))
                                                Text("What You're Doing Well")
                                                    .font(.subheadline)
                                                    .fontWeight(.semibold)
                                            }

                                            VStack(alignment: .leading, spacing: 6) {
                                                ForEach(insights.strengths, id: \.self) { strength in
                                                    HStack(spacing: 8) {
                                                        Image(systemName: "star.fill")
                                                            .font(.system(size: 10))
                                                            .foregroundColor(.yellow)
                                                        Text(strength)
                                                            .font(.caption)
                                                            .foregroundColor(.secondary)
                                                    }
                                                }
                                            }
                                            .padding(.leading, 8)
                                        }
                                    }

                                    // Gaps
                                    if !insights.gaps.isEmpty {
                                        VStack(alignment: .leading, spacing: 8) {
                                            HStack {
                                                Image(systemName: "exclamationmark.circle.fill")
                                                    .foregroundColor(.orange)
                                                    .font(.system(size: 14))
                                                Text("Areas to Improve")
                                                    .font(.subheadline)
                                                    .fontWeight(.semibold)
                                            }

                                            VStack(alignment: .leading, spacing: 6) {
                                                ForEach(insights.gaps, id: \.self) { gap in
                                                    HStack(spacing: 8) {
                                                        Image(systemName: "arrow.up")
                                                            .font(.system(size: 10))
                                                            .foregroundColor(.orange)
                                                        Text(gap)
                                                            .font(.caption)
                                                            .foregroundColor(.secondary)
                                                    }
                                                }
                                            }
                                            .padding(.leading, 8)
                                        }
                                    }

                                    // Recommendations
                                    if !insights.recommendations.isEmpty {
                                        VStack(alignment: .leading, spacing: 8) {
                                            HStack {
                                                Image(systemName: "fork.knife")
                                                    .foregroundColor(.green)
                                                    .font(.system(size: 14))
                                                Text("Recommendations")
                                                    .font(.subheadline)
                                                    .fontWeight(.semibold)
                                            }

                                            VStack(spacing: 8) {
                                                ForEach(Array(insights.recommendations.enumerated()), id: \.offset) { index, rec in
                                                    VStack(alignment: .leading, spacing: 0) {
                                                        HStack(spacing: 12) {
                                                            VStack(alignment: .leading, spacing: 4) {
                                                                Text(rec.nutrient)
                                                                    .font(.subheadline)
                                                                    .fontWeight(.semibold)
                                                                    .foregroundColor(.primary)

                                                                if !rec.foods.isEmpty {
                                                                    Text(rec.foods.prefix(2).joined(separator: ", "))
                                                                        .font(.caption)
                                                                        .foregroundColor(.secondary)
                                                                        .lineLimit(1)
                                                                }
                                                            }

                                                            Spacer()

                                                            Image(systemName: "chevron.right")
                                                                .font(.system(size: 12, weight: .semibold))
                                                                .foregroundColor(.secondary)
                                                        }
                                                        .padding(12)
                                                        .contentShape(Rectangle())
                                                    }
                                                    .background(Color(.systemBackground))
                                                    .cornerRadius(8)
                                                    .overlay(
                                                        RoundedRectangle(cornerRadius: 8)
                                                            .stroke(Color(.systemGray4).opacity(0.2), lineWidth: 1)
                                                    )
                                                }
                                            }
                                        }
                                    }
                                }
                                .padding()
                                .background(Color(.systemBackground))
                                .cornerRadius(12)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 12)
                                        .stroke(Color(.systemGray3).opacity(0.2), lineWidth: 1)
                                )
                            }

                            // Calories Line Chart
                            LineChart(
                                dailyBreakdown: summary.dailyBreakdown,
                                period: viewModel.selectedPeriod,
                                metricType: .calories,
                                targetValue: Double(summary.calories.target)
                            )

                            // Protein Line Chart
                            LineChart(
                                dailyBreakdown: summary.dailyBreakdown,
                                period: viewModel.selectedPeriod,
                                metricType: .protein,
                                targetValue: Double(summary.proteinG.target)
                            )

                            // Carbs Line Chart
                            LineChart(
                                dailyBreakdown: summary.dailyBreakdown,
                                period: viewModel.selectedPeriod,
                                metricType: .carbs,
                                targetValue: Double(summary.carbsG.target)
                            )

                            // Fat Line Chart
                            LineChart(
                                dailyBreakdown: summary.dailyBreakdown,
                                period: viewModel.selectedPeriod,
                                metricType: .fat,
                                targetValue: Double(summary.fatG.target)
                            )
                        } else if viewModel.isLoading {
                            VStack(spacing: 20) {
                                ProgressView()
                                Text("Loading weekly summary...")
                                    .foregroundColor(.secondary)
                            }
                            .frame(maxHeight: .infinity, alignment: .center)
                        }

                        // Error Message
                        if let error = viewModel.errorMessage {
                            VStack(spacing: 8) {
                                HStack {
                                    Image(systemName: "exclamationmark.circle.fill")
                                        .foregroundColor(.red)
                                    Text(error)
                                        .font(.caption)
                                        .foregroundColor(.red)
                                    Spacer()
                                }
                            }
                            .padding()
                            .background(Color.red.opacity(0.1))
                            .cornerRadius(8)
                        }
                    }
                    .padding()
                }
                .navigationTitle("📊 Insight")
            }
            .task {
                print("[WeeklyNutritionView] View appeared, loading summary and insights")
                await viewModel.loadWeeklySummary()
                await viewModel.loadNutritionInsights()
            }
        }
    }
}

struct NutrientRow: View {
    let icon: String
    let label: String
    let current: Double
    let target: Int
    let unit: String
    let percentage: Double?
    let status: String

    var body: some View {
        HStack(spacing: 12) {
            Text(icon)
                .font(.system(size: 24))

            VStack(alignment: .leading, spacing: 4) {
                Text(label)
                    .font(.body)
                    .fontWeight(.semibold)
                Text(String(format: "%.0f\(unit) / \(target)\(unit)", current))
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            Spacer()

            VStack(alignment: .trailing, spacing: 4) {
                Text(status)
                    .font(.headline)
                if let percentage = percentage {
                    Text(String(format: "%.0f%%", percentage))
                        .font(.caption)
                        .foregroundColor(.secondary)
                } else {
                    Text("N/A")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
    }
}

#Preview {
    WeeklyNutritionView()
}
