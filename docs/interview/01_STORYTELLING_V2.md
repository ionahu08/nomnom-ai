# NomNom: Interview Story (Resume-Aligned)
## Conversational Versions (2-min, 5-min, 15-min)

**Simplified for retention. Focus on resume points only. Save energy for delivery.**

---

## Quick Navigation

| Version | Time | Best For |
|---------|------|----------|
| **2-min** | 120s | Elevator pitches, quick screens |
| **5-min** | 300s | Technical screens |
| **15-min** | 900s | System design, deep dive |

---

## 2-Minute Version

> "I discovered my diet was imbalanced—lots of carbs, not enough protein. I built NomNom to solve it, but used it as a testbed for LLM engineering at scale.
>
> The real challenge: making it fast, cheap, and reliable.
>
> **I used task-based model routing.** Haiku for lightweight extraction, Sonnet for complex reasoning. Combined with orchestration patterns (tool use, retry, fallback), this achieved 5–15 second latency and 4.3x cost reduction compared to Sonnet-only.
>
> **I designed a multi-agent architecture.** For structured analysis (meal → nutrition → recommendation), I used an orchestrator-worker pipeline. For the interactive coach, I used a plan-act-reflect loop. Different patterns solve different problems.
>
> **I built production guardrails.** 97% of early failures weren't hallucination—they were JSON parsing bugs. So I added prompt templating, structured outputs, and validation + retry guardrails. Near-100% success rate on 10K+ API calls.
>
> **I implemented semantic caching.** With RAG-style retrieval using vector + BM25 hybrid search, I achieved 85% cache hit rate by testing the optimal threshold (0.82) on 150 real meals.
>
> Throughout all of this: every decision was data-driven, measured on real data."

**Time:** ~2 minutes

---

## 5-Minute Version

> "I built NomNom because my diet was imbalanced. But I didn't just build an app—I used it to solve a real LLM engineering problem: how do you build fast, cheap, reliable systems?
>
> **The Problem:** Most teams use powerful models for everything. That's expensive.
>
> **My Solution: Task-Based Model Routing**
>
> I used multimodal AI to analyze food photos. But I routed based on complexity:
> - Haiku for lightweight extraction (identifying food)
> - Sonnet for complex reasoning (personalized nutrition)
> - Orchestration patterns (tool use, retry) for robustness
>
> Result: 5–15s latency, 4.3x cost reduction vs. Sonnet-only baseline.
>
> **Multi-Agent Architecture: Right Pattern for Right Job**
>
> - Structured meal analysis (vision → nutrition → recommendation): Fixed orchestrator-worker pipeline. Predictable, reliable.
> - Interactive coach (user questions): Autonomous plan-act-reflect loop. Flexible, adaptive.
>
> **Production Reliability: Fix the System, Not the Model**
>
> Early on, I thought failures were hallucination. I measured: 97% were JSON parsing bugs.
>
> So I built guardrails: prompt templating, structured outputs, validation + retry. Near-100% success on 10K+ calls.
>
> **Semantic Caching: Measure Before Deciding**
>
> I tested thresholds (0.70 to 0.95) on 150 real meals. Found 0.82 optimal: 85% cache hit rate with RAG-style vector + BM25 hybrid search.
>
> Key insight: measurement beats intuition. I thought 0.95 would be safe. Real data proved me wrong.
>
> **Throughout:** Every decision validated on real data."

**Time:** ~5 minutes

---

## 15-Minute Version

