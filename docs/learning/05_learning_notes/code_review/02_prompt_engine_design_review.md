# Code Review: `src/llm/prompt_engine.py`

## What This File Does

This module renders prompts. It provides a core `render_prompt()` function that loads Jinja2 templates and injects variables, plus 3 specialized wrapper functions for different prompts (food analysis, meal recommendations, weekly recap). It exists so prompts live in separate `.j2` files instead of being hardcoded in Python.

## Understanding Jinja2 (Background)

Jinja2 is Python's most popular template engine. It takes a template file (with placeholders) + variables, and combines them into a final string.

**Core syntax:**

| Syntax | Meaning |
|---|---|
| `{{ variable }}` | Variable substitution |
| `{% if condition %} ... {% elif %} ... {% else %} ... {% endif %}` | Conditional block |
| `{% include "file.j2" %}` | Include another template |

## How It Works at Runtime

```
[1] User uploads food photo in iOS app
    ↓
[2] FastAPI backend calls: render_analyze_food_prompt(cat_style="sassy")
    ↓
[3] prompt_engine internally:
    - Jinja2 loads prompts/analyze_food.j2
    - Injects cat_style="sassy"
    - Processes {% include "cat_personas.j2" %}
    - The if/elif chain in cat_personas.j2 matches "sassy"
    - Returns the combined string
    ↓
[4] String passed to: client.create_message_with_retry(...)
    ↓
[5] client.py sends to Anthropic API (Haiku)
    ↓
[6] Claude returns food analysis JSON
```

## Templates in `prompts/` (Real Inventory)

### `analyze_food.j2` — Food photo analysis (for Haiku)

**Purpose:** Extract nutrition data + personality commentary from food photos

**Variables used:** `{{ cat_style }}` (injected via include)

**Structure:**
- Comment header (2 lines)
- `{% include "cat_personas.j2" %}` at the top (establishes personality)
- JSON output schema (7 fields: food_name, calories, protein_g, carbs_g, fat_g, food_category, cuisine_origin, cat_roast)
- Rules: concise names, realistic calories (300-1200)
- 2 few-shot examples (Big Mac & fries, Caesar salad)

**Prompt engineering techniques:**
- Role assignment via cat_personas include
- Structured JSON output format (enforces consistency)
- Few-shot examples (2 diverse examples: high-cal fast food + low-cal healthy)
- Guardrails (calorie bounds, concise naming)

**Design insight:** `{{ cat_style }}` appears twice — once in the persona, once in the JSON schema field. This is defense in depth: the include establishes overall tone, the field reference reinforces it at the specific place that needs it (cat_roast).

---

### `cat_personas.j2` — Personality definitions

**Purpose:** Define 5 cat personalities that inject tone into other prompts

**Variables used:** `{{ cat_style }}` (conditional selector)

**Structure:** `{% if/elif/else %}` chain with 5 personalities:
- `sassy` — sharp, witty, judgmental
- `grumpy` — curmudgeonly, dry humor
- `wholesome` — encouraging, supportive
- `concerned` — worried about health
- `neutral` (default) — observant, non-judgmental

**Defensive design:** Any unrecognized `cat_style` silently falls back to neutral. No crash, no error — graceful degradation.

**Prompt engineering techniques:**
- Conditional role switching (one role per style)
- Concrete voice examples ("Think: ...") for each personality
- Default fallback for robustness

---

### `recommend_meal.j2` — Meal recommendation

**Purpose:** Suggest meals based on nutrition targets, preferences, restrictions, and meal history

**Variables used:** `today_calories`, `today_protein`, `today_carbs`, `today_fat`, `target_calories`, `target_protein`, `target_carbs`, `target_fat`, `missing_calories`, `missing_protein`, `missing_carbs`, `missing_fat`, `dietary_restrictions`, `cuisine_preferences`, `allergies`, `recent_meals` (list), `kb_entries` (list)

**Structure:**
- Role: "friendly nutrition assistant"
- User Profile section (current macros, targets, missing amounts, restrictions, preferences, allergies)
- Recent Meals section (loop over recent_meals)
- Nutrition Knowledge Base section (loop over kb_entries)
- Instructions: suggest 2-3 meals, explain why, include fun fact
- Tone: conversational, encouraging

