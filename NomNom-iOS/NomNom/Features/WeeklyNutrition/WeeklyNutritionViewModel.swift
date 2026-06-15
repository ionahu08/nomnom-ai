import Foundation

@MainActor
class WeeklyNutritionViewModel: ObservableObject {
    @Published var summary: WeeklySummaryResponse?
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var selectedDate = Date()

    private let api = APIClient.shared

    func loadWeeklySummary(endDate: Date = Date()) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        let dateString = formatter.string(from: endDate)

        print("[WeeklyNutritionViewModel] Loading summary for period=week, date=\(dateString)")

        do {
            summary = try await api.get(path: "/api/v1/analytics/summary?period=week&date=\(dateString)")
            print("[WeeklyNutritionViewModel] Summary loaded successfully")
        } catch {
            print("[WeeklyNutritionViewModel] Failed to load summary: \(error)")
            errorMessage = "Failed to load weekly summary: \(error.localizedDescription)"
        }
    }

    func previousWeek() async {
        if let currentEndDate = getEndDateFromSummary() {
            let newEndDate = Calendar.current.date(byAdding: .day, value: -7, to: currentEndDate) ?? Date()
            selectedDate = newEndDate
            await loadWeeklySummary(endDate: newEndDate)
        }
    }

    func nextWeek() async {
        if let currentEndDate = getEndDateFromSummary() {
            let newEndDate = Calendar.current.date(byAdding: .day, value: 7, to: currentEndDate) ?? Date()
            selectedDate = newEndDate
            await loadWeeklySummary(endDate: newEndDate)
        }
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
