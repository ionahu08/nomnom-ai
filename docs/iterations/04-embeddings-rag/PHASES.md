# Phases — Iteration 04: Embeddings, Vector Search & RAG

## Phase 6: Embeddings + Vector Search

### 6.1: Enable pgvector

- [ ] `psql -d nomnom -c "CREATE EXTENSION IF NOT EXISTS vector;"`
- [ ] Update `src/database.py` — auto-enable pgvector on startup

### 6.2: Embedding Service

- [ ] Create `src/services/embedding_service.py`:
  - `embed_text(text) → list[float]` — convert text to 1024-dim vector
  - `similarity_search(db, query_embedding, table, limit=5)` — find similar rows via pgvector
- [ ] Create `tests/unit/services/test_embedding_service.py`

### 6.3: NutritionKB Model + Migration

- [ ] Create `src/models/nutrition_kb.py`:
  - id, title, content, category, embedding (Vector(1024)), created_at
- [ ] Update `src/models/food_log.py` — add `embedding` column
- [ ] Alembic migration for both models

### 6.4: Knowledge Service + Seed Data

- [ ] Create `src/services/knowledge_service.py`:
  - `retrieve_nutrition_context(query, limit=5)` — embed query, search KB
  - `retrieve_similar_meals(user_id, query, limit=5)` — search past meals
- [ ] Create `src/seed/nutrition_kb.py` — 50-100 nutrition knowledge entries
- [ ] Create `tests/integration/test_knowledge_service.py`

### 6.5: Update Semantic Cache

- [ ] Update `src/llm/cache.py` — now uses real embeddings + pgvector search

---

## Phase 7: RAG Recommendations + Streaming

### 7.1: Recommendation Prompt Template

- [ ] Create `src/llm/prompts/recommend_meal.j2` — includes retrieved context

### 7.2: Recommendations Endpoint + Streaming

- [ ] Create `src/api/recommendations.py`:
  - POST `/api/v1/recommendations/meal` → streaming SSE
  - Retrieve context (nutrition + past meals)
  - Build prompt with context
  - Stream Sonnet response token-by-token
- [ ] Add `stream_message()` to `src/llm/client.py` — use Anthropic streaming API
- [ ] Create `tests/integration/test_recommendations.py`

### 7.3: iOS Streaming Service

- [ ] Update `NomNom-iOS/NomNom/Core/Services/StreamingService.swift` — parse SSE events

---

## Success Criteria

- [x] pgvector enabled
- [x] Embeddings generated + stored
- [x] Similarity search works (pgvector queries)
- [x] Knowledge base seeded (~50-100 entries)
- [x] RAG retrieval returns relevant context
- [x] Recommendations endpoint implemented
- [x] Streaming SSE works end-to-end (backend → iOS)
- [x] All tests pass