**Prompt engineering techniques:**
- Context marshaling (comprehensive data provided)
- Structured data organization (markdown headers for clarity)
- Loops for dynamic content (recent_meals, kb_entries)
- Safe defaults (`{{ dietary_restrictions if dietary_restrictions else 'None' }}` prevents null errors)
- Explicit output format (numbered bullets)
- Warm tone (encouraging vs. sarcastic)

**What could be improved:**
- Add constraint: "Keep suggestions realistic (easy to prepare, available)"
- Add priority: "Fill the largest nutrition gap first"
- Handle edge case: "If user is new (0 recent meals), suggest meal variety"

---

### `weekly_recap.j2` — Weekly summary

**Purpose:** Generate entertaining weekly food habit summaries

**Variables used:** `week_start`, `week_end`, `total_meals_logged`, `avg_calories`, `best_day`, `best_day_calories`, `worst_day`, `worst_day_calories`, `most_eaten_category`, `avg_protein`, `avg_carbs`, `avg_fat`, `cat_style`, `meals` (list)

**Structure:**
- Header (week start/end)
- Statistics section (8 metrics)
- Meals This Week section (loop over meals)
- 5-step narrative arc:
  1. Open with witty observation
  2. Call out patterns
  3. Celebrate wins
  4. Nudge toward improvement
  5. Encourage for next week
- Secondary output: "Actionable Nudge" (specific, easy suggestion)

**Prompt engineering techniques:**
- Narrative arc (5-step structure guides coherent output)
- Dynamic personality (`{{ cat_style }}` varies tone)
- Statistical grounding (raw metrics provided)
- Loops for recent content
- Tone guidance ("Be funny, be honest, be kind")
- Secondary output (actionable next step)

**What could be improved:**
- Add length constraint: "3-5 paragraphs (not essays)"
- Handle edge case: "If only 1 meal logged all week, be encouraging, not critical"
- Clarify tone alignment between recap and Actionable Nudge

---

## Summary: Prompt Engineering Techniques Across All 4

| Technique | Used? | Where |
|-----------|-------|-------|
| **Role assignment** | ✅ | All 4 (cat personas, nutrition assistant, food critic) |
| **Few-shot examples** | ✅ | analyze_food.j2 (2 examples) |
| **Structured output format** | ✅ | All 4 (JSON, markdown, bullets) |
| **Context marshaling** | ✅ | recommend_meal.j2, weekly_recap.j2 |
| **Loops/iteration** | ✅ | recommend_meal.j2, weekly_recap.j2 |
| **Conditionals** | ✅ | cat_personas.j2, recommend_meal.j2 |
| **Tone/style guidance** | ✅ | All 4 |
| **Guardrails/constraints** | ✅ | analyze_food.j2 (calorie bounds 300-1200) |
| **Default fallbacks** | ✅ | cat_personas.j2 (neutral default), recommend_meal.j2 (safe defaults) |

**Overall assessment:** The prompts are well-designed, intentional, and professional. They use industry-standard techniques with no major red flags.

---

## Design Choices I Can Defend

### Why Jinja2 templates instead of hardcoded f-strings in .py?

Prompts are product assets, not code. They change more frequently than Python logic. Hardcoding forces every prompt iteration through the code deployment cycle. Template files decouple prompt changes from code changes — a non-engineer (or me, fast) can edit a `.j2` without touching `.py`.

### Why specialized wrappers like `render_analyze_food_prompt()`?

These functions act as an API contract. Callers see the explicit signature (`cat_style="sassy"`) instead of needing to remember the template filename + variable names. This prevents typos, enables IDE autocomplete, and makes the call site self-documenting.

### Why include `cat_personas.j2` instead of inlining 5 personas in each template?

DRY. Multiple templates likely want the same cat personalities. Without extraction, every change to a persona would need to be repeated across each template that uses it. Extraction = single source of truth.

### Why does `analyze_food.j2` target Haiku, not Sonnet?

Image-to-JSON food analysis is a simple, high-frequency, latency-sensitive task. Haiku's strengths (fast, cheap, sufficient quality for structured output) match this use case. Combined with `MODEL_CONFIG` in `client.py` (Haiku timeout=20s, max_tokens=400), the design is optimized for low latency at high call frequency.

