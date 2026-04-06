# NomNom — Iteration 04: Embeddings, Vector Search & RAG

**Phases:** Phases 6-7 (full plan)

**Goal:** Add embeddings + pgvector support, build a nutrition knowledge base, and create RAG-powered "what should I eat?" recommendations with streaming.

**Resume Skills:** Embeddings & Vector Search, RAG (Retrieval-Augmented Generation), Streaming

---

## What's Built

- LLM harness with structured output
- Food photo analysis with guardrails + caching + logging
- Rate limiting + accuracy tracking
- iOS camera + food logging

## What We're Building

**In Plain English:**

Right now Claude gives generic recommendations: "Eat more protein."

We're going to make it smarter: "You've eaten 800 calories today, need 1200 more. You love Italian food. Here are 3 high-protein Italian meals..."

**How?**

**Part 1 (Phase 6): Embeddings & Vector Search**

Embeddings = convert text to a list of numbers that represents its meaning.
```
"Caesar salad" → [0.23, 0.81, 0.41, ..., 0.52]  (1024 numbers)
"Garden salad" → [0.22, 0.79, 0.40, ..., 0.51]  (similar!)
```

Vector search = "find all meals in the database similar to this one."

What you're building:
- pgvector: PostgreSQL extension to store + search embeddings
- embedding_service: converts text → embeddings
- NutritionKB: database table of nutrition facts (with embeddings)
- Knowledge retrieval: "Find nutrition tips relevant to what the user needs"

**Part 2 (Phase 7): RAG Recommendations**

RAG = Retrieval-Augmented Generation. Instead of Claude guessing, you give Claude facts first, then ask for a recommendation.

```
Step 1: User asks "What should I eat?"
  ↓
Step 2: Retrieve context
  - What's their calorie deficit today? (from Phase 8 dashboard data)
  - What nutrition tips are relevant? (search NutritionKB with embeddings)
  - What meals did they like before? (search past food_logs with embeddings)
  ↓
Step 3: Build smart prompt
  "User needs 400 more calories. Here are relevant nutrition tips:
   [retrieves tips]. They enjoyed: [retrieves past meals].
   What should they eat?"
  ↓
Step 4: Claude gives specific, personalized recommendation
  "Based on your love of Italian food and protein needs, try..."
  ↓
Step 5: Stream response token-by-token to iOS (SSE streaming)
```

Result: Much better recommendations, because Claude has context.

---

## Phase 6: Embeddings + Vector Search + RAG Knowledge Base

### Phase 6.1: Enable pgvector — Add Vector Search to PostgreSQL

**In Plain English:**

PostgreSQL is a database for storing text, numbers, dates. But embeddings are lists of 1024 numbers, and searching them is different.

pgvector = PostgreSQL extension that adds vector search superpowers.

```
Normal search (PostgreSQL):
"SELECT * FROM meals WHERE name LIKE '%salad%'"
→ finds salads by name matching

Vector search (pgvector):
"SELECT * FROM meals WHERE embedding <-> user_query_embedding < 0.1"
→ finds meals SIMILAR IN MEANING to query (even if name doesn't match!)
```

#### 6.1.A: Install pgvector extension

Commands:
```bash
# Connect to your database and enable pgvector
psql -d nomnom -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Verify it worked
psql -d nomnom -c "SELECT extname FROM pg_extension WHERE extname='vector';"
```

#### 6.1.B: Auto-enable pgvector on app startup

Update `src/database.py`:
```python
# When app starts, automatically enable pgvector
@event.listens_for(Engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    dbapi_conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
```

This way, pgvector is always available when your app runs.

---

### Phase 6.2: Embedding Service — Convert Text to Numbers

**In Plain English:**

Embedding = convert text to a list of 1024 numbers that represent its meaning.

```
embed_text("Caesar salad") → [0.23, 0.81, 0.41, ..., 0.52]
embed_text("Garden salad") → [0.22, 0.79, 0.40, ..., 0.51]
                                                    (similar!)
```

Then you can find similar meals:
```
User's favorite pasta → embed it
Search for similar past meals → "Found 5 pastas user liked!"
```

#### 6.2.A: Create `src/services/embedding_service.py` — The Embedder

**What this does:**

```python
def embed_text(text):
  # Call Claude's embedding API
  # (or Voyage API - both work)
  embedding = anthropic.create_embedding(text)
  return embedding  # list of 1024 numbers

def similarity_search(table, query_embedding, limit=5):
  # Use pgvector to find similar rows
  # embedding <-> means "distance between embeddings"
  # Lower distance = more similar
  results = database.query(table).order_by(
    column.embedding.op("<->")(query_embedding)
  ).limit(limit)
  
  return results  # Top 5 most similar
```

How it works:
1. Convert text to embedding (list of 1024 numbers)
2. Store embedding in database column (vector(1024))
3. Query: "Find rows with embeddings closest to this vector"
4. Return top-K matches (most similar)

