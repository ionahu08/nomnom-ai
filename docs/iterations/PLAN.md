# NomNom — Implementation Plan

A food tracking app with an AI-powered cat that roasts your food choices.

- **Backend:** Python 3.12 + FastAPI + SQLAlchemy 2.0 + PostgreSQL + pgvector
- **Frontend:** Swift + SwiftUI (iOS 17+) + MVVM
- **AI:** Claude Haiku (photo analysis) + Claude Sonnet (recaps & recommendations)

---

## Resume Skills Covered

This project is designed to demonstrate **12 key AI/MLE skills**:

| # | Skill | Where in NomNom |
|---|-------|-----------------|
| 1 | **Multimodal AI** | Haiku vision model analyzes food photos |
| 2 | **RAG (Retrieval-Augmented Generation)** | "What should I eat?" retrieves nutrition knowledge + past meals before generating |
| 3 | **Embeddings & Vector Search** | pgvector stores food log embeddings; finds similar past meals for better recommendations |
| 4 | **Prompt Engineering** | Jinja2 prompt templates, persona system prompts, few-shot examples for consistent output |
| 5 | **Structured Output** | Anthropic tool_use to get reliable JSON (not hoping the AI returns valid JSON) |
| 6 | **Streaming** | Server-Sent Events (SSE) stream the cat's roast and recommendations token-by-token |
| 7 | **LLM Harness Engineering** | Retry logic, fallback models, timeouts, token budget caps, multi-model routing |
| 8 | **Output Parsing & Validation** | Pydantic validates AI output; auto-retry on bad responses |
| 9 | **Model Evaluation** | Track AI accuracy from user corrections; measure how often AI gets food wrong |
| 10 | **Cost Optimization** | Model tiering (Haiku vs Sonnet), semantic caching for repeated foods |
| 11 | **AI Observability** | Log every AI call: model, tokens, latency, cost; simple stats endpoint |
| 12 | **Guardrails** | Validate AI output (are calories reasonable?), rate limiting, graceful fallbacks |

---

## Project Structure

### Backend: `NomNom-Backend/`

```
NomNom-Backend/
├── pyproject.toml              <- dependencies & config
├── alembic.ini                 <- database migration config
├── .env.template               <- environment variables template
├── uploads/                    <- where food photos are saved
│
├── alembic/versions/           <- database migration files
│
├── src/
│   ├── app.py                  <- starts the server, connects everything
│   ├── run.py                  <- "press play" file
│   ├── config.py               <- settings (DB url, API keys, etc.)
│   ├── database.py             <- connects to PostgreSQL (+ pgvector extension)
│   ├── constants.py            <- cat moods, food categories, etc.
│   │
│   ├── models/                 <- "what the data looks like" in the database
│   │   ├── user.py             <- User + UserProfile
│   │   ├── food_log.py         <- each meal you log (+ embedding column)
│   │   ├── cat_state.py        <- the cat's current mood
│   │   ├── weekly_recap.py     <- Sunday recap data
│   │   ├── ai_call_log.py      <- every AI call logged here (observability)
│   │   └── nutrition_kb.py     <- nutrition knowledge base entries (for RAG)
│   │
│   ├── schemas/                <- "what the data looks like" in API requests
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── food_log.py
│   │   ├── dashboard.py
│   │   ├── recommendation.py
│   │   ├── cat_state.py
│   │   ├── weekly_recap.py
│   │   └── ai_stats.py         <- AI observability response schemas
│   │
│   ├── api/                    <- the "receptionist" - handles HTTP requests
│   │   ├── deps.py             <- "who is this user?" check
│   │   ├── auth.py             <- register, login
│   │   ├── profile.py          <- onboarding + settings
│   │   ├── food_logs.py        <- upload photo, list/edit/delete meals
│   │   ├── dashboard.py        <- today's macro progress
│   │   ├── recommendations.py  <- "what should I eat?" (streaming SSE)
│   │   ├── weekly_recaps.py    <- past recaps
│   │   ├── cat.py              <- cat mood
│   │   ├── photos.py           <- serve food photos
│   │   └── ai_stats.py         <- AI usage stats endpoint (observability)
│   │
│   ├── services/               <- the "workers" - business logic
│   │   ├── auth_service.py     <- passwords + tokens
│   │   ├── profile_service.py  <- profile CRUD + calorie calculation
│   │   ├── food_log_service.py <- save/load meals, daily totals
│   │   ├── cat_service.py      <- mood calculation (no AI, just rules)
│   │   ├── recap_service.py    <- weekly recap orchestration
│   │   ├── photo_service.py    <- save/load photos
│   │   ├── scheduler.py        <- Sunday recap cron job
│   │   ├── embedding_service.py <- generate & search embeddings (pgvector)
│   │   └── knowledge_service.py <- RAG: retrieve nutrition facts
│   │
│   ├── llm/                    <- LLM harness (all AI orchestration lives here)
│   │   ├── __init__.py
│   │   ├── client.py           <- Anthropic SDK wrapper with retry, timeout, fallback
│   │   ├── router.py           <- picks Haiku vs Sonnet based on task type
│   │   ├── prompts/            <- Jinja2 prompt templates
│   │   │   ├── analyze_food.j2     <- food photo analysis prompt
│   │   │   ├── recommend_meal.j2   <- meal recommendation prompt
│   │   │   ├── weekly_recap.j2     <- weekly recap prompt
│   │   │   └── cat_personas.j2     <- cat personality definitions
│   │   ├── tools.py            <- Anthropic tool_use definitions (structured output)
│   │   ├── parser.py           <- parse + validate AI output with Pydantic, retry on failure
│   │   ├── cache.py            <- semantic cache: reuse results for similar food photos
│   │   ├── guardrails.py       <- validate output (calories in range? food name real?)
│   │   ├── rate_limiter.py     <- per-user rate limiting
│   │   ├── logger.py           <- log every AI call: model, tokens, latency, cost
│   │   └── evaluator.py        <- track accuracy from user corrections
│   │
│   └── seed/                   <- seed data
│       └── nutrition_kb.py     <- populate nutrition knowledge base
│
└── tests/
    ├── unit/                   <- test individual functions
    └── integration/            <- test full API endpoints
```

