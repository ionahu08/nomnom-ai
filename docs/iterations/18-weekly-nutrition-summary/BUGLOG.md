# Iteration 18: Bug Log & Decisions

**Status:** Phase 1 Complete ✅ | Settings Regression Fixed ✅

---

## Known Issues

(None currently)

---

## Blockers

(None currently)

---

## Design Decisions

### 1. Weekly Stats Aggregation (Phase 1)
**Decision:** Calculate stats in Python, not SQL  
**Why:** Simplicity and readability; data volume is small (< 300 logs/week typical)  
**Trade-off:** Slightly slower than raw SQL GROUP BY, but more maintainable

### 2. Default Nutrition Targets
**Decision:** Provide sensible defaults (2000 cal, 150g protein, 200g carbs, 65g fat)  
**Why:** App should work for users without a profile; can override via Settings  
**Implementation:** AnalyticsRepository.get_user_targets() returns defaults if no profile

### 3. Daily Breakdown as List, Not Dict
**Decision:** Return daily_breakdown as list sorted by date  
**Why:** Matches JSON conventions; easier for iOS to iterate and chart  
**Trade-off:** Slightly less flexible than dict keyed by date

### 4. Consistency Calculation
**Formula:** `(days_logged / 7) * 100`  
**Why:** Shows percentage of the week user actually tracked  
**Example:** 6 days logged = 85.7% consistency

---

## Critical Bug: Backend Import Error Causing All API Timeouts

**Symptom:** iOS app showed "Failed to load profile: The request timed out" when accessing Settings tab. All API calls to backend timed out after ~5 seconds.

**Root Cause Analysis:**
- Phase 1 (analytics.py creation) introduced an incorrect import: `from src.api.dependencies import get_current_user, get_db`
- The correct module names are: `src.api.deps` (for get_current_user) and `src.database` (for get_db)
- This import error prevented the entire FastAPI app from loading
- Backend process was running but refusing all connections (hung during startup)
- No error was visible in logs because the terminal session was backgrounded

**Impact:**
- Every iOS API request to /api/v1/profile and other endpoints timed out
- Settings tab became completely unusable
- Error message "Failed to load profile: The request timed out" was misleading (actual issue was app not loading, not a timeout)

**Debugging Process:**
1. Initial hypothesis: APIClient baseURL wrong (ngrok vs localhost) ❌ Wrong
2. Hypothesis: AuthService not properly initialized ❌ Wrong
3. Actual investigation: Tested curl against localhost:8000, request hung
4. Checked backend process - was running but not responding
5. Restarted backend to see logs: discovered ModuleNotFoundError in analytics.py import
6. Fixed import paths to use correct modules

**Fix (Commit 586c6b4):**
```python
# Before (WRONG):
from src.api.dependencies import get_current_user, get_db

# After (CORRECT):
from src.api.deps import get_current_user
from src.database import get_db
```

**Status:** ✅ Fixed - Backend now responds to all API requests

**Lessons Learned:**
- Import errors in new API files can silently break the entire backend
- Always verify backend is actually running and responding before debugging client code
- When backend timeouts occur, check backend startup logs first
- Easy to miss import errors when creating new endpoint files

---

## Testing Notes

**Phase 1 Testing:**
- ✅ API endpoint accessible at `/api/v1/analytics/summary`
- ✅ Endpoint returns 401 Unauthorized (auth working)
- ✅ Test fixtures created for 6 logs across 6 days
- ✅ 8 test cases written (totals, averages, top foods, targets, defaults, empty data)
- ✅ Ready for full pytest run with proper auth token

**Settings Tab Regression Testing:**
- ✅ Health Profile section loads without spinner after app launch
- ✅ Cat Style section displays correctly
- ✅ Profile data fetches from localhost:8000 API
- ✅ No errors in console

---

## Prevention Checklist for Future Iteration 18 Work

**MANDATORY STEPS after creating any new backend API file:**

### 1. Import Verification
- [ ] Check all imports use correct module names:
  - `get_current_user, security` → from `src.api.deps` (NOT `src.api.dependencies`)
  - `get_db` → from `src.database` (NOT `src.api.deps` or other modules)
  - Use model imports: `from src.models.* import ...`
  - Use schema imports: `from src.schemas.* import ...`
  - Use service imports: `from src.services.* import ...`

### 2. Backend Startup Test (DO THIS EVERY TIME)
After modifying any backend code:
```bash
cd NomNom-Backend
# Kill any running backend process
pkill -f "uvicorn src.app:app"

# Restart and watch for errors
./venv/bin/python -m uvicorn src.app:app --reload --host 0.0.0.0 --port 8000

# Wait for message: "Application startup complete"
# If it hangs or errors, fix before proceeding
```

### 3. API Endpoint Test
```bash
# Test with invalid token (should get 401, not timeout)
curl -m 5 http://localhost:8000/api/v1/analytics/summary \
  -H "Authorization: Bearer test_token"

# Should respond with JSON error, not timeout
# Expected: {"detail":"Invalid or expired token"} (or similar)
# NOT: timeout after 5 seconds
```

### 4. iOS App Test
- [ ] Clean build: `Product → Clean Build Folder` (⇧⌘K)
- [ ] Run app in simulator
- [ ] Navigate to Settings tab
- [ ] Verify Health Profile section loads (no spinner)
- [ ] Check Xcode console for `[ProfileService]` and `[APIClient]` logs
- [ ] Should see: `[APIClient] GET http://localhost:8000/api/v1/profile`

### 5. Import Style Guide (Reference)
```python
# CORRECT import order for API endpoints:
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user  # ✅ Correct
from src.database import get_db             # ✅ Correct
from src.models.user import User            # ✅ Correct
from src.schemas.analytics import ResponseSchema  # ✅ Correct
from src.repositories.analytics_repository import AnalyticsRepository  # ✅ Correct
from src.services.profile_service import get_effective_targets  # ✅ Correct

# NEVER use:
from src.api.dependencies import ...  # ❌ Module doesn't exist
from src.api import deps              # ❌ Wrong syntax
from src.llm.something import ...     # ❌ Wrong layer
```

### 6. Common Mistakes to Avoid
| Mistake | Symptom | Fix |
|---------|---------|-----|
| Wrong import path for deps | ModuleNotFoundError, app won't start | Use `src.api.deps` |
| Mixing sync/async imports | Various async/await errors | Use AsyncSession from sqlalchemy.ext.asyncio |
| Circular imports | App won't load | Check import order |
| Missing service/repo files | ImportError | Create file before importing |
| Typos in model field names | Validation errors | Match schema to model exactly |

### 7. After Phase 1 Completion
- [ ] All imports verified and tested
- [ ] Backend starts with "Application startup complete"
- [ ] curl test returns JSON response (not timeout)
- [ ] iOS Settings tab loads without spinner
- [ ] Console logs show successful profile fetch
- [ ] Tests pass: `pytest tests/test_analytics.py`

**Next Phase (2) Testing:**
- Will test with actual logged-in user
- Verify iOS can parse WeeklySummaryResponse
- Test week navigation (prev/next week)
