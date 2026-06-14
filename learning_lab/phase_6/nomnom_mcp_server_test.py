"""
Simplified NomNom MCP Server (Test Version)

Uses mock implementations instead of importing backend code.
This verifies the MCP protocol works before we integrate the real backend.

Usage:
    python nomnom_mcp_server_test.py
"""

import json
from mcp.server import FastMCP

# Create server instance
app = FastMCP("NomNom")


@app.tool()
def recommend_meal(calories: int, diet_type: str) -> dict:
    """
    Recommend a meal matching calorie and diet constraints.

    This is a test version using mock data.
    Production version calls the real workflow.
    """
    mock_recommendations = {
        "vegetarian": {
            600: {"meal": "Lentil Buddha Bowl", "protein": 18, "carbs": 65, "fat": 12}
        },
        "vegan": {
            600: {"meal": "Tofu Pad Thai", "protein": 20, "carbs": 68, "fat": 14}
        },
        "omnivore": {
            600: {"meal": "Salmon with Sweet Potato", "protein": 40, "carbs": 35, "fat": 18}
        }
    }

    diet_meals = mock_recommendations.get(diet_type, mock_recommendations["omnivore"])
    meal_data = diet_meals.get(calories, list(diet_meals.values())[0])

    return {
        "meal_name": meal_data["meal"],
        "calories": calories,
        "diet_type": diet_type,
        "protein_g": meal_data["protein"],
        "carbs_g": meal_data["carbs"],
        "fat_g": meal_data["fat"],
        "prep_time_minutes": 15,
        "source": "Mock (test version)"
    }


@app.tool()
def analyze_food_image(image_path: str) -> dict:
    """
    Analyze a food image and extract nutritional information.

    This is a test version using mock data.
    Production version uses Claude vision API.
    """
    return {
        "food_name": "Pasta Carbonara (estimated from image)",
        "estimated_calories": 450,
        "protein_g": 18,
        "carbs_g": 55,
        "fat_g": 18,
        "source": "Mock (test version)"
    }


@app.tool()
def lookup_nutrition(query: str) -> dict:
    """
    Query the nutrition knowledge base for food information.

    This is a test version using mock data.
    Production version queries the RAG knowledge base.
    """
    mock_results = [
        {"food": "Grilled Chicken Breast", "calories": 165, "protein": 31, "citation": "[1]"},
        {"food": "Lentil Bowl", "calories": 250, "protein": 18, "citation": "[2]"},
        {"food": "Greek Yogurt", "calories": 100, "protein": 18, "citation": "[3]"}
    ]

    return {
        "query": query,
        "results": mock_results,
        "count": len(mock_results),
        "citations": "Results from nutrition knowledge base [1] USDA [2] Nutrition DB [3] NomNom KB",
        "source": "Mock (test version)"
    }


if __name__ == "__main__":
    import sys
    print("NomNom MCP Server (Test Version) starting...", file=sys.stderr)
    print("Available tools: recommend_meal, analyze_food_image, lookup_nutrition", file=sys.stderr)
    print("Note: Using mock data (not real backend)", file=sys.stderr)
    app.run()
