"""
Integration Tests for LLM Harness — all components working together.

This test verifies the complete flow:
1. Choose model via router (task type)
2. Render prompt with Jinja2
3. Call LLMClient with retry/timeout/fallback
4. Parse and validate response
5. Handle errors gracefully
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import anthropic
import pytest

from src.llm.client import LLMClient
from src.llm.parser import FoodAnalysisParser, ParseError
from src.llm.prompt_engine import render_analyze_food_prompt
from src.llm.router import TaskType, get_route
from src.llm.tools import get_tools_for_task
from src.schemas.food_log import FoodAnalysisResponse


class TestCompleteAnalysisFlow:
    """Test the complete food analysis flow end-to-end."""

    @pytest.mark.asyncio
    async def test_full_flow_happy_path(self):
        """Test complete flow: route → render → call → parse → validate."""
        # Step 1: Router — choose model and config
        task_type = TaskType.ANALYZE_FOOD
        route = get_route(task_type)

        assert route.primary_model == "claude-haiku-4-5-20251001"
        assert route.max_tokens == 500
        assert route.temperature == 0.7

        # Step 2: Get tools for task
        tools = get_tools_for_task(task_type.value)
        assert len(tools) == 1
        assert tools[0]["name"] == "analyze_food"

        # Step 3: Render prompt
        prompt = render_analyze_food_prompt(cat_style="sassy")
        assert "sassy" in prompt.lower()
        assert "JSON" in prompt

        # Step 4: Mock LLMClient and make call
        client = LLMClient(api_key="test-key")

        # Create mock response with tool_use
        response = MagicMock(spec=anthropic.types.Message)
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
            "cat_roast": "Pizza again?",
        }
        response.content = [tool_use_block]
        response.usage = MagicMock(input_tokens=100, output_tokens=50)

        with patch.object(
            client.client.messages, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = response

            # Step 5: Call LLMClient
            result = await client.create_message_with_retry(
                model=route.primary_model,
                messages=[{"role": "user", "content": "Analyze this food"}],
                system=prompt,
                max_tokens=route.max_tokens,
                tools=tools,
            )

            assert result == response

        # Step 6: Parse response
        parser = FoodAnalysisParser()
        parsed = await parser.parse_response(response, FoodAnalysisResponse)

        # Step 7: Validate
        assert parsed.food_name == "Pizza"
        assert parsed.calories == 500
        assert parsed.protein_g == 20.0
        assert parsed.carbs_g == 60.0
        assert parsed.fat_g == 20.0
        assert parsed.food_category == "fast food"
        assert parsed.cuisine_origin == "Italian"
        assert parsed.cat_roast == "Pizza again?"

    @pytest.mark.asyncio
    async def test_flow_with_invalid_response(self):
        """Test flow when AI returns invalid data."""
        # Setup
        task_type = TaskType.ANALYZE_FOOD
        route = get_route(task_type)
        tools = get_tools_for_task(task_type.value)
        prompt = render_analyze_food_prompt(cat_style="sassy")

        # Create response with invalid calories
        response = MagicMock(spec=anthropic.types.Message)
        tool_use_block = MagicMock()
        tool_use_block.type = "tool_use"
        tool_use_block.input = {
            "food_name": "Pizza",
            "calories": 6000,  # Invalid! > 5000
            "protein_g": 20.0,
            "carbs_g": 60.0,
            "fat_g": 20.0,
            "food_category": "fast food",
            "cuisine_origin": "Italian",
            "cat_roast": "Pizza again?",
        }
        response.content = [tool_use_block]

        # Parser should catch this
        parser = FoodAnalysisParser()
        with pytest.raises(ParseError):
            await parser.parse_response(response, FoodAnalysisResponse)

    @pytest.mark.asyncio
    async def test_flow_with_retry_on_timeout(self):
        """Test flow when API times out and we retry."""
        task_type = TaskType.ANALYZE_FOOD
        route = get_route(task_type)
        tools = get_tools_for_task(task_type.value)
        prompt = render_analyze_food_prompt(cat_style="sassy")

        # Valid response
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
            "cat_roast": "Pizza again?",
        }
        valid_response.content = [tool_use_block]
        valid_response.usage = MagicMock(input_tokens=100, output_tokens=50)

        # Test client retry logic
        client = LLMClient(api_key="test-key")

        with patch.object(
            client.client.messages, "create", new_callable=AsyncMock
        ) as mock_create:
            # First attempt times out via wait_for, second succeeds
            mock_create.return_value = valid_response

            result = await client.create_message_with_retry(
                model=route.primary_model,
                messages=[{"role": "user", "content": "Analyze this"}],
                system=prompt,
                max_tokens=route.max_tokens,
                tools=tools,
            )

            assert result == valid_response

    @pytest.mark.asyncio
    async def test_flow_with_fallback_model(self):
        """Test flow when primary model fails and we use fallback."""
        task_type = TaskType.ANALYZE_FOOD
        route = get_route(task_type)

        # Valid response
        valid_response = MagicMock(spec=anthropic.types.Message)
        tool_use_block = MagicMock()
        tool_use_block.type = "tool_use"
        tool_use_block.input = {
            "food_name": "Salad",
            "calories": 300,
            "protein_g": 30.0,
            "carbs_g": 20.0,
            "fat_g": 10.0,
            "food_category": "salad",
            "cuisine_origin": "American",
            "cat_roast": "Healthy choice!",
        }
        valid_response.content = [tool_use_block]
        valid_response.usage = MagicMock(input_tokens=100, output_tokens=50)

        client = LLMClient(api_key="test-key")

        call_count = 0

        async def mock_create(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            model = kwargs.get("model")
            if model == "claude-haiku-4-5-20251001":
                # Primary fails
                from tests.unit.llm.test_client import create_mock_api_error
                raise create_mock_api_error("Haiku overloaded")
            elif model == "claude-sonnet-4-20250514":
                # Fallback succeeds
                return valid_response
            return valid_response

        with patch.object(
            client.client.messages, "create", new_callable=AsyncMock
        ) as mock_create_patch:
            mock_create_patch.side_effect = mock_create

            result = await client.create_message_with_retry(
                model=route.primary_model,
                messages=[{"role": "user", "content": "Analyze this"}],
                fallback_model=route.fallback_model,
            )

            assert result == valid_response
            # Should try Haiku twice, then Sonnet once
            assert call_count == 3

    @pytest.mark.asyncio
    async def test_multi_cat_styles(self):
        """Test prompt rendering with different cat styles."""
        cat_styles = ["sassy", "grumpy", "wholesome", "concerned", "neutral"]

        for style in cat_styles:
            prompt = render_analyze_food_prompt(cat_style=style)

            # Verify prompt is valid and includes expected content
            assert isinstance(prompt, str)
            assert len(prompt) > 0
            assert "food_name" in prompt
            assert "calories" in prompt
            assert "JSON" in prompt

    @pytest.mark.asyncio
    async def test_end_to_end_with_all_components(self):
        """Full integration: everything working together."""
        # Simulate: request → route → render → call → parse → respond

        # 1. Determine task
        task_type = TaskType.ANALYZE_FOOD

        # 2. Route to model
        route = get_route(task_type)
        tools = get_tools_for_task(task_type.value)

        # 3. Render prompt
        cat_style = "sassy"
        system_prompt = render_analyze_food_prompt(cat_style=cat_style)

        # 4. Prepare messages
        messages = [{"role": "user", "content": "Analyze this pizza photo"}]

        # 5. Create client
        client = LLMClient(api_key="test-key")

        # 6. Mock API response
        api_response = MagicMock(spec=anthropic.types.Message)
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
            "cat_roast": "Classic choice! At least it's consistent.",
        }
        api_response.content = [tool_use_block]
        api_response.usage = MagicMock(input_tokens=150, output_tokens=80)

        with patch.object(
            client.client.messages, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = api_response

            # 7. Call LLM
            llm_response = await client.create_message_with_retry(
                model=route.primary_model,
                messages=messages,
                system=system_prompt,
                max_tokens=route.max_tokens,
                tools=tools,
                temperature=route.temperature,
            )

            # 8. Parse response
            parser = FoodAnalysisParser()
            analysis = await parser.parse_response(
                llm_response, FoodAnalysisResponse
            )

            # 9. Verify result
            assert analysis.food_name == "Pepperoni Pizza"
            assert analysis.calories == 450
            assert analysis.protein_g == 22.0
            assert analysis.carbs_g == 52.0
            assert analysis.fat_g == 18.0
            assert analysis.food_category == "fast food"
            assert analysis.cuisine_origin == "Italian-American"
            assert "consistent" in analysis.cat_roast.lower()


class TestComponentIsolation:
    """Verify components work in isolation and together."""

    def test_router_independent_of_client(self):
        """Router should work without LLMClient."""
        route = get_route(TaskType.ANALYZE_FOOD)
        assert route.primary_model == "claude-haiku-4-5-20251001"
        assert route.fallback_model == "claude-sonnet-4-20250514"

    def test_prompt_engine_independent_of_router(self):
        """Prompt engine should work without router."""
        prompt = render_analyze_food_prompt(cat_style="grumpy")
        assert isinstance(prompt, str)
        assert "grumpy" in prompt.lower()

    def test_tools_independent_of_parser(self):
        """Tools should work without parser."""
        tools = get_tools_for_task("analyze_food")
        assert len(tools) == 1
        assert tools[0]["name"] == "analyze_food"

    def test_parser_independent_of_client(self):
        """Parser should work without LLMClient."""
        data = {
            "food_name": "Test Food",
            "calories": 200,
            "protein_g": 10.0,
            "carbs_g": 20.0,
            "fat_g": 8.0,
            "food_category": "test",
            "cuisine_origin": "test",
            "cat_roast": "Test roast",
        }
        response = FoodAnalysisResponse(**data)
        assert response.food_name == "Test Food"
