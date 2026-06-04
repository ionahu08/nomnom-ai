# Iona's LLM Harnessing Capability Profile — Phase 1 Snapshot

**Date:** June 4, 2026 (End of Phase 1)

> This is a historical snapshot of capability progression. See `Iona_Capability_Profile.md` for the forward-looking living profile.

---

## Phase 1 Summary

**What was accomplished:**
- 15 Jupyter notebooks: API fundamentals, prompt engineering, output control, augmentation, agents
- 3 project directories: MCP server, Claude Code labs, hooks  
- 2 deep code reviews: client.py (reliability), prompt_engine.py (templating)
- NomNom v0.5 capstone: Full LLM pipeline demonstration
- **Key insight:** Prompts are product assets (10x change frequency)

**Duration:** May 17–June 4, 2026 (10 working days)

---

## Layer-by-Layer Capability at Phase 1 End

### Layer 0: API Mastery
- **Phase 0 → Phase 1:** 1/5 → **4/5** ✅
- **Target:** 4/5
- **Status:** ON TARGET
- **Evidence:**
  - Completed 15 notebooks covering messages, model selection, streaming, multimodal
  - Understand O(n²) token cost dynamics in multi-turn conversations
  - Reviewed client.py: retry logic, timeout enforcement, fallback strategy, per-model config
  - Experimented with real Claude API in NomNom v0.5 capstone
  - Can explain stop_reason, usage tracking, model tiering trade-offs

---

### Layer 1: Prompt Engineering
- **Phase 0 → Phase 1:** 1/5 → **3/5** ✅
- **Target:** 4/5
- **Status:** ON TRACK (1/5 of way to target)
- **Evidence:**
  - Analyzed 4 production templates (analyze_food, cat_personas, recommend_meal, weekly_recap)
  - Identified 9 prompt engineering techniques: role assignment, few-shot, CoT, XML tags, system prompt, temperature, guardrails, defense-in-depth, structured output
  - Defended 7 design choices: why 2 examples vs. 5, why cat_style appears twice, why cat_personas extracted
  - Understand Jinja2 templating: variables, conditionals, includes
  - Key insight: Prompts are product assets — separation from code is essential
  - Built NomNom v0.5 integrating prompt rendering + multimodal

---

### Layer 2: Output Control
- **Phase 0 → Phase 1:** 0/5 → **1/5** ✅
- **Target:** 4/5
- **Status:** FOUNDATION LAID
- **Evidence:**
  - Understand tool_choice vs. text parsing trade-off (tool_choice is better)
  - Built text parser in capstone, recognized fragility
  - Know that JSON text parsing is unreliable when Claude adds markdown
  - Ready to implement tool_choice in Phase 2
  - Aware of structured output patterns (stop sequences, prefill+stop, tool_choice)

---

