# Phases — Iteration 01: MVP Core Flow

## Overview

This iteration takes NomNom from empty repos to a working end-to-end app on your phone. The loop: camera → backend → see results.

---

## Phase S1: Backend — Food Log CRUD ✅

**Goal:** Build food log endpoints and photo storage.

### S1.1: FoodLog model + migration

- [x] Create `src/models/food_log.py` — FoodLog model:
  - id (PK), user_id (FK), photo_path, food_name, calories, protein_g, carbs_g, fat_g, food_category, cuisine_origin, cat_roast, logged_at, created_at
- [x] Update `src/models/__init__.py` — import and re-export FoodLog
- [x] Run `alembic revision --autogenerate -m "create food_logs table"`
- [x] Run `alembic upgrade head`
- [x] Verify: `psql -d nomnom -c "\dt"` shows food_logs table

**Tests:**
- [x] Alembic migration runs without errors
- [x] Table exists in PostgreSQL with correct columns

### S1.2: Food log schemas

- [x] Create `src/schemas/food_log.py`:
  - FoodAnalysisResponse — what AI returns (food_name, calories, protein_g, carbs_g, fat_g, food_category, cuisine_origin, cat_roast)
  - FoodLogCreate — what client sends to save (all fields except id, created_at)
  - FoodLogResponse — what API returns (all fields)

### S1.3: Photo + food log services

- [x] Create `src/services/photo_service.py`:
  - `save_photo(image_bytes) → filename` — write to uploads/ folder
  - `get_photo_path(filename) → path`
  - `delete_photo(filename)`
- [x] Create `src/services/food_log_service.py`:
  - `create_food_log(db, user_id, data) → FoodLog`
  - `list_today_logs(db, user_id) → [FoodLog]`
  - `get_food_log(db, log_id) → FoodLog`
  - `delete_food_log(db, log_id)`

**Tests:**
- [x] Photo saved to disk, can be retrieved
- [x] Photo deleted from disk
- [x] Food log CRUD works

### S1.4: API endpoints

- [x] Create `src/api/food_logs.py`:
  - POST `/api/v1/food-logs/analyze` — upload photo, return AI analysis (stub for now)
  - POST `/api/v1/food-logs` — save confirmed food log
  - GET `/api/v1/food-logs/today` — list today's logs
  - GET `/api/v1/food-logs/{log_id}` — get one log
  - DELETE `/api/v1/food-logs/{log_id}` — delete log
- [x] Create `src/api/photos.py`:
  - GET `/api/v1/photos/{filename}` — serve food photo
- [x] Update `src/app.py` — register food_logs and photos routers

**Tests:**
- [x] POST /analyze with photo returns 200 (stub response)
- [x] POST /food-logs saves and returns created log
- [x] GET /food-logs/today returns list
- [x] DELETE removes log from database
- [x] Photo endpoint serves image
- [x] All endpoints require auth (401 without token)

**Deliverable:** Backend responds to food log CRUD. Photos saved and served. All tests pass.

---

## Phase S2: Backend — AI Photo Analysis ✅

**Goal:** Wire up Haiku to analyze food photos.

### S2.1: AI service with Haiku vision

- [x] Create `src/services/ai_service.py`:
  - `analyze_food_photo(image_bytes, cat_style) → FoodAnalysisResponse`
  - Create AsyncAnthropic client
  - Encode image to base64
  - Send vision request with system prompt (includes cat personality)
  - System prompt tells Haiku: "Return JSON with: food_name, calories, protein_g, carbs_g, fat_g, food_category, cuisine_origin, cat_roast"
  - Parse JSON response, return FoodAnalysisResponse

**Note:** This is basic AI (no retry, no fallback, no structured output). Phase 3 adds the harness.

### S2.2: Wire /analyze endpoint to real AI

- [x] Update `src/api/food_logs.py`:
  - Import ai_service
  - Replace stub in POST /analyze with real call
  - Get user's cat_style from profile (default: "sassy")
  - Pass image_bytes to ai_service
  - Return FoodAnalysisResponse
- [x] Add `ANTHROPIC_API_KEY` to `.env`

### S2.3: Test with real photo

