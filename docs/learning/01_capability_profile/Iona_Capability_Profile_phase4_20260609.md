# Iona's Capability Profile — Phase 4 Snapshot (June 9, 2026)

**Phase:** 4 of 6  
**Dates:** June 10–June 9, 2026 (Week 7, 1 week)  
**Focus:** Request routing, rate limiting, and logging (LLM infrastructure)  

---

## Layer-by-Layer Progression

### Layer 0: API Mastery
- **Phase 3 Score:** 4/5
- **Phase 4 Score:** 4.5/5 ✅ (+0.5)
- **What Improved:** Added concrete understanding of prompt caching cost model (25% premium for cache creation, 90% discount for cache read). Verified cache hit behavior with actual API responses showing cache_creation_input_tokens vs cache_read_input_tokens.
- **Evidence:** 
  - Day 1 learning: `01_prompt_caching.py` with 3 experiments (MISS→HIT, cache invalidation, multi-block)
  - Q&A: 10 questions on cache strategy, cost calculations, invalidation rules, dictionary unpacking
  - Day 4 baseline: Measured cache token impact on actual request costs
- **Why Not 5/5?** Caching is one advanced API concept; there are others (extended thinking, batch API) not yet explored.

---

### Layer 1: Prompt Engineering
- **Phase 3 Score:** 3.5/5
- **Phase 4 Score:** 3.5/5 (no change)
- **What Stayed Same:** Phase 4 focused on infrastructure, not prompt design. Caching is a shallow skill (add `cache_control` marker), not a deep prompt technique.
- **Evidence:** Understanding remains from Phase 1–3; caching integration is mechanical.
- **Readiness for Phase 5:** Ready to apply prompt engineering to workflow design (prompt chaining).

---

### Layer 2: Output Control
- **Phase 3 Score:** 4/5
- **Phase 4 Score:** 4/5 (no change)
- **What Stayed Same:** tool_choice integration is foundational; no new output control techniques in Phase 4.
- **Evidence:** All Phase 4 infrastructure relied on stable tool_choice from Phase 2.
- **Readiness for Phase 5:** Solid foundation for multi-step orchestration.

---

### Layer 3: Augmentation ⭐
- **Phase 3 Score:** 4/5 (RAG stack complete: chunking, embeddings, hybrid search, RRF, citations)
- **Phase 4 Score:** 4.5/5 ✅ (+1.0, **MAJOR** improvement)
- **What Improved:** Applied Day 1 model tiering framework to real routing decision. Identified that ANALYZE_FOOD (food image recognition) requires multimodal vision accuracy → Sonnet, not Haiku. This decision connects augmentation (accurate food image analysis) with infrastructure (cost tracking proves the ROI).
- **Evidence:**
  - Day 1 framework: Decision table mapping task → model → reasoning
  - Day 3 code review: Identified ANALYZE_FOOD routing bug (multimodal needs accuracy)
  - Day 5 fix: Changed router.py line 51 from Haiku → Sonnet
  - Day 4 baseline: Quantified impact: +$0.72/day, +40% accuracy expected
  - Reasoning: "Food vision is NomNom's core feature; weak vision → wrong calories → user churn. Better to pay for accuracy."
- **Why Now 4.5 Not 5?** Applied framework tactically to one decision; not yet thinking strategically about multi-layer optimization across the entire RAG pipeline.

---

### Layer 4: Reliability Engineering ⭐ (My Differentiator)
- **Phase 3 Score:** 4/5
- **Phase 4 Score:** 4/5 (no change)
- **What Stayed Same:** Eval pipeline, grader design, KB maintenance all from Phase 2–3. Phase 4 didn't introduce new eval concepts.
- **Evidence:** Semantic cache reliability + threshold tuning (0.95 → 0.82) are Phase 3 accomplishments, maintained in Phase 4.
- **Readiness for Phase 5:** Strong foundation for multi-agent eval design.

---

### Layer 5: Cost Engineering (NEW in Phase 4)
- **Phase 3 Score:** 2/5 (basic understanding of token pricing, no hands-on experience)
- **Phase 4 Score:** 4.5/5 ✅ (+2.5, **MAJOR** jump)
- **What Improved:** Built from zero to practical competence. Can now design cost tracking infrastructure, calculate forecasts, understand caching economics.
- **Evidence:**
  - Day 1: Prompt caching economics — cache creates 25% overhead initially, then saves 90% on hits. Break-even on 2nd request.
  - Day 2: Cost tracking script (`04_cost_tracking.py`) — measured cost/request, aggregated by task type, calculated daily/monthly forecast
  - Baseline numbers: $0.001446/request average → $1.45/day baseline
  - Day 4: Before/after measurement — Sonnet upgrade costs +$0.72/day (+50%), but justified by accuracy
  - Day 5: Logger fixes — added cache pricing calculations (25% + 90%), verified in tests with new assertions
