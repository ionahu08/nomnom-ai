# NomNom — Shortcut Plan (MVP)

Goal: Snap a food photo → AI roasts it → see today's meals on your phone.

Built on top of Phase 1 (auth, profile, database) which is already done.

---

## What's in vs what's out

| In (shortcut) | Out (add later from full plan) |
|---|---|
| Food log save/list/delete | Food log edit, pagination, corrections |
| AI photo analysis (Haiku, basic) | LLM harness (retry, fallback, cache, guardrails, logging) |
| Simple JSON response | Streaming SSE |
| Hardcoded cat prompt | Jinja2 templates, tool_use structured output |
| 3 iOS screens (login, camera, today) | Dashboard, timeline, weekly recap, onboarding, settings |
| Free Xcode signing + ngrok | — |

---

## Shortcut Phases

### S1: Backend — food log endpoints + photo upload [DONE]

Add the ability to save, list, and delete food logs with photos.

#### S1.1: FoodLog model + migration
- Create `src/models/food_log.py` — FoodLog model (id, user_id, photo_path, food_name, calories, protein_g, carbs_g, fat_g, food_category, cuisine_origin, cat_roast, logged_at, created_at)
- Update `src/models/__init__.py` — add FoodLog
- Run `alembic revision --autogenerate -m "create food_logs table"`
- Run `alembic upgrade head`
- Verify: `psql -d nomnom -c "\dt"` shows food_logs table

#### S1.2: Food log schemas
- Create `src/schemas/food_log.py`:
  - FoodAnalysisResponse — what AI returns (food_name, calories, macros, cat_roast)
  - FoodLogCreate — what client sends to save a confirmed log
  - FoodLogResponse — what the API returns

#### S1.3: Photo + food log services
- Create `src/services/photo_service.py` — save_photo (writes to uploads/), get_photo_path, delete_photo
- Create `src/services/food_log_service.py` — create_food_log, list_today_logs, get_food_log, delete_food_log

#### S1.4: API endpoints + wire up
- Create `src/api/food_logs.py` — router with endpoints:
  - POST /api/v1/food-logs/analyze — upload photo, get AI analysis (stub first, real AI in S2)
  - POST /api/v1/food-logs — save a confirmed food log
  - GET /api/v1/food-logs/today — list today's logs
  - DELETE /api/v1/food-logs/{log_id} — delete a log
- Create `src/api/photos.py` — GET /api/v1/photos/{filename} — serve a food photo
- Update `src/app.py` — register food_logs and photos routers

#### S1.5: Tests + verify
- Create `tests/integration/test_food_logs.py` — test analyze, save, list, delete, auth required
- Run `uv run pytest tests/ -v` — all 24 tests pass

---

### S2: Backend — AI analyze endpoint (Haiku)

Wire up Anthropic Haiku to analyze food photos and generate roasts.

#### S2.1: AI service with Haiku vision
- Create `src/services/ai_service.py` — one function:
  - analyze_food_photo(image_bytes, cat_style) → calls Haiku vision API
  - Creates Anthropic AsyncAnthropic client
  - Sends base64 image + system prompt with cat personality
  - System prompt tells Haiku to return JSON: food_name, calories, protein_g, carbs_g, fat_g, food_category, cuisine_origin, cat_roast
  - Parses JSON from response, returns FoodAnalysisResponse

#### S2.2: Wire analyze endpoint to real AI
- Update `src/api/food_logs.py`:
  - Import ai_service
  - Replace stub in POST /analyze with real call to analyze_food_photo()
  - Pass image_bytes and user's cat_style (from profile, default "sassy")
- Add ANTHROPIC_API_KEY to `.env`

