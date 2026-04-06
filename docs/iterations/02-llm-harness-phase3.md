# NomNom — Iteration 02: LLM Harness Engineering

**Phase:** Phase 3 (full plan)

**Goal:** Build a production-grade LLM harness with retry logic, fallback models, structured output, and prompt templates — before wiring it to the API.

**Resume Skills:** LLM Harness Engineering, Structured Output, Prompt Engineering

---

## What's Built

- Basic AI photo analysis via Haiku (no harness, raw calls)
- iOS camera + food logging working end-to-end

## What We're Building

A **robust LLM layer** that handles:
- Retries with exponential backoff (up to 2 attempts)
- Fallback model (Sonnet if Haiku fails)
- Timeout protection (10s for Haiku, 30s for Sonnet)
- Token budget caps per call
- Structured output via tool_use (not "hope for JSON")
- Jinja2 prompt templates (food analysis, recommendations, weekly recap)
- Cat persona system
- Pydantic-validated output with auto-retry on bad responses

## Phases

### Phase 3.1: LLM client wrapper

Build the core Anthropic wrapper with retry and fallback.

#### 3.1.A: Create `src/llm/__init__.py`

Empty init file to make llm a package.

#### 3.1.B: Create `src/llm/client.py`

```python
# What it does:
# - Wraps anthropic.AsyncAnthropic with retry, timeout, fallback
# - On Haiku failure after retries: falls back to Sonnet
# - On Sonnet failure: returns graceful error
# - Logs every call via logger.py (built in Phase 5)
# - Token budget: cap max_tokens per call

# Key functions:
# - __init__(self) — create AsyncAnthropic client
# - create_message_with_retry(
#     model: str,
#     messages: list,
#     max_tokens: int,
#     tools: list | None,
#     system: str | None,
#     fallback_model: str | None
#   ) -> CreateMessageResponse
#     Retries up to 2 times with exponential backoff (1s, 2s)
#     On failure: falls back to fallback_model if provided
#     Timeout: 10s for Haiku, 30s for Sonnet
#     Token budget: capped at max_tokens
```

Files to create:
- `src/llm/client.py` — AsyncAnthropic wrapper with retry/timeout/fallback logic

How to verify:
- `uv run python -c "from src.llm.client import LLMClient; print('OK')"`

#### 3.1.C: Test retry logic

Files to create:
- `tests/unit/llm/__init__.py`
- `tests/unit/llm/test_client.py` — test retry 3x with mock, test fallback, test timeout

Commands:
- `uv run pytest tests/unit/llm/test_client.py -v`

---

### Phase 3.2: Router + Prompt Templates

Map tasks to models and create reusable prompt templates.

#### 3.2.A: Create `src/llm/router.py`

```python
# What it does:
# - Routes tasks to the right model
# - "analyze_food" -> Haiku (fast, cheap)
# - "recommend_meal" -> Sonnet (better writing)
# - "weekly_recap" -> Sonnet (narrative quality)

# Key function:
# - get_model_for_task(task_type: str) -> tuple[str, int]
#     Returns (model_id, max_tokens)
#     Example: ("claude-haiku-4-5-20251001", 500)
```

Files to create:
- `src/llm/router.py` — task type to model mapping

#### 3.2.B: Create Jinja2 prompt templates

```
src/llm/prompts/
├── cat_personas.j2       — defines cat personality modifiers
├── analyze_food.j2       — food photo analysis prompt (with few-shot examples)
├── recommend_meal.j2     — meal recommendation prompt (with RAG context injection)
└── weekly_recap.j2       — weekly recap prompt
```

Files to create:
- `src/llm/prompts/__init__.py`
- `src/llm/prompts/cat_personas.j2` — persona definitions (sassy, grumpy, wholesome, etc.)
- `src/llm/prompts/analyze_food.j2` — food analysis with few-shot examples
- `src/llm/prompts/recommend_meal.j2` — recommendation prompt (stub for RAG context)
- `src/llm/prompts/weekly_recap.j2` — recap prompt

