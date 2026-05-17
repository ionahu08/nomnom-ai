import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";

// Mock everything before any imports
vi.doMock("server-only");
vi.doMock("next/headers", () => ({
  cookies: vi.fn(),
}));
vi.doMock("jose");

describe("createSession", () => {
  let createSession: any;
  let mockCookieStore: any;
  let mockSignJWT: any;
  let jose: any;
  let cookiesModule: any;

  beforeEach(async () => {
    vi.clearAllMocks();

    // Dynamic import after mocks are set up
    const authModule = await import("@/lib/auth");
    createSession = authModule.createSession;

    // Get the mocked modules
    cookiesModule = await import("next/headers");
    jose = await import("jose");

    // Setup cookie store mock
    mockCookieStore = {
      set: vi.fn(),
      get: vi.fn(),
      delete: vi.fn(),
    };

    cookiesModule.cookies.mockResolvedValue(mockCookieStore);

    // Setup SignJWT mock with fluent interface
    mockSignJWT = {
      setProtectedHeader: vi.fn().mockReturnThis(),
      setExpirationTime: vi.fn().mockReturnThis(),
      setIssuedAt: vi.fn().mockReturnThis(),
      sign: vi.fn().mockResolvedValue("mock-jwt-token"),
    };

    jose.SignJWT.mockImplementation(() => mockSignJWT);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("should create a JWT token with correct headers", async () => {
    await createSession("user-123", "test@example.com");

    expect(jose.SignJWT).toHaveBeenCalled();
    expect(mockSignJWT.setProtectedHeader).toHaveBeenCalledWith({
      alg: "HS256",
    });
  });

  it("should set JWT expiration to 7 days", async () => {
    await createSession("user-123", "test@example.com");

    expect(mockSignJWT.setExpirationTime).toHaveBeenCalledWith("7d");
  });

  it("should set issued at timestamp", async () => {
    await createSession("user-123", "test@example.com");

    expect(mockSignJWT.setIssuedAt).toHaveBeenCalled();
  });

  it("should sign the JWT token", async () => {
    await createSession("user-123", "test@example.com");

    expect(mockSignJWT.sign).toHaveBeenCalled();
  });

  it("should set auth-token cookie with token value", async () => {
    await createSession("user-123", "test@example.com");

    expect(mockCookieStore.set).toHaveBeenCalledWith(
      "auth-token",
      "mock-jwt-token",
      expect.any(Object)
    );
  });

  it("should set cookie with httpOnly flag", async () => {
    await createSession("user-123", "test@example.com");

    const callArgs = mockCookieStore.set.mock.calls[0][2];
    expect(callArgs.httpOnly).toBe(true);
  });

  it("should set cookie with sameSite=lax", async () => {
    await createSession("user-123", "test@example.com");

    const callArgs = mockCookieStore.set.mock.calls[0][2];
    expect(callArgs.sameSite).toBe("lax");
  });

  it("should set cookie path to root", async () => {
    await createSession("user-123", "test@example.com");

    const callArgs = mockCookieStore.set.mock.calls[0][2];
    expect(callArgs.path).toBe("/");
  });

  it("should set secure flag in production", async () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = "production";

    await createSession("user-123", "test@example.com");

    const callArgs = mockCookieStore.set.mock.calls[0][2];
    expect(callArgs.secure).toBe(true);

    process.env.NODE_ENV = originalEnv;
  });

  it("should not set secure flag in development", async () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = "development";

    await createSession("user-123", "test@example.com");

    const callArgs = mockCookieStore.set.mock.calls[0][2];
    expect(callArgs.secure).toBe(false);

    process.env.NODE_ENV = originalEnv;
  });

  it("should set cookie expiration to 7 days from now", async () => {
    const beforeTime = Date.now();

    await createSession("user-123", "test@example.com");

    const afterTime = Date.now();
    const callArgs = mockCookieStore.set.mock.calls[0][2];
    const expiresAt = callArgs.expires.getTime();
    const sevenDaysMs = 7 * 24 * 60 * 60 * 1000;

    expect(expiresAt - beforeTime).toBeGreaterThanOrEqual(sevenDaysMs);
    expect(expiresAt - afterTime).toBeLessThanOrEqual(sevenDaysMs + 100); // +100ms buffer for execution time
  });

  it("should include userId and email in JWT payload", async () => {
    const userId = "user-456";
    const email = "user@test.com";

    await createSession(userId, email);

    const signJwtPayload = (jose.SignJWT as any).mock.calls[0][0];
    expect(signJwtPayload.userId).toBe(userId);
    expect(signJwtPayload.email).toBe(email);
  });

  it("should include expiresAt in JWT payload", async () => {
    await createSession("user-123", "test@example.com");

    const signJwtPayload = (jose.SignJWT as any).mock.calls[0][0];
    expect(signJwtPayload.expiresAt).toBeDefined();
    expect(signJwtPayload.expiresAt instanceof Date).toBe(true);
  });
});

