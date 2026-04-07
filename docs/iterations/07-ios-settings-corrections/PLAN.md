# Iteration 07 — iOS: Settings, Corrections & Recommendations

## Goal

Complete the iOS app's missing pieces: a Settings tab (logout, cat style, macro goals), fix the unreachable food correction button, wire up the RAG meal recommendations endpoint, and display errors in the Today view.

## What's Built

- iOS: login, camera, food logging, today's log list
- Backend: full LLM harness, embeddings, semantic cache, RAG recommendations endpoint (`GET /api/v1/recommendations/meal`), profile API (`GET/PUT /api/v1/profile`)
- Auth: login/register, JWT, keychain storage, 401 auto-logout

## What We're Building

**4 things to complete the app for real users:**

1. **Settings tab** — logout button, cat personality picker, macro goal inputs (calorie, protein, carb, fat targets)
2. **Food correction UX fix** — after saving a food log the "This is wrong" button is unreachable because a dismiss alert resets all state immediately; replace with inline saved state that keeps the correction button accessible
3. **Meal recommendations** — "What should I eat?" button in Today view calls the RAG endpoint and shows Sonnet's suggestion in a modal sheet
4. **Error display in Today** — `errorMessage` is set in TodayViewModel but never shown to the user

## Resume Skills Demonstrated

- SwiftUI MVVM (new screen from scratch)
- REST API integration in Swift (profile + recommendations endpoints)
- Bug diagnosis and UX state machine fix
- Async/await in SwiftUI 

## Success Criteria

- [ ] Settings tab visible with gear icon
- [ ] Cat style picker saves to backend profile
- [ ] Macro goal inputs (calorie, protein, carb, fat) save to backend
- [ ] Logout button works and returns to LoginView
- [ ] After saving food log, "This is wrong" button is reachable
- [ ] Correction PATCH call succeeds and updates the food log
- [ ] "What should I eat?" button appears in Today view
- [ ] Tapping it calls `/api/v1/recommendations/meal` and shows result
- [ ] Network errors in Today view are displayed (not silently swallowed)
