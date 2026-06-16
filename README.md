# NomNom — AI-Powered Food Tracking with Semantic Caching & RAG

**An intelligent food tracking application that uses Claude AI to analyze meals, provide personalized nutrition coaching, and learn user preferences through semantic caching and retrieval-augmented generation.**

Portfolio project showcasing full-stack AI engineering: production-grade architecture, empirical validation, transparent problem-solving.

---

## The Problem

Food tracking apps fail at the same core issues:

| Problem | Cost | Impact |
|---------|------|--------|
| **Redundant API calls** | "Salmon with rice" and "salmon & vegetables" each cost $0.12 | 85% of requests are variations; exact-match cache = 15% hit rate |
| **Generic advice** | System says "600 calories" without context | No insight into whether it's good/bad for this user's goals |
| **Slow analysis** | Photo analysis takes 60+ seconds | Users abandon the app mid-session |
| **No personalization** | Recommendations ignore allergies, goals, history | Advice feels irrelevant and untrusted |

NomNom solves this with three core innovations built on rigorous engineering.

---

## Solution: Three Core Innovations

### 1. Semantic Caching (pgvector) — Smart Matching, Not Exact

**The Problem:** Traditional caching (Redis) requires exact matches. Users don't eat identical meals twice.

**The Solution:** Embed meal photos, use pgvector cosine similarity with empirically tuned threshold (0.82).

```
User photograph → Extract embedding → Query pgvector (cosine > 0.82)
→ Find "salmon & vegetables" (cached 3 days ago) → Return instantly (<100ms)
→ NO API CALL MADE
```

**Key Insight:** Threshold of 0.82 was not arbitrary. Tested thresholds from 0.70 → 0.95 on 150+ real meal photos; 0.82 achieved 85% hit rate with <1% false positives. (See [detailed tuning process](docs/iterations/12-semantic-cache-production/PHASES.md))

**Result:** 85% cache hit rate, 60% cost reduction, instant responses for repeated meals.

---

### 2. Retrieval-Augmented Generation (RAG) — Context-Aware Recommendations

**The Problem:** "This meal has 600 calories" without context means nothing.

**The Solution:** Maintain searchable knowledge base of user's food history + health profile. Retrieve relevant context before generating advice.

**In Practice:**
```
User: "I've been gaining weight. What should I eat differently?"

System:
  ├─ Retrieve: 30-day food history + health profile
  ├─ RAG: Identify patterns
  │   └─ High-cal meals (pasta, avg 850 cal) vs. low-cal meals user rated 5/5 (grilled chicken, avg 450 cal)
  └─ Claude generates personalized analysis with specific swaps based on user's preferences
```

**Result:** Recommendations feel relevant because they're grounded in actual user data and constraints.

---

### 3. Intelligent Nutrition Coaching — Multi-Turn Agent with Context

**The Problem:** Nutrition advice requires follow-ups and clarifications. Single API call isn't enough.

**The Solution:** Maintain conversation history server-side. Claude asks follow-up questions, retrieves user data dynamically via tool use.

**Example:**
```
User: "I'm training for a marathon. Protein target?"
Coach: "120g/day for your 70kg weight + training schedule."

User: "I hate chicken. Alternatives?"
Coach: "You rated salmon 5/5, turkey 4/5. Both hit your target."

User: "Vegetarian options?"
Coach: "Tempeh + lentil bowl matches your target and you rated it 4/5 before."
```

**Result:** Multi-turn conversations maintain perfect context across 20+ exchanges. (See [conversation threading design](src/services/nutrition_chat_service.py))

---

## Key Achievements

### Performance & Cost

| Metric | Baseline | Optimized | Improvement |
|--------|----------|-----------|-------------|
| **Latency** | 60s | 25s | 67% faster |
| **Cache Hit Rate** | 15% (exact match) | 85% (semantic) | 5.7x better |
| **Daily API Cost** | $12/day (Opus) | $2/day (Sonnet + cache) | 83% savings |
| **Cost/Request (avg)** | $0.12 | $0.08 | 33% cheaper |

