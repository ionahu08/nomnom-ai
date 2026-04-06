import Foundation

@MainActor
class TodayViewModel: ObservableObject {
    @Published var logs: [FoodLogResponse] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var recommendation: String?
    @Published var isLoadingRecommendation = false
    @Published var recommendationKBEntries = 0

    private let api = APIClient.shared
    private let recommendationService = RecommendationService()

    func loadTodayLogs() async {
        isLoading = true
        errorMessage = nil

        do {
            logs = try await api.get(path: "/api/v1/food-logs/today")
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func deleteLog(id: Int) async {
        do {
            try await api.delete(path: "/api/v1/food-logs/\(id)")
            logs.removeAll { $0.id == id }
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func loadRecommendation() async {
        isLoadingRecommendation = true
        errorMessage = nil
        defer { isLoadingRecommendation = false }

        do {
            let result = try await recommendationService.getMealRecommendation()
            recommendation = result.recommendation
            recommendationKBEntries = result.kbEntriesUsed
        } catch {
            errorMessage = "Failed to get recommendation: \(error.localizedDescription)"
        }
    }
}
