import SwiftUI

struct RoastBubble: View {
    let text: String

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Text("🐱")
                .font(.system(size: 36))

            Text(text)
                .font(.body)
                .foregroundColor(NomNomColors.textPrimary)
                .padding(12)
                .background(NomNomColors.surface)
                .cornerRadius(16)
        }
    }
}
