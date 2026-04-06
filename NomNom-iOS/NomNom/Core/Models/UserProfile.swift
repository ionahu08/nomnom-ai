import Foundation

struct UserProfile: Codable {
    var age: Int?
    var gender: String?
    var heightCm: Double?
    var weightKg: Double?
    var activityLevel: String?
    var calorieTarget: Int?
    var proteinTarget: Int?
    var carbTarget: Int?
    var fatTarget: Int?
    var catStyle: String?
    var dietaryRestrictions: [String]?
    var allergies: [String]?
    var cuisinePreferences: [String]?

    enum CodingKeys: String, CodingKey {
        case age
        case gender
        case heightCm = "height_cm"
        case weightKg = "weight_kg"
        case activityLevel = "activity_level"
        case calorieTarget = "calorie_target"
        case proteinTarget = "protein_target"
        case carbTarget = "carb_target"
        case fatTarget = "fat_target"
        case catStyle = "cat_style"
        case dietaryRestrictions = "dietary_restrictions"
        case allergies
        case cuisinePreferences = "cuisine_preferences"
    }
}

struct MacroTargets: Codable {
    let calorieTarget: Int
    let proteinTarget: Int
    let carbTarget: Int
    let fatTarget: Int

    enum CodingKeys: String, CodingKey {
        case calorieTarget = "calorie_target"
        case proteinTarget = "protein_target"
        case carbTarget = "carb_target"
        case fatTarget = "fat_target"
    }
}
