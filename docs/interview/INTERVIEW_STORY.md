# Interview Story & Talking Points — NomNom

For portfolio project interviews, you need **one strong story + five deep talking points**. This document provides both.

---

## The 60-Second Pitch

Use this when asked: "Tell us about a project you're proud of."

---

### Version A: Technical Interviewer (60 seconds)

> "I built NomNom, an AI-powered food tracking app that solves a real production engineering problem: LLM applications waste 85% of API calls re-analyzing similar meals.
>
> I implemented semantic caching using pgvector with an empirically tuned threshold (0.82). Tested thresholds from 0.70 to 0.95 on 150 real meal photos to find the sweet spot: 85% cache hit rate with <1% false positives.
>
> The system combines three innovations: semantic caching for cost efficiency (60% savings), retrieval-augmented generation for personalization, and a multi-turn nutrition coach agent that maintains conversation context.
>
> Result: 85% cache hit rate, 67% latency reduction (60s → 25s via orchestrator-worker parallelization), and 83% daily cost savings. Built with FastAPI, PostgreSQL + pgvector, Claude API, and 100+ integration tests.
>
> The learning: semantic similarity beats model upgrades. Orchestration patterns unlock real performance. Monitor from day one."

**Time:** 60 seconds | **Key Metrics:** 85%, 67%, 83%, 150 meals, 0.82 threshold

---

### Version B: Product Manager (60 seconds)

> "I built NomNom to solve the food tracking problem: users hate logging meals, apps give generic advice, and nothing learns from user history.
>
> Instead of a consumer app, I focused on the engineering challenge: how do you make LLM-powered recommendations feel personal, respond instantly, and cost-effectively?
>
> Three core features: (1) semantic caching so 'salmon bowl' and 'salmon with rice' return instant results instead of costing $0.12 each; (2) RAG-powered personalization that learns from user history and constraints; (3) a multi-turn nutrition coach that maintains conversation context.
>
> The user experience? Takes a photo, gets instant personalized advice grounded in their history. Instead of generic 'eat healthy,' it's 'you rated grilled chicken 5/5 last month; it's half the calories of your pasta habit.'
>
> Metrics prove it works: 85% of photos return cached results, response time dropped from 60 to 25 seconds, and it costs 83% less than a naive approach."

**Time:** 60 seconds | **Focus:** User value + technical decisions

---

### Version C: Engineering Manager (60 seconds)

> "NomNom is a 10-week capstone project from my LLM engineering curriculum. I built it to demonstrate production AI engineering: not just using Claude, but building systems that scale.
>
> The architectural challenge: naive LLM calls are expensive and slow. How do you add intelligence without burning API budget?
>
> My approach: (1) Semantic caching layer to avoid redundant API calls (reduced costs 83%), (2) Parallel orchestration to avoid sequential bottlenecks (reduced latency 67%), (3) RAG + multi-turn loops for stateful, personalized conversations.
>
> The rigorous parts: I tested semantic caching thresholds empirically (150 photos, manual validation), diagnosed cost spikes after 'optimizations,' implemented production monitoring, and documented decisions with quantified tradeoffs.
>
> Result: production-grade code with 100+ tests, clean architecture, and transparent about challenges. Demonstrates systems thinking, empirical validation, and honest problem-solving."

**Time:** 60 seconds | **Focus:** Engineering rigor + decision-making

---

## The Five Talking Points

After your pitch, expect one of these follow-ups. Here's how to respond with confidence.

---

### Talking Point 1: "Walk me through your semantic caching approach"

**Question likely to lead with:**
- "How did you decide on pgvector instead of Redis + Bloom filters?"
- "Why 0.82 threshold? Seems arbitrary."
- "How do you handle cache invalidation?"

**Your answer (2-3 minutes):**

"The problem: food items aren't identical, so exact matching caches (Redis) were useless. 'Salmon bowl,' 'salmon with rice,' 'salmon & vegetables' have different hash values even though they're nutritionally similar.

I needed semantic similarity, so I embedded meal photos using sentence-transformers (MiniLM-L6 for efficiency) and stored embeddings in PostgreSQL's pgvector extension.