### Why exactly 2 few-shot examples in `analyze_food.j2` (not 1 or 5)?

- 1 example: not enough diversity, model may overfit
- 5 examples: token bloat (Haiku max_tokens=400 for output)
- 2 examples: meaningful axes — one high-calorie fast food (Big Mac), one low-calorie healthy (Caesar salad). Together they anchor both ends of the realistic range.

### Why does `{% include "cat_personas.j2" %}` come at the TOP of the template?

Persona/role should frame the entire downstream output. Putting it at the end risks Claude treating the persona as an afterthought decoration rather than the guiding tone.

### Why is `{{ cat_style }}` referenced AGAIN in the JSON schema (in `cat_roast` field)?

Reinforces the field-level constraint. Even though `cat_personas.j2` establishes the role, repeating `{{ cat_style }}` at the specific field that needs it (cat_roast) reduces the risk of Claude generating that field in a default/neutral tone. Critical constraints restated near where they apply have higher compliance rates.

### Why functions, not a class?

No persistent state needed. Each `render_*` call is stateless: load template → inject variables → return string. A module-level `jinja_env` constant handles the Jinja2 setup once. Class would add structure without benefit at this scale.

---

## Open Questions / Things I Don't Fully Understand

- How does Jinja2 handle injection safety if a user-generated string ends up in a template variable? (e.g., if a malicious `cat_style` contained `{% raw %}` markers, would it confuse rendering?)
- Should there be runtime validation that all required template variables are provided before render? (Currently a missing variable raises an error from Jinja2, not a friendly error from prompt_engine.)

## Things I Would Change

- Nothing critical for current scale. The design cleanly separates prompt iteration from code iteration, which is the main goal.
- **Future consideration:** If `recommend_meal.j2` / `weekly_recap.j2` also start using cat personas, the `{% include "cat_personas.j2" %}` pattern will be more clearly justified.

---

## Follow-up Q&A (Interview Prep)

### Q: What happens if a developer adds a new cat_style "playful" in iOS UI but forgets to add `{% elif cat_style == "playful" %}` in cat_personas.j2?

A: The `{% if/elif/else %}` chain falls through to `{% else %}`, which is the "neutral" persona. No crash, no error — just silent degradation to neutral. This is defensive design: prod doesn't break, but the bug is also harder to catch because there's no log/warning.

### Q: Why does `cat_style` appear twice in `analyze_food.j2` (once via include, once in the JSON schema)?

A: Defense in depth. The include establishes the overall persona framing. The JSON schema reference reinforces it at the specific field (cat_roast) that needs to use the persona. Without the second reference, Claude might treat `cat_roast` as a generic field and lose the persona voice.

### Q: Why is `analyze_food.j2` designed for Haiku rather than Sonnet?

A: It's a simple structured task (image → JSON). Haiku is faster, cheaper, and 400 max_tokens is enough for the schema. NomNom calls this on every food photo upload — high frequency = cost optimization matters.

### Q: How would you test if a prompt change in `analyze_food.j2` actually improved results?

A: This is what Phase 2's eval pipeline (`evaluator.py` + test dataset) is for. Before merging a `.j2` change, run the eval suite: structured parse rate, accuracy on test photos, regression check. Without this, prompt changes are vibes-based. **(Phase 2 will deepen this.)**

---

## Capability Profile Update (after Day 7)

- **Layer 1 (Prompt Engineering):** 1/5 → 3/5
  - Evidence: Defended prompt template architecture, articulated 7 design choices with reasoning
- **Layer 2 (Output Control):** 1/5 → 2/5
  - Evidence: Identified field-level constraint reinforcement pattern (cat_style in both persona and JSON schema)

---

## Phase 1 Status

- ✅ Day 6: client.py review (Layer 0 — API resilience)
- ✅ Day 7: prompt_engine.py review (Layer 1 — prompt engineering infrastructure)
- ⏳ Next: Phase 2 (parser.py, guardrails.py, evaluator.py, tools.py)

## Phase 6 Follow-up TODOs

- Deep audit of recommend_meal.j2 + weekly_recap.j2
- Verify Jinja2 injection safety
- Confirm if all 4 templates use cat_personas (validates DRY justification)
