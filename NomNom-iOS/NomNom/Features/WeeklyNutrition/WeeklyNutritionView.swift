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
                            // Consistency
                            VStack(spacing: 12) {
                                HStack {
                                    Text("Logging Consistency")
                                        .font(.headline)
                                    Spacer()
                                    Text("\(summary.daysLogged)/\(summary.totalDays) days")
                                        .font(.body)
                                        .fontWeight(.semibold)
                                }

                                ProgressView(value: Double(summary.daysLogged) / Double(summary.totalDays))
                                    .tint(.blue)

                                Text(String(format: "%.1f%% logged", summary.consistency))
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            .padding()
                            .background(Color(.systemGray6))
                            .cornerRadius(12)

                            // Calories Line Chart
                            LineChart(
                                dailyBreakdown: summary.dailyBreakdown,
                                period: viewModel.selectedPeriod,
                                metricType: .calories
                            )

                            // Protein Line Chart
                            LineChart(
                                dailyBreakdown: summary.dailyBreakdown,
                                period: viewModel.selectedPeriod,
                                metricType: .protein
                            )

                            // Carbs Line Chart
                            LineChart(
                                dailyBreakdown: summary.dailyBreakdown,
                                period: viewModel.selectedPeriod,
                                metricType: .carbs
                            )

                            // Fat Line Chart
                            LineChart(
                                dailyBreakdown: summary.dailyBreakdown,
                                period: viewModel.selectedPeriod,
                                metricType: .fat
                            )

                            // Nutrient Summary
                            VStack(spacing: 16) {
                                Text("Daily Targets")
                                    .font(.headline)
                                    .frame(maxWidth: .infinity, alignment: .leading)

                                // Protein
                                NutrientRow(
                                    icon: "🍗",
                                    label: "Protein",
                                    current: summary.proteinG.average,
                                    target: summary.proteinG.target,
                                    unit: "g",
                                    percentage: summary.proteinG.percentage,
                                    status: viewModel.getNutrientStatus(percentage: summary.proteinG.percentage)
                                )

                                Divider()

                                // Carbs
                                NutrientRow(
                                    icon: "🍙",
                                    label: "Carbs",
                                    current: summary.carbsG.average,
                                    target: summary.carbsG.target,
                                    unit: "g",
                                    percentage: summary.carbsG.percentage,
                                    status: viewModel.getNutrientStatus(percentage: summary.carbsG.percentage)
                                )

                                Divider()

                                // Fat
                                NutrientRow(
                                    icon: "🍖",
                                    label: "Fat",
                                    current: summary.fatG.average,
                                    target: summary.fatG.target,
                                    unit: "g",
                                    percentage: summary.fatG.percentage,
                                    status: viewModel.getNutrientStatus(percentage: summary.fatG.percentage)
                                )
                            }
                            .padding()
                            .background(Color(.systemGray6))
                            .cornerRadius(12)

                            // Top Foods
                            if !summary.topFoods.isEmpty {
                                VStack(spacing: 12) {
                                    Text("Top Foods")
                                        .font(.headline)
                                        .frame(maxWidth: .infinity, alignment: .leading)

                                    ForEach(summary.topFoods, id: \.food) { food in
                                        HStack {
                                            VStack(alignment: .leading, spacing: 4) {
                                                Text(food.food)
                                                    .font(.body)
                                                    .fontWeight(.semibold)
                                                Text("\(food.count)x")
                                                    .font(.caption)
                                                    .foregroundColor(.secondary)
                                            }
                                            Spacer()
                                            Text("\(food.calories) cal")
                                                .font(.body)
                                                .fontWeight(.semibold)
                                        }
                                        .padding(.vertical, 8)
                                    }
                                }
                                .padding()
                                .background(Color(.systemGray6))
                                .cornerRadius(12)
                            }
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
                print("[WeeklyNutritionView] View appeared, loading summary")
                await viewModel.loadWeeklySummary()
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