### Frontend: `NomNom/`

```
NomNom/
├── App/
│   ├── NomNomApp.swift          <- starts the app
│   └── ContentView.swift         <- 5 tabs at the bottom
│
├── Core/
│   ├── Models/                   <- data shapes (matching backend)
│   ├── Services/
│   │   ├── APIClient.swift       <- talks to the backend
│   │   ├── AuthService.swift     <- login/logout
│   │   ├── KeychainService.swift <- stores passwords securely
│   │   ├── PhotoCaptureService.swift  <- camera access
│   │   └── StreamingService.swift     <- handles SSE streaming from backend
│   ├── Components/               <- reusable UI pieces
│   │   ├── CatView.swift         <- the cat with mood expressions
│   │   ├── MacroProgressBar.swift <- colored progress bar
│   │   ├── FoodLogCard.swift     <- meal card
│   │   ├── RoastBubble.swift     <- speech bubble for roast (streams in)
│   │   └── PhotoGridItem.swift   <- thumbnail in timeline
│   └── Utilities/                <- colors, fonts, helpers
│
└── Features/                     <- one folder per screen
    ├── Camera/        (View + ViewModel)
    ├── Dashboard/     (View + ViewModel)
    ├── Timeline/      (View + ViewModel + FoodDetailView)
    ├── WeeklyRecap/   (View + ViewModel + RecapDetailView)
    ├── Onboarding/    (View + ViewModel)
    └── Settings/      (View + ViewModel + LoginView)
```

---

## Database Tables

### `users` - who you are

| Column | Type | What it stores |
|--------|------|---------------|
| id | Integer, PK | unique number |
| email | String(255), unique | your email |
| hashed_password | String(255) | your password (encrypted) |
| created_at | DateTime(tz) | when you signed up |

### `user_profiles` - your body stats & preferences

