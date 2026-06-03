# Code Review: `src/llm/prompt_engine.py`

## What This File Does

This module renders prompts. It provides a core `render_prompt()` function that generates templated prompts, plus 3 specialized wrapper functions that generate different prompts for different use cases (food analysis, meal recommendations, weekly recap). It exists so that product people only need to update the .j2 files without changing any Python code.

## Understanding Jinja2 (In Simple Terms)

**What is Jinja2?**

Jinja2 = Python's most popular "template engine." It takes a template file (with placeholders) + variables, and combines them into a final string.

**Example without Jinja2:**

```python
# Hardcoded in Python
prompt = f"Analyze this food. Diet: {diet}. Calories: {calories}."
```

Problems:
- Long prompts (hundreds of lines) become messy in Python code
- Every prompt change requires changing Python code + redeploy
- Hard to add conditionals (e.g., "if vegetarian, add this text")

**Example with Jinja2:**

File: `prompts/analyze_food.j2` (plain text, not Python):
```jinja2
Analyze this food image.

User's diet preference: {{ diet }}
Calorie target: {{ calorie_target }}

{% if vegetarian %}
Only recommend vegetarian options.
{% endif %}

Cat persona:
{% include "cat_personas.j2" %}
```

Python code:
```python
prompt = render_prompt(
    "analyze_food.j2",
    diet="weight loss",
    calorie_target=600,
    vegetarian=True
)
# Returns: fully rendered string ready for Claude
```

**Jinja2 Core Syntax:**

| Syntax | Meaning | Example |
|--------|---------|---------|
| `{{ variable }}` | Variable substitution | `{{ diet }}` → "weight loss" |
| `{% if condition %} ... {% endif %}` | Conditional block | Only include text if condition is true |
| `{% include "file.j2" %}` | Include another template | `{% include "cat_personas.j2" %}` |

## How It Works at Runtime

**Flow: User upload → Prompt generation → Claude call**

```
[1] User uploads food photo in iOS app
    ↓
[2] FastAPI backend receives request
    ↓
[3] Backend calls: render_analyze_food_prompt(cat_style="sassy")
    ↓
[4] prompt_engine internally:
    - Jinja2 loads prompts/analyze_food.j2
    - Injects cat_style="sassy" variable
    - Processes: {% include "cat_personas.j2" %}
    - Selects the "sassy" personality block from cat_personas.j2
    - Combines everything into one complete string
    ↓
[5] Returns fully rendered prompt string
    ↓
[6] String passed to: client.create_message_with_retry(messages=[{content: prompt}])
    ↓
[7] client.py sends to Anthropic API
    ↓
[8] Claude returns food analysis
```

**Key insight:** The 4 .j2 files (analyze_food.j2, cat_personas.j2, recommend_meal.j2, weekly_recap.j2) are **handwritten by developers**, not generated. Jinja2 just renders them.

## Before and After: The Problem It Solves

**Without prompt_engine.py (hardcoded prompts in Python):**
```python
def get_analyze_food_prompt(cat_style):
    if cat_style == "sassy":
        persona = "You are a sassy, judgmental cat with a sharp tongue..."
    elif cat_style == "grumpy":
        persona = "You are a grumpy cat who criticizes everything..."
    
    prompt = f"""{persona}
    
Analyze the food photo. Respond with ONLY JSON:
{{"food_name": "...", "calories": ..., "cat_roast": "..."}}"""
    return prompt
```

Problems:
- Has to update Python code every time you want to change wording
- Every change requires code review and redeployment
- Product people can't edit without a developer
- Hard to A/B test different phrasings (need to write new code each time)
- Prompt logic mixed with Python logic (hard to maintain)

**With prompt_engine.py (Jinja2 templates):**
```python
prompt = render_analyze_food_prompt(cat_style="sassy")
```

Benefits:
- Separate Python code from .j2 files (clean separation of concerns)
- Product people can edit .j2 templates directly without touching code
- Prompt changes deploy instantly (no redeployment needed)
- Easy to A/B test different phrasings (just edit the template and refresh)
- Prompts are version-controlled separately from Python logic
- Reusable templates (cat_personas.j2 included in multiple prompts, DRY principle)

