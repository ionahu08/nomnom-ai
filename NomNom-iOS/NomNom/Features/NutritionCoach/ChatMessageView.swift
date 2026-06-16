import SwiftUI

struct ChatMessageView: View {
    let message: ChatMessage

    var body: some View {
        VStack(alignment: message.isUserMessage ? .trailing : .leading, spacing: 4) {
            // Message bubble
            Text(message.content)
                .font(.body)
                .foregroundColor(message.isUserMessage ? .white : .primary)
                .padding(.horizontal, 12)
                .padding(.vertical, 10)
                .background(
                    RoundedRectangle(cornerRadius: 16)
                        .fill(message.isUserMessage ? Color.blue : Color(.systemGray5))
                )
                .frame(maxWidth: 280, alignment: message.isUserMessage ? .trailing : .leading)

            // Timestamp
            Text(formatTimestamp(message.timestamp))
                .font(.caption2)
                .foregroundColor(.secondary)
                .padding(.horizontal, 12)
        }
        .frame(maxWidth: .infinity, alignment: message.isUserMessage ? .trailing : .leading)
        .padding(.horizontal)
        .padding(.vertical, 4)
    }

    private func formatTimestamp(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

#Preview {
    VStack(spacing: 12) {
        ChatMessageView(
            message: ChatMessage(
                id: "1",
                role: "user",
                content: "What should I eat tomorrow to improve my protein intake?",
                timestamp: Date()
            )
        )

        ChatMessageView(
            message: ChatMessage(
                id: "2",
                role: "assistant",
                content: "Based on your recent logs, I see you've been enjoying chicken and eggs. Try adding Greek yogurt to breakfast or a protein shake. You could also increase portions of the lean meats you already like!",
                timestamp: Date()
            )
        )
    }
}
