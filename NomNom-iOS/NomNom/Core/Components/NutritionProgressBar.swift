import SwiftUI

struct NutritionProgressBar: View {
    let nutrient: String
    let consumed: Double
    let target: Double
    let unit: String
    let icon: String

    var percentage: Double {
        guard target > 0 else { return 0 }
        return consumed / target
    }

    var color: Color {
        if percentage <= 1.0 {
            return .green
        } else if percentage <= 1.1 {
            return .yellow
        } else {
            return .red
        }
    }

    var body: some View {
        VStack(alignment: .center, spacing: 5) {
            // Icon + name
            HStack(spacing: 4) {
                Text(icon)
                    .font(.system(size: 14))
                Text(nutrient)
                    .font(.caption.weight(.semibold))
                    .foregroundColor(.primary)
            }

            // Progress bar
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    // Background bar
                    RoundedRectangle(cornerRadius: 3)
                        .fill(Color.gray.opacity(0.2))

                    // Progress fill
                    RoundedRectangle(cornerRadius: 3)
                        .fill(color)
                        .frame(width: geometry.size.width * min(percentage, 1.0))
                }
            }
            .frame(height: 6)

            // Values
            Text("\(Int(consumed)) / \(Int(target))\(unit)")
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .animation(.easeInOut(duration: 0.3), value: percentage)
    }
}

#Preview {
    HStack(spacing: 20) {
        NutritionProgressBar(nutrient: "Protein", consumed: 45, target: 150, unit: "g", icon: "🟢")
        NutritionProgressBar(nutrient: "Carbs", consumed: 120, target: 200, unit: "g", icon: "🟠")
        NutritionProgressBar(nutrient: "Fat", consumed: 55, target: 65, unit: "g", icon: "🟡")
    }
    .padding()
}
