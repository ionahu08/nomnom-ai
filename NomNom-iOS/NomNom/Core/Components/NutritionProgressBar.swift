import SwiftUI

struct NutritionProgressBar: View {
    let nutrient: String
    let consumed: Double
    let target: Double
    let unit: String

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
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(nutrient)
                    .font(.subheadline)
                    .foregroundColor(.primary)
                Spacer()
                Text("\(Int(consumed))/\(Int(target))\(unit)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 6)
                        .fill(Color.gray.opacity(0.2))

                    RoundedRectangle(cornerRadius: 6)
                        .fill(color)
                        .frame(width: geometry.size.width * min(percentage, 1.0))
                }
            }
            .frame(height: 8)
        }
        .animation(.easeInOut(duration: 0.3), value: percentage)
    }
}

#Preview {
    VStack(spacing: 16) {
        NutritionProgressBar(nutrient: "Protein", consumed: 45, target: 150, unit: "g")
        NutritionProgressBar(nutrient: "Carbs", consumed: 120, target: 200, unit: "g")
        NutritionProgressBar(nutrient: "Fat", consumed: 55, target: 65, unit: "g")
    }
    .padding()
}
