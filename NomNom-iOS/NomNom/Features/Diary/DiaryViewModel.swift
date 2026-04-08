import Foundation

@MainActor
class DiaryViewModel: ObservableObject {
    @Published var selectedDate: Date = Date()
    @Published var logsForSelectedDate: [FoodLogResponse] = []
    @Published var calendarSummary: [DayCalendarSummary] = []
    @Published var isLoadingLogs = false
    @Published var isLoadingCalendar = false
    @Published var errorMessage: String?

    private let api = APIClient.shared
    private let dateFormatter = ISO8601DateFormatter()

    init() {
        dateFormatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
    }

    func loadCalendarSummary() async {
        isLoadingCalendar = true
        errorMessage = nil

        do {
            let calendar = Calendar.current
            let startDate = calendar.date(from: DateComponents(year: 2026, month: 1, day: 1))!

            // End date: first day of next month (so current month is fully visible)
            let now = Date()
            let endComponents = calendar.dateComponents([.year, .month], from: now)
            var nextMonthComponents = endComponents
            nextMonthComponents.month! += 1
            if nextMonthComponents.month! > 12 {
                nextMonthComponents.month! = 1
                nextMonthComponents.year! += 1
            }
            nextMonthComponents.day = 1
            let endDate = calendar.date(from: nextMonthComponents)!

            let startStr = formatDateForAPI(startDate)
            let endStr = formatDateForAPI(endDate)

            let summary: [DayCalendarSummary] = try await api.get(
                path: "/api/v1/food-logs/calendar-summary?start=\(startStr)&end=\(endStr)"
            )
            self.calendarSummary = summary

            // After loading calendar, find last date with logs and set it as selected
            if let lastDate = summary.first?.date {
                if let date = parseAPIDate(lastDate) {
                    self.selectedDate = date
                    await loadLogs(for: date)
                }
            } else {
                // No logs at all, default to today
                self.selectedDate = Date()
                await loadLogs(for: Date())
            }
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoadingCalendar = false
    }

    func loadLogs(for date: Date) async {
        isLoadingLogs = true
        errorMessage = nil

        do {
            let dateStr = formatDateForAPI(date)
            let logs: [FoodLogResponse] = try await api.get(path: "/api/v1/food-logs/by-date?date=\(dateStr)")
            self.logsForSelectedDate = logs
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoadingLogs = false
    }

    func deleteLog(id: Int) async {
        do {
            try await api.delete(path: "/api/v1/food-logs/\(id)")
            logsForSelectedDate.removeAll { $0.id == id }

            // Reload calendar summary to update badges
            let calendar = Calendar.current
            let startDate = calendar.date(from: DateComponents(year: 2026, month: 1, day: 1))!

            let now = Date()
            let endComponents = calendar.dateComponents([.year, .month], from: now)
            var nextMonthComponents = endComponents
            nextMonthComponents.month! += 1
            if nextMonthComponents.month! > 12 {
                nextMonthComponents.month! = 1
                nextMonthComponents.year! += 1
            }
            nextMonthComponents.day = 1
            let endDate = calendar.date(from: nextMonthComponents)!

            let startStr = formatDateForAPI(startDate)
            let endStr = formatDateForAPI(endDate)

            let summary: [DayCalendarSummary] = try await api.get(
                path: "/api/v1/food-logs/calendar-summary?start=\(startStr)&end=\(endStr)"
            )
            self.calendarSummary = summary
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    // MARK: - Helpers

    private func formatDateForAPI(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.string(from: date)
    }

    private func parseAPIDate(_ dateStr: String) -> Date? {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.date(from: dateStr)
    }
}
