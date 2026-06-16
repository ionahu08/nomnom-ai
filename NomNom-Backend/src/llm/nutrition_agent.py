import json
import logging
from typing import Optional

from anthropic import Anthropic

from src.schemas.nutrition_insights import (
    HealthProfile,
    NutritionAnalysis,
    NutritionGap,
    PeriodData,
)

logger = logging.getLogger(__name__)


class NutritionAgent:
    """Claude-powered nutrition analysis and recommendation agent."""

    def __init__(self):
        self.client = Anthropic()

    def analyze_and_recommend(
        self,
        periods: dict[str, PeriodData],
        health_profile: HealthProfile,
    ) -> Optional[NutritionAnalysis]:
        """
        Analyze user's nutrition patterns and generate personalized recommendations.

        Args:
            periods: Multi-period nutrition data (day, week, month)
            health_profile: User's health profile (goals, allergies, conditions, targets)

        Returns:
            NutritionAnalysis with summary, strengths, gaps, and recommendations
            Returns None if analysis fails
        """
        try:
            # Build context for Claude
            context = self._build_context(periods, health_profile)

            # Call Claude API
            response = self.client.messages.create(
                model="claude-opus-4-7",
                max_tokens=1024,
                system=self._get_system_prompt(health_profile),
                messages=[
                    {
                        "role": "user",
                        "content": f"Please analyze this nutrition data and provide recommendations:\n\n{context}",
                    }
                ],
            )

            # Extract text response
            response_text = response.content[0].text

            # Parse response into structured format
            analysis = self._parse_response(response_text)
            logger.info(f"[NutritionAgent] Generated analysis: {analysis.summary[:100]}")
            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"[NutritionAgent] Failed to parse Claude response as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"[NutritionAgent] Error during nutrition analysis: {e}")
            logger.exception(f"[NutritionAgent] Full traceback: {e}")
            return None

    def _get_system_prompt(self, profile: HealthProfile) -> str:
        """Build system prompt customized to user's goal and constraints."""
        goal_context = self._get_goal_context(profile.goal)
        return f"""You are a friendly nutritionist assistant for a food tracking app.

Analyze the user's eating patterns from past 1 day, 1 week, and 1 month, and provide:
1. A brief summary of their nutrition status (1-2 sentences)
2. 2-3 things they're doing well (strengths)
3. 2-3 key nutrient gaps (areas for improvement)
4. 3-5 specific food recommendations to address gaps

Context:
- User's Goal: {goal_context}
- Dietary Constraints: No foods with {', '.join(profile.allergies or ['none'])}
- Medical Considerations: {', '.join(profile.medical_conditions or ['none'])}

IMPORTANT RULES:
1. NEVER recommend foods that match allergies or conflict with medical conditions
2. Base recommendations on foods they've already logged (show they like them)
3. Connect each recommendation to their specific goal
4. Be conversational and encouraging
5. Focus on practical, actionable changes

Format your response as a JSON object ONLY (no markdown, no extra text):
{{
  "summary": "One or two sentences about their overall nutrition status",
  "strengths": [
    "Thing they're doing well #1",
    "Thing they're doing well #2",
    "Thing they're doing well #3"
  ],
  "gaps": [
    "Nutrient or food category gap #1",
    "Nutrient or food category gap #2",
    "Nutrient or food category gap #3"
  ],
  "recommendations": [
    {{
      "nutrient": "Iron-rich foods",
      "foods": ["Spinach", "Lean beef", "Fortified cereals"],
      "reasoning": "Why this matters for their goal and current situation"
    }}
  ]
}}

Return ONLY the JSON object, nothing else."""

    def _get_goal_context(self, goal: Optional[str]) -> str:
        """Get human-readable description of user's goal."""
        goal_map = {
            "maintain": "Maintain current weight and fitness level",
            "lean_out": "Reduce body fat while preserving muscle",
            "gain_muscle": "Build muscle mass",
            "lose_weight": "Lose weight",
        }
        return goal_map.get(goal, "Maintain health") if goal else "Maintain health"

    def _build_context(self, periods: dict[str, PeriodData], profile: HealthProfile) -> str:
        """Build context string with nutrition data for Claude."""
        lines = []

        # Add period summaries
        for period_name in ["day", "week", "month"]:
            if period_name not in periods:
                continue
            period = periods[period_name]

            period_label = {
                "day": "Last 24 Hours",
                "week": "Last 7 Days",
                "month": "Last 30 Days",
            }.get(period_name, period_name)

            lines.append(f"\n{period_label} ({period.start_date} to {period.end_date}):")
            lines.append(f"  Calories: {period.calories.total:.0f} / {period.calories.target} ({period.calories.percentage:.0f}%)")
            lines.append(f"  Protein: {period.protein.total:.0f}g / {period.protein.target}g ({period.protein.percentage:.0f}%)")
            lines.append(f"  Carbs: {period.carbs.total:.0f}g / {period.carbs.target}g ({period.carbs.percentage:.0f}%)")
            lines.append(f"  Fat: {period.fat.total:.0f}g / {period.fat.target}g ({period.fat.percentage:.0f}%)")
            if period.foods:
                lines.append(f"  Foods: {', '.join(period.foods[:10])}")

        # Add health profile
        lines.append(f"\nHealth Profile:")
        if profile.age:
            lines.append(f"  Age: {profile.age}")
        if profile.height_cm and profile.weight_kg:
            lines.append(f"  Height: {profile.height_cm}cm, Weight: {profile.weight_kg}kg")
        if profile.goal:
            lines.append(f"  Goal: {self._get_goal_context(profile.goal)}")
        if profile.allergies:
            lines.append(f"  Allergies: {', '.join(profile.allergies)}")
        if profile.medical_conditions:
            lines.append(f"  Medical Conditions: {', '.join(profile.medical_conditions)}")

        return "\n".join(lines)

    def _parse_response(self, response_text: str) -> NutritionAnalysis:
        """Parse Claude's JSON response into NutritionAnalysis."""
        # Try to extract JSON from response (in case Claude adds markdown)
        json_str = response_text
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()

        data = json.loads(json_str)

        # Parse recommendations
        recommendations = []
        for rec in data.get("recommendations", []):
            recommendations.append(
                NutritionGap(
                    nutrient=rec.get("nutrient", ""),
                    foods=rec.get("foods", []),
                    reasoning=rec.get("reasoning", ""),
                )
            )

        return NutritionAnalysis(
            summary=data.get("summary", ""),
            strengths=data.get("strengths", []),
            gaps=data.get("gaps", []),
            recommendations=recommendations,
        )


# Singleton instance
_nutrition_agent: Optional[NutritionAgent] = None


def get_nutrition_agent() -> NutritionAgent:
    """Get or create nutrition agent instance."""
    global _nutrition_agent
    if _nutrition_agent is None:
        _nutrition_agent = NutritionAgent()
    return _nutrition_agent
