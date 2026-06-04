# Phase 1 Retrospective: NomNom MVP — Make It Recognize Food

**Duration:** May 17–June 4, 2026 (10 working days + 5 days Days 1-5 prep)  
**Status:** ✅ Complete

---

## What Was Built

**Phase 1 achieved the goal: Build a working understanding of the entire NomNom LLM pipeline from API to production.**

The work spans **two halves:**

### **Days 1-5: Concept Learning** (learning_lab/phase_1/ notebooks 01-15 + 3 projects)

15 Jupyter notebooks exploring the Anthropic API and LLM engineering patterns:

**Layer 0 — API Fundamentals:**
- **01_first_api_call.ipynb** — Messages structure, model selection (Opus/Sonnet/Haiku), `stop_reason`, usage tracking
- **02_multi_turn.ipynb** — Conversation state management, role alternation (user/assistant), O(n²) token cost, prompt caching motivation
- **03_streaming.ipynb** — Real-time response streaming with event handlers
- **04_multimodal.ipynb** — Image input (base64 encoding), vision capabilities
- **05_SystemPrompt_Temperature_StructuredData.ipynb** — System prompts, temperature control, structured output requests

**Layer 1 — Prompt Engineering & Evaluation:**
- **06_Prompt_evaluation.ipynb** — Building evaluation pipelines, measuring prompt quality (accuracy, consistency, cost)
- **07_prompt_engineering.ipynb** — Techniques: role assignment, few-shot examples, chain-of-thought, XML tags

**Layer 2 — Output Control & Tools:**
- **08_tool_use_with_claude.ipynb** — Tool schemas, `tool_choice`, parsing tool calls
- **08a_advanced_tool_TextEditorTool.ipynb** — Building custom tools (text editor)
- **08b_advanced_tool_WebSearchTool.ipynb** — Building custom tools (web search)

**Layer 3 — Augmentation & Advanced Patterns:**
- **09_RAG_and_agentic_search.ipynb** — RAG pipeline (chunking, embeddings, vector search), agentic patterns
- **10_MCP.ipynb** — Model Context Protocol for tool exposure

**Layer 5 — Agent Engineering & Cloud Tools:**
- **11_Claude_Code_in_action.ipynb** — Claude Code SDK, CLI integration
- **12_agents_and_workflows.ipynb** — Agent loops, multi-step workflows
- **13_subagent.ipynb** — Subagent patterns for delegation
- **14_Features_of_Claude.ipynb** — Feature inventory (caching, thinking, batch, files)
- **15_agent_skills.ipynb** — Agent skills and capabilities

