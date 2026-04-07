import SwiftUI

struct FoodLogCard: View {
    let log: FoodLogResponse
    @State private var photoImage: UIImage?
    @State private var isLoadingPhoto = false

    var body: some View {
        HStack(spacing: 12) {
            // Food photo thumbnail
            ZStack {
                RoundedRectangle(cornerRadius: 12)
                    .fill(NomNomColors.surfaceSecondary)
                    .frame(width: 80, height: 80)

                if let image = photoImage {
                    Image(uiImage: image)
                        .resizable()
                        .scaledToFill()
                        .frame(width: 80, height: 80)
                        .clipped()
                        .cornerRadius(12)
                } else if isLoadingPhoto {
                    ProgressView()
                        .tint(NomNomColors.primary)
                } else {
                    Text("🍽️")
                        .font(.title2)
                }
            }

            // Food info
            VStack(alignment: .leading, spacing: 4) {
                Text(log.foodName)
                    .font(.headline)
                    .foregroundColor(NomNomColors.textPrimary)

                Text("\(log.calories) kcal • P: \(String(format: "%.0f", log.proteinG))g • C: \(String(format: "%.0f", log.carbsG))g • F: \(String(format: "%.0f", log.fatG))g")
                    .font(.caption)
                    .foregroundColor(NomNomColors.textSecondary)

                if log.isUserCorrected {
                    HStack(spacing: 2) {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.caption2)
                            .foregroundColor(NomNomColors.success)
                        Text("Corrected")
                            .font(.caption2)
                            .foregroundColor(NomNomColors.success)
                    }
                } else {
                    Text(log.catRoast)
                        .font(.caption)
                        .foregroundColor(NomNomColors.primary)
                        .lineLimit(1)
                }
            }

            Spacer()
        }
        .padding(12)
        .background(NomNomColors.surface)
        .cornerRadius(16)
        .onAppear {
            loadPhoto()
        }
    }

    private func loadPhoto() {
        isLoadingPhoto = true
        Task {
            let filename = log.photoPath.split(separator: "/").last.map(String.init) ?? log.photoPath

            do {
                let imageData: Data = try await APIClient.shared.getData(
                    path: "/api/v1/photos/\(filename)"
                )
                if let uiImage = UIImage(data: imageData) {
                    await MainActor.run {
                        self.photoImage = uiImage
                        self.isLoadingPhoto = false
                    }
                } else {
                    await MainActor.run {
                        self.isLoadingPhoto = false
                    }
                }
            } catch {
                await MainActor.run {
                    self.isLoadingPhoto = false
                }
            }
        }
    }
}
