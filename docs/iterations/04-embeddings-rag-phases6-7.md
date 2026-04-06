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

**Part 1 (Phase 6): Embeddings & Vector Search**
- Enable pgvector extension in PostgreSQL
- Create embedding_service.py — generate embeddings for text
- Add NutritionKB model — knowledge base entries with embeddings
- Implement semantic search — find similar food logs and nutrition tips

**Part 2 (Phase 7): RAG Recommendations**
- Create recommendations API endpoint
- Flow: user asks "what should I eat?" → retrieve context from KB + past meals → build prompt with retrieved context → stream Sonnet response
- Streaming: use Server-Sent Events (SSE) to stream recommendation token-by-token to iOS

---

## Phase 6: Embeddings + Vector Search + RAG Knowledge Base

### Phase 6.1: Enable pgvector

#### 6.1.A: Install pgvector PostgreSQL extension

Commands:
```bash
# Connect to PostgreSQL
psql -d nomnom -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Verify installation
psql -d nomnom -c "SELECT extname FROM pg_extension WHERE extname='vector';"
```

#### 6.1.B: Update database.py

Update `src/database.py`:
- Import `from sqlalchemy import event`
- Add event listener on connection: `conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))`
- This auto-creates pgvector on startup

---

### Phase 6.2: Embedding Service

Create the service that generates embeddings.

#### 6.2.A: Create `src/services/embedding_service.py`

```python
# What it does:
# - Generate embeddings for text using Claude API or Voyage
# - Store embeddings as Vector(1024) in database
# - Perform similarity search via pgvector

# Key functions:
# - embed_text(text: str) -> list[float]
#     Call Anthropic embedding API or Voyage
#     Return 1024-dim vector
# - similarity_search(
#     db: AsyncSession,
#     query_embedding: list[float],
#     table: str,  # "food_logs" or "nutrition_kb"
#     limit: int = 5,
#     similarity_threshold: float = 0.5
#   ) -> list[Result]
#     Use pgvector: SELECT * FROM table WHERE embedding <-> query_embedding < distance
#     Return top-k results ordered by similarity
```

Files to create:
- `src/services/embedding_service.py` — embedding generation + similarity search

Note: For now, use placeholder embeddings (not calling API). Phase 6.4 will integrate real embeddings.

#### 6.2.B: Test embedding service

Files to create:
- `tests/unit/services/test_embedding_service.py` — test embed_text, similarity_search (mocked)

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

#### 7.2.A: Create `src/api/recommendations.py`

```python
# Endpoint:
# POST /api/v1/recommendations/meal
# Body: { "query": "I need more protein" }
# Response: Server-Sent Events stream (text/event-stream)

# Flow:
# 1. Get user profile (dietary preferences, targets)
# 2. Get today's food intake (calories, macros)
# 3. Embed query
# 4. Retrieve nutrition context (knowledge_service)
# 5. Retrieve similar meals (knowledge_service)
# 6. Build prompt with template
# 7. Call Sonnet (streaming)
# 8. Stream response token-by-token as SSE
```

Files to create:
- `src/api/recommendations.py` — recommendations endpoint

#### 7.2.B: Wire SSE streaming into LLMClient

Update `src/llm/client.py`:
- Add `stream_message()` method that yields tokens
- Use `anthropic.AsyncAnthropic().messages.stream()` for token-by-token streaming

```python
async def stream_message(
    self,
    model: str,
    messages: list,
    max_tokens: int,
    system: str | None = None
):
    # Use Anthropic streaming
    # Yield each token as it arrives
    # Handle errors gracefully
```

#### 7.2.C: Implement SSE in FastAPI

Update `src/api/recommendations.py`:
```python
from fastapi.responses import StreamingResponse

@router.post("/meal")
async def recommend_meal(
    query: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # ... prepare context ...
    
    async def event_generator():
        async for token in llm_client.stream_message(...):
            yield f"data: {token}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

#### 7.2.D: Test recommendations endpoint

Files to create:
- `tests/integration/test_recommendations.py` — test /meal endpoint (mocked streaming)

Commands:
- `uv run pytest tests/integration/test_recommendations.py -v`

---

### Phase 7.3: iOS Streaming Service

Update iOS app to handle SSE streaming (you may have this already):

Files to update:
- `NomNom-iOS/NomNom/Core/Services/StreamingService.swift` — parse SSE events, yield tokens

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
