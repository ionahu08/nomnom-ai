import SwiftUI

struct ProgressCircle: View {
    let consumed: Int
    let target: Int
    let label: String

    var percentage: Double {
        guard target > 0 else { return 0 }
        return Double(consumed) / Double(target)
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
        VStack(spacing: 12) {
            ZStack {
                // Background circle
                Circle()
                    .stroke(Color.gray.opacity(0.2), lineWidth: 8)

                // Progress circle
                Circle()
                    .trim(from: 0, to: min(percentage, 1.0))
                    .stroke(color, style: StrokeStyle(lineWidth: 8, lineCap: .round))
                    .rotationEffect(.degrees(-90))

                // Center content
                VStack(spacing: 2) {
                    Text("\(consumed)")
                        .font(.system(size: 24, weight: .semibold))
                        .foregroundColor(.primary)

                    Text("/ \(target) kcal")
                        .font(.caption2)
                        .foregroundColor(.secondary)

                    Text("Remaining")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
            .frame(height: 140)

            Text(label)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .animation(.easeInOut(duration: 0.3), value: percentage)
    }
}

#Preview {
    ProgressCircle(consumed: 1450, target: 2000, label: "Daily Calories")
        .padding()
}