## Design Choices I Can Defend

### Why Jinja2 templates instead of hardcoding?

Prompts are **product assets, not code**. They change 10x more frequently than code. Hardcoding forces product iteration through the Python development cycle (code change → review → test → deploy). Jinja2 templates decouple prompt changes from code changes.

**Philosophy:** Prompts should live in their own files so non-engineers can iterate on them independently.

### Why specialized wrapper functions like `render_analyze_food_prompt()`?

These functions serve as an **API contract**. Instead of callers needing to know `render_prompt("analyze_food.j2", cat_style=...)`, they call `render_analyze_food_prompt(cat_style=...)`.

Benefits:
- **Type safety:** Function signature shows required parameters
- **IDE autocomplete:** Editor knows what parameters exist
- **Prevent bugs:** Can't typo the template name or forget required parameters
- **Self-documenting:** New engineer reads the function name and knows exactly what it does

**Philosophy:** Explicit contracts prevent mistakes.

### Why include `cat_personas.j2` inside `analyze_food.j2`?

Multiple prompts will need the same cat personalities (analyze_food, recommend_meal, weekly_recap). Without extracting, you'd duplicate the 5 cat personas across 4 files. Every time you want to update a persona, you'd change it in 4 places (risk of getting out of sync).

By including `cat_personas.j2`, changes in one place automatically propagate everywhere.

**Philosophy:** DRY principle — single source of truth for reused content.

### Why Jinja2 specifically?

Jinja2 is lightweight, widely used in web frameworks (Flask, Django), and easy to learn. It supports:
- Variable substitution: `{{ variable }}`
- Conditionals: `{% if condition %}`
- Loops: `{% for item in list %}`
- Template inclusion: `{% include "file.j2" %}`

This lets you keep prompts readable while adding just enough logic.

### Why functions, not a class?

The module uses **functions, not a class**, because:

1. **No state needed.** Each render call is independent: load template → inject variables → return string. Functions are sufficient.

2. **Simplicity.** `render_analyze_food_prompt(cat_style="sassy")` is simpler than instantiating a class: `engine = PromptEngine(); engine.render_analyze_food_prompt(...)`.

3. **Global Jinja2 environment.** The `jinja_env` is created once at module load and reused. This is fine as a module-level constant — no need to wrap it in a class.

4. **Factory pattern.** Think of it as a lightweight factory: `render_prompt()` is the core, and `render_*_prompt()` functions are convenience factories for specific use cases.

**When you'd use a class instead:**
- If you needed different Jinja2 configurations per instance
- If you needed to cache rendered templates per instance
- If the object stored state (e.g., render history, metrics)

**Philosophy:** Keep it simple — use the simplest structure that solves the problem.

## Analysis of prompts/ Folder

The 4 prompt templates use industry-standard prompt engineering techniques. Here's what each does:

### `analyze_food.j2` — Food Photo Analysis

**Prompt engineering techniques:**
- **Role assignment:** "You are a {{ cat_style }} cat"
- **Structured output:** Enforces JSON format (no markdown, specific fields)
- **Few-shot examples:** Shows 2 real food examples with expected output
- **Clear rules:** "Be accurate with nutrition. Calories realistic (300-1200). Entertain, don't be cruel."
- **Guardrails:** Bounds on calorie ranges, concise naming rules

**Structure:** ✅ **Intentional and clear**
- Role comes from cat_personas.j2 (reusable across prompts)
- Output format is crystal clear (JSON structure shown)
- Examples teach the model without ambiguity
- Rules prevent common failures (unrealistic calories, cruelty)

**What I would change:** Nothing major. This is well-designed for its purpose (fast, reliable food analysis). Could add "nutrition values must sum to realistic totals" but might be unnecessary complexity.

---

### `cat_personas.j2` — Personality Definitions

**Prompt engineering techniques:**
- **Conditional role switching:** Each `cat_style` gets a different personality
- **Concrete voice examples:** Each persona has a "Think:" example showing speech pattern
- **Default fallback:** Unrecognized cat_style falls back to "neutral"

