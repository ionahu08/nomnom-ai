import Foundation

struct MealRecommendation: Codable {
    let recommendation: String
    let kbEntriesUsed: Int

    enum CodingKeys: String, CodingKey {
        case recommendation
        case kbEntriesUsed = "kb_entries_used"
    }
}

class RecommendationService {
    private let api = APIClient.shared

    func getMealRecommendation() async throws -> MealRecommendation {
        return try await api.get(path: "/api/v1/recommendations/meal")
    }
}
