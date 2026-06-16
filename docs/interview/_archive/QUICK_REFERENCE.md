# NomNom Interview Cheat Sheet
**Print this. Memorize the 60-second pitch and 8 metrics. Reference during interview prep.**

---

## 60-Second Pitch (Say This First)

> "I built NomNom, an AI food tracking app that solves a production LLM problem: re-analyzing similar meals wastes 85% of API calls.
>
> I implemented semantic caching using pgvector with a tuned threshold (0.82), achieving **85% cache hit rate** and **60% cost reduction**. The system combines three innovations: semantic caching for efficiency, RAG for personalization, and a multi-turn nutrition coach with context.
>
> Result: **67% latency reduction** (60s → 25s), **85% cache hit rate**, and **83% daily cost savings** ($12 → $2/day). Built with FastAPI, PostgreSQL + pgvector, Claude API, and 100+ tests."

**Time:** 60 seconds | **Tone:** Confident, specific, metrics-driven

---

## Memorize These 8 Numbers

| Metric | Value | Why It Matters |
|--------|-------|---|
| 🚀 **Cache Hit Rate** | **85%** | Most requests return instant results |
| ⚡ **Latency Reduction** | **67%** (60s → 25s) | Difference between abandoned & daily driver |
| 💰 **Cost Savings** | **83%** ($12 → $2/day) | Systems thinking, not just coding |
| 🎯 **Semantic Threshold** | **0.82** | Empirically tuned (0.70–0.95 tested) |
| 📸 **Meal Dataset** | **150 photos** | Validation sample size |
| ✅ **Integration Tests** | **100+** | Production-ready code |
| 📉 **Accuracy Drop (Sonnet)** | **2%** (98% → 96%) | Acceptable for speed/cost |
| ❌ **False Positive Rate** | **<1%** | Caching is reliable |

**Practice:** Recite these three times without looking. Then do it in your sleep.

---

## 5 Talking Points (Quick Version)

### 1️⃣ Semantic Caching (If asked: "Explain your caching approach")
- **Problem:** Exact match cache (Redis) = 15% hit rate. Useless.
- **Solution:** pgvector similarity search (threshold 0.82)
- **Why 0.82?** Tested 0.70–0.95 on 150 meals; 0.82 = 85% hit rate + <1% false positives
- **Result:** 85% hit rate, 60% cost reduction
- **Proof:** See `docs/iterations/12-semantic-cache-production/PHASES.md`

### 2️⃣ Cost Spike (If asked: "Your costs went UP after optimizing?")
- **Expected:** $12/day → $4/day (switch Opus to Sonnet)
- **Reality:** $12/day → $10/day (why?)
- **Root cause:** Faster response → more user engagement → higher volume
- **Decision:** Keep Sonnet + add semantic caching (final: $2/day, 83% savings)
- **Lesson:** Cost + latency + quality are coupled; optimize holistically
- **Proof:** See `docs/iterations/13-cost-and-latency/SUMMARY.md`

