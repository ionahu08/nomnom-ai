import SwiftUI

struct MacroBreakdown: View {
    let proteinTotal: Int
    let carbsTotal: Int
    let fatTotal: Int

    var body: some View {
        VStack(spacing: 16) {
            Text("Macro Distribution")
                .font(.headline)
                .frame(maxWidth: .infinity, alignment: .leading)

            HStack(spacing: 24) {
                // Donut chart
                ZStack {
                    Circle()
                        .stroke(Color(.systemGray5), lineWidth: 20)

                    Circle()
                        .trim(from: 0, to: proteinPercentage)
                        .stroke(Color(red: 0.95, green: 0.7, blue: 0.2), style: StrokeStyle(lineWidth: 20, lineCap: .round))
                        .rotationEffect(.degrees(-90))

                    Circle()
                        .trim(from: proteinPercentage, to: proteinPercentage + carbsPercentage)
                        .stroke(Color(red: 0.2, green: 0.8, blue: 0.95), style: StrokeStyle(lineWidth: 20, lineCap: .round))
                        .rotationEffect(.degrees(-90))

                    Circle()
                        .trim(from: proteinPercentage + carbsPercentage, to: 1)
                        .stroke(Color(red: 0.95, green: 0.4, blue: 0.3), style: StrokeStyle(lineWidth: 20, lineCap: .round))
                        .rotationEffect(.degrees(-90))

                    VStack(spacing: 4) {
                        Text(String(format: "%.0f%%", totalCalories > 0 ? (Double(proteinTotal) * 4 / Double(totalCalories) * 100) : 0))
                            .font(.caption2)
                            .fontWeight(.semibold)
                        Text("Protein")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                }
                .frame(width: 120, height: 120)

                // Stats
                VStack(alignment: .leading, spacing: 12) {
                    MacroStatRow(
                        icon: "🍗",
                        label: "Protein",
                        value: proteinTotal,
                        unit: "g",
                        percentage: proteinPercentage * 100,
                        color: Color(red: 0.95, green: 0.7, blue: 0.2)
                    )

                    MacroStatRow(
                        icon: "🍙",
                        label: "Carbs",
                        value: carbsTotal,
                        unit: "g",
                        percentage: carbsPercentage * 100,
                        color: Color(red: 0.2, green: 0.8, blue: 0.95)
                    )

                    MacroStatRow(
                        icon: "🍖",
                        label: "Fat",
                        value: fatTotal,
                        unit: "g",
                        percentage: fatPercentage * 100,
                        color: Color(red: 0.95, green: 0.4, blue: 0.3)
                    )
                }
            }

            // Calorie breakdown
            HStack(spacing: 12) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Protein")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    Text("\(proteinTotal * 4)")
                        .font(.body)
                        .fontWeight(.semibold)
                    Text("cal")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity)
                .padding(8)
                .background(Color(red: 0.95, green: 0.7, blue: 0.2).opacity(0.1))
                .cornerRadius(8)

                VStack(alignment: .leading, spacing: 4) {
                    Text("Carbs")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    Text("\(carbsTotal * 4)")
                        .font(.body)
                        .fontWeight(.semibold)
                    Text("cal")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity)
                .padding(8)
                .background(Color(red: 0.2, green: 0.8, blue: 0.95).opacity(0.1))
                .cornerRadius(8)

                VStack(alignment: .leading, spacing: 4) {
                    Text("Fat")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    Text("\(fatTotal * 9)")
                        .font(.body)
                        .fontWeight(.semibold)
                    Text("cal")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity)
                .padding(8)
                .background(Color(red: 0.95, green: 0.4, blue: 0.3).opacity(0.1))
                .cornerRadius(8)
            }
        }
    }

    private var totalCalories: Int {
        (proteinTotal * 4) + (carbsTotal * 4) + (fatTotal * 9)
    }

    private var proteinPercentage: Double {
        totalCalories > 0 ? Double(proteinTotal * 4) / Double(totalCalories) : 0
    }

    private var carbsPercentage: Double {
        totalCalories > 0 ? Double(carbsTotal * 4) / Double(totalCalories) : 0
    }

    private var fatPercentage: Double {
        totalCalories > 0 ? Double(fatTotal * 9) / Double(totalCalories) : 0
    }
}

struct MacroStatRow: View {
    let icon: String
    let label: String
    let value: Int
    let unit: String
    let percentage: Double
    let color: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack(spacing: 8) {
                Text(icon)
                    .font(.system(size: 16))
                Text(label)
                    .font(.caption)
                    .fontWeight(.semibold)
                Spacer()
                Text(String(format: "%.0f%%", percentage))
                    .font(.caption2)
                    .fontWeight(.semibold)
                    .foregroundColor(color)
            }
            ProgressView(value: percentage / 100)
                .tint(color)
                .frame(height: 4)
            Text("\(value)\(unit)")
                .font(.caption2)
                .foregroundColor(.secondary)
        }
    }
}

#Preview {
    MacroBreakdown(
        proteinTotal: 120,
        carbsTotal: 180,
        fatTotal: 60
    )
}
