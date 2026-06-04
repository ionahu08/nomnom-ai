# Phase 1 Retrospective: NomNom MVP — Make It Recognize Food

**Duration:** May 17–June 4, 2026 (10 working days)  
**Status:** ✅ Complete

---

## What Was Built

**Phase 1 achieved the goal: understand how NomNom's LLM pipeline works.**

Three comprehensive code reviews analyzed the core infrastructure:

1. **`client.py` review** — LLM API wrapper with reliability patterns
   - Retry logic (2 attempts, exponential backoff: 1s → 2s)
   - Timeout enforcement (per-model: 20s for Haiku, 30s for Sonnet)
   - Fallback strategy (quality-first: Sonnet primary, Haiku fallback)
   - Per-model configuration for future-proofing

2. **`prompt_engine.py` + `prompts/` review** — Template-driven prompt rendering
   - Jinja2 templating system separating prompts from code
   - 4 production templates analyzed: analyze_food, cat_personas, recommend_meal, weekly_recap
   - Prompt engineering techniques: role assignment, few-shot examples, structured output, guardrails
   - DRY principle: reusable templates (cat_personas.j2 included by others)

3. **NomNom v0.5 sandbox capstone** — Integration and experimentation
   - Standalone Python script combining client.py + prompt_engine.py
   - 5-step pipeline: image encoding → prompt rendering → Claude API call → JSON parsing → display
   - Tested with real food image (Buddha bowl) across 3 cat personalities (sassy, grumpy, wholesome)
   - Data flow traced and documented in code comments

**Artifacts:**
- 2 detailed code reviews (01_client_py_design_review.md, 02_prompt_engine_design_review.md)
- 1 fully-commented sandbox script (nomnom_v0_5.py) with high-level overview + flow trace Q&A
- 3 successful test runs with different cat personalities

---

## Challenges

### 1. Understanding `async/await`

**Challenge:** Why does the script use `async def` and `await`? Why not just call functions normally?

**Resolution:** Learned that:
- `await` pauses a function without blocking other code
- Claude API calls take 5-10 seconds; without async, the app would freeze
- `asyncio.run()` starts the event loop to actually execute async functions
- This is essential for responsive user experiences

**Takeaway:** Async isn't complexity for its own sake — it's a pattern for concurrent I/O.

---

### 2. Module imports and path setup

**Challenge:** Script couldn't find `llm.client` and `llm.prompt_engine` when running from learning_lab/.

**Resolution:** 
- Calculated absolute path: `learning_lab/phase_1/capstone/` → up 3 levels → `NomNom-Backend/src`
- Debugged and fixed the `sys.path.insert()` call
- Verified imports worked by running the script

**Takeaway:** Python import paths are relative to where you run from; explicit path calculation beats guessing.

---

### 3. JSON parsing from Claude responses

**Challenge:** Claude sometimes wraps JSON in markdown backticks instead of returning pure JSON.

**Resolution:** Implemented fallback parsing:
- Try direct `json.loads()` first
- If that fails, search for `{...}` in the response and extract the JSON

**Discovery:** This is fragile! The CCAF guide recommends using tool_choice instead (Phase 2 topic). Noted for refactoring.

**Takeaway:** Text parsing is simple but unreliable. Structured output should use tools, not prompts.

---

## Testing Results

### What Worked Well ✅

1. **Prompt templating** — Same food, different cat_style → different tones, same nutrition data
   - Confirmed Jinja2 rendering works correctly
   - Templating enables fast iteration without redeployment

2. **Retry + timeout + fallback** — client.py handled the API call robustly
   - Script ran successfully with real Claude API
   - Timeout enforcement prevented hanging
   - Fallback logic ready if primary model failed

3. **Data flow** — Traced from argparse → render_prompt → client call → JSON → display
   - Every step worked as designed
   - No unexpected failures or surprises

### Known Issues / Regressions

1. **No error handling for missing image file** — Script crashes if file doesn't exist
   - Not critical for sandbox, but production would need validation

2. **JSON parsing depends on Claude's cooperation** — If Claude refuses to return JSON, parsing fails
   - Workaround: Use tool_choice (Phase 2)

3. **No handling for edge cases** — Only tested with one food image
   - Edge cases: ambiguous food, low-quality photo, unusual cuisine

### What Wasn't Tested

- recommend_meal.j2 and weekly_recap.j2 (only analyze_food.j2 was used)
- Fallback model trigger (Sonnet never failed, so Haiku fallback never ran)
- Jinja2 security (injection safety if user-generated content in variables)

---

## Key Insights & Lessons Learned

