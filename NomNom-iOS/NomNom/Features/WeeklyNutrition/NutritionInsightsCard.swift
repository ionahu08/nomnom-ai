import SwiftUI

struct NutritionInsightsCard: View {
    let summary: String
    let strengths: [String]
    let gaps: [String]
    let recommendations: [RecommendationItem]
    @State private var expandedRecommendation: Int? = nil

    var body: some View {
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
                Text(summary)
                    .font(.body)
                    .foregroundColor(.primary)
                    .lineLimit(5)
            }
            .padding(12)
            .background(Color(.systemGray6))
            .cornerRadius(8)

            // Strengths
            if !strengths.isEmpty {
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
                        ForEach(strengths, id: \.self) { strength in
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
            if !gaps.isEmpty {
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
                        ForEach(gaps, id: \.self) { gap in
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
            if !recommendations.isEmpty {
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
                        ForEach(Array(recommendations.enumerated()), id: \.offset) { index, rec in
                            RecommendationCard(
                                item: rec,
                                isExpanded: expandedRecommendation == index,
                                onTap: {
                                    withAnimation {
                                        expandedRecommendation = expandedRecommendation == index ? nil : index
                                    }
                                }
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
}

struct RecommendationCard: View {
    let item: RecommendationItem
    let isExpanded: Bool
    let onTap: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            Button(action: onTap) {
                HStack(spacing: 12) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(item.nutrient)
                            .font(.subheadline)
                            .fontWeight(.semibold)
                            .foregroundColor(.primary)

                        if !item.foods.isEmpty {
                            Text(item.foods.prefix(2).joined(separator: ", "))
                                .font(.caption)
                                .foregroundColor(.secondary)
                                .lineLimit(1)
                        }
                    }

                    Spacer()

                    Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundColor(.secondary)
                }
                .padding(12)
                .contentShape(Rectangle())
            }

            if isExpanded {
                Divider()
                    .padding(.horizontal, 12)

                VStack(alignment: .leading, spacing: 8) {
                    // Foods list
                    VStack(alignment: .leading, spacing: 6) {
                        Text("Try these foods:")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.secondary)

                        ForEach(item.foods, id: \.self) { food in
                            HStack(spacing: 8) {
                                Image(systemName: "checkmark")
                                    .font(.system(size: 10))
                                    .foregroundColor(.green)
                                Text(food)
                                    .font(.caption)
                                    .foregroundColor(.primary)
                            }
                        }
                    }

                    // Reasoning
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Why:")
                            .font(.caption)
                            .fontWeight(.semibold)
                            .foregroundColor(.secondary)
                        Text(item.reasoning)
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .lineLimit(4)
                    }
                }
                .padding(12)
                .background(Color(.systemGray6))
            }
        }
        .background(Color(.systemBackground))
        .cornerRadius(8)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(Color(.systemGray4).opacity(0.2), lineWidth: 1)
        )
    }
}


#Preview {
    NutritionInsightsCard(
        summary: "You're doing great with protein this week, but carbs are running 10% high. Consider adding more vegetables to balance it out.",
        strengths: [
            "Consistent protein intake throughout the week",
            "Good variety of vegetables in your meals"
        ],
        gaps: [
            "Low iron-rich foods",
            "Missing omega-3 sources"
        ],
        recommendations: [
            RecommendationItem(
                nutrient: "Iron-rich foods",
                foods: ["Spinach", "Lean beef", "Fortified cereals"],
                reasoning: "You've logged almost no iron-rich foods this week. Iron is crucial for energy and oxygen transport. Try adding a spinach-based meal or lean beef to your rotation."
            ),
            RecommendationItem(
                nutrient: "Omega-3 sources",
                foods: ["Salmon", "Walnuts", "Chia seeds"],
                reasoning: "Omega-3 fatty acids support heart and brain health. Salmon is great for lunch, or sprinkle walnuts on your breakfast."
            )
        ]
    )
}