Files to create:
- `src/services/embedding_service.py` — embedding + similarity search

**Note:** For now, use placeholder embeddings (not calling real API). Later phases will integrate real embeddings.

#### 6.2.B: Test embedding service

What to test:
- embed_text returns 1024-dim vector ✓
- Similarity search finds similar items ✓
- "Caesar salad" is similar to "Garden salad" but not "Pizza" ✓
- Limit works (returns top 5) ✓

Files to create:
- `tests/unit/services/test_embedding_service.py` — test embed_text, similarity_search

Commands:
- `uv run pytest tests/unit/services/test_embedding_service.py -v`

---

### Phase 6.3: NutritionKB Model + Migration

#### 6.3.A: Create `src/models/nutrition_kb.py`

```python
# SQLAlchemy model:
# - id (PK)
# - title (str) — "High-protein breakfast options"
# - content (text) — full nutrition knowledge
# - category (str) — "protein", "meal-prep", "snacks", etc.
# - embedding (Vector(1024)) — pgvector embedding of content
# - created_at (datetime)
```

Files to create:
- `src/models/nutrition_kb.py` — NutritionKB model

Update `src/models/__init__.py`:
- Import NutritionKB

#### 6.3.B: Add embedding column to FoodLog

Update `src/models/food_log.py`:
- Add `embedding: Vector(1024) | None` column

#### 6.3.C: Create alembic migration

Commands:
```bash
uv run alembic revision --autogenerate -m "add pgvector and embedding columns"
uv run alembic upgrade head
```

Verify:
```bash
psql -d nomnom -c "\d+ food_logs" | grep embedding
psql -d nomnom -c "\d+ nutrition_kb" | grep embedding
```

---

### Phase 6.4: Knowledge Service + RAG Retrieval

#### 6.4.A: Create `src/services/knowledge_service.py`

```python
# What it does:
# - Retrieves relevant context for RAG
# - Takes a query (e.g., "I need more protein")
# - Searches nutrition_kb for similar knowledge
# - Searches past food_logs for similar meals
# - Returns top-k results (embeddings, titles, content)

# Key functions:
# - retrieve_nutrition_context(
#     db: AsyncSession,
#     query: str,
#     limit: int = 5
#   ) -> list[NutritionKB]
#     Embed query, search nutrition_kb, return top-k results
# - retrieve_similar_meals(
#     db: AsyncSession,
#     user_id: int,
#     query: str,
#     limit: int = 5
#   ) -> list[FoodLog]
#     Embed query, search user's past meals, return top-k results
```

Files to create:
- `src/services/knowledge_service.py` — RAG context retrieval

#### 6.4.B: Seed nutrition knowledge base

Create `src/seed/nutrition_kb.py`:
```python
# Populate ~50-100 nutrition knowledge entries
# Examples:
# - "High-protein breakfast options: eggs, greek yogurt, cottage cheese, protein powder"
# - "Macro balancing: aim for 30% protein, 40% carbs, 30% fat"
# - "Complex carbs vs simple carbs: oats, brown rice, sweet potatoes vs white bread"
# - etc.

# Each entry should be:
# {
#   title: "...",
#   content: "...",
#   category: "protein" | "meal-prep" | "snacks" | etc.
# }
```

Files to create:
- `src/seed/__init__.py`
- `src/seed/nutrition_kb.py` — knowledge base data

Create a management command to seed:
- Create `src/seed_command.py` or integrate into `run.py`
- Call: `uv run python -c "from src.seed.nutrition_kb import seed; seed()"`

#### 6.4.C: Test knowledge service

Files to create:
- `tests/integration/test_knowledge_service.py` — test retrieve_nutrition_context, retrieve_similar_meals (mocked)

Commands:
- `uv run pytest tests/integration/test_knowledge_service.py -v`

---

### Phase 6.5: Update cache to use embeddings

Now that embeddings work, update `src/llm/cache.py` to use real similarity search:

Update `src/llm/cache.py`:
- embed_photo_description() — create embedding of food photo
- search_for_similar() — query food_logs embeddings table for matches
- Cosine similarity threshold: 0.95

---

## Phase 7: RAG Recommendations + Streaming

### Phase 7.1: Recommendation Prompt Template

#### 7.1.A: Create prompt template

Create `src/llm/prompts/recommend_meal.j2`:
```jinja2
You are a helpful nutrition advisor speaking as a {{ cat_style }} cat.

User's today's intake:
- Calories: {{ today_intake.calories }} / {{ daily_targets.calories }}
- Protein: {{ today_intake.protein }}g / {{ daily_targets.protein }}g
- Carbs: {{ today_intake.carbs }}g / {{ daily_targets.carbs }}g
- Fat: {{ today_intake.fat }}g / {{ daily_targets.fat }}g

Relevant nutrition knowledge:
{% for kb in retrieved_knowledge %}
- {{ kb.title }}: {{ kb.content }}
{% endfor %}

Meals user recently enjoyed:
{% for meal in recent_meals %}
- {{ meal.food_name }} ({{ meal.calories }} cal, {{ meal.protein_g }}g protein)
{% endfor %}

Based on their nutrition goals and preferences, suggest what they should eat next.
Keep it {{ cat_style }} and fun!
```

