# Features — NomNom

Complete inventory of NomNom features with status and implementation reference.

## Core Features

### Authentication
- **Status**: ✅ Complete
- **Features**:
  - User registration with email + password
  - JWT-based login (access token)
  - Token storage in iOS Keychain
  - Auto-logout on 401 (expired token)
  - Password hashing (bcrypt)
- **Implementation**: 
  - Backend: `src/api/auth.py`, `src/services/auth_service.py`
  - iOS: `Features/Settings/LoginView.swift`, `Core/Services/AuthService.swift`
  - Database: `users` table

### Photo Capture & Analysis
- **Status**: ✅ Complete
- **Features**:
  - Photo picker in iOS Camera tab
  - Image upload to backend (multipart/form-data)
  - LLM analysis via Claude (food name, macros, roast)
  - Structured JSON response with validation
  - Retry logic + timeout protection (30s)
  - Fallback to Haiku if analysis fails
- **Implementation**:
  - Backend: `src/api/food_logs.py`, `src/services/ai_service.py`, `src/llm/client.py`
  - iOS: `Features/Camera/CameraView.swift`, `Features/Camera/CameraViewModel.swift`
  - LLM Harness: `src/llm/harness.py`, `src/llm/guardrails.py`, `src/llm/parser.py`

### Food Log Saving
- **Status**: ✅ Complete
- **Features**:
  - Save analyzed food to database
  - Store photo path, macros, user roast, AI response
  - Mark if user has corrected the food name
  - Timestamp (logged_at = when user ate it, created_at = when we logged it)
- **Implementation**:
  - Backend: `src/api/food_logs.py`, `src/services/food_log_service.py`
  - iOS: `Features/Camera/CameraView.swift`
  - Database: `food_logs` table

### Food Correction ("This is Wrong")
- **Status**: ✅ Complete
- **Features**:
  - User taps "This is wrong" button after saving
  - Modal prompts for corrected food name
  - PATCH `/api/v1/food-logs/{id}` to update
  - Sets `is_user_corrected = true` in database
- **Implementation**:
  - Backend: `src/api/food_logs.py`, `update_food_log()` endpoint
  - iOS: `Features/Camera/CameraView.swift`, correction modal
  - Schema: `FoodLogUpdate` (accepts only food_name)

### Today's Food Logs View
- **Status**: ✅ Complete (Iteration 7), 🚧 Grouping by meal type (Iteration 8)
- **Features**:
  - List all food logs from today
  - Display thumbnail, food name, macros, cat roast
  - Show daily summary (total cals, protein, carbs, fat)
  - Pull-to-refresh
  - Swipe-to-delete individual logs
  - Error display banner
  - Group logs by meal category (Breakfast/Lunch/Dinner/Snack) — NEW
- **Implementation**:
  - Backend: `src/api/food_logs.py`, `get_today_logs()` endpoint
  - iOS: `Features/Dashboard/TodayView.swift`, `Features/Dashboard/TodayViewModel.swift`
  - Database: Query `food_logs` WHERE user_id = ? AND DATE(logged_at) = TODAY

### Meal Categorization
- **Status**: 🚧 In Progress (Iteration 8)
- **Features**:
  - Classify each food log as Breakfast, Lunch, Dinner, or Snack
  - Segmented picker in Camera tab (shown before save)
  - Group Today tab logs by meal category with section headers
  - Each category shows daily summary (total cals, macros)
  - Optional: can update meal type via food correction PATCH
- **Implementation**:
  - Backend: `src/api/food_logs.py`, `src/services/food_log_service.py`
  - iOS: `Features/Camera/CameraView.swift`, `Features/Camera/CameraViewModel.swift`, `Features/Dashboard/TodayView.swift`
  - Database: `food_logs.meal_type` (String, nullable)
  - Schema: `FoodLogCreate`, `FoodLogUpdate`, `FoodLogResponse` include `meal_type`

### Settings Tab
- **Status**: ✅ Complete
- **Features**:
  - Load user profile from `/api/v1/profile`
  - Picker for cat personality (sassy, grumpy, wholesome, concerned, neutral)
  - Input fields for macro targets (calorie, protein, carb, fat)
  - Save changes to backend
  - Logout button
- **Implementation**:
  - Backend: `src/api/profile.py`, `src/services/profile_service.py`
  - iOS: `Features/Settings/SettingsView.swift`, `Features/Settings/SettingsViewModel.swift`
  - Database: `user_profiles` table

### Semantic Caching
- **Status**: ✅ Complete
- **Features**:
  - Generate embedding for food description (sentence-transformers)
  - Query pgvector for similar cached analyses (cosine distance < 0.15)
  - Return cached LLM result if hit found (instant response, no API call)
  - Store new analyses in cache for future lookups
  - Reduces latency + Claude API costs
