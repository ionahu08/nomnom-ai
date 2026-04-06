# Phases — Iteration 02: LLM Harness Engineering

## Overview

Build the core LLM infrastructure layer before wiring it to APIs.

---

## Phase 3.1: LLM Client Wrapper (Retry + Fallback) ⚠️

Create the Anthropic wrapper with retry and fallback logic.

### 3.1.A: Create `src/llm/__init__.py`

- [ ] Empty init file to make llm a package

### 3.1.B: Create `src/llm/client.py` — The Safety Net

- [ ] Wrap AsyncAnthropic
- [ ] Implement `create_message_with_retry()` function:
  - Retry up to 2 times with exponential backoff (1s, then 2s)
  - Timeout: 10s for Haiku, 30s for Sonnet
  - Fallback to alternate model if provided
  - Return response or raise error
- [ ] Cap max_tokens per call

**Tests:**
- [ ] Retry: fail → wait → retry → succeed
- [ ] Fallback: Haiku fails twice → try Sonnet → succeed
- [ ] All fail → graceful error
- [ ] Timeout works

Files to create:
- `src/llm/client.py`
- `tests/unit/llm/__init__.py`
- `tests/unit/llm/test_client.py`

Verify: `uv run pytest tests/unit/llm/test_client.py -v`

---

## Phase 3.2: Router + Prompt Templates

Choose the right model and store prompts in files.

### 3.2.A: Create `src/llm/router.py` — Model Selection

- [ ] Map task types to models:
  - "analyze_food" → Haiku (fast, cheap)
  - "recommend_meal" → Sonnet (better writing)
  - "weekly_recap" → Sonnet (narrative quality)
- [ ] Include max_tokens per task

Files to create:
- `src/llm/router.py`

### 3.2.B: Create Jinja2 Prompt Templates

- [ ] Create `src/llm/prompts/__init__.py`
- [ ] Create `src/llm/prompts/cat_personas.j2` — personality definitions
- [ ] Create `src/llm/prompts/analyze_food.j2` — food analysis prompt with few-shot examples
- [ ] Create `src/llm/prompts/recommend_meal.j2` — recommendation prompt
- [ ] Create `src/llm/prompts/weekly_recap.j2` — recap prompt

### 3.2.C: Create `src/llm/prompt_engine.py` — Template Renderer

- [ ] Implement `render_prompt(template_name, **context)`:
  - Load .j2 file
  - Render with Jinja2
  - Return complete prompt string
- [ ] Import Environment from jinja2

Files to create:
- `src/llm/prompt_engine.py`

**Tests:**
- [ ] Load and render template
- [ ] Variables fill in correctly
- [ ] Missing variables handled gracefully

Files to create:
- `tests/unit/llm/test_prompt_engine.py`

Verify: `uv run pytest tests/unit/llm/test_prompt_engine.py -v`

---

## Phase 3.3: Tool Definitions + Output Parsing

Force structured output and validate it.

### 3.3.A: Create `src/llm/tools.py` — JSON Schema Enforcement

- [ ] Define `analyze_food_tool`: JSON schema with required fields (food_name, calories, protein_g, carbs_g, fat_g, food_category, cuisine_origin, cat_roast)

Files to create:
- `src/llm/tools.py`

### 3.3.B: Create `src/llm/parser.py` — Validation + Auto-Retry

- [ ] Implement `parse_food_analysis(response)`:
  - Extract tool_use response
  - Validate: calories 0-5000, macros 0-500g, non-empty names
  - If invalid: retry AI call (up to 2 times)
  - If all fail: raise ParseError
- [ ] Add `validate_food_analysis(data)` helper

Update `src/schemas/food_log.py`:
- [ ] Add FoodAnalysisResponse Pydantic model with validation

**Tests:**
- [ ] Valid data passes
- [ ] Invalid data retries
- [ ] Retries give up after 2 tries

Files to create:
- `src/llm/parser.py`
- `tests/unit/llm/test_parser.py`

Verify: `uv run pytest tests/unit/llm/test_parser.py -v`

---

## Phase 3.4: Integration Test

Wire everything together.

### 3.4.A: Integration Test

- [ ] Create `tests/unit/llm/test_integration.py`
- [ ] Test LLMClient + Router + PromptEngine + Parser together (mocked Anthropic)

Verify: `uv run pytest tests/unit/llm/ -v` — all LLM tests pass

---

## Success Criteria

- [x] LLMClient wraps Anthropic with retry, timeout, fallback
- [x] Router maps tasks to correct models
- [x] Jinja2 templates render with cat personas
- [x] Tool definitions enforce structured output
- [x] Parser validates output, retries on failure
- [x] All unit tests pass
- [x] No direct Anthropic calls elsewhere — all through LLMClient

## Next

Phase 4 wires this harness to the `/food-logs/analyze` endpoint.
