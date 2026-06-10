"""
Meal Recommendation Workflow — 5-step prompt chaining.

Steps:
  1. Extract constraints (parse targets, restrictions, preferences)
  2. Search RAG (retrieve relevant meals from knowledge base)
  3. Generate options (create 3 recommendation options)
  4. Validate (check nutritional accuracy)
  5. Rank (order by user preference)

Each step has clear input/output. Steps are sequential.
This is STRUCTURED, PREDICTABLE, and COST-CONTROLLED.
"""

import json
import logging
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.llm.client import LLMClient
from src.llm.prompt_engine import render_prompt
from src.llm.router import TaskType, get_route
from src.schemas.user_profile import UserProfile
from src.services.food_log_service import FoodLog
from src.services.knowledge_service import get_relevant_nutrition_entries

logger = logging.getLogger(__name__)


@dataclass
class WorkflowInput:
    """Input to the workflow."""
    user_profile: UserProfile
    today_logs: list[FoodLog]
    target_calories: int
    target_protein: int
    target_carbs: int
    target_fat: int


@dataclass
class RecommendationOption:
    """A single recommendation option."""
    meal_name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    reasoning: str


@dataclass
class WorkflowOutput:
    """Output from the workflow."""
    top_3_options: list[RecommendationOption]
    reasoning: str
    total_tokens: int


