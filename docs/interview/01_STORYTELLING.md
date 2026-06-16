# NomNom: The Storytelling Guide

**Quick reference for telling your NomNom story at different depths.**

---

## Table of Contents

- [Your Story in One Sentence](#your-story-in-one-sentence)
- [2-Minute Version (Base Framework)](#2-minute-version)
- [5-Minute Version (Technical Depth)](#5-minute-version)
- [15-Minute Version (Deep Dive)](#15-minute-version)
- [Core Insights](#core-insights)

---

## Your Story in One Sentence

You discovered your diet is imbalanced, built an app to fix it, and learned production LLM engineering while solving a real problem.

---

## 2-Minute Version

> "I discovered my diet is imbalanced—too many carbs, lacking protein and fiber. I needed an app to track this, analyze patterns, and get personalized recommendations based on my health profile.
>
> While building this real app, I incorporated every LLM concept I learned: RAG for personalized recommendations, multi-modality (photos + health data), workflow vs agent patterns, tool orchestration, eval pipelines. Real problem + real learning.
>
> **The 6 phases:**
>
> **1. API Fundamentals (v0.5):** Food recognition. Built Jinja2 templating so prompts are product assets. Iteration time: 2hrs → 10min.
>
> **2. Output Control (v1.0):** 97% of errors were JSON parsing, not hallucination. Switched to `tool_choice` + hybrid eval. Accuracy: 72% → 88%.
>
> **3. RAG + Caching (v2.0):** Semantic caching (0.82 threshold) achieved 85% hit rate. Hybrid search improved recommendations 70% → 91%.
>
> **4. Cost Optimization (v2.5):** Model tiering + prompt caching reduced costs 4.3x. Cost per user: $1.50 → $0.35/day.
>
> **5. Orchestration (v3.0):** Workflow vs agent framework. Orchestrator-workers parallelization: 60s → 18s latency.
>
> **6. Ecosystem (v3.1):** MCP server for Claude Code integration. Integration time: 30min → 2min.
>
> **Key thread:** Data-driven decisions. Every choice—0.82 threshold, Sonnet vs Haiku, hybrid search—was measured, not guessed."

**Time:** 2 minutes | **Use when:** Quick elevator pitch, need to hit the "6 phases" narrative

---

## 5-Minute Version

Use the 2-minute version as your skeleton, but add these details:

> "I discovered my diet is imbalanced and built an app to fix it. But I also wanted to actually apply what I learned about LLM engineering—not just read about it.
>
> So I incorporated: RAG (retrieve food history for context), multi-modality (combine photos + health data), workflow orchestration, tool use, eval pipelines, MCP integration.
>
> This taught me: **architecture beats raw model capability.** Here's how:
>
> **Phase 1-2 (Foundation):** Separated prompts from code with Jinja2. Discovered 97% of errors were system design (JSON parsing), not hallucination. Switched to structured output + hybrid eval. Accuracy improved 72% → 88%.
>
> **Phase 3 (Personalization):** Semantic caching with pgvector: tested 0.70–0.95 thresholds on 150 meals, found 0.82 = 85% hit rate + 60% cost reduction. RAG with hybrid BM25+vector search improved recommendations 70% → 91%.
>
> **Phase 4 (Economics):** Model tiering—Sonnet for accuracy (worth 5x cost), Haiku for JSON. Prompt caching saved 89% tokens. Cost per user dropped 4.3x.
>
> **Phase 5 (Performance):** Workflow vs agent framework. Deterministic tasks (meal planning) use workflows (fast, cheap, parallelizable). Exploratory tasks use agents (flexible, slower). Orchestrator-workers pattern: 60s → 18s latency.
>
> **Phase 6 (Integration):** MCP server for Claude Code ecosystem. Shows that NomNom is extensible, not siloed.
>
> **Key metrics:**
> - Latency: 60s → 18s
> - Cache hit rate: 85%
> - Cost savings: 83%
> - Accuracy: 72% → 88%
> - Test coverage: 100+ tests
>
> **Why it matters:** Architecture thinking beats model choice. Sonnet + caching outperforms Opus alone."

**Time:** 5 minutes | **Use when:** Technical screen, want to show depth without overwhelming detail

---

## 15-Minute Version

Use the 2-minute structure as your roadmap, but expand each phase with:

> "I'll walk you through NomNom from concept to production, showing how I approached each phase.
>
> **Context:** Real health problem (my diet) + learning goal (production LLM engineering) = motivated for rigor.
>
> **Phase 1: API Fundamentals (v0.5)**
> - Problem: Prompts hardcoded in Python. Every A/B test meant code+redeploy+retest.
> - Decision: Jinja2 templating. Prompts in `.j2` files, variables injected at runtime.
> - Result: Iteration time 2 hours → 10 minutes.
> - Insight: Prompts are product assets, not code. They change 10x more frequently.
>
> **Phase 2: Output Control (v1.0)**
> - Problem: Prefill+stop for JSON worked, but fragile. 2.8% failure rate.
> - Diagnosis: Spent 2 hours on failed cases. Found: 97% weren't hallucination—they were JSON parsing edge cases.
> - Decision: tool_choice="force" + hybrid eval. Code grader (fast) catches 90% of issues. Model grader (expensive) samples 10%.
> - Result: 100% JSON validity. Accuracy 72% → 88%. Eval cost 90% cheaper.
> - Insight: Most LLM bugs aren't hallucination—they're system design. Fix the system, not the prompt.
>
> **Phase 3: Semantic Caching + RAG (v2.0)**
> - Problem: Every query triggers full Claude call, even for repeated meals. "What did I eat yesterday?" costs same as new analysis.
> - Decision 1: Semantic caching. Tested thresholds 0.70–0.95 on 150 real meals. Data said 0.82.
> - Decision 2: RAG with hybrid search (BM25 + vector + RRF). Retrieve food history + health profile.
> - Decision 3: Citations for every claim. Users can verify.
> - Result: 85% cache hit rate. Recommendations 70% → 91% accuracy. 60% cost reduction.
> - Insight: You need both vector AND keyword search. Semantic similarity > exact matching.
>
> **Phase 4: Cost Optimization (v2.5)**
> - Problem: System unsustainable at $1.50/user/day ($45k/month at 1k users).
> - Decision 1: Model tiering. Sonnet for food recognition (accuracy critical). Why? Tested Haiku vs Sonnet on ambiguous foods (muesli vs granola): 72% vs 88%. That 40% gap matters for health. Cost: $0.0015/request × 1k users × 20/day = $30/day sustainable.
> - Decision 2: Prompt caching (400-token system prompt, 1-hour TTL). 89% token savings.
> - Decision 3: Cost tracking dashboard. Revealed RAG = 60% of spend.
> - Challenge: Switched to Sonnet expecting cost drop. Costs went UP. Why? Faster → better UX → more volume. Classic optimization trap.
> - Breakthrough: Optimize systems holistically, not variables in isolation.
> - Result: Daily cost $1.50 → $0.35 per user (4.3x reduction).
> - Insight: Cost + latency + quality are coupled. Measure systems, not levers.
>
> **Phase 5: Agents & Orchestration (v3.0)**
> - Problem: 'Plan my week' = 21 recommendations. Single agent loop = 60s, costs too much.
> - Decision: Workflow vs agent framework.
>   - Deterministic (meal planning): workflow. Steps known upfront. Result: 2.1s, $0.004, parallelizable.
>   - Exploratory (fridge leftovers): agent. Steps unknown. Result: 12s, $0.02.
> - Decision: Orchestrator-workers for meal planning. Decompose 'week' into 7 workers (one per day), run parallel.
> - Result: 60s → 18s latency. Same cost. 3.3x faster.
> - Insight: 95% of real-world tasks are workflows. Architecture beats raw capability.
>
> **Phase 6: MCP & Ecosystem (v3.1)**
> - Problem: App siloed. Only iOS + REST API. Claude Code can't easily use it.
> - Decision: MCP server. Tools (`analyze_food_image`, `lookup_nutrition`, `recommend_meal`) + Resources + Prompts.
> - Result: Integration time 30min → 2min. Ecosystem reach multiplies.
> - Insight: Standards matter. MCP positions NomNom as a service, not an app.
>
> **Summary Table:**
> | Phase | Focus | Key Decision | Outcome |
> |-------|-------|---|---|
> | 1 | Prompts | Jinja2 templating | 12x iteration speed |
> | 2 | Output | tool_choice + eval | 100% JSON, 88% accuracy |
> | 3 | Personalization | Semantic caching (0.82) | 85% hit rate, 91% recall |
> | 4 | Economics | Model tiering | 4.3x cost reduction |
> | 5 | Performance | Orchestrator-workers | 3.3x latency improvement |
> | 6 | Integration | MCP server | Ecosystem-ready |
>
> **Through-line:** Every decision involved tradeoffs. I didn't pick 'best'—I measured and chose based on constraints. Sonnet costs 5x more but 40% accuracy gain justifies it. Orchestrator-workers adds complexity but 3.3x speedup justifies it. Caching at 0.82 accepts 1% false positives to get 85% hits.
>
> This is production thinking: measure and choose, not hype."

**Time:** 15 minutes | **Use when:** System design interview, whiteboarding, want to show end-to-end thinking

---

## Core Insights

### **1. The Real Problem Isn't the Model—It's System Design**

**Before:** Bigger models = better results.  
**What happened:** Sonnet (cheaper) + semantic caching (85% hit rate) outperformed Opus alone.  
**Now:** Every problem, diagnose the constraint first. Is it quality? Cost? Latency? Then design accordingly.  
**Why it matters:** Changes how you approach *every* LLM problem.

### **2. Blame the System, Not the Model**

**Before:** LLM fails → improve prompt.  
**What happened:** Phase 2: 97% of failures were JSON parsing, not hallucination.  
**Now:** Diagnose: is this a capability gap or a system design gap? I spend 80% on systems, 20% on prompts.  
**Why it matters:** Explains why my output is 100% valid, eval is cheap, latency is fast.

### **3. Optimize Holistically or Break Everything**

**Before:** Optimize each variable independently.  
**What happened:** Switched to cheaper model, costs went UP (better UX → more volume).  
**Now:** Think in constraints, not levers. What's coupled? What breaks if I change X?  
**Why it matters:** Single-variable optimization fails. Phase 4 taught me this.

### **4. Measure Everything Or You're Guessing**

**Before:** Build → test → ship.  
**What happened:** 0.82 threshold came from measuring, not intuition. Tested 8 thresholds, data said 0.82.  
**Now:** I trust data over intuition. Every decision: how would I measure this?  
**Why it matters:** Makes me data-driven for life.

---

**Last Updated:** June 16, 2026  
**Status:** Ready for interviews  
**Total prep time:** 5-15 min depending on version
