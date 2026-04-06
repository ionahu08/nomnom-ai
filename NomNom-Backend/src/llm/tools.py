"""
Tool Definitions — Anthropic tool_use schemas.

In Plain English:
Instead of asking Claude "please return JSON", we force it by using tool_use.
Tool definitions are JSON schemas that tell Claude: "You MUST return data in THIS shape,
and you MUST use a tool to do it. No plain text allowed."

Result: Claude is guaranteed to return valid JSON matching our schema.
"""

from typing import Any

# Anthropic tool_use schema for food analysis
# This tells Claude: "You must call the analyze_food_tool with these exact fields"
ANALYZE_FOOD_TOOL = {
    "name": "analyze_food",
    "description": "Analyze a food photo and return nutritional information and a funny roast",
    "input_schema": {
        "type": "object",
        "properties": {
            "food_name": {
                "type": "string",
                "description": "The name of the food (e.g., 'Chicken Caesar Salad')",
            },
            "calories": {
                "type": "integer",
                "description": "Estimated calories (0-5000)",
            },
            "protein_g": {
                "type": "number",
                "description": "Estimated protein in grams (0-500)",
            },
            "carbs_g": {
                "type": "number",
                "description": "Estimated carbs in grams (0-500)",
            },
            "fat_g": {
                "type": "number",
                "description": "Estimated fat in grams (0-500)",
            },
            "food_category": {
                "type": "string",
                "description": "Category like 'salad', 'fast food', 'dessert', 'home-cooked', 'sandwich', 'soup'",
            },
            "cuisine_origin": {
                "type": "string",
                "description": "Cuisine origin like 'Japanese', 'Italian', 'American', 'Mexican', 'Indian'",
            },
            "cat_roast": {
                "type": "string",
                "description": "A short, funny roast about the food (1-2 sentences)",
            },
        },
        "required": [
            "food_name",
            "calories",
            "protein_g",
            "carbs_g",
            "fat_g",
            "food_category",
            "cuisine_origin",
            "cat_roast",
        ],
    },
}


def get_tools_for_task(task_type: str) -> list[dict[str, Any]]:
    """
    Get tool definitions for a task type.

    Args:
        task_type: Task type (e.g., "analyze_food")

    Returns:
        List of tool definitions for Anthropic API
    """
    if task_type == "analyze_food":
        return [ANALYZE_FOOD_TOOL]
    elif task_type == "recommend_meal":
        # Recommendations don't use tool_use, just text generation
        return []
    elif task_type == "weekly_recap":
        # Recaps don't use tool_use, just text generation
        return []
    else:
        return []
