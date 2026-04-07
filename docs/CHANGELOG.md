# CHANGELOG — NomNom

Chronological development history. For detailed iteration notes, see `docs/iterations/`.

## Iteration 07: iOS Settings, Corrections & Recommendations (2026-04-06)

### Features Completed
- **Settings Tab**: Cat personality picker, macro goal inputs, logout button
- **Food Correction UX**: Fixed unreachable "This is wrong" button; now inline success state with persistent buttons
- **Meal Recommendations**: RAG-powered "What to eat?" endpoint with semantic search of nutrition KB
- **Error Display**: Network errors now shown in Today and Settings tabs instead of silently swallowed

### Bugs Fixed
- Fixed `AttributeError: 'FoodLogCreate' object has no attribute 'foodName'` in food log cache
- Fixed 307 redirect on profile endpoint losing Authorization header (added GET route without trailing slash)
- Fixed duplicate Swift files in iOS project; properly configured Xcode build target
- Fixed 422 validation errors on food correction endpoint (created `FoodLogUpdate` schema with only food_name)

### Testing
- iOS app tested on physical iPhone device (hyy iPhone)
- Backend tested with ngrok tunnel for remote device access
- Food photo → save → correct → today list flow verified end-to-end

### Database
- Migration `f2c3a8d9e1f4_add_pgvector_embeddings_and_nutrition_kb` applied
- Added `embedding` column to `food_logs` (pgvector 384-dim)
- Added `nutrition_kb` table with 40+ seeded nutrition tips

### Infrastructure
- Installed pgvector extension (HomeBrew)
- Set up ngrok for iPhone device testing
- Configured iOS app to use ngrok URL for device deployment

---

## Iteration 06: Embeddings & Semantic Cache (2026-04-05)

### Features Completed
- **Semantic Embeddings**: Text-to-vector using sentence-transformers (all-MiniLM-L6-v2, 384-dim)
- **Semantic Cache**: Cache food analyses by embedding similarity (pgvector cosine distance < 0.15)
- **RAG Knowledge Base**: Seeded 40+ nutrition facts for meal recommendations
- **Knowledge Service**: Retrieve KB entries via vector similarity search

### Database
- Created `nutrition_kb` table with embedding vectors
- Added `embedding` column to `food_logs` for caching
- pgvector enabled on PostgreSQL

---

## Iteration 05: LLM Harness Complete (2026-04-04)

### Features Completed
- **Retry Logic**: Exponential backoff (2^attempt seconds) with 3 retries
- **Timeout Protection**: 30-second hard timeout per request
- **Fallback Models**: Haiku → text-davinci if Claude unavailable
- **Structured Output**: Tool-use for JSON-validated food analysis
- **Guardrails**: Semantic validation (calories reasonable, macros > 0, etc.)
- **Logging**: Every call logged with tokens, latency, errors
- **Rate Limiting**: Token bucket implementation
- **Parser**: Robust extraction of food name, macros, roast from tool_use response

### Testing
- 159 tests passing (harness, parsing, guardrails, rate limiter)
- All critical paths covered (retry, timeout, fallback, error handling)

---

## Iteration 04: Food Analysis MVP (2026-04-02)

### Features Completed
- **Photo Upload**: Multipart/form-data to backend
- **LLM Analysis**: Claude analyzes food → returns JSON (name, calories, macros, roast)
- **Photo Storage**: Compress and save to disk; serve via static endpoint
- **Food Thumbnails**: Display in Today view and Timeline (planned)

### Database
- Created `food_logs` table
- Implemented photo storage on disk (uploads/)

---

## Iteration 03: Auth & iOS Login (2026-03-31)

### Features Completed
- **User Registration**: Email + password → hashed storage
- **JWT Login**: Access token generation + refresh strategy
- **Keychain Storage**: Secure token storage on iOS
- **Auto-Logout**: 401 response triggers logout + redirect to LoginView
- **Auth Middleware**: `get_current_user` dependency on protected endpoints

### Database
- Created `users` table

---

## Iteration 02: iOS App Structure (2026-03-28)

### Features Completed
- **SwiftUI MVVM Architecture**: Camera, Today, Settings tabs
- **APIClient**: REST wrapper with multipart upload, auth headers
- **Camera Tab**: Photo picker + analysis result display
- **Today Tab**: Food log list with macros summary
- **Settings Tab**: User profile (placeholder)
- **Color System**: NomNomColors palette (primary, success, warning, danger)

---

## Iteration 01: Backend Scaffolding (2026-03-25)

### Features Completed
- **FastAPI Server**: Core API structure
- **Database Setup**: PostgreSQL + SQLAlchemy async ORM
- **Alembic Migrations**: Version control for schema
- **Auth Scaffolding**: JWT + password hashing
- **Error Handling**: Structured responses (APIError types)
- **CORS**: Configured for iOS app

---

## Pre-MVP Work (2026-03-20 — 2026-03-24)

- Initial project setup (iOS + Backend)
- Architecture planning
- Git repo initialization
- Dependency management (pyproject.toml, SPM for iOS)