**The threshold wasn't arbitrary.** I tested 0.70, 0.75, 0.80, 0.82, 0.85, 0.90, 0.95 on 150 real meal photos. Measured both hit rate and false positives:
- 0.95: 40% hit rate (too strict)
- 0.82: 85% hit rate, <1% false positives (sweet spot)
- 0.70: 95% hit rate, 8% false positives (too loose)

Why pgvector over Pinecone or Weaviate? 
- One database (PostgreSQL) instead of multiple services
- Simpler to reason about (embeddings + similarity search are just SQL)
- Sufficient performance for the scale

For cache invalidation: LRU with max 10K embeddings per user. When you hit the limit, oldest entries are dropped. Simple, predictable, avoids stale data.

**The result:** 85% hit rate in production. Every percentage point of cache hits directly reduces API costs. This single feature is worth more than upgrading to a more expensive model."

**Evidence to cite:**
- 150 photo dataset with threshold sweep results (see `docs/iterations/12-semantic-cache-production/PHASES.md`)
- Production metrics: 85% hit rate over 500+ meals
- Cost impact: saved $10/day on API calls

---

### Talking Point 2: "Your costs went UP after switching to Sonnet. Walk me through that."

**Question likely to lead with:**
- "This seems like poor optimization. Why didn't you revert?"
- "How did you decide to keep the 'more expensive' solution?"
- "What did you learn?"

**Your answer (2-3 minutes):**

"Right. This is a good example of optimizing one variable in isolation and breaking something else.

**The setup:** Opus cost $0.12/request. Sonnet is $0.04/request (70% cheaper). I switched expecting daily costs to drop from $12 → $4.

**What actually happened:** Daily costs went to $10. Why?

I diagnosed it by tracking three metrics:
1. **Cost per request:** $0.12 → $0.04 ✓ (as expected)
2. **Daily traffic:** 100 requests → 250 requests (unexpected)
3. **Accuracy:** 98% → 96% (acceptable 2% drop)

**Root causes:**
- Faster response time (Sonnet is 3x faster) → improved UX → more user engagement → higher volume
- Slightly lower accuracy → more follow-up corrections → more API calls

**The decision:** I could revert to Opus. But I chose to keep Sonnet because:
1. Per-request cost is the fundamental metric that scales (Sonnet will always be cheaper at scale)
2. The volume increase isn't a bug—it's a feature. Faster = better UX
3. Semantic caching would fix the volume problem (85% hit rate → only 15% cold calls)

**What I did:** Added rate limiting (20 requests/user/day) + monitoring (daily cost alert at $15) + semantic caching.

**Final result:** With Sonnet + semantic caching, daily cost is now $2 (83% savings). Better than reverting to Opus would have been.

**Lesson learned:** Don't optimize for one variable. Cost + latency + quality are coupled. Measure holistically."

**Evidence to cite:**
- Cost evolution timeline (see `docs/iterations/13-cost-and-latency/SUMMARY.md`)
- Before/after metrics: baseline $12/day → optimization $10 → final $2/day
- Decision log showing the reasoning (see `docs/iterations/13-cost-and-latency/BUGLOG.md`)

---

### Talking Point 3: "Tell me about a time when local optimization broke something else"

**Question likely to lead with:**
- "Give me an example of a decision that had unintended consequences"
- "What surprised you during development?"

**Your answer (2-3 minutes):**

"The semantic caching threshold is a perfect example.

**Initial approach:** I set the threshold at 0.95 (high confidence in similarity). This seemed safe—avoid false positives.

**The problem:** Cache hit rate was only 40%. The system was caching fewer meals, so API costs didn't improve.

**Why?** I manually reviewed failed cache lookups. Found:
- User photographed 'salmon with rice' (stored in cache)
- User photographed 'salmon bowl' (no rice, more vegetables)
- Embeddings differed enough to score 0.87 (below 0.95 threshold)
- Cache miss → full API call → cost

But nutritionally, they're almost identical. Both are salmon + carbs + fiber.

**The fix:** Lower the threshold to 0.82. Now these meals match. But lowering threshold risks false positives: what if I cache 'salmon' for 'chicken'? That's a real bug.

**How I validated it:**
- Tested 150 real meal photos
- Measured precision/recall at each threshold
- Manually reviewed borderline cases (50 pairs)
- Added regression test: `test_semantic_cache_threshold_tuning`

