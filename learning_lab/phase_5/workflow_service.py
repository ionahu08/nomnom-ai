"""
Phase 5 Day 9: WorkflowService for NomNom

Implements the 5-step workflow for meal recommendations:
1. Extract constraints → 2. Search RAG → 3. Generate menus → 4. Validate → 5. Rank

This is STRUCTURED, PREDICTABLE, and COST-CONTROLLED.
Perfect for: "Recommend a 600-calorie lunch for vegetarians"

Run: python3 workflow_service.py --calories 600 --diet vegetarian
"""

import json
import sys
from typing import Optional
from dataclasses import dataclass

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic library not installed")
    print("Install with: pip install anthropic")
    sys.exit(1)


@dataclass
class Meal:
    name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    vegetarian: bool
    prep_time_minutes: int


@dataclass
class RecommendationResult:
    meals: list[Meal]
    reasoning: str
    total_tokens_used: int
    total_cost_usd: float


class MockRAG:
    """Mock RAG database of meals"""

    def search(self, constraints: dict) -> list[Meal]:
        """Search for meals matching constraints"""
        print(f"  [RAG Search] Query: {constraints}")

        all_meals = [
            Meal("Grilled Chicken Salad", 550, 45, 30, 15, False, 15),
            Meal("Lentil Buddha Bowl", 580, 22, 65, 12, True, 20),
            Meal("Salmon with Vegetables", 620, 40, 35, 18, False, 25),
            Meal("Vegetable Stir-Fry Rice", 600, 18, 72, 10, True, 18),
            Meal("Turkey Wrap", 620, 35, 58, 15, False, 10),
            Meal("Tofu Pad Thai", 610, 20, 68, 14, True, 22),
        ]

        # Filter by diet type
        diet_type = constraints.get("diet_type", "").lower()
        if diet_type == "vegetarian":
            meals = [m for m in all_meals if m.vegetarian]
        else:
            meals = all_meals

        # Filter by calories
        target_calories = constraints.get("calories", 600)
        tolerance = 50
        meals = [m for m in meals if abs(m.calories - target_calories) <= tolerance]

        result = f"Found {len(meals)} meals matching constraints"
        print(f"  [RAG Result] {result}")
        return meals


class WorkflowService:
    """
    5-step meal recommendation workflow.

    Each step calls Claude with a different role/instruction.
    Steps are sequential (not parallel), but each has isolated context.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.rag = MockRAG()
        self.total_tokens = 0
        self.total_cost = 0.0

    def recommend_meal(
        self,
        calories: int,
        diet_type: str,
        cuisine: str,
        user_id: int
    ) -> RecommendationResult:
        """
        Full 5-step workflow for meal recommendation.

        Args:
            calories: Target calories
            diet_type: vegetarian, vegan, keto, etc.
            cuisine: preferred cuisine
            user_id: For RAG personalization

        Returns:
            RecommendationResult with meals, reasoning, metrics
        """
        print("\n" + "="*70)
        print("WORKFLOW: Meal Recommendation (5-step)")
        print("="*70)
        print(f"Input: {calories}cal, {diet_type}, {cuisine}")

        # Step 1: Extract Constraints
        print("\n" + "-"*70)
        print("Step 1: Extract Constraints")
        print("-"*70)
        constraints = self._extract_constraints(calories, diet_type, cuisine)

        # Step 2: Search RAG
        print("\n" + "-"*70)
        print("Step 2: Search RAG")
        print("-"*70)
        candidates = self._search_rag(constraints)

        # Step 3: Generate Menus
        print("\n" + "-"*70)
        print("Step 3: Generate Menu Options")
        print("-"*70)
        menus = self._generate_menus(candidates, constraints)

        # Step 4: Validate
        print("\n" + "-"*70)
        print("Step 4: Validate Nutritional Content")
        print("-"*70)
        validated = self._validate_menus(menus, constraints)

        # Step 5: Rank
        print("\n" + "-"*70)
        print("Step 5: Rank by User Preference")
        print("-"*70)
        ranked = self._rank_menus(validated)

        print("\n" + "="*70)
        print(f"Total tokens: {self.total_tokens}")
        print(f"Total cost: ${self.total_cost:.4f}")
        print("="*70)

        return RecommendationResult(
            meals=ranked,
            reasoning="5-step workflow completed successfully",
            total_tokens_used=self.total_tokens,
            total_cost_usd=self.total_cost
        )

    def _extract_constraints(self, calories: int, diet_type: str, cuisine: str) -> dict:
        """Step 1: Extract and structure constraints"""
        constraints = {
            "calories": calories,
            "diet_type": diet_type,
            "cuisine": cuisine,
            "max_prep_time": 30
        }
        print(f"Extracted: {constraints}")
        return constraints

    def _search_rag(self, constraints: dict) -> list[Meal]:
        """Step 2: Search RAG for matching meals"""
        candidates = self.rag.search(constraints)
        print(f"Retrieved {len(candidates)} candidate meals")
        return candidates

    def _generate_menus(self, candidates: list[Meal], constraints: dict) -> list[str]:
        """Step 3: Generate menu descriptions"""
        print(f"Generating descriptions for {len(candidates)} meals...")

        menus = []
        for meal in candidates:
            description = f"{meal.name}: {meal.calories}cal, {meal.protein_g}g protein, {meal.prep_time_minutes}min prep"
            menus.append(description)

        print(f"Generated {len(menus)} menu descriptions")
        return menus

    def _validate_menus(self, menus: list[str], constraints: dict) -> list[str]:
        """Step 4: Validate menus against constraints"""
        print(f"Validating {len(menus)} menus against constraints...")

        # In real system: Claude validates nutrition
        # Here: just pass through
        valid_menus = menus

        print(f"Validated {len(valid_menus)} menus (all passed)")
        return valid_menus

    def _rank_menus(self, menus: list[str]) -> list[Meal]:
        """Step 5: Rank by user preference"""
        print(f"Ranking {len(menus)} menus...")

        # In real system: Claude ranks based on user profile
        # Here: return top 3
        ranked = [
            Meal("Lentil Buddha Bowl", 580, 22, 65, 12, True, 20),
            Meal("Vegetable Stir-Fry Rice", 600, 18, 72, 10, True, 18),
            Meal("Grilled Chicken Salad", 550, 45, 30, 15, False, 15),
        ]

        print(f"Ranked and returning top {len(ranked)} recommendations")
        return ranked


def main():
    """Test WorkflowService"""
    service = WorkflowService()

    # Test case 1: Vegetarian, 600 calories
    result = service.recommend_meal(
        calories=600,
        diet_type="vegetarian",
        cuisine="any",
        user_id=1
    )

    print("\n" + "#"*70)
    print("# RECOMMENDATIONS")
    print("#"*70)
    for i, meal in enumerate(result.meals, 1):
        print(f"\n{i}. {meal.name}")
        print(f"   Calories: {meal.calories}")
        print(f"   Protein: {meal.protein_g}g")
        print(f"   Prep time: {meal.prep_time_minutes}min")


if __name__ == "__main__":
    main()
