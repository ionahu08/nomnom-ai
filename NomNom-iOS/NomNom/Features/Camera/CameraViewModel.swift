import Foundation
import SwiftUI

@MainActor
class CameraViewModel: ObservableObject {
    @Published var capturedImageData: Data?
    @Published var analysisResult: FoodAnalysisResponse?
    @Published var isAnalyzing = false
    @Published var isSaving = false
    @Published var showCamera = false
    @Published var errorMessage: String?
    @Published var savedSuccessfully = false

    private let api = APIClient.shared

    func analyzePhoto() async {
        guard let imageData = capturedImageData else { return }

        isAnalyzing = true
        errorMessage = nil

        do {
            let result: FoodAnalysisResponse = try await api.upload(
                path: "/api/v1/food-logs/analyze",
                imageData: imageData
            )
            analysisResult = result
        } catch {
            errorMessage = error.localizedDescription
        }

        isAnalyzing = false
    }

    func saveLog() async {
        guard let analysis = analysisResult else { return }

        isSaving = true

        do {
            let logData = FoodLogCreate(
                photoPath: "from-app.jpg",
                foodName: analysis.foodName,
                calories: analysis.calories,
                proteinG: analysis.proteinG,
                carbsG: analysis.carbsG,
                fatG: analysis.fatG,
                foodCategory: analysis.foodCategory,
                cuisineOrigin: analysis.cuisineOrigin,
                catRoast: analysis.catRoast
            )

            let _: FoodLogResponse = try await api.post(
                path: "/api/v1/food-logs/",
                body: logData
            )
            savedSuccessfully = true
        } catch {
            errorMessage = error.localizedDescription
        }

        isSaving = false
    }

    func reset() {
        capturedImageData = nil
        analysisResult = nil
        errorMessage = nil
        savedSuccessfully = false
    }
}
