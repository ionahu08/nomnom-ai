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

### S1: Backend — food log endpoints + photo upload

Add the ability to save, list, and delete food logs with photos.

Files to create:
- `src/models/food_log.py` — FoodLog model (id, user_id, photo_path, food_name, calories, protein_g, carbs_g, fat_g, food_category, cuisine_origin, cat_roast, logged_at, created_at)
- Update `src/models/__init__.py` — add FoodLog
- `src/schemas/food_log.py` — FoodLogCreate, FoodLogResponse
- `src/services/food_log_service.py` — create, list_today, delete
- `src/services/photo_service.py` — save uploaded photo to disk, return path
- `src/api/food_logs.py` — router with endpoints:
  - POST /api/v1/food-logs/analyze — upload photo, get AI analysis (stub first, real AI in S2)
  - POST /api/v1/food-logs — save a confirmed food log
  - GET /api/v1/food-logs/today — list today's logs
  - DELETE /api/v1/food-logs/{log_id} — delete a log
- `src/api/photos.py` — GET /api/v1/photos/{filename} — serve a food photo
- Update `src/app.py` — register food_logs and photos routers
- Alembic migration for food_logs table
- Tests: food log CRUD

### S2: Backend — AI analyze endpoint (Haiku)

Wire up Anthropic Haiku to analyze food photos and generate roasts.

Files to create:
- `src/services/ai_service.py` — one function:
  - analyze_food_photo(image_bytes, cat_style) → calls Haiku vision API
  - Sends base64 image + system prompt with cat personality
  - Parses response JSON: food_name, calories, protein_g, carbs_g, fat_g, food_category, cuisine_origin, cat_roast
- Update `src/api/food_logs.py` — replace analyze stub with real AI call
- Add ANTHROPIC_API_KEY to .env
- Tests: ai_service (mocked)

### S3: iOS — project setup + login screen

Create the Xcode project and login screen.

Files to create:
- `NomNom-iOS/project.yml` — XcodeGen config (bundle ID, iOS 17, Swift 5.9)
- `NomNom-iOS/NomNom/App/NomNomApp.swift` — app entry, auth gate
- `NomNom-iOS/NomNom/App/ContentView.swift` — tab view (camera + today)
- `NomNom-iOS/NomNom/Core/Services/APIClient.swift` — HTTP client with multipart upload
  - Compile-time baseURL switch: localhost (simulator) vs ngrok (device)
- `NomNom-iOS/NomNom/Core/Services/AuthService.swift` — login/logout, store token
- `NomNom-iOS/NomNom/Core/Services/KeychainService.swift` — secure token storage
- `NomNom-iOS/NomNom/Core/Models/Auth.swift` — LoginRequest, TokenResponse
- `NomNom-iOS/NomNom/Features/Settings/LoginView.swift` — email + password form

Steps:
- Run `xcodegen generate` to create .xcodeproj
- Open in Xcode, set signing to your Apple ID
- Run on simulator, verify login works

### S4: iOS — camera screen + today's log

The main app experience.

Files to create:
- `NomNom-iOS/NomNom/Core/Models/FoodLog.swift` — FoodLog, FoodAnalysisResponse
- `NomNom-iOS/NomNom/Core/Services/PhotoCaptureService.swift` — camera access
- `NomNom-iOS/NomNom/Features/Camera/CameraView.swift` — camera button, shows analysis result + roast
- `NomNom-iOS/NomNom/Features/Camera/CameraViewModel.swift` — capture, upload, display
- `NomNom-iOS/NomNom/Features/Dashboard/TodayView.swift` — list of today's food log cards
- `NomNom-iOS/NomNom/Features/Dashboard/TodayViewModel.swift` — fetch today's logs
- `NomNom-iOS/NomNom/Core/Components/FoodLogCard.swift` — thumbnail + food name + calories + roast
- `NomNom-iOS/NomNom/Core/Components/RoastBubble.swift` — cat speech bubble
- `NomNom-iOS/NomNom/Core/Utilities/NomNomColors.swift` — color palette

### S5: Deploy to phone

Get the app running on a real iPhone.

Steps:
1. Enable Developer Mode on iPhone (connect USB, then Settings → Privacy & Security → Developer Mode)
2. Add Apple ID to Xcode (Xcode → Settings → Accounts)
3. In Xcode: select NomNom target → Signing → check "Automatically manage signing" → set Team to your Apple ID
4. Install ngrok: `brew install ngrok`
5. Start backend: `cd NomNom-Backend && PYTHONPATH=. uv run python -m src.run`
6. Start ngrok: `ngrok http 8000` → copy the https URL
7. Update APIClient.swift with ngrok URL
8. Connect iPhone via USB → select as build target → Cmd+R
9. On iPhone: Settings → General → VPN & Device Management → Trust
10. Launch app, snap a photo, see the roast!

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