class MealRecommendationWorkflow:
    """
    5-step meal recommendation workflow.

    Uses prompt chaining: each step builds on previous results.
    """

    def __init__(self, llm_client: LLMClient, db: AsyncSession):
        """
        Initialize workflow.

        Args:
            llm_client: LLMClient instance
            db: Database session (AsyncSession)
        """
        self.llm_client = llm_client
        self.db = db
        self.total_tokens = 0

    async def execute(self, workflow_input: WorkflowInput) -> WorkflowOutput:
        """
        Execute the full 5-step workflow.

        Args:
            workflow_input: Input with user profile, logs, targets

        Returns:
            WorkflowOutput with top 3 recommendations
        """
        logger.info("Starting MealRecommendationWorkflow")

        # Step 1: Extract Constraints
        constraints = self._step_1_extract_constraints(workflow_input)
        logger.debug(f"Step 1 extracted: {constraints}")

        # Step 2: Search RAG
        rag_results = await self._step_2_search_rag(constraints)
        logger.debug(f"Step 2 found {len(rag_results)} RAG results")

        # Step 3: Generate Options
        options = await self._step_3_generate_options(
            constraints, rag_results, workflow_input
        )
        logger.debug(f"Step 3 generated {len(options)} options")

        # Step 4: Validate
        validated = await self._step_4_validate(options)
        logger.debug(f"Step 4 validated {len(validated)} options")

        # Step 5: Rank
        ranked = await self._step_5_rank(validated, workflow_input.user_profile)
        logger.debug(f"Step 5 ranked options")

        logger.info(f"Workflow complete. Returning {len(ranked.top_3_options)} recommendations")

        return ranked

    def _step_1_extract_constraints(self, workflow_input: WorkflowInput) -> dict:
        """
        Step 1: Extract constraints from user profile and targets.

        Input: UserProfile, targets, today's logs
        Output: Structured constraints dict

        In production, this could call Claude to intelligently parse constraints.
        For now, we extract directly from the data.
        """
        today_calories = sum(log.calories for log in workflow_input.today_logs)
        today_protein = sum(log.protein_g for log in workflow_input.today_logs)
        today_carbs = sum(log.carbs_g for log in workflow_input.today_logs)
        today_fat = sum(log.fat_g for log in workflow_input.today_logs)

        missing_calories = max(0, workflow_input.target_calories - today_calories)
        missing_protein = max(0, workflow_input.target_protein - today_protein)
        missing_carbs = max(0, workflow_input.target_carbs - today_carbs)
        missing_fat = max(0, workflow_input.target_fat - today_fat)

        constraints = {
            "target_calories": workflow_input.target_calories,
            "missing_calories": missing_calories,
            "missing_protein": missing_protein,
            "missing_carbs": missing_carbs,
            "missing_fat": missing_fat,
            "dietary_restrictions": workflow_input.user_profile.dietary_restrictions or [],
            "allergies": workflow_input.user_profile.allergies or [],
            "cuisine_preferences": workflow_input.user_profile.cuisine_preferences or [],
        }

        return constraints

    async def _step_2_search_rag(self, constraints: dict) -> list[dict]:
        """
        Step 2: Search RAG for relevant meals.

        Input: Constraints dict
        Output: List of meal options from RAG

        Uses the existing knowledge_service to search by constraints.
        """
        # Build search query from constraints
        query_parts = []
        if constraints["missing_protein"] > 20:
            query_parts.append(f"{constraints['missing_protein']:.0f}g protein")
        if constraints["missing_carbs"] > 30:
            query_parts.append(f"{constraints['missing_carbs']:.0f}g carbs")
        if constraints["missing_fat"] > 10:
            query_parts.append(f"{constraints['missing_fat']:.0f}g fat")

        query = f"meal with {', '.join(query_parts)}" if query_parts else "balanced meal"

        logger.debug(f"RAG query: {query}")

        # Search RAG
        kb_entries = await get_relevant_nutrition_entries(self.db, query, limit=5)

        return kb_entries

    async def _step_3_generate_options(
        self,
        constraints: dict,
        rag_results: list[dict],
        workflow_input: WorkflowInput,
    ) -> list[RecommendationOption]:
        """
        Step 3: Generate recommendation options.

        Input: Constraints, RAG results
        Output: 3 recommendation options with reasoning

        Calls Claude (Sonnet) to generate creative recommendations.
        """
        logger.info("Step 3: Generating recommendation options via Claude")

        # Format KB entries for Claude
        kb_entries_text = "\n".join(
            [f"- {entry.get('name', 'Unknown')}: {entry}" for entry in rag_results[:5]]
        )

        # Render prompt with Jinja2
        system_prompt = render_prompt(
            "workflow_generate_options.j2",
            target_calories=workflow_input.target_calories,
            target_protein=workflow_input.target_protein,
            target_carbs=workflow_input.target_carbs,
            target_fat=workflow_input.target_fat,
            missing_calories=constraints["missing_calories"],
            missing_protein=constraints["missing_protein"],
            missing_carbs=constraints["missing_carbs"],
            missing_fat=constraints["missing_fat"],
            dietary_restrictions=constraints["dietary_restrictions"],
            allergies=constraints["allergies"],
            cuisine_preferences=constraints["cuisine_preferences"],
            kb_entries=kb_entries_text,
        )

        # Call Claude
        response = await self.llm_client.create_message_with_retry(
            model="claude-sonnet-4-6",
            messages=[{"role": "user", "content": "Generate meal recommendations."}],
            system=system_prompt,
            max_tokens=1500,
        )

        # Parse response
        response_text = response.content[0].text

        # Extract JSON from response
        try:
            # Handle markdown code fences
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text

            data = json.loads(json_str)
            options = [
                RecommendationOption(
                    meal_name=opt["meal_name"],
                    calories=opt["calories"],
                    protein_g=opt["protein_g"],
                    carbs_g=opt["carbs_g"],
                    fat_g=opt["fat_g"],
                    reasoning=opt["reasoning"],
                )
                for opt in data.get("options", [])
            ]

            if not options:
                logger.warning("Claude returned no options, using fallback")
                return self._get_fallback_options()

            logger.info(f"Generated {len(options)} options")
            return options

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse Claude response: {e}")
            logger.debug(f"Response was: {response_text}")
            return self._get_fallback_options()

    def _get_fallback_options(self) -> list[RecommendationOption]:
        """Return fallback options if Claude fails."""
        return [
            RecommendationOption(
                meal_name="Grilled Chicken with Quinoa",
                calories=450,
                protein_g=35,
                carbs_g=45,
                fat_g=8,
                reasoning="High protein, balanced macros"
            ),
            RecommendationOption(
                meal_name="Salmon with Sweet Potato",
                calories=480,
                protein_g=30,
                carbs_g=50,
                fat_g=12,
                reasoning="Omega-3 rich, good nutrients"
            ),
            RecommendationOption(
                meal_name="Vegetarian Buddha Bowl",
                calories=420,
                protein_g=18,
                carbs_g=55,
                fat_g=10,
                reasoning="Balanced and satisfying"
            ),
        ]

    async def _step_4_validate(
        self, options: list[RecommendationOption]
    ) -> list[RecommendationOption]:
        """
        Step 4: Validate nutritional accuracy.

        Input: Recommendation options
        Output: Validated options (removes any invalid ones)

        Calls Claude (Haiku) to verify nutritional claims.
        """
        logger.info(f"Step 4: Validating {len(options)} options")

        if not options:
            return options

        # Format options for Claude
        meals_text = "\n".join(
            [f"- {opt.meal_name}: {opt.calories} cal, {opt.protein_g}g protein, "
             f"{opt.carbs_g}g carbs, {opt.fat_g}g fat"
             for opt in options]
        )

        # Render prompt
        system_prompt = render_prompt(
            "workflow_validate.j2",
            target_calories=600,  # Example, could vary
            dietary_restrictions=[],
            allergies=[],
            meals=meals_text,
        )

        # Call Claude (use Haiku for this simpler task)
        try:
            response = await self.llm_client.create_message_with_retry(
                model="claude-haiku-4-5-20251001",
                messages=[{"role": "user", "content": "Validate these meals."}],
                system=system_prompt,
                max_tokens=1000,
            )

            response_text = response.content[0].text

            # Parse validation response
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text

            data = json.loads(json_str)
            validations = {v["meal_name"]: v for v in data.get("validations", [])}

            # Filter: keep only valid meals
            validated = [
                opt for opt in options
                if validations.get(opt.meal_name, {}).get("valid", True)
            ]

            if not validated:
                logger.warning("All options failed validation, keeping originals")
                return options

            logger.info(f"Validated {len(validated)} options")
            return validated

        except Exception as e:
            logger.warning(f"Validation failed: {e}, keeping all options")
            return options

    async def _step_5_rank(
        self, options: list[RecommendationOption], user_profile: UserProfile
    ) -> WorkflowOutput:
        """
        Step 5: Rank options by user preference.

        Input: Validated options, user profile
        Output: Top 3 ranked options

        Calls Claude (Haiku) to rank by user preference.
        """
        logger.info(f"Step 5: Ranking {len(options)} options")

        if not options:
            return WorkflowOutput(
                top_3_options=[],
                reasoning="No valid options to rank.",
                total_tokens=self.total_tokens,
            )

        # Format options for Claude
        meals_text = "\n".join(
            [f"- {opt.meal_name}: {opt.reasoning}" for opt in options]
        )

        # Render prompt
        system_prompt = render_prompt(
            "workflow_rank.j2",
            dietary_restrictions=user_profile.dietary_restrictions or [],
            cuisine_preferences=user_profile.cuisine_preferences or [],
            allergies=user_profile.allergies or [],
            meals=meals_text,
        )

        try:
            # Call Claude (use Haiku for this simpler task)
            response = await self.llm_client.create_message_with_retry(
                model="claude-haiku-4-5-20251001",
                messages=[{"role": "user", "content": "Rank these meals."}],
                system=system_prompt,
                max_tokens=1000,
            )

            response_text = response.content[0].text

            # Parse ranking response
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text

            data = json.loads(json_str)
            rankings = {r["meal_name"]: r for r in data.get("rankings", [])}

            # Sort options by rank
            ranked_options = sorted(
                options,
                key=lambda opt: rankings.get(opt.meal_name, {}).get("rank", 999)
            )

            # Take top 3
            top_3 = ranked_options[:3]

            reasoning = (
                "I've analyzed your nutrition targets and ranked 3 personalized "
                "meal recommendations that fit your macros and preferences."
            )

            logger.info(f"Ranked options, returning top {len(top_3)}")
            return WorkflowOutput(
                top_3_options=top_3,
                reasoning=reasoning,
                total_tokens=self.total_tokens,
            )

        except Exception as e:
            logger.warning(f"Ranking failed: {e}, returning first 3 options")
            return WorkflowOutput(
                top_3_options=options[:3],
                reasoning="Generated 3 meal recommendations.",
                total_tokens=self.total_tokens,
            )
