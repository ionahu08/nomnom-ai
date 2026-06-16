# Iteration 20: Nutrition Coach Chatbot — Implementation Phases

---

## Phase 1: Backend Chat Infrastructure

### 1.1 Create Chat Message Model

**File:** `src/models/nutrition_chat.py`

```python
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, Mapped
from src.database import Base
import enum
import uuid

class ChatMessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"

class NutritionChatMessage(Base):
    __tablename__ = "nutrition_chat_messages"
    
    id: Mapped[uuid.UUID] = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = Column(ForeignKey("users.id"), nullable=False, index=True)
    role: Mapped[str] = Column(String(20), nullable=False)  # "user" or "assistant"
    content: Mapped[str] = Column(Text, nullable=False)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Index for fast retrieval
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
    )
```

### 1.2 Create Pydantic Schemas

**File:** `src/schemas/nutrition_chat.py`

```python
from pydantic import BaseModel
from datetime import datetime

class ChatMessageRequest(BaseModel):
    message: str

class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    timestamp: datetime

class ChatHistoryResponse(BaseModel):
    messages: list[ChatMessageResponse]
```

### 1.3 Create Chat Service

**File:** `src/services/nutrition_chat_service.py`

Key methods:
- `get_chat_history(user_id, limit=50)` → Fetch last N messages from DB
- `save_message(user_id, role, content)` → Store message in DB
- `gather_context(user_id)` → Fetch user's food logs, health profile, nutrition summary
- `get_chat_response(user_id, user_message)` → Call Claude with full context

