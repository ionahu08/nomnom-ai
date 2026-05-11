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

### 0.0 Workspace Setup (Do This First, 10 Minutes)

Every output over the next 10 weeks (specs, notes, retros, code) needs a stable physical location. Build the directory first so each Phase knows where things go.

**Recommended structure** (build locally):

```
~/Documents/NomNom_Learning/
├── README.md                              ← Project navigation (top-level intro)
├── 00_roadmap/
│   ├── roadmap_main_nomnom.md             ← Main roadmap (this document)
│   └── roadmap_reference.md               ← Capability stack version (reference)
├── 01_capability_profile/
│   └── Chris_Capability_Profile.md        ← To be created in 0.4
├── 02_nomnom_spec/
│   └── NomNom_v1_spec.md                  ← To be created in 0.3
├── 03_phase_retrospectives/               ← End-of-Phase retros
│   ├── phase_1_retro.md
│   ├── phase_2_retro.md
│   └── ...
└── 04_code/                               ← NomNom code + side practice
    ├── nomnom/                            ← Main project
    └── side_projects/                     ← tech_comparison_agent, etc.
```

**Mapping** (what each folder holds):

| Directory | Purpose | Who Updates It |
|---|---|---|
| `00_roadmap/` | Learning roadmaps (static) | Almost never |
| `01_capability_profile/` | Your capability profile | End of each Phase |
| `02_nomnom_spec/` | NomNom product spec | When the product evolves |
| `03_phase_retrospectives/` | Per-Phase retros | End of each Phase |
| `04_code/` | Code | Daily |
| `05_learning_notes/` | Notes taken during learning | when picking up new knownledge |

**Claude Code usage**: Each time you start Claude Code, `cd ~/Documents/NomNom_Learning/`. It reads all files directly — no manual upload needed.