- **Implementation**:
  - Backend: `src/llm/embedding.py`, `src/llm/cache.py`
  - Database: `food_logs` table with pgvector column, `nutrition_kb` for RAG
  - Model: `all-MiniLM-L6-v2` (384-dim vectors)

### Meal Recommendations (RAG)
- **Status**: ✅ Complete
- **Features**:
  - Button "What to eat?" in Today view
  - Retrieves top-5 nutrition KB entries via pgvector similarity search
  - Injects KB context into Claude prompt
  - Returns personalized meal suggestion
  - Shows count of KB entries used
  - Displayed in modal sheet
- **Implementation**:
  - Backend: `src/api/recommendations.py`, `src/services/knowledge_service.py`
  - iOS: `Features/Dashboard/TodayView.swift` (button + modal)
  - Database: `nutrition_kb` table with embeddings
  - Service: `RecommendationService` (iOS), calls GET `/api/v1/recommendations/meal`

## Planned Features

### User Onboarding Flow
- **Status**: ❌ Planned (post-Iteration 7)
- **Description**: Initial profile creation after first login (age, gender, height, weight, dietary restrictions)
- **Priority**: Medium
- **Prerequisite**: Settings tab (done)

### Weekly Nutrition Report
- **Status**: ❌ Planned (post-Iteration 7)
- **Description**: Summary of weekly macros vs targets, trending charts
- **Priority**: Low

### Meal Timeline / History
- **Status**: ❌ Planned (post-Iteration 7)
- **Description**: Chronological view of all logged meals, searchable, filterable by date/category
- **Priority**: Medium

### Food Photo Thumbnails
- **Status**: ✅ Complete (Iteration 6)
- **Features**:
  - Store compressed photo on disk
  - Serve via static file endpoint
  - Display in Today view and Timeline
- **Implementation**:
  - Backend: `src/api/photos.py`, photo storage in `uploads/`
  - iOS: `FoodLogCard.swift` displays thumbnail

### Cat Personality Variations
- **Status**: ✅ Complete (system prompt parametrized by cat_style)
- **Features**:
  - System prompt adapts roast tone based on `cat_style` (sassy, grumpy, wholesome, etc.)
  - User can change style in Settings tab
  - New analyses respect chosen style
- **Implementation**:
  - Backend: `src/services/ai_service.py` reads profile.cat_style
  - iOS: Settings tab cat style picker

## Known Limitations & Gaps

| Gap | Impact | Workaround | Priority |
|-----|--------|-----------|----------|
| No user onboarding | New users land on empty Settings tab with 404 profile | Create profile via API call | High |
| No profile creation endpoint | Users can't create initial profile | PUT endpoint accepts missing profile | High |
| No photo storage cleanup | Photos accumulate indefinitely | Manual cleanup or TTL policy | Low |
| No rate limiting | API vulnerable to abuse | Add token bucket limiter | Medium |
| No error retry (iOS) | Failed API calls don't retry | Implement exponential backoff in APIClient | Medium |
| Limited KB entries | Only ~40 nutrition tips seeded | Expand nutrition_kb over time | Low |

## Architecture Reference by Feature

| Feature | API Endpoint | Database Table | Service | iOS View |
|---------|--------------|-----------------|---------|----------|
| Auth | POST /auth/login | users | AuthService | LoginView |
| Analysis | POST /food-logs/analyze | food_logs (embedding) | AIService | CameraView |
| Save Log | POST /food-logs | food_logs | FoodLogService | CameraView |
| Correct | PATCH /food-logs/{id} | food_logs | FoodLogService | CameraView |
| Categorize | (in Save/Correct) | food_logs.meal_type | FoodLogService | CameraView |
| Today Logs | GET /food-logs/today | food_logs (grouped) | FoodLogService | TodayView |
| Profile | GET/PUT /profile | user_profiles | ProfileService | SettingsView |
| Recommend | GET /recommendations/meal | nutrition_kb (RAG) | KnowledgeService | TodayView |
| Photos | GET /photos/{id} | uploads/ (disk) | (static files) | FoodLogCard |

## Test Coverage

| Module | Status | Notes |
|--------|--------|-------|
| LLM Harness | ✅ 159 tests passing | Retry, timeout, fallback, parsing, guardrails |
| Semantic Cache | ✅ Tested | Embedding generation, pgvector queries |
| Food Log Service | ✅ Tested | CRUD operations, embedding storage |
| Auth | ✅ Tested | JWT validation, 401 handling |
| iOS Models | ✅ Codable | Auto-tested via compile |
| Integration (iOS ↔ Backend) | 🚧 Manual | Food photo → save → list flow verified on device |

---

**Last Updated**: 2026-04-08  
**Current Iteration**: 08 (Meal Categorization)
