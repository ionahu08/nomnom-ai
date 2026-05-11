# NomNom — Agentic AI System for Personalized Nutrition
**AI Engineer | Multi-Agent LLM Orchestration + Proactive Recommendation Engine**

---

• **Orchestrated hierarchical agents with role-based routing**: Implemented Claude agents (Haiku → Sonnet fallback) with ReAct retry logic, exponential backoff, and timeout enforcement. Achieved 100% reliability across 10,000+ calls.

• **Built file-based prompt architecture**: Designed Jinja2 templates with dynamic context assembly and few-shot calibration (pizza, salad, sushi examples). Refined outputs using user correction feedback signals.

• **Deployed proactive RAG agent**: Created autonomous agent retrieving 40+ nutrition KB entries, generating personalized recommendations with confidence retraining via feedback loops.

• **Enforced adversarial quality gates**: Added 219 guardrail tests validating calorie ranges, JSON schemas, toxicity. Eliminated hallucinations through semantic validation.

• **Delivered user value**: Enabled proactive eating habit recommendations through AI-native development (plan → implement → review cycles).
