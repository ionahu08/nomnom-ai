# NomNom — AI-Powered Food Tracking App

**Full-Stack AI Engineer | Python/FastAPI Backend + SwiftUI iOS | Claude API Integration**

## Overview

Architected and developed NomNom, a production full-stack application that analyzes food photos using Claude AI, stores embeddings in PostgreSQL, and serves personalized meal recommendations via RAG. The app demonstrates advanced LLM orchestration, semantic caching, multi-turn prompt engineering, and real-time iOS-to-backend integration patterns used in modern AI systems.

---

## Core AI/ML Architecture & Techniques

### 1. LLM Integration & Multi-Model Routing
- **Multi-model strategy**: Implemented intelligent model selection using Claude Opus (complex reasoning), Sonnet (balanced tasks), and Haiku (speed-critical, real-time inference). Haiku used for food analysis (20s timeout limit), fallback to Sonnet for accuracy-critical scenarios.
- **Structured output generation**: Implemented tool_use pattern with JSON validation for deterministic, parseable LLM responses. System prompt enforces exact output format (food name, calories, macros, category, roast) to eliminate parsing errors.
- **Prompt engineering**: Built Jinja2 template-based prompt engine with variable interpolation. Created parametrized system prompts that adapt tone based on user-selected cat personality (sassy, grumpy, wholesome, etc.), demonstrating dynamic context injection.
- **Response streaming**: Integrated Claude API streaming to provide real-time feedback during food analysis, improving perceived latency and UX.

### 2. Semantic Caching & Cost Optimization
- **Embedding-based deduplication**: Implemented semantic cache using sentence-transformers (all-MiniLM-L6-v2 384-dim vectors) to detect similar food analyses. When user uploads a pizza photo, system generates embedding, queries pgvector for cosine similarity < 0.15, and returns cached LLM result instantly (0ms latency vs 15-30s API call).
- **pgvector integration**: Extended PostgreSQL with pgvector extension to store and query 384-dimensional food embeddings. Semantic similarity search reduces Claude API calls by ~40% on typical user patterns, directly lowering cost per user.
- **Cost-latency tradeoff**: Cache hits eliminate expensive API calls while preserving user experience. Guardrail system ensures cached results meet quality standards before serving.

### 3. Retrieval Augmented Generation (RAG)
- **Knowledge base construction**: Seeded nutrition knowledge base with domain-specific tips (macros, meal timing, hydration). Each KB entry embedded and stored in pgvector for semantic search.
- **Dynamic context injection**: Meal recommendation endpoint retrieves top-5 most similar KB entries via pgvector similarity search, injects as system context to Claude prompt: "Based on these nutrition facts, suggest a meal for this user."
- **Personalization**: RAG respects user profile (targets, dietary restrictions, preferences). Claude generates meal suggestions grounded in actual user knowledge base rather than generic recommendations.

