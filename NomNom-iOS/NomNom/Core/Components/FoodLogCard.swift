import SwiftUI

struct FoodLogCard: View {
    let log: FoodLogResponse

    var body: some View {
        HStack(spacing: 12) {
            // Food icon (placeholder for photo thumbnail)
            ZStack {
                RoundedRectangle(cornerRadius: 12)
                    .fill(NomNomColors.surfaceSecondary)
                    .frame(width: 56, height: 56)
                Text("🍽️")
                    .font(.title2)
            }

            // Food info
            VStack(alignment: .leading, spacing: 4) {
                Text(log.foodName)
                    .font(.headline)
                    .foregroundColor(NomNomColors.textPrimary)

                Text("\(log.calories) kcal • P: \(String(format: "%.0f", log.proteinG))g • C: \(String(format: "%.0f", log.carbsG))g • F: \(String(format: "%.0f", log.fatG))g")
                    .font(.caption)
                    .foregroundColor(NomNomColors.textSecondary)

                Text(log.catRoast)
                    .font(.caption)
                    .foregroundColor(NomNomColors.primary)
                    .lineLimit(1)
            }

            Spacer()
        }
        .padding(12)
        .background(NomNomColors.surface)
        .cornerRadius(16)
    }
}
