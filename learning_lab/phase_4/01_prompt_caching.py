#!/usr/bin/env python3
"""
Phase 4 Day 1 (Morning): Prompt Caching

Key insight: Re-sending the same long system prompt on every request
is wasteful. Prompt caching lets Claude reuse it across calls,
slashing input token costs on repeated requests.

The pattern:
1. Mark system prompt (and optionally tool schemas) with cache_control
2. First call: cache MISS — Claude processes + stores the prompt
   → usage.cache_creation_input_tokens > 0
3. Subsequent calls (within 1 hour): cache HIT — Claude reads from cache
   → usage.cache_read_input_tokens > 0, input_tokens drops significantly

Cache rules to internalize:
- Minimum 1024 tokens to be cacheable (short prompts are not worth caching)
- TTL: 1 hour from last use (resets on each hit)
- Max 4 cache breakpoints per request
- Content processing order: tools → system → messages
  → Cache tool schemas FIRST so cached tools + system = max savings
- Any change to content BEFORE the cache_control marker invalidates it
  → Keep the stable system prompt first, dynamic content at the end

Cost impact (Sonnet pricing):
- Normal input tokens:  $3.00 / 1M tokens
- Cache creation:       $3.75 / 1M tokens  (25% premium to store)
- Cache read:           $0.30 / 1M tokens  (90% savings vs normal)

Break-even: if you repeat the same prompt 2+ times within 1 hour, you save.

Usage:
    python day1_caching.py

You will see:
    Call 1 (MISS) → cache_creation_input_tokens populated
    Call 2 (HIT)  → cache_read_input_tokens populated, cost drops ~90%
"""

import os
import asyncio
from anthropic import AsyncAnthropic

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set")

client = AsyncAnthropic(api_key=api_key)


# ============================================================================
# THE LONG SYSTEM PROMPT (must be ≥ 1024 tokens to cache)
#
# NomNom's real system prompt is a nutritionist persona + usage guidelines.
# We simulate a realistic-length version here.
# ============================================================================

NOMNOM_SYSTEM_PROMPT = """
You are NomNom, an AI-powered nutrition assistant with the personality of a
sarcastic but caring cat. You analyze food photos and give nutritional
breakdowns with witty commentary.

## Your Role
You are a certified nutrition expert who has memorized:
- USDA FoodData Central database (900,000+ foods)
- Standard serving size conventions (FDA, USDA)
- Macro and micronutrient composition of common and uncommon foods
- Regional cuisine variations (e.g., Thai vs. Chinese fried rice differ)
- Restaurant portion sizes vs. home-cooked portions
- Cooking methods and their nutritional impact (frying adds fat, boiling
  reduces water-soluble vitamins, etc.)

## Analysis Framework
When analyzing a food photo, follow this structured approach:

Step 1 — Identify the food
- Name the dish precisely (e.g., "Chicken Caesar Salad" not "salad")
- Note preparation method (grilled, fried, baked, raw)
- Estimate portion size relative to standard reference objects in image
- Identify all visible components (dressing, croutons, cheese separately)

Step 2 — Estimate macronutrients
- Calories: estimate total kcal
- Protein (g): primary protein sources
- Carbohydrates (g): total and fiber separately
- Fat (g): total, distinguish saturated vs unsaturated if possible
- Sodium (mg): especially for restaurant meals or processed foods

Step 3 — Assign confidence level
- HIGH: recognizable dish with standard composition
- MEDIUM: ambiguous portion size or hidden ingredients
- LOW: blurry, obscured, or unfamiliar cuisine

Step 4 — Generate NomNom commentary
- Lead with the cat's personality: skeptical, slightly judgmental, secretly
  caring
- Reference specific visual details in the photo
- End with one actionable insight (not a lecture)

## Boundaries
- Never diagnose medical conditions
- Never provide personalized diet plans without user health profile
- Always clarify when a food is outside your confidence range
- Flag allergens when identifiable (nuts, shellfish, dairy, gluten)

## Output Format
Always return structured JSON via tool_use. Never return free-form text
for nutritional data — only use the structured schema provided.

## Tone Examples
WRONG: "This appears to be approximately 450 calories."
RIGHT: "450 calories. That's... ambitious for a Tuesday. But the avocado
is a nice touch — your heart appreciates you even if your portion control
doesn't."

WRONG: "I cannot determine the exact calorie count."
RIGHT: "Look, I'm a cat not a food scale. But given that mountain of pasta,
I'd say we're looking at 600-800 kcal. The pesto alone is doing heavy
lifting."
""".strip()


# ============================================================================
# PRICING (per 1M tokens) — Sonnet 3.5
# ============================================================================

PRICING = {
    "input":            3.00,   # $3.00 / 1M normal input tokens
    "cache_creation":   3.75,   # $3.75 / 1M cache write tokens
    "cache_read":       0.30,   # $0.30 / 1M cache read tokens
    "output":          15.00,   # $15.00 / 1M output tokens
}

