import Foundation

@MainActor
class InsightsViewModel: ObservableObject {
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var insights: InsightsResponse?

    private let api = APIClient.shared

    func loadInsights() async {
        // TODO: Implement insights loading after Phase 2 backend is ready
        // For now, just show placeholder
    }
}

struct InsightsResponse: Codable {
    let period: String  // "week" or "month"
    let summary: String
    let highlights: [String]
    let recommendations: [String]
}
