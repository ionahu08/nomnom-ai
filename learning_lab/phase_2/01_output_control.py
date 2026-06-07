#!/usr/bin/env python3
"""
Phase 2 Day 1: Output Control Trio

Three techniques to force Claude into predictable output formats:
1. Prefill assistant content — manually inject an assistant message to guide format
2. Stop sequences — model halts when it generates a specified string
3. Prefill + Stop combo — classic structured output (prefill JSON start, stop at closing }})

Each demo analyzes the same food and requests JSON output, but uses different
techniques to guarantee the format. Compare the results.

Usage:
    python 01_output_control.py
"""

import os
import json
import asyncio
from anthropic import AsyncAnthropic

# Initialize Anthropic client
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set")

client = AsyncAnthropic(api_key=api_key)


async def demo_1_prefill_assistant():
    """
    Technique 1: Prefill Assistant Content

    Manually inject an assistant message that starts the response in the desired format.
    Claude will continue from where you left off, completing the JSON structure.

    Why it works:
    - Claude sees it already "started" returning JSON
    - Natural continuation = finishing the JSON object
    - Less restrictive than stop sequences

    Trade-off:
    - Uses tokens for the prefilled content (wasteful if it's long)
    - Requires you to know the exact format to prefill
    """

    print("\n" + "=" * 70)
    print("DEMO 1: Prefill Assistant Content")
    print("=" * 70)

    user_prompt = """Analyze this food: "grilled chicken Caesar salad with croutons"

Respond with ONLY valid JSON (no markdown, no extra text):
{
  "food_name": "...",
  "calories": number,
  "protein_g": number,
  "carbs_g": number,
  "fat_g": number
}"""

    # Prefill: start the assistant message with the opening of the JSON object
    # Claude will continue from here and complete the fields
    prefilled_response = "{"

    messages = [
        {"role": "user", "content": user_prompt},
        # This is the key: inject an assistant message that's already started
        {"role": "assistant", "content": prefilled_response},
    ]

    print("\nMessages structure:")
    print(f"  1. User asks for JSON")
    print(f"  2. Assistant already has: '{prefilled_response}'")
    print(f"\nClaude must continue the JSON from where we left off...")

    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=messages,
    )

    # The response is a continuation of our prefill, so we need to add the opening "{"
    full_response = prefilled_response + response.content[0].text

    print(f"\nClaude's continuation: {response.content[0].text}")
    print(f"\nFull JSON (prefill + continuation):\n{full_response}")

    # Try to parse it
    try:
        parsed = json.loads(full_response)
        print(f"✅ Valid JSON! Parsed: {json.dumps(parsed, indent=2)}")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")


async def demo_2_stop_sequences():
    """
    Technique 2: Stop Sequences

    Tell Claude to stop generating when it produces a specific string.
    Common use: ask for JSON, set stop sequence to `}` so Claude halts after closing brace.

    Why it works:
    - Claude generates freely but stops at the specified string
    - No token waste from prefilling
    - Works for any format (JSON, markdown, code, etc.)

    Trade-off:
    - If Claude hasn't finished the structure by stop sequence, output is incomplete
    - Requires you to choose the right stopping point
    """

    print("\n" + "=" * 70)
    print("DEMO 2: Stop Sequences")
    print("=" * 70)

    user_prompt = """Analyze this food: "grilled chicken Caesar salad with croutons"

Respond with ONLY valid JSON (no markdown, no extra text):
{
  "food_name": "...",
  "calories": number,
  "protein_g": number,
  "carbs_g": number,
  "fat_g": number
}"""

    messages = [
        {"role": "user", "content": user_prompt},
    ]

    print("\nUsing stop_sequences=['}'] — Claude stops after first }")
    print("No prefilling, Claude starts fresh...")

    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=messages,
        stop_sequences=["}"],  # Stop after closing brace
    )

    output = response.content[0].text + "}"  # Add back the } that triggered the stop

    print(f"\nClaude's response:\n{output}")

    # Try to parse it
    try:
        parsed = json.loads(output)
        print(f"✅ Valid JSON! Parsed: {json.dumps(parsed, indent=2)}")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")


