import Foundation

struct WeeklySummaryResponse: Codable {
    let period: String
    let startDate: String
    let endDate: String
    let daysLogged: Int
    let totalDays: Int
    let consistency: Double
    let calories: NutrientSummary
    let proteinG: NutrientSummary
    let carbsG: NutrientSummary
    let fatG: NutrientSummary
    let dailyBreakdown: [DailyBreakdown]
    let topFoods: [TopFood]

    enum CodingKeys: String, CodingKey {
        case period
        case startDate = "start_date"
        case endDate = "end_date"
        case daysLogged = "days_logged"
        case totalDays = "total_days"
        case consistency
        case calories
        case proteinG = "protein_g"
        case carbsG = "carbs_g"
        case fatG = "fat_g"
        case dailyBreakdown = "daily_breakdown"
        case topFoods = "top_foods"
    }
}

struct NutrientSummary: Codable {
    let total: Int
    let average: Double
    let target: Int
    let percentage: Double?
}

struct DailyBreakdown: Codable {
    let date: String
    let calories: Int
    let proteinG: Int
    let carbsG: Int
    let fatG: Int

    enum CodingKeys: String, CodingKey {
        case date
        case calories
        case proteinG = "protein_g"
        case carbsG = "carbs_g"
        case fatG = "fat_g"
    }
}

struct TopFood: Codable {
    let food: String
    let count: Int
    let calories: Int
}
