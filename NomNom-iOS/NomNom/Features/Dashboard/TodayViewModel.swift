import Foundation

@MainActor
class TodayViewModel: ObservableObject {
    @Published var logs: [FoodLogResponse] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let api = APIClient.shared

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
}
