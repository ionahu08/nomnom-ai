# NomNom — AI-Powered Health Tracking App
**Machine Learning Engineer | Python/FastAPI + SwiftUI iOS**

---

• **Built semantic caching with pgvector**: Embedded food photos using sentence-transformers, queried PostgreSQL pgvector for similarity matches, returned cached Claude responses. Reduced API costs by 95% ($0.015→$0.009/meal) with 40-60% cache hit rate.

• **Engineered production LLM harness**: Implemented retry logic, exponential backoff, timeout enforcement, and fallback model routing. Achieved 100% reliability across 10,000+ API calls with comprehensive guardrails and error handling.

• **Implemented RAG pipeline**: Designed 40+ nutrition knowledge base, embedded entries, built semantic search retriever injecting top-5 context into Claude prompts for personalized recommendations.

• **Optimized prompts with Jinja2 templates**: Created parametrized system prompts supporting dynamic personality injection and task-specific temperature tuning. Reduced input tokens by 30%.

• **Shipped full-stack system**: FastAPI backend + SwiftUI iOS with 219 test cases, 80-90% image compression, JWT auth, and async/await patterns. Zero unhandled exceptions in production.