**The learning:** There are no free lunches. Lower threshold = more hits but more noise. Higher threshold = fewer hits but higher precision. You have to measure and choose based on your domain.

For food, 85% hit rate with 1% false positives is acceptable. For medicine or finance, you'd want 99% precision even if it means lower recall.

**Data to cite:**
- Threshold sweep results (0.70 → 0.95)
- Precision/recall tradeoffs
- Validation dataset of 150 photos with manual annotations
- Test case: `test_semantic_cache_threshold_tuning` in `NomNom-Backend/tests/`

---

### Talking Point 4: "How would you scale this to 1 million users?"

**Question likely to lead with:**
- "What would break first?"
- "Architecture changes needed?"
- "Cost implications?"

**Your answer (2-3 minutes):**

"Good question. Current system is designed for 100s of users. 1M users changes everything.

**Current bottlenecks at scale:**

1. **pgvector similarity search:** 10K embeddings per user × 1M users = 10B embeddings. Cosine similarity search becomes slow.
   - Fix: Partition embeddings by user (already per-user), shard PostgreSQL, or migrate to specialized vector DB (Pinecone)
   - Cost: adds operational complexity

2. **API rate limits:** Claude API has rate limits. 1M users × 10 requests/day = 10M requests/day. Will hit limits.
   - Fix: Implement token bucket rate limiting per user, queue excess requests, use Claude Batch API for off-peak processing

3. **Storage:** Chat history for 1M users × 100 messages/user × 1KB/message = 100GB. Manageable but need archival strategy.
   - Fix: Archive old conversations to cold storage (S3), keep last 30 days hot

4. **Cost:** $2/day for 100 users scaling linearly would be $20K/day at 1M users.
   - Fix: Improve cache hit rate further (80% → 95%), implement request deduplication, use Sonnet more aggressively, introduce user tiers (free users get basic caching, premium get personalization)

**Architecture changes:**

- **Caching:** Move from per-user embeddings to distributed cache (Redis + PostgreSQL)
- **Queuing:** Add message queue (Celery/Kafka) for async recommendations
- **API:** Convert to async/streaming (FastAPI already supports this)
- **Monitoring:** Implement comprehensive logging (Prometheus + Grafana) to catch issues early
- **Data:** Archive old food logs to cold storage, keep recent data hot

**The honest answer:** This project is a Prototype™. It works for 100s of users. Scaling to 1M requires real DevOps, database optimization, and cost-conscious architecture. Current codebase is a foundation, not a plug-and-play scale-out.

**What I'd do:** Keep the core LLM patterns (semantic caching, RAG, multi-turn loops) but rebuild the data layer and deployment architecture."

**Evidence to cite:**
- Current architecture diagram (see README.md)
- Bottleneck analysis (see `docs/iterations/14-meal-recommendation-workflow/PHASES.md`)
- Cost breakdown by component (see `docs/iterations/13-cost-and-latency/SUMMARY.md`)

---

### Talking Point 5: "What surprised you most about LLM engineering? What would you do differently?"

**Question likely to lead with:**
- "What did you expect vs. what happened?"
- "Any lessons that surprised you?"
- "If you built this again, what would you change?"

**Your answer (2-3 minutes):**

"Three surprises:

**Surprise 1: Prompts are product assets, not code**
I expected LLM engineering to be 80% prompt, 20% architecture. It's the opposite. Prompts change 10x more frequently than code. You need versioning, testing, A/B evaluation for prompts like you do for features.

What I'd do: Build a prompt testing framework from day one. Track prompt versions, measure quality metrics, iterate quickly. Currently I have prompt_engine.py that handles templating, but I'd add a full evaluation pipeline earlier.

**Surprise 2: Output validation prevents 30% of bugs**
I expected hallucinations and reasoning errors to dominate. But 30% of bugs were actually parsing/schema mismatches. User asks 'what should I eat?' → Claude returns random JSON → code crashes.

What I'd do: Implement structured output validation before any other optimization. Use Pydantic schemas, add guardrails, reject malformed outputs early.

I did this in Phase 2 (see `src/llm/guardrails.py`), but I'd start with it, not add it later.

