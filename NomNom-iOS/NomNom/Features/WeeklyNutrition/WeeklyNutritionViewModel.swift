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
    @Published var nutritionInsights: NutritionInsights?
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
        formatter.timeZone = TimeZone(abbreviation: "UTC")  // Always use UTC for consistency
        let dateString = formatter.string(from: endDate)

        let apiPeriod = period.rawValue
        print("[InsightViewModel] Loading summary for period=\(apiPeriod), date=\(dateString)")

        do {
            let path = "/api/v1/analytics/summary?period=\(apiPeriod)&date=\(dateString)"
            print("[InsightViewModel] API Request: GET \(path)")

            summary = try await api.get(path: path)

            if let summary = summary {
                print("[InsightViewModel] ✅ Summary loaded successfully")
                print("[InsightViewModel] - Period: \(summary.period)")
                print("[InsightViewModel] - Date range: \(summary.startDate) to \(summary.endDate)")
                print("[InsightViewModel] - Days logged: \(summary.daysLogged)/\(summary.totalDays)")
                print("[InsightViewModel] - Daily breakdown count: \(summary.dailyBreakdown.count)")
            } else {
                print("[InsightViewModel] ⚠️ Summary is nil after API call")
            }
        } catch {
            print("[InsightViewModel] ❌ Failed to load summary: \(error)")
            print("[InsightViewModel] Error type: \(type(of: error))")
            print("[InsightViewModel] Error description: \(error.localizedDescription)")
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

            // Use UTC calendar to avoid timezone issues
            var utcCalendar = Calendar(identifier: .gregorian)
            utcCalendar.timeZone = TimeZone(abbreviation: "UTC") ?? TimeZone.current

            let newEndDate = utcCalendar.date(byAdding: .day, value: -days, to: currentEndDate) ?? Date()
            selectedDate = newEndDate

            let formatter = DateFormatter()
            formatter.dateFormat = "yyyy-MM-dd"
            formatter.timeZone = TimeZone(abbreviation: "UTC")
            let currentStr = formatter.string(from: currentEndDate)
            let newStr = formatter.string(from: newEndDate)
            print("[InsightViewModel] Previous button: Moving from \(currentStr) to \(newStr) (period=\(days) days)")

            await loadInsightData(endDate: newEndDate, period: selectedPeriod)
        } else {
            print("[InsightViewModel] Previous button: Could not get current end date from summary")
        }
    }

    func nextPeriod() async {
        if let currentEndDate = getEndDateFromSummary() {
            let maxDate = getDefaultEndDate()
            let days = selectedPeriod.days

            // Use UTC calendar to avoid timezone issues
            var utcCalendar = Calendar(identifier: .gregorian)
            utcCalendar.timeZone = TimeZone(abbreviation: "UTC") ?? TimeZone.current

            let newEndDate = utcCalendar.date(byAdding: .day, value: days, to: currentEndDate) ?? Date()

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

            var utcCalendar = Calendar(identifier: .gregorian)
            utcCalendar.timeZone = TimeZone(abbreviation: "UTC") ?? TimeZone.current

            if let nextDate = utcCalendar.date(byAdding: .day, value: days, to: currentEndDate) {
                return nextDate <= maxDate
            }
        }
        return false
    }

    private func getEndDateFromSummary() -> Date? {
        guard let summary = summary else { return nil }
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        formatter.timeZone = TimeZone(abbreviation: "UTC")  // Always use UTC for consistency
        let parsedDate = formatter.date(from: summary.endDate)
        if parsedDate == nil {
            print("[InsightViewModel] ⚠️ Failed to parse endDate: \(summary.endDate)")
        }
        return parsedDate
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
        formatter.timeZone = TimeZone(abbreviation: "UTC")  // Always use UTC for consistency
        return formatter.date(from: dateString)
    }

    func loadNutritionInsights() async {
        do {
            print("[InsightViewModel] Loading nutrition insights...")
            let path = "/api/v1/nutrition/insights"

            let response: NutritionInsightsResponse = try await api.get(path: path)
            print("[InsightViewModel] API Response received: analysis=\(response.analysis != nil ? "not nil" : "nil")")

            nutritionInsights = response.analysis

            if let insights = nutritionInsights {
                print("[InsightViewModel] ✅ Nutrition insights loaded successfully")
                print("[InsightViewModel]   - Summary: \(insights.summary.prefix(50))...")
                print("[InsightViewModel]   - Strengths: \(insights.strengths.count)")
                print("[InsightViewModel]   - Gaps: \(insights.gaps.count)")
                print("[InsightViewModel]   - Recommendations: \(insights.recommendations.count)")
            } else {
                print("[InsightViewModel] ⚠️ Insights returned but analysis is nil")
            }
        } catch {
            print("[InsightViewModel] ❌ Failed to load nutrition insights: \(error)")
            print("[InsightViewModel]    Error type: \(type(of: error))")
            if let decodingError = error as? DecodingError {
                print("[InsightViewModel]    Decoding error: \(decodingError)")
            }
            // Don't set errorMessage - this is supplementary data
        }
    }
}

// MARK: - API Response Models

struct NutritionInsightsResponse: Codable {
    let analysis: NutritionInsights?
}

struct NutritionInsights: Codable {
    let summary: String
    let strengths: [String]
    let gaps: [String]
    let recommendations: [RecommendationItem]
}

struct RecommendationItem: Codable {
    let nutrient: String
    let foods: [String]
    let reasoning: String
}
