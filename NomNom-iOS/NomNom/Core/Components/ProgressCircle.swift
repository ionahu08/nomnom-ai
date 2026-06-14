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
        VStack(spacing: 8) {
            ZStack {
                Circle()
                    .stroke(Color.gray.opacity(0.3), lineWidth: 12)

                Circle()
                    .trim(from: 0, to: min(percentage, 1.0))
                    .stroke(color, style: StrokeStyle(lineWidth: 12, lineCap: .round))
                    .rotationEffect(.degrees(-90))

                VStack(spacing: 4) {
                    Text("\(Int(percentage * 100))%")
                        .font(.system(size: 28, weight: .semibold))
                        .foregroundColor(.primary)

                    Text("\(consumed) / \(target) kcal")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .frame(height: 180)

            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .animation(.easeInOut(duration: 0.3), value: percentage)
    }
}

#Preview {
    ProgressCircle(consumed: 1450, target: 2000, label: "Daily Calories")
        .padding()
}
