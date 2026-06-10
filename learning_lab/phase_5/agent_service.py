"""
Phase 5 Day 9: AgentService for NomNom

Implements the agent loop for open-ended cooking advice.
Agent autonomously decides what tools to call based on intermediate results.

This is FLEXIBLE, AUTONOMOUS, and ADAPTIVE.
Perfect for: "I have eggs, onions, potatoes. What can I make?"

The agent might:
  - Search recipes first OR check pantry first
  - Decide to check nutrition OR skip it
  - Adapt based on what it learns

Run: python3 agent_service.py
"""

import json
import sys
import time
from typing import Optional

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic library not installed")
    print("Install with: pip install anthropic")
    sys.exit(1)


def mock_search_recipes(ingredients: list[str]) -> str:
    """Mock recipe search"""
    print(f"    [search_recipes] {ingredients}")
    recipes_db = {
        "eggs_onions_potatoes": [
            {"name": "Spanish Tortilla", "time": 20, "difficulty": "easy"},
            {"name": "Shakshuka", "time": 25, "difficulty": "medium"},
            {"name": "Potato Frittata", "time": 30, "difficulty": "medium"},
        ]
    }
    key = "_".join([i.lower().replace(" ", "_") for i in ingredients[:3]])
    if key in recipes_db:
        result = json.dumps(recipes_db[key])
    else:
        result = json.dumps({"recipes": [], "message": "No recipes found"})
    print(f"    [result] Found {len(json.loads(result))} recipes")
    return result


def mock_check_nutrition(recipe_name: str) -> str:
    """Mock nutrition check"""
    print(f"    [check_nutrition] {recipe_name}")
    nutrition_db = {
        "Spanish Tortilla": {"calories": 350, "protein_g": 15, "carbs_g": 25},
        "Shakshuka": {"calories": 280, "protein_g": 12, "carbs_g": 15},
        "Potato Frittata": {"calories": 320, "protein_g": 14, "carbs_g": 28},
    }
    result = nutrition_db.get(recipe_name, {"error": "Recipe not found"})
    print(f"    [result] {result.get('calories', 'N/A')} calories")
    return json.dumps(result)


def mock_check_pantry(user_id: int) -> str:
    """Mock pantry check"""
    print(f"    [check_pantry] user_id={user_id}")
    pantry = {
        "eggs": 3,
        "onions": 2,
        "potatoes": 4,
        "butter": True,
        "salt": True,
        "pepper": True
    }
    print(f"    [result] {len(pantry)} items available")
    return json.dumps(pantry)


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a mock tool"""
    if tool_name == "search_recipes":
        return mock_search_recipes(tool_input.get("ingredients", []))
    elif tool_name == "check_nutrition":
        return mock_check_nutrition(tool_input.get("recipe_name", ""))
    elif tool_name == "check_pantry":
        return mock_check_pantry(tool_input.get("user_id", 1))
    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})


class AgentService:
    """
    Open-ended cooking advice agent.

    Agent loop:
      1. Claude reads user input
      2. Claude decides which tool to call (if any)
      3. Tool executes, Claude sees result
      4. Claude decides: do I need more info? or am I done?
      5. Repeat until Claude says "I have enough info, here's my answer"
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.total_tokens = 0
        self.total_cost = 0.0

    def cook_with_ingredients(
        self,
        ingredients: list[str],
        constraints: dict,
        user_id: int
    ) -> dict:
        """
        Open-ended cooking advice.

        Args:
            ingredients: List of available ingredients
            constraints: {"allergies": [...], "diet": "...", "time_minutes": 30}
            user_id: For personalization

        Returns:
            {
                "recommendation": "...",
                "recipe": "...",
                "nutrition": {...},
                "total_tokens": int,
                "total_cost": float
            }
        """
        print("\n" + "="*70)
        print("AGENT: Open-Ended Cooking Advice")
        print("="*70)
        print(f"Input: {ingredients}")
        print(f"Constraints: {constraints}")

        # Define tools the agent can use
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
                "description": "Get nutrition information for a recipe",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "recipe_name": {
                            "type": "string",
                            "description": "Name of recipe to check"
                        }
                    },
                    "required": ["recipe_name"]
                }
            },
            {
                "name": "check_pantry",
                "description": "Check what's available in user's pantry",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "integer",
                            "description": "User ID"
                        }
                    },
                    "required": ["user_id"]
                }
            }
        ]

        # Initialize messages
        messages = [
            {
                "role": "user",
                "content": f"""I have these ingredients: {', '.join(ingredients)}.
Constraints: {json.dumps(constraints)}

What should I cook? Please search for recipes, check nutrition if needed,
and give me a recommendation."""
            }
        ]

        # Agent loop
        loop_count = 0
        max_loops = 10
        start_time = time.time()

        while loop_count < max_loops:
            loop_count += 1
            print(f"\n{'─'*70}")
            print(f"Loop #{loop_count}: Agent decides what to do")
            print(f"{'─'*70}")

            response = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                tools=tools,
                messages=messages
            )

            print(f"Stop reason: {response.stop_reason}")

            # Track tokens
            if hasattr(response, 'usage'):
                self.total_tokens += response.usage.input_tokens + response.usage.output_tokens
                # Rough cost estimate (Haiku: $0.80/$4 per 1M tokens)
                self.total_cost += (response.usage.input_tokens * 0.80 +
                                   response.usage.output_tokens * 4) / 1_000_000

            # Agent is done
            if response.stop_reason == "end_turn":
                print("\n✓ Agent finished (end_turn)")
                for block in response.content:
                    if hasattr(block, "text"):
                        final_answer = block.text
                        print(f"\nRecommendation:\n{final_answer}")
                        break

                elapsed = time.time() - start_time
                return {
                    "recommendation": final_answer,
                    "recipe": "See recommendation above",
                    "nutrition": {},
                    "total_tokens": self.total_tokens,
                    "total_cost": self.total_cost,
                    "latency_seconds": elapsed,
                    "loops": loop_count
                }

            # Agent wants to call a tool
            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})

                # Execute tools
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"\n{'='*70}")
                        print(f"Tool Call: {block.name}")
                        print(f"{'='*70}")

                        result = execute_tool(block.name, block.input)

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })

                messages.append({"role": "user", "content": tool_results})
                print(f"↻ Agent will consider {len(tool_results)} tool result(s)")

            else:
                print(f"Unexpected stop reason: {response.stop_reason}")
                break

        return {
            "recommendation": "Agent did not complete",
            "recipe": "Max loops reached",
            "nutrition": {},
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "latency_seconds": time.time() - start_time,
            "loops": loop_count
        }


def main():
    """Test AgentService"""
    service = AgentService()

    result = service.cook_with_ingredients(
        ingredients=["eggs", "onions", "potatoes"],
        constraints={"diet": "vegetarian", "time_minutes": 30},
        user_id=1
    )

    print("\n" + "#"*70)
    print("# METRICS")
    print("#"*70)
    print(f"Loops: {result['loops']}")
    print(f"Latency: {result['latency_seconds']:.2f}s")
    print(f"Tokens: {result['total_tokens']}")
    print(f"Cost: ${result['total_cost']:.4f}")


if __name__ == "__main__":
    main()
