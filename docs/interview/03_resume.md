# Resume — NomNom Project

## Food Analysis & Health Tracking App with Multimodal AI Agents

**Duration:** March 2026 – Present  
**Repository:** [https://github.com/ionahu08/nomnom-ai](https://github.com/ionahu08/nomnom-ai)

---

## Project Description

### Core Achievements

• Built an AI-powered food tracking app that analyzes meal photos using multimodal AI to estimate nutrition and generate personalized diet recommendations, with an interactive **nutrition coach agent** that refines suggestions based on user constraints.

• Architected full-stack system (FastAPI + SwiftUI) with **model routing** (Haiku/Sonnet by task) and **agentic orchestration** (tool use, retry, fallback), achieving **15–30s latency** and **4.3x cost reduction** ($12 → $2.80/user/day).

• Engineered production LLM harness & prompt system using prompt templating, **structured outputs**, and **guardrails** (validation + retry), achieving **100% success rate** on 10K+ API calls and eliminating parsing failures.

• Built **semantic caching system** using pgvector embeddings and **hybrid search** (RAG + BM25), achieving **85% cache hit rate** through empirically-tuned similarity threshold (0.82, tested on 150 real meals).

---

## Key Skills

**Top 5 Skills:**
1. LLM Harness Engineering
2. Agentic Workflows
3. Full-Stack Development
4. Retrieval-Augmented Generation (RAG)
5. Prompt Engineering

---

## Impact Metrics

| Metric | Result | Impact |
|--------|--------|--------|
| **Latency** | 60s → 15–30s | 67% faster response time |
| **Cost Reduction** | $12 → $2.80/user/day | 4.3x cheaper per user |
| **Cache Hit Rate** | 85% | Reduced API calls by 5.7x |
| **System Reliability** | 100% success rate | Zero parsing failures on 10K+ calls |
| **Empirical Validation** | 0.82 threshold | Tested on 150 real meals |

---

## Technical Stack

**Backend:**
- FastAPI (Python 3.12+)
- PostgreSQL 14+ with pgvector extension
- Claude API (Sonnet/Haiku with model routing)
- SQLAlchemy with async support

**Frontend:**
- SwiftUI (iOS)
- MVVM architecture with dependency injection

**LLM Patterns:**
- Orchestrator-worker pattern (parallel processing)
- Model routing (task-based selection)
- Semantic caching (pgvector embeddings)
- Structured output validation
- Tool use for agentic workflows

---

## Key Learnings

1. **Architecture beats raw capability** — Sonnet + semantic caching outperforms Opus alone at 70% lower cost
2. **Measurement validates assumptions** — 0.82 threshold tested on real data proved more effective than theoretical 0.95
3. **System design is the real constraint** — 97% of failures were JSON parsing (system), not hallucination (model)
4. **Production LLM reliability requires layered guardrails** — Validation + retry + structured outputs = 100% success
5. **Empirical tuning matters** — Threshold tuning on 150 real meals captured edge cases that generic approaches miss

---

## Interview Discussion Points

- "Walk me through your semantic caching threshold tuning process"
- "Why did you choose model routing over a single model?"
- "How did you achieve 100% success rate on 10K+ API calls?"
- "Tell me about your orchestrator-worker pattern implementation"
- "What surprised you most about LLM system design?"

---

**Last Updated:** June 18, 2026  
**Status:** Production-ready, actively iterating
