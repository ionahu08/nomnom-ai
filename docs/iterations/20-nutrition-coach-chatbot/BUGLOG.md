# Iteration 20: Nutrition Coach Chatbot — Bug Log

**Status:** In Progress  
**Last Updated:** 2026-06-15

---

## Known Issues

### Issue 1: Coach Tab Returns 500 Error (CRITICAL) ❌

**Description:**
- Coach tab fails to send messages with "Failed to send message" error
- Backend returns HTTP 500 Internal Server Error
- Cascades to slow photo saving and slow diary loading

**Root Cause:**
- `NutritionChatService.gather_context()` tries to access `user.profile` (lazy-loaded relationship)
- In async context, SQLAlchemy can't lazy-load without `await`
- Error: `sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called`

**Solution:**
- ✅ Fixed: Added `await db.refresh(current_user, ["profile"])` before accessing `.profile`
- Location: `src/services/nutrition_chat_service.py` line 117-118

**Verification:**
- Test Coach tab message sending
- Should return 200 OK with assistant response

---

### Issue 2: Photo Saving Takes >1 Minute ⏱️

**Description:**
- Taking a photo and saving takes over 1 minute
- User sees no progress/loading indicator
- Likely caused by cascading 500 errors from Issue #1

**Root Cause:**
- Backend endpoints returning 500 errors due to SQLAlchemy async issue (Issue #1)
- iOS app waits for response, timeout retry delays occur
- No loading indicator shows what's happening

**Solution:**
- ✅ Fixed Issue #1 (Coach backend errors) - should resolve this
- ✅ Added loading indicator for nutrition insights (similar feedback needed for photo save)
- Consider adding progress indicator for photo upload in future iteration

**Verification:**
- After fixing Issue #1, test photo saving time
- Should be <10 seconds (image upload + processing)

---

### Issue 3: Food Diary Slow to Load Pictures 📸

**Description:**
- After saving a photo, Food Diary tab takes too long to display the image
- Appears to be network/API latency issue
- Related to backend performance issues

**Root Cause:**
- Backend endpoints returning 500 errors (Issue #1) cause cascading failures
- iOS app retries with exponential backoff, adding delays
- No loading indicator while fetching image data

**Solution:**
- ✅ Fixed Issue #1 (backend errors) - should resolve this
- Consider caching thumbnail images on iOS
- Add loading spinner in Food Diary while images load

**Verification:**
- After fixing Issue #1, test Food Diary image loading
- Should load within 2-3 seconds
- Check if issue persists after backend fix

---

---

## Blockers

*None yet*

---

## Testing Notes

- [ ] Backend chat endpoint accepts and returns valid JSON
- [ ] Chat messages persist across app restarts
- [ ] Quick prompts send correctly formatted messages
- [ ] Claude responses include personalized context (goals, allergies, foods)
- [ ] Long conversation histories load without performance issues
- [ ] Message auto-scroll to bottom works correctly
- [ ] Error handling works (network errors, Claude timeout, etc.)

---

## Design Decisions

| Decision | Rationale | Impact |
|----------|-----------|--------|
| Store all messages in DB | Chat history must persist for user continuity | Adds DB model, requires migration |
| Fetch last 50 messages | Balance between history depth and API response size | Users can scroll back through conversation |
| Auto-scroll to newest message | Better UX for real-time chat | Easier to see new responses immediately |
| 5 quick prompts hardcoded | Faster UX, reduces typing | Can add customization in future iterations |
| Use last 7 days of food logs as context | Recent data most relevant to recommendations | Older logs excluded for brevity |

---

## Session Notes

### Session 1 (June 15, 2026)
- Created PLAN.md with full feature scope
- Created PHASES.md with implementation details
- Updated CLAUDE.md to reflect Iteration 20 start
- Estimated 3-5 days to complete

### Session 2 (June 15, 2026)
- **Phase 1: Backend Infrastructure** ✅ COMPLETE
  * Created NutritionChatMessage model with proper indexing
  * Created Pydantic schemas for chat requests/responses
  * Implemented NutritionChatService with context gathering
  * Created nutrition_coach_prompt.py with customized system prompt
  * Built two API endpoints: POST /chat and GET /chat/history
  * Registered router in app.py
  * Created and ran database migration successfully
  
- **Phase 2: iOS Chat UI** ✅ COMPLETE
  * Created ChatMessage model (Swift Codable)
  * Created ChatMessageView bubble component
  * Created NutritionCoachViewModel with state management
  * Built main NutritionCoachView with:
    - Message list with auto-scroll
    - 5 quick-prompt buttons
    - Input field with send button
    - Loading states
    - Error messages
    - Empty state UI
  * Updated ContentView to add "Coach" tab after Insight tab
  * All files committed and ready for testing

- **Next: Phase 3 (Testing & Integration)**
  - Rebuild iOS app and test on simulator
  - Verify backend endpoints work correctly
  - Test end-to-end chat flow
  - Debug any issues

