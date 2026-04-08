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
            // Compress image before upload (reduces from 2-4MB to ~200-500KB)
            let compressedData = Self.compressImage(imageData, targetSize: 800)

            let result: FoodAnalysisResponse = try await api.upload(
                path: "/api/v1/food-logs/analyze",
                imageData: compressedData
            )
            analysisResult = result
            correctedFoodName = result.foodName
        } catch {
            errorMessage = error.localizedDescription
        }

        isAnalyzing = false
    }

    /// Compress JPEG image to target size while maintaining quality
    private static func compressImage(_ imageData: Data, targetSize: CGFloat = 800) -> Data {
        guard let uiImage = UIImage(data: imageData) else { return imageData }

        // Resize image to target size (usually ~800px max)
        let resizedImage = Self.resizeImage(uiImage, maxDimension: targetSize)

        // Compress as JPEG with 0.7 quality (barely noticeable, huge size reduction)
        return resizedImage.jpegData(compressionQuality: 0.7) ?? imageData
    }

    /// Resize image to fit within maxDimension while maintaining aspect ratio
    private static func resizeImage(_ image: UIImage, maxDimension: CGFloat) -> UIImage {
        let size = image.size
        if size.width <= maxDimension && size.height <= maxDimension { return image }

        let scale = min(maxDimension / size.width, maxDimension / size.height)
        let newSize = CGSize(width: size.width * scale, height: size.height * scale)

        UIGraphicsBeginImageContextWithOptions(newSize, false, 1.0)
        image.draw(in: CGRect(origin: .zero, size: newSize))
        let resized = UIGraphicsGetImageFromCurrentImageContext() ?? image
        UIGraphicsEndImageContext()

        return resized
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
                catRoast: analysis.catRoast,
                mealType: nil
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
