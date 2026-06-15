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

## Regression: Settings Tab Loading Spinners

**Symptom:** After building/running app, Settings tab showed indefinite loading spinners in Health Profile and Cat Style sections.

**Root Cause:** 
1. APIClient.baseURL was pointing to ngrok instead of localhost:8000 for simulator
2. SettingsView was creating a detached AuthService() instead of using @EnvironmentObject
3. When ProfileService tried to load from ngrok, it would fail or hang indefinitely

**Fix (Commit e1f3acf):**
- Changed APIClient baseURL for simulator from ngrok to localhost:8000
- Removed detached AuthService creation in SettingsView.init()
- Made authService optional in SettingsViewModel (set via setAuthService callback)
- Moved logout button handling directly to SettingsView
- Settings tab now loads profile correctly on app run

**Status:** ✅ Fixed

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

**Next Phase (2) Testing:**
- Will test with actual logged-in user
- Verify iOS can parse WeeklySummaryResponse
- Test week navigation (prev/next week)
