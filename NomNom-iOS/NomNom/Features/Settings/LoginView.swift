import SwiftUI

struct LoginView: View {
    @EnvironmentObject var authService: AuthService
    @State private var email = ""
    @State private var password = ""
    @State private var isRegistering = false

    var body: some View {
        ZStack {
            NomNomColors.background.ignoresSafeArea()

            VStack(spacing: 32) {
                Spacer()

                Text("🐱")
                    .font(.system(size: 64))

                Text("NomNom")
                    .font(.system(size: 48, weight: .bold))
                    .foregroundColor(NomNomColors.primary)

                Text("Your cat judges your food")
                    .font(.body)
                    .foregroundColor(NomNomColors.textSecondary)

                VStack(spacing: 16) {
                    TextField("Email", text: $email)
                        .textFieldStyle(.plain)
                        .padding()
                        .background(NomNomColors.surfaceSecondary)
                        .cornerRadius(12)
                        .foregroundColor(NomNomColors.textPrimary)
                        .autocapitalization(.none)
                        .keyboardType(.emailAddress)

                    SecureField("Password", text: $password)
                        .textFieldStyle(.plain)
                        .padding()
                        .background(NomNomColors.surfaceSecondary)
                        .cornerRadius(12)
                        .foregroundColor(NomNomColors.textPrimary)
                }
                .padding(.horizontal, 16)

                if let error = authService.errorMessage {
                    Text(error)
                        .font(.caption)
                        .foregroundColor(NomNomColors.danger)
                }

                Button(action: {
                    Task {
                        if isRegistering {
                            await authService.register(email: email, password: password)
                        } else {
                            await authService.login(email: email, password: password)
                        }
                    }
                }) {
                    Text(isRegistering ? "Create Account" : "Sign In")
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(NomNomColors.primary)
                        .cornerRadius(12)
                }
                .padding(.horizontal, 16)

                Button(action: { isRegistering.toggle() }) {
                    Text(isRegistering ? "Already have an account? Sign In" : "Don't have an account? Register")
                        .font(.caption)
                        .foregroundColor(NomNomColors.textSecondary)
                }

                Spacer()
            }
        }
    }
}
