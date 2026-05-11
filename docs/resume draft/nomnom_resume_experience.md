# NomNom — AI-Powered Food Tracking App

**Full-Stack AI Engineer | Python/FastAPI + SwiftUI iOS | Claude API**

• **LLM Orchestration & Multi-Model Routing**: Implemented intelligent model selection (Claude Opus/Sonnet/Haiku) with retry logic, exponential backoff, and automatic fallback. Built Jinja2 prompt templating engine with parametrized system prompts that adapt tone based on user preferences. Integrated streaming responses for real-time feedback and structured JSON output with validation guardrails.

• **Semantic Caching with pgvector**: Implemented vector embedding-based deduplication using sentence-transformers (384-dim) and PostgreSQL pgvector extension. Semantic cache hit rate ~40%, reducing Claude API calls by 40% ($0.015 → $0.009 per request) while maintaining sub-50ms latency on cache hits vs 15-30s on misses.

• **Retrieval Augmented Generation (RAG)**: Built knowledge base search system that retrieves top-5 nutrition tips via pgvector similarity search and injects as context to Claude prompts. Personalized meal recommendations grounded in domain-specific knowledge base rather than generic outputs.

• **Full-Stack Production Architecture**: Async/await FastAPI backend with JWT auth, SQLAlchemy ORM, and service layer abstraction. Comprehensive error handling (retry/fallback/timeout), structured logging, and 159+ unit tests. SwiftUI iOS app with image compression (2-4MB → 200-500KB), in-memory photo caching, and MainActor concurrency patterns.

• **Applied Claude API Course Techniques**: Multi-turn conversation management, system prompts for behavior control, structured data generation with stop sequences, prompt evaluation framework with model-based grading, and temperature control (low=deterministic, high=creative).