**Project knowledge sync strategy**:
- ✅ Upload the two roadmaps in `00_roadmap/` (won't change for 10 weeks)
- ❌ Don't upload other directories (they change daily, version mismatches will appear)
- When you want Claude to see the latest spec or capability profile, **paste into the chat live** or **temporarily upload to that conversation**

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

### 0.3 NomNom Product Definition (Core Action, 2–3 hours)

**Write a `NomNom_v1_spec.md`** that answers:

**Target users**:
- Who will use NomNom? (Fitness people? Weight-loss seekers? Chronic disease management?)
- Pick **one primary scenario** (don't be greedy — MVP serves one user story).

**Core features (V1)**:
- User takes a photo of food → what does the system output?
- Example: Recognize food, estimate portion, give macros (calories, protein, fat, carbs).

**MVP boundary (what V1 does NOT do)**:
- V1 has no user system, no history, no nutritional advice
- V1 only does "one photo → one nutrition data response"

**Technical decisions (write down assumptions; verify later)**:
- Which Claude model? Why?
- Input: local image vs. URL?
- Output format: JSON? What schema?
- Where does it run? (CLI script, Streamlit, mobile app?)

**v2-v6 roadmap** (one sentence per version):
- v2: Stabilize output + eval (Phase 2)
- v3: Nutrition label PDF parsing + RAG knowledge base (Phase 3)
- v4: Performance optimization (Phase 4)
- v5: Open question handling ("what should I eat for weight loss?") (Phase 5)
- v6: MCP server-ization for use by other agents (Phase 6)

### 0.4 Build Capability Profile (30 minutes)

Create `Chris_Capability_Profile.md`:

```markdown
# Chris's LLM Harnessing Capability Profile

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

- [ ] Workspace `~/Documents/NomNom_Learning/` is built with all subdirectories
- [ ] Finished reading the 3 must-reads
- [ ] `NomNom_v1_spec.md` written, including target users, MVP features, technical decisions, v2-v6 roadmap
- [ ] `Chris_Capability_Profile.md` built, with current/target for each layer
- [ ] Can explain LLM Harnessing in 30 seconds

---

## Phase 1: NomNom MVP — Make It Recognize Food (Week 1–2)

> **NomNom current state**: Nothing yet
> **State after Phase**: CLI script — input a food photo path, output JSON nutrition data
> **Core question**: "How do I get Claude to understand the image and output the format I want?"

### Phase 1 Main Line: Get It Working

#### Week 1: API Basics + Make Claude See

**Day 1–2: API Quickstart + Model Selection**

- Sign up for Anthropic API, run through Quickstart
- Understand messages structure, separate `system` parameter, `max_tokens`
- **`stop_reason` field deep-dive** (key signal for the agent loop, used repeatedly from Phase 2):
  - `end_turn`: Model finishes naturally (most common)
  - `max_tokens`: Hit token limit and got truncated (either raise the limit, or make the prompt require brevity)
  - `tool_use`: Model wants to call a tool (this is the "should I continue?" signal in your agent loop)
  - `stop_sequence`: Hit a stop sequence you set (commonly used for structured output)
- **Model family**: Opus (smartest, expensive) / Sonnet (balanced) / Haiku (fast, cheap)
  - **NomNom decision**: Start with Sonnet — multimodal accuracy is acceptable, cost is manageable
  - Phase 4 will revisit and tier models
- **Core parameters**: `temperature`, `max_tokens`, `stop_sequences`
  - **NomNom decision**: Nutrition recognition needs stability; set temperature to 0 or 0.1

**Day 3: Multi-Turn Conversation Basics**

- Key fact: API stores no state. Each request is independent.
- Write two helpers: `add_user_message`, `add_assistant_message`
- Write a CLI multi-turn chat script (don't connect to NomNom yet)
- **Why learn this first**: Future agent loop skeleton is exactly these 30 lines of code

**Day 4–5: Multimodal — Make Claude See**

This is the core of NomNom.
- Image block structure: base64 encoding + media_type
- Write NomNom v0.1: Input food photo path → model outputs text description
- Key insight: **multimodal accuracy is extremely dependent on prompt quality** — simple prompts fail. Use step-by-step instructions and explicit analysis frameworks.
- Try: Same photo with three prompt detail levels, compare output quality.

#### Week 2: Basic Prompt Engineering + NomNom v0.5

**Day 6–7: Deep Read of Prompt Engineering Documentation**

Read the [Anthropic Prompt Engineering documentation](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview) in this order:
1. Be clear and direct
2. Use examples (multishot prompting)
3. Let Claude think (Chain of Thought)
4. Use XML tags
5. Give Claude a role (system prompts)
6. Prefill Claude's response
7. Chain complex prompts

Use NomNom as the test bed for each technique:
- "Use XML tags" → wrap image description task in `<food_image>`
- "Give Claude a role" → "You are a registered nutritionist"
- "Multishot" → give 1–2 food → nutrition data examples

**Day 8–10: NomNom v0.5 (Phase 1 capstone)**

Implement full v0.5:
- CLI input food photo path
- Output markdown-formatted: food name, estimated portion, macros, confidence notes
- Use system prompt with nutritionist role
- Use multishot with 2 examples
- Use CoT to make the model analyze image first, then give numbers

**Discipline**: Manually test 10 photos of different foods. Record which were accurate, which crashed. **This is the seed dataset for Phase 2 eval**.

### Phase 1 Side Line (~1 day)

What NomNom doesn't need but interviews require:

**Side 1: Streaming Basics (half day)**
- `client.messages.stream()` and event types (`message_start`, `content_block_delta`, `message_stop`)
- Write a streaming version chat script
- Why learn it: Future agent loops and tool use are based on this event model

**Side 2: Brief Look at OpenAI API (half day)**
- Interface design differences (system position, tool use schema, streaming format)
- In interviews, articulating differences between two providers is 100x more professional than "I prefer Claude"

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

## Phase 2: Make NomNom Not Crash (Week 3–4)

> **NomNom current state**: Recognizes food, but output is unstable (JSON occasionally crashes, no accuracy data, errors are silent)
> **State after Phase**: 100% valid JSON output, quantified accuracy metrics, ability to A/B test different prompts
> **Core question**: "How do I make the product stable enough to ship?"

> **Critical turning point**: This is the watershed from "personal project" to "engineering project". Eval isn't an afterthought — it's the core infrastructure of LLM engineering.

### Phase 2 Main Line: Stability Engineering

#### Week 3: Output Control + Eval Onboarding

**Day 1: The Output Control Trio**

Practice these three closely related techniques together:
1. **Prefill assistant content**: Manually inject an assistant message to guide format
2. **Stop sequences**: Model halts when it generates a specified string
3. **Prefill + Stop combo**: Classic structured output — prefill `` ```json ``, stop `` ``` ``, model only outputs the JSON in between

**Apply to NomNom**: Use this trio to make v0.5 output strict JSON. Test on 20 photos, record parse failure rate.

**Day 2: First Eval Pipeline (core action)**

This is the first formal eval in the roadmap. Do it carefully.

**6-step eval workflow**:
1. Write initial prompt
2. Create eval dataset (test cases)
3. Insert dataset inputs into prompt template
4. Run LLM to get outputs
5. Use grader to score, compute average
6. Modify prompt based on scores, repeat

**Apply to NomNom**:
- Dataset: 10 photos collected in Phase 1 + 20 more = 30 test photos
- Manually annotate ground truth for each photo (food name, calorie range estimate)
- Grader v1: Start code-based — JSON parse success = 10, fail = 0

**Day 3: Test Dataset Generation**

- Hand-write vs. Claude-generated
- **Use Haiku to bulk-generate test cases**: prompt + prefill `` ```json `` + stop `` ``` ``
- Apply to NomNom: Have Haiku generate 50 "hard-to-recognize food" descriptions ("translucent Vietnamese spring rolls", "blurred far-shot cake") to help you brainstorm test scenarios

**Day 4: Code-Based Grading**

- `validate_json()`: parse success returns 10
- `validate_python()`: `ast.parse()`
- `validate_regex()`: `re.compile()`
- Apply to NomNom: Write a `validate_nutrition_json()` — check required fields, numeric value plausibility (calories > 0 and < 5000)

**Day 5: Model-Based Grading (LLM-as-judge)**

- Use Opus as grader to evaluate Sonnet's output
- **Key technique**: Have the grader output strengths / weaknesses / reasoning / score together — don't just output score
- Force grader output structured via JSON tool
- Apply to NomNom: Write a grader for "nutrition estimation reasonableness"

#### Week 4: Tool Use + Error Handling (Layer 3 + Layer 5 starter)

**Day 6–7: Tool Use Basics**

- Read Anthropic Tool Use documentation
- Understand how `tools` parameters, `tool_use` blocks, and `tool_result` blocks flow back and forth
- Learn JSON Schema syntax

**Day 8: Tool-Forced Structured Output (NomNom upgrade)**

NomNom currently outputs JSON via prefill+stop. **Upgrade to tool_choice forcing**:
- Define a schema describing the nutrition structure
- Register the schema as a tool
- Use `tool_choice = {"type": "tool", "name": "extract_nutrition"}` to force calling
- The `input` Claude fills when calling the tool is JSON conforming to the schema
- **Much more reliable than prefill** — this is NomNom v1.0's output approach

**Day 9: Tool Function Error Handling Design**

The detail beginners overlook most:
- **Core insight: error messages raised by tool functions are read by Claude**
- Error messages should read like "instructions for use" — telling Claude what's wrong and how to fix it

```python
# Bad
raise ValueError("invalid input")

# Good
raise ValueError("date_format cannot be empty, expected format like '%Y-%m-%d'")
```

NomNom doesn't use many tool functions yet at this Phase, but **the design pattern must be established now** — the key to agent robustness.

**Day 10: NomNom v1.0 (Phase 2 capstone)**

Integrate everything from Phase 2:
- tool_choice forcing structured output
- 30-photo eval dataset
- Code-based grader (JSON validity, numeric plausibility)
- Model-based grader (recognition accuracy, estimation reasonableness)
- Run v0.5 vs. v1.0 comparison, output report

**This comparison report is your portfolio's first eval case**. In interviews you can directly say: "I used an eval pipeline to drive NomNom's JSON parse failure from X% to 0% and recognition accuracy from Y to Z."

### Phase 2 Side Line (~1 day)

**Side 1: Batch Tool Concept (half day)**
- Claude calls multiple tools in parallel within a single request
- NomNom doesn't need it (single-image recognition), but understand the concept
- Use case: future multi-agent

**Side 2: Combined Grading Approach (half day)**
- `final_score = (model_score + code_score) / 2`
- RecSys background is useful here — **this is multi-signal fusion ranking, same idea as hybrid search**
- Apply to NomNom: try adding combined score

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

**Product Acceptance (NomNom v1.0)**:
- [ ] tool_choice forces JSON output, 100% parse success on 30 test photos
- [ ] Complete eval pipeline code: dataset + code grader + model grader + report output
- [ ] v0.5 vs. v1.0 comparison report written, articulates what improved and why
- [ ] Can articulate the design logic of the model-based grader (why not just output score)

**Capability Acceptance**:
- [ ] Can sketch the 6-step eval workflow on a whiteboard
- [ ] Can compare prefill+stop vs. tool_choice for structured output
- [ ] Can explain why tool error messages are "for Claude to read"
- [ ] Capability Profile: Layer 4 at least 4/5

---

## Phase 3: Make NomNom Smarter (Week 5–6)

> **NomNom current state**: Stable food recognition with nutrition output
> **State after Phase**: Can parse nutrition label PDFs, can answer questions using a nutrition knowledge base, with cited sources
> **Core question**: "How do I get Claude to use my own private data?"

### Phase 3 Main Line: Full Augmentation Stack

#### Week 5: Tool Use Advanced + RAG Onboarding

**Day 1: Multi-Tool + Agent Loop (Hand-Coded)**

- Add multiple tools to NomNom: `extract_nutrition_from_image`, `lookup_food_database`, `calculate_daily_total`
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

**Day 2: PDF Support (NomNom Nutrition Label Parsing)**

- Document block + media_type `application/pdf`
- Claude reads text, charts, and tables from PDFs directly
- NomNom application: User uploads a nutrition label PDF (e.g., protein powder packaging), system extracts nutrition data automatically
- Write a `parse_nutrition_label_pdf(path)` function

**Day 3: RAG Concepts + Chunking Strategies**

- Why RAG: Nutrition knowledge base is too large to fit in context
- Three chunking strategies: size-based, structure-based, semantic-based
- NomNom data: Find a public nutrition manual (USDA FoodData Central PDF or doc) as RAG knowledge base
- Implement size-based + overlap chunking

**Day 4: Embeddings + Vector Search**

- Embedding model concept (use Voyage AI or open-source)
- Cosine similarity math
- Write the simplest vector store (numpy or FAISS)
- NomNom: Chunk the nutrition knowledge and store in vector store

**Day 5: Full RAG Flow (NomNom v2.0 Prototype)**

- 7-step RAG full flow: chunking → embedding → store → query → similarity search → assemble prompt → LLM
- NomNom v2.0: User asks "how much protein per 100g of chicken breast?" → RAG retrieves nutrition knowledge → Claude answers

#### Week 6: Advanced RAG + Citations

**Day 6: BM25 + Hybrid Search**

- BM25 algorithm: lexical search based on term frequency
- Why needed: Semantic search sometimes misses exact term matches
- **RecSys background is force-multiplier here** — hybrid search is exactly the multi-channel recall pattern in RecSys
- NomNom upgrade: vector + BM25 dual indexes

**Day 7: Reciprocal Rank Fusion + Reranking**

- RRF: Merge results from multiple search sources
- Reranking: Use LLM to rerank candidate results
- NomNom upgrade: retrieval → BM25 + vector → RRF merge → LLM reranking

**Day 8: Contextual Retrieval (Advanced Technique)**

- Anthropic's technique: Add context to chunks before embedding via LLM
- Use case: Long documents where chunks lack context, hurting retrieval accuracy
- NomNom application: Nutrition manual sections cross-reference each other; adding context improves recall

**Day 9: Citations (NomNom Anti-Hallucination Killer)**

- `"citations": {"enabled": true}` + add title to source
- Claude annotates each output with source location (PDF page or character position)
- NomNom application: Each nutrition recommendation tagged "Source: USDA FoodData Central, p.45"
- **This is the killer feature for RAG productization** — users can verify, dodging hallucination accusations

**Day 10: NomNom v2.0 (Phase 3 capstone)**

Integration:
- Multimodal food recognition (carry over v1.0)
- Nutrition label PDF parsing (new)
- Nutrition knowledge RAG system (new): hybrid search + reranking + citations
- User can ask "is the oil in the stir-fry I just photographed too much?" — the system synthesizes recognition + knowledge base answer + sources

**Write a RAG eval report**:
- 30 nutrition-related questions as dataset
- Retrieval accuracy (NDCG@5, MRR)
- Answer quality (model-based grading)
- Simple RAG vs. hybrid + reranking comparison

### Phase 3 Side Line (~half day)

**Side 1: Code Execution Concept (30 minutes)**
- Upload file → get file ID → Claude runs Python in Docker container
- NomNom doesn't need it now, but **future "nutrition data visualization" might use it**
- Know about Files API existence and usage

**Side 2: Built-in Tools Complete List (45 minutes)**

The built-in tools Anthropic provides — no need to implement schemas or functions. Interview question "what built-in tools does Anthropic provide?" requires a complete list.

| Tool | Use | Useful for NomNom? |
|---|---|---|
| **Web Search Tool** | Claude searches web autonomously | Optional — for "any new weight-loss research?", restrict to nih.gov |
| **Text Editor Tool** | File read, write, edit, delete | No — meant for coding agents |
| **Code Execution + Files API** | Claude runs Python in Docker | Future for nutrition data visualization |
| **Computer Use** (separate product) | Claude views screen, clicks mouse, types | No — skip (see Appendix C) |

**Web Search Tool key points**: `max_uses` limits total searches (default 5); `allowed_domains` restricts to trusted domains.

**Text Editor Tool key points**: Schema is a stub (just name + type); Claude expands internally. Schema string is versioned with model. **Actual file ops you implement yourself** — schema only tells Claude the tool exists; you write the read/write code. This is one of the core mechanisms of products like Claude Code.

**This Phase doesn't implement these — just understand the concepts**. Phase 6 returns to make similar capabilities ecosystem-grade via MCP.

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

## Phase 4: Make NomNom Cheap and Fast (Week 7)

> **NomNom current state**: Feature-rich but slow and expensive
> **State after Phase**: Faster response, lower cost, better user experience
> **Core question**: "How do I make the product affordable enough for users?"

### Phase 4 Main Line: Performance and Cost Engineering (~1 week)

#### Day 1–2: Prompt Caching

- Cache unchanged system prompts and tool schemas; reuse on repeated requests
- Rules: cache lasts 1 hour; minimum 1024 tokens; max 4 breakpoints; any change before cached content invalidates the entire cache
- Content processing order: tools → system prompt → messages
- NomNom application: Cache long system prompt (nutritionist role + output schema) + tool schemas
- Verify cache hits: observe `cache_creation_input_tokens` vs. `cache_read_input_tokens`

#### Day 3: Model Tiering

Revisit Phase 1's "NomNom uses Sonnet" decision and refine:

| Task | Recommended Model | Reason |
|---|---|---|
| Food image recognition | Sonnet | Multimodal accuracy |
| JSON structure extraction | Haiku | Simple, save money |
| Nutrition knowledge RAG answer | Sonnet | Reasoning + synthesis |
| Complex advice (v3+) | Opus | High-quality reasoning |
| Eval grader | Opus | Deep judgment |
| Test dataset generation | Haiku | Fast, cheap |

Implement: Route NomNom internal tasks to different models.

#### Day 4: Streaming in NomNom

- Streaming basics from Phase 1
- Apply to NomNom: After photo capture, real-time display "Recognizing... Querying nutrition database... Generating answer..."
- Use `client.messages.stream()` + `text_stream` property

#### Day 5: Cost & Latency Tracking

- Each request records: tokens (input/output/cache), latency, model, cost (computed from pricing)
- Build a dashboard (CLI table or simple Streamlit)
- Run NomNom v2.0 vs. v2.1 (optimized) comparison: how much cost/latency dropped

**This data is interview gold**: "I drove NomNom's average request cost from $0.05 to $0.018, p95 latency from 4.2s to 1.8s."

### Phase 4 Side Line (~half day)

**Side 1: Extended Thinking Concept (30 minutes)**
- Enable for complex reasoning. `thinking_budget` minimum 1024.
- NomNom v2.0 doesn't need it — nutrition recognition isn't deep reasoning
- v3 "open questions" might (Phase 5)
- When to enable: Prompt optimization can't reach target accuracy → enable thinking

**Side 2: Fine-Grained Tool Calling Concept (30 minutes)**
- Streaming + tool use, disable JSON validation for speed
- NomNom doesn't need it — batch task, not real-time
- Understand the concept

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

#### Week 8: 5 Patterns + Workflow Hands-On

**Day 1: Re-Read Building Effective Agents (2nd time)**

First time was Phase 0 framework view. Second time focuses on the 5 patterns:
1. **Prompt Chaining**: Break complex tasks into sequential steps
2. **Routing**: Classify user input into different pipelines
3. **Parallelization**: Execute subtasks in parallel, aggregate at end
4. **Orchestrator-Workers**: Dynamically split tasks, dispatch, aggregate
5. **Evaluator-Optimizer**: Producer outputs result → evaluator scores → reproduce if not enough

Companion: Run each pattern from [anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook).

**Day 2: NomNom v3.0 Design — Workflow for "What to Eat Today"**

User story: "I'm on a weight-loss diet; recommend a 600-calorie lunch."

**Implement with workflow** (not agent):
```
Step 1: Routing (intent recognition)
  - "what did I eat" → use v2 pipeline
  - "what should I eat" → use new pipeline

Step 2 (new pipeline): Prompt Chaining
  - Sub-step 1: Extract constraints (calorie target, dietary preferences, allergies)
  - Sub-step 2: RAG retrieves foods meeting constraints
  - Sub-step 3: Generate 3 candidate menus
  - Sub-step 4: Evaluator checks each candidate truly meets constraints
  - Sub-step 5: Output final recommendation
```

**Key discipline**: Each step is an independent LLM call (not one mega-prompt). This is the essence of prompt chaining.

**Day 3: Implement NomNom v3.0 Workflow**

Implement the design from Day 2. Use suitable models per step (routing → Haiku, generation → Sonnet, evaluator → Opus).

**Day 4: Single Agent — When Workflow Isn't Enough?**

Discover workflow's limitation: User asks "I have eggs, onions, potatoes, and leftover rice in my fridge — what should I make tonight?"
- Workflow's fixed steps can't handle this — may need to list ingredient combos, then judge nutrition, then consider cook time
- **Use single agent**: Let Claude decide tool call order autonomously

Implement NomNom v3.1 single agent mode (for freestyle cooking questions):
- Give the agent tools: `check_pantry`, `search_recipes`, `calculate_nutrition`, `estimate_cooking_time`
- Agent loop lets Claude self-compose the calls

**Day 5: Workflow vs. Agent Decision Framework (Your Interview Power Phrase)**

Write a `workflow_vs_agent_decision.md`:

```markdown
# My Decision Framework

Ask in this order:
1. Can a single LLM call solve it? → Don't make agent/workflow
2. Steps known and fixed? → Workflow (chain/route/parallelize)
3. Need LLM autonomous path decisions? → Single agent
4. Single agent not enough? → Then consider Multi-agent

NomNom v3.0 "weight-loss lunch recommendation" → workflow (steps fixed)
NomNom v3.1 "fridge leftovers" → single agent (path uncertain)
```

#### Week 9: Multi-Agent Special Topic (Side Line, but Deep)

> **Important: NomNom truly doesn't need multi-agent**. But interviews ask, so this Phase covers it deeply with an independent small project.

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

**Day 7: Hands-On — Independent Small Project `tech_comparison_agent`**

**This is for interviews, not NomNom.**

Task: User inputs "compare PyTorch vs. TensorFlow for production", system outputs a comparison report.

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

**Day 9–10: NomNom v3.0 + v3.1 Polish + Overall Demo**

Wrap up by getting Week 8's NomNom v3.0 (workflow) and v3.1 (single agent) running end-to-end.
Make a 5-minute demo video showing all three modes:
- v2.0: recognition + RAG (augmentation)
- v3.0: weight-loss recommendation (workflow)
- v3.1: fridge leftovers (single agent)

**This demo video becomes your deep-dive material for interviews**.

### Phase 5 Side Line (Embedded in Multi-Agent Special Topic)

Multi-agent week is the side line, deep-learned.

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

#### Day 1–2: MCP Concepts + Trio

**MCP (Model Context Protocol)** = Anthropic-promoted protocol for standardized agent connectivity to external tools/data.

The trio:
- **Tools**: `@mcp.tool` decorator. Function signatures auto-generate JSON schemas.
- **Resources**: `@mcp.resource` decorator. **Proactively expose data to clients**.
  - Difference from tools: tools are reactive (Claude decides when); resources are proactive (clients read directly).
  - URI types: direct (`docs://documents`) and templated (`docs://documents/{doc_id}`)
- **Prompts**: `@mcpserver.prompt` decorator. High-quality prompt templates pre-baked by server authors. Clients expose them as slash commands.

**MCP Inspector**: `mcp dev server.py` launches a browser debugger.

#### Day 3: Make NomNom an MCP Server

Implement `nomnom_mcp_server.py`:
- Tool: `analyze_food_image(path)` - food recognition + nutrition
- Tool: `lookup_nutrition(food_name)` - knowledge base query
- Tool: `recommend_meal(constraints)` - meal recommendation
- Resource: `nomnom://foods/{food_id}` - expose recognized food data
- Resource: `nomnom://history` - user history (if available)
- Prompt: `daily_summary` - pre-built daily summary template

#### Day 4: Claude Code Integration

Connect NomNom MCP server to Claude Code:
```
claude mcp add nomnom <startup-command>
```

Now you can use NomNom's features directly in Claude Code. **This is the real shape of productization** — your product becomes a service in the Claude ecosystem.

#### Day 5: Studying Claude Code Itself (Reference Implementation)

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

**Advanced techniques**:
- **Git worktrees + multiple Claude Code instances in parallel**: For complex tasks, give different sub-tasks different worktrees
- **Custom slash commands**: Write markdown templates in `.claude/commands/` to crystallize high-frequency workflows
- **Three-step prompting**: (1) find files (2) produce a plan (3) implement

### Phase 6 Side Line (~half day)

**Side 1: Claude Agent SDK (half day)**
- Anthropic's official agent library
- Claude Code is built around this
- Run a quick demo to see the difference vs. your hand-written agent loop

**Side 2: LangGraph (Optional, OK to Skip)**
- Third-party graph-based agent workflow framework
- Skip reason: You've mastered Anthropic's native tooling; LangGraph isn't required
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
