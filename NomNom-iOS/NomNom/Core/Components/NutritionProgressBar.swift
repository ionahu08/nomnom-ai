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
        HStack(spacing: 12) {
            Text(icon)
                .font(.system(size: 18))

            VStack(alignment: .leading, spacing: 2) {
                Text(nutrient)
                    .font(.caption)
                    .foregroundColor(.secondary)
                Text("\(Int(consumed)) / \(Int(target))\(unit)")
                    .font(.subheadline.weight(.semibold))
                    .foregroundColor(.primary)
            }

            Spacer()
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(Color.gray.opacity(0.05))
        .cornerRadius(8)
        .animation(.easeInOut(duration: 0.3), value: percentage)
    }
}

#Preview {
    VStack(spacing: 10) {
        NutritionProgressBar(nutrient: "Protein", consumed: 45, target: 150, unit: "g", icon: "🟢")
        NutritionProgressBar(nutrient: "Carbs", consumed: 120, target: 200, unit: "g", icon: "🟠")
        NutritionProgressBar(nutrient: "Fat", consumed: 55, target: 65, unit: "g", icon: "🟡")
    }
    .padding()
}
