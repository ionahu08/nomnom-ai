# NomNom — Learning Notes

## Tech Stack
- **Frontend:** SwiftUI (iOS 17+)
- **Backend:** Python + FastAPI
- **Database:** SQLite (via SQLAlchemy)
- **AI Models:** Claude Haiku (food photo analysis) + Claude Sonnet (weekly recaps & recommendations)
- **Hosting:** Local + ngrok (for now)

## Key Concepts

### API
A way for two programs to talk to each other. The iPhone app asks the backend server for data, the server responds. Like a restaurant menu — the menu lists what you can order, you ask the waiter, the kitchen makes it, the waiter brings it back.

### SQLite vs PostgreSQL
- SQLite = a single file on your computer. No setup. One user at a time. Good for learning and prototyping.
- PostgreSQL = a separate server. Needs installation and configuration. Handles many users at once. Good for production.
- Start with SQLite, switch to PostgreSQL later when you need multiple users. The code change is minimal because SQLAlchemy works with both — you just change the connection string.

### Claude Model Tiers
- **Haiku** — fast, cheap, good enough for most tasks (food photo analysis)
- **Sonnet** — smarter, mid-price (weekly recaps, recommendations)
- **Opus** — smartest, most expensive (not needed for this app)
- You pick the model per request in code, not a global setting.

### Multi-Agent System (from Nexora)
- Multiple specialized AIs instead of one that does everything
- Hierarchical: backend decides which agent to call
- ReAct pattern: Think → Call tool → Read result → Repeat → Final answer
- Role-based routing: different request types go to different agents
- Tool scoping: each agent only accesses the tools and data it needs

### Paper Trading (Nexora concept)
- Trade with fake money at real prices. No risk, full learning.

### LLM Agent
- A chatbot that can take actions (call functions), not just reply
- Tools = functions the AI can call (look up prices, save to database, etc.)

## App Scope — NomNom

### 3 Tabs
1. **Home** — cat + nutrient progress bars + today's meals + "What should I eat?" button
2. **Timeline** — scrollable photo grid of past meals by date
3. **Settings** — profile, preferences, cat customization

### Pop-up Screens (not tabs)
- **Camera** — floating button on Home tab, opens as overlay
- **Weekly Recap** — card at top of Home tab
- **Food Detail** — tap any photo in Timeline

### Core Flow
Camera → Vision LLM → structured food data (name, calories, protein, carbs, fat) + funny roast → saved to database → progress bars update → cat reacts

## Decisions Made
- Using SQLite because we're the only user and it's zero setup
- Using Haiku for high-volume cheap tasks, Sonnet for low-volume smart tasks
- Same stack as teacher's Nexora (SwiftUI + FastAPI) to reference patterns directly
- .env file for API key storage, .gitignore to keep it out of git
