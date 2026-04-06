# NomNom — Iteration 02: LLM Harness Engineering

**Phase:** Phase 3 (full plan)

**Goal:** Build a production-grade LLM harness with retry logic, fallback models, structured output, and prompt templates — before wiring it to the API.

**Resume Skills:** LLM Harness Engineering, Structured Output, Prompt Engineering

---

## What's Built

- Basic AI photo analysis via Haiku (no harness, raw calls)
- iOS camera + food logging working end-to-end

## What We're Building

**In Plain English:**

Right now your app calls Claude and hopes it works. If Claude is slow or breaks, your app crashes.

An **LLM Harness** is a safety net that wraps around Claude and makes it reliable:

1. **Retry Logic** — If Claude fails, try again automatically (up to 2 times)
2. **Fallback Model** — If Haiku keeps failing, use Sonnet (smarter, more reliable) instead
3. **Structured Output** — Force Claude to return JSON in the exact shape you need (not random text)
4. **Validation** — Check the response is actually good (e.g., calories aren't 50,000), and auto-retry if it's garbage
5. **Prompt Templates** — Store prompts in files (not hardcoded in Python) so you can change them without editing code
6. **Timeouts** — Don't wait forever for Claude to respond (10s max for Haiku, 30s for Sonnet)
7. **Token Budget** — Don't spend too much money on one call (cap max_tokens)

**Result:** Your app is 10x more reliable and doesn't crash when Claude has a bad day.

## Phases

### Phase 3.1: LLM client wrapper (Retry + Fallback)

Build the core Anthropic wrapper that handles retries and fallback models.

#### 3.1.A: Create `src/llm/__init__.py`

Empty init file to make llm a package.

#### 3.1.B: Create `src/llm/client.py` — The Safety Net

**What this does in plain English:**
```
When you call Claude:
  Try Haiku
    ↓ fails?
  Wait 1 second, try Haiku again
    ↓ fails again?
  Use Sonnet (backup) instead
    ↓ Sonnet also fails?
  Return error gracefully (don't crash)
```

**Technical implementation:**

```python
# Key function:
# - create_message_with_retry(
#     model: str,              # "haiku" or "sonnet"
#     messages: list,          # the conversation history
#     max_tokens: int,         # max tokens to use (save money)
#     tools: list | None,      # the JSON schema Claude must follow
#     system: str | None,      # the system prompt
#     fallback_model: str | None  # what to try if first model fails
#   ) -> response
#
# Logic:
#   Try model with timeout (10s for Haiku, 30s for Sonnet)
#   If fails:
#     Wait 1 second
#     Try again
#   If fails again:
#     If fallback_model provided:
#       Try fallback_model instead
#     Else:
#       Return error
```

Files to create:
- `src/llm/client.py` — AsyncAnthropic wrapper with retry/timeout/fallback logic

How to verify:
- `uv run python -c "from src.llm.client import LLMClient; print('OK')"`

#### 3.1.C: Test retry logic

What to test:
- Call fails → retries → succeeds ✓
- Haiku fails twice → tries Sonnet → succeeds ✓
- Everything fails → returns graceful error ✓
- Timeout works (doesn't wait forever) ✓

Files to create:
- `tests/unit/llm/__init__.py`
- `tests/unit/llm/test_client.py` — test retry, test fallback, test timeout

Commands:
- `uv run pytest tests/unit/llm/test_client.py -v`

---

### Phase 3.2: Router + Prompt Templates

Choose the right model for each task, and store prompts in files (not hardcoded).

#### 3.2.A: Create `src/llm/router.py` — Pick the Right Model

**What this does in plain English:**
```
User: "Analyze a food photo"
Router: "Use Haiku (fast + cheap)"

User: "Write a funny recommendation"
Router: "Use Sonnet (smarter writer)"

User: "Create a weekly recap story"
Router: "Use Sonnet (better narrative)"
```

**Technical implementation:**

```python
# Key function:
# - get_model_for_task(task_type: str) -> tuple[str, int]
#     Returns (model_id, max_tokens)
#     Examples:
#       "analyze_food" → ("claude-haiku-4-5-20251001", 500 tokens)
#       "recommend_meal" → ("claude-sonnet-4-20250514", 1000 tokens)
#       "weekly_recap" → ("claude-sonnet-4-20250514", 2000 tokens)
```

Files to create:
- `src/llm/router.py` — task type to model mapping

#### 3.2.B: Create Jinja2 prompt templates — Fill-in-the-Blank Prompts

**What this does in plain English:**

Instead of hardcoding prompts in Python:
```python
prompt = "You are a sassy cat. Analyze this food..."  # Bad: hardcoded
```

Use templates with blanks:
```jinja2
You are a {{ cat_style }} cat.  # Good: fill in the blank
Analyze this food and return JSON.
```

Then in your code:
```python
prompt = render_template("analyze_food.j2", cat_style="sassy")
# → "You are a sassy cat. Analyze this food and return JSON."
```

**Why this is good:**
- Change cat style without editing Python code
- Easy to review and version control
- Production teams do it this way

```
src/llm/prompts/
├── cat_personas.j2       ← personality descriptions (sassy, grumpy, wholesome)
├── analyze_food.j2       ← food analysis prompt (with examples)
├── recommend_meal.j2     ← recommendation prompt
└── weekly_recap.j2       ← recap generation prompt
```

Example `analyze_food.j2`:
```jinja2
You are a {{ cat_style }} food critic cat.

Analyze this food photo and return JSON with fields:
- food_name: what the food is called
- calories: estimated calories
- protein_g, carbs_g, fat_g: macros in grams
- food_category: "salad", "fast food", "dessert", etc.
- cuisine_origin: "Italian", "Japanese", etc.
- cat_roast: a funny one-liner comment

Cat personality: {{ cat_persona }}

Few-shot examples (to be consistent):
1. Pizza → {"food_name": "Pepperoni Pizza", "calories": 450, ..., "cat_roast": "Grease fest, but you do you"}
2. Salad → {"food_name": "Caesar Salad", "calories": 350, ..., "cat_roast": "Rabbit food, but I'll allow it"}

Now analyze the user's food photo and respond in JSON format ONLY.
```

Files to create:
- `src/llm/prompts/__init__.py`
- `src/llm/prompts/cat_personas.j2` — personality definitions for "sassy", "grumpy", "wholesome", etc.
- `src/llm/prompts/analyze_food.j2` — food analysis with few-shot examples
- `src/llm/prompts/recommend_meal.j2` — recommendation prompt
- `src/llm/prompts/weekly_recap.j2` — recap prompt

#### 3.2.C: Create `src/llm/prompt_engine.py` — Template Renderer

**What this does:**
```python
# Load analyze_food.j2
# Replace {{ cat_style }} with "sassy"
# Replace {{ cat_persona }} with "sarcastic, judges your choices"
# Return the complete prompt
```

```python
# Key function:
# - render_prompt(
#     template_name: str,      # "analyze_food"
#     cat_style: str,          # "sassy"
#     cat_persona: str,        # the personality description
#     **context                # any other variables to inject
#   ) -> str
#     Loads template from src/llm/prompts/{template_name}.j2
#     Fills in all the {{ }} blanks
#     Returns complete prompt string
```

Files to create:
- `src/llm/prompt_engine.py` — Jinja2 template renderer

How to verify:
- `uv run python -c "from src.llm.prompt_engine import PromptEngine; p = PromptEngine(); print(p.render_prompt('analyze_food', 'sassy'))"`

#### 3.2.D: Test template rendering

What to test:
- Load template ✓
- Render with variables ✓
- Variables actually get filled in ✓
- Handles missing variables gracefully ✓

Files to create:
- `tests/unit/llm/test_prompt_engine.py` — test template rendering with variables

Commands:
- `uv run pytest tests/unit/llm/test_prompt_engine.py -v`

---

### Phase 3.3: Tool Definitions + Output Parsing

Force Claude to return valid JSON, and validate it's actually good.

#### 3.3.A: Create `src/llm/tools.py` — Force JSON Format

**What this does in plain English:**

Problem: Claude might return text instead of JSON:
```
Claude says: "This is a pizza with about 500 calories"
Your code expects: {"food_name": "pizza", "calories": 500}
→ Your code crashes because it's not JSON!
```

Solution: Use "tools" to tell Claude "You MUST return this exact JSON shape":
```json
{
  "food_name": "string",
  "calories": 123,
  "protein_g": 25.5,
  "carbs_g": 40.0,
  "fat_g": 15.0,
  "food_category": "string",
  "cuisine_origin": "string",
  "cat_roast": "string"
}
```

Now Claude HAS to follow this format. No choice. The SDK enforces it.

**Technical implementation:**

```python
# Define a "tool" that Claude must use:
analyze_food_tool = {
    "name": "analyze_food",
    "description": "Analyze a food photo and return nutritional info",
    "input_schema": {
        "type": "object",
        "properties": {
            "food_name": {"type": "string"},
            "calories": {"type": "integer"},
            "protein_g": {"type": "number"},
            "carbs_g": {"type": "number"},
            "fat_g": {"type": "number"},
            "food_category": {"type": "string"},
            "cuisine_origin": {"type": "string"},
            "cat_roast": {"type": "string"}
        },
        "required": ["food_name", "calories", "protein_g", "carbs_g", "fat_g", "food_category", "cuisine_origin", "cat_roast"]
    }
}
```

Files to create:
- `src/llm/tools.py` — Anthropic tool_use schema definitions

#### 3.3.B: Create `src/llm/parser.py` — Validate + Auto-Retry

**What this does in plain English:**

Even with tools, Claude might return bad data like:
```
{
  "calories": -50,          ← negative calories? nonsense!
  "protein_g": 5000,        ← 5000g of protein? impossible!
  "food_name": ""           ← empty name? useless!
}
```

Solution: Check the data. If it's garbage, try again automatically.

```python
# Logic:
def parse_food_analysis(response):
  data = response.json()  # Extract the JSON
  
  # Validation checks:
  assert 0 <= data['calories'] <= 5000, "Calories out of range"
  assert 0 <= data['protein_g'] <= 500, "Protein out of range"
  assert 0 <= data['carbs_g'] <= 500, "Carbs out of range"
  assert 0 <= data['fat_g'] <= 500, "Fat out of range"
  assert len(data['food_name']) > 0, "Food name is empty"
  
  if any check fails:
    retry_llm_call()  # Try again
  
  return data  # Passed all checks!
```

**Technical implementation:**

```python
# Key functions:
# - parse_food_analysis(response: dict) -> FoodAnalysisResponse
#     Validates: calories in 0-5000 range, protein/carbs/fat in 0-500g, non-empty names
#     If validation fails: retry the AI call (up to 2 times)
#     If all retries fail: raise ParseError with context
# - validate_food_analysis(data: dict) -> bool
#     Runs all guardrail checks
#     Returns True if valid, False if invalid
```

Create Pydantic models in `src/schemas/food_log.py`:
- `FoodAnalysisResponse` — the validated schema

Files to create/update:
- `src/llm/parser.py` — output validation + retry logic
- Update `src/schemas/food_log.py` — add FoodAnalysisResponse Pydantic model

#### 3.3.C: Test parsing + validation

What to test:
- Valid data passes ✓
- Invalid data (bad calories) fails and retries ✓
- Retries give up after 2 tries ✓
- Error message is helpful ✓

Files to create:
- `tests/unit/llm/test_parser.py` — test validation, test retry on bad output

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