### Code Quality

- ✅ **100+ integration tests**, all passing
- ✅ **25+ bugs identified and fixed** through structured testing (see [BUGLOG examples](docs/iterations/*/BUGLOG.md))
- ✅ **Clean architecture:** API → Services → LLM with dependency injection
- ✅ **Production-ready:** error handling, monitoring, cost tracking

### Why These Numbers Matter

**Latency:** Not just micro-optimization. 60s → 25s is difference between "demo that impresses" and "product people use."

**Cache Hit Rate:** Semantic caching beats model upgrades. 85% hit rate is worth more than paying for Opus.

**Cost Journey:** Worth understanding because it shows *systems thinking*. We didn't just use a cheaper model; we combined cheaper model + better caching + faster response → exponential savings. (See [detailed cost analysis](docs/iterations/13-cost-and-latency/SUMMARY.md))

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     iOS App (SwiftUI)                       │
│  Camera → Diary → Insights → Nutrition Coach → Settings     │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS + JWT
┌────────────────────────▼────────────────────────────────────┐
│                  FastAPI Backend (Python)                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ API Layer (auth, photos, nutrition_chat, analytics) │   │
│  │ Services (ai_service, cache, RAG, knowledge)        │   │
│  │ LLM Orchestration (embeddings, workflows, agents)   │   │
│  └──────────────────┬──────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────┼──────────────────┐                   │
│  │                  │                  │                   │
│  ▼                  ▼                  ▼                   │
│ Claude API    PostgreSQL         pgvector              │
│ (Sonnet)      (Meals, Users)      (Embeddings)         │
│               + Knowledge Base                         │
│               + Chat History                           │
└─────────────────────────────────────────────────────────────┘
```

**Key Innovation:** Semantic caching layer between app and LLM prevents redundant Claude calls.

---

## How Problems Were Solved: Key Challenges

Three challenges demonstrate the engineering rigor behind this project:

### Challenge 1: Cache Hit Rate Plateau (40% → 85%)

**Problem:** Implemented semantic caching with threshold 0.95. Hit rate stuck at 40%—barely better than static cache.

**Root Cause:** Threshold too strict. "Salmon bowl," "salmon with rice," "salmon & vegetables" all have different embeddings despite similar nutrition.

**Solution:** 
- Tested thresholds 0.95 → 0.82 on 150 meal pairs
- Measured precision/recall at each point
- Added regression test: `test_semantic_cache_threshold_tuning`

**Result:** Hit rate jumped to 85% with <1% false positives.

**Learning:** Threshold tuning > infrastructure. Empirical data beats guesses.

---

### Challenge 2: Cost Spike After "Optimization"

**Problem:** Switched from Opus ($0.12/request) to Sonnet ($0.04/request). Expected cost $12 → $4. Got $10 instead.

**Root Cause:** Cheaper model → faster response → more user engagement → higher volume. Also slightly lower accuracy → more follow-up calls.

**Solution:** Accepted trade-off because:
- Per-request cost is fundamental (scales to millions of users)
- Added rate limiting + monitoring (daily cost alert)
- Semantic caching + Sonnet combo yields 83% final savings anyway

**Learning:** Can't optimize single variables in isolation. Volume, quality, and latency are coupled. The final system (Sonnet + 85% cache hit rate) costs $2/day vs. baseline $12/day.

---

### Challenge 3: Multi-Turn Chat Context Loss

**Problem:** Nutrition coach "forgot" user constraints. Re-asking about allergies even though user mentioned it 3 turns ago.

**Root Cause:** Only passing current message to Claude, not conversation history.

**Solution:**
- Implemented message threading: store full conversation history server-side
- Added lazy-loading: retrieve last N messages (tested N=10 as optimal)
- Dynamic context injection: Include user health profile in every request
- Regression test: `test_nutrition_coach_context_preservation_20_turns`

**Result:** Perfect context across 20+ turns. Token usage ~3.2K per request (acceptable).

---

## Design Decisions & Tradeoffs

| Decision | Why | Tradeoff |
|----------|-----|----------|
| **pgvector for caching** | Semantic similarity > exact match | Slightly higher latency on cache miss (~200ms embedding) |
| **Orchestrator-worker pattern** | Parallelize meal analysis, RAG, cost tracking | Slightly more complex debugging |
| **Sonnet over Opus** | 3x cheaper, still 96% accurate, 3x faster | 2% accuracy drop (immaterial for nutrition) |
| **Stateless API with server-side history** | Simplifies scaling, clear separation of concerns | Need careful invalidation strategy |

(See [detailed design explorations](docs/iterations/14-meal-recommendation-workflow/PHASES.md) for evaluation process)

---

## Technical Stack

### Backend
- **Framework:** FastAPI (Python 3.12+)
- **Database:** PostgreSQL 14+ with pgvector extension
- **LLM:** Anthropic Claude 3.5 Sonnet (with prompt caching)
- **Embeddings:** sentence-transformers (MiniLM-L6)
- **ORM:** SQLAlchemy with async support
- **Validation:** Pydantic v2 (structured output, guardrails)
- **Testing:** Pytest (100+ tests, unit/integration/E2E)

### Frontend
- **Language:** Swift with SwiftUI
- **Architecture:** MVVM with dependency injection
- **HTTP Client:** URLSession + Codable
- **Secure Storage:** iOS Keychain (JWT tokens)

### LLM Patterns
- **Orchestration:** Orchestrator-worker pattern (3 parallel workers)
- **Multi-turn:** Conversation history threading, tool use for context retrieval
- **Output Control:** Structured output validation, Pydantic guardrails
- **Caching:** Semantic (pgvector) + prompt caching (Anthropic native)

---

## Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL 14+ with pgvector extension
- Xcode 15+ (for iOS development)
- Claude API key from Anthropic

### Backend Setup
```bash
cd NomNom-Backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your Claude API key and PostgreSQL connection

# Run migrations
alembic upgrade head

# Start server
python src/run.py
# Server runs on http://localhost:8000
```

### iOS Setup
```bash
cd NomNom-iOS

# Install dependencies
pod install

# Open in Xcode
open NomNom.xcodeproj

# Build and run on simulator (Cmd+R)
```

### Running Tests
```bash
cd NomNom-Backend

pytest tests/                    # All tests
pytest tests/unit/llm/ -v       # Specific suite
pytest --cov=src tests/         # With coverage
ruff check src/ && ruff format src/  # Linting & formatting
```

---

## Project Structure

```
NomNom/
├── NomNom-Backend/
│   ├── src/
│   │   ├── api/              # REST endpoints
│   │   ├── services/         # Business logic (ai_service, cache, RAG)
│   │   ├── llm/              # LLM orchestration
│   │   │   ├── cache.py      # Semantic caching logic
│   │   │   ├── client.py     # Claude API wrapper with cost tracking
│   │   │   └── workflow/     # Orchestrator-worker pattern
│   │   ├── models/           # SQLAlchemy ORM
│   │   ├── schemas/          # Pydantic validation
│   │   └── config.py         # Settings & environment
│   ├── alembic/              # Database migrations
│   └── tests/                # Test suite (100+ tests)
│
├── NomNom-iOS/
│   ├── NomNom/
│   │   ├── Core/             # Shared models, services, components
│   │   └── Features/         # Feature modules (Camera, Diary, etc)
│   └── NomNomTests/          # Test suite
│
└── docs/
    ├── iterations/           # 20 tracked iterations (PLAN/PHASES/BUGLOG/SUMMARY)
    ├── learning/             # 7-phase learning journey documentation
    └── northstar/            # Architecture & feature planning
```

**For detailed navigation:** See [`.claude/rules/repo-navigation-quick-ref.md`](.claude/rules/repo-navigation-quick-ref.md)

---

## What I Learned About Production AI

After building NomNom through a 10-week LLM engineering curriculum:

1. **Semantic similarity beats exact matching** — For user-facing AI, capturing "similar enough" unlocks real economics.

2. **Prompts are product assets** — They change 10x more frequently than code. Version and test them.

3. **Output validation is non-negotiable** — 30% of LLM bugs come from parsing/schema mismatches, not hallucinations.

4. **Architecture decisions > model upgrades** — Sonnet + semantic caching beats paying 3x for Opus.

5. **Measure holistically** — Cost + latency + quality are coupled. Optimizing one variable in isolation backfires.

6. **Transparent about challenges** — The problems we overcame (threshold tuning, cost spike, context loss) are more informative than the final results.

(See [Phase 6 retrospective](docs/learning/03_phase_retrospectives/phase_6_retro.md) for full learning journey)

---

## Features & Status

| Feature | Status | Tech |
|---------|--------|------|
| Photo-to-analysis with semantic caching | ✅ Complete | Claude vision, pgvector |
| Multi-period analytics (daily/weekly/monthly) | ✅ Complete | FastAPI, SQLAlchemy |
| Personalized health profile (TDEE, macros) | ✅ Complete | Mifflin-St Jeor calculations |
| Nutrition Coach chatbot | ✅ Complete | Multi-turn agent, tool use |
| Meal recommendations with RAG | ✅ Complete | Orchestrator-worker pattern |
| Semantic caching with empirical tuning | ✅ Complete | pgvector, 0.82 threshold |
| Chat history & context preservation | ✅ Complete | Message threading |
| Production monitoring & cost tracking | ✅ Complete | Logging, alerts |

---

## What Makes This Real

This is a **portfolio project** that demonstrates genuine engineering rigor:

✅ **Production-grade architecture** — Not toy code; handles caching, concurrency, error recovery  
✅ **Empirical validation** — Threshold tuning, A/B evaluation, regression testing  
✅ **Transparent challenges** — Problems + root causes + solutions documented (see [BUGLOG examples](docs/iterations/*/BUGLOG.md))  
✅ **Quantified results** — Specific metrics (85% cache hit, 67% latency reduction, 83% cost savings)  
✅ **Learning journey documented** — 7-phase curriculum with reflections (see [learning docs](docs/learning/))  
✅ **Code quality** — 100+ tests, clean architecture, comprehensive documentation  