**Context building:**
1. Fetch last 7 days of food logs
2. Fetch user's health profile (goals, allergies, conditions, targets)
3. Fetch nutrition summary (today's intake vs. targets)
4. Fetch last 5 chat messages (for conversation continuity)
5. Pass all as context to Claude

### 1.4 Create Chat Endpoint

**File:** `src/api/nutrition_chat.py`

```
POST /api/v1/nutrition/chat

Request:
{
  "message": "What should I eat tomorrow?"
}

Response:
{
  "id": "msg-123",
  "role": "assistant",
  "content": "Based on your food logs...",
  "timestamp": "2026-06-15T21:30:00Z"
}
```

**Endpoint logic:**
1. Validate user (authentication)
2. Save user message to DB
3. Gather context (food logs, profile, chat history)
4. Call Claude nutrition coach with context
5. Save assistant response to DB
6. Return response to client

### 1.5 Create Nutrition Coach System Prompt

**File:** `src/llm/nutrition_coach_prompt.py`

**System prompt template:**

```
You are a friendly, knowledgeable nutrition coach for a food tracking app.
You help users understand their nutrition, improve their diet, and reach their health goals.

Style:
- Be conversational and encouraging
- Reference the user's actual food logs and goals
- Give specific, actionable advice
- Respect dietary restrictions and medical conditions
- Keep responses concise (3-4 sentences max)

Current user context:
- Goal: {goal}
- Allergies: {allergies}
- Medical conditions: {medical_conditions}
- This week's summary: {nutrition_summary}
- Food logs: {recent_foods}

Answer the user's question based on their specific situation.
Always respect their allergies and medical conditions when recommending foods.
Reference their logged foods when possible to show you understand their eating patterns.
```

---

## Phase 2: iOS Chat UI

### 2.1 Create Chat Message Model

**File:** `NomNom-iOS/NomNom/Features/NutritionCoach/ChatMessage.swift`

```swift
struct ChatMessage: Codable, Identifiable {
    let id: String
    let role: String  // "user" or "assistant"
    let content: String
    let timestamp: Date
    
    var isUserMessage: Bool {
        role == "user"
    }
}
```

### 2.2 Create Message Bubble View

**File:** `NomNom-iOS/NomNom/Features/NutritionCoach/ChatMessageView.swift`

Features:
- Message bubble with text
- Different colors for user (blue) vs. assistant (gray)
- Aligned to right for user, left for assistant
- Timestamp below message
- Word wrapping for long messages

### 2.3 Create Chat ViewModel

**File:** `NomNom-iOS/NomNom/Features/NutritionCoach/NutritionCoachViewModel.swift`

```swift
@MainActor
class NutritionCoachViewModel: ObservableObject {
    @Published var chatMessages: [ChatMessage] = []
    @Published var userInput: String = ""
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let api = APIClient.shared
    
    func loadChatHistory() async {
        // GET /api/v1/nutrition/chat/history
        // Populate chatMessages
    }
    
    func sendMessage(_ text: String) async {
        // 1. Add user message to local list
        // 2. POST /api/v1/nutrition/chat { "message": text }
        // 3. Add assistant response to list
        // 4. Scroll to bottom
    }
    
    func sendQuickPrompt(_ prompt: String) async {
        await sendMessage(prompt)
    }
}
```

### 2.4 Create Main Chat View

**File:** `NomNom-iOS/NomNom/Features/NutritionCoach/NutritionCoachView.swift`

Layout (top to bottom):
1. Navigation title: "🥗 Nutrition Coach"
2. ScrollView with message list
   - ChatMessageView for each message
   - Scrolls to bottom when new message arrives
3. Divider
4. Quick prompt buttons (5 buttons in 2 rows)
   - "Summarize my nutrition this week"
   - "Suggest foods to improve protein intake"
   - "Recommend supplements based on my gaps"
   - "What should I eat tomorrow?"
   - "Am I hitting my goals?"
5. Message input section
   - TextEditor for user input
   - Send button (enabled if text is not empty)
   - Loading indicator while waiting

### 2.5 Update Tab Navigation

**File:** `NomNom-iOS/NomNom/App/ContentView.swift` (MODIFIED)

Add new tab:
```swift
TabView(selection: $selectedTab) {
    // ... existing tabs ...
    
    NutritionCoachView()
        .tabItem {
            Label("Coach", systemImage: "message.fill")
        }
        .tag("coach")
}
```

---

## Phase 3: Integration & Testing

### 3.1 Backend Integration
- Register chat endpoint in `src/app.py`
- Run database migrations (create `nutrition_chat_messages` table)
- Test endpoint with curl:
  ```bash
  curl -X POST http://localhost:8000/api/v1/nutrition/chat \
    -H "Authorization: Bearer {token}" \
    -H "Content-Type: application/json" \
    -d '{"message": "What should I eat tomorrow?"}'
  ```

### 3.2 iOS Integration
- Build and run on simulator
- Test message sending/receiving
- Verify quick prompts work
- Check chat history persists after app close/reopen
- Verify scrolling to bottom on new messages

### 3.3 End-to-End Testing
- User sends message → backend receives it
- Backend calls Claude → response is generated
- Response appears in iOS chat UI
- Message history loads on view open
- Quick prompts send pre-written messages

---

## Key Implementation Details

### Message Persistence
- **Backend:** Save every message immediately (both user and assistant)
- **iOS:** Load chat history on view load (limit to last 50 messages)
- **Scrolling:** Auto-scroll to newest message after sending

### Error Handling
- **Network error:** Show error message, keep input, allow retry
- **Claude timeout:** Show "Assistant is thinking..." and retry after delay
- **DB error:** Log and return 500 to client

### Context Gathering
- Fetch user's last 7 days of food logs
- Fetch health profile (goals, allergies, conditions)
- Calculate nutrition summary (intake vs. targets)
- Include last 5 chat messages for context

### Claude Prompt
- System prompt customized per user (goal, allergies, conditions)
- Context includes actual food logs and nutrition data
- Instruct Claude to reference user's specific foods and goals
- Limit response length (3-4 sentences max to keep UI clean)

---

## Timeline

| Task | Est. Time | Day |
|------|-----------|-----|
| Chat model, schemas, service | 2 hours | 1 |
| Chat endpoint | 1.5 hours | 1 |
| Claude coach prompt | 1 hour | 1 |
| Testing backend | 1 hour | 1 |
| Chat message model (iOS) | 0.5 hours | 2 |
| ChatMessageView bubble | 1 hour | 2 |
| NutritionCoachViewModel | 1.5 hours | 2 |
| NutritionCoachView main UI | 2 hours | 2 |
| Tab navigation integration | 0.5 hours | 3 |
| End-to-end testing | 2 hours | 3 |
| Debugging & refinement | 1.5 hours | 3 |