**Structure:** ✅ **Intentional and well-organized**
- Personalities are mutually exclusive (clean separation)
- Each has consistent voice + concrete example
- Default prevents crashes on unexpected input

**What I would change:**
- Add a comment explaining the tone spectrum: sassy (critical) → wholesome (supportive) → helps users pick personality
- Consider adding personas: "playful" (mischievous) or "lazy" (indifferent) if product wants more variety

---

### `recommend_meal.j2` — Meal Recommendation

**Prompt engineering techniques:**
- **Context marshaling:** Provides all relevant data (macros, preferences, restrictions, past meals, knowledge base)
- **Structured data organization:** Uses markdown **headers** to organize sections
- **Loops:** Iterates over recent_meals and kb_entries (Jinja2 `{% for %}`)
- **Safe defaults:** `{{ dietary_restrictions if dietary_restrictions else 'None' }}` prevents empty/null errors
- **Explicit output format:** "Format as: 1. suggestions, 2. why, 3. fun fact"
- **Tone:** Conversational and encouraging (warmer than analyze_food's roasting)

**Structure:** ✅ **Intentional and clear**
- Data hierarchy is readable (User Profile → Recent Meals → KB)
- Expectations are explicit (2-3 options, reasoning, fun fact)
- Tone matches the use case (helping, not judging)

**What I would change:**
- Add constraint: "Keep suggestions realistic (easy to prepare, available ingredients)"
- Add priority: "Prioritize suggestions that fill the largest nutrition gap first"
- Add edge case: "If user has 0 recent meals (new user), suggest meal variety and common beginner mistakes to avoid"

---

### `weekly_recap.j2` — Weekly Summary

**Prompt engineering techniques:**
- **Narrative arc:** 5-step structure (open with wit → patterns → wins → nudge → encourage)
- **Dynamic personality:** Uses `{{ cat_style }}` to vary tone across recaps
- **Statistical context:** Raw data (meals, macros, best/worst days) provides grounding
- **Loops:** Lists all meals logged that week
- **Tone guidance:** "Be funny, be honest, but be kind"
- **Secondary output:** "Actionable Nudge" (specific, easy suggestion for next week)

**Structure:** ✅ **Intentional and clear**
- The 5-step arc guides output without being rigid
- Cat style variation keeps it fresh across weeks
- Statistics ground the narrative in data

**What I would change:**
- Add length constraint: "Keep recap to 3-5 paragraphs (not essays)"
- Add edge case: "If user logged only 1 meal all week, be encouraging, not critical"
- Clarify alignment: The "Actionable Nudge" sometimes contradicts the recap tone. Could align them: if recap is playful, nudge should be playful too

---

## Summary: Prompt Engineering Techniques Used

| Technique | Used? | Where |
|-----------|-------|-------|
| **Role assignment** | ✅ | All 4 (cat personas, nutrition assistant, food critic) |
| **Few-shot examples** | ✅ | analyze_food.j2 |
| **Structured output format** | ✅ | All 4 (JSON, markdown, bullets) |
| **Context marshaling** | ✅ | recommend_meal.j2, weekly_recap.j2 |
| **Loops/iteration** | ✅ | recommend_meal.j2, weekly_recap.j2 |
| **Conditionals** | ✅ | cat_personas.j2, recommend_meal.j2 |
| **Tone/style guidance** | ✅ | All 4 |
| **Guardrails/constraints** | ✅ | analyze_food.j2 (calorie bounds) |

**Overall:** The prompts are well-designed, intentional, and professional. They use industry-standard techniques. No major red flags.

## Design Choices I Still Don't Understand

- How does Jinja2 handle escaping/security if prompts contain user-generated content? (e.g., if a user's food name gets injected into a template, could that cause issues?)
- Should there be validation to ensure all required context keys are provided before rendering? (Currently it just errors if a key is missing.)

## Things I Would Change

None yet. The design cleanly separates concerns and enables fast product iteration.