| Column | Type | What it stores |
|--------|------|---------------|
| id | Integer, PK | unique number |
| user_id | Integer, FK(users.id), unique | links to your user |
| age | Integer | your age |
| gender | String(20) | "male", "female", "other" |
| height_cm | Float | height in centimeters |
| weight_kg | Float | weight in kilograms |
| activity_level | String(20) | "sedentary", "light", "moderate", "active", "very_active" |
| cat_style | String(50) | "sassy", "grumpy", "wholesome", etc. |
| allergies | JSON | ["peanuts", "shellfish"] |
| dietary_restrictions | JSON | ["vegetarian", "halal"] |
| cuisine_preferences | JSON | ["japanese", "mexican"] |
| calorie_target | Integer, nullable | daily calorie goal (auto-calculated or override) |
| protein_target | Integer, nullable | daily protein goal in grams |
| carb_target | Integer, nullable | daily carb goal in grams |
| fat_target | Integer, nullable | daily fat goal in grams |
| notification_enabled | Boolean | default True |
| created_at | DateTime(tz) | |
| updated_at | DateTime(tz) | |

### `food_logs` - every meal you log

| Column | Type | What it stores |
|--------|------|---------------|
| id | Integer, PK | unique number |
| user_id | Integer, FK(users.id) | whose meal this is |
| photo_path | String(500) | where the food photo is saved |
| food_name | String(200) | "Chicken Caesar Salad" |
| calories | Integer | estimated calories |
| protein_g | Float | grams of protein |
| carbs_g | Float | grams of carbs |
| fat_g | Float | grams of fat |
| food_category | String(100) | "salad", "fast food", "dessert" |
| cuisine_origin | String(100) | "Japanese", "Italian" |
| portion_multiplier | Float | default 1.0, user can adjust |
| cat_roast | Text | the cat's funny comment |
| ai_raw_response | JSON, nullable | full AI response for debugging |
| embedding | Vector(1024), nullable | food description embedding for similarity search |
| is_user_corrected | Boolean | default False — flips to True when user edits (used for eval) |
| logged_at | DateTime(tz) | when you ate it |
| created_at | DateTime(tz) | when the log was created |

### `cat_states` - the cat's current mood

| Column | Type | What it stores |
|--------|------|---------------|
| id | Integer, PK | unique number |
| user_id | Integer, FK(users.id), unique | whose cat |
| mood | String(50) | "happy", "judging", "worried", "proud", "sleeping" |
| status_line | Text | "3 meals down, but where are the veggies?" |
| last_updated | DateTime(tz) | |

### `weekly_recaps` - Sunday summaries

| Column | Type | What it stores |
|--------|------|---------------|
| id | Integer, PK | unique number |
| user_id | Integer, FK(users.id) | whose recap |
| week_start | Date | Monday of that week |
| week_end | Date | Sunday of that week |
| narrative | Text | the funny recap story |
| avg_calories | Integer | average daily calories that week |
| best_day | String(20) | day name |
| worst_day | String(20) | day name |
| most_eaten_category | String(100) | "fast food" |
| total_meals_logged | Integer | how many meals that week |
| actionable_nudge | Text | "Try adding eggs at lunch" |
| stats_json | JSON | extra stats |
| created_at | DateTime(tz) | |

### `nutrition_kb` - nutrition knowledge base (for RAG)

| Column | Type | What it stores |
|--------|------|---------------|
| id | Integer, PK | unique number |
| title | String(200) | "High-protein breakfast options" |
| content | Text | the actual nutrition knowledge |
| category | String(100) | "protein", "meal-prep", "snacks", etc. |
| embedding | Vector(1024) | for semantic search |
| created_at | DateTime(tz) | |

### `ai_call_logs` - every AI call logged (observability)

| Column | Type | What it stores |
|--------|------|---------------|
| id | Integer, PK | unique number |
| user_id | Integer, FK(users.id), nullable | who triggered it |
| model | String(100) | "claude-haiku-4-5-20251001" or "claude-sonnet-4-20250514" |
| task_type | String(50) | "analyze_food", "recommend_meal", "weekly_recap" |
| input_tokens | Integer | how many tokens went in |
| output_tokens | Integer | how many tokens came out |
| latency_ms | Integer | how long it took |
| estimated_cost | Float | estimated cost in USD |
| success | Boolean | did it work? |
| error_message | Text, nullable | what went wrong (if it failed) |
| cached | Boolean | was a cached result used instead? |
| created_at | DateTime(tz) | |

---

## API Endpoints

All endpoints prefixed with `/api/v1`.