**Plus 3 Project Directories:**
- **10a_cli_MCPproject/** — MCP server implementation (NomNom as MCP)
- **11a_Claude_Code_lab_uigen/** — Claude Code + UI generation sandbox
- **11b_Hooks_queries/** — Claude Code hooks + query patterns

---

### **Days 6-7: Production Code Review** (docs/learning/05_learning_notes/code_review/)

Two deep code reviews of NomNom's core infrastructure:

1. **01_client_py_design_review.md** — LLM API wrapper with reliability patterns
   - Retry logic (2 attempts, exponential backoff: 1s → 2s)
   - Timeout enforcement (per-model: 20s for Haiku, 30s for Sonnet)
   - Fallback strategy (quality-first: Sonnet primary, Haiku fallback)
   - Per-model configuration for future-proofing
   - 7 design choices with detailed reasoning

2. **02_prompt_engine_design_review.md** — Template-driven prompt rendering
   - Jinja2 templating system (3 core syntaxes: variables, conditionals, includes)
   - 4 production templates analyzed: analyze_food, cat_personas, recommend_meal, weekly_recap
   - 9 prompt engineering techniques identified across templates
   - DRY principle: reusable templates (cat_personas.j2 included by others)
   - Trade-off analysis: tool_choice vs. text parsing (noted for Phase 2)

---

### **Days 8-9: Sandbox Capstone** (learning_lab/phase_1/capstone/nomnom_v0_5.py)

Integrated Python script combining client.py + prompt_engine.py:

- **5-step pipeline:** Image encoding → prompt rendering → Claude API call → JSON parsing → display
- **High-level overview:** 5 main functions with clear responsibilities
- **Flow trace Q&A:** Data flow documented with 4 deep questions answered
- **Tested with real image:** Buddha bowl food photo analyzed across 3 cat personalities (sassy, grumpy, wholesome)
- **Experimentation:** Same food + different templates = different Claude responses
- **Fully commented:** Every function documented with inline explanations

---

## Key Learning Outcomes by Layer

### **Layer 0 (API Mastery):** 1/5 → 4/5

**Learned:**
- Messages structure (list of blocks, not strings)
- Model family trade-offs (Haiku: fast/cheap, Sonnet: balanced, Opus: smart/expensive)
- `stop_reason` as truth source (end_turn vs. max_tokens vs. tool_use)
- Multi-turn state management (O(n²) token growth motivates prompt caching)
- Token usage tracking for cost analysis
- Streaming events for real-time responses
- Multimodal support (images, documents)

**Evidence:** Designed and ran multi-turn conversations, experimented with streaming, tested multimodal input, analyzed token costs

---

### **Layer 1 (Prompt Engineering):** 1/5 → 3/5

**Learned:**
- 9 prompt engineering techniques: role assignment, few-shot examples, chain-of-thought, XML tags, system prompts, temperature, structured output, guardrails (calorie bounds), defense-in-depth (reinforcing constraints at multiple points)
- Jinja2 templating (variables, conditionals, includes) for separating prompts from code
- Prompts as product assets (10x change frequency vs. code)
- Evaluation pipelines for measuring prompt quality
- Design choices: why 2 few-shot examples vs. 5, why cat_style appears twice in the prompt

**Evidence:** Analyzed 4 production templates, defended 7 design choices, experimented with 3 cat personalities, identified pattern of reusable templates

---

### **Layer 2 (Output Control):** 0/5 → 1/5

**Learned:**
- Structured output patterns: stop sequences, prefill+stop, tool_choice
- Tool schemas (input_schema, name, description)
- Why tool_choice is better than text parsing (guaranteed structure vs. fragile)
- JSON text parsing is unreliable (Claude may wrap in markdown)

**Evidence:** Built text parsing in capstone, recognized its fragility, noted tool_choice as better approach for Phase 2

---

### **Layer 3 (Augmentation):** 0/5 → 1/5

**Learned:**
- Tool use basics (schemas, tool calls, parsing)
- RAG pipeline concepts (chunking, embeddings, vector search, reranking)
- Image multimodal support (base64 encoding, media types)

**Evidence:** Studied 09_RAG_and_agentic_search.ipynb, experimented with image input in capstone

---

### **Layer 4 (Reliability Engineering):** 0/5 → 2/5

**Learned:**
- Retry strategies (exponential backoff, when to retry vs. fallback)
- Timeout enforcement per model
- Fallback model selection (quality-first: primary is high-quality, fallback is fast)
- Latency vs. reliability trade-offs (2 retries not 3 or 5)

**Evidence:** Reviewed client.py, defended retry/timeout/fallback choices, understood why backoff is short (1s → 2s)

---

### **Layer 5 (Agent Engineering):** 0/5 → 1/5

**Learned:**
- Agent loops and multi-step workflows
- Subagent patterns for delegation
- Claude Code SDK basics
- MCP (Model Context Protocol) for tool exposure
- Agent skills and capabilities

**Evidence:** Studied notebooks 11-15, explored 3 project directories, understand agent patterns conceptually (not yet implemented)

---

## Challenges Overcome

### **1. Understanding async/await**

**Challenge:** Why does the script use `async def` and `await`? Why not just call functions normally?

**Resolution:** 
- Learned that `await` pauses a function without blocking other code
- Claude API calls take 5-10 seconds; async prevents the app from freezing
- `asyncio.run()` starts the event loop to execute async functions
- This is essential for responsive user experiences

**Takeaway:** Async isn't complexity for its own sake — it's a pattern for concurrent I/O. Necessary for production code.

---

### **2. O(n²) token cost in multi-turn conversations**

**Challenge:** Why does token cost grow so fast in conversation history?

**Resolution:**
- Measured: Round 1 = 16 tokens, Round 2 = 262 tokens, Round 5 ≈ 1075 tokens
- Each new round re-sends the entire history (user + assistant messages)
- Growth is O(n²), not linear — by round 50, you'd exceed context window

**Takeaway:** Prompt caching (Phase 4) is essential for long conversations. Cost-aware design requires this understanding.

---

### **3. Role alternation requirement**

**Challenge:** Why are `user` and `assistant` roles so strict? Why can't I send two `user` messages in a row?

**Resolution:**
- Claude is trained to generate only in the `assistant` position
- Past `assistant` messages are treated as "things I already said" (don't re-answer)
- Past `user` messages are treated as "what I need to respond to now"
- Without role separation, Claude would re-answer its own messages or treat output as new input

**Takeaway:** The API protocol reflects Claude's training, not arbitrary design. Understanding the why prevents confusion.

---

### **4. Jinja2 templating and template reuse**

**Challenge:** Why separate prompts into .j2 files instead of hardcoding them in Python?

**Resolution:**
- Prompts change 10x more frequently than code
- Separating them enables non-engineers (product, PMs) to iterate without touching Python
- Template includes (cat_personas.j2) eliminate copy-paste and sync bugs
- DRY principle applies to prompts too

**Takeaway:** Product assets should be separated from infrastructure code. This enables organizational velocity.

---

### **5. Module imports and path setup**

**Challenge:** Script couldn't find `llm.client` and `llm.prompt_engine` when running from learning_lab/.

**Resolution:** 
- Calculated absolute path: `learning_lab/phase_1/capstone/` → up 3 levels → `NomNom-Backend/src`
- Debugged and fixed the `sys.path.insert()` call
- Verified imports worked by running the script

**Takeaway:** Python import paths are relative to where you run from. Explicit path calculation beats guessing.

---

### **6. JSON parsing fragility**

**Challenge:** Claude sometimes wraps JSON in markdown backticks instead of returning pure JSON.

**Resolution:** 
- Implemented fallback parsing: try direct `json.loads()` first, then search for `{...}` in response
- Recognized this as fragile — CCAF guide recommends tool_choice instead
- Noted for Phase 2 refactoring

**Takeaway:** Text parsing is simple but unreliable. Structured output should use tools, not prompts.

---

### **7. Experimentation vs. documentation**

**Challenge:** Reading Jinja2 docs doesn't beat actually running the script with 3 different cat-styles.

**Resolution:**
- After learning the theory, running the script 3 times (sassy, grumpy, wholesome) made it crystal clear
- Seeing `{{ cat_style }}` → grumpy persona → different output is 10x more convincing than reading docs

**Takeaway:** Sandbox-first learning. Theory is backdrop, experimentation is foreground.

---

## Testing Results

### What Worked Well ✅

1. **Multi-turn conversations** — Tested context resolution across 5+ turns
2. **Streaming responses** — Real-time output working correctly
3. **Multimodal (images)** — Food photo analysis with base64 encoding working
4. **Prompt templating** — Same food, different cat_style → different tones, same nutrition data
5. **Retry + timeout + fallback** — client.py handled the API call robustly
6. **Data flow** — Traced from argparse → render_prompt → client call → JSON → display

### Known Issues / Regressions

1. **No error handling for missing image file** — Script crashes if file doesn't exist (not critical for sandbox)
2. **JSON parsing depends on Claude's cooperation** — If Claude refuses to return JSON, parsing fails (fixed in Phase 2 with tool_choice)
3. **Capstone only tested with one food image** — Limited test coverage

### What Wasn't Tested

- recommend_meal.j2 and weekly_recap.j2 (only analyze_food.j2 was used)
- Fallback model trigger (Sonnet never failed, so Haiku fallback never ran)
- Jinja2 security (injection safety if user-generated content in variables)
- Tool use parsing (learned theory, haven't implemented)
- RAG pipeline (learned concepts, haven't built)
- Agent loops (learned patterns, haven't implemented)
- MCP server (learned protocols, haven't deployed)

---

## Key Insights & Lessons Learned

### **1. Prompts are product assets, not code**

The biggest realization from Phase 1.

**Before:** "Prompts should be in the code so engineers can change them."  
**After:** "Prompts change 10x more frequently than code. Separating them into .j2 files lets product people iterate without touching Python."

**Evidence:** Same script, 3 different prompts → 3 different outputs. Non-engineers could edit those templates without breaking anything.

**Application:** Phase 2+ should treat prompts as first-class citizen, not implementation detail. This affects how we design guardrails and evaluation pipelines.

---

### **2. Reliability engineering is invisible but essential**

client.py seems simple (30 lines of code), but it encodes 5 crucial decisions:
- 2 retries (not 3 or 5) — latency vs. reliability tradeoff
- 1s → 2s backoff — spread retry load, don't wait forever
- Per-model timeout — Haiku doesn't need 30 seconds
- Fallback to Haiku — quality-first strategy (Sonnet primary)
- Terminal fallback — if both fail, error immediately (don't hang)

Each choice has a reason. This is engineering taste. Reliability isn't add-on, it's designed in from the start.

---

### **3. Token cost is a first-class design constraint**

Multi-turn conversations cost O(n²) because every round re-sends full history. By round 5, cumulative cost is ~170× the first round. This is why:
- Prompt caching (Phase 4) is essential for long conversations
- Model tiering (Phase 4) matters — Haiku at 20s timeout saves 3-5x vs. Sonnet
- Structured outputs need careful design to avoid reprompting

Cost awareness must be built into the architecture, not bolted on later.

---

### **4. DRY applies to prompts too**

cat_personas.j2 is included by analyze_food.j2. If we add more templates that need cat personalities, they all reuse the same file. This prevents:
- Copy-paste drift (3 templates with 5 personalities each = 15 copies to maintain)
- Sync bugs (update personality in one file, forget the others)
- Inconsistent behavior

Template design should follow the same principles as code: DRY, single responsibility, separation of concerns.

---

### **5. Sandbox-first learning beats reading documentation**

Reading Jinja2 docs is fine, but seeing it in action is 10x more convincing. Running the script 3 times (sassy, grumpy, wholesome) made the entire system crystal clear. Similarly:
- Understanding token cost from *measured* O(n²) growth (not theory)
- Understanding role alternation from *seeing* Claude break when roles are wrong (not docs)

This is why Days 1-5 notebooks include actual experiments, not just theory.

---

### **6. Tool use > text parsing for structured output**

Current capstone asks Claude for JSON, then parses it. This is fragile — Claude may wrap JSON in markdown or refuse to return JSON.

Better approach: Define a tool schema, set `tool_choice="force analyze_food"`, extract the tool parameters. Guaranteed structure.

**Status:** Deferred to Phase 2 (Output Control). This is exactly what Phase 2 will focus on.

---

### **7. API protocol reflects training**

The strict user/assistant role alternation isn't arbitrary design — it reflects how Claude is trained. Understanding the why (Claude generates only in assistant position) prevents confusion and helps with debugging.

Same for `stop_reason` — it's not just metadata, it's the truth source for "did Claude finish?" Hiding it (as some tutorials do) discards important signal.

---

## Next Steps

### **Immediate (Day 10)**

- [x] Write Phase 1 retrospective (comprehensive, covering all 15 notebooks + projects + capstone + reviews)
- [ ] Update CLAUDE.md (Phase 1 complete, Phase 2 in progress)
- [ ] Update Capability Profile (Layer scores + evidence)
- [ ] Update Roadmap (Phase 1 marked complete)

### **Phase 2 (Week 3–4): Make NomNom Not Crash**

**Focus:** parser.py, guardrails.py, evaluator.py, tools.py

**Why these?** Output control — how to reliably extract, validate, and score Claude's responses.

**Planned improvements from Phase 1:**
- Replace JSON text parsing with tool_choice (structured output guaranteed)
- Add guardrails for validation (is the JSON valid? are calories realistic?)
- Add evaluator for scoring (did Claude understand the food?)
- Implement tool use patterns learned in notebooks

**Deferred work:**
- RAG pipeline (Phase 3)
- Semantic caching (Phase 3)
- Agent loops (Phase 5)
- MCP server (Phase 6)

---

## Capability Profile Update

**Layer 0 (API Mastery):** 1/5 → **4/5** ⭐
- ✅ Understand messages structure, model selection, stop_reason, streaming, multimodal
- ✅ Know token cost dynamics and how to track usage
- ✅ Can explain retry/timeout/fallback strategies
- ✅ Understand role alternation requirement and why
- ⏳ Haven't built production API integration yet (Phase 2+)

**Layer 1 (Prompt Engineering):** 1/5 → **3/5** ⭐
- ✅ Know 9 prompt engineering techniques (role, few-shot, CoT, XML, system prompt, temperature, guardrails, defense-in-depth)
- ✅ Understand Jinja2 templating (variables, conditionals, includes)
- ✅ Can defend prompt design choices (why 2 examples vs. 5, why cat_style appears twice)
- ✅ Recognize DRY principle applies to templates
- ⏳ Haven't designed prompts from scratch in production yet
- ❌ Don't understand advanced techniques (few-shot optimization, adaptive prompting) yet

**Layer 2 (Output Control):** 0/5 → **1/5** ⭐
- ✅ Aware that text parsing is fragile, tool_choice is better
- ✅ Understand tool schemas and tool_choice patterns (from notebooks)
- ⏳ Will implement in Phase 2

**Layer 3 (Augmentation):** 0/5 → **1/5** ⭐
- ✅ Understand tool use basics (from notebooks)
- ✅ Know RAG pipeline concepts (chunking, embeddings, vector search)
- ✅ Experienced multimodal input (images in capstone)
- ⏳ Will build RAG in Phase 3

**Layer 4 (Reliability Engineering):** 0/5 → **2/5** ⭐
- ✅ Understand retry/timeout/fallback (client.py review)
- ✅ Know latency vs. reliability trade-offs
- ✅ Can defend why 2 retries, 1s→2s backoff
- ⏳ Will build reliability infrastructure in Phase 4

**Layer 5 (Agent Engineering):** 0/5 → **1/5** ⭐
- ✅ Understand agent loops, subagent patterns (from notebooks)
- ✅ Know MCP basics
- ⏳ Will implement in Phase 5

---

## Phase 1 Summary

**What went well:**
- Comprehensive learning path (15 notebooks → 2 code reviews → capstone integration)
- Sandbox-first approach (theory → implementation → experimentation)
- Detailed documentation (comments, Q&A, flow traces)
- Discovered fragility of text parsing (important for Phase 2)

**What was harder than expected:**
- async/await (but now understand the why)
- O(n²) token growth (realized cost awareness is essential)
- Module path setup (but now know how to debug)
- Realizing how much Phase 1 covered (15 notebooks is huge!)

**Key takeaway:**
Prompts are not an afterthought — they're product assets that deserve the same engineering rigor as code. NomNom's architecture (templates separate from Python) reflects this philosophy. This insight carries through Phases 2-6.

---

**Phase 1 Status:** ✅ **COMPLETE**

**Capability Growth:** 7 layers, starting at 0-1/5, now averaging 2/5 with strong foundation in Layers 0-2 (API, Prompt Engineering, Output Control fundamentals)

Ready for Phase 2: Make NomNom Not Crash (Output Control + Reliability).
