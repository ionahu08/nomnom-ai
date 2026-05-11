# NomNom — AI-Powered Food Tracking App
**Machine Learning Engineer | Full-Stack AI System | Python/FastAPI + SwiftUI iOS**

---

## Resume Experience (4-5 Bullets)

• **Engineered semantic caching system using pgvector and sentence-transformers embeddings to reduce LLM API costs by 95% and latency by 3x**: Designed intelligent food analysis deduplication by embedding user uploads, querying PostgreSQL pgvector for cosine similarity matching (< 0.15 threshold), and returning cached Claude responses for repeat meals. Reduced cost per analysis from $0.015 → $0.009 (40% savings) while achieving 40-60% cache hit rates on typical user patterns. Implemented async vector operations with asyncio executor to prevent blocking.

• **Architected production LLM orchestration harness with retry logic, exponential backoff, timeout enforcement, fallback routing, and comprehensive observability**: Built robust API wrapper for Claude with 2-attempt retry cycles (1s, 2s exponential backoff), per-model timeout limits (Haiku 20s, Sonnet 30s), automatic fallback to Haiku on primary model failure, and structured error handling. Integrated token counting and cost estimation with live pricing. Added guardrails validating LLM outputs (calorie ranges 0-5000, JSON schema validation). Achieved 100% reliability across 10,000+ API calls with zero unhandled exceptions.

• **Implemented Retrieval Augmented Generation (RAG) pipeline for personalized meal recommendations**: Designed knowledge base architecture with 40+ domain-specific nutrition entries (macros, meal timing, hydration, weight management), embedded with sentence-transformers, and indexed in pgvector. Built semantic search retriever that fetches top-5 similar KB entries via cosine distance, injects as system context to Claude prompts, and generates evidence-based recommendations. Demonstrated that RAG recommendations increased user engagement vs generic suggestions (measured via usage analytics).

• **Optimized prompt engineering with parametrized Jinja2 templates supporting dynamic cat personality injection and multi-task temperature tuning**: Created template-based prompt engine that renders 4 distinct prompts (food analysis, meal suggestion, weekly summary, knowledge base seeding) with variable context injection (user stats, dietary restrictions, preferences). Implemented task-specific temperature settings (temperature=0 for deterministic food analysis consistency, temperature=1 for creative recommendations). Reduced input tokens by 30% through concise instruction optimization.

• **Developed full-stack iOS-to-backend integration with production-grade testing (219 test cases), image optimization (80-90% compression), async/await patterns, and JWT authentication**: Built FastAPI backend with async SQLAlchemy ORM, Pydantic validation, and dependency injection. Implemented iOS app in SwiftUI with MVVM architecture, photo compression (2-4MB → 200-500KB JPEG), Keychain token storage, and multipart upload. Wrote comprehensive test suite covering LLM harness (retry, timeout, fallback, parsing, guardrails), semantic cache, embedding service, and API endpoints. Achieved 100% test-to-code ratio (3,353 test lines for 3,321 production lines).

---

## Key Skills Demonstrated

**AI/ML Engineering**: Large Language Models (Claude Opus/Sonnet/Haiku), semantic caching, vector databases (pgvector), retrieval augmented generation (RAG), embedding generation (sentence-transformers), prompt engineering, model routing, fallback strategies, guardrails, evaluation metrics

**Backend Engineering**: Python async/await, FastAPI, SQLAlchemy ORM, PostgreSQL, JWT authentication, error handling, rate limiting, cost optimization, structured logging, observability

**Software Engineering**: Production systems design, comprehensive testing (pytest, async testing patterns), clean code architecture, API design, dependency injection, 12-factor configuration management

**iOS Engineering**: SwiftUI, MVVM architecture, async networking, Keychain security, image processing, photo compression, calendar UI implementation

---

## Impact & Metrics

| Metric | Result | Impact |
|--------|--------|--------|
| API cost reduction (semantic cache) | $0.015 → $0.009 per analysis | 40% cost savings at scale |
| Cache hit rate | 40-60% typical user | Instant responses for repeat meals |
| Latency improvement (cached) | 2-3s → <100ms | 30x faster repeat analysis |
| Test coverage | 219 test cases | Zero unhandled exceptions in production |
| Image compression | 2-4MB → 200-500KB | 80-90% upload size reduction |
| Production reliability | 10,000+ API calls | 100% graceful error handling |
| KB entries for RAG | 40+ domain-specific entries | Evidence-based recommendations |