---

## Interview Discussion Points

- "Walk me through your semantic caching threshold tuning process"
- "Why did costs spike after switching to Sonnet? How did you diagnose it?"
- "Tell me about a time when local optimization broke something else"
- "How would you scale this to 1 million users?"
- "What surprised you most about LLM engineering?"

---

## For Deeper Dives

| Topic | Read This |
|-------|-----------|
| Full project overview | [CLAUDE.md](CLAUDE.md) |
| Semantic caching implementation | [docs/iterations/12-semantic-cache-production/](docs/iterations/12-semantic-cache-production/) |
| Cost optimization journey | [docs/iterations/13-cost-and-latency/](docs/iterations/13-cost-and-latency/) |
| Meal recommendation workflow | [docs/iterations/14-meal-recommendation-workflow/](docs/iterations/14-meal-recommendation-workflow/) |
| Nutrition coach chatbot | [docs/iterations/20-nutrition-coach-chatbot/](docs/iterations/20-nutrition-coach-chatbot/) |
| Full learning curriculum | [docs/learning/00_roadmap/](docs/learning/00_roadmap/) |
| Bug tracking & solutions | [docs/iterations/*/BUGLOG.md](docs/iterations/) |

---

## Security & Data Privacy

- **Authentication:** JWT tokens; stored in iOS Keychain with encryption
- **Data Transit:** TLS encryption for all requests
- **Data at Rest:** PostgreSQL encrypted backups, role-based access
- **User Deletions:** Food logs deleted on user deletion (GDPR-compliant)
- **Photo Storage:** Local on device first; uploaded with user consent
- **Sensitive Fields:** Health profile encrypted at application level (AES-256)

---

**Last Updated:** June 16, 2026  
**Status:** Core features complete, production-ready, actively iterating (Iteration 20 in progress)  
**Next Phase:** iOS App Store launch and feedback-driven improvements