- [x] Start server: `PYTHONPATH=. uv run python -m src.run`
- [x] Upload real food photo: `curl -F "file=@pizza.jpg" http://localhost:8000/api/v1/food-logs/analyze`
- [x] Verify response contains: food_name, calories, macros, cat_roast
- [x] Create `tests/unit/test_ai_service.py` — mocked test (doesn't call real API)

**Tests:**
- [x] Haiku returns valid JSON with all required fields
- [x] Calories are reasonable (0-5000)
- [x] Cat roast is non-empty and funny

**Deliverable:** POST /analyze calls Haiku, returns analysis. Mocked tests pass.

---

## Phase S3: iOS — Project Setup + Login ✅

**Goal:** Create Xcode project and login screen.

### S3.1: Project setup with XcodeGen

- [x] Install XcodeGen: `brew install xcodegen`
- [x] Create `NomNom-iOS/project.yml`:
  - Bundle ID: `com.nomnom-ai.app`
  - Deployment target: iOS 17.0
  - Swift version: 5.9
  - Sources: `NomNom/`
- [x] Run `xcodegen generate` to create .xcodeproj
- [x] Open in Xcode, verify it builds (Cmd+B)

### S3.2: Core services

- [x] Create `NomNom-iOS/NomNom/Core/Services/APIClient.swift`:
  - Singleton HTTP client
  - `#if targetEnvironment(simulator)` → localhost:8000
  - `#else` → ngrok URL (device)
  - Methods: `request<T>(_ method, path, body) async throws → T`
  - Methods: `upload<T>(path, imageData) async throws → T` (multipart form)
  - Attaches JWT token to Authorization header
- [x] Create `NomNom-iOS/NomNom/Core/Services/KeychainService.swift`:
  - `save(token: String)`
  - `load() → String?`
  - `delete()`
  - Uses system Keychain (secure token storage)
- [x] Create `NomNom-iOS/NomNom/Core/Services/AuthService.swift`:
  - ObservableObject
  - @Published var isAuthenticated
  - `login(email, password) async` → POST /auth/login → save token
  - `logout()` → delete token
  - `checkAuth()` → try loading saved token on app launch

### S3.3: Models + login UI

- [x] Create `NomNom-iOS/NomNom/Core/Models/Auth.swift`:
  - LoginRequest (email, password)
  - RegisterRequest (email, password)
  - TokenResponse (access_token, token_type)
- [x] Create `NomNom-iOS/NomNom/Features/Settings/LoginView.swift`:
  - Email text field
  - Password text field
  - Login button
  - Error message display
- [x] Create `NomNom-iOS/NomNom/App/NomNomApp.swift`:
  - @main entry point
  - @StateObject AuthService
  - Auth gate: show LoginView if !isAuthenticated, else ContentView
- [x] Create `NomNom-iOS/NomNom/App/ContentView.swift`:
  - TabView with 2 tabs: Camera, Today's Log
  - Placeholder views for now

### S3.4: Verify on simulator

- [x] Run on iOS Simulator (Cmd+R)
- [x] Start backend locally: `uv run python -m src.run`
- [x] Test register → login → see tab view
- [x] Kill app, relaunch → verify token is saved and login persists

**Tests:**
- [x] Login with correct credentials succeeds
- [x] Login with wrong credentials shows error
- [x] Token is saved to Keychain
- [x] App remembers login after restart

**Deliverable:** Xcode project builds. Login works. Auth gate works. Token saved.

---

## Phase S4: iOS — Camera + Today's Log ✅

**Goal:** Implement food logging flow.

### S4.1: Food log models + colors

- [x] Create `NomNom-iOS/NomNom/Core/Models/FoodLog.swift`:
  - FoodLog (id, userId, photoPath, foodName, calories, proteinG, carbsG, fatG, foodCategory, cuisineOrigin, catRoast, loggedAt, createdAt)
  - FoodAnalysisResponse (same fields)
- [x] Create `NomNom-iOS/NomNom/Core/Utilities/NomNomColors.swift`:
  - Color palette (background, primary, surface, text, danger, warning, success)

### S4.2: Camera screen

- [x] Create `NomNom-iOS/NomNom/Core/Services/PhotoCaptureService.swift`:
  - Wraps UIImagePickerController
  - Real device: use .camera
  - Simulator: use .photoLibrary (no camera)
  - Returns selected image as Data
- [x] Create `NomNom-iOS/NomNom/Features/Camera/CameraViewModel.swift`:
  - @Published var capturedImageData, analysisResult, isAnalyzing, errorMessage
  - `capturePhoto()` → open camera/photo library
  - `analyzePhoto()` → upload to POST /analyze, get analysis
  - `saveLog()` → POST to /food-logs to save
  - `reset()` → clear state for retake
- [x] Create `NomNom-iOS/NomNom/Features/Camera/CameraView.swift`:
  - Prompt: big camera button "Take Photo"
  - After capture: show photo + analysis + roast + confirm/retake buttons
  - Loading state: spinner + "Cat is judging your food..."
  - Error state: show error message

### S4.3: Reusable components

- [x] Create `NomNom-iOS/NomNom/Core/Components/FoodLogCard.swift`:
  - Show: thumbnail, food name, calories, time
  - Tappable for details (future)
- [x] Create `NomNom-iOS/NomNom/Core/Components/RoastBubble.swift`:
  - Speech bubble with cat roast text
  - Styled nicely with background, padding, corner radius

### S4.4: Today's log screen

- [x] Create `NomNom-iOS/NomNom/Features/Dashboard/TodayViewModel.swift`:
  - @Published var logs
  - `loadTodayLogs()` → GET /food-logs/today
  - `deleteLog(id)` → DELETE /food-logs/{id}
- [x] Create `NomNom-iOS/NomNom/Features/Dashboard/TodayView.swift`:
  - Scrollable list of FoodLogCard
  - Pull-to-refresh
  - Swipe-to-delete
  - Empty state: "No meals logged yet"

### S4.5: Verify on simulator

- [x] Run on simulator
- [x] Flow: login → camera → pick photo → see roast + macros → confirm → see in today's list
- [x] Delete works (swipe)
- [x] Refresh works (pull-to-refresh)

**Tests:**
- [x] Camera view shows prompt when no photo
- [x] Camera view shows analysis after photo capture
- [x] Today view loads and displays logs
- [x] Delete removes log from list
- [x] Refresh reloads logs

**Deliverable:** Full MVP loop works on simulator. Camera → analyze → save → list.

---

## Phase S5: Deploy to Real iPhone ✅

**Goal:** Get the app running on your actual iPhone.

### S5.1: ngrok prerequisites

- [x] Install ngrok: `brew install ngrok`
- [x] Sign up at https://ngrok.com (free account)
- [x] Run `ngrok config add-authtoken YOUR_TOKEN`
- [x] Verify: `ngrok config check`

### S5.2: iPhone developer setup

- [x] Connect iPhone to Mac via USB
- [x] Open Xcode (prompts iPhone for Developer Mode)
- [x] On iPhone: Settings → Privacy & Security → Developer Mode → ON
- [x] iPhone restarts
- [x] Tap "Trust This Computer" on iPhone

### S5.3: Xcode signing

- [x] In Xcode: Settings → Accounts → Add Apple ID
- [x] Select NomNom target → Signing & Capabilities
- [x] Check "Automatically manage signing"
- [x] Set Team to your Apple ID
- [x] Verify Bundle ID is `com.nomnom-ai.app`

### S5.4: Deploy and test

- [x] Terminal 1: Start backend
  ```bash
  cd NomNom-Backend
  PYTHONPATH=. uv run python -m src.run
  ```
- [x] Terminal 2: Start ngrok
  ```bash
  ngrok http 8000
  ```
  Copy the https URL (e.g., https://loris-spleenish-nonopera...ngrok-free.dev)
- [x] Update `APIClient.swift` line 38 with your ngrok URL
- [x] In Xcode: Select your iPhone as build target (top bar)
- [x] Press Cmd+R to build and install
- [x] On iPhone: Settings → General → VPN & Device Management → tap your cert → Trust
- [x] Launch app on iPhone
- [x] Login, take photo, see roast! 🎉

**Tests:**
- [x] App installs on iPhone
- [x] Login works with real backend
- [x] Camera access granted
- [x] Photo upload works (sees analysis)
- [x] Analysis saves to backend
- [x] Today's log shows on phone

**Deliverable:** Working app on your real iPhone. Take photo, see cat roast, see it logged.

---

## Success Criteria

- [x] Backend API running, health check responds
- [x] Food log CRUD endpoints all working
- [x] Photo upload, storage, and serving working
- [x] Haiku vision API integration working
- [x] iOS Xcode project builds without errors
- [x] iOS app runs on simulator
- [x] iOS app runs on real iPhone
- [x] Full end-to-end flow works: login → camera → analyze → save → view
- [x] All tests pass (24+ tests)
- [x] App deployed to real device via ngrok

## Gaps to Fill Later

| Gap | Iteration | Why it matters |
|---|---|---|
| LLM harness (retry, fallback, timeout) | 02 | LLM Harness Engineering |
| Structured output (tool_use) | 02 | Structured Output |
| Prompt templates (Jinja2) | 02 | Prompt Engineering |
| Guardrails + validation | 03 | Guardrails |
| Semantic caching | 03 | Cost Optimization |
| AI call logging | 03 | AI Observability |
| Rate limiting | 03 | Guardrails |
| Accuracy tracking | 03 | Model Evaluation |
| Embeddings + vector search | 04 | Embeddings & Vector Search |
| RAG recommendations | 04 | RAG |
| Streaming SSE | 04 | Streaming |
| Dashboard + cat mood | 05 | — |
| Weekly recaps | 05 | — |
| Timeline screen | 06 | — |
| Onboarding flow | 06 | — |
| Settings screen | 06 | — |
