import SwiftUI

struct WeeklyChart: View {
    let dailyBreakdown: [DailyBreakdown]
    let calorieTarget: Int

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Daily Calories")
                .font(.headline)

            VStack(spacing: 16) {
                // Chart bars
                HStack(alignment: .bottom, spacing: 8) {
                    ForEach(dailyBreakdown, id: \.date) { day in
                        VStack(spacing: 6) {
                            // Bar
                            VStack {
                                Spacer()
                                RoundedRectangle(cornerRadius: 4)
                                    .fill(colorForCalories(day.calories, target: calorieTarget))
                                    .frame(height: getBarHeight(day.calories))
                            }
                            .frame(height: 120)

                            // Label
                            Text(getDayLabel(day.date))
                                .font(.caption2)
                                .fontWeight(.semibold)
                        }
                    }
                }

                // Target line reference
                HStack {
                    Text("Target: \(calorieTarget) cal")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Spacer()
                    Text("Max shown: \(getMaxCalories())")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            // Legend
            HStack(spacing: 16) {
                HStack(spacing: 4) {
                    RoundedRectangle(cornerRadius: 2)
                        .fill(Color.green)
                        .frame(width: 8, height: 8)
                    Text("On Track (±10%)")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                HStack(spacing: 4) {
                    RoundedRectangle(cornerRadius: 2)
                        .fill(Color.orange)
                        .frame(width: 8, height: 8)
                    Text("Over")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                HStack(spacing: 4) {
                    RoundedRectangle(cornerRadius: 2)
                        .fill(Color.red)
                        .frame(width: 8, height: 8)
                    Text("Way Over")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private func getBarHeight(_ calories: Int) -> CGFloat {
        let maxCals = getMaxCalories()
        return CGFloat(calories) / CGFloat(maxCals) * 110
    }

    private func getMaxCalories() -> Int {
        let maxDaily = dailyBreakdown.map { $0.calories }.max() ?? calorieTarget
        return max(maxDaily, Int(Double(calorieTarget) * 1.3))
    }

    private func colorForCalories(_ calories: Int, target: Int) -> Color {
        let percentage = Double(calories) / Double(target) * 100
        if percentage >= 90 && percentage <= 110 {
            return .green
        } else if percentage > 110 && percentage <= 130 {
            return .orange
        } else {
            return .red
        }
    }

    private func getDayLabel(_ dateString: String) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        if let date = formatter.date(from: dateString) {
            let dayFormatter = DateFormatter()
            dayFormatter.dateFormat = "EEE"
            return dayFormatter.string(from: date).prefix(3).uppercased()
        }
        return "?"
    }
}

#Preview {
    WeeklyChart(
        dailyBreakdown: [
            DailyBreakdown(date: "2026-06-08", calories: 1950, proteinG: 125, carbsG: 185, fatG: 62),
            DailyBreakdown(date: "2026-06-09", calories: 2100, proteinG: 130, carbsG: 195, fatG: 65),
            DailyBreakdown(date: "2026-06-10", calories: 1800, proteinG: 110, carbsG: 160, fatG: 55),
            DailyBreakdown(date: "2026-06-11", calories: 2300, proteinG: 140, carbsG: 220, fatG: 72),
            DailyBreakdown(date: "2026-06-12", calories: 1900, proteinG: 120, carbsG: 180, fatG: 60),
            DailyBreakdown(date: "2026-06-13", calories: 2050, proteinG: 128, carbsG: 190, fatG: 64),
            DailyBreakdown(date: "2026-06-14", calories: 1850, proteinG: 115, carbsG: 170, fatG: 58),
        ],
        calorieTarget: 2000
    )
}