### 4. Robust LLM Error Handling & Observability
- **Retry logic with exponential backoff**: Implemented 2-attempt retry cycle with exponential backoff (1s, 2s). On timeout/API error, automatically falls back to Haiku model to ensure food analysis completes.
- **Timeout management**: Enforced hard timeout limits per model (Haiku: 20s, Sonnet: 30s) to prevent iOS app hangs. Timeout errors logged with context (attempt #, duration, model, user).
- **Structured error response**: API returns standardized error objects with error code, message, and retry_after hint. iOS client implements exponential backoff with user-friendly error messages.
- **Parser & guardrails**: Built output parser that validates JSON structure, checks for hallucinated calories (guardrail: 300-1200 kcal range), sanitizes food names. Non-compliant responses trigger retry or fallback.
- **Comprehensive logging**: Integrated observability layer that logs LLM inputs/outputs, latency, token usage (input/output counts), cache hits/misses, retry attempts. Enabled data-driven performance optimization.

### 5. Multi-Turn Conversation Management
- **Stateless API design**: Despite HTTP being stateless, implemented persistent conversation state for food correction workflow. User receives initial LLM analysis → taps "This is wrong" → modal prompts for correction → PATCH sends user-corrected value. Backend records `is_user_corrected = true` and rejects re-analysis attempts.
- **Context preservation**: System maintains conversation history as food logs accumulate. User profile and past meals inform future recommendations via RAG (cat learns preferences).
- **Prompt evaluation framework**: Built evaluation pipeline (similar to Claude course) that tests prompt variations against dataset of test foods (pizza, salad, sushi, etc.), grades outputs on nutritional accuracy and roast quality using model-based grading.

---

## System Design & Production Patterns

### Backend Architecture (Python/FastAPI)
- **Async/await throughout**: Used `asyncio` with `async` services for database queries, LLM API calls, embedding generation. Non-blocking I/O allows handling multiple concurrent user requests without thread overhead.
- **Dependency injection**: FastAPI Depends() pattern for request authentication, database sessions, service layer instantiation. `get_current_user` validates JWT on protected routes, automatically rejects 401 on expired tokens.
- **Structured error handling**: Custom exception types (ValidationError, LLMError, NotFoundError) propagate to endpoint handlers, return standardized HTTP responses with descriptive messages.
- **Service layer abstraction**: 
  - `AIService`: Orchestrates LLM calls, handles retry/fallback, parses responses, applies guardrails
  - `FoodLogService`: CRUD operations for food logs, embedding generation, semantic cache queries
  - `KnowledgeService`: RAG search, KB entry seeding, user preference ranking
  - `EmbeddingService`: Text-to-vector conversion, similarity computation, batch operations

### Data Model (PostgreSQL + pgvector)
- **Extensible schema**: 
  - `users`: Authentication, timestamps
  - `user_profiles`: Personalization (cat style, macro targets, dietary restrictions, allergies)
  - `food_logs`: Core entity with pgvector column storing 384-dim food embeddings, `is_user_corrected` flag for tracking user feedback
  - `nutrition_kb`: Knowledge base entries (nutrition tips, category tags) with pgvector embeddings
- **Vector search**: `SELECT * FROM food_logs WHERE embedding <-> query_embedding < 0.15 LIMIT 5` for semantic cache hits.
- **Indexing strategy**: HNSW index on embedding columns for sub-millisecond vector search at scale.

### iOS Integration (SwiftUI)
- **Async/await on MainActor**: ViewModel uses `@MainActor` to ensure all UI updates happen on main thread. Async functions like `analyzePhoto()`, `saveLog()` run on background threads without blocking UI.
- **Image compression pipeline**: Before upload, compress photos from 2-4MB → 200-500KB via JPEG quality reduction (0.7) + resize to 800px max. Reduces upload time by 80%.
- **Photo caching**: In-memory cache (actor-based, thread-safe) stores downloaded thumbnails to avoid re-fetching same images multiple times in calendar view.
- **Error recovery**: Failed API calls show error banner with retry button. Retry logic uses exponential backoff. On 401 (expired token), automatically redirect to LoginView.

---

## Performance Optimization & Iteration

### Speed Optimizations (Claude Course Application)
- **Temperature tuning**: Used temperature=0 for deterministic food analysis (consistent results for same meal). Temperature=1 for meal suggestions to add variety.
- **Token reduction**: Optimized prompts to reduce input tokens by 30% through concise instructions, eliminating verbose rules, keeping only essential format examples.
- **Stop sequences**: For structured output, used stop sequence `"}"` to halt generation exactly at JSON close, eliminating trailing commentary.
- **Response streaming**: Streamed LLM responses to iOS for perceived 2-3x faster feedback (user sees text arriving immediately vs waiting 20s for complete response).

### Semantic Caching Impact
- **Baseline**: Food analysis (LLM API call): 15-30s latency, ~5k tokens (input+output), $0.015 per call
- **With cache**: 40% of requests hit cache, return in 0-50ms (pgvector latency), $0 API cost
- **Result**: Effective average latency reduced to ~18s, API costs cut to $0.009 per request (40% savings)

### Calendar & Food Diary Implementation
- **Newest-first sorting**: Implemented descending order (DESC) on `logged_at` timestamp so users see recent meals first (natural expectation).
- **Lazy evaluation**: Calendar view renders up to 4 months (120+ days) using LazyVGrid with in-memory pagination. No database query pagination needed.
- **Image thumbnail caching**: Actor-based PhotoCache stores downloaded images in memory, eliminating redundant API calls when calendar shows same photo multiple times.

---

## Testing, Evaluation & Code Quality

### Test Coverage
- **159+ unit tests**: Comprehensive coverage of LLM harness (retry logic, timeout, fallback, parser, guardrails), semantic cache (hit/miss scenarios), embedding service, auth, food log CRUD.
- **Integration tests**: End-to-end flow validation (photo upload → LLM analysis → save → retrieve list → delete).
- **Prompt evaluation framework**: Built custom eval pipeline inspired by Claude course. Generate test dataset of diverse foods → run each through prompt candidate → score outputs on nutritional accuracy + roast quality → average scores across dataset → A/B compare prompt versions.
- **Model-based grading**: Used Claude Sonnet to grade food analysis outputs (strengths/weaknesses/score). Enables systematic prompt improvement beyond manual testing.

### Code Quality Standards
- **Type hints throughout**: Python functions annotated with parameter types and return types. Enables early error detection and improved IDE autocomplete.
- **Linting & formatting**: Ruff for code style enforcement. All code passes `ruff check src/` + `ruff format src/` before commit.
- **No technical debt**: Aggressive deletion of unused code, imports, tests. Each commit is atomic and leaves codebase in working state.
- **Documentation**: Per-iteration PLAN.md, PHASES.md, BUGLOG.md tracking decisions and learnings. ARCHITECTURE.md diagrams system flows. Enables seamless handoffs and future development.

---

## Key Learnings & Technical Decisions

### From Claude "Built with Claude API" Course
1. **Multi-turn conversation management**: Learned to manually maintain message history and send complete context with each request (no stateful API session). Applied to food correction workflow.
2. **System prompts for behavior control**: Used parametrized system prompts to inject cat personality dynamically. System prompt structure: role assignment → behavioral rules → output format → examples.
3. **Structured data generation**: Used assistant message pre-filling + stop sequences to get clean JSON output without explanatory text.
4. **Prompt evaluation**: Built custom eval pipeline to measure prompt effectiveness objectively (not just manual testing). Tested multiple prompt variations on test dataset, compared scores.
5. **Model selection**: Applied intelligence/speed/cost tradeoff framework. Haiku for real-time analysis, Sonnet for accuracy-critical tasks, Opus only when reasoning is essential.
6. **Temperature control**: Low temperature for deterministic outputs (food analysis), high for creative outputs (meal suggestions).

### Design Decisions
- **Semantic caching over naive caching**: Exact-match cache (hash of photo) would miss similar meals. pgvector semantic search catches "pizza" + "margherita pizza" as same, enabling real deduplication.
- **Async/await architecture**: Production systems need to handle concurrent requests. Async from the start avoids refactoring for scale later.
- **RAG over fine-tuning**: Fine-tuning would require large labeled dataset. RAG enables dynamic KB updates without retraining.
- **iOS/Backend separation**: Never expose API keys to client. All LLM integration happens server-side. iOS only sends photos, receives analysis.

---

## Impact & Metrics

| Metric | Value | Impact |
|--------|-------|--------|
| API cost per food analysis (with cache) | $0.009 (vs $0.015 baseline) | 40% cost reduction |
| Semantic cache hit rate | ~40% typical user | Instant analysis for repeat meals |
| Food analysis latency (cache miss) | 15-30s | Acceptable for batch operation |
| Image upload size | 200-500 KB (vs 2-4 MB) | 80% reduction via compression |
| Test coverage | 159+ tests | Enables confident refactoring |
| Prompt evaluation framework | 10+ variations tested | Data-driven prompt optimization |

---

## Technologies & Tools

**LLM & AI**: Claude API (Opus, Sonnet, Haiku), sentence-transformers (embedding), pgvector (semantic search), Jinja2 (prompt templating)

**Backend**: Python 3.11, FastAPI, asyncio, SQLAlchemy, PostgreSQL, JWT auth, Pydantic validation

**iOS**: SwiftUI, async/await, Keychain (secure storage), URLSession, Codable (JSON serialization)

**DevOps**: Docker (local backend), Cloudflare tunnel (remote access), git (version control)

**Testing**: pytest (unit/integration), custom evaluation framework, model-based grading

**Observability**: Structured logging, request tracing, error alerts