### Layer 3: Augmentation ⭐
- **Phase 0 → Phase 1:** 0/5 → **1/5** ✅
- **Target:** 5/5 (NomNom's main battlefield)
- **Status:** FOUNDATION LAID
- **Evidence:**
  - Studied RAG pipeline concepts: chunking, embeddings, vector search, reranking
  - Experimented with multimodal (food image input, base64 encoding)
  - Know tool use basics from notebooks (schemas, tool_choice, parsing)
  - Aware of MCP (Model Context Protocol) concepts
  - Ready to build full RAG stack in Phase 3

---

### Layer 4: Reliability Engineering ⭐
- **Phase 0 → Phase 1:** 1/5 → **2/5** ✅
- **Target:** 5/5 (My differentiator)
- **Status:** FOUNDATION LAID
- **Evidence:**
  - Reviewed client.py in detail: retry logic (2 attempts, 1s→2s backoff), timeout per-model, fallback strategy
  - Understand latency vs. reliability trade-offs (why 2 retries not 3 or 5)
  - Know quality-first strategy: Sonnet primary (high-quality), Haiku fallback (fast)
  - Can defend design choices: why 20s Haiku timeout vs. 30s Sonnet
  - Aware that reliability is designed in, not bolted on
  - Ready to build eval pipelines in Phase 2

---

### Layer 5: Agent Engineering
- **Phase 0 → Phase 1:** 0/5 → **1/5** ✅
- **Target:** 4/5
- **Status:** FOUNDATION LAID
- **Evidence:**
  - Studied agent loops, multi-step workflows from notebooks
  - Understand subagent patterns for delegation
  - Know MCP basics and Claude Code SDK concepts
  - Aware of 5 workflow patterns (chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer)
  - Haven't implemented yet, but understand patterns conceptually
  - Ready to hand-code agent loops in Phase 3

---

### Layer 6: Multi-Agent Coordination
- **Phase 0 → Phase 1:** 0/5 → **0/5** (Not in Phase 1 scope)
- **Target:** 3/5
- **Status:** NOT STARTED
- **Notes:** Intentionally deferred to Phase 5 (week 8-9)

---

## Key Insights from Phase 1

### 1. Prompts are product assets, not code
- Change frequency: 10x more than code
- Separation enables: product teams to iterate without touching Python
- Architecture reflects this: templates separate from infrastructure (client.py)

### 2. Reliability is designed in, not bolted on
- client.py encodes 5 crucial decisions in 30 lines
- Each choice (2 retries, 1s→2s backoff, per-model timeouts) has reasoning
- Trade-offs are about balancing latency vs. reliability

### 3. Token cost is a first-class design constraint
- Multi-turn conversations cost O(n²) because every round re-sends full history
- By round 5, cumulative cost ≈ 170× round 1
- Prompt caching (Phase 4) essential for long conversations

### 4. DRY applies to templates too
- cat_personas.j2 included by multiple templates
- Prevents: copy-paste drift, sync bugs, inconsistent behavior
- Template design should follow code principles: DRY, single responsibility

### 5. Tool use > text parsing for structured output
- Text parsing is fragile (Claude may wrap JSON in markdown)
- Tool schemas guarantee structure (tool_choice forces compliance)
- Deferred to Phase 2 for implementation

### 6. Sandbox-first learning > documentation
- Reading Jinja2 docs helpful, but experimentation is 10x better
- Running capstone with 3 cat-styles made templating crystal clear
- Measured token costs teach better than theory

### 7. API protocol reflects training
- User/assistant role alternation not arbitrary — reflects Claude's training
- Claude generates only in assistant position
- Understanding the why prevents confusion and aids debugging

---

## Phase 1 Challenges & Resolutions

| Challenge | Resolution | Insight |
|-----------|-----------|---------|
| async/await | Understood as concurrent I/O necessity | Essential for responsive apps |
| O(n²) token cost | Measured empirically (16 → 262 → 1075) | Prompt caching critical |
| Role alternation requirement | Learned it reflects Claude's training | Protocol matches architecture |
| Module import paths | Explicit path calculation, not guessing | Python imports are relative to runtime |
| JSON parsing fragility | Text parser + fallback, noted tool_choice as better | Tool use is Phase 2 refactor |
| Template reuse design | Extracted cat_personas.j2 to avoid duplication | DRY applies to templates |
| Experimentation vs. reading | Ran capstone 3 times with different cat-styles | Sandbox-first > documentation |

---

## Next Phase Preview

**Phase 2 (Week 3–4, starting June 5):** Make NomNom Not Crash

**Focus files:**
- parser.py — Parse Claude's structured output
- guardrails.py — Validate output meets constraints
- evaluator.py — Measure prompt quality
- tools.py — Define tool schemas

**Phase 1 → Phase 2 handoff:**
- Replace JSON text parsing with tool_choice (guaranteed structure)
- Build eval pipeline to measure prompt quality
- Add guardrails to validate parsed output
- Learn when and how to use structured output patterns

**Expected capability gains:**
- Layer 2 (Output Control): 1/5 → 4/5
- Layer 4 (Reliability): 2/5 → 4/5 (eval pipelines)

---

## Snapshot at a Glance

| Layer | Phase 0 | Phase 1 | Phase 1 Target | Status |
|---|---|---|---|---|
| **0 — API Mastery** | 1/5 | **4/5** ✅ | 4/5 | ON TARGET |
| **1 — Prompt Engineering** | 1/5 | **3/5** ✅ | 4/5 | ON TRACK |
| **2 — Output Control** | 0/5 | **1/5** ✅ | 4/5 | FOUNDATION |
| **3 — Augmentation ⭐** | 0/5 | **1/5** ✅ | 5/5 | FOUNDATION |
| **4 — Reliability ⭐** | 1/5 | **2/5** ✅ | 5/5 | FOUNDATION |
| **5 — Agent Engineering** | 0/5 | **1/5** ✅ | 4/5 | FOUNDATION |
| **6 — Multi-Agent** | 0/5 | 0/5 | 3/5 | NOT STARTED |

**Overall Phase 1 Progression:** Average 0.5/5 → 1.7/5

---

## Artifacts & Evidence

### Learning Materials
- 15 Jupyter notebooks (01-15)
- 3 project directories (10a, 11a, 11b)

### Code Reviews
- `docs/learning/05_learning_notes/code_review/01_client_py_design_review.md`
- `docs/learning/05_learning_notes/code_review/02_prompt_engine_design_review.md`

### Capstone
- `learning_lab/phase_1/capstone/nomnom_v0_5.py`
- Fully documented with high-level overview + flow trace Q&A

### Retrospective
- `docs/learning/03_phase_retrospectives/phase_1_retro.md`

---

**Phase 1 Complete.** Ready for Phase 2.