> "Let me walk you through how I built NomNom and what it taught me.
>
> **Why I Built It**
>
> I discovered my diet was imbalanced—lots of noodles and rice, not enough protein and fiber. I needed an app to track and understand my eating patterns.
>
> But here's the thing: I didn't just want to build a food tracker. I wanted to use it as a testbed for a hypothesis I had about LLM engineering.
>
> Most teams approach LLM applications like: Claude is powerful, use it for everything. But that gets expensive and slow. I hypothesized: with proper architecture, you can build systems that are fast, cheap, AND reliable. NomNom became my proof.
>
> ---
>
> **Phase 1: Task-Based Model Routing**
>
> The system needed to:
> 1. Analyze food photos (multimodal AI)
> 2. Estimate nutrition
> 3. Generate personalized recommendations
>
> I could use Sonnet for everything. But that would be expensive and slow.
>
> So I made an architectural decision: route by task complexity.
>
> - **Haiku** for simple extraction: What's in the photo? Fast, cheap, 90%+ accurate for this job.
> - **Sonnet** for reasoning: Personalized nutrition? Use the heavy hitter.
> - **Orchestration patterns**: Tool use (structured outputs), retry logic, fallback handling.
>
> Result: 5–15 second response time. 4.3x cost reduction ($12/user/day → $2.80/user/day) versus Sonnet-only.
>
> The lesson: the constraint isn't always the model. Often it's how you orchestrate it.
>
> ---
>
> **Phase 2: Multi-Agent Architecture**
>
> I realized different parts of the system needed different approaches.
>
> **For meal analysis** (determine food → calculate nutrition → generate recommendation):
> - Steps are known, order is fixed
> - I used orchestrator-worker pattern: one coordinator, three workers parallel
> - Result: predictable latency, zero surprises
>
> **For the nutrition coach** (user asks questions, agent responds):
> - Unknown questions, adaptive responses needed
> - I used plan-act-reflect loop: think → act → reflect → repeat if needed
>
> Different problems, different patterns. That's the key insight: not everything is an agent, not everything is a fixed pipeline.
>
> ---
>
> **Phase 3: Production-Grade LLM Harness**
>
> Early on, my system was giving wrong answers. I assumed: hallucination. So I spent time on better prompts.
>
> Then I measured my actual failures. Out of 100 errors:
> - 97: JSON parsing bugs (malformed output)
> - 3: Actual hallucinations
>
> The problem wasn't the model. It was system design.
>
> So I built guardrails:
> - **Prompt templating**: Separated prompts from code (easier iteration)
> - **Structured outputs**: Pydantic validation forces correct JSON
> - **Validation + retry**: If parsing fails, retry automatically
>
> Result: Near-100% success rate on 10K+ API calls. Parsing failures dropped to near-zero.
>
> Big lesson: don't blame the model. Fix the system.
>
> ---
>
> **Phase 4: Semantic Caching with RAG-Style Retrieval**
>
> Users log similar meals. \"Salmon bowl\" and \"salmon with rice\" are nutritionally similar. But exact-match caching only catches ~15% of these.
>
> I built semantic caching:
> - Convert meals to vectors (embeddings)
> - Use hybrid search: vector similarity + BM25 (keywords)
> - If we've analyzed something similar, reuse it
>
> But how similar is \"similar enough\"?
> - Too low threshold: incorrect results
> - Too high threshold: miss real matches
>
> I tested thresholds (0.70, 0.75, 0.80, 0.82, 0.85, 0.90, 0.95) on 150 real meals. Measured precision and recall.
>
> Found: **0.82 optimal.** 85% cache hit rate, only 1% false positives.
>
> Result: Cuts redundant LLM calls massively. Saves cost and latency.
>
> The lesson: measurement beats intuition. I initially thought 0.95 would be safe. Real data proved me wrong.
>
> ---
>
> **The Consistent Pattern**
>
> Across all phases, the theme is the same: data-driven decision making.
>
> - Task routing: measured model accuracy/cost tradeoff
> - Architecture: orchestrator-worker pattern measured 8x faster than sequential
> - Caching threshold: tested on 150 real meals, found 0.82 optimal
>
> Not guesses. Not best practices. Actual measurement on real data.
>
> That's what I learned: in LLM engineering, measurement is your superpower. Decide by measuring, not by assuming."

**Time:** ~15 minutes

---

## Delivery Tips

- **Pause on numbers:** Let 5–15s, 4.3x, 0.82, 85%, 10K+ sink in.
- **Own the struggle:** "I thought it was hallucination. Then I measured..." (credible)
- **Use bridges:** "So...", "But here's the thing...", "That's when I realized..."
- **Invite questions:** "Does that make sense?" or "Want me to go deeper?"
- **Don't memorize:** Use these as frameworks. Tell naturally in your voice.

---

## Alignment with Resume

This story covers all 5 resume bullets:
1. ✅ **Multimodal AI** — Phase 1 opening
2. ✅ **Task-based model routing + orchestration + 5–15s latency + 4.3x cost** — Phase 1
3. ✅ **Multi-agent architecture + orchestrator-worker + plan-act-reflect** — Phase 2
4. ✅ **Production-grade harness + prompt templating + guardrails + near-100%** — Phase 3
5. ✅ **Semantic caching + RAG-style retrieval + hybrid search + 85% + 0.82 on 150 meals** — Phase 4

**Key:** Everything here can be backed up by the 5 resume bullets. No extra details to remember.
