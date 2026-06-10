"""
Phase 5 Day 4: Single Agent Implementation

The agent loop: Claude decides what tools to call based on intermediate results.

Use case: "I have eggs, onions, potatoes, and rice. What can I make?"

Run: python3 04_agent_sandbox.py
"""

import json
import sys
from typing import Any

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic library not installed")
    print("Install with: pip install anthropic")
    sys.exit(1)


# Mock tool implementations
def search_recipes(ingredients: list[str]) -> list[dict]:
    """Search for recipes matching ingredients"""
    print(f"\n  [Tool: search_recipes] Input: {ingredients}")

    # Mock recipe database
    recipes_db = {
        ("eggs", "onions", "potatoes", "rice"): [
            {
                "name": "Fried Rice with Eggs",
                "ingredients_used": ["eggs", "rice", "onions"],
                "ingredients_needed": ["oil", "soy sauce"],
                "difficulty": "easy"
            },
            {
                "name": "Potato Omelette with Rice",
                "ingredients_used": ["eggs", "potatoes", "onions"],
                "ingredients_needed": ["butter", "cheese"],
                "difficulty": "medium"
            },
            {
                "name": "Vegetable Stir-Fry with Rice",
                "ingredients_used": ["rice", "potatoes", "onions"],
                "ingredients_needed": ["oil", "garlic"],
                "difficulty": "easy"
            }
        ]
    }

    key = tuple(sorted(ingredients))
    results = recipes_db.get(key, [])

    output = f"Found {len(results)} recipes: " + ", ".join([r["name"] for r in results])
    print(f"  [Tool Result] {output}")
    return results


def check_nutrition(dish_name: str) -> dict:
    """Check nutrition info for a dish"""
    print(f"\n  [Tool: check_nutrition] Input: {dish_name}")

    nutrition_db = {
        "Fried Rice with Eggs": {
            "calories": 450,
            "protein_g": 18,
            "carbs_g": 52,
            "fat_g": 15,
            "fiber_g": 2
        },
        "Potato Omelette with Rice": {
            "calories": 520,
            "protein_g": 20,
            "carbs_g": 45,
            "fat_g": 22,
            "fiber_g": 3
        },
        "Vegetable Stir-Fry with Rice": {
            "calories": 380,
            "protein_g": 12,
            "carbs_g": 58,
            "fat_g": 8,
            "fiber_g": 5
        }
    }

    result = nutrition_db.get(dish_name, {"error": "Dish not found"})
    print(f"  [Tool Result] {dish_name}: {result.get('calories', 'N/A')} cal")
    return result


def estimate_cooking_time(dish_name: str) -> dict:
    """Estimate cooking time for a dish"""
    print(f"\n  [Tool: estimate_cooking_time] Input: {dish_name}")

    time_db = {
        "Fried Rice with Eggs": {
            "prep_minutes": 5,
            "cook_minutes": 15,
            "total_minutes": 20
        },
        "Potato Omelette with Rice": {
            "prep_minutes": 10,
            "cook_minutes": 20,
            "total_minutes": 30
        },
        "Vegetable Stir-Fry with Rice": {
            "prep_minutes": 10,
            "cook_minutes": 15,
            "total_minutes": 25
        }
    }

    result = time_db.get(dish_name, {"error": "Dish not found"})
    print(f"  [Tool Result] {dish_name}: {result.get('total_minutes', 'N/A')} minutes total")
    return result


def check_pantry(user_id: int) -> dict:
    """Check what's in the user's pantry"""
    print(f"\n  [Tool: check_pantry] Input: user_id={user_id}")

    # Mock pantry data
    pantry = {
        "eggs": 2,
        "onions": 1,
        "potatoes": 3,
        "rice": 1,
        "oil": True,
        "soy_sauce": True,
        "salt": True,
        "pepper": True
    }

    print(f"  [Tool Result] Pantry contents: {json.dumps(pantry, indent=2)}")
    return pantry


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool and return the result as a string"""
    print(f"\n{'='*70}")
    print(f"Tool Call: {tool_name}")
    print(f"{'='*70}")

    if tool_name == "search_recipes":
        result = search_recipes(tool_input.get("ingredients", []))
    elif tool_name == "check_nutrition":
        result = check_nutrition(tool_input.get("dish_name", ""))
    elif tool_name == "estimate_cooking_time":
        result = estimate_cooking_time(tool_input.get("dish_name", ""))
    elif tool_name == "check_pantry":
        result = check_pantry(tool_input.get("user_id", 1))
    else:
        result = {"error": f"Unknown tool: {tool_name}"}

    # Convert result to JSON string
    return json.dumps(result)


def run_agent(user_input: str):
    """Run the agent loop"""
    print("\n" + "#"*70)
    print("# AGENT LOOP: Fridge Leftovers Recommendation")
    print("#"*70)
    print(f"User: {user_input}\n")

    client = anthropic.Anthropic()

    # Define tools that Claude can use
    tools = [
        {
            "name": "search_recipes",
            "description": "Search for recipes that match given ingredients",
            "input_schema": {
                "type": "object",
                "properties": {
                    "ingredients": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of ingredients to search for"
                    }
                },
                "required": ["ingredients"]
            }
        },
        {
            "name": "check_nutrition",
            "description": "Get nutrition information for a specific dish",
            "input_schema": {
                "type": "object",
                "properties": {
                    "dish_name": {
                        "type": "string",
                        "description": "Name of the dish to get nutrition info for"
                    }
                },
                "required": ["dish_name"]
            }
        },
        {
            "name": "estimate_cooking_time",
            "description": "Estimate prep and cooking time for a dish",
            "input_schema": {
                "type": "object",
                "properties": {
                    "dish_name": {
                        "type": "string",
                        "description": "Name of the dish to estimate time for"
                    }
                },
                "required": ["dish_name"]
            }
        },
        {
            "name": "check_pantry",
            "description": "Check what ingredients are available in the pantry",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "User ID to check pantry for"
                    }
                },
                "required": ["user_id"]
            }
        }
    ]

    # Initialize message history
    messages = [
        {
            "role": "user",
            "content": user_input
        }
    ]

    # Agent loop
    loop_count = 0
    max_loops = 10  # Prevent infinite loops

    while loop_count < max_loops:
        loop_count += 1
        print(f"\n{'─'*70}")
        print(f"Loop #{loop_count}: Claude decides what to do")
        print(f"{'─'*70}")

        # Call Claude with tools
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        print(f"Stop reason: {response.stop_reason}")

        # Check if Claude is done
        if response.stop_reason == "end_turn":
            print("\n✓ Claude finished (end_turn)")
            # Extract and print final response
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"\nFinal Answer:\n{block.text}")
            break

        # Handle tool use
        if response.stop_reason == "tool_use":
            # Add Claude's response to messages (including tool calls)
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            # Process each tool call
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

                    # Execute the tool
                    result = execute_tool(tool_name, tool_input)

                    # Record the tool result
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            # Add all tool results in a single user message
            messages.append({
                "role": "user",
                "content": tool_results
            })

            print(f"↻ Claude will consider {len(tool_results)} tool result(s) and decide next step")
        else:
            print(f"Unexpected stop reason: {response.stop_reason}")
            break

    if loop_count >= max_loops:
        print(f"\n⚠ Reached max loops ({max_loops})")


if __name__ == "__main__":
    user_input = "I have eggs, onions, potatoes, and rice in my fridge. What can I make for dinner tonight?"
    run_agent(user_input)
