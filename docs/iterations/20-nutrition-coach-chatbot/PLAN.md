# Iteration 20: Nutrition Coach Chatbot — Plan

**Status:** 🚀 STARTING (June 15, 2026)  
**Duration:** 3-5 days  
**Complexity:** Medium-High (chat UI + stateful backend + Claude integration)

---

## Goals

Build an interactive nutrition chatbot that users can chat with about their diet, goals, and nutrition gaps. Users can ask questions or use quick-prompt buttons to get personalized advice based on their food logs and health profile.

**Primary User Value:**
- Conversational, engaging way to get nutrition advice
- Personalized recommendations based on actual food logs and health data
- Quick access to common nutrition questions without typing

---

## What's Already Built

From Iteration 19:
- ✅ Nutrition insights backend (`/api/v1/nutrition/insights`)
- ✅ Claude-powered analysis (`NutritionAgent`)
- ✅ Health profile and analytics repository
- ✅ iOS data models and networking

From earlier iterations:
- ✅ Authentication & user sessions
- ✅ Food log storage & analytics
- ✅ User profile management

---

## What We're Building

### Phase 1: Backend Chat API (2 days)

**New Database Model:**
- `NutritionChatMessage` table
  - `id` (uuid)
  - `user_id` (foreign key)
  - `role` (enum: "user" | "assistant")
  - `content` (text)
  - `created_at` (timestamp)
  - Index on `(user_id, created_at)` for fast message retrieval

**New Endpoint:**
- `POST /api/v1/nutrition/chat` — Submit user message, get chatbot response
  - Request: `{ "message": "What should I eat tomorrow?" }`
  - Response: `{ "message": "Based on your logs...", "role": "assistant" }`
  - Returns 200 with response, or 500 if Claude fails

**New Service:**
- `NutritionChatService` class
  - `get_chat_history(user_id, limit=50)` — Fetch last 50 messages
  - `save_message(user_id, role, content)` — Store message in DB
  - `get_chat_response(user_id, user_message)` — Call Claude with context

**Claude Integration:**
- System prompt for "Nutrition Coach" role
  - Conversational, friendly tone
  - References user's current nutrition data
  - Gives specific food/supplement recommendations
  - Respects allergies and medical conditions
  - Suggests meals for specific goals

---

### Phase 2: iOS Chat UI (2 days)

**New Tab:**
- Add "Nutrition Coach" tab to main tab bar (after "Insight" tab)

**New Views:**
- `NutritionCoachView` — Main chat screen
  - ScrollView with message list (scrolls to bottom on new messages)
  - Message bubbles (user on right, assistant on left, different colors)
  - Input field with send button
  - 5 quick-prompt buttons below input

- `ChatMessageView` — Reusable message bubble
  - Shows message content
  - Timestamp
  - Sender indicator (You / Coach)

**New ViewModel:**
- `NutritionCoachViewModel`
  - `@Published var chatMessages: [ChatMessage]` — Message history
  - `@Published var userInput: String` — Current input text
  - `@Published var isLoading: Bool` — Sending/waiting state
  - `@Published var errorMessage: String?` — Error handling
  - `loadChatHistory()` async — Fetch old messages on view load
  - `sendMessage(_ text: String)` async — Send message, get response
  - `sendQuickPrompt(_ prompt: String)` async — Send pre-written prompt

**New Models:**
- `ChatMessage` — Local message model
  - `id: UUID`
  - `role: String` ("user" | "assistant")
  - `content: String`
  - `timestamp: Date`
  - Codable for API serialization

**Data Flow:**
```
User types message or taps quick prompt
    ↓
ViewModel.sendMessage(text) called
    ↓
POST /api/v1/nutrition/chat { "message": text }
    ↓
Backend:
  1. Save user message to DB
  2. Fetch user's food logs, health profile, recent chat history
  3. Call Claude API with full context
  4. Save assistant response to DB
  5. Return response JSON
    ↓
iOS receives response
    ↓
Add both user message and assistant response to UI
    ↓
Scroll to bottom, show new messages
```

---

## Files to Create

### Backend

| Path | Purpose |
|------|---------|
| `src/models/nutrition_chat.py` (NEW) | SQLAlchemy `NutritionChatMessage` model |
| `src/schemas/nutrition_chat.py` (NEW) | Pydantic schemas for chat request/response |
| `src/services/nutrition_chat_service.py` (NEW) | Chat logic, Claude integration, context gathering |
| `src/api/nutrition_chat.py` (NEW) | FastAPI endpoint `/nutrition/chat` |
| `src/llm/nutrition_coach_prompt.py` (NEW) | System prompt for nutrition coach role |

### iOS

| Path | Purpose |
|------|---------|
| `NomNom-iOS/NomNom/Features/NutritionCoach/NutritionCoachView.swift` (NEW) | Main chat UI |
| `NomNom-iOS/NomNom/Features/NutritionCoach/ChatMessageView.swift` (NEW) | Message bubble component |
| `NomNom-iOS/NomNom/Features/NutritionCoach/NutritionCoachViewModel.swift` (NEW) | Chat state management |
| `NomNom-iOS/NomNom/Features/NutritionCoach/ChatMessage.swift` (NEW) | Data model |
| `NomNom-iOS/NomNom/App/ContentView.swift` (MODIFIED) | Add "Nutrition Coach" tab |

### Documentation

| Path | Purpose |
|------|---------|
| `docs/iterations/20-nutrition-coach-chatbot/PLAN.md` (NEW) | This file |
| `docs/iterations/20-nutrition-coach-chatbot/PHASES.md` (NEW) | Detailed implementation steps |

---

## Success Criteria

- [ ] Backend chat endpoint returns 200 with valid response
- [ ] Chat messages persist in database and load on view refresh
- [ ] iOS chat UI displays message list with scrolling
- [ ] Quick prompt buttons send pre-written messages
- [ ] Claude responses are personalized based on user's food logs
- [ ] Chatbot mentions user's health goals, allergies, and gaps
- [ ] No crashes or unhandled errors
- [ ] All existing tests pass
- [ ] Code follows project conventions

---

## Known Risks

1. **Token limits:** Long chat history + full context could exceed Claude token limits
   - Mitigation: Limit chat history to last 10 messages, keep summaries brief

2. **Latency:** Claude API calls take 1-2 seconds
   - Mitigation: Show loading state, disable input during send

3. **Cost:** Each chat message triggers a Claude API call
   - Mitigation: Use Haiku for faster/cheaper responses (consider Sonnet for quality)

4. **Database migration:** New `NutritionChatMessage` table needs to be created
   - Mitigation: Write clean migration, test on staging first

---

## Next Steps

1. Write detailed implementation phases (PHASES.md)
2. Create backend models and endpoint
3. Integrate Claude coaching prompts
4. Build iOS chat UI
5. Test end-to-end
6. Document findings (SUMMARY.md)

---

## Iteration Timeline

| Day | Focus | Deliverable |
|-----|-------|-------------|
| 1 | Backend: DB model, schemas, chat service | Chat endpoint returns response |
| 2 | Backend: Claude integration & context gathering | Responses are personalized |
| 3 | iOS: Chat UI, ViewModel, message display | Chat view renders messages |
| 4 | iOS: Quick prompts, loading states, error handling | Full feature working |
| 5 | Testing, debugging, documentation | SUMMARY.md complete, ready to ship |