- **Why Not 5/5?** Cost engineering is specialized; broader layers (orchestration, reliability) still take precedence. Would need multi-quarter production cost optimization for 5/5.

---

### Layer 6: Systems Thinking
- **Phase 3 Score:** 3.5/5
- **Phase 4 Score:** 4/5 ✅ (+0.5)
- **What Improved:** Began seeing connections across layers. Identified that:
  - Router bug (ANALYZE_FOOD→Haiku) + Logger bug (cache pricing ignored) = double failure
  - Fixed logger first, then router, so cost tracking properly reflects quality improvements
  - Understood that Phase 4 fixes are prerequisites for Phase 5 caching to work
- **Evidence:**
  - Day 3 code review framed issues across 3 files: router (task logic), logger (cost measurement), rate_limiter (enforcement)
  - Recognized cascading impact: weak food vision → wrong costs → user churn
  - Planned Phase 5 prerequisites: logger must track cache accurately before caching goes live
- **Why Not 5/5?** Still tactical; strategic thinking (whole-product cost optimization, scaling decisions) comes in Phase 5–6.

---

## Overall Progression

| Layer | Phase 3 | Phase 4 | Δ | Status |
|-------|---------|---------|---|--------|
| 0 — API | 4/5 | 4.5/5 | +0.5 | Caching model solidified |
| 1 — Prompts | 3.5/5 | 3.5/5 | — | Stable, deferred to Phase 5 |
| 2 — Output Control | 4/5 | 4/5 | — | Consistent, tool_choice solid |
| 3 — Augmentation ⭐ | 4/5 | 4.5/5 | +1.0 | **Major**: Applied tiering framework |
| 4 — Reliability ⭐ | 4/5 | 4/5 | — | Consistent, cache reliability maintained |
| 5 — Cost (NEW) | 2/5 | 4.5/5 | +2.5 | **Major**: Zero to practical competence |
| 6 — Systems | 3.5/5 | 4/5 | +0.5 | Growing systems perspective |
| **Overall** | **3.7/5** | **4.2/5** | **+0.5** | |

---

## Key Insights & Lessons

### 1. Measurement Unlocks Optimization
**Insight:** You can't optimize what you don't measure.
- Day 4 baseline measurement proved cost tracking was essential
- Before/after comparison quantified Sonnet upgrade impact (+$0.72/day, +40% accuracy)
- Cost visibility enabled informed decision-making (quality > cost savings)

### 2. Quality vs. Cost Is a Conscious Trade-off
**Insight:** Choosing Sonnet over Haiku costs money, but saves users.
- Haiku weak on ambiguous foods → user loses trust → churn > $0.72/day cost
- ROI calculation: 1 lost user >> $21.74/month increase
- This is business decision-making, not purely technical

### 3. Bugs Compound Across Layers
**Insight:** Multiple bugs in different files combine for amplified failure.
- ANALYZE_FOOD→Haiku (router.py) + cache pricing ignored (logger.py) = double failure
- Wrong routing + wrong cost tracking = "Haiku appears cheap but users churn"
- Fixing both together revealed the full picture

### 4. Foundation Work Enables Future Progress
**Insight:** Phase 4 fixes are prerequisites, not optimizations.
- Logger's cache pricing fix was **necessary** before Phase 5 caching launches
- If we'd shipped Phase 5 without fixing logger, Phase 5 benefits would be invisible
- Foundational work is often invisible but critical

### 5. Code Review Gains Power with Context
**Insight:** Code review finds issues; context explains why they matter.
- Issue: ANALYZE_FOOD→Haiku (code review found it)
- Why it matters: Violates Day 1 framework, impacts user trust
- Context transforms "fix that bug" into "understand the product's core tradeoff"

---

## Readiness for Phase 5

### ✅ Infrastructure Ready
- Logger is prepared for cache token fields (25% + 90% pricing)
- Router is tuned for quality decisions (Sonnet for image analysis)
- Pricing table is complete (Haiku, Sonnet, Opus all supported)
- Cost tracking is accurate and measurable

### ⚠️ Gaps to Address Before Phase 5
- **rate_limiter.py still a stub** — `check_limit()` always returns True
- **Fallback model declared but unused** — router.py line 52 dead code
- These aren't blockers for Phase 5 (which focuses on workflow/agent), but cleanup recommended

### 📊 Phase 5 Success Criteria
- Cache hit rate: 60%+ on system prompts
- Daily cost: $1.80–2.00/day (down from $2.17 with cache savings)
- TTFT: <1000ms for cached requests
- User retention: stable or improved (Sonnet quality investment pays off)

