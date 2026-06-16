import Foundation

@MainActor
class NutritionCoachViewModel: ObservableObject {
    @Published var chatMessages: [ChatMessage] = []
    @Published var userInput: String = ""
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let api = APIClient.shared

    // MARK: - Lifecycle

    func loadChatHistory() async {
        do {
            print("[NutritionCoach] Loading chat history...")
            let path = "/api/v1/nutrition/chat/history"

            let response: ChatHistoryResponse = try await api.get(path: path)
            chatMessages = response.messages

            print("[NutritionCoach] ✅ Loaded \(chatMessages.count) messages")
        } catch {
            print("[NutritionCoach] ⚠️ Failed to load chat history: \(error)")
            errorMessage = "Failed to load chat history"
        }
    }

    // MARK: - Message Sending

    func sendMessage(_ text: String) async {
        guard !text.trimmingCharacters(in: .whitespaces).isEmpty else { return }

        isLoading = true
        errorMessage = nil
        userInput = ""

        do {
            print("[NutritionCoach] Sending message: \(text.prefix(50))...")

            let request = ChatMessageRequest(message: text)
            let path = "/api/v1/nutrition/chat"

            let response: ChatMessage = try await api.post(path: path, body: request)

            print("[NutritionCoach] ✅ Got response from coach")

            // Add response to messages
            chatMessages.append(response)

            // Scroll to bottom
            if !chatMessages.isEmpty {
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                    // Message added, UI will scroll automatically
                }
            }
        } catch {
            print("[NutritionCoach] ❌ Failed to send message: \(error)")
            errorMessage = "Failed to send message"
            isLoading = false
        }

        isLoading = false
    }

    func sendQuickPrompt(_ prompt: String) async {
        await sendMessage(prompt)
    }
}

// MARK: - API Models

struct ChatMessageRequest: Codable {
    let message: String
}

struct ChatHistoryResponse: Codable {
    let messages: [ChatMessage]
}
