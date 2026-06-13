"""
Phase 6 Day 2: NomNom MCP Server (Skeleton)

Minimal working MCP server with one hardcoded tool.

Usage:
    python nomnom_mcp_server.py

The server runs on stdio transport, waiting for MCP messages from a client.
To test, see 02_mcp_server_skeleton.md for test script.
"""

import json
from mcp.server import Server


# Create server instance
server = Server("NomNom")


@server.tool()
def recommend_meal(calories: int, diet_type: str) -> dict:
    """
    Recommend a meal matching calorie and diet constraints.

    Args:
        calories: Target calorie count (e.g., 600)
        diet_type: Dietary preference (vegetarian, vegan, keto, omnivore)

    Returns:
        Dictionary with meal recommendation and nutrition info
    """
    # Hardcoded responses for Day 2 testing
    recommendations = {
        "vegetarian": {
            400: "Vegetable Stir-Fry with Rice",
            600: "Lentil Buddha Bowl",
            800: "Pasta Primavera with Vegetables"
        },
        "vegan": {
            400: "Chickpea Salad",
            600: "Tofu Pad Thai",
            800: "Black Bean Burrito Bowl"
        },
        "omnivore": {
            400: "Grilled Chicken Breast with Greens",
            600: "Salmon with Sweet Potato",
            800: "Turkey Meatballs with Pasta"
        },
        "keto": {
            400: "Bacon and Eggs",
            600: "Steak with Butter",
            800: "Pork Chops with Avocado"
        }
    }

    # Find closest match
    diet_meals = recommendations.get(diet_type, recommendations["omnivore"])

    # Find meal closest to target calories
    meal_name = diet_meals.get(calories)
    if not meal_name:
        # Fallback to closest calorie level
        available_cals = sorted(diet_meals.keys())
        closest_cal = min(available_cals, key=lambda x: abs(x - calories))
        meal_name = diet_meals[closest_cal]

    return {
        "meal_name": meal_name,
        "calories": calories,
        "diet_type": diet_type,
        "protein_g": 20,
        "carbs_g": 45,
        "fat_g": 15,
        "prep_time_minutes": 15,
        "source": "Hardcoded for Day 2 testing"
    }


if __name__ == "__main__":
    # stdio transport: reads MCP messages from stdin, writes responses to stdout
    print("NomNom MCP Server starting on stdio transport...", file=__import__('sys').stderr)
    server.run(transport="stdio")