#### S2.3: Test + verify with real photo
- Start server: `PYTHONPATH=. uv run python -m src.run`
- Test with curl: upload a real food photo to POST /analyze
- Verify AI returns food name, macros, and a funny roast
- Create `tests/unit/test_ai_service.py` — mocked test (doesn't call real API)

---

### S3: iOS — project setup + login screen

Create the Xcode project and login screen.

#### S3.1: Project setup + XcodeGen config
- Install XcodeGen: `brew install xcodegen`
- Create `NomNom-iOS/project.yml` — XcodeGen config:
  - Bundle ID: com.nomnom-ai.app
  - Deployment target: iOS 17.0
  - Swift version: 5.9
  - Sources: NomNom/
- Run `xcodegen generate` to create .xcodeproj
- Open in Xcode, verify it builds

#### S3.2: Core services (APIClient, Auth, Keychain)
- Create `NomNom-iOS/NomNom/Core/Services/APIClient.swift`:
  - Singleton HTTP client
  - Compile-time baseURL switch: localhost (simulator) vs ngrok (device)
  - Methods: request() for JSON, upload() for multipart photo
  - Attaches JWT token to Authorization header
- Create `NomNom-iOS/NomNom/Core/Services/KeychainService.swift`:
  - Save/load/delete JWT token securely
- Create `NomNom-iOS/NomNom/Core/Services/AuthService.swift`:
  - ObservableObject with @Published isAuthenticated
  - login(email, password) → calls /auth/login → saves token
  - logout() → deletes token
  - checkAuth() → tries loading saved token

#### S3.3: Models + login screen
- Create `NomNom-iOS/NomNom/Core/Models/Auth.swift`:
  - LoginRequest, RegisterRequest, TokenResponse (Codable structs)
- Create `NomNom-iOS/NomNom/Features/Settings/LoginView.swift`:
  - Email + password text fields
  - Login button
  - Error message display
- Create `NomNom-iOS/NomNom/App/NomNomApp.swift`:
  - @main entry point
  - Auth gate: show LoginView if not logged in, ContentView if logged in
- Create `NomNom-iOS/NomNom/App/ContentView.swift`:
  - TabView with 2 tabs: Camera, Today's Log
  - Placeholder views for now

#### S3.4: Verify on simulator
- Run on iOS Simulator in Xcode (Cmd+R)
- Start backend locally
- Test: register → login → see the tab view
- Verify token is saved (app remembers login after restart)

---

### S4: iOS — camera screen + today's log

The main app experience.

#### S4.1: Food log models + utilities
- Create `NomNom-iOS/NomNom/Core/Models/FoodLog.swift`:
  - FoodLog, FoodAnalysisResponse (Codable structs matching backend schemas)
- Create `NomNom-iOS/NomNom/Core/Utilities/NomNomColors.swift`:
  - Color palette for the app

#### S4.2: Camera screen
- Create `NomNom-iOS/NomNom/Core/Services/PhotoCaptureService.swift`:
  - Wraps UIImagePickerController for camera access
  - Falls back to photo library on simulator (simulator has no camera)
- Create `NomNom-iOS/NomNom/Features/Camera/CameraViewModel.swift`:
  - capturePhoto() → opens camera
  - analyzePhoto(imageData) → uploads to POST /analyze → gets AI response
  - saveLog() → sends confirmed data to POST /food-logs
  - @Published states: isAnalyzing, analysisResult, error
- Create `NomNom-iOS/NomNom/Features/Camera/CameraView.swift`:
  - Big camera button in center
  - After photo taken: shows food photo + AI analysis + cat roast
  - Confirm button to save, retake button to try again

#### S4.3: Reusable components
- Create `NomNom-iOS/NomNom/Core/Components/FoodLogCard.swift`:
  - Shows: thumbnail photo, food name, calories, time
- Create `NomNom-iOS/NomNom/Core/Components/RoastBubble.swift`:
  - Cat speech bubble showing the roast text

#### S4.4: Today's log screen
- Create `NomNom-iOS/NomNom/Features/Dashboard/TodayViewModel.swift`:
  - loadTodayLogs() → calls GET /food-logs/today
  - deleteLog(id) → calls DELETE /food-logs/{id}
  - @Published logs list
- Create `NomNom-iOS/NomNom/Features/Dashboard/TodayView.swift`:
  - Scrollable list of FoodLogCard components
  - Pull to refresh
  - Swipe to delete

#### S4.5: Verify on simulator
- Run on simulator
- Test full flow: login → tap camera → pick photo → see roast → save → see in today's list
- Verify delete works

---

### S5: Deploy to phone

Get the app running on a real iPhone.

#### S5.1: Prerequisites
- Install ngrok: `brew install ngrok`
- Sign up for free ngrok account at https://ngrok.com
- Run `ngrok config add-authtoken YOUR_TOKEN`

#### S5.2: iPhone setup
- Connect iPhone to Mac via USB cable
- Open Xcode (triggers Developer Mode option on iPhone)
- On iPhone: Settings → Privacy & Security → Developer Mode → ON
- iPhone will restart
- On iPhone: tap "Trust This Computer" when prompted

#### S5.3: Xcode signing
- Add Apple ID to Xcode: Xcode → Settings → Accounts → "+" → Apple ID
- Select NomNom target → Signing & Capabilities
- Check "Automatically manage signing"
- Set Team to your Apple ID
- Set Bundle Identifier to `com.nomnom-ai.app`

#### S5.4: Run it
- Start backend: `cd NomNom-Backend && PYTHONPATH=. uv run python -m src.run`
- Start ngrok: `ngrok http 8000` → copy the https URL
- Update APIClient.swift with your ngrok URL (the #else branch)
- In Xcode: select your iPhone as build target (not simulator)
- Press Cmd+R to build and install
- On iPhone: Settings → General → VPN & Device Management → tap your developer cert → Trust
- Launch app, snap a photo, see the roast!

---

## What you'll have after the shortcut

A real app on your phone where you:
1. Open app → log in
2. Tap camera → snap food photo
3. See the cat's roast + calorie/macro estimate
4. Scroll today's meals with thumbnails

---

## Gaps to fill later (from full PLAN.md)

| Gap | Full plan phase | Why it matters for resume |
|---|---|---|
| LLM harness (retry, fallback, timeout) | Phase 3 | LLM Harness Engineering |
| Structured output (tool_use) | Phase 3 | Structured Output |
| Prompt templates (Jinja2) | Phase 3 | Prompt Engineering |
| Guardrails + output validation | Phase 5 | Guardrails |
| Semantic caching | Phase 5 | Cost Optimization |
| AI call logging | Phase 5 | AI Observability |
| Rate limiting | Phase 5 | Guardrails |
| Accuracy tracking from corrections | Phase 5 | Model Evaluation |
| Embeddings + pgvector | Phase 6 | Embeddings & Vector Search |
| RAG recommendations | Phase 7 | RAG |
| Streaming SSE | Phase 7 | Streaming |
| Dashboard + progress bars + cat mood | Phase 8 + 11 | — |
| Weekly recaps + scheduler | Phase 8 | — |
| Timeline screen | Phase 12 | — |
| Onboarding flow | Phase 12 | — |
| Settings screen | Phase 12 | — |