### Auth (`/auth`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/register` | Create account, return JWT token |
| POST | `/login` | Log in, return JWT token |
| GET | `/me` | Get current user info |

### Profile (`/profile`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/` | Create profile (onboarding) |
| GET | `/` | Get your profile |
| PATCH | `/` | Update profile fields |
| GET | `/targets` | Get calculated daily macro targets |

### Food Logs (`/food-logs`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/analyze` | Upload photo, get AI analysis + roast (streaming SSE) |
| POST | `/` | Save a confirmed meal |
| GET | `/` | List meals (filter by date) |
| GET | `/today` | Shortcut: today's meals |
| GET | `/{log_id}` | Get one meal's details |
| PATCH | `/{log_id}` | Fix a meal entry (triggers eval tracking) |
| DELETE | `/{log_id}` | Delete a meal |

### Dashboard (`/dashboard`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/today` | Today's macro totals + progress vs targets + cat mood |

### Recommendations (`/recommendations`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/meal` | "What should I eat?" - streaming SSE, uses RAG |

### Weekly Recaps (`/recaps`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | List all past recaps |
| GET | `/{recap_id}` | Get one recap |
| POST | `/generate` | Manually trigger recap (debug) |

### Cat (`/cat`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/state` | Current cat mood + status line |

### Photos (`/photos`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/{filename}` | Serve a food photo |

### AI Stats (`/ai-stats`) - observability

| Method | Path | Description |
|--------|------|-------------|
| GET | `/summary` | Total calls, tokens, cost, avg latency (filterable by date range) |
| GET | `/accuracy` | Food ID accuracy rate (% of user corrections) |
| GET | `/cache-hit-rate` | How often the semantic cache was used |

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |

---

## LLM Harness Design (src/llm/)

**Plain English:** An LLM Harness is a **safety net** that wraps around Claude API calls to make them reliable. Instead of calling Claude directly and hoping for the best, the harness:
- Retries if it fails
- Uses a backup model if the first one keeps failing
- Validates the response to make sure it's actually good
- Handles slow/broken API calls gracefully

**Result:** Your app stops crashing when Claude has a bad day.

This is the core AI engineering layer. All AI calls go through this harness — no direct Anthropic SDK calls anywhere else.

### client.py - Anthropic SDK wrapper with Retry + Fallback