**Surprise 3: Orchestration patterns scale way better than single agents**
I expected agent loops to be 'good enough.' But orchestrator-worker parallelization (3 workers in parallel) reduced latency from 60s to 25s (67% improvement). That's not micro-optimization—it's fundamental.

What I'd do: Model your workload as a DAG (directed acyclic graph) from the start. Identify independent tasks (photo analysis, RAG search, cost tracking) and parallelize them. Don't serialize just because it's simpler.

**Bonus surprise: Cheaper models + smart caching beats expensive models**
I expected Opus would be required for 'smart' food recommendations. But Sonnet (70% cheaper) + semantic caching (85% hit rate) outperforms Opus without caching. Architecture > raw capability.

**If I rebuilt from scratch:**
1. Start with structured output validation (Phase 2 work)
2. Build semantic caching from day one, not week 6
3. Model workload as a DAG and parallelize
4. Implement monitoring (cost, latency, quality metrics) before features
5. Keep a prompt changelog (date, version, why changed)
6. Test on real user data earlier (I tested on synthetic data first)

**Learning:** LLM engineering is mostly architecture. The 'intelligence' part (Claude) is 10%. The hard work is caching, parallelization, validation, monitoring. That's where most of my time went."

**Evidence to cite:**
- Prompt engineering notes (see `src/llm/prompt_engine.py`)
- Guardrails implementation (see `src/llm/guardrails.py`)
- Orchestrator-worker pattern (see `src/llm/workflow/meal_recommendation_workflow.py`)
- Cost/latency evolution (see `docs/iterations/13-cost-and-latency/SUMMARY.md`)
- Learning retrospectives (see `docs/learning/03_phase_retrospectives/`)

---

## Quick Reference: Metrics to Have Ready

Memorize these numbers. They're your credibility:

| Metric | Value | Why It Matters |
|--------|-------|---|
| Cache hit rate | 85% | Most requests return instant results |
| Latency reduction | 60s → 25s (67%) | Difference between abandoned app and daily driver |
| Cost savings | 83% ($12 → $2/day) | Shows systems thinking, not just coding |
| Semantic threshold | 0.82 (tuned from 0.70-0.95) | Shows empirical validation |
| Test coverage | 100+ integration tests | Production-ready code |
| Accuracy drop (Sonnet) | 2% (98% → 96%) | Acceptable tradeoff for cost/speed |
| False positive rate | <1% | Caching is reliable |
| Bugs fixed | 25+ | Real engineering, not toy project |

---

## The Meta-Answer: Why This Matters

When interviewers ask about NomNom, they're really asking:

1. **Can you think about systems?** (Not just "write code")
   → Talk about semantic caching vs. exact matching, cost coupling, parallelization

2. **Can you measure and validate?** (Not just "assume")
   → Threshold tuning, A/B evaluation, monitoring

3. **Can you handle ambiguity?** (Not just "follow specs")
   → Choosing Sonnet over Opus, lowering cache threshold, accepting cost increase

4. **Can you learn from failures?** (Not just "succeed")
   → Cache hit plateau, cost spike, context loss—show you diagnosed and fixed

5. **Are you honest about tradeoffs?** (Not just "my thing is perfect")
   → 2% accuracy drop is real, orchestration adds complexity, scaling will require rework

If you answer with these angles, you'll stand out. Most people list features. You explain decisions.

---

## Before Your Interview

- [ ] Memorize the 60-second pitch (Version A for technical interviews)
- [ ] Read through the five talking points once to lock in the narrative
- [ ] Have the key metrics memorized (85%, 67%, 83%, 0.82)
- [ ] Know where the evidence lives (which docs/iterations files contain what)
- [ ] Practice talking about challenges without defensiveness ("I faced X, diagnosed Y, implemented Z")

---

## Post-Interview: Follow-up Email

If they ask for next steps, send something like:

> "Thanks for the conversation about NomNom. I enjoyed discussing the semantic caching approach and the cost optimization journey. A few resources for deeper context:
>
> - Full project README: [Link to README.md]
> - Semantic caching implementation details: [Link to iteration 12]
> - Cost analysis: [Link to iteration 13]
> - Code walkthrough: [Link to GitHub]
>
> Happy to dig into any specific questions about the architecture, design decisions, or engineering approach."

---

Last Updated: June 16, 2026