### 1. **Prompts are product assets, not code**

**Insight:** The biggest realization from Phase 1.

Before: "Prompts should be in the code so engineers can change them."  
After: "Prompts change 10x more frequently than code. Separating them into .j2 files lets product people iterate without touching Python."

**Evidence:** Same script, 3 different prompts → 3 different outputs. Non-engineers could edit those templates.

**Application:** Phase 2+ should treat prompts as first-class citizen, not implementation detail.

---

### 2. **Reliability engineering is invisible but essential**

**Insight:** client.py seems simple (30 lines of code), but it encodes 5 crucial decisions:
- 2 retries (not 3 or 5) — latency vs. reliability tradeoff
- 1s → 2s backoff — spread retry load, but don't wait forever
- Per-model timeout — Haiku doesn't need 30 seconds
- Fallback to Haiku — quality-first strategy (Sonnet primary)
- Terminal fallback — if both fail, error immediately (don't hang)

Each choice has a reason. This is engineering taste.

**Application:** Reliability isn't add-on, it's designed in from the start.

---

### 3. **DRY applies to prompts too**

**Insight:** cat_personas.j2 is included by analyze_food.j2. If we add more templates that need cat personalities, they all reuse the same file.

This prevents:
- Copy-paste drift (3 templates with 5 personalities each = 15 copies to maintain)
- Sync bugs (update personality in one file, forget the others)
- Inconsistent behavior

**Application:** Template design should follow the same principles as code: DRY, single responsibility, separation of concerns.

---

### 4. **Experimentation beats reading documentation**

**Insight:** After learning the theory of cat-styles, running the script 3 times (sassy, grumpy, wholesome) made it crystal clear how Jinja2 works.

You could read Jinja2 docs, but seeing `{{ cat_style }}` → grumpy persona → different output is 10x more convincing.

**Application:** Sandbox-first learning. Theory is backdrop, experimentation is foreground.

---

### 5. **Tool use > text parsing for structured output**

**Insight:** The current script asks Claude for JSON, then parses it. This is fragile.

Better approach: Define a tool schema, set `tool_choice="force analyze_food"`, extract the tool parameters. Guaranteed structure.

**Status:** Deferred to Phase 2 (Output Control). Noted for refactoring.

---

## Next Steps

### Immediate (Day 10)

- [ ] Write Phase 1 capability profile update (Layer 0 → Layer 1)
- [ ] Document production refactoring plan for NomNom-Backend/src/llm/
- [ ] Identify which production code should be touched (if any) vs. deferred to Phase 2

### Phase 2 (Week 3–4): Make NomNom Not Crash

**Focus:** parser.py, guardrails.py, evaluator.py, tools.py

**Why these?** Output control — how to reliably extract, validate, and score Claude's responses.

**Planned improvements from Phase 1:**
- Replace JSON text parsing with tool_choice (structured output)
- Add guardrails for validation (is the JSON valid? are calories realistic?)
- Add evaluator for scoring (did Claude understand the food?)

---

## Capability Profile Update

**Layer 0 (API Basics):** 3/5 → 4/5
- ✅ Can explain Anthropic API, async/await, model selection
- ✅ Understand client.py's retry/timeout/fallback strategy
- ⏳ Haven't built production API integration yet (Phase 2+)

**Layer 1 (Prompt Engineering):** 1/5 → 3/5
- ✅ Understand Jinja2 templating, template variables, conditionals, includes
- ✅ Can defend prompt design choices (role assignment, few-shot, output format, guardrails)
- ✅ Recognize prompt engineering techniques in real templates
- ⏳ Haven't designed prompts from scratch yet (will do in Phase 2 guardrails)
- ❌ Don't understand advanced techniques (chain-of-thought, few-shot optimization) yet

**Layer 2 (Output Control):** 0/5 → 1/5
- ✅ Aware that text parsing is fragile, tool_choice is better
- ⏳ Will learn in Phase 2

---

## Retrospective Summary

**What went well:**
- Code review process (detailed, systematic, builds muscle memory)
- Sandbox-first learning (theory → experiment → understanding)
- Documentation (comments, Q&A, flow traces make future learning easier)

**What was harder than expected:**
- async/await (but now understand the why)
- Module path setup (but now know how to debug)
- Realizing JSON parsing is fragile (good lesson for Phase 2)

**Key takeaway:**
Prompts are not an afterthought — they're product assets that deserve the same engineering rigor as code. NomNom's architecture (templates separate from Python) reflects this philosophy.

---

**Phase 1 Status:** ✅ **COMPLETE**

Ready for Phase 2: Make NomNom Not Crash.
