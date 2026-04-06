import Foundation

struct FoodAnalysisResponse: Codable {
    let foodName: String
    let calories: Int
    let proteinG: Double
    let carbsG: Double
    let fatG: Double
    let photoPath: String
    let foodCategory: String?
    let cuisineOrigin: String?
    let catRoast: String

    enum CodingKeys: String, CodingKey {
        case foodName = "food_name"
        case calories
        case proteinG = "protein_g"
        case carbsG = "carbs_g"
        case fatG = "fat_g"
        case photoPath = "photo_path"
        case foodCategory = "food_category"
        case cuisineOrigin = "cuisine_origin"
        case catRoast = "cat_roast"
    }
}

struct FoodLogCreate: Codable {
    let photoPath: String
    let foodName: String
    let calories: Int
    let proteinG: Double
    let carbsG: Double
    let fatG: Double
    let foodCategory: String?
    let cuisineOrigin: String?
    let catRoast: String

    enum CodingKeys: String, CodingKey {
        case photoPath = "photo_path"
        case foodName = "food_name"
        case calories
        case proteinG = "protein_g"
        case carbsG = "carbs_g"
        case fatG = "fat_g"
        case foodCategory = "food_category"
        case cuisineOrigin = "cuisine_origin"
        case catRoast = "cat_roast"
    }
}

struct FoodLogResponse: Codable, Identifiable {
    let id: Int
    let userId: Int
    let photoPath: String
    let foodName: String
    let calories: Int
    let proteinG: Double
    let carbsG: Double
    let fatG: Double
    let foodCategory: String?
    let cuisineOrigin: String?
    let catRoast: String
    let isUserCorrected: Bool
    let loggedAt: String
    let createdAt: String

    enum CodingKeys: String, CodingKey {
        case id
        case userId = "user_id"
        case photoPath = "photo_path"
        case foodName = "food_name"
        case calories
        case proteinG = "protein_g"
        case carbsG = "carbs_g"
        case fatG = "fat_g"
        case foodCategory = "food_category"
        case cuisineOrigin = "cuisine_origin"
        case catRoast = "cat_roast"
        case isUserCorrected = "is_user_corrected"
        case loggedAt = "logged_at"
        case createdAt = "created_at"
    }
}