def compute_cost(usage) -> dict:
    """Compute USD cost breakdown from a response usage object."""
    input_tokens     = getattr(usage, "input_tokens", 0)
    output_tokens    = getattr(usage, "output_tokens", 0)
    cache_creation   = getattr(usage, "cache_creation_input_tokens", 0)
    cache_read       = getattr(usage, "cache_read_input_tokens", 0)

    # Cache-read tokens are NOT counted in input_tokens, so we add them back
    # for display, but they're priced at the discount rate.
    cost_input          = input_tokens     * PRICING["input"]          / 1_000_000
    cost_cache_creation = cache_creation   * PRICING["cache_creation"] / 1_000_000
    cost_cache_read     = cache_read       * PRICING["cache_read"]     / 1_000_000
    cost_output         = output_tokens    * PRICING["output"]         / 1_000_000
    cost_total          = cost_input + cost_cache_creation + cost_cache_read + cost_output

    return {
        "input_tokens":           input_tokens,
        "output_tokens":          output_tokens,
        "cache_creation_tokens":  cache_creation,
        "cache_read_tokens":      cache_read,
        "cost_input_usd":         round(cost_input, 6),
        "cost_cache_creation_usd": round(cost_cache_creation, 6),
        "cost_cache_read_usd":    round(cost_cache_read, 6),
        "cost_output_usd":        round(cost_output, 6),
        "cost_total_usd":         round(cost_total, 6),
    }


def print_usage(label: str, usage, cost: dict):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(f"  input_tokens             : {usage.input_tokens}")
    print(f"  output_tokens            : {usage.output_tokens}")
    print(f"  cache_creation_tokens    : {cost['cache_creation_tokens']}")
    print(f"  cache_read_tokens        : {cost['cache_read_tokens']}")
    print(f"  ---")
    print(f"  cost_input_usd           : ${cost['cost_input_usd']:.6f}")
    print(f"  cost_cache_creation_usd  : ${cost['cost_cache_creation_usd']:.6f}")
    print(f"  cost_cache_read_usd      : ${cost['cost_cache_read_usd']:.6f}")
    print(f"  cost_output_usd          : ${cost['cost_output_usd']:.6f}")
    print(f"  TOTAL                    : ${cost['cost_total_usd']:.6f}")


# ============================================================================
# EXPERIMENT 1: Basic system prompt caching
#
# Cache breakpoint is placed at the END of the system prompt block.
# Everything before it gets cached as one unit.
# ============================================================================

