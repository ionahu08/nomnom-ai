"""
Integration tests for AI service with LLM harness.

This verifies that the harness is properly integrated into the service layer:
1. Service uses all harness components (client, router, parser, prompts, tools)
2. Valid responses are properly parsed and returned
3. Invalid responses trigger fallback
4. All cat styles work
5. Error handling is graceful
"""

from unittest.mock import AsyncMock, MagicMock, patch

import anthropic
import pytest

from src.services.ai_service import analyze_food_photo


@pytest.mark.asyncio
class TestFoodLogsAnalyzeWithHarness:
    """Test food analysis service using LLM harness."""

    async def test_analyze_photo_success_with_harness(self):
        """Test successful photo analysis with harness."""
        # Mock the LLM response with tool_use
        mock_response = MagicMock(spec=anthropic.types.Message)
        tool_use_block = MagicMock()
        tool_use_block.type = "tool_use"
        tool_use_block.input = {
            "food_name": "Pepperoni Pizza",
            "calories": 450,
            "protein_g": 22.0,
            "carbs_g": 52.0,
            "fat_g": 18.0,
            "food_category": "fast food",
            "cuisine_origin": "Italian-American",
            "cat_roast": "Pizza again? Consistent choices!",
        }
        mock_response.content = [tool_use_block]
        mock_response.usage = MagicMock(input_tokens=200, output_tokens=100)

        with patch("src.llm.client.LLMClient.create_message_with_retry") as mock_call:
            mock_call.return_value = mock_response

            # Call the service
            result = await analyze_food_photo(b"fake image data", cat_style="sassy")

            # Verify result
            assert result.food_name == "Pepperoni Pizza"
            assert result.calories == 450
            assert result.protein_g == 22.0
            assert result.carbs_g == 52.0
            assert result.fat_g == 18.0
            assert result.food_category == "fast food"
            assert result.cuisine_origin == "Italian-American"
            assert "consistent" in result.cat_roast.lower()

            # Verify harness was called with correct params
            call_args = mock_call.call_args
            assert call_args[1]["model"] == "claude-haiku-4-5-20251001"
            assert call_args[1]["fallback_model"] == "claude-sonnet-4-20250514"
            assert "sassy" in call_args[1]["system"].lower()

    async def test_analyze_photo_with_invalid_response(self):
        """Test that invalid AI responses return fallback."""
        # Mock response with invalid calories (> 5000)
        mock_response = MagicMock(spec=anthropic.types.Message)
        tool_use_block = MagicMock()
        tool_use_block.type = "tool_use"
        tool_use_block.input = {
            "food_name": "Huge Meal",
            "calories": 6000,  # Invalid! Should be 0-5000
            "protein_g": 22.0,
            "carbs_g": 52.0,
            "fat_g": 18.0,
            "food_category": "fast food",
            "cuisine_origin": "American",
            "cat_roast": "That's a lot.",
        }
        mock_response.content = [tool_use_block]

        with patch("src.llm.client.LLMClient.create_message_with_retry") as mock_call:
            mock_call.return_value = mock_response

            # Service should catch validation error and return fallback
            result = await analyze_food_photo(b"fake image", cat_style="sassy")

            # Should return fallback response
            assert result.food_name == "Unknown Food"
            assert result.calories == 0
            assert "encountered a problem" in result.cat_roast

    async def test_analyze_photo_with_different_cat_styles(self):
        """Test that different cat styles produce different prompts."""
        from src.llm.prompt_engine import render_analyze_food_prompt

        cat_styles = ["sassy", "grumpy", "wholesome", "concerned"]

        for style in cat_styles:
            prompt = render_analyze_food_prompt(cat_style=style)
            assert isinstance(prompt, str)
            assert len(prompt) > 0
            # Verify cat style is in the prompt
            assert style.lower() in prompt.lower()

    async def test_analyze_photo_with_fallback_model(self):
        """Test that fallback model is passed to harness."""
        valid_response = MagicMock(spec=anthropic.types.Message)
        tool_use_block = MagicMock()
        tool_use_block.type = "tool_use"
        tool_use_block.input = {
            "food_name": "Pizza",
            "calories": 500,
            "protein_g": 20.0,
            "carbs_g": 60.0,
            "fat_g": 20.0,
            "food_category": "fast food",
            "cuisine_origin": "Italian",
            "cat_roast": "Classic.",
        }
        valid_response.content = [tool_use_block]
        valid_response.usage = MagicMock(input_tokens=100, output_tokens=50)

        with patch(
            "src.llm.client.LLMClient.create_message_with_retry"
        ) as mock_call:
            mock_call.return_value = valid_response

            await analyze_food_photo(b"fake image", cat_style="sassy")

            # Verify fallback model is passed
            call_kwargs = mock_call.call_args[1]
            assert call_kwargs["fallback_model"] == "claude-sonnet-4-20250514"
            assert call_kwargs["model"] == "claude-haiku-4-5-20251001"


class TestHarnessIntegration:
    """Test harness integration at service layer."""

    def test_ai_service_imports_harness(self):
        """Verify ai_service uses harness components."""
        from src.services import ai_service

        # Check that harness components are imported
        assert hasattr(ai_service, "llm_client")
        assert hasattr(ai_service, "parser")
        assert hasattr(ai_service, "render_analyze_food_prompt")
        assert hasattr(ai_service, "get_route")
        assert hasattr(ai_service, "get_tools_for_task")

    def test_analyze_food_photo_signature(self):
        """Verify function signature matches endpoint expectations."""
        from src.services.ai_service import analyze_food_photo
        import inspect

        sig = inspect.signature(analyze_food_photo)
        params = list(sig.parameters.keys())

        # Should accept image_bytes and cat_style
        assert "image_bytes" in params
        assert "cat_style" in params

        # Should return FoodAnalysisResponse (async)
        assert inspect.iscoroutinefunction(analyze_food_photo)

    def test_fallback_response_is_valid(self):
        """Verify fallback response is a valid FoodAnalysisResponse."""
        from src.services.ai_service import _get_fallback_response
        from src.schemas.food_log import FoodAnalysisResponse

        fallback = _get_fallback_response("test error")

        # Should be valid FoodAnalysisResponse
        assert isinstance(fallback, FoodAnalysisResponse)
        assert fallback.food_name == "Unknown Food"
        assert fallback.calories == 0
        # Should not raise validation error
        FoodAnalysisResponse(**fallback.model_dump())
