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
    @Published var showCorrectModal = false
    @Published var correctedFoodName = ""
    @Published var savedFoodLogId: Int?

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
            correctedFoodName = result.foodName
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
                photoPath: analysis.photoPath,
                foodName: analysis.foodName,
                calories: analysis.calories,
                proteinG: analysis.proteinG,
                carbsG: analysis.carbsG,
                fatG: analysis.fatG,
                foodCategory: analysis.foodCategory,
                cuisineOrigin: analysis.cuisineOrigin,
                catRoast: analysis.catRoast
            )

            let response: FoodLogResponse = try await api.post(
                path: "/api/v1/food-logs/",
                body: logData
            )
            savedFoodLogId = response.id
            savedSuccessfully = true
        } catch {
            errorMessage = error.localizedDescription
        }

        isSaving = false
    }

    func correctFood() async {
        guard let logId = savedFoodLogId, !correctedFoodName.isEmpty else { return }

        isSaving = true
        errorMessage = nil

        do {
            struct CorrectionData: Codable {
                let foodName: String
                let isUserCorrected: Bool

                enum CodingKeys: String, CodingKey {
                    case foodName = "food_name"
                    case isUserCorrected = "is_user_corrected"
                }
            }

            let correctionData = CorrectionData(
                foodName: correctedFoodName,
                isUserCorrected: true
            )

            let _: FoodLogResponse = try await api.patch(
                path: "/api/v1/food-logs/\(logId)",
                body: correctionData
            )

            showCorrectModal = false
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
        showCorrectModal = false
        correctedFoodName = ""
        savedFoodLogId = nil
    }
}
