# LLM Harnessing Learning Roadmap (NomNom Main Line Version)

> **Design philosophy**: Use the real product evolution of NomNom Nutrition Analysis App as the skeleton. Every concept learned is immediately applied to the product. The capability stack serves as a side-line checklist, ensuring no interview blind spots are missed.
>
> **Total duration**: 10 weeks (at 6 hours/day pace)
> **Final deliverables**: 1 deep capstone project (NomNom) + 2 supporting projects + complete Capability Profile

---

## Table of Contents

- [Prologue: Cognitive Map and Product Definition](#prologue-cognitive-map-and-product-definitionweek-0)
- [Phase 1: NomNom MVP — Make It Recognize Food (Week 1–2)](#phase-1-nomnom-mvp--make-it-recognize-foodweek-12)
- [Phase 2: Make NomNom Not Crash (Week 3–4)](#phase-2-make-nomnom-not-crashweek-34)
- [Phase 3: Make NomNom Smarter (Week 5–6)](#phase-3-make-nomnom-smarterweek-56)
- [Phase 4: Make NomNom Cheap and Fast (Week 7)](#phase-4-make-nomnom-cheap-and-fastweek-7)
- [Phase 5: Make NomNom Handle Complex Questions (Week 8–9)](#phase-5-make-nomnom-handle-complex-questionsweek-89)
- [Phase 6: Make NomNom Extensible (Week 10)](#phase-6-make-nomnom-extensibleweek-10)
- [Phase 7: Extension Projects and Interview Prep (Week 11–12, Optional)](#phase-7-extension-projects-and-interview-prepweek-1112-optional)
- [Appendix A: Per-Phase Retrospective Template](#appendix-a-per-phase-retrospective-template)
- [Appendix B: Capability Stack Coverage Tracker](#appendix-b-capability-stack-coverage-tracker)
- [Appendix C: Skip List](#appendix-c-skip-list)

---

## Design Principles

Each Phase strictly follows three principles:

**1. NomNom product state first**
Each Phase starts by stating "what NomNom can currently do" and "what it can do after this Phase". Learning goals are concrete progress, not abstract knowledge points.

**2. 70% main line + 30% side line**
- **Main line**: Knowledge NomNom must use. Apply immediately to product after learning.
- **Side line**: Knowledge NomNom doesn't need but interviews ask about. Cover with an independent small exercise.

**3. Every Phase ends with a Retrospective**
30–60 minutes. Return to the capability stack map and reorganize what was learned by layer. **This builds both the "story chain" structure and the "tree" structure** — story chain when discussing projects, tree when explaining concepts.

---

## Prologue: Cognitive Map and Product Definition (Week 0)

> **Goal**: Establish a cognitive framework + put NomNom design on paper, giving the next 10 weeks direction.
> **Duration**: 1–2 days

### 0.0 Workspace Setup (Already Done in Phase 0)

The learning materials live inside the real NomNom repo. Structure:

```
NomNom/                                    ← real product repo
├── CLAUDE.md                              ← AI context (dual-purpose framing)
├── NomNom-Backend/
│   └── src/llm/                           ← ⭐ main learning target (12 files)
├── NomNom-iOS/                            ← iOS app (not in scope for learning)
├── docs/
│   ├── northstar/                         ← product vision (already exists)
│   ├── iterations/                        ← 09 past iterations + future (10+) retros
│   └── learning/                          ← LLM Harnessing learning plan
│       ├── 00_roadmap/                    ← this document + capability stack reference
│       ├── 01_capability_profile/         ← Iona_Capability_Profile.md
│       ├── 03_phase_retrospectives/       ← End-of-Phase retros (populated as I go)
│       └── 05_learning_notes/             ← deep concept notes
└── learning_lab/                          ← Phase 1-6 hands-on sandbox (separate from production)
```

**Mapping** (what each folder holds):

| Directory | Purpose | Who Updates It |
|---|---|---|
| `docs/learning/00_roadmap/` | Learning roadmaps (this doc + reference) | Almost never; minor Phase notes added during journey |
| `docs/learning/01_capability_profile/` | 7-layer skill tracker | End of each Phase |
| `docs/learning/03_phase_retrospectives/` | Per-Phase retros | End of each Phase |
| `docs/learning/05_learning_notes/` | Deep concept notes | When a concept crystallizes |
| `learning_lab/` | Sandbox practice code | During each Phase |
| `NomNom-Backend/src/llm/` | ⭐ Production LLM code to be understood + refactored | After learning_lab work each Phase |
| `docs/iterations/10+/` | Real product iteration records (post-learning refactors) | After each Phase's refactor work |

**Claude Code usage**: Run from repo root. `CLAUDE.md` is auto-loaded — it includes dual-purpose framing and Phase-aware AI behavior rules.

### 0.1 Cognitive Map

**Definition of LLM Harnessing**: The capability stack for treating an LLM as an unreliable but powerful component, and using engineering techniques to "harness" it into a reliable system.

**Capability stack (your checklist)**:

```
┌─────────────────────────────────────┐
│  Layer 6: Multi-Agent Coordination  │
├─────────────────────────────────────┤
│  Layer 5: Agent Engineering         │
├─────────────────────────────────────┤
│  Layer 4: Reliability Engineering   │
├─────────────────────────────────────┤
│  Layer 3: Augmentation              │
├─────────────────────────────────────┤
│  Layer 2: Output Control            │
├─────────────────────────────────────┤
│  Layer 1: Prompt Engineering        │
├─────────────────────────────────────┤
│  Layer 0: API Mastery               │
└─────────────────────────────────────┘
```

**Mapping of NomNom phases to capability layers** (skim now, no need to memorize):

| NomNom Phase | Primary Layers Hit |
|---|---|
| Phase 1 (MVP food recognition) | Layer 0, 1, 3 (multimodal) |
| Phase 2 (output stabilization) | Layer 2, 4 |
| Phase 3 (knowledge expansion) | Layer 3 (RAG, PDF) |
| Phase 4 (optimization) | Layer 0 advanced, Layer 1 optimization |
| Phase 5 (complex questions) | Layer 5, 6 |
| Phase 6 (standardization) | Layer 3 engineering |

### 0.2 Required Reading (1.5 hours total)

Read in order:
1. **Anthropic — Building Effective Agents** (30 minutes)
   - https://www.anthropic.com/research/building-effective-agents
   - First read: only look at the framework — workflow vs. agent, when not to use an agent
2. **Chip Huyen — Building LLM Applications for Production** (45 minutes)
   - https://huyenchip.com/2023/04/11/llm-engineering.html
3. **Karpathy — LLM OS Concept Diagram** (15 minutes)
   - Search "Karpathy LLM OS"

### 0.3 NomNom Reality Check (Core Action, 1 hour)

> **Important context**: NomNom is **not** being built from scratch. By the start of this learning journey (May 10, 2026), the product is already at **Iteration 09 (Food Diary)**, with a working iOS app, FastAPI backend, RAG, semantic cache, and an LLM module at `NomNom-Backend/src/llm/`. The challenge isn't to build it — it's to **understand the LLM-related code I've already shipped with heavy AI assistance**.

#### What NomNom is today (May 2026)

- **Stack**: iOS (SwiftUI) + FastAPI backend + PostgreSQL with pgvector + Anthropic Claude API
- **Live features** (see `docs/northstar/FEATURES.md`): auth, photo→nutrition analysis, food log saving, food correction, today's logs, meal categorization, settings, semantic cache, RAG meal recommendations, food diary calendar
- **Architecture** (see `docs/northstar/ARCHITECTURE.md`): standard FastAPI 3-tier with an `src/llm/` module orchestrating all Claude calls
- **Iteration history**: 9 iterations complete (Iterations 01–09 in `docs/iterations/`)
- **Honest self-assessment**: most of `src/llm/` was AI-assisted; design choices are not deeply owned

#### The LLM module inventory (the actual learning target)

`NomNom-Backend/src/llm/` contains ~1,500 lines across 12 files. Each file corresponds to a Phase of the roadmap:

| File | Lines | Phase | What "understood" means |
|---|---|---|---|
| `client.py` | 154 | Phase 1 | Defend the retry/timeout/fallback design |
| `prompt_engine.py` | 138 | Phase 1 | Defend the prompt template architecture |
| `prompts/` | — | Phase 1 | Defend each prompt's structure & techniques used |
| `parser.py` | 154 | Phase 2 | Explain why not just `json.loads()` |
| `guardrails.py` | 141 | Phase 2 | List validation rules + reasoning behind each |
| `tools.py` | 88 | Phase 2/3 | Walk through the full tool_use flow |
| `evaluator.py` | 158 | Phase 2 | Critique the grader design; identify improvements |
| `embedding.py` | 94 | Phase 3 | Justify the embedding model + dimension choice |
| `cache.py` | 187 | Phase 3 | Defend the cosine 0.15 threshold |
| `seed_knowledge.py` | 41 | Phase 3 | Explain how the RAG knowledge base is constructed |
| `router.py` | 97 | Phase 4 | Explain the routing decision logic |
| `rate_limiter.py` | 85 | Phase 4 | Justify the rate-limiting algorithm choice |
| `logger.py` | 163 | Phase 4 | Defend the observability design |

#### Self-assessment at Phase 0 start

**My current understanding across all 12 files: 0/5**.

This is not modesty — it's the literal starting point. By the end of Phase 6, every file in this table should have my understanding at 4/5 or 5/5, with the "What 'understood' means" column as the bar.

#### What this changes about how each Phase works

Each Phase no longer means "build something new from scratch". It means **two coordinated activities**:

1. **In `learning_lab/`**: hand-write minimal demos of the Phase's concepts (skip Claude Code for this part)
2. **In `NomNom-Backend/src/llm/`**: deeply review and refactor the corresponding production files, applying what I just learned

Each Phase section below now includes two new subsections to make this concrete:
- **Existing Code Touched This Phase** — which production files I'll be reviewing
- **Refactor Plan (after Phase)** — what concrete changes I'll bring back to production

#### No `NomNom_v1_spec.md` needed

The original roadmap suggested writing a separate `NomNom_v1_spec.md`. **Skipped**. The product already exists and has its own product documentation (`docs/northstar/`). This roadmap is the only learning-track document needed — everything Phase-related lives here.

### 0.4 Build Capability Profile (30 minutes)

Located at `docs/learning/01_capability_profile/Iona_Capability_Profile.md`.

Track 7 layers, current vs. target, with evidence required at any score ≥ 3:

```markdown
# Iona's LLM Harnessing Capability Profile

## Layer 0: API Mastery
- Current: 0/5
- Target by end of plan: 4/5
- Evidence: (empty, fill after completing Phases)

## Layer 1: Prompt Engineering
- Current: 0/5
- Target: 4/5
- Evidence:

## Layer 2: Output Control
- Current: 0/5
- Target: 4/5
- Evidence:

## Layer 3: Augmentation
- Current: 0/5
- Target: 5/5  ← NomNom main battlefield
- Evidence:

## Layer 4: Reliability Engineering
- Current: 1/5  ← Statistics/RecSys background gives a head start
- Target: 5/5  ← This is your differentiator
- Evidence:

## Layer 5: Agent Engineering
- Current: 0/5
- Target: 4/5
- Evidence:

## Layer 6: Multi-Agent Coordination
- Current: 0/5
- Target: 3/5  ← Knowing the concept + being able to articulate it is enough
- Evidence:

## My Differentiator
(One sentence about which layer you're stronger at than others, and why.)
```

Update once per Phase.

### 0.5 Two Disciplines That Span the Entire Journey

1. **Every learning item must be one you can explain on a whiteboard without Claude Code**. Claude Code is a co-pilot, not a substitute.
2. **At least one "hard mode" session per week**: Write a small demo without Claude Code.

### Prologue Acceptance

- [ ] Workspace verified: `docs/learning/` structure in place inside NomNom repo
- [ ] Finished reading the 3 must-reads (with notes in `05_learning_notes/`)
- [ ] NomNom Reality Check section (0.3) read — I can recite the 12-file inventory and which Phase touches which file
- [ ] `Iona_Capability_Profile.md` built, with current/target for each layer
- [ ] Can explain LLM Harnessing in 30 seconds
- [ ] `CLAUDE.md` updated with dual-purpose framing

---

## Existing Code × Phase Mapping (Global Index)

A quick-reference table to know, at any moment in the journey, which production files I should be deeply reviewing in the current Phase.

| File | Lines | Phase | What it does | What "5/5 understood" means |
|---|---|---|---|---|
| `client.py` | 154 | Phase 1 | Wraps `AsyncAnthropic` with retry/timeout/fallback | Defend the retry count (2), backoff (1s→2s), and recursive fallback design |
| `prompt_engine.py` | 138 | Phase 1 | Prompt template system | Defend the template architecture; explain variable injection |
| `prompts/` (folder) | — | Phase 1 | Actual prompt templates used in production | Explain each prompt's structure & which techniques it uses |
| `parser.py` | 154 | Phase 2 | Parses Claude's structured output | Explain why dedicated parser vs. naked `json.loads()` |
| `guardrails.py` | 141 | Phase 2 | Validates LLM output (semantic checks on food data) | List all validation rules + business reasoning for each |
| `tools.py` | 88 | Phase 2/3 | Tool use definitions and dispatching | Walk through one full tool_use flow on the whiteboard |
| `evaluator.py` | 158 | Phase 2 | Eval system for LLM output quality | Critique the current grader; identify what's code-based vs. model-based |
| `embedding.py` | 94 | Phase 3 | Sentence-transformers embedding wrapper | Justify model choice (`all-MiniLM-L6-v2`) & 384-dim |
| `cache.py` | 187 | Phase 3 | Semantic cache via pgvector | Defend cosine 0.15 threshold; explain cache-hit/miss logic |
| `seed_knowledge.py` | 41 | Phase 3 | Seeds RAG knowledge base | Explain KB construction; chunking strategy |
| `router.py` | 97 | Phase 4 | Routes requests (likely model tiering) | Explain decision logic; defend the routing rules |
| `rate_limiter.py` | 85 | Phase 4 | API rate limiting | Justify algorithm (token bucket? leaky bucket?) |
| `logger.py` | 163 | Phase 4 | LLM call observability | Defend the structured logging design |

**Total**: ~1,500 lines of production LLM code.

**Phase 5–6** don't map to existing files — they require **building new modules** (`workflow/` or `agent/` in Phase 5, MCP server in Phase 6). These are net-new development, not refactor work.

**Reading this table during the journey**: at any time, ask "what Phase am I in?" → look up that row → those are the files to focus on. The Phase-by-Phase sections below give the detail.

## Phase 1: NomNom MVP — Make It Recognize Food (Week 1–2) ✅ COMPLETE

**Completion Date:** June 4, 2026

> **NomNom current state**: Nothing yet
> **State after Phase**: Comprehensive understanding of LLM API, prompt engineering, and reliability patterns
> **Core question**: "How do I get Claude to understand the image and output the format I want?"
> **Answer**: Via templated prompts (Jinja2), reliable API calls (retry/timeout/fallback), and multimodal image input

### Phase 1 Completion Summary

**What was built:**
- 15 Jupyter notebooks: API fundamentals, prompt engineering, output control, augmentation, agents
- 3 project directories: MCP server, Claude Code labs, hooks
- 2 deep code reviews: client.py (reliability), prompt_engine.py (templating)
- NomNom v0.5 sandbox capstone: Full LLM pipeline demonstration

**Key insight learned:**
Prompts are product assets (10x change frequency) — should be separated from infrastructure code via templating. This architectural decision enables non-engineers (product, PMs) to iterate without touching Python.

**Capability progression:**
- Layer 0 (API): 1/5 → 4/5 ✅
- Layer 1 (Prompt Eng): 1/5 → 3/5 ✅
- Layer 2-5: 0/5 → 1-2/5 (foundation laid)

**Snapshot:** `docs/learning/01_capability_profile/Iona_Capability_Profile_phase1_20260604.md`
**Retrospective:** `docs/learning/03_phase_retrospectives/phase_1_retro.md`

### Phase 1 Main Line: Get It Working

> **Time budget (10 working days)**:
> - **Days 1–5**: Concept learning (in `learning_lab/`)
> - **Days 6–7**: Code review of existing production files
> - **Days 8–9**: Sandbox capstone (NomNom v0.5 hand-written)
> - **Day 10**: Production refactor (apply learning to `NomNom-Backend/src/llm/`)

#### Week 1: Concept Learning (in `learning_lab/`)

**Day 1–2: API Quickstart + Model Selection**

- Sign up for Anthropic API, run through Quickstart
- Understand messages structure, separate `system` parameter, `max_tokens`
- **`stop_reason` field deep-dive** (key signal for the agent loop, used repeatedly from Phase 2):
  - `end_turn`: Model finishes naturally (most common)
  - `max_tokens`: Hit token limit and got truncated (either raise the limit, or make the prompt require brevity)
  - `tool_use`: Model wants to call a tool (this is the "should I continue?" signal in your agent loop)
  - `stop_sequence`: Hit a stop sequence you set (commonly used for structured output)
- **Model family**: Opus (smartest, expensive) / Sonnet (balanced) / Haiku (fast, cheap)
  - **NomNom decision context**: Production currently uses Sonnet — you'll defend or revise this in Phase 4
- **Core parameters**: `temperature`, `max_tokens`, `stop_sequences`

All practice goes in `learning_lab/phase_1/day1_2_api_basics.py`.

**Day 3: Multi-Turn Conversation Basics + Streaming (side line)**

- Key fact: API stores no state. Each request is independent.
- Write two helpers: `add_user_message`, `add_assistant_message`
- Write a CLI multi-turn chat script (don't connect to NomNom yet)
- **Why learn this first**: Future agent loop skeleton is exactly these 30 lines of code
- **Side line (afternoon)**: Streaming basics — `client.messages.stream()` and event types (`message_start`, `content_block_delta`, `message_stop`). Write a streaming version of the chat script.

Output: `learning_lab/phase_1/day3_multi_turn.py` and `day3_streaming.py`.

**Day 4: Multimodal — Make Claude See**

This is the core of NomNom.
- Image block structure: base64 encoding + media_type
- Write a minimal CLI: input food photo path → model outputs text description
- Key insight: **multimodal accuracy is extremely dependent on prompt quality** — simple prompts fail. Use step-by-step instructions and explicit analysis frameworks.
- Try: Same photo with three prompt detail levels, compare output quality.

Output: `learning_lab/phase_1/day4_multimodal.py`.

**Day 5: Deep Read of Prompt Engineering Documentation**

Read the [Anthropic Prompt Engineering documentation](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview) in this order:
1. Be clear and direct
2. Use examples (multishot prompting)
3. Let Claude think (Chain of Thought)
4. Use XML tags
5. Give Claude a role (system prompts)
6. Prefill Claude's response
7. Chain complex prompts

For each technique, write a 2-line note in `learning_lab/phase_1/day5_prompt_techniques.md`: what it is, when to use it.

**Side line (afternoon, optional)**: Brief look at OpenAI API for comparison — interface design differences (system position, tool use schema, streaming format). In interviews, articulating differences between two providers is 100x more professional than "I prefer Claude".

#### Week 2: Code Review + Sandbox Capstone + Production Refactor

**Day 6: Code Review — `client.py` (154 lines)**

This is your first deep production code review. Goal: by end of day, you can defend every design choice in this file.

Process:
1. Open `NomNom-Backend/src/llm/client.py` in VS Code, read top to bottom
2. For each line you can't fully justify, add a comment with `# Q: <your question>` and your best-guess explanation
3. After reading, write `learning_lab/phase_1/day6_client_review.md` with:
   - **What this file does** (one paragraph in your words)
   - **Design choices I can now defend** (with reasoning)
   - **Design choices I still don't fully understand** (questions to research)
   - **Things I would change** (if any — and why)

Key questions to answer:
- Why 2 retries, not 3 or 5?
- Why exponential backoff (1s → 2s)? Why not constant or longer?
- Why is fallback implemented recursively, not as a loop?
- Why per-model `MODEL_CONFIG` dictionary with timeout + max_tokens?
- What happens if both primary and fallback fail?

**Day 7: Code Review — `prompt_engine.py` (138 lines) + `prompts/` folder**

Same process as Day 6, but for the prompt template system.

For `prompt_engine.py`:
- How are prompts loaded? From files? Embedded strings?
- How are variables injected? f-strings? Jinja? Custom?
- Why a class/module structure vs. plain function?

For each file in `prompts/`:
- Which prompt engineering techniques does it use? (XML tags? CoT? multishot? role?)
- Is the structure clear and intentional, or accidental?
- What would I change?

Output: `learning_lab/phase_1/day7_prompt_engine_review.md` + a per-prompt technique audit.

**Day 8–9: Sandbox Capstone — NomNom v0.5 hand-written**

Build a **minimal CLI version of NomNom from scratch**, with no Claude Code assistance. Goal: prove I can write the prompt + API flow myself, not just review someone else's.

- CLI: `python nomnom_v05.py <photo_path>`
- Output: markdown-formatted nutrition data
- Must use at least: system prompt with role + multishot + CoT + XML tags
- Save under `learning_lab/phase_1/nomnom_v05_sandbox.py`

**Discipline**: Manually test 10 photos of different foods. Record which were accurate, which crashed. **This 10-photo set is the seed dataset for Phase 2 eval**.

Compare: how does your sandbox version differ from production `client.py` + `prompt_engine.py`? What did you do better? Worse?

**Day 10: Production Refactor — apply learning to `NomNom-Backend/src/llm/`**

Concrete changes to land in production:

- **`prompts/` folder**: refactor the food analysis prompt to explicitly use XML tags + role + CoT + multishot, with a header comment explaining the design
- **`client.py`**: add inline comments explaining retry/backoff decisions (don't change logic — just document what you can now defend)
- **`prompt_engine.py`**: minor cleanups only if needed; no major changes unless something is clearly wrong

Create `docs/iterations/10-llm-foundation-deepdive/` with:
- `PLAN.md`: what I planned to refactor (from Day 6–7 reviews)
- `SUMMARY.md`: what actually changed + before/after diff highlights
- Commit the production changes with a clear message

### Phase 1 Side Line — Already Embedded

Streaming basics (Day 3 afternoon) and OpenAI API comparison (Day 5 afternoon) are now folded into the main-line days. No separate side-line block needed.

### Phase 1 Retrospective (30 minutes)

Return to the capability stack and categorize this week's learnings:

| Learning Item | Layer | My Understanding (one sentence) |
|---|---|---|
| messages structure, API call | Layer 0 | … |
| temperature, max_tokens | Layer 0 | … |
| streaming events | Layer 0 | … |
| Multi-turn maintenance | Layer 0–1 | … |
| XML tags, CoT, multishot | Layer 1 | … |
| Image block + multimodal prompt | Layer 3 | … |

Update Capability Profile:
- Layer 0: 0/5 → 3/5 (evidence: NomNom v0.5 + streaming script)
- Layer 1: 0/5 → 3/5 (evidence: NomNom v0.5 used at least 4 prompt techniques)
- Layer 3: 0/5 → 2/5 (evidence: NomNom multimodal recognition)

### Phase 1 Acceptance

**Product Acceptance (NomNom v0.5)**:
- [ ] CLI script runs: input photo → output nutrition data
- [ ] Tested on 10 photos with recorded accuracy (gut score is fine; formal eval comes next phase)
- [ ] Used at least 3 of the prompt techniques (system prompt + multishot + CoT)
- [ ] Code can be explained line by line without Claude Code

**Capability Acceptance**:
- [ ] Can write a complete API call without consulting docs
- [ ] Can explain streaming event types
- [ ] Can articulate why NomNom uses Sonnet, not Haiku or Opus
- [ ] Capability Profile updated

---

## Phase 2: Make NomNom Not Crash (Week 3–4) ✅ COMPLETE

**Status:** ✅ Complete (June 5–8, 2026)

> **NomNom current state**: Recognizes food, but output is unstable (JSON occasionally crashes, no accuracy data, errors are silent)
> **State after Phase**: 100% valid JSON output, quantified accuracy metrics, ability to A/B test different prompts
> **Core question**: "How do I make the product stable enough to ship?"

> **Critical turning point**: This is the watershed from "personal project" to "engineering project". Eval isn't an afterthought — it's the core infrastructure of LLM engineering.

**Key Results:**
- ✅ tool_choice integrated (100% success rate on 30 edge cases)
- ✅ Eval pipeline built (code-based + model-based grading, staging pattern)
- ✅ Error messages improved (Claude-readable)
- ✅ Iteration docs created (docs/iterations/11-eval-pipeline/)

### Phase 2 Main Line: Stability Engineering

> **Time budget (10 working days)**:
> - **Days 1–5**: Concept learning (in `learning_lab/`)
> - **Days 6–7**: Code review of `parser.py`, `guardrails.py`, `tools.py`, `evaluator.py`
> - **Days 8–9**: Sandbox capstone (eval pipeline + v0 vs v1 comparison)
> - **Day 10**: Production refactor — land eval pipeline + tool_choice in `src/llm/`

#### Week 3: Concept Learning (in `learning_lab/`)

**Day 1: The Output Control Trio**

Practice these three closely related techniques together:
1. **Prefill assistant content**: Manually inject an assistant message to guide format
2. **Stop sequences**: Model halts when it generates a specified string
3. **Prefill + Stop combo**: Classic structured output — prefill `` ```json ``, stop `` ``` ``, model only outputs the JSON in between

In `learning_lab/phase_2/day1_output_control.py`, write 3 small demos.

**Day 2: First Eval Pipeline (core action)**

This is the first formal eval in the roadmap. Do it carefully.

**6-step eval workflow**:
1. Write initial prompt
2. Create eval dataset (test cases)
3. Insert dataset inputs into prompt template
4. Run LLM to get outputs
5. Use grader to score, compute average
6. Modify prompt based on scores, repeat

In sandbox: build a minimal eval framework around the Day 1 output control demos.

**Day 3: Test Dataset Generation**

- Hand-write vs. Claude-generated
- **Use Haiku to bulk-generate test cases**: prompt + prefill `` ```json `` + stop `` ``` ``
- Practice: Have Haiku generate 50 "hard-to-recognize food" descriptions ("translucent Vietnamese spring rolls", "blurred far-shot cake") — this becomes part of your Phase 2 dataset.

**Day 4: Code-Based Grading**

- `validate_json()`: parse success returns 10
- `validate_python()`: `ast.parse()`
- `validate_regex()`: `re.compile()`
- Build `learning_lab/phase_2/day4_code_graders.py` with a `validate_nutrition_json()` — check required fields, numeric value plausibility (calories > 0 and < 5000).

**Day 5: Model-Based Grading (LLM-as-judge) + Tool Use Basics**

Morning: Model-based grading
- Use Opus as grader to evaluate Sonnet's output
- **Key technique**: Have the grader output strengths / weaknesses / reasoning / score together — don't just output score
- Force grader output structured via JSON tool

Afternoon: Tool Use basics (read-only)
- Read Anthropic Tool Use documentation
- Understand how `tools` parameters, `tool_use` blocks, and `tool_result` blocks flow back and forth
- Learn JSON Schema syntax
- Don't implement yet — Day 8 will use it

#### Week 4: Code Review + Sandbox Capstone + Production Refactor

**Day 6: Code Review — `parser.py` (154 lines) + `guardrails.py` (141 lines)**

For `parser.py`:
- What does it handle that naked `json.loads()` doesn't? (Markdown fences? Whitespace? Multiple JSON blocks?)
- Are there edge cases it misses?
- Could it be replaced by tool_choice?

For `guardrails.py`:
- What are the full validation rules?
- Is each rule justified by a real failure mode you've seen, or speculative?
- Are error messages written for Claude to read (so Claude can self-correct)?

Write `learning_lab/phase_2/day6_parser_guardrails_review.md` with:
- A full inventory of validation rules + justifications
- A list of changes you'd make + reasoning

**Day 7: Code Review — `tools.py` (88 lines) + `evaluator.py` (158 lines)**

For `tools.py`:
- What tools are defined?
- Is there an actual tool_use loop, or just single-shot calls?
- How are tool errors fed back to Claude?

For `evaluator.py` — **this is the Layer 4 differentiator file. Spend extra time here**:
- Is the grader code-based, model-based, or hybrid?
- What's the test dataset? Where does it come from?
- Is the evaluator actually running in production / CI, or is it dormant?
- What would a strong eval pipeline look like vs. what's there now?

Write `learning_lab/phase_2/day7_tools_evaluator_review.md` — be thorough on evaluator. This file's review will guide your Day 10 refactor more than any other.

**Day 8–9: Sandbox Capstone — Eval Pipeline + v0 vs v1 Comparison**

Build a **real eval pipeline from scratch** in `learning_lab/phase_2/eval_pipeline/`:

- 30-photo test dataset (10 from Phase 1 + 20 new, manually annotated with ground truth)
- Code-based grader: JSON validity + numeric plausibility
- Model-based grader: recognition accuracy + estimation reasonableness, with structured output (strengths/weaknesses/reasoning/score)
- Combined score: `final_score = (model_score + code_score) / 2` (RecSys-style signal fusion)
- **Comparison run**: NomNom v0.5 prompt (Phase 1) vs. v1.0 prompt (with tool_choice forcing)
- Output: `eval_report_v05_vs_v10.md` with scores, parse failure rates, qualitative findings

This is your **portfolio's first eval case**. In interviews you can say: "I used an eval pipeline to drive NomNom's JSON parse failure from X% to 0% and recognition accuracy from Y to Z."

**Day 10: Production Refactor — land eval pipeline + tool_choice in `src/llm/`**

Concrete changes:
- **`parser.py`**: migrate from prefill+stop to `tool_choice` for stricter structured output (since `tools.py` already exists). Or, if `parser.py` is doing something parser can't replace, document why.
- **`guardrails.py`**: rewrite error messages to be "Claude-readable" — telling Claude what's wrong and how to fix it.
- **`evaluator.py`**: this is the big change. Bring the sandbox eval pipeline into production:
  - Add real grader functions (both code-based and model-based)
  - Add a real test dataset (move from `learning_lab/` into `NomNom-Backend/tests/eval/datasets/`)
  - Add a CLI command or pytest target so you can run eval before any prompt change
- **`tools.py`**: minor — add error handling per Day 9 design pattern if missing.

Create `docs/iterations/11-eval-pipeline/`:
- `PLAN.md`: refactor plan from Day 6–7 reviews
- `SUMMARY.md`: what changed, before/after metrics
- Include `eval_comparison_v05_vs_v10.md` from Day 8–9 here

### Phase 2 Side Line — Already Embedded

Tool use basics (Day 5 afternoon) and combined grading approach (Day 8–9 capstone) are now folded into the main line.

**Batch Tool concept (half-day, optional reading)** — Claude can call multiple tools in parallel within a single request. NomNom doesn't need it (single-image recognition), but understand the concept; useful for future multi-agent work.

### Phase 2 Retrospective

| Learning Item | Layer | Understanding |
|---|---|---|
| Prefill + stop sequence | Layer 2 | … |
| tool_choice forced structured | Layer 2 + 3 | … |
| 6-step eval workflow | Layer 4 | … |
| Code-based grading | Layer 4 | … |
| Model-based grading | Layer 4 | … |
| Tool use basics (schema, id pairing) | Layer 3 | … |
| Error message design principles | Layer 5 (agent robustness) | … |

Update Capability Profile:
- Layer 2: 0/5 → 4/5
- Layer 3: 2/5 → 3/5
- Layer 4: 1/5 → 4/5 (**This is your differentiator layer — emphasize evidence**)

### Phase 2 Acceptance

**Product Acceptance (NomNom v1.0)** ✅ ALL CRITERIA MET:
- ✅ tool_choice forces JSON output, 100% parse success on 30 test photos
- ✅ Complete eval pipeline code: dataset + code grader + model grader + report output
- ✅ v0.5 vs. v1.0 comparison report written, articulates what improved and why
- ✅ Can articulate the design logic of the model-based grader (why not just output score)

**Evidence:**
- `learning_lab/phase_2/08_capstone_v1_tool_choice.py` — v1.0 implementation
- `learning_lab/phase_2/09_capstone_comparison_report.py` — full eval + reporting
- `09_capstone_comparison_report.md` — comprehensive analysis
- `docs/iterations/11-eval-pipeline/` — iteration documentation
- Production changes in `NomNom-Backend/src/` (tool_choice + error messages)

**Capability Acceptance**:
- [ ] Can sketch the 6-step eval workflow on a whiteboard
- [ ] Can compare prefill+stop vs. tool_choice for structured output
- [ ] Can explain why tool error messages are "for Claude to read"
- [ ] Capability Profile: Layer 4 at least 4/5

---

## Phase 3: Make NomNom Smarter (Week 5–6) ✅ COMPLETE

**Status:** ✅ Complete (June 9–8, 2026)

> **NomNom current state**: Stable food recognition with nutrition output (Phase 2 complete)
> **State after Phase**: RAG pipeline + semantic cache functional; can find similar meals and avoid redundant API calls
> **Core question**: "How do I get Claude to use my own private data efficiently?"

**What was built:**
- Days 1–5: Multi-tool agents, PDF parsing, naive RAG, hybrid search (BM25+RRF), contextual retrieval + citations
- Days 6–7: Production code reviews (embedding.py, cache.py, seed_knowledge.py, tools.py)
- Days 8–9: Advanced RAG capstone with evaluation metrics (NDCG@5, MRR)
- Day 10: Production integration (7 bugs fixed, 5 files updated, semantic cache now functional)

**Key Results:**
- ✅ Semantic cache fixed (hardcoded bug removed, threshold enforced, tuned to 0.82)
- ✅ RAG pipeline implemented (hybrid search + RRF + contextual retrieval)
- ✅ Evaluation metrics integrated (NDCG@5, MRR for ranking quality)
- ✅ Iteration docs created (docs/iterations/12-semantic-cache-production/)
- ✅ Production integration complete (4 commits, all files compile, no deprecation warnings)

### Phase 3 Main Line: Full Augmentation Stack

> **Time budget (10 working days)**:
> - **Days 1–5**: Concept learning (in `learning_lab/`)
> - **Days 6–7**: Code review of `embedding.py`, `cache.py`, `seed_knowledge.py`, plus `tools.py` agent loop
> - **Days 8–9**: Sandbox capstone (hybrid search + reranking + citations RAG pipeline)
> - **Day 10**: Production refactor — land hybrid search + citations into `src/llm/`

#### Week 5: Concept Learning (in `learning_lab/`)

**Day 1: Multi-Tool + Agent Loop (Hand-Coded)**

- Practice multiple tools: `extract_nutrition_from_image`, `lookup_food_database`, `calculate_daily_total`
- **Hand-write a while loop for multi-turn tool calls — no frameworks**
  ```
  while True:
      response = call_claude(messages, tools)
      messages.append(assistant_message)
      if response.stop_reason != "tool_use":
          break
      for tool_use in response.tool_use_blocks:
          result = run_tool(tool_use.name, tool_use.input)
          messages.append(tool_result_message(tool_use.id, result))
  ```
- **One of the most important exercises in the roadmap. Must be written from scratch.**
- After it works, ask Claude Code to review.

Output: `learning_lab/phase_3/day1_agent_loop.py`.

**Day 2: PDF Support (Nutrition Label Parsing)**

- Document block + media_type `application/pdf`
- Claude reads text, charts, and tables from PDFs directly
- Write a `parse_nutrition_label_pdf(path)` function in `learning_lab/phase_3/day2_pdf.py`
- Test on 5 real product label PDFs

**Day 3: RAG Concepts + Chunking + Embeddings + Vector Search**

Combined day — these are tightly linked concepts:
- **Why RAG**: knowledge base too large for context
- **Chunking strategies**: size-based, structure-based, semantic-based
- **Embedding model concept** (Voyage AI, OpenAI, sentence-transformers options + tradeoffs)
- **Cosine similarity math** + simplest vector store (numpy or FAISS)
- Find a public nutrition manual (USDA FoodData Central) as RAG knowledge base
- Implement size-based + overlap chunking + embedding + naive cosine search

Output: `learning_lab/phase_3/day3_naive_rag.py` — a working end-to-end naive RAG.

**Day 4: BM25 + Hybrid Search + RRF + Reranking**

This day = **your RecSys background pays off**.
- **BM25 algorithm**: lexical search based on term frequency
- Why hybrid: Semantic search sometimes misses exact term matches; lexical sometimes misses synonyms
- **RRF (Reciprocal Rank Fusion)**: merge results from multiple sources — **exactly the multi-channel recall pattern in RecSys**
- **Reranking**: Use LLM to rerank top-K candidates

Build `learning_lab/phase_3/day4_hybrid_search.py`:
- Vector index + BM25 index
- RRF merge
- LLM rerank top 10 → top 3

**Day 5: Contextual Retrieval + Citations**

Morning: Contextual Retrieval
- Anthropic's technique: Add context to chunks before embedding via LLM
- Use case: Long documents where chunks lack context, hurting retrieval accuracy
- Try on the nutrition manual — measure recall before/after

Afternoon: Citations (RAG anti-hallucination killer)
- `"citations": {"enabled": true}` + add title to source
- Claude annotates each output with source location (PDF page or character position)
- **This is the killer feature for RAG productization** — users can verify
- Practice on a 5-question demo

#### Week 6: Code Review + Sandbox Capstone + Production Refactor

**Day 6: Code Review — `embedding.py` (94 lines) + `cache.py` (187 lines)**

For `embedding.py`:
- What model is used? Why this choice (e.g., `all-MiniLM-L6-v2`, 384-dim)?
- How are embeddings cached, if at all?
- Is batch behavior optimized?
- Cost/quality tradeoff vs. Voyage AI or OpenAI alternatives — which would you choose now?

For `cache.py` — semantic cache:
- Cosine 0.15 threshold — was this measured, or guessed? What's a "near miss"?
- How is cache hit/miss logged?
- Is there cache invalidation? TTL?
- How does it interact with `embedding.py`?

Write `learning_lab/phase_3/day6_embedding_cache_review.md`:
- Defend or refute the 0.15 threshold with reasoning (you may need to run a quick experiment with real cache hit data)
- A justified opinion on the embedding model choice
- Concrete improvements you'd ship

**Day 7: Code Review — `seed_knowledge.py` (41 lines) + `tools.py` (88 lines, agent loop angle)**

For `seed_knowledge.py`:
- What KB entries exist? How many?
- Chunking strategy? Where did the source data come from?
- Is the KB ever updated? How?

For `tools.py` (revisit from Phase 2 angle):
- Is there a real multi-tool agent loop, or single-shot tool use?
- How does it handle tool errors? (Especially after Day 5's contextual retrieval — does the LLM get useful feedback when retrieval fails?)

Output: `learning_lab/phase_3/day7_seed_knowledge_tools_review.md`.

**Day 8–9: Sandbox Capstone — Advanced RAG pipeline + eval**

Build a **complete advanced RAG pipeline from scratch** in `learning_lab/phase_3/advanced_rag/`:

- Source: nutrition manual PDF (real)
- Chunking: size-based with overlap + contextual retrieval (LLM adds context)
- Index: vector + BM25
- Query: hybrid search → RRF → top-10 → LLM rerank → top-3
- Generation: prompt assembly with retrieved chunks + citations enabled
- **Eval report**: 30 nutrition-related questions; measure NDCG@5, MRR, answer quality (model-graded)
- **Comparison**: simple cosine retrieval vs. hybrid + reranking — quantify the lift

Output: `learning_lab/phase_3/rag_eval_report.md` — your second portfolio artifact.

**Day 10: Production Refactor — land RAG improvements in `src/llm/`**

Concrete changes:
- **`cache.py`**: refine the cosine threshold based on Day 6 analysis; add citation metadata to cache entries so cached responses include sources
- **`seed_knowledge.py`**: expand KB if undersized; switch chunking to size-based-with-overlap if it isn't already; consider contextual retrieval
- **`embedding.py`**: probably keep MiniLM (right tradeoff for scale), but add doc comment explaining why over alternatives
- **New file (if needed)**: `pdf_parser.py` — production-grade nutrition label PDF parsing (from Day 2 sandbox)
- **New file (if needed)**: `hybrid_search.py` — hybrid BM25 + vector + RRF + rerank pipeline
- **Citations**: enable in the meal recommendation flow so users see which KB entries informed the suggestion

Create `docs/iterations/12-rag-upgrade/`:
- `PLAN.md` (from Day 6–7 reviews)
- `SUMMARY.md` with before/after retrieval accuracy metrics
- Include `rag_eval_report.md` from Day 8–9

### Phase 3 Side Line — Built-in Tools (~half day, reading only)

Knowing the built-in tools Anthropic provides is interview material. **Do not implement** — just understand.

| Tool | Use | Useful for NomNom? |
|---|---|---|
| **Web Search Tool** | Claude searches web autonomously | Optional — for "any new weight-loss research?", restrict to nih.gov |
| **Text Editor Tool** | File read, write, edit, delete | No — meant for coding agents |
| **Code Execution + Files API** | Claude runs Python in Docker | Future for nutrition data visualization |
| **Computer Use** (separate product) | Claude views screen, clicks mouse, types | No — skip (see Appendix C) |

**Web Search Tool key points**: `max_uses` limits total searches (default 5); `allowed_domains` restricts to trusted domains.

**Text Editor Tool key points**: Schema is a stub (just name + type); Claude expands internally. **Actual file ops you implement yourself** — schema only tells Claude the tool exists; you write the read/write code. This is one of the core mechanisms of products like Claude Code.

Phase 6 returns to make similar capabilities ecosystem-grade via MCP.

### Phase 3 Retrospective

| Learning Item | Layer | Understanding |
|---|---|---|
| Multi-tool agent loop (hand-coded) | Layer 3 + 5 | … |
| PDF support | Layer 3 | … |
| Chunking strategies | Layer 3 (RAG) | … |
| Embedding + vector search | Layer 3 (RAG) | … |
| BM25 + hybrid search | Layer 3 (RAG) | … |
| RRF + reranking | Layer 3 (RAG) | … |
| Contextual retrieval | Layer 3 (advanced RAG) | … |
| Citations | Layer 3 + 4 | … |

Update Capability Profile:
- Layer 3: 3/5 → 5/5 (NomNom v2.0 is strong evidence)
- Layer 5: 0/5 → 3/5 (hand-coded agent loop)

### Phase 3 Acceptance

**Product Acceptance (NomNom v2.0)**:
- [ ] Multi-tool agent loop calls multiple tools
- [ ] PDF nutrition label parsing works
- [ ] Complete RAG pipeline: hybrid search + reranking + citations
- [ ] RAG eval report written, comparing simple RAG vs. hybrid+rerank

**Capability Acceptance**:
- [ ] Can hand-write the agent loop pseudo-code on a whiteboard
- [ ] Can articulate why hybrid search beats vector-only (using RecSys lens)
- [ ] Can explain Citations' engineering value for RAG products
- [ ] Capability Profile: Layer 3 at least 5/5

---

## Phase 4: Make NomNom Cheap and Fast (Week 7) 🚀 STARTING

**Status:** 🚀 Starting June 10, 2026

> **NomNom current state**: Feature-rich but slow and expensive (Phase 3 complete)
> **State after Phase**: Faster response, lower cost, better user experience
> **Core question**: "How do I make the product affordable enough for users?"

**Coming up:**
- Days 1–2: Prompt caching, model tiering, streaming concepts
- Day 3: Code review4s (router.py, rate_limiter.py, logger.py)
- Day 4: Capstone (cost/latency baseline + optimization)
- Day 5: Production integration

### Phase 4 Main Line: Performance and Cost Engineering (~1 week)

> **Time budget (5 working days)**:
> - **Days 1–2**: Concept learning (caching + tiering + streaming basics) in `learning_lab/`
> - **Day 3**: Code review of `router.py`, `rate_limiter.py`, `logger.py`
> - **Day 4**: Sandbox capstone — cost/latency tracking + baseline measurement
> - **Day 5**: Production refactor — land caching + tiering + cost dashboard

#### Day 1: Prompt Caching + Model Tiering Concepts

Morning: Prompt Caching
- Cache unchanged system prompts and tool schemas; reuse on repeated requests
- Rules: cache lasts 1 hour; minimum 1024 tokens; max 4 breakpoints; any change before cached content invalidates the entire cache
- Content processing order: tools → system prompt → messages
- Verify cache hits: observe `cache_creation_input_tokens` vs. `cache_read_input_tokens`
- Practice: cache a long system prompt in `learning_lab/phase_4/day1_caching.py`

Afternoon: Model Tiering Framework

Build the decision framework for NomNom's task → model mapping:

| Task | Recommended Model | Reason |
|---|---|---|
| Food image recognition | Sonnet | Multimodal accuracy |
| JSON structure extraction | Haiku | Simple, save money |
| Nutrition knowledge RAG answer | Sonnet | Reasoning + synthesis |
| Complex advice (v3+) | Opus | High-quality reasoning |
| Eval grader | Opus | Deep judgment |
| Test dataset generation | Haiku | Fast, cheap |

In `learning_lab/phase_4/day1_tiering.md`, write the rationale for each row.

#### Day 2: Streaming + Cost & Latency Tracking Concepts

Morning: Streaming application
- Streaming basics (from Phase 1 Day 3 side line)
- Apply: real-time display "Recognizing... Querying nutrition database... Generating answer..."
- Use `client.messages.stream()` + `text_stream` property
- Practice in `learning_lab/phase_4/day2_streaming.py`

Afternoon: Cost & Latency Tracking
- What to log per call: tokens (input/output/cache), latency, model, cost (computed from pricing)
- Simple dashboard concept: aggregate by task type, time window
- **Side line concepts** (read-only, 30 min each):
  - **Extended Thinking** — for complex reasoning (`thinking_budget` ≥ 1024). NomNom doesn't need it yet; v3 might. Just understand when to enable.
  - **Fine-Grained Tool Calling** — streaming + tool use, disable JSON validation for speed. NomNom doesn't need it (batch task). Concept only.

#### Day 3: Code Review — `router.py`, `rate_limiter.py`, `logger.py`

For `router.py` (97 lines):
- Is it model tiering, or some other kind of routing?
- What's the decision logic — deterministic rules, LLM-driven, or both?
- How does it interact with `client.py`'s fallback mechanism?
- Is the routing as good as the Day 1 tiering table you wrote?

For `rate_limiter.py` (85 lines):
- What algorithm? Token bucket? Leaky bucket? Sliding window?
- Per-user or global?
- What happens on limit hit — fail, queue, throttle?
- Are there metrics to know if the limit is right?

For `logger.py` (163 lines):
- What's captured per call? Tokens? Latency? Model? **Cost?**
- Structured (JSON) or string-based?
- Where do logs go — file? DB? stdout?
- Can you query "what's daily spend per task type"?

Write `learning_lab/phase_4/day3_router_limiter_logger_review.md`.

#### Day 4: Sandbox Capstone — Cost & Latency Baseline

In `learning_lab/phase_4/baseline_measurement/`:
- Pick 20 representative requests across NomNom task types (image recognition, JSON extraction, RAG answer)
- Measure pre-optimization: cost, latency (p50, p95), per task type
- Generate `baseline_report.md` with the numbers

This baseline is what your Day 5 refactor will improve against.

#### Day 5: Production Refactor — land caching, tiering, cost dashboard

Concrete changes:
- **`router.py`**: refine routing rules per Day 1 tiering table — explicit mapping like "image recognition → Sonnet, JSON extraction → Haiku, meal recommendation → Sonnet". Document each choice.
- **`client.py`** (revisit from Phase 1): add prompt caching for long system prompts (the nutritionist role + tool schemas)
- **`logger.py`**: ensure `cost_usd` field per call. If missing, add it.
- **New: cost dashboard**. Build a script or endpoint that shows daily spend + p50/p95 latency per task type. This becomes interview gold.

After refactor, re-run Day 4 baseline measurement → produce **`docs/iterations/13-cost-and-latency/before_after_report.md`** with actual dollar/millisecond improvements.

**Capstone artifact**: "NomNom Cost & Latency Optimization Report" — for example: "I drove NomNom's average request cost from $0.05 to $0.018, p95 latency from 4.2s to 1.8s." **This data is interview gold**.

Create `docs/iterations/13-cost-and-latency/` with `PLAN.md` + `SUMMARY.md` + the before/after report.

### Phase 4 Side Line — Already Embedded

Extended Thinking and Fine-Grained Tool Calling are Day 2 afternoon reading.

### Phase 4 Retrospective

| Learning Item | Layer | Understanding |
|---|---|---|
| Prompt caching | Layer 0 advanced | … |
| Model tiering | Layer 0 + business | … |
| Streaming application | Layer 0 + UX | … |
| Cost tracking | Layer 0 + engineering | … |

Update Capability Profile:
- Layer 0: 3/5 → 4/5 (**Evidence: cache hit verification + model tiering decision report**)

### Phase 4 Acceptance

**Product Acceptance (NomNom v2.1)**:
- [ ] Prompt caching enabled, cache hit data observable
- [ ] At least 3 task types routed to different models (Haiku/Sonnet/Opus)
- [ ] Streaming implemented in CLI or UI
- [ ] Cost & latency comparison report: v2.0 vs. v2.1

**Capability Acceptance**:
- [ ] Can explain prompt caching invalidation rules
- [ ] Can articulate why a specific NomNom task should use Haiku not Sonnet
- [ ] Can diagnose cost optimization for an LLM product (where waste is, how to fix it)

---

## Phase 5: Make NomNom Handle Complex Questions (Week 8–9)

> **NomNom current state**: Fast, cheap, smart — but **only answers "what did I eat?", not "what should I eat?"**
> **State after Phase**: Can handle "what should I have for dinner if I'm on a weight-loss diet?"
> **Core question**: "When to use workflow? When to elevate to agent?"

> **Important stance**: Anthropic emphasizes "first workflow, then agent if needed". This Phase isn't about forcing NomNom to become an agent — it teaches you **how to make this decision**.

### Phase 5 Main Line: Workflow vs. Agent

> **Time budget (10 working days)**:
> - **Days 1–5**: Concept + sandbox — 5 patterns, workflow design, single-agent design (all in `learning_lab/`)
> - **Days 6–8**: Multi-agent side project (`tech_comparison_agent`) — **separate from NomNom**, lives in `learning_lab/` only
> - **Days 9–10**: Production refactor — bring workflow + single agent into `NomNom-Backend/src/llm/`

> **Important**: Phase 5 has **no existing files to refactor** in the strict sense. The current `NomNom-Backend/src/llm/` doesn't have a workflow module or agent module. This Phase is mostly **net-new production code**, informed by sandbox practice.

#### Week 8: Concept Learning + Sandbox (in `learning_lab/`)

**Day 1: Re-Read Building Effective Agents (2nd time) + 5 Patterns**

First time was Phase 0 framework view. Second time focuses on the 5 patterns:
1. **Prompt Chaining**: Break complex tasks into sequential steps
2. **Routing**: Classify user input into different pipelines
3. **Parallelization**: Execute subtasks in parallel, aggregate at end
4. **Orchestrator-Workers**: Dynamically split tasks, dispatch, aggregate
5. **Evaluator-Optimizer**: Producer outputs result → evaluator scores → reproduce if not enough

Companion: Run each pattern from [anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook) in `learning_lab/phase_5/day1_5_patterns/`.

**Day 2: Workflow Design — "What to Eat Today"**

User story: "I'm on a weight-loss diet; recommend a 600-calorie lunch."

**Design with workflow** (not agent), in `learning_lab/phase_5/day2_workflow_design.md`:
```
Step 1: Routing (intent recognition)
  - "what did I eat" → existing v2 pipeline
  - "what should I eat" → new pipeline

Step 2 (new pipeline): Prompt Chaining
  - Sub-step 1: Extract constraints (calorie target, dietary preferences, allergies)
  - Sub-step 2: RAG retrieves foods meeting constraints
  - Sub-step 3: Generate 3 candidate menus
  - Sub-step 4: Evaluator checks each candidate truly meets constraints
  - Sub-step 5: Output final recommendation
```

**Key discipline**: Each step is an independent LLM call (not one mega-prompt). This is the essence of prompt chaining.

**Day 3: Workflow Sandbox Implementation**

Implement the Day 2 design in `learning_lab/phase_5/day3_workflow_sandbox/`. Use suitable models per step (routing → Haiku, generation → Sonnet, evaluator → Opus).

This is the **reference implementation** — you'll port a cleaned-up version to production on Day 9.

**Day 4: Single Agent — When Workflow Isn't Enough?**

Discover workflow's limitation: User asks "I have eggs, onions, potatoes, and leftover rice in my fridge — what should I make tonight?"
- Workflow's fixed steps can't handle this — may need to list ingredient combos, then judge nutrition, then consider cook time
- **Use single agent**: Let Claude decide tool call order autonomously

Implement single-agent mode sandbox in `learning_lab/phase_5/day4_agent_sandbox/`:
- Tools: `check_pantry`, `search_recipes`, `calculate_nutrition`, `estimate_cooking_time`
- Agent loop lets Claude self-compose the calls (reuse the loop pattern from Phase 3 Day 1)

**Day 5: Workflow vs. Agent Decision Framework + Notes**

Write `docs/learning/05_learning_notes/workflow_vs_agent_decision.md`:

```markdown
# My Decision Framework

Ask in this order:
1. Can a single LLM call solve it? → Don't make agent/workflow
2. Steps known and fixed? → Workflow (chain/route/parallelize)
3. Need LLM autonomous path decisions? → Single agent
4. Single agent not enough? → Then consider Multi-agent

NomNom "weight-loss lunch recommendation" → workflow (steps fixed)
NomNom "fridge leftovers" → single agent (path uncertain)
```

**This document is interview gold** — it's exactly the kind of judgment-based answer that distinguishes senior from junior LLM engineers.

#### Week 9: Multi-Agent Side Project + Production Refactor

> Days 6–8 deeply learn multi-agent via a side project (not NomNom). Days 9–10 bring the workflow + agent work into NomNom production.

**Day 6: Multi-Agent Concepts**

Read:
1. **Anthropic — How we built our multi-agent research system** (1 hour, take notes)
   - Architecture, token usage vs. single agent, context passing, scenarios where they **don't** recommend it
2. **Cognition — Don't Build Multi-Agents** (30 minutes, opposing view)
   - Read alongside Anthropic's article for dialectical thinking

**Three multi-agent forms**:
- Orchestrator-workers (most practical)
- Conversational (multi-agent dialogues)
- Hierarchical (layered, **99% don't need**)

**Five engineering challenges**:
1. Context passing
2. Coordination
3. Error propagation
4. Cost explosion
5. Eval is extremely hard

Notes in `docs/learning/05_learning_notes/multi_agent_dialectic.md`.

**Day 7: Hands-On Side Project — `tech_comparison_agent`**

**This is for interviews, not NomNom.**

Task: User inputs "compare PyTorch vs. TensorFlow for production", system outputs a comparison report.

Location: `learning_lab/phase_5/tech_comparison_agent/`. This is a **standalone side project** — has its own README, runs independently of NomNom.

Architecture:
```
Orchestrator (Sonnet)  ── Use tool_choice to decompose dimensions
    ├──► Worker 1: Performance research  (Haiku + web_search)
    ├──► Worker 2: Ecosystem research    (Haiku + web_search)
    └──► Worker 3: Deployment research   (Haiku + web_search)
    ▼
Aggregator (Sonnet)  ── Synthesize report
```

Implementation key points (**hand-write, don't have Claude Code do it directly**):
- Orchestrator uses tool_choice to force `{tasks: [{dimension, query}]}`
- Workers in parallel (`asyncio.gather`)
- Context decision: Each worker gets only its sub-prompt; not the whole user input
- Aggregator no longer web_searches; only synthesizes

**Day 8: Multi-Agent Eval (Interview Bonus)**

Design 4-dimensional eval for the Day 7 demo:
1. Final report quality (Opus model-based)
2. Single worker answer quality
3. Orchestrator decomposition reasonableness
4. Cost & latency (programmatic recording)

**Comparison experiment**: Implement a workflow control group (hardcoded 3 dimensions called serially). Run on the same 5 test cases:

| Metric | Multi-Agent | Workflow |
|---|---|---|
| Avg final quality | ? | ? |
| Avg cost | ? | ? |
| Avg latency | ? | ? |

**This table will tell you the real value boundary of multi-agent** — workflow may win on some cases. This is engineering reality.

Save report as `learning_lab/phase_5/tech_comparison_agent/multi_agent_vs_workflow_report.md`.

**Day 9: Production Refactor — workflow integration**

Bring the Day 2–3 workflow design into `NomNom-Backend/src/llm/`:

- **New module**: `NomNom-Backend/src/llm/workflow/` containing:
  - `routing.py`: classifies user requests (what did I eat? what should I eat?)
  - `meal_recommendation_workflow.py`: the 5-sub-step chain
  - `__init__.py`
- **Integrate with existing recommendations**: locate the current meal recommendation entry point in NomNom and route through the new workflow when the request is "what should I eat"-style
- **Eval**: run the workflow against the Day 3 sandbox tests to confirm parity

Create `docs/iterations/14-meal-recommendation-workflow/` with `PLAN.md` + `SUMMARY.md`.

**Day 10: Production Refactor — single-agent feature**

Bring the Day 4 single-agent design into production as a new feature:

- **New module**: `NomNom-Backend/src/llm/agent/fridge_assistant.py`
- **Tools**: `check_pantry`, `search_recipes`, `calculate_nutrition`, `estimate_cooking_time` — implement against real DB/RAG where possible
- **Add a new API endpoint** in `NomNom-Backend/src/api/` for the fridge-leftovers feature
- **Add to iOS** is out of scope for this Phase (Phase 5 is about LLM logic, not iOS work)

Create `docs/iterations/15-fridge-leftovers-agent/` with `PLAN.md` + `SUMMARY.md`.

**Final artifact**: a 5-minute demo video showing all three NomNom modes:
- Recognition + RAG (Phase 1–3 work)
- Workflow-based meal recommendation (Day 9)
- Agent-based fridge leftovers (Day 10)

**This demo video becomes your deep-dive material for interviews**.

### Phase 5 Side Line — Embedded

Multi-agent (Days 6–8) is the side line. The `tech_comparison_agent` lives separately in `learning_lab/`, separately demoed for interview purposes.

### Phase 5 Retrospective

| Learning Item | Layer | Understanding |
|---|---|---|
| 5 workflow patterns | Layer 5 | … |
| Prompt chaining hands-on | Layer 5 | … |
| Routing | Layer 5 | … |
| Single agent loop (NomNom freestyle) | Layer 5 | … |
| Workflow vs. agent decision | Layer 5 + engineering judgment | … |
| Multi-agent 3 forms + 5 challenges | Layer 6 | … |
| Orchestrator-workers hands-on | Layer 6 | … |
| Multi-agent eval | Layer 4 + 6 | … |

Update Capability Profile:
- Layer 5: 3/5 → 5/5 (NomNom v3.0 + v3.1 dual evidence)
- Layer 6: 0/5 → 4/5 (tech_comparison_agent + decision framework)

### Phase 5 Acceptance

**Product Acceptance**:
- [ ] NomNom v3.0 (workflow mode) works
- [ ] NomNom v3.1 (single agent mode) works
- [ ] tech_comparison_agent project complete with README covering architecture, eval, comparison-vs-workflow
- [ ] 5-minute demo video shot

**Capability Acceptance**:
- [ ] Can articulate when to use each of the 5 patterns
- [ ] **Can explain in 60 seconds "when not to use multi-agent"** (interview kill question)
- [ ] Can explain why NomNom uses workflow for weight-loss recommendation but agent for fridge leftovers
- [ ] Capability Profile: Layer 5 at least 5/5, Layer 6 at least 4/5

---

## Phase 6: Make NomNom Extensible (Week 10)

> **NomNom current state**: Feature-complete, stable, with agent capability
> **State after Phase**: Callable by other systems (MCP server), with standardized interfaces
> **Core question**: "How do I make NomNom not just an app, but a service integrable into the ecosystem?"

### Phase 6 Main Line: MCP + Ecosystem-ization

> **Time budget (5 working days)**:
> - **Day 1**: MCP concepts + sandbox MCP server in `learning_lab/`
> - **Day 2**: Production MCP server — build `nomnom_mcp_server.py` in NomNom
> - **Day 3**: Claude Code integration + verification
> - **Day 4**: Final `src/llm/` whole-module audit (the most important production work of this Phase)
> - **Day 5**: Documentation pass + Claude Code study + capability profile final update

#### Day 1: MCP Concepts + Sandbox Server (in `learning_lab/`)

**MCP (Model Context Protocol)** = Anthropic-promoted protocol for standardized agent connectivity to external tools/data.

The trio:
- **Tools**: `@mcp.tool` decorator. Function signatures auto-generate JSON schemas.
- **Resources**: `@mcp.resource` decorator. **Proactively expose data to clients**.
  - Difference from tools: tools are reactive (Claude decides when); resources are proactive (clients read directly).
  - URI types: direct (`docs://documents`) and templated (`docs://documents/{doc_id}`)
- **Prompts**: `@mcpserver.prompt` decorator. High-quality prompt templates pre-baked by server authors. Clients expose them as slash commands.

**MCP Inspector**: `mcp dev server.py` launches a browser debugger.

Sandbox practice in `learning_lab/phase_6/day1_sandbox_mcp/`:
- Build a toy MCP server (3 fake tools, 1 resource, 1 prompt)
- Verify it with MCP Inspector
- Get comfortable with the protocol before touching NomNom

#### Day 2: Production MCP Server — `nomnom_mcp_server.py`

Implement the real NomNom MCP server. Location: `NomNom-Backend/src/llm/mcp/nomnom_mcp_server.py` (or wherever fits NomNom's structure).

Expose:
- **Tool**: `analyze_food_image(path)` - food recognition + nutrition (wraps existing analyze logic)
- **Tool**: `lookup_nutrition(food_name)` - knowledge base query (wraps existing RAG)
- **Tool**: `recommend_meal(constraints)` - meal recommendation (wraps Phase 5 workflow)
- **Resource**: `nomnom://foods/{food_id}` - expose recognized food data
- **Resource**: `nomnom://history` - user history (if available)
- **Prompt**: `daily_summary` - pre-built daily summary template

The MCP server is a **thin adapter** — it should not reimplement any logic. It calls into existing `src/llm/` modules.

#### Day 3: Claude Code Integration + Verification

Connect NomNom MCP server to Claude Code:
```
claude mcp add nomnom <startup-command>
```

Now you can use NomNom's features directly in Claude Code. **This is the real shape of productization** — your product becomes a service in the Claude ecosystem.

Verification checklist:
- [ ] Claude Code can list NomNom tools
- [ ] `analyze_food_image` works with a local photo
- [ ] `lookup_nutrition` returns RAG-backed answers with citations
- [ ] `recommend_meal` invokes the workflow
- [ ] Resources can be browsed

Create `docs/iterations/16-mcp-server/` with `PLAN.md` + `SUMMARY.md` + setup instructions.

#### Day 4: Whole-Module `src/llm/` Audit (Most Important Production Day)

This is the **single most important day of the entire 10-week journey**. Step back and re-evaluate the whole `src/llm/` module.

Per-file checklist (revisit each of the 12 files):

| File | Q1: Do I now understand it fully? | Q2: Any leftover opacity? | Q3: Any change I want to make? |
|---|---|---|---|
| `client.py` | (after Phase 1) | | |
| `prompt_engine.py` | (after Phase 1) | | |
| `prompts/` | (after Phase 1) | | |
| `parser.py` | (after Phase 2) | | |
| `guardrails.py` | (after Phase 2) | | |
| `tools.py` | (after Phase 2/3) | | |
| `evaluator.py` | (after Phase 2) | | |
| `embedding.py` | (after Phase 3) | | |
| `cache.py` | (after Phase 3) | | |
| `seed_knowledge.py` | (after Phase 3) | | |
| `router.py` | (after Phase 4) | | |
| `rate_limiter.py` | (after Phase 4) | | |
| `logger.py` | (after Phase 4) | | |

For any file with "leftover opacity": **today is the day to resolve it**. After today, every file must be 4/5 or 5/5.

Make the changes. Commit each as a separate small commit so the audit is traceable.

Create `docs/iterations/17-final-audit/SUMMARY.md` summarizing what changed and what didn't.

#### Day 5: Documentation Pass + Claude Code Study + Capability Profile Final

**Morning: Documentation pass**

Update `docs/northstar/ARCHITECTURE.md` to reflect the post-learning state of `src/llm/`. Add a **"Design Decisions"** section that captures the rationale for each key file's design — this section didn't exist before; it does now because you can defend each choice.

**Afternoon: Study Claude Code as a reference implementation**

Now with full LLM Harnessing knowledge, look back at Claude Code, the industrial-grade autonomous coding agent. Each mechanism corresponds to concepts you've learned:

| Claude Code Mechanism | Capability Stack |
|---|---|
| `CLAUDE.md` | Layer 1: project-level system prompt |
| Slash commands | Layer 1: Prompt template engineering |
| Subagents | Layer 6: Orchestrator-workers |
| Hooks | Layer 5: Agent lifecycle control |
| Plan mode / Thinking | Layer 5: ReAct / Plan-and-Execute |
| Memory (project / local / user) | Layer 5: Multi-tier context management |
| MCP servers | Layer 3: Standardized tool use |

**Advanced techniques to try**:
- **Git worktrees + multiple Claude Code instances in parallel**: For complex tasks, give different sub-tasks different worktrees
- **Custom slash commands**: Write markdown templates in `.claude/commands/` to crystallize high-frequency workflows
- **Three-step prompting**: (1) find files (2) produce a plan (3) implement

**End of day: Capability Profile final update + 30-min walkthrough recording**

Update `Iona_Capability_Profile.md` to its final state. Every layer should hit its target.

Record a **30-minute walkthrough video** taking a viewer from `client.py` through `nomnom_mcp_server.py`, explaining every design choice. **This is the deep-dive that wins technical interviews.**

### Phase 6 Side Line — Reading List

**Claude Agent SDK** (half day, optional)
- Anthropic's official agent library
- Claude Code is built around this
- Run a quick demo to see the difference vs. your hand-written agent loop

**LangGraph** (skip — only learn if a future job needs it)
- Third-party graph-based agent workflow framework
- Skip reason: You've mastered Anthropic's native tooling
- Learn it when joining a project that already uses it

### Phase 6 Retrospective

| Learning Item | Layer | Understanding |
|---|---|---|
| MCP tools/resources/prompts | Layer 3 engineering | … |
| MCP Inspector debugging | Engineering practice | … |
| Productizing as MCP server | Ecosystem-ization | … |
| Claude Code internal mechanisms | Comprehensive Layer 0–6 | … |

Update Capability Profile:
- Layer 3: 5/5 (saturated)
- Layer 5: 5/5 (saturated)
- Overall: All layers ≥ 4/5

### Phase 6 Acceptance

**Product Acceptance (NomNom Complete)**:
- [ ] NomNom MCP server runnable
- [ ] Claude Code can call NomNom MCP
- [ ] Trio (tools + resources + prompts) each implemented at least once

**Capability Acceptance**:
- [ ] Can explain MCP's design philosophy (why this protocol is needed)
- [ ] Can articulate the difference between tool and resource
- [ ] Can connect any Claude Code behavior to a specific capability layer

**Overall Acceptance**:
- [ ] Capability Profile: All layers at 4+/5, at least 2 layers at 5/5
- [ ] NomNom complete README with architecture diagram, eval results, decision log
- [ ] Can give a 30-minute deep-dive of NomNom from v0.5 to v3.1

---

## Phase 7: Extension Projects and Interview Prep (Week 11–12, Optional)

> After Phase 6 you have a portfolio main project. These two weeks depend on your time and energy.

### Option A: Job-Search Multi-Agent System (Recommended)

**Background**: Memory states clearly that job search is a current priority. This project simultaneously serves interview portfolio and actual job search.

**Architecture**:
- **Job Search Agent**: Search matching roles based on preferences (web_search built-in tool)
- **JD Analysis Agent**: Extract key skills, culture, salary from each JD (reuse Phase 1 information extraction experience)
- **Resume Tailoring Agent**: Modify your resume bullets per JD
- **Cover Letter Agent**: Write customized cover letters
- **Orchestrator**: Coordinate the 4 agents, output the "Today's Job Search Action Pack"

**Eval**:
- Tailored resume vs. JD keyword match rate
- Bullet rewriting quality (model-based grader)
- Coverage of must-have skills

### Option B: BQ Simulation Agent

**Background**: BQ interviews are mandatory in career-switch interviews.

**Features**:
- Input your 5 STAR stories
- Agent plays interviewer, asks dynamic follow-ups, scores per leadership principles

**Eval**:
- Compare to real interviewer scoring; tune the grader prompt

**Bonus value**: Posting it on social media as "career switch journal" makes excellent content.

### Option C: Mock Interview Prep (Systematic)

No new project — focus on interview prep:
- Prepare every NomNom technical decision as a tellable story
- Prepare 8–10 high-frequency technical questions (how to write the agent loop, when to use multi-agent, how to eval RAG, etc.)
- Mock interviews with people, record video and rewatch
- Distill the Capability Profile into a one-page version for LinkedIn / resume

### Phase 7 Recommended Combinations

**If short on time**: Choose C, focus on interview prep
**If time is sufficient**: A + C combo
**If wanting to make content**: B + C combo

---

## Appendix A: Per-Phase Retrospective Template

Use this template at the end of each Phase, 30–60 minutes:

```markdown
# Phase X Retrospective

## 1. Specific skills I learned (categorized by capability stack)
| Learning Item | Layer | My Understanding (one sentence) | Where used in NomNom |
|---|---|---|---|
| ... | ... | ... | ... |

## 2. Explaining this Phase to a non-technical friend
(Within 200 words, articulate how NomNom progressed this Phase and why)

## 3. Explaining this Phase's technical decisions to an interviewer
(Within 300 words; pick 1–2 key decisions: why this choice, alternatives considered)

## 4. Capability Profile Update
- Layer X: old score → new score (evidence: ...)
- ...

## 5. What I'm most worried about for the next Phase
(Identify learning risks early)
```

---

## Appendix B: Capability Stack Coverage Tracker

Check off after completing each Phase. Final goal: all checked.

### Layer 0: API Mastery
- [ ] Messages structure, API call (Phase 1)
- [ ] System prompt as separate parameter (Phase 1)
- [ ] Temperature, max_tokens, stop_sequences (Phase 1)
- [ ] stop_reason 4 values (end_turn / max_tokens / tool_use / stop_sequence) (Phase 1)
- [ ] Multi-turn maintenance (Phase 1)
- [ ] Streaming events (Phase 1)
- [ ] Model family selection (Phase 1 + 4)
- [ ] Prompt caching (Phase 4)
- [ ] Cost tracking (Phase 4)

### Layer 1: Prompt Engineering
- [ ] Clear and direct (Phase 1)
- [ ] Examples / multishot (Phase 1)
- [ ] Chain of Thought (Phase 1)
- [ ] XML tags (Phase 1)
- [ ] System prompt / role (Phase 1)
- [ ] Prefill response (Phase 2)

### Layer 2: Output Control
- [ ] Stop sequences (Phase 2)
- [ ] Prefill + stop combo (Phase 2)
- [ ] tool_choice forced structured (Phase 2)

### Layer 3: Augmentation
- [ ] Tool use basics (Phase 2)
- [ ] Multi-tool agent loop (Phase 3)
- [ ] Tool error message design (Phase 2)
- [ ] Image multimodal (Phase 1)
- [ ] PDF support (Phase 3)
- [ ] Citations (Phase 3)
- [ ] Chunking strategies (Phase 3)
- [ ] Embedding + vector search (Phase 3)
- [ ] BM25 + hybrid search (Phase 3)
- [ ] RRF + reranking (Phase 3)
- [ ] Contextual retrieval (Phase 3)
- [ ] Web search built-in tool (Phase 3 side)
- [ ] Text editor built-in tool (Phase 3 side)
- [ ] Code execution (Phase 3 side)
- [ ] MCP tools/resources/prompts (Phase 6)
- [ ] Batch tool concept (Phase 2 side)

### Layer 4: Reliability Engineering
- [ ] 6-step eval workflow (Phase 2)
- [ ] Test dataset generation (Phase 2)
- [ ] Code-based grading (Phase 2)
- [ ] Model-based grading (Phase 2)
- [ ] Combined grading (Phase 2 side)
- [ ] Multi-agent eval (Phase 5)

### Layer 5: Agent Engineering
- [ ] Agent loop (hand-coded) (Phase 3)
- [ ] 5 workflow patterns (Phase 5)
- [ ] Prompt chaining hands-on (Phase 5)
- [ ] Routing hands-on (Phase 5)
- [ ] Single agent hands-on (Phase 5)
- [ ] Workflow vs. agent decision (Phase 5)
- [ ] Extended thinking concept (Phase 4 side)
- [ ] Claude Code internals (Phase 6)
- [ ] Claude Agent SDK (Phase 6 side)

### Layer 6: Multi-Agent Coordination
- [ ] Three forms (Phase 5)
- [ ] Five engineering challenges (Phase 5)
- [ ] Orchestrator-workers hands-on (Phase 5)
- [ ] Multi-agent decision framework (Phase 5)
- [ ] Anthropic stance and opposing view (Phase 5)

---

## Appendix C: Skip List

These topics are in the notes but **not included** in this roadmap — intentionally:

| Topic | Skip Reason | When to Come Back |
|---|---|---|
| Computer Use | Non-core, only for QA testing | When doing UI automation testing |
| Fine-grained tool calling | Streaming micro-optimization | When doing real-time UI |
| Hierarchical multi-agent | 99% won't need | When doing enterprise scale |
| LangGraph deep dive | Anthropic native tooling is sufficient | When joining a project that uses LangGraph |
| Automated debugging (GitHub Action) | DevOps-leaning | After deploying to production |

---

## Timeline Overview

| Phase | Weeks | NomNom State | Primary Layer |
|---|---|---|---|
| 0 | Week 0 | Not started | Global cognition |
| 1 | Week 1–2 | MVP: recognizes food | Layer 0, 1, 3 |
| 2 | Week 3–4 | Stable: 100% valid output + eval | Layer 2, 4 |
| 3 | Week 5–6 | Smart: RAG + PDF + citations | Layer 3 full stack |
| 4 | Week 7 | Optimized: caching + model tiering | Layer 0 advanced |
| 5 | Week 8–9 | Complex: workflow + agent | Layer 5, 6 |
| 6 | Week 10 | Standardized: MCP server | Layer 3 engineering |
| 7 | Week 11–12 | Extension projects + interview prep | Comprehensive |

**Total: 10–12 weeks** (Phase 7 optional).

---

## Final Notes

Design philosophy of this roadmap:

1. **Every concept learned is immediately applied to NomNom** — learning and doing aren't separated
2. **Each Phase solves a real engineering problem** — not learning for learning's sake
3. **Side line ensures no interview blind spots** — what NomNom doesn't need but interviews ask, covered with independent small exercises
4. **Retrospective builds both "story chain" and "tree" structures** — can discuss projects and explain concepts
5. **Capability stack tracker is the final acceptance checklist** — ensures 100% knowledge coverage

After completion you should have:
- **Complete NomNom project** (from v0.5 to MCP server, your resume's core portfolio)
- **2 supporting projects** (tech_comparison_agent + job-search multi-agent or BQ agent)
- **Complete Capability Profile** (all layers at 4+/5)
- **30-minute deep-dive ability** (full engineering narrative of NomNom from need to implementation to optimization)
- **Interview kill-question reserves** (when not to use multi-agent, how to design eval, how to tune RAG)

Good luck.
