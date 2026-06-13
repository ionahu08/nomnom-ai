"""
Phase 6 Day 3: NomNom MCP Server (Real Workflow)

MCP server with real meal recommendation workflow integration.

Usage:
    python nomnom_mcp_server.py

The server runs on stdio transport, waiting for MCP messages from a client.
To test, see test_nomnom_server.py or connect with Claude Code MCP client.

Day 3 Update:
- Replaced hardcoded recommendations with real MealRecommendationWorkflow
- Added error handling for production use
- Imports NomNom backend code via sys.path manipulation
"""

import json
import sys
from pathlib import Path
from mcp.server import Server

# Add NomNom-Backend to path so we can import src
nomnom_root = Path(__file__).parent.parent.parent
backend_path = nomnom_root / "NomNom-Backend"
sys.path.insert(0, str(backend_path))

# Import real NomNom code
from src.llm.workflow.meal_recommendation_workflow import MealRecommendationWorkflow
from src.llm.client import LLMClient
from src.config import settings


# Create server instance
server = Server("NomNom")


@server.tool()
def recommend_meal(calories: int, diet_type: str) -> dict:
    """
    Recommend a meal matching calorie and diet constraints.

    Calls the real NomNom meal recommendation workflow (5-step chaining with Claude).

    Args:
        calories: Target calorie count (e.g., 600)
        diet_type: Dietary preference (vegetarian, vegan, keto, omnivore)

    Returns:
        Dictionary with meal recommendation, nutrition info, and reasoning
    """
    try:
        # Initialize LLM client and workflow
        llm_client = LLMClient(api_key=settings.anthropic_api_key)
        workflow = MealRecommendationWorkflow(llm_client)

        # Execute the real 5-step workflow
        result = workflow.execute(
            calories=calories,
            diet_type=diet_type
        )

        # Convert result object to JSON-serializable dict
        return {
            "meal_name": result.get("meal_name", "Unknown"),
            "calories": result.get("calories", calories),
            "diet_type": diet_type,
            "protein_g": result.get("protein_g", 0),
            "carbs_g": result.get("carbs_g", 0),
            "fat_g": result.get("fat_g", 0),
            "prep_time_minutes": result.get("prep_time_minutes", 0),
            "reasoning": result.get("reasoning", ""),
            "source": "NomNom MealRecommendationWorkflow (real)"
        }

    except Exception as e:
        # Return structured error response
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "meal_name": None,
            "source": "Error in MealRecommendationWorkflow"
        }


if __name__ == "__main__":
    # stdio transport: reads MCP messages from stdin, writes responses to stdout
    print("NomNom MCP Server starting on stdio transport...", file=__import__('sys').stderr)
    server.run(transport="stdio")