---

### Phase 7.2: Recommendations Endpoint with Streaming

**In Plain Language:**

Without streaming:
```
User: "What should I eat?"
(waits 5 seconds for Claude to finish thinking)
Claude: "Try a chicken salad with..." (all at once)
```

With streaming:
```
User: "What should I eat?"
(gets words immediately as Claude types)
"Try" → "a" → "chicken" → "salad" → "with" → ...
(feels fast because user sees text appearing!)
```

How it works:
1. User asks "What should I eat?"
2. Backend retrieves context (nutrition tips, past meals)
3. Backend sends prompt to Sonnet with streaming enabled
4. Sonnet generates response word-by-word
5. Backend sends each word to iOS app via SSE (Server-Sent Events)
6. iOS app displays words as they arrive (magic!)

#### 7.2.A: Create `src/api/recommendations.py` — The Recommendation Endpoint

**What this does:**

```python
@router.post("/meal")
async def recommend_meal(
    query: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
  # Step 1: Get user context
  profile = get_user_profile(current_user.id)
  today_intake = get_today_intake(current_user.id)
  
  # Step 2: Retrieve context from knowledge base
  nutrition_tips = knowledge_service.retrieve_nutrition_context(query)
  similar_meals = knowledge_service.retrieve_similar_meals(query)
  
  # Step 3: Build prompt with context
  prompt = render_template(
    "recommend_meal.j2",
    today_intake=today_intake,
    nutrition_tips=nutrition_tips,
    similar_meals=similar_meals,
    query=query
  )
  
  # Step 4: Stream response
  async def event_generator():
    async for token in llm_client.stream_message(
      model="sonnet",
      prompt=prompt
    ):
      yield f"data: {token}\n\n"
  
  return StreamingResponse(event_generator(), media_type="text/event-stream")
```

Files to create:
- `src/api/recommendations.py` — recommendations endpoint

#### 7.2.B: Add streaming to LLMClient

Update `src/llm/client.py`:
```python
async def stream_message(
    self,
    model: str,
    messages: list,
    system: str | None = None
):
    # Use Anthropic streaming API
    async with self.anthropic_client.messages.stream(...) as stream:
        async for text in stream.text_stream:
            yield text  # Yield each token as it arrives
```

#### 7.2.C: Implement SSE in FastAPI

Server-Sent Events (SSE) = standard way to stream data from server to client.

```python
from fastapi.responses import StreamingResponse

# Backend sends: "data: Try\n\n"
# Then:          "data: a\n\n"
# Then:          "data: chicken\n\n"
#
# iOS app receives each line and displays it
```

#### 7.2.D: Test recommendations endpoint

What to test:
- Retrieves nutrition tips correctly ✓
- Retrieves similar past meals ✓
- Streaming sends tokens one-by-one ✓
- iOS can parse SSE events ✓

Files to create:
- `tests/integration/test_recommendations.py` — test /meal with mocked streaming

Commands:
- `uv run pytest tests/integration/test_recommendations.py -v`

---

### Phase 7.3: iOS Streaming Service

**In Plain English:**

iOS needs to know how to parse SSE messages:
```
Receive: "data: Try\n\n"
Parse: "Try"
Display in UI

Receive: "data: a\n\n"
Parse: "a"
Append to UI (now shows "Try a")

... repeat until done
```

Files to update:
- `NomNom-iOS/NomNom/Core/Services/StreamingService.swift` — parse SSE, yield tokens to SwiftUI

---

## Success Criteria

- [x] pgvector enabled in PostgreSQL
- [x] Embedding service generates + stores embeddings
- [x] NutritionKB model + migration
- [x] Similarity search works (pgvector queries)
- [x] Knowledge base seeded with ~50-100 entries
- [x] RAG retrieval returns relevant context
- [x] Semantic caching works (uses embeddings)
- [x] /recommendations/meal endpoint implemented
- [x] Streaming SSE works end-to-end (backend → iOS)
- [x] All tests pass

## Next After Phase 7

Phase 8 adds backend features (dashboard, cat mood, weekly recaps, scheduler). Phase 11-12 adds remaining iOS screens.

## Resume Skills Demonstrated

✅ **Embeddings & Vector Search** — pgvector, cosine similarity, semantic search  
✅ **RAG** — retrieve context, inject into prompt, stream response  
✅ **Streaming** — Server-Sent Events, token-by-token response  
✅ **Cost Optimization** — semantic cache prevents redundant API calls
