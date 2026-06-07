#!/usr/bin/env python3
"""
Phase 2 Day 3: Test Dataset Generation

Two approaches:
1. Hand-written test cases (what you did in Day 2 — 5 cases)
2. Claude-generated test cases (what you'll do today — 30 "hard-to-recognize" cases)

The insight: Use Claude to bulk-generate challenging edge cases.
This teaches you how to build realistic eval datasets that expose weaknesses.

You'll generate 30 food descriptions that are ambiguous, blurry, or hard to identify.
These become your Phase 2 test dataset.

Usage:
    python 03_dataset_generation.py

Output:
    Creates learning_lab/phase_2/generated_dataset.json with 30 test cases.
"""

import os
import json
import asyncio
from anthropic import AsyncAnthropic

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set")

client = AsyncAnthropic(api_key=api_key)


async def generate_test_cases(num_cases: int = 30) -> list:
    """
    Use Claude (Haiku) to generate challenging food descriptions.

    Strategy:
    1. Tell Claude to generate "hard-to-recognize food" descriptions
    2. Use prefill+stop (Day 1 technique) to force structured JSON output
    3. Parse and return the generated dataset

    Returns: list of dicts with "description" field
    """

    print(f"\n🤖 Using Claude to generate {num_cases} challenging food descriptions...")
    print("(This teaches you how to build eval datasets at scale)\n")

    # The generation prompt tells Claude what kind of test cases we need
    generation_prompt = f"""Generate {num_cases} challenging food descriptions for an AI nutrition analyzer.

These should be HARD TO RECOGNIZE - test edge cases and ambiguous situations:
- Blurry or unclear descriptions ("something brown and round on a plate")
- Ambiguous items ("white fluffy stuff in a bowl")
- Mixed dishes ("rice with vegetables, some are recognizable some aren't")
- Unusual presentations ("food cut into tiny pieces, can't identify what it was")
- Crowded plates ("several different foods on one plate, hard to separate")
- Foreign/unfamiliar foods ("translucent noodles in a clear broth, unknown origin")
- Overexposed/underexposed ("very dark photo of something, can't see clearly")
- Partially eaten items ("half-eaten sandwich, mostly bread visible")
- Unappetizing descriptions ("something beige that was cooked too long")
- Minimal context ("mushy brown stuff, could be multiple things")

Return as JSON array of objects with "description" field (string, 10-30 words each).

Example format:
[
  {{"description": "A blurry photo of a brown round shape, possibly a burger or meatball"}},
  {{"description": "Translucent Vietnamese spring rolls with rice paper, unclear filling"}},
  ...
]

Generate exactly {num_cases} cases. Make them diverse and challenging."""

    # Use prefill+stop (Day 1) to force JSON array output
    prefilled = "["
    messages = [
        {"role": "user", "content": generation_prompt},
        {"role": "assistant", "content": prefilled},
    ]

    print(f"Prompting Claude (Haiku) with prefill+stop technique...\n")

    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=messages,
        stop_sequences=["]"],  # Stop at closing bracket
    )

    # Reconstruct full JSON
    full_json = prefilled + response.content[0].text + "]"

    print(f"Parsing generated JSON...")
    try:
        test_cases = json.loads(full_json)
        print(f"✅ Successfully generated {len(test_cases)} test cases\n")
        return test_cases
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse generated JSON: {e}")
        print(f"Raw output:\n{full_json[:500]}")
        return []


async def save_dataset(test_cases: list, filename: str = "generated_dataset.json"):
    """Save generated test cases to file."""
    filepath = f"learning_lab/phase_2/{filename}"

    # Add metadata
    dataset = {
        "version": "phase_2_day3_generated",
        "count": len(test_cases),
        "source": "Claude-generated (Haiku) hard-to-recognize food descriptions",
        "test_cases": test_cases,
    }

    with open(filepath, "w") as f:
        json.dump(dataset, f, indent=2)

    print(f"💾 Saved to: {filepath}")
    return filepath


async def preview_dataset(test_cases: list):
    """Show a preview of the generated dataset."""
    print(f"\n{'=' * 70}")
    print(f"PREVIEW: First 10 Generated Test Cases")
    print(f"{'=' * 70}\n")

    for i, case in enumerate(test_cases[:10], 1):
        desc = case.get("description", "")
        # Truncate long descriptions
        if len(desc) > 80:
            desc = desc[:77] + "..."
        print(f"{i:2d}. {desc}")

    if len(test_cases) > 10:
        print(f"\n... and {len(test_cases) - 10} more cases in the full dataset")


async def main():
    """Generate dataset and save it."""
    print("🎯 Phase 2 Day 3: Test Dataset Generation")
    print("Learn how to build eval datasets by bulk-generating edge cases\n")

    # Generate 30 test cases
    test_cases = await generate_test_cases(num_cases=30)

    if not test_cases:
        print("❌ Failed to generate dataset")
        return

    # Save to file
    filepath = await save_dataset(test_cases)

    # Preview
    await preview_dataset(test_cases)

    print(f"\n{'=' * 70}")
    print("KEY INSIGHTS")
    print(f"{'=' * 70}")
    print("""
What you just did:

1. **Defined what "hard" means** — ambiguity, blur, mixed foods, unfamiliar items
2. **Asked Claude to generate examples** — bulk creation, not hand-written
3. **Used prefill+stop (Day 1)** — forced structured JSON output at scale
4. **Built a realistic test dataset** — 30 edge cases, not 5 easy cases

Why this matters:

Eval datasets are artifacts. They need:
- Diversity (easy + hard + edge cases)
- Realism (represent actual problems you'll see)
- Scale (30 cases > 5 cases)

Using Claude to generate them is efficient: write a clear spec, Claude fills in examples.

NEXT (Day 4-5):
- Expand: manually add ground truth annotations (expected calories, food name)
- Use in eval: run this 30-case dataset through your v1/v2 prompts
- Measure: see how your prompts perform on harder cases
- Iterate: use failures to drive prompt improvements

The loop is now:
  Generate edge cases → Eval prompts → Identify failures → Improve → Re-eval
""")


if __name__ == "__main__":
    asyncio.run(main())