async def experiment_1_system_prompt_caching():
    print("\n" + "="*60)
    print("EXPERIMENT 1: System Prompt Caching")
    print("="*60)
    print("Goal: observe cache_creation on call 1, cache_read on call 2.")

    user_message = "Analyze this food: a large bowl of ramen with pork belly, soft-boiled egg, and nori."

    # ── Call 1: cache MISS (first time Claude sees this prompt)
    print("\n▶ Call 1 (expect cache MISS → cache_creation_input_tokens > 0)")
    response_1 = await client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=256,
        system=[
            {
                "type": "text",
                "text": NOMNOM_SYSTEM_PROMPT,
                # ↑ cache_control goes on the LAST block you want cached.
                # Everything up to (and including) this block gets stored.
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_message}],
    )

    cost_1 = compute_cost(response_1.usage)
    print_usage("Call 1 — MISS", response_1.usage, cost_1)
    print(f"\n  Claude says: {response_1.content[0].text[:120]}...")

    # ── Call 2: cache HIT (same system prompt, different user message)
    print("\n▶ Call 2 (expect cache HIT → cache_read_input_tokens > 0)")
    response_2 = await client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=256,
        system=[
            {
                "type": "text",
                "text": NOMNOM_SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": "What about a plain Greek yogurt with honey?"}],
    )

    cost_2 = compute_cost(response_2.usage)
    print_usage("Call 2 — HIT", response_2.usage, cost_2)
    print(f"\n  Claude says: {response_2.content[0].text[:120]}...")

    # ── Compare
    print(f"\n{'='*60}")
    print("  COMPARISON")
    print(f"{'='*60}")
    print(f"  Call 1 total cost : ${cost_1['cost_total_usd']:.6f}")
    print(f"  Call 2 total cost : ${cost_2['cost_total_usd']:.6f}")
    if cost_1['cost_total_usd'] > 0:
        savings_pct = (1 - cost_2['cost_total_usd'] / cost_1['cost_total_usd']) * 100
        print(f"  Savings on call 2 : {savings_pct:.1f}%")
    print()
    print("  Key insight: cache_creation happens once. Every subsequent call")
    print("  within 1 hour pays only cache_read (10% of normal input cost).")


# ============================================================================
# EXPERIMENT 2: Cache invalidation
#
# Changing ANY content BEFORE the cache_control marker invalidates the cache.
# Appending dynamic content AFTER the marker is safe.
# ============================================================================

async def experiment_2_cache_invalidation():
    print("\n" + "="*60)
    print("EXPERIMENT 2: Cache Invalidation")
    print("="*60)
    print("Goal: understand what breaks the cache.")

    base_prompt = NOMNOM_SYSTEM_PROMPT

    # ── Call A: stable prompt — will warm the cache
    print("\n▶ Call A: stable system prompt (warms cache)")
    resp_a = await client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=64,
        system=[{"type": "text", "text": base_prompt, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": "Quick test: what is your name?"}],
    )
    cost_a = compute_cost(resp_a.usage)
    print(f"  cache_creation: {cost_a['cache_creation_tokens']}  "
          f"cache_read: {cost_a['cache_read_tokens']}")

    # ── Call B: modified prompt (prepend one word) — INVALIDATES cache
    print("\n▶ Call B: modified system prompt (prepend 'NOTE: ' before stable content)")
    print("  → Adding content BEFORE the cache_control block breaks the cache.")
    modified_prompt = "NOTE: Dynamic prefix injected here.\n\n" + base_prompt
    resp_b = await client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=64,
        system=[{"type": "text", "text": modified_prompt, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": "Quick test: what is your name?"}],
    )
    cost_b = compute_cost(resp_b.usage)
    print(f"  cache_creation: {cost_b['cache_creation_tokens']}  "
          f"cache_read: {cost_b['cache_read_tokens']}")
    print()
    print("  Key insight: if you need to inject dynamic content (user name,")
    print("  date, preferences) put it AFTER the cached block, not before.")
    print("  Structure: [stable cached block] + [dynamic block] in system.")


# ============================================================================
# EXPERIMENT 3: Caching tool schemas alongside system prompt
#
# Tool schemas are sent before the system prompt in the API's processing
# order. Cache them first to maximize savings on tool-heavy requests.
# ============================================================================

ANALYZE_FOOD_TOOL = {
    "name": "analyze_food",
    "description": "Return structured nutritional analysis for a food item",
    "input_schema": {
        "type": "object",
        "properties": {
            "food_name":     {"type": "string"},
            "calories":      {"type": "number"},
            "protein_g":     {"type": "number"},
            "carbs_g":       {"type": "number"},
            "fat_g":         {"type": "number"},
            "confidence":    {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
            "commentary":    {"type": "string"},
        },
        "required": ["food_name", "calories", "protein_g", "carbs_g", "fat_g",
                     "confidence", "commentary"],
    },
}

async def experiment_3_tool_schema_caching():
    print("\n" + "="*60)
    print("EXPERIMENT 3: Tool Schema + System Prompt Caching")
    print("="*60)
    print("Goal: cache both tool schema AND system prompt together.")
    print("Processing order: tools first, then system, then messages.")
    print("→ Place cache_control on tools to include them in the cache.\n")

    user_message = "Analyze this: a plate of sushi — 6 pieces of salmon nigiri."

    # ── Call 1: cache MISS
    print("▶ Call 1 (MISS)")
    resp_1 = await client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=256,
        tools=[{**ANALYZE_FOOD_TOOL, "cache_control": {"type": "ephemeral"}}],
        tool_choice={"type": "auto"},
        system=[{"type": "text", "text": NOMNOM_SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user_message}],
    )
    cost_1 = compute_cost(resp_1.usage)
    print(f"  cache_creation: {cost_1['cache_creation_tokens']}  "
          f"cache_read: {cost_1['cache_read_tokens']}  "
          f"total: ${cost_1['cost_total_usd']:.6f}")

    # ── Call 2: cache HIT
    print("▶ Call 2 (HIT)")
    resp_2 = await client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=256,
        tools=[{**ANALYZE_FOOD_TOOL, "cache_control": {"type": "ephemeral"}}],
        tool_choice={"type": "auto"},
        system=[{"type": "text", "text": NOMNOM_SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": "Analyze this: a chicken burrito bowl."}],
    )
    cost_2 = compute_cost(resp_2.usage)
    print(f"  cache_creation: {cost_2['cache_creation_tokens']}  "
          f"cache_read: {cost_2['cache_read_tokens']}  "
          f"total: ${cost_2['cost_total_usd']:.6f}")

    print()
    print("  Key insight: on a busy NomNom server handling 1000 requests/day,")
    print("  caching the system prompt + tool schemas saves ~$X/day.")
    print("  Compute: 1000 × (normal_cost - cached_cost) = daily savings.")


# ============================================================================
# MAIN
# ============================================================================

async def main():
    print("Phase 4 Day 1: Prompt Caching")
    print("Model: claude-sonnet-4-5")
    print()
    print("Running 3 experiments:")
    print("  1. Basic system prompt caching (MISS → HIT pattern)")
    print("  2. Cache invalidation (what breaks the cache)")
    print("  3. Tool schema + system prompt caching together")

    await experiment_1_system_prompt_caching()
    await experiment_2_cache_invalidation()
    await experiment_3_tool_schema_caching()

    print("\n" + "="*60)
    print("SUMMARY — What you should now know:")
    print("="*60)
    print("1. Add cache_control={'type':'ephemeral'} to stable content blocks")
    print("2. cache_creation on first call, cache_read on subsequent calls")
    print("3. Dynamic content goes AFTER the cached block, not before")
    print("4. Cache tools + system prompt together for max savings")
    print("5. Cache TTL is 1 hour, resets on each hit")
    print("6. Minimum 1024 tokens to qualify for caching")
    print("7. Break-even: 2+ identical calls in 1 hour = net savings")


if __name__ == "__main__":
    asyncio.run(main())
