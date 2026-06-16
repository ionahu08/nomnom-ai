import SwiftUI

struct NutritionCoachView: View {
    @StateObject private var viewModel = NutritionCoachViewModel()
    @FocusState private var isInputFocused: Bool

    var body: some View {
        NavigationStack {
            ZStack {
                VStack(spacing: 0) {
                    // Message list
                    ScrollViewReader { scrollProxy in
                        ScrollView {
                            VStack(spacing: 0) {
                                if viewModel.chatMessages.isEmpty {
                                    emptyStateView
                                } else {
                                    ForEach(viewModel.chatMessages) { message in
                                        ChatMessageView(message: message)
                                            .id(message.id)
                                    }
                                    // Spacer to push messages up and auto-scroll to bottom
                                    Spacer()
                                        .id("bottom")
                                }
                            }
                        }
                        .frame(maxHeight: .infinity)
                        .onReceive(viewModel.$chatMessages) { messages in
                            if !messages.isEmpty {
                                withAnimation {
                                    scrollProxy.scrollTo("bottom", anchor: .bottom)
                                }
                            }
                        }
                    }

                    Divider()

                    // Quick prompts
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 8) {
                            quickPromptButton(
                                "📊 Summarize week",
                                prompt: "Summarize my nutrition this week"
                            )
                            quickPromptButton(
                                "💪 Protein boost",
                                prompt: "Suggest foods to improve protein intake"
                            )
                            quickPromptButton(
                                "💊 Supplements",
                                prompt: "Recommend supplements based on my gaps"
                            )
                            quickPromptButton(
                                "🍽️ Tomorrow's plan",
                                prompt: "What should I eat tomorrow?"
                            )
                            quickPromptButton(
                                "✅ On track?",
                                prompt: "Am I hitting my goals?"
                            )
                        }
                        .padding(.horizontal)
                        .padding(.vertical, 8)
                    }

                    // Input section
                    VStack(spacing: 8) {
                        HStack(spacing: 8) {
                            TextField("Ask me anything...", text: $viewModel.userInput)
                                .font(.body)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 10)
                                .background(Color(.systemGray6))
                                .cornerRadius(20)
                                .focused($isInputFocused)

                            Button(action: {
                                Task {
                                    let messageText = viewModel.userInput
                                    await viewModel.sendMessage(messageText)
                                }
                            }) {
                                Image(systemName: "arrow.up.circle.fill")
                                    .font(.system(size: 24))
                                    .foregroundColor(viewModel.userInput.trimmingCharacters(in: .whitespaces).isEmpty ? .gray : .blue)
                            }
                            .disabled(viewModel.userInput.trimmingCharacters(in: .whitespaces).isEmpty || viewModel.isLoading)
                        }
                        .padding(.horizontal)
                        .padding(.vertical, 8)

                        if viewModel.isLoading {
                            HStack(spacing: 6) {
                                ProgressView()
                                    .scaleEffect(0.8)
                                Text("Coach is thinking...")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            .padding(.horizontal)
                        }

                        if let error = viewModel.errorMessage {
                            HStack(spacing: 8) {
                                Image(systemName: "exclamationmark.circle.fill")
                                    .foregroundColor(.red)
                                Text(error)
                                    .font(.caption)
                                    .foregroundColor(.red)
                                Spacer()
                            }
                            .padding(.horizontal)
                            .padding(.vertical, 8)
                            .background(Color.red.opacity(0.1))
                            .cornerRadius(8)
                            .padding(.horizontal)
                        }
                    }
                }

                if viewModel.isLoading && viewModel.chatMessages.isEmpty {
                    VStack(spacing: 16) {
                        ProgressView()
                        Text("Loading chat history...")
                            .foregroundColor(.secondary)
                    }
                }
            }
            .navigationTitle("🥗 Nutrition Coach")
            .navigationBarTitleDisplayMode(.inline)
        }
        .task {
            print("[NutritionCoach] View appeared, loading chat history")
            await viewModel.loadChatHistory()
        }
    }

    // MARK: - Subviews

    private var emptyStateView: some View {
        VStack(spacing: 16) {
            Text("🥗")
                .font(.system(size: 48))

            Text("Welcome to Your Nutrition Coach")
                .font(.headline)

            Text("Ask me about your nutrition, get food recommendations, or use the quick prompts below to get started!")
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)
        }
        .frame(maxHeight: .infinity, alignment: .center)
        .padding()
    }

    private func quickPromptButton(_ label: String, prompt: String) -> some View {
        Button(action: {
            Task {
                await viewModel.sendQuickPrompt(prompt)
            }
        }) {
            Text(label)
                .font(.caption)
                .fontWeight(.semibold)
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .background(Color.blue.opacity(0.1))
                .foregroundColor(.blue)
                .cornerRadius(16)
        }
        .disabled(viewModel.isLoading)
    }
}

#Preview {
    NutritionCoachView()
}
