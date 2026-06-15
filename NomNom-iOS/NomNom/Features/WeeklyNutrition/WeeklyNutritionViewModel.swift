import Foundation

enum PeriodType: String, CaseIterable {
    case week = "week"
    case month = "month"
    case sixMonth = "6m"

    var label: String {
        switch self {
        case .week: return "W"
        case .month: return "M"
        case .sixMonth: return "6M"
        }
    }

    var days: Int {
        switch self {
        case .week: return 7
        case .month: return 30
        case .sixMonth: return 180
        }
    }
}

@MainActor
class WeeklyNutritionViewModel: ObservableObject {
    @Published var summary: WeeklySummaryResponse?
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var selectedDate = Date()
    @Published var selectedPeriod: PeriodType = .week

    private let api = APIClient.shared

    func loadInsightData(endDate: Date = Date(), period: PeriodType) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        let dateString = formatter.string(from: endDate)

        let apiPeriod = period.rawValue
        print("[InsightViewModel] Loading summary for period=\(apiPeriod), date=\(dateString)")

        do {
            summary = try await api.get(path: "/api/v1/analytics/summary?period=\(apiPeriod)&date=\(dateString)")
            print("[InsightViewModel] Summary loaded successfully")
        } catch {
            print("[InsightViewModel] Failed to load summary: \(error)")
            errorMessage = "Failed to load insight data: \(error.localizedDescription)"
        }
    }

    func loadWeeklySummary(endDate: Date? = nil) async {
        let dateToUse = endDate ?? getDefaultEndDate()
        await loadInsightData(endDate: dateToUse, period: .week)
    }

    func selectPeriod(_ period: PeriodType) async {
        selectedPeriod = period
        let dateToUse = selectedDate > getDefaultEndDate() ? getDefaultEndDate() : selectedDate
        await loadInsightData(endDate: dateToUse, period: period)
    }

    func previousPeriod() async {
        if let currentEndDate = getEndDateFromSummary() {
            let days = selectedPeriod.days
            let newEndDate = Calendar.current.date(byAdding: .day, value: -days, to: currentEndDate) ?? Date()
            selectedDate = newEndDate
            await loadInsightData(endDate: newEndDate, period: selectedPeriod)
        }
    }

    func nextPeriod() async {
        if let currentEndDate = getEndDateFromSummary() {
            let maxDate = getDefaultEndDate()
            let days = selectedPeriod.days
            let newEndDate = Calendar.current.date(byAdding: .day, value: days, to: currentEndDate) ?? Date()

            // Only allow moving forward if it doesn't exceed the default (today - 1 day)
            if newEndDate <= maxDate {
                selectedDate = newEndDate
                await loadInsightData(endDate: newEndDate, period: selectedPeriod)
            }
        }
    }

    private func getDefaultEndDate() -> Date {
        // End date should be today - 1 day
        let calendar = Calendar.current
        let today = Date()
        let yesterday = calendar.date(byAdding: .day, value: -1, to: today) ?? today
        return yesterday
    }

    var canGoNext: Bool {
        if let currentEndDate = getEndDateFromSummary() {
            let maxDate = getDefaultEndDate()
            let days = selectedPeriod.days
            if let nextDate = Calendar.current.date(byAdding: .day, value: days, to: currentEndDate) {
                return nextDate <= maxDate
            }
        }
        return false
    }

    private func getEndDateFromSummary() -> Date? {
        guard let summary = summary else { return nil }
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.date(from: summary.endDate)
    }

    func getWeekLabel() -> String {
        guard let summary = summary else { return "" }
        let formatter = DateFormatter()
        formatter.dateFormat = "MMM d"
        if let startDate = parseDate(summary.startDate),
           let endDate = parseDate(summary.endDate) {
            let startStr = formatter.string(from: startDate)
            let endStr = formatter.string(from: endDate)
            return "\(startStr) - \(endStr)"
        }
        return ""
    }

    func getCalorieStatus() -> String {
        guard let summary = summary, let percentage = summary.calories.percentage else { return "" }
        if percentage >= 95 && percentage <= 105 {
            return "On Track ✅"
        } else if percentage > 105 {
            return "Over Target ⚠️"
        } else {
            return "Under Target"
        }
    }

    func getNutrientStatus(percentage: Double?) -> String {
        guard let percentage = percentage else { return "?" }
        if percentage >= 90 && percentage <= 110 {
            return "✅"
        } else if percentage > 110 {
            return "⚠️"
        } else {
            return "↓"
        }
    }

    private func parseDate(_ dateString: String) -> Date? {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.date(from: dateString)
    }
}