### 3️⃣ Local Optimization Backfires (If asked: "When did optimization break something?")
- **Initial approach:** Cache threshold 0.95 (safe, strict)
- **Problem:** 40% hit rate (doesn't work)
- **Why?** "Salmon bowl" and "salmon with rice" have different embeddings (score 0.87)
- **Fix:** Lower to 0.82, validate on 150 photos + manual review
- **Tradeoff:** Slightly accept false positives (~1%) to get real benefit (85% hits)
- **Learning:** No free lunches. Measure + choose based on domain.

### 4️⃣ Orchestrator-Worker Pattern (If asked: "How did you achieve 67% latency reduction?")
- **Sequential (v1):** Photo analysis (2s) → RAG (1s) → Generate (2s) = 5s total
- **Parallel (v2):** All three run at same time = 2s total (bottleneck)
- **Why?** Workers are independent; parallelize independent tasks
- **Implementation:** asyncio.gather() to run 3 workers, then combine
- **Result:** 60s → 25s (67% faster)
- **Proof:** See `src/llm/workflow/meal_recommendation_workflow.py`

### 5️⃣ LLM Engineering Surprise (If asked: "What surprised you?")
- **Expectation:** Model quality matters most
- **Reality:** Output validation matters more (prevents 30% of bugs)
- **Example:** Claude returns malformed JSON → code crashes
- **Solution:** Pydantic schema validation + guardrails
- **Another surprise:** Semantic caching beats model upgrades. Sonnet + cache > Opus alone.
- **Lesson:** Architecture > raw capability

---

## Quick Answers (1-Minute Versions)

**Q: Why pgvector instead of Redis/Pinecone?**  
A: Redis can't do semantic similarity (exact match only = 15% hit rate). Pinecone works but adds infrastructure. pgvector is in PostgreSQL—one database, simpler.

**Q: How do you maintain conversation context?**  
A: Store full history in database. Pass last 10 messages + dynamically retrieve user health profile to Claude. Result: 20+ turn conversations with perfect context.

**Q: What's your error handling?**  
A: Layers: input validation → API error handling → output validation → timeouts. Fallback to cached result or generic advice if anything fails. Users get *something*, not 500 error.

**Q: How do you test LLM systems?**  
A: Deterministic tests (cache hit rate, schema validation). Output validation tests (guardrails). Model grading tests (use another Claude to grade quality). 100+ tests, all passing.

**Q: Why Sonnet over Opus?**  
A: Tested both on 150 meal photos. Sonnet: 96% accuracy, 0.8s latency, $0.04/request. Opus: 98%, 2.3s, $0.12. 2% accuracy = ~3g macro error (immaterial for nutrition). Sonnet 3x faster, 70% cheaper. Worth it.

**Q: How would you scale to 1M users?**  
A: Current: works for 100s. At 1M, bottlenecks are: Claude API rate limits (add queue), pgvector search (add index), storage (move to S3), cost ($20/day, sustainable). Architecture stays same, ops scale.

**Q: What's your biggest technical debt?**  
A: Conversation history in PostgreSQL (could be in Redis). Photo analysis is synchronous (could be async queue). Both acceptable tradeoffs now; would fix if they became bottlenecks.

**Q: If building again, what'd you change?**  
A: Start semantic caching day 1 (not week 6). Start output validation day 1. Build monitoring dashboard day 1. Get real user feedback by week 2. Same architecture; faster discovery.

---

## The Meta-Answer (When They Ask "Why Should We Hire You?")

> "I don't just build with LLMs; I architect around them. I demonstrated that semantic caching beats model upgrades, orchestration beats single agents, and monitoring prevents surprises. I measure everything, validate empirically, and make decisions based on data—not hunches. That's how you build LLM systems that scale."

---

## Evidence Pointers (If They Ask "Prove It")

| What They Ask | Where to Point |
|---|---|
| "Show me the caching logic" | `src/llm/cache.py` |
| "Where's the orchestrator-worker pattern?" | `src/llm/workflow/meal_recommendation_workflow.py` |
| "How do you handle multi-turn conversations?" | `src/services/nutrition_chat_service.py` |
| "What's your test coverage?" | `NomNom-Backend/tests/` (100+ tests) |
| "Show the cost analysis" | `docs/iterations/13-cost-and-latency/SUMMARY.md` |
| "What bugs did you fix?" | `docs/iterations/*/BUGLOG.md` |
| "How did you design the API?" | `src/api/` (clean, documented endpoints) |

---

## Interview Timeline

**Minute 0-1:** 60-second pitch (recite exactly)

**Minute 1-3:** "Tell me more" → Pick a talking point (usually #1, #2, or #5)

**Minute 3-5:** Follow-up Q → Likely one of #3 or #4

**Minute 5-10:** Technical deep dive → "Walk me through X" → Reference TECHNICAL_QA.md mentally

**Minute 10-15:** Wrap-up Q → "What surprised you?" or "What would you do differently?"

**After:** "Thanks for the conversation. Here are the docs: [README, INTERVIEW_STORY, TECHNICAL_QA]"

---

## Red Flags (What NOT to Say)

❌ "It's just a food tracking app"  
✅ "It's a case study in LLM production engineering"

❌ "Semantic caching was complicated"  
✅ "Semantic caching solved the right problem (similarity vs. exact match)"

❌ "I couldn't figure out why costs spiked"  
✅ "I diagnosed the cost spike, understood it was behavioral (good sign), and mitigated with caching"

❌ "My code is perfect"  
✅ "I found 25+ bugs through systematic testing and fixed them all"

❌ "I would do it the same way again"  
✅ "With hindsight, I'd start semantic caching and monitoring on day 1, not later"

---

## Confidence Checklist

Before the interview, verify:

- [ ] Can recite 60-second pitch without notes?
- [ ] Can recall all 8 metrics instantly?
- [ ] Can explain semantic caching in 2 minutes?
- [ ] Can explain cost spike story (shows diagnosis)?
- [ ] Can walk through orchestrator-worker pattern?
- [ ] Can point to code files (GitHub evidence)?
- [ ] Can answer "What surprised you?" (shows reflection)?
- [ ] Can answer "What would you do differently?" (shows maturity)?

**If yes to 6+:** You're ready. Go crush it.

---

## Last-Minute Tips

1. **Speak with confidence, not speed.** Slower is better than rushed.
2. **Use the 80/20 rule.** 80% of value from 20% of talking points—focus on #1, #2, #5.
3. **Bring examples.** "For example, when I tested threshold 0.82..." is more convincing than generic.
4. **Admit uncertainty gracefully.** "That's a good question; I haven't implemented that yet, but I would..." shows maturity.
5. **Ask thoughtful follow-up questions.** Shows genuine interest, not just selling yourself.

---

## Post-Interview Email Template

> Hi [Name],
>
> Thanks for the conversation about NomNom! I really enjoyed discussing [specific topic they asked about].
>
> Here are the resources I mentioned:
> - Full README: [link to README.md]
> - Detailed story & talking points: [link to INTERVIEW_STORY.md]
> - 25 technical Q&A: [link to TECHNICAL_QA.md]
> - GitHub repo: [link to GitHub]
>
> Happy to discuss any follow-up questions about the architecture, design decisions, or code.
>
> Looking forward to hearing from you!

---

**Print This Page. Memorize the Pitch and 8 Numbers. You're Ready. Good Luck!** 🚀

---

**Last Updated:** June 16, 2026  
**Status:** Ready for interviews  
**Confidence Level:** High (if you've read INTERVIEW_STORY.md and TECHNICAL_QA.md)
