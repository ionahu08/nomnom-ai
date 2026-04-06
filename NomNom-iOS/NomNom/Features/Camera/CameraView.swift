import SwiftUI

struct CameraView: View {
    @StateObject private var viewModel = CameraViewModel()

    var body: some View {
        NavigationStack {
            ZStack {
                NomNomColors.background.ignoresSafeArea()

                if let analysis = viewModel.analysisResult {
                    // Show analysis result
                    analysisResultView(analysis)
                } else if viewModel.isAnalyzing {
                    // Loading state
                    VStack(spacing: 16) {
                        ProgressView()
                            .tint(NomNomColors.primary)
                            .scaleEffect(1.5)
                        Text("Cat is judging your food...")
                            .foregroundColor(NomNomColors.textSecondary)
                    }
                } else {
                    // Camera prompt
                    cameraPromptView
                }
            }
            .navigationTitle("Camera")
            .navigationBarTitleDisplayMode(.inline)
            .toolbarColorScheme(.dark, for: .navigationBar)
            .sheet(isPresented: $viewModel.showCamera) {
                PhotoPicker(imageData: $viewModel.capturedImageData)
            }
            .onChange(of: viewModel.capturedImageData != nil) { hasData in
                if hasData {
                    Task { await viewModel.analyzePhoto() }
                }
            }
            .alert("Saved!", isPresented: $viewModel.savedSuccessfully) {
                Button("OK") { viewModel.reset() }
            } message: {
                Text("Your food log has been saved.")
            }
        }
    }

    // MARK: - Camera prompt (no photo taken yet)

    private var cameraPromptView: some View {
        VStack(spacing: 24) {
            Spacer()

            Text("🐱")
                .font(.system(size: 80))

            Text("Feed me a photo")
                .font(.title2.bold())
                .foregroundColor(NomNomColors.textPrimary)

            Text("Snap a pic of your food and\nI'll tell you what I think")
                .font(.body)
                .foregroundColor(NomNomColors.textSecondary)
                .multilineTextAlignment(.center)

            Button(action: { viewModel.showCamera = true }) {
                HStack {
                    Image(systemName: "camera.fill")
                    Text("Take Photo")
                }
                .font(.headline)
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding()
                .background(NomNomColors.primary)
                .cornerRadius(16)
            }
            .padding(.horizontal, 32)

            Spacer()
        }
    }

    // MARK: - Analysis result

    private func analysisResultView(_ analysis: FoodAnalysisResponse) -> some View {
        ScrollView {
            VStack(spacing: 20) {
                // Food photo
                if let imageData = viewModel.capturedImageData,
                   let uiImage = UIImage(data: imageData) {
                    Image(uiImage: uiImage)
                        .resizable()
                        .scaledToFill()
                        .frame(height: 250)
                        .clipped()
                        .cornerRadius(16)
                        .padding(.horizontal, 16)
                }

                // Cat roast bubble
                RoastBubble(text: analysis.catRoast)
                    .padding(.horizontal, 16)

                // Food info card
                VStack(alignment: .leading, spacing: 12) {
                    Text(analysis.foodName)
                        .font(.title2.bold())
                        .foregroundColor(NomNomColors.textPrimary)

                    if let category = analysis.foodCategory, let cuisine = analysis.cuisineOrigin {
                        Text("\(cuisine) • \(category)")
                            .font(.subheadline)
                            .foregroundColor(NomNomColors.textSecondary)
                    }

                    Divider().background(NomNomColors.surfaceSecondary)

                    // Macro grid
                    HStack(spacing: 16) {
                        macroItem(label: "Calories", value: "\(analysis.calories)", unit: "kcal", color: NomNomColors.primary)
                        macroItem(label: "Protein", value: String(format: "%.0f", analysis.proteinG), unit: "g", color: NomNomColors.success)
                        macroItem(label: "Carbs", value: String(format: "%.0f", analysis.carbsG), unit: "g", color: NomNomColors.warning)
                        macroItem(label: "Fat", value: String(format: "%.0f", analysis.fatG), unit: "g", color: NomNomColors.danger)
                    }
                }
                .padding()
                .background(NomNomColors.surface)
                .cornerRadius(16)
                .padding(.horizontal, 16)

                // Action buttons
                HStack(spacing: 12) {
                    Button(action: { viewModel.reset() }) {
                        Text("Retake")
                            .font(.headline)
                            .foregroundColor(NomNomColors.textPrimary)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(NomNomColors.surfaceSecondary)
                            .cornerRadius(12)
                    }

                    Button(action: { Task { await viewModel.saveLog() } }) {
                        HStack {
                            if viewModel.isSaving {
                                ProgressView().tint(.white)
                            }
                            Text("Save")
                        }
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(NomNomColors.primary)
                        .cornerRadius(12)
                    }
                    .disabled(viewModel.isSaving)
                }
                .padding(.horizontal, 16)

                if let error = viewModel.errorMessage {
                    Text(error)
                        .font(.caption)
                        .foregroundColor(NomNomColors.danger)
                        .padding(.horizontal, 16)
                }
            }
            .padding(.vertical, 16)
        }
    }

    // MARK: - Macro item

    private func macroItem(label: String, value: String, unit: String, color: Color) -> some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.title3.bold())
                .foregroundColor(color)
            Text(unit)
                .font(.caption2)
                .foregroundColor(color.opacity(0.7))
            Text(label)
                .font(.caption2)
                .foregroundColor(NomNomColors.textSecondary)
        }
        .frame(maxWidth: .infinity)
    }
}