Example `analyze_food.j2`:
```jinja2
You are a {{ cat_style }} food critic cat.

Analyze this food photo and return JSON with: food_name, calories, protein_g, carbs_g, fat_g, food_category, cuisine_origin, cat_roast.

Cat personality: {{ cat_persona }}

Few-shot examples:
1. Input: salad photo → Output: {"food_name": "Caesar Salad", "calories": 350, ..., "cat_roast": "Rabbit food, but I'll allow it"}
2. Input: pizza photo → Output: {"food_name": "Pepperoni Pizza", "calories": 450, ..., "cat_roast": "Grease fest, but you do you"}

Now analyze the user's food photo and respond in JSON format only.
```

#### 3.2.C: Create `src/llm/prompt_engine.py`

```python
# What it does:
# - Renders Jinja2 templates with variables (cat_style, user preferences, today's intake, etc.)
# - Injects context like user profile, cat mood, etc.

# Key function:
# - render_prompt(
#     template_name: str,
#     cat_style: str,
#     cat_persona: str,
#     user_context: dict = None
#   ) -> str
#     Loads template from src/llm/prompts/{template_name}.j2
#     Renders with Jinja2
#     Returns complete prompt string
```

Files to create:
- `src/llm/prompt_engine.py` — Jinja2 template renderer

How to verify:
- `uv run python -c "from src.llm.prompt_engine import PromptEngine; p = PromptEngine(); print(p.render_prompt('analyze_food', 'sassy'))"`

#### 3.2.D: Test template rendering

Files to create:
- `tests/unit/llm/test_prompt_engine.py` — test template rendering with variables

Commands:
- `uv run pytest tests/unit/llm/test_prompt_engine.py -v`

---

### Phase 3.3: Tool Definitions + Output Parsing

Define structured output schemas and validate AI responses.

#### 3.3.A: Create `src/llm/tools.py`

```python
# What it does:
# - Defines Anthropic tool_use schemas for food analysis
# - Forces AI to return JSON matching exact schema
# - No more "hope the AI returns valid JSON"

# Tool definitions:
# - analyze_food_tool: {
#     name: "analyze_food",
#     description: "Analyze a food photo",
#     input_schema: {
#       type: "object",
#       properties: {
#         food_name: {type: "string"},
#         calories: {type: "integer"},
#         protein_g: {type: "number"},
#         carbs_g: {type: "number"},
#         fat_g: {type: "number"},
#         food_category: {type: "string"},
#         cuisine_origin: {type: "string"},
#         cat_roast: {type: "string"}
#       },
#       required: [all fields]
#     }
#   }
```

Files to create:
- `src/llm/tools.py` — Anthropic tool_use schema definitions

#### 3.3.B: Create `src/llm/parser.py`

```python
# What it does:
# - Takes raw AI tool_use output (JSON)
# - Validates with Pydantic models
# - If validation fails: retry the AI call (up to 2 times)
# - If still fails: raise ParseError with context

# Key functions:
# - parse_food_analysis(response: dict) -> FoodAnalysisResponse
#     Validates: calories in 0-5000 range, protein/carbs/fat in 0-500g
#     Auto-retry on validation failure
# - validate_food_analysis(data: dict) -> bool
#     Runs guardrail checks (see Phase 5)
```

Create Pydantic models in `src/schemas/food_log.py`:
- `FoodAnalysisResponse` — validated food analysis schema

Files to create/update:
- `src/llm/parser.py` — output validation + retry
- Update `src/schemas/food_log.py` — add Pydantic models for validation

#### 3.3.C: Test parsing + validation

Files to create:
- `tests/unit/llm/test_parser.py` — test Pydantic validation, test retry on bad output

Commands:
- `uv run pytest tests/unit/llm/test_parser.py -v`

---

### Phase 3.4: Integration test

Wire everything together and test end-to-end.

Files to create:
- `tests/unit/llm/test_integration.py` — test LLMClient + Router + PromptEngine + Parser together (mocked API)

Commands:
- `uv run pytest tests/unit/llm/ -v` — all LLM tests pass

---

## Success Criteria

- [x] LLMClient wraps Anthropic with retry, timeout, fallback
- [x] Router maps tasks to correct models
- [x] Jinja2 templates render with cat personas
- [x] Tool definitions enforce structured output schema
- [x] Parser validates output, retries on failure
- [x] All unit tests pass
- [x] No direct Anthropic calls anywhere else in codebase — all go through LLMClient

## Next After Phase 3

Phase 4 wires this harness to the `/food-logs/analyze` endpoint. Then Phase 5 adds guardrails, caching, and logging.
