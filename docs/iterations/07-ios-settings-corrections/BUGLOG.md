# BUGLOG — Iteration 07: iOS Settings, Corrections & Recommendations

Tracker for issues, blockers, decisions, and testing notes during this iteration.

## Critical Issues (Resolved)

### Issue: foodName → food_name Mismatch
- **Date Found**: 2026-04-06
- **Severity**: High (broke food save)
- **Root Cause**: Backend was accessing `data.foodName` (camelCase) but Pydantic expected `data.food_name` (snake_case)
- **Location**: `src/api/food_logs.py:52` in cache_analysis() call
- **Resolution**: Changed `data.foodName` to `data.food_name`
- **Test**: Food photo → save → appears in Today tab ✅

### Issue: Auth Header Lost on 307 Redirect
- **Date Found**: 2026-04-06
- **Severity**: High (blocked profile loading)
- **Root Cause**: Backend had `@router.get("/")` but iOS called `/api/v1/profile` (no slash). FastAPI redirected to `/` (with slash), losing Authorization header on redirect.
- **Location**: `src/api/profile.py:53-56`
- **Resolution**: Added `@router.get("")` (empty route) in addition to existing `@router.get("/")` to accept both paths
- **Test**: Settings tab → profile loads ✅

### Issue: Food Correction Endpoint Expected Full FoodLogCreate
- **Date Found**: 2026-04-06
- **Severity**: High (correction button broken)
- **Root Cause**: PATCH endpoint used `FoodLogCreate` schema requiring all fields (calories, macros, etc.). iOS only sent corrected food name.
- **Location**: `src/api/food_logs.py:72`
- **Resolution**: Created new `FoodLogUpdate` schema accepting only `food_name`. Updated endpoint to use it.
- **Test**: Photo → Save → "This is wrong" → correct food name → PATCH succeeds ✅

### Issue: iOS Project Missing New Swift Files in Build Target
- **Date Found**: 2026-04-06
- **Severity**: High (Xcode build failed)
- **Root Cause**: Manually adding files to Xcode via File menu created duplicates (ProfileService 2.swift, etc.) and didn't register files in build target
- **Location**: Xcode build target Sources phase + project.pbxproj
- **Resolution**: 
  1. Deleted duplicate numbered Swift files from disk
  2. Manually edited project.pbxproj to add ProfileService, RecommendationService, SettingsView, SettingsViewModel, UserProfile to build files
  3. Re-added UserProfile.swift to Models group
- **Test**: `xcodebuild build` succeeds with no errors ✅

