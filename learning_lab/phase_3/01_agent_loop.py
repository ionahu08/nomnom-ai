#!/usr/bin/env python3
"""
Phase 3 Day 1: Multi-Tool Agent Loop (Hand-Coded)

Key insight: Don't use frameworks. Hand-write the agent loop from scratch.
This teaches you the fundamental pattern that all LLM agents follow.

The pattern:
1. Send message + tools to Claude
2. Claude responds with tool_use blocks
3. Execute tools, get results
4. Feed results back as tool_result messages
5. Loop until Claude outputs text (stop_reason != "tool_use")

This is the most important exercise in Phase 3. After this, everything else
(RAG, semantic search, multi-agent orchestration) becomes obvious.

Usage:
    python 01_agent_loop.py

You should see Claude:
1. Call tool A
2. Get result
3. Call tool B (using result from A)
4. Get result
5. Generate final text answer
"""

import os
import json
import asyncio
from anthropic import AsyncAnthropic

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set")

client = AsyncAnthropic(api_key=api_key)


# ============================================================================
# DEFINE THREE TOOLS (food analysis domain)
# ============================================================================

TOOLS = [
    {
        "name": "extract_nutrition_from_image",
        "description": "Extract nutritional data from a food photo",
        "input_schema": {
            "type": "object",
            "properties": {
                "food_name": {
                    "type": "string",
                    "description": "What food is in the image",
                },
                "estimated_calories": {
                    "type": "integer",
                    "description": "Estimated calories",
                },
            },
            "required": ["food_name", "estimated_calories"],
        },
    },
    {
        "name": "lookup_food_database",
        "description": "Look up accurate nutrition info for a food from database",
        "input_schema": {
            "type": "object",
            "properties": {
                "food_name": {
                    "type": "string",
                    "description": "Food to look up (e.g., 'grilled chicken Caesar salad')",
                },
            },
            "required": ["food_name"],
        },
    },
    {
        "name": "calculate_daily_total",
        "description": "Calculate total calories for the day from food log",
        "input_schema": {
            "type": "object",
            "properties": {
                "foods_eaten": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of foods eaten today",
                },
            },
            "required": ["foods_eaten"],
        },
    },
]


# ============================================================================
# IMPLEMENT TOOL FUNCTIONS (mocked for learning)
# ============================================================================

def extract_nutrition_from_image(food_name: str, estimated_calories: int) -> dict:
    """Mock: extract nutrition from food photo."""
    print(f"[Tool] extract_nutrition_from_image: {food_name}, {estimated_calories} cal")
    return {
        "food_name": food_name,
        "calories": estimated_calories,
        "protein_g": estimated_calories // 20,  # Rough estimate
        "carbs_g": estimated_calories // 15,
        "fat_g": estimated_calories // 30,
    }


def lookup_food_database(food_name: str) -> dict:
    """Mock: look up accurate nutrition from database."""
    print(f"[Tool] lookup_food_database: {food_name}")
    # Pretend we queried a nutrition database
    database = {
        "grilled chicken Caesar salad": {
            "calories": 320,
            "protein_g": 35,
            "carbs_g": 15,
            "fat_g": 12,
            "source": "USDA FoodData Central",
        },
        "pizza slice": {
            "calories": 285,
            "protein_g": 12,
            "carbs_g": 36,
            "fat_g": 10,
            "source": "USDA FoodData Central",
        },
    }
    return database.get(food_name.lower(), {"error": f"Food '{food_name}' not found in database"})


def calculate_daily_total(foods_eaten: list) -> dict:
    """Mock: calculate total calories for the day."""
    print(f"[Tool] calculate_daily_total: {foods_eaten}")
    # Pretend we looked up each food and summed calories
    total_calories = 0
    for food in foods_eaten:
        if "salad" in food.lower():
            total_calories += 320
        elif "pizza" in food.lower():
            total_calories += 285
        else:
            total_calories += 200  # default

    return {
        "foods": foods_eaten,
        "total_calories": total_calories,
        "recommendation": "You're within healthy range" if total_calories < 2500 else "Consider lighter meals",
    }


def run_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool and return the result as JSON string."""
    if tool_name == "extract_nutrition_from_image":
        result = extract_nutrition_from_image(
            tool_input["food_name"],
            tool_input["estimated_calories"],
        )
    elif tool_name == "lookup_food_database":
        result = lookup_food_database(tool_input["food_name"])
    elif tool_name == "calculate_daily_total":
        result = calculate_daily_total(tool_input["foods_eaten"])
    else:
        result = {"error": f"Unknown tool: {tool_name}"}

    return json.dumps(result)


# ============================================================================
# AGENT LOOP (the core pattern)
# ============================================================================

async def agent_loop(user_message: str, max_iterations: int = 10) -> str:
    """
    Run an agent loop that can call multiple tools in sequence.

    This is the fundamental pattern:
    1. Call Claude with tools
    2. If Claude returns tool_use, execute tools
    3. Feed tool results back to Claude
    4. Repeat until Claude returns text (stop_reason != "tool_use")

    Args:
        user_message: The user's question
        max_iterations: Prevent infinite loops

    Returns:
        Claude's final text response
    """

    # Step 1: Initialize conversation with user message
    messages = [
        {"role": "user", "content": user_message}
    ]

    print(f"\n{'='*70}")
    print(f"USER: {user_message}")
    print(f"{'='*70}\n")

    iteration = 0
    while iteration < max_iterations:
        iteration += 1
        print(f"[Iteration {iteration}]")

        # Step 2: Call Claude with tools
        response = await client.messages.create(
            model="claude-opus-4-1-20250805",
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

        # Step 3: Check stop reason
        print(f"  stop_reason: {response.stop_reason}")

        if response.stop_reason == "end_turn":
            # Claude generated text, we're done
            final_text = response.content[0].text
            print(f"\n{'='*70}")
            print(f"ASSISTANT: {final_text}")
            print(f"{'='*70}\n")
            return final_text

        elif response.stop_reason == "tool_use":
            # Claude called tools, we need to execute them

            # Step 4: Extract tool_use blocks from response
            assistant_message = {"role": "assistant", "content": response.content}
            messages.append(assistant_message)

            # Step 5: Execute each tool
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id

                    print(f"  Tool call: {tool_name}({json.dumps(tool_input)})")

                    # Execute the tool
                    result = run_tool(tool_name, tool_input)

                    print(f"  Result: {result[:100]}...")

                    # Package result for Claude
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": result,
                    })

            # Step 6: Feed tool results back to Claude
            messages.append({"role": "user", "content": tool_results})
            print()

        else:
            # Unexpected stop reason
            print(f"  Unexpected stop_reason: {response.stop_reason}")
            return "Error: unexpected stop reason"

    return "Error: max iterations reached"


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Run the agent loop demo."""
    print("🤖 Phase 3 Day 1: Multi-Tool Agent Loop (Hand-Coded)\n")
    print("This demonstrates the fundamental pattern for all LLM agents:")
    print("1. Send message + tools to Claude")
    print("2. If Claude calls tools, execute them")
    print("3. Feed results back to Claude")
    print("4. Repeat until Claude outputs text\n")

    # Example 1: Extract nutrition from food photo + look up database
    await agent_loop(
        "I just ate a grilled chicken Caesar salad. "
        "First, estimate the nutrition from the photo, "
        "then look up the accurate nutrition from a database."
    )

    # Example 2: Calculate daily total
    await agent_loop(
        "I've eaten pizza and salad today. "
        "Calculate my total calories and tell me if I'm within healthy range."
    )


if __name__ == "__main__":
    asyncio.run(main())