**In Plain Language:**
- Try to call Claude Haiku. If it fails, wait 1 second and try again.
- If it fails twice, give up on Haiku and use Claude Sonnet instead (more reliable).
- If everything fails, return a graceful error (don't crash the app).

**Technical Details:**
- Wraps anthropic.AsyncAnthropic with retry, timeout, and fallback logic
- On failure: retry up to 2 times with exponential backoff (1s, then 2s)
- If Haiku fails after retries: fall back to Sonnet
- Timeout: 10s for Haiku, 30s for Sonnet (don't wait forever)
- Token budget: cap max_tokens per call (prevent expensive runaway calls)
- Logs every call to ai_call_logs table via logger.py

### router.py - Choose the right model for the job

**In Plain Language:**
- Food photo analysis? Use Haiku (fast + cheap).
- Writing a funny recommendation? Use Sonnet (smarter).
- Generating a weekly recap story? Use Sonnet (better writing).

**Technical Details:**
- Routes tasks to the right model:
  - "analyze_food" → Haiku (fast, cheap)
  - "recommend_meal" → Sonnet (better writing)
  - "weekly_recap" → Sonnet (narrative quality)

### prompts/ - Jinja2 prompt templates (not hardcoded strings)

**In Plain Language:**
Instead of writing prompts like this in your Python code:
```python
prompt = "You are a sassy cat. Analyze this food..."
```

Store them in separate `.j2` files that are like **fill-in-the-blank templates:**
```jinja2
You are a {{ cat_style }} cat.
Analyze this food and return JSON.
```

Now you can change the cat style without editing code:
```python
prompt = render("template.j2", cat_style="grumpy")
```

**Technical Details:**
- Each AI task has a .j2 template file instead of hardcoded strings
- Templates inject variables: cat_style, user preferences, today's intake, etc.
- cat_personas.j2 defines personality modifiers per cat style
- Few-shot examples included in analyze_food.j2 for consistent output
- Production AI systems always separate prompts from code (easy to version control, review, tweak)

### tools.py - Force Claude to return valid JSON

**In Plain Language:**
Problem: Claude might return text like "Pizza has 500 calories" instead of JSON.

Solution: Tell Claude "You MUST return JSON in THIS exact shape, no other format allowed":
```json
{
  "food_name": "string",
  "calories": 500,
  "protein_g": 25
}
```

Claude is now forced to follow this format. No garbage text.

**Technical Details:**
- Defines tool schemas that tell the AI exactly what JSON shape to return
- Example: analyze_food tool has properties: food_name, calories, protein_g, fat_g, etc.
- The AI is forced to return structured data matching the schema via `tool_use`
- This is more reliable than asking for JSON in the prompt (SDK guarantees the shape)

### parser.py - Check the response is actually good + auto-retry

**In Plain Language:**
Even with tool_use, Claude might return bad data like:
- Calories: 50,000 (impossible)
- Protein: -50g (negative doesn't make sense)

Solution: Check the data and if it's bad, try again automatically.

**Technical Details:**
- Takes raw AI tool_use output and validates with Pydantic models
- Checks: are calories between 0-5000? is protein between 0-500g?
- If validation fails: retry the AI call (up to 2 times)
- If still fails: return a "could not analyze" fallback
- AI output is never trusted blindly — always validate before using

### cache.py - semantic caching

```
What it does:
- Before calling AI, generate an embedding of the food photo description
- Search pgvector for similar past analyses (cosine similarity > 0.95)
- If found: return cached result instead of calling AI again
- Saves money when users photograph the same lunch repeatedly

Why this matters:
- Real AI apps optimize costs by avoiding redundant API calls
- Demonstrates embeddings + vector search in a practical context
```

### guardrails.py - output validation

```
What it does:
- Checks AI output makes sense:
  - Calories: must be 0-5000 (a meal can't be 50,000 calories)
  - Protein/carbs/fat: must be 0-500g
  - Food name: must be non-empty, under 200 chars
  - Roast: must be non-empty, under 500 chars, no harmful content
- If any check fails: flag the response, use a safe default

Why this matters:
- LLMs hallucinate. Guardrails prevent nonsense from reaching users.
```

### rate_limiter.py - per-user rate limiting

```
What it does:
- Tracks AI calls per user per hour
- Default limit: 30 analyze calls/hour, 10 recommendation calls/hour
- Returns 429 Too Many Requests if exceeded
- Prevents abuse and runaway costs

Why this matters:
- Any production AI API needs rate limiting
```

### logger.py - AI call logging

```
What it does:
- Logs every AI call to the ai_call_logs table:
  - model used, task type, input/output tokens, latency, cost, success/failure
- Cost calculated from Anthropic's per-token pricing
- Powers the /ai-stats endpoints

Why this matters:
- You can't optimize what you can't measure
- Shows you understand AI ops and cost management
```

### evaluator.py - accuracy tracking

```
What it does:
- When a user corrects a food log (PATCH with is_user_corrected=True):
  - Records what the AI said vs what the user changed it to
  - Tracks correction rate over time
- Powers the /ai-stats/accuracy endpoint
- Example metric: "AI correctly identified food 87% of the time"

Why this matters:
- Model evaluation from real user feedback is a core MLE skill
- Shows you think about model quality, not just shipping features
```

---

## How AI is Used

| Feature | Model | Harness features used |
|---------|-------|-----------------------|
| Photo analysis + roast | **Haiku** | tool_use, prompt templates, guardrails, cache, retry, logging, streaming |
| "What should I eat?" | **Sonnet** | RAG (retrieves nutrition KB + past meals), prompt templates, streaming, logging |
| Weekly recap | **Sonnet** | prompt templates, retry, logging |
| Cat mood | **No AI** | just if/else rules in cat_service.py |
| Embeddings | **Voyage or Anthropic** | embedding_service generates vectors for food logs and nutrition KB |

### Cat mood rules (no AI, just logic in `cat_service.py`):

- All macros 80-110% of target = "proud"
- Calories over 120% = "judging"
- Calories under 50% = "worried"
- Good protein but junk food = "conflicted"
- No food logged today = "sleeping"
- Default = "happy"

---

## Key Design Decisions

### TDEE Formula (calorie calculation)
Uses Mifflin-St Jeor equation: calculate BMR from age, weight, height, gender. Multiply by activity factor. Default macro split: 40% carbs, 30% protein, 30% fat. User can override individual targets.

### Two-Step Photo Flow
1. `POST /food-logs/analyze` - sends photo, streams AI analysis back (not saved yet)
2. User reviews, can edit the food name or portion size
3. `POST /food-logs` - saves the confirmed data

This lets users fix AI mistakes before saving — and those corrections feed into evaluation metrics.

### RAG for Recommendations
When user asks "What should I eat?":
1. Get today's intake (what macros are missing)
2. Embed the query + context
3. Search nutrition_kb via pgvector for relevant nutrition tips
4. Search past food_logs via pgvector for meals the user liked with good macros
5. Pack retrieved context into the Sonnet prompt
6. Stream the recommendation back

### Sunday Recap Scheduler
Uses APScheduler with a CronTrigger for Sunday at midnight. The job loops through all users who logged food that week and generates a recap for each one.

### Semantic Cache Strategy
- After analyzing a food photo, generate an embedding of the result
- Store it on the food_log row
- Next time, before calling Haiku, embed a description of the new photo
- If cosine similarity > 0.95 with a past result, return the cached analysis
- This saves API costs for users who eat the same meals regularly

---

## Build Order (12 Phases)

| Phase | What you build | Resume skills covered |
|-------|---------------|----------------------|
| **1** | Project setup, database, auth, user profile | Foundation |
| **2** | Food log CRUD + photo storage | Foundation |
| **3** | LLM harness: client, router, prompts, tools, parser | **LLM Harness, Structured Output, Prompt Engineering** |
| **4** | AI photo analysis (Haiku) via harness | **Multimodal AI** |
| **5** | Guardrails, caching, logging, rate limiting, evaluation | **Guardrails, Caching, Observability, Evaluation, Cost Optimization** |
| **6** | Embeddings + vector search + nutrition KB | **Embeddings, Vector Search** |
| **7** | RAG-powered recommendations (Sonnet) + streaming | **RAG, Streaming** |
| **8** | Dashboard + cat mood + weekly recaps + scheduler | Full backend complete |
| **9** | iOS app - foundation + auth | Phone app skeleton |
| **10** | iOS - camera + food logging (with streaming) | Main screen |
| **11** | iOS - dashboard | Progress bars + cat |
| **12** | iOS - timeline, recaps, onboarding, settings | Remaining screens |

### Phase 1: Backend Foundation

#### Step 1: Project setup — config files

Create the project skeleton with all configuration files.

Files to create:
- `NomNom-Backend/pyproject.toml` — project name, Python version, all dependencies (fastapi, sqlalchemy, anthropic, bcrypt, pyjwt, etc.), ruff linter config, pytest config
- `NomNom-Backend/.env.template` — lists env vars: DATABASE_URL, JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRY_MINUTES, ANTHROPIC_API_KEY
- `NomNom-Backend/.env` — copy of .env.template with real values filled in (gitignored)
- `NomNom-Backend/.gitignore` — ignore __pycache__, .env, .venv, uploads/*, *.db
- `NomNom-Backend/.python-version` — "3.12"
- `NomNom-Backend/uploads/.gitkeep` — empty file so git tracks the folder
- `NomNom-Backend/src/__init__.py` — empty file

#### Step 2: Core infrastructure — config, database, app, run

The backbone files that everything else depends on.

Files to create:
- `src/config.py` — Pydantic BaseSettings class that reads from .env: database_url, jwt_secret_key, jwt_algorithm, jwt_expiry_minutes, anthropic_api_key, upload_dir
- `src/database.py` — SQLAlchemy async engine, async_sessionmaker, Base class, get_db() generator for FastAPI dependency injection
- `src/constants.py` — TDEE activity multipliers, default macro split percentages (30% protein, 40% carbs, 30% fat), calories per gram
- `src/app.py` — FastAPI factory: create_app() registers routers, adds CORS middleware, adds /health endpoint
- `src/run.py` — uvicorn entrypoint: runs src.app:app on port 8000 with reload

How to verify: `uv run python -c "from src.config import settings; print(settings.database_url)"`

#### Step 3: Database setup — create the PostgreSQL database

Create the `nomnom` database in PostgreSQL.

Commands to run:
- `createdb nomnom` — creates the database
- Verify: `psql -d nomnom -c "SELECT 1"` — should return 1

#### Step 4: Models — User and UserProfile

Define what users and profiles look like in the database.

Files to create:
- `src/models/__init__.py` — imports and re-exports User, UserProfile
- `src/models/user.py` — two SQLAlchemy models:
  - **User**: id (PK), email (unique, indexed), hashed_password, created_at (auto)
  - **UserProfile**: id (PK), user_id (FK to users, unique), age, gender, height_cm, weight_kg, activity_level, cat_style, allergies (JSON), dietary_restrictions (JSON), cuisine_preferences (JSON), calorie_target, protein_target, carb_target, fat_target, notification_enabled, created_at, updated_at
  - User has relationship to UserProfile (one-to-one)

#### Step 5: Alembic setup + first migration

Set up database migrations and create the users + user_profiles tables.

Files to create:
- `NomNom-Backend/alembic.ini` — alembic config pointing to ./alembic directory
- `NomNom-Backend/alembic/env.py` — async migration runner (imports settings, Base, all models)
- `NomNom-Backend/alembic/script.py.mako` — migration template

Commands to run:
- `uv run alembic revision --autogenerate -m "create users and user_profiles"` — generates migration
- `uv run alembic upgrade head` — runs migration, creates tables in PostgreSQL
- Verify: `psql -d nomnom -c "\dt"` — should show users and user_profiles tables

#### Step 6: Schemas — auth and user

Define what API requests and responses look like.

Files to create:
- `src/schemas/__init__.py` — empty
- `src/schemas/auth.py` — Pydantic models:
  - RegisterRequest (email, password)
  - LoginRequest (email, password)
  - TokenResponse (access_token, token_type)
  - UserResponse (id, email)
- `src/schemas/user.py` — Pydantic models:
  - ProfileCreate (age, gender, height_cm, weight_kg, activity_level, cat_style, allergies, dietary_restrictions, cuisine_preferences)
  - ProfileUpdate (all fields optional)
  - ProfileResponse (all fields + calculated targets)

#### Step 7: Services — auth_service and profile_service

The business logic layer.

Files to create:
- `src/services/__init__.py` — empty
- `src/services/auth_service.py` — functions:
  - hash_password(password) — bcrypt hash
  - verify_password(password, hashed) — bcrypt check
  - create_token(user_id) — JWT with expiry
  - decode_token(token) — JWT decode
  - register_user(db, email, password) — create user in DB
  - authenticate_user(db, email, password) — check credentials
  - get_user_by_id(db, user_id) — lookup user
- `src/services/profile_service.py` — functions:
  - calculate_tdee(age, gender, height_cm, weight_kg, activity_level) — Mifflin-St Jeor formula
  - calculate_macro_targets(tdee) — split into protein/carbs/fat grams
  - create_profile(db, user_id, data) — save profile to DB
  - get_profile(db, user_id) — load profile
  - update_profile(db, user_id, data) — partial update

#### Step 8: API endpoints — auth, profile, deps

The HTTP endpoints that the iOS app will call.

Files to create:
- `src/api/__init__.py` — empty
- `src/api/deps.py` — get_current_user() dependency: extracts JWT from Authorization header, decodes it, returns User
- `src/api/auth.py` — router with prefix /api/v1/auth:
  - POST /register — create account, return token
  - POST /login — check credentials, return token
  - GET /me — return current user info
- `src/api/profile.py` — router with prefix /api/v1/profile:
  - POST / — create profile (onboarding)
  - GET / — get profile + calculated targets
  - PATCH / — update profile fields

Then wire all routers into src/app.py.

#### Step 9: Install dependencies and verify

Commands to run:
- `uv sync` — install all dependencies into virtual environment
- `uv run python -m src.run` — start the server
- Open browser: http://localhost:8000/docs — FastAPI's auto-generated test page
- Test: register a user, login, create a profile

#### Step 10: Tests

Files to create:
- `tests/__init__.py` — empty
- `tests/conftest.py` — test database setup (SQLite for tests), test client, test user fixture
- `tests/unit/__init__.py` — empty
- `tests/unit/test_tdee.py` — test TDEE calculation with known values
- `tests/unit/test_auth_service.py` — test password hashing, token creation/decoding
- `tests/integration/__init__.py` — empty
- `tests/integration/test_auth.py` — test register, login, me endpoints
- `tests/integration/test_profile.py` — test profile create, get, update endpoints

Command to run: `uv run pytest tests/ -v`

### Phase 2: Food Logging + Photo Storage
- models: FoodLog (without embedding column yet)
- schemas: food_log
- services: food_log_service, photo_service
- api: food_logs (analyze is a stub for now), photos
- alembic migration: food_logs table
- tests: food_logs

### Phase 3: LLM Harness
This is the big AI engineering phase. Build the harness before wiring it up.
- llm/client.py: Anthropic wrapper with retry (exponential backoff), timeout (10s/30s), fallback model
- llm/router.py: task -> model mapping
- llm/prompts/: Jinja2 templates for all 3 tasks + cat personas
- llm/tools.py: Anthropic tool_use schema definitions for food analysis
- llm/parser.py: Pydantic validation of AI output + retry on failure
- tests: client retry logic, parser validation, prompt rendering

### Phase 4: AI Photo Analysis
- Wire up POST /food-logs/analyze to the harness
- Flow: photo -> base64 -> client.py -> router (Haiku) -> tool_use -> parser -> response
- Add streaming SSE to the analyze endpoint
- tests: analyze endpoint (mocked AI)

### Phase 5: Guardrails, Caching, Logging, Rate Limiting, Evaluation
- llm/guardrails.py: calorie range checks, food name validation, roast content check
- llm/cache.py: semantic cache lookup before AI calls
- llm/logger.py: log every call to ai_call_logs table
- llm/rate_limiter.py: per-user call limits
- llm/evaluator.py: track corrections when users PATCH food logs
- models: AiCallLog
- schemas: ai_stats
- api: ai_stats (summary, accuracy, cache-hit-rate endpoints)
- alembic migration: ai_call_logs table
- tests: guardrails, rate limiter, evaluator

### Phase 6: Embeddings + Vector Search + RAG Knowledge Base
- Enable pgvector extension in database.py
- services/embedding_service.py: generate embeddings, similarity search
- models: NutritionKB (with embedding column)
- Add embedding column to food_logs (alembic migration)
- seed/nutrition_kb.py: populate ~50-100 nutrition knowledge entries
- services/knowledge_service.py: RAG retrieval (query -> embed -> search -> return top-k)
- tests: embedding search, knowledge retrieval

### Phase 7: RAG Recommendations + Streaming
- llm/prompts/recommend_meal.j2: template that includes retrieved context
- api/recommendations.py: streaming SSE endpoint
- Flow: user asks -> get today's intake -> embed query -> retrieve from nutrition_kb + past meals -> build prompt -> stream Sonnet response
- tests: recommendation endpoint

### Phase 8: Dashboard + Cat Mood + Weekly Recaps
- models: CatState, WeeklyRecap
- schemas: dashboard, cat_state, weekly_recap
- services: cat_service, recap_service, scheduler
- llm/prompts/weekly_recap.j2: recap prompt template
- api: dashboard, cat, weekly_recaps
- alembic migration: cat_states + weekly_recaps tables
- tests: cat mood logic, dashboard, recaps

### Phase 9: iOS Foundation + Auth
- NomNomApp.swift, ContentView.swift
- APIClient, AuthService, KeychainService
- NomNomColors, NomNomTypography
- LoginView

### Phase 10: iOS Camera + Food Logging
- Models: FoodLog
- PhotoCaptureService
- StreamingService (handles SSE from backend)
- CameraView + CameraViewModel
- RoastBubble (streams text in), FoodLogCard components

### Phase 11: iOS Dashboard
- Models: Dashboard, CatState
- CatView, MacroProgressBar components
- DashboardView + DashboardViewModel

### Phase 12: iOS Remaining Screens
- Timeline: TimelineView, FoodDetailView, PhotoGridItem
- Weekly Recap: WeeklyRecapView, RecapDetailView
- Onboarding: OnboardingView (multi-step flow)
- Settings: SettingsView
