"""
AI Service — Production-grade food analysis using LLM Harness.

This replaces the basic AI calls with the full harness:
- Retry logic for resilience
- Fallback models for reliability
- Structured output enforcement via tool_use
- Validation with Pydantic
- Comprehensive logging
"""

import base64
import logging
from typing import Optional

from src.config import settings
from src.llm.client import LLMClient
from src.llm.guardrails import FoodAnalysisGuardrails, GuardrailViolation
from src.llm.parser import FoodAnalysisParser, ParseError
from src.llm.prompt_engine import render_analyze_food_prompt
from src.llm.router import TaskType, get_route
from src.llm.tools import get_tools_for_task
from src.schemas.food_log import FoodAnalysisResponse

logger = logging.getLogger(__name__)

# Initialize LLM client once
llm_client = LLMClient(api_key=settings.anthropic_api_key)
parser = FoodAnalysisParser()


async def analyze_food_photo(
    image_bytes: bytes, cat_style: str = "sassy"
) -> FoodAnalysisResponse:
    """
    Analyze a food photo using the production LLM harness.

    This is the complete, resilient version with:
    - Retry logic (up to 2 attempts)
    - Fallback model (Haiku → Sonnet if needed)
    - Structured output via tool_use (forced JSON)
    - Validation (catches hallucinations)
    - Comprehensive logging

    Args:
        image_bytes: JPEG image data as bytes
        cat_style: Cat personality ("sassy", "grumpy", "wholesome", "concerned", "neutral")

    Returns:
        FoodAnalysisResponse with validated nutritional data

    Raises:
        ParseError: If AI response is invalid and retries fail
    """
    try:
        # Step 1: Get route (model selection + config)
        task_type = TaskType.ANALYZE_FOOD
        route = get_route(task_type)

        # Step 2: Render prompt with cat personality
        system_prompt = render_analyze_food_prompt(cat_style=cat_style)

        # Step 3: Prepare image as base64 + message
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": "What food is this? Analyze it and roast me.",
                    },
                ],
            }
        ]

        # Step 4: Get tool definitions (enforce structured output)
        tools = get_tools_for_task(task_type.value)

        # Step 5: Call LLM with retry, timeout, fallback
        logger.info(
            "Calling LLM for food analysis",
            extra={
                "model": route.primary_model,
                "fallback": route.fallback_model,
                "cat_style": cat_style,
            },
        )

        response = await llm_client.create_message_with_retry(
            model=route.primary_model,
            messages=messages,
            system=system_prompt,
            max_tokens=route.max_tokens,
            fallback_model=route.fallback_model,
            tools=tools,
            temperature=route.temperature,
        )

        logger.debug(
            f"LLM response received",
            extra={
                "model": response.model if hasattr(response, "model") else "unknown",
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
            },
        )

        # Step 6: Parse and validate response
        analysis = await parser.parse_response(response, FoodAnalysisResponse)

        # Step 7: Apply guardrails (catch toxicity, safety issues)
        try:
            analysis = FoodAnalysisGuardrails.validate(analysis)
        except GuardrailViolation as e:
            logger.warning(f"Guardrail violation: {e}")
            # Return fallback if guardrails fail
            return _get_fallback_response(f"Guardrail violation: {e}")

        logger.info(
            "Food analysis succeeded",
            extra={
                "food_name": analysis.food_name,
                "calories": analysis.calories,
                "cat_style": cat_style,
            },
        )

        return analysis

    except ParseError as e:
        logger.error(f"Failed to parse food analysis response: {e}")
        # Return graceful fallback
        return _get_fallback_response(str(e))
    except Exception as e:
        logger.error(f"Unexpected error during food analysis: {e}", exc_info=True)
        return _get_fallback_response(str(e))


def _get_fallback_response(error_message: str) -> FoodAnalysisResponse:
    """
    Return a safe fallback response when analysis fails.

    This lets the user know something went wrong but doesn't crash the app.
    """
    logger.warning(f"Returning fallback response due to: {error_message}")
    return FoodAnalysisResponse(
        food_name="Unknown Food",
        calories=0,
        protein_g=0,
        carbs_g=0,
        fat_g=0,
        food_category="unknown",
        cuisine_origin="unknown",
        cat_roast="I tried to judge your food but encountered a problem. Please try again.",
    )