async def demo_3_prefill_stop_combo():
    """
    Technique 3: Prefill + Stop Combo (MOST COMMON)

    Combine both techniques:
    1. Prefill: start with ` ```json ` to signal JSON is coming
    2. Stop sequence: halt at ` ``` ` to end the JSON block

    Claude generates JSON between the fences, guaranteed structure.

    Why it works:
    - Markdown fences are a familiar convention (Claude sees them in training data)
    - Stop sequence is unambiguous (Claude won't generate triple backticks in JSON)
    - Clear visual boundaries for humans reading the output

    Trade-off:
    - Slightly wasteful (2 lines of fences), but negligible
    - Most reliable for production use

    Note: This is what you'll replace with tool_choice in Phase 2 Days 2-9.
    For now, it's the gold standard before tool_choice.
    """

    print("\n" + "=" * 70)
    print("DEMO 3: Prefill + Stop Combo (PRODUCTION PATTERN)")
    print("=" * 70)

    user_prompt = """Analyze this food: "grilled chicken Caesar salad with croutons"

Respond with ONLY valid JSON inside markdown code fences:"""

    # Prefill: start the assistant message with opening markdown fence for JSON
    prefilled_response = "```json\n{"

    messages = [
        {"role": "user", "content": user_prompt},
        {"role": "assistant", "content": prefilled_response},
    ]

    print("\nMessages structure:")
    print(f"  1. User asks for JSON in markdown fences")
    print(f"  2. Assistant already has: '{repr(prefilled_response)}'")
    print(f"  3. Stop sequence: ['```'] — Claude stops at closing fence")
    print(f"\nClaude generates JSON between the fences...")

    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=messages,
        stop_sequences=["```"],  # Stop at closing backticks
    )

    # Reconstruct: prefill + continuation + closing fence
    full_response = prefilled_response + response.content[0].text + "```"

    print(f"\nClaude's continuation:\n{response.content[0].text}")
    print(f"\nFull output:\n{full_response}")

    # Extract JSON from between the fences
    json_start = full_response.find("{")
    json_end = full_response.rfind("}") + 1

    if json_start >= 0 and json_end > json_start:
        json_str = full_response[json_start:json_end]
        print(f"\nExtracted JSON:\n{json_str}")

        try:
            parsed = json.loads(json_str)
            print(f"✅ Valid JSON! Parsed: {json.dumps(parsed, indent=2)}")
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
    else:
        print(f"❌ Could not find JSON in output")


async def main():
    """Run all three demos."""
    print("🎯 Phase 2 Day 1: Output Control Trio")
    print("Learning three techniques to force Claude into predictable formats\n")

    await demo_1_prefill_assistant()
    await demo_2_stop_sequences()
    await demo_3_prefill_stop_combo()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
Three techniques, ranked by production readiness:

1. ⭐⭐⭐ Prefill + Stop Combo
   - Most reliable, clear boundaries
   - Current NomNom pattern (being replaced by tool_choice in Phase 2)
   - Recommended for any text-based structured output

2. ⭐⭐ Prefill Assistant
   - Works, but wastes tokens on prefilled content
   - Useful when you want to guide a specific partial response

3. ⭐ Stop Sequences Alone
   - Simple, but fragile (Claude might not complete structure by stop point)
   - Useful only when structure is simple (e.g., one-line responses)

PHASE 2 DIRECTION:
Days 2-9 will show you tool_choice, which replaces all three:
- Guaranteed structure (schema validation)
- No token waste on format guidance
- Production-grade reliability

But understand these three first — they're building blocks for understanding
why tool_choice is better.
""")


if __name__ == "__main__":
    asyncio.run(main())