describe("getSession", () => {
  let getSession: any;
  let mockCookieStore: any;
  let jose: any;
  let cookiesModule: any;

  beforeEach(async () => {
    vi.clearAllMocks();

    // Dynamic import after mocks are set up
    const authModule = await import("@/lib/auth");
    getSession = authModule.getSession;

    // Get the mocked modules
    cookiesModule = await import("next/headers");
    jose = await import("jose");

    // Setup cookie store mock
    mockCookieStore = {
      set: vi.fn(),
      get: vi.fn(),
      delete: vi.fn(),
    };

    cookiesModule.cookies.mockResolvedValue(mockCookieStore);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("should return null when no auth token exists", async () => {
    mockCookieStore.get.mockReturnValue(undefined);

    const session = await getSession();

    expect(session).toBeNull();
    expect(mockCookieStore.get).toHaveBeenCalledWith("auth-token");
  });

  it("should attempt to verify token when it exists", async () => {
    const mockToken = "valid-jwt-token";
    mockCookieStore.get.mockReturnValue({ value: mockToken });

    jose.jwtVerify.mockResolvedValue({
      payload: {
        userId: "user-123",
        email: "test@example.com",
        expiresAt: new Date(),
      },
    });

    await getSession();

    expect(jose.jwtVerify).toHaveBeenCalled();
    const callArgs = jose.jwtVerify.mock.calls[0];
    expect(callArgs[0]).toBe(mockToken);
    expect(callArgs[1]).toBeDefined();
  });

  it("should return session payload on successful token verification", async () => {
    const mockPayload = {
      userId: "user-456",
      email: "user@test.com",
      expiresAt: new Date("2026-05-24"),
    };

    mockCookieStore.get.mockReturnValue({ value: "valid-token" });
    jose.jwtVerify.mockResolvedValue({
      payload: mockPayload,
    });

    const session = await getSession();

    expect(session).toEqual(mockPayload);
    expect(session?.userId).toBe("user-456");
    expect(session?.email).toBe("user@test.com");
  });

  it("should return null on token verification failure", async () => {
    mockCookieStore.get.mockReturnValue({ value: "invalid-token" });
    jose.jwtVerify.mockRejectedValue(new Error("Invalid signature"));

    const session = await getSession();

    expect(session).toBeNull();
  });

  it("should return null on JWT verification timeout", async () => {
    mockCookieStore.get.mockReturnValue({ value: "expired-token" });
    jose.jwtVerify.mockRejectedValue(
      new Error("Token is expired or invalid")
    );

    const session = await getSession();

    expect(session).toBeNull();
  });

  it("should return null on malformed token", async () => {
    mockCookieStore.get.mockReturnValue({ value: "not-a-valid-jwt" });
    jose.jwtVerify.mockRejectedValue(new Error("Malformed JWT"));

    const session = await getSession();

    expect(session).toBeNull();
  });

  it("should get cookie from auth-token specifically", async () => {
    mockCookieStore.get.mockReturnValue(undefined);

    await getSession();

    expect(mockCookieStore.get).toHaveBeenCalledWith("auth-token");
    expect(mockCookieStore.get).toHaveBeenCalledTimes(1);
  });

  it("should return payload with all required session fields", async () => {
    const expiresAtDate = new Date("2026-06-01");
    const mockPayload = {
      userId: "user-789",
      email: "session@test.com",
      expiresAt: expiresAtDate,
    };

    mockCookieStore.get.mockReturnValue({ value: "token-with-payload" });
    jose.jwtVerify.mockResolvedValue({
      payload: mockPayload,
    });

    const session = await getSession();

    expect(session).toBeDefined();
    expect(session?.userId).toBeDefined();
    expect(session?.email).toBeDefined();
    expect(session?.expiresAt).toBeDefined();
    expect(session?.expiresAt).toEqual(expiresAtDate);
  });

  it("should handle empty token string gracefully", async () => {
    mockCookieStore.get.mockReturnValue({ value: "" });
    jose.jwtVerify.mockRejectedValue(new Error("Empty token"));

    const session = await getSession();

    expect(session).toBeNull();
  });

  it("should not return session if verification fails even with token present", async () => {
    mockCookieStore.get.mockReturnValue({ value: "some-token" });
    jose.jwtVerify.mockRejectedValue(new Error("Verification failed"));

    const session = await getSession();

    expect(session).toBeNull();
    expect(mockCookieStore.get).toHaveBeenCalled();
    expect(jose.jwtVerify).toHaveBeenCalled();
  });

  it("should use the JWT_SECRET for verification", async () => {
    mockCookieStore.get.mockReturnValue({ value: "valid-token" });
    jose.jwtVerify.mockResolvedValue({
      payload: {
        userId: "user-123",
        email: "test@example.com",
        expiresAt: new Date(),
      },
    });

    await getSession();

    expect(jose.jwtVerify).toHaveBeenCalled();
    const callArgs = jose.jwtVerify.mock.calls[0];
    expect(callArgs[0]).toBe("valid-token");
    expect(callArgs[1]).toBeDefined();
    expect(typeof callArgs[1]).toBe("object");
  });
});