### Issue: SettingsViewModel Requires AuthService But No Access To Shared Instance
- **Date Found**: 2026-04-06
- **Severity**: Medium (architectural)
- **Root Cause**: AuthService is created in NomNomApp as @StateObject, not exposed as singleton. SettingsViewModel tried to use `AuthService.shared` (doesn't exist).
- **Location**: `Features/Settings/SettingsViewModel.swift:11`
- **Resolution**: Modified SettingsViewModel to accept `authService` as init parameter. SettingsView creates ViewModel with local AuthService instance (workaround for now).
- **Note**: Better solution would be environment object, but current approach works for MVP
- **Test**: Settings tab loads without crashes ✅

### Issue: ngrok Port 8000 Already in Use
- **Date Found**: 2026-04-06
- **Severity**: Medium (infrastructure)
- **Root Cause**: Previous uvicorn process (PID 23376) was still running from earlier session
- **Resolution**: Killed old process (`kill -9 23376`), restarted fresh backend
- **Test**: Backend running on port 8000, ngrok tunnel active ✅

### Issue: pgvector Extension Missing
- **Date Found**: 2026-04-06
- **Severity**: High (migration failed)
- **Root Cause**: PostgreSQL on Mac didn't have pgvector installed
- **Resolution**: `brew install pgvector`
- **Test**: Migration `alembic upgrade head` succeeds ✅

### Issue: UndefinedColumnError for food_logs.embedding
- **Date Found**: 2026-04-06
- **Severity**: High (queries failed)
- **Root Cause**: Migration created column, but backend wasn't restarted so old code was still running
- **Resolution**: Restarted backend (`python -m uvicorn src.app:app`)
- **Test**: GET /api/v1/food-logs/today returns 200 OK ✅

### Issue: Photo Thumbnails Not Loading in Today Tab
- **Date Found**: 2026-04-06
- **Severity**: High (broken user experience)
- **Root Cause**: `APIClient.shared.get()` method designed for JSON responses (uses JSONDecoder). FoodLogCard was attempting to fetch binary photo data using this JSON-expecting method, causing silent failure.
- **Location**: `FoodLogCard.swift` and `APIClient.swift`
- **Resolution**: 
  1. Added new `getData()` method to APIClient.swift that fetches raw binary data without JSON decoding
  2. Updated FoodLogCard.swift to use `APIClient.shared.getData()` instead of `get()`
- **Test**: Photo → save → navigate to Today tab → thumbnail displays actual food photo ✅

### Issue: Settings Tab Returns 404 (Profile Not Found)
- **Date Found**: 2026-04-06
- **Severity**: High (blocked user onboarding)
- **Root Cause**: User profile was not auto-created on registration. GET /api/v1/profile returned 404 because UserProfile didn't exist for new users.
- **Location**: `src/services/auth_service.py` register_user()
- **Resolution**: Modified register_user() to auto-create default UserProfile with sensible defaults (age:25, gender:other, height:170cm, weight:70kg, activity:moderate, cat_style:sassy)
- **Test**: Register new account → Settings tab loads profile ✅

### Issue: Meal Recommendation Returns 404 (Profile Not Found)
- **Date Found**: 2026-04-06
- **Severity**: High (feature broken on first login)
- **Root Cause**: Same as above — recommendations endpoint calls get_effective_targets(profile) which fails if profile doesn't exist
- **Location**: `src/api/recommendations.py:49` and `src/services/auth_service.py`
- **Resolution**: Fixed by auto-creating default profile on registration (same fix as Issue #9)
- **Test**: Register new account → Today tab → "What to eat?" button → AI recommendation displays with meal suggestions ✅

### Issue: Food Correction Button Needs Polish
- **Date Found**: 2026-04-06
- **Severity**: Medium (UX)
- **Status**: Functionally working but UX could be improved
- **Notes**: "This is wrong" button works correctly but UI flow could be more polished
- **Next Steps**: Polish the correction modal/flow in a future iteration

## Blockers (Current)

None at this time.

## Decisions Made

### Decision: Use ngrok for iPhone Device Testing
- **Context**: Need to test on physical iPhone, not just simulator
- **Options Considered**: 
  1. ngrok (public tunnel) ✓ **Chosen**
  2. Local IP + WiFi (only works on same network)
  3. Deploy to staging server (overhead)
- **Rationale**: ngrok is free, requires no infrastructure, works from anywhere
- **URL**: https://loris-spleenish-nonoperatically.ngrok-free.dev
- **Impact**: iOS app uses ngrok URL for device, localhost:8000 for simulator

### Decision: Fix SettingsViewModel Auth via Init Parameter
- **Context**: SettingsViewModel needs to call logout() on AuthService
- **Options Considered**:
  1. Environment object (EnvironmentObject var) — requires passing through SettingsView init ✓ **Partial use**
  2. Singleton (AuthService.shared) — not available in current design
  3. Dependency injection via init ✓ **Chosen**
- **Current**: SettingsViewModel accepts authService in init; SettingsView creates dummy AuthService (workaround)
- **Improvement Needed**: Should pass actual authService from NomNomApp via environment object
- **Status**: Works for MVP, refactor in later iteration

### Decision: Split FoodLogCreate and FoodLogUpdate Schemas
- **Context**: Different endpoints need different payloads (save vs correct)
- **Options Considered**:
  1. Single schema with optional fields (unclear intent, error-prone)
  2. Separate schemas ✓ **Chosen**
- **Rationale**: Explicit, validates only required fields, prevents accidental overwrites
- **Implementation**: 
  - `FoodLogCreate` — full analysis (for POST /food-logs)
  - `FoodLogUpdate` — only food_name (for PATCH /food-logs/{id})

### Decision: Store photo_path in food_logs (Not Binary Blob)
- **Context**: Photos need to be served and displayed in iOS
- **Options Considered**:
  1. Store photo binary in DB (blob field) — slower queries, bloats DB
  2. Store path on disk, reference in DB ✓ **Chosen**
- **Rationale**: Photos are large, accessed separately, can be served as static files
- **Storage**: uploads/ directory on server
- **Cleanup**: TODO — no TTL policy (planned for later)

## Testing Notes

### Manual Testing (iPhone Device)
- [x] Login flow (email + password)
- [x] Photo capture → analysis (AI roasts correctly)
- [x] Food save (POST /food-logs succeeds)
- [x] Today tab (shows logged food with macros)
- [x] Food correction ("This is wrong" → correct name → PATCH succeeds)
- [x] Settings load (profile shows, no errors)
- [x] Cat style picker (loads options)
- [x] Error display (404 → shown in banner, not silent)
- [ ] Logout (not tested yet)
- [ ] Meal recommendations (button exists, backend untested on device)

### Automated Tests
- [x] LLM Harness: 159 tests passing
- [x] Semantic Cache: Embedding generation, pgvector queries
- [x] Food Log Service: CRUD operations
- [ ] Auth: JWT validation
- [ ] Profile: CRUD operations
- [ ] iOS Integration: No automated tests (would require simulators + mocking)

## Known Limitations

| Limitation | Impact | Workaround | Priority |
|------------|--------|-----------|----------|
| User profile doesn't auto-create | Settings tab shows 404 on first login | Manually create profile via API | High |
| No profile creation endpoint | User can't create initial profile | API only supports update | High |
| iOS SettingsViewModel gets dummy AuthService | Logout may not work correctly | Refactor to use environment object | Medium |
| Photos accumulate forever | Disk space grows unbounded | No TTL cleanup policy | Low |
| No API rate limiting | Vulnerable to abuse | Can add token bucket later | Medium |
| Recommendation service untested on device | May have network issues | Test "What to eat?" button on iPhone | Medium |

## Next Steps

1. **Test meal recommendations** on iPhone: Tap "What to eat?" button, verify suggestion displays
2. **Create onboarding flow** or auto-create profile on first login
3. **Refactor SettingsViewModel** to use environment object for authService
4. **Test logout** button on Settings tab
5. **Add photo cleanup** policy (delete photos older than 30 days)
6. **Expand nutrition KB** with more seeded entries
7. **Add rate limiting** to API (token bucket per user)

---

**Last Updated**: 2026-04-06 18:30 UTC  
**Status**: In Progress 🚧 (Major blockers resolved, ready for further testing)
