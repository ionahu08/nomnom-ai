"""
Local Verification Script for MealRecommendationWorkflow

Run this to test the workflow without modifying the API:
  python -m NomNom-Backend.src.llm.workflow.test_workflow_local

This creates mock data, runs the workflow, and prints results.
No API integration needed - pure workflow testing.
"""

import asyncio
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Mock classes (simulate database objects)
@dataclass
class MockUserProfile:
    """Mock user profile"""
    dietary_restrictions: list[str] = None
    allergies: list[str] = None
    cuisine_preferences: list[str] = None

    def __post_init__(self):
        if self.dietary_restrictions is None:
            self.dietary_restrictions = []
        if self.allergies is None:
            self.allergies = []
        if self.cuisine_preferences is None:
            self.cuisine_preferences = ["Italian", "Asian"]


@dataclass
class MockFoodLog:
    """Mock food log entry"""
    food_name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float


@dataclass
class MockTargets:
    """Mock nutrition targets"""
    calorie_target: int = 2000
    protein_target: int = 150
    carb_target: int = 250
    fat_target: int = 65


# Mock LLMClient (for local testing)
class MockLLMClient:
    """Mock LLM client for testing without real API calls"""

    async def create_message_with_retry(self, model, messages, system, max_tokens, **kwargs):
        """Return mock response"""
        print(f"\n  [Mock Claude] Model: {model}")
        print(f"  [Mock Claude] System: {system[:100]}...")

        # Return appropriate mock response based on system prompt
        if "Generate" in system or "generate" in system:
            mock_response = {
                "options": [
                    {
                        "meal_name": "Grilled Chicken with Vegetables",
                        "calories": 450,
                        "protein_g": 40,
                        "carbs_g": 35,
                        "fat_g": 10,
                        "reasoning": "High protein, fits macro targets"
                    },
                    {
                        "meal_name": "Salmon Salad",
                        "calories": 480,
                        "protein_g": 35,
                        "carbs_g": 30,
                        "fat_g": 15,
                        "reasoning": "Omega-3 rich, good nutrients"
                    },
                    {
                        "meal_name": "Tofu Stir-Fry",
                        "calories": 420,
                        "protein_g": 25,
                        "carbs_g": 45,
                        "fat_g": 12,
                        "reasoning": "Vegetarian friendly, balanced"
                    }
                ]
            }
        elif "Validate" in system or "validate" in system:
            mock_response = {
                "validations": [
                    {"meal_name": "Grilled Chicken with Vegetables", "valid": True, "issues": [], "confidence": 95, "notes": "Accurate macros"},
                    {"meal_name": "Salmon Salad", "valid": True, "issues": [], "confidence": 90, "notes": "Good estimates"},
                    {"meal_name": "Tofu Stir-Fry", "valid": True, "issues": [], "confidence": 85, "notes": "Reasonable"}
                ]
            }
        elif "Rank" in system or "rank" in system:
            mock_response = {
                "rankings": [
                    {"meal_name": "Grilled Chicken with Vegetables", "rank": 1, "score": 95, "rationale": "Best macro fit"},
                    {"meal_name": "Salmon Salad", "rank": 2, "score": 88, "rationale": "Good but higher fat"},
                    {"meal_name": "Tofu Stir-Fry", "rank": 3, "score": 82, "rationale": "Good vegetarian option"}
                ]
            }
        else:
            mock_response = {}

        # Create mock response object
        class MockMessage:
            def __init__(self, text):
                self.content = [type('obj', (object,), {'text': text})]
                self.content[0].text = text

        import json
        return MockMessage(json.dumps(mock_response))


async def test_workflow():
    """Test the workflow locally"""
    print("\n" + "="*70)
    print("LOCAL VERIFICATION: MealRecommendationWorkflow")
    print("="*70)

    # Import workflow classes
    try:
        from src.llm.workflow.meal_recommendation_workflow import (
            MealRecommendationWorkflow,
            WorkflowInput,
        )
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from NomNom-Backend directory")
        return

    # Create mock data
    print("\n1️⃣  Creating test data...")
    user_profile = MockUserProfile()
    today_logs = [
        MockFoodLog("Breakfast", 300, 20, 35, 8),
        MockFoodLog("Snack", 150, 5, 20, 5),
    ]
    targets = MockTargets()

    print(f"   User profile: {user_profile.cuisine_preferences}")
    print(f"   Today's calories: {sum(log.calories for log in today_logs)}")
    print(f"   Target calories: {targets.calorie_target}")

    # Create workflow with mock client
    print("\n2️⃣  Initializing workflow...")
    mock_client = MockLLMClient()
    mock_db = None  # Not used in this test

    workflow = MealRecommendationWorkflow(mock_client, mock_db)
    print("   ✅ Workflow initialized")

    # Build workflow input
    print("\n3️⃣  Building workflow input...")
    workflow_input = WorkflowInput(
        user_profile=user_profile,
        today_logs=today_logs,
        target_calories=targets.calorie_target,
        target_protein=targets.protein_target,
        target_carbs=targets.carb_target,
        target_fat=targets.fat_target,
    )
    print("   ✅ Workflow input ready")

    # Execute workflow
    print("\n4️⃣  Executing 5-step workflow...\n")
    try:
        result = await workflow.execute(workflow_input)
        print("\n   ✅ Workflow completed successfully")
    except Exception as e:
        print(f"\n   ❌ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Display results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)

    print(f"\n📋 Reasoning:\n{result.reasoning}\n")

    print(f"🍽️  Top 3 Recommendations:\n")
    for i, option in enumerate(result.top_3_options, 1):
        print(f"{i}. {option.meal_name}")
        print(f"   Calories: {option.calories}")
        print(f"   Macros: {option.protein_g}g protein, {option.carbs_g}g carbs, {option.fat_g}g fat")
        print(f"   Why: {option.reasoning}\n")

    print("="*70)
    print("✅ LOCAL VERIFICATION PASSED")
    print("="*70)
    print("\nNext steps:")
    print("1. Check output above looks reasonable")
    print("2. If OK, integrate into API (src/api/recommendations.py)")
    print("3. Add use_workflow=True query parameter")
    print("4. Route to WorkflowRecommendationService")


if __name__ == "__main__":
    asyncio.run(test_workflow())
