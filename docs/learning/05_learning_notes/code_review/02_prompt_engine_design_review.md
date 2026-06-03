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

## Design Choices I Still Don't Understand

- How does Jinja2 handle escaping/security if prompts contain user-generated content? (e.g., if a user's food name gets injected into a template, could that cause issues?)
- Should there be validation to ensure all required context keys are provided before rendering? (Currently it just errors if a key is missing.)

## Things I Would Change

None yet. The design cleanly separates concerns and enables fast product iteration.