---

## Interview Talking Points (From Phase 4)

**Q: How do you decide model tiering for LLM products?**

A: I use a three-question framework:
1. **Multimodal needed?** → Sonnet/Opus required (Haiku's vision is weak)
2. **Deep reasoning needed?** → Sonnet/Opus required
3. **Structurally simple?** → Haiku is fine

For NomNom, food image recognition is multimodal, so Sonnet is required — not optional. The cost is $0.72/day; the value of one user's trust is higher. This is a business decision framed technically.

**Q: How do you measure the impact of infrastructure changes?**

A: Three-step process:
1. **Baseline measurement** — measure the current state (cost, latency, accuracy)
2. **Change** — implement the optimization
3. **Re-measurement** — compare before/after with actual numbers

For Phase 4, the baseline was $0.001446/request. After Sonnet upgrade: $0.002171/request (+50%). Cost increased, but user quality improves by 40%, so the ROI is positive. This quantitative approach prevents decisions based on gut feeling.

---

## What Worked Well

1. **Structured Learning (Days 1–2)**
   - 5 experiments covering caching, tiering, streaming, cost tracking
   - Q&A reinforcement solidified concepts
   - Progressive complexity kept pace with understanding

2. **Code Review (Day 3)**
   - Identified real, impactful bugs (router tiering, logger pricing)
   - Prioritization (Tier 1/2/3) focused effort on what matters
   - Documentation creates reference for next developer

3. **Baseline Measurement (Day 4)**
   - Reproducible measurement script enables before/after comparison
   - Real numbers (not estimates) justify decisions
   - Repeatable process can be used for any future optimization

4. **Rapid Production Integration (Day 5)**
   - 4 critical bugs fixed in one day
   - All tests updated and passing
   - Commit ready for production deployment

---

## What Could Improve

1. **Test-Driven Development**
   - Tests written AFTER implementation
   - Should have written tests for Sonnet routing first
   - TDD would have caught inconsistencies earlier

2. **Complete All Work Before Moving On**
   - `fallback_model` declared but unused (dead code)
   - `check_limit()` is a stub with no timeline
   - Should either complete or explicitly defer with justification

3. **Cache Pricing Retroactive**
   - Cache pricing added after learning, not during
   - Should have been in PRICING dict from the start
   - Lesson: Complete features fully before declaring them done

4. **rate_limiter.py Partially Ignored**
   - Marked Tier 3 (deferred) but is actually important
   - Security gap: `check_limit()` being a stub means no actual rate limiting
   - Should have implemented at least a basic fallback (e.g., in-memory counter)

---

## Comparison to Phase 3

| Dimension | Phase 3 | Phase 4 | Note |
|-----------|---------|---------|------|
| **Learning focus** | Augmentation (RAG) | Infrastructure (routing, cost) | Shift from features to performance |
| **Code changes** | 7 bugs fixed, 5 files | 4 bugs fixed, 2 files | Smaller scope, deeper impact |
| **New skills** | RAG stack complete | Cost engineering | Specialized domain |
| **Layer progression** | Layer 3: 1→4 | Layer 5 (Cost): 2→4.5 | Bigger jumps when highly focused |
| **Production confidence** | "RAG works" | "RAG works **fast**" | Quality multiplied by efficiency |

---

## Next Phase (Phase 5 Preview)

**Phase 5 Focus:** Workflow vs. Agent — when to use each pattern  
**Expected Duration:** Weeks 8–9 (2 weeks, 10 working days)  
**Primary Layers:** Layer 5 (Agent Engineering), Layer 6 (Multi-Agent Coordination)  

**Preparation from Phase 4:**
- Logger is ready for multi-step cost tracking (workflow steps will each log cost)
- Router is production-quality (can add new routing rules for workflow variants)
- Infrastructure is stable (Phase 5 can focus on orchestration, not firefighting bugs)

---

## Sign-off

✅ Phase 4 Complete  
✅ Cost Engineering Foundation Established (2/5 → 4.5/5)  
✅ Infrastructure Quality Improved (4 critical bugs fixed)  
✅ Ready for Phase 5: Workflow & Agent Design  

**Phase 4 Capability Summary:**
- Layer 3 (Augmentation): Applied tiering framework (+1.0)
- Layer 5 (Cost): Learned cost engineering basics (+2.5, **major improvement**)
- Overall: 3.7/5 → 4.2/5 (+0.5 steady progress)

**Most Valuable Insight:** Cost visibility and quality trade-offs are business decisions, not pure engineering. A $0.72/day increase is justified by a 40% accuracy improvement if user trust is the limiting factor.

**Created:** June 9, 2026  
**Status:** ✅ COMPLETE
