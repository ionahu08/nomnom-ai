import SwiftUI

struct LineChart: View {
    let dailyBreakdown: [DailyBreakdown]
    let period: PeriodType
    let metricType: MetricType
    let targetValue: Double

    enum MetricType {
        case calories
        case protein
        case carbs
        case fat
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(metricTitle)
                .font(.headline)
                .padding(.horizontal)

            HStack(alignment: .top, spacing: 4) {
                // Y-axis labels
                VStack(alignment: .trailing, spacing: 0) {
                    ForEach(0..<5, id: \.self) { index in
                        let maxValue = getMaxValue()
                        let value = maxValue * Double(4 - index) / 4
                        Text(String(format: "%.0f", value))
                            .font(.caption2)
                            .foregroundColor(.secondary)
                            .frame(height: 40)
                            .frame(maxHeight: .infinity)
                    }
                }
                .frame(width: 35)

                // Chart area
                GeometryReader { geometry in
                    Canvas { context, size in
                        let padding: CGFloat = 20
                        let width = size.width - padding * 2
                        let height = size.height - padding * 2

                        guard !dailyBreakdown.isEmpty else { return }

                        let maxValue = getMaxValue()
                        guard maxValue > 0 else { return }

                        // Draw grid lines
                        for i in 0..<5 {
                            let y = padding + CGFloat(i) * (height / 4)
                            var path = Path()
                            path.move(to: CGPoint(x: padding, y: y))
                            path.addLine(to: CGPoint(x: size.width - padding, y: y))
                            context.stroke(path, with: .color(.gray.opacity(0.2)), lineWidth: 0.5)
                        }

                        // Draw target reference line
                        let targetRatio = targetValue / maxValue
                        let targetY = padding + CGFloat(1 - targetRatio) * height
                        var targetPath = Path()
                        targetPath.move(to: CGPoint(x: padding, y: targetY))
                        targetPath.addLine(to: CGPoint(x: size.width - padding, y: targetY))
                        context.stroke(targetPath, with: .color(.green), lineWidth: 2)

                        // Calculate points for line
                        let points = calculatePoints(width: width, height: height, maxValue: maxValue, padding: padding)

                        if !points.isEmpty {
                            // Draw line connecting points
                            var path = Path()
                            path.move(to: points[0])
                            for point in points.dropFirst() {
                                path.addLine(to: point)
                            }
                            context.stroke(path, with: .color(lineColor), lineWidth: 2)

                            // Draw circles at data points
                            for point in points {
                                context.fill(
                                    Path(ellipseIn: CGRect(x: point.x - 4, y: point.y - 4, width: 8, height: 8)),
                                    with: .color(lineColor)
                                )
                            }
                        }
                    }
                }
                .frame(height: 200)
                .background(Color(.systemGray6))
                .cornerRadius(8)
            }

            // X-axis labels
            HStack(spacing: 0) {
                Spacer().frame(width: 35)
                HStack(spacing: 0) {
                    ForEach(0..<xAxisLabels.count, id: \.self) { index in
                        Text(xAxisLabels[index])
                            .font(.caption2)
                            .frame(maxWidth: .infinity)
                    }
                }
            }
        }
    }

    private var metricTitle: String {
        switch metricType {
        case .calories:
            return "Calories"
        case .protein:
            return "Protein (g)"
        case .carbs:
            return "Carbs (g)"
        case .fat:
            return "Fat (g)"
        }
    }

    private var lineColor: Color {
        switch metricType {
        case .calories:
            return Color.blue
        case .protein:
            return Color.orange
        case .carbs:
            return Color.green
        case .fat:
            return Color.red
        }
    }

    private var xAxisLabels: [String] {
        switch period {
        case .week:
            return ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        case .month:
            return stride(from: 0, to: dailyBreakdown.count, by: max(1, dailyBreakdown.count / 6))
                .map { index in
                    if index < dailyBreakdown.count {
                        let dateStr = dailyBreakdown[index].date
                        if let day = extractDay(from: dateStr) {
                            return day
                        }
                    }
                    return ""
                }
        case .sixMonth:
            return getMonthLabels()
        }
    }

    private func extractDay(from dateString: String) -> String? {
        // dateString format: "2026-06-15"
        let components = dateString.split(separator: "-")
        if components.count >= 3 {
            return String(components[2])
        }
        return nil
    }

    private func getMonthLabels() -> [String] {
        let months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        guard !dailyBreakdown.isEmpty else { return [] }

        var labels: [String] = []
        var currentMonth: String? = nil

        for breakdown in dailyBreakdown {
            if let month = extractMonth(from: breakdown.date) {
                if month != currentMonth {
                    labels.append(month)
                    currentMonth = month
                }
            }
        }

        return labels.isEmpty ? months : labels
    }

    private func extractMonth(from dateString: String) -> String? {
        let components = dateString.split(separator: "-")
        if components.count >= 2, let monthNum = Int(components[1]) {
            let months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            if monthNum >= 1 && monthNum <= 12 {
                return months[monthNum - 1]
            }
        }
        return nil
    }

    private func getMaxValue() -> Double {
        let dataMax: Double
        let defaultMin: Double

        switch metricType {
        case .calories:
            dataMax = Double(dailyBreakdown.map { $0.calories }.max() ?? 0)
            defaultMin = 2000
        case .protein:
            dataMax = Double(dailyBreakdown.map { $0.proteinG }.max() ?? 0)
            defaultMin = 150
        case .carbs:
            dataMax = Double(dailyBreakdown.map { $0.carbsG }.max() ?? 0)
            defaultMin = 200
        case .fat:
            dataMax = Double(dailyBreakdown.map { $0.fatG }.max() ?? 0)
            defaultMin = 65
        }

        return max(dataMax, targetValue, defaultMin)
    }

    private func calculatePoints(width: CGFloat, height: CGFloat, maxValue: Double, padding: CGFloat) -> [CGPoint] {
        guard !dailyBreakdown.isEmpty else { return [] }

        var points: [CGPoint] = []

        for (index, breakdown) in dailyBreakdown.enumerated() {
            let xRatio = CGFloat(index) / CGFloat(max(1, dailyBreakdown.count - 1))
            let x = padding + xRatio * width

            let value: Double
            switch metricType {
            case .calories:
                value = Double(breakdown.calories)
            case .protein:
                value = Double(breakdown.proteinG)
            case .carbs:
                value = Double(breakdown.carbsG)
            case .fat:
                value = Double(breakdown.fatG)
            }

            let yRatio = 1 - (value / maxValue)
            let y = padding + yRatio * height

            points.append(CGPoint(x: x, y: y))
        }

        return points
    }
}

#Preview {
    LineChart(
        dailyBreakdown: [
            DailyBreakdown(date: "2026-06-09", calories: 1950, proteinG: 125, carbsG: 185, fatG: 62),
            DailyBreakdown(date: "2026-06-10", calories: 2100, proteinG: 140, carbsG: 210, fatG: 70),
            DailyBreakdown(date: "2026-06-11", calories: 1800, proteinG: 115, carbsG: 170, fatG: 58),
        ],
        period: .week,
        metricType: .calories,
        targetValue: 2000
    )
}
