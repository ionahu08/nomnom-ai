import Foundation

enum APIError: Error, LocalizedError {
    case invalidURL
    case unauthorized
    case badRequest(String)
    case serverError(Int)
    case decodingError
    case networkError(Error)

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Invalid URL"
        case .unauthorized: return "Please log in again"
        case .badRequest(let message): return message
        case .serverError(let code): return "Server error (\(code))"
        case .decodingError: return "Failed to process response"
        case .networkError(let error): return error.localizedDescription
        }
    }
}

private struct ErrorDetail: Decodable {
    let detail: String
}

class APIClient {
    static let shared = APIClient()

    let baseURL: String
    private var token: String?
    var onUnauthorized: (() -> Void)?

    init(baseURL: String? = nil) {
        #if targetEnvironment(simulator)
        self.baseURL = baseURL ?? "http://localhost:8000"
        #else
        self.baseURL = baseURL ?? "https://viewer-set-worm-extended.trycloudflare.com"
        #endif
    }

    func setToken(_ token: String?) {
        self.token = token
    }

    // MARK: - JSON requests

    func request<T: Decodable>(
        _ method: String,
        path: String,
        body: Encodable? = nil
    ) async throws -> T {
        guard let url = URL(string: "\(baseURL)\(path)") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if let token = token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body = body {
            request.httpBody = try JSONEncoder().encode(body)
        }

        return try await execute(request)
    }

    // MARK: - Multipart upload (for food photos)

    func upload<T: Decodable>(
        path: String,
        imageData: Data,
        filename: String = "photo.jpg"
    ) async throws -> T {
        guard let url = URL(string: "\(baseURL)\(path)") else {
            throw APIError.invalidURL
        }

        let boundary = UUID().uuidString
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        if let token = token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
        body.append(imageData)
        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)

        request.httpBody = body

        return try await execute(request)
    }

    // MARK: - Convenience methods

    func get<T: Decodable>(path: String) async throws -> T {
        try await request("GET", path: path)
    }

    // Binary data fetching (for images, etc.)
    func getData(path: String) async throws -> Data {
        guard let url = URL(string: "\(baseURL)\(path)") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "GET"

        if let token = token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.networkError(URLError(.badServerResponse))
        }

        switch httpResponse.statusCode {
        case 200...299:
            return data
        case 401, 403:
            await MainActor.run { onUnauthorized?() }
            throw APIError.unauthorized
        default:
            throw APIError.serverError(httpResponse.statusCode)
        }
    }

    func post<T: Decodable>(path: String, body: Encodable? = nil) async throws -> T {
        try await request("POST", path: path, body: body)
    }

    func patch<T: Decodable>(path: String, body: Encodable? = nil) async throws -> T {
        try await request("PATCH", path: path, body: body)
    }

    func delete(path: String) async throws {
        guard let url = URL(string: "\(baseURL)\(path)") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        if let token = token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        let (_, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.networkError(URLError(.badServerResponse))
        }

        if httpResponse.statusCode == 401 || httpResponse.statusCode == 403 {
            await MainActor.run { onUnauthorized?() }
            throw APIError.unauthorized
        }

        if httpResponse.statusCode >= 400 {
            throw APIError.serverError(httpResponse.statusCode)
        }
    }

    // MARK: - Private

    private func execute<T: Decodable>(_ request: URLRequest) async throws -> T {
        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.networkError(URLError(.badServerResponse))
        }

        switch httpResponse.statusCode {
        case 200...299:
            do {
                let decoder = JSONDecoder()
                decoder.dateDecodingStrategy = .iso8601
                return try decoder.decode(T.self, from: data)
            } catch {
                throw APIError.decodingError
            }
        case 401, 403:
            await MainActor.run { onUnauthorized?() }
            throw APIError.unauthorized
        case 400:
            if let body = try? JSONDecoder().decode(ErrorDetail.self, from: data) {
                throw APIError.badRequest(body.detail)
            }
            throw APIError.serverError(400)
        default:
            throw APIError.serverError(httpResponse.statusCode)
        }
    }
}
