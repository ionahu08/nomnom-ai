import Foundation

struct ChatMessage: Codable, Identifiable {
    let id: String
    let role: String  // "user" or "assistant"
    let content: String
    let timestamp: Date

    var isUserMessage: Bool {
        role == "user"
    }

    enum CodingKeys: String, CodingKey {
        case id
        case role
        case content
        case timestamp
    }
}
