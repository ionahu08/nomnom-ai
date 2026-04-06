"""
Tests for parser and validation logic.
"""

import json
from unittest.mock import MagicMock

import anthropic
import pytest
from pydantic import ValidationError

from src.llm.parser import (
    FoodAnalysisParser,
    ParseError,
    extract_tool_use_response,
    safe_parse_json,
    validate_and_parse,
)
from src.llm.tools import get_tools_for_task
from src.schemas.food_log import FoodAnalysisResponse


class TestToolDefinitions:
    """Test tool_use schema definitions."""

    def test_get_tools_for_analyze_food(self):
        """Should return tool for food analysis."""
        tools = get_tools_for_task("analyze_food")
        assert len(tools) == 1
        assert tools[0]["name"] == "analyze_food"
        assert "input_schema" in tools[0]

    def test_get_tools_for_recommend_meal(self):
        """Recommendations don't use tools."""
        tools = get_tools_for_task("recommend_meal")
        assert tools == []

    def test_get_tools_for_weekly_recap(self):
        """Recaps don't use tools."""
        tools = get_tools_for_task("weekly_recap")
        assert tools == []

    def test_analyze_food_tool_has_required_fields(self):
        """Tool schema should define all required fields."""
        tools = get_tools_for_task("analyze_food")
        tool = tools[0]
        schema = tool["input_schema"]
        required = schema["required"]

        expected_fields = [
            "food_name",
            "calories",
            "protein_g",
            "carbs_g",
            "fat_g",
            "food_category",
            "cuisine_origin",
            "cat_roast",
        ]

        for field in expected_fields:
            assert field in required

    def test_analyze_food_tool_schema_structure(self):
        """Tool schema should be valid JSON schema."""
        tools = get_tools_for_task("analyze_food")
        tool = tools[0]
        schema = tool["input_schema"]

        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema


class TestFoodAnalysisResponseValidation:
    """Test FoodAnalysisResponse Pydantic validation."""

    def test_valid_food_analysis(self):
        """Valid data should pass validation."""
        data = {
            "food_name": "Chicken Caesar Salad",
            "calories": 350,
            "protein_g": 45.0,
            "carbs_g": 15.0,
            "fat_g": 14.0,
            "food_category": "salad",
            "cuisine_origin": "American",
            "cat_roast": "Look at you being healthy!",
        }
        response = FoodAnalysisResponse(**data)
        assert response.food_name == "Chicken Caesar Salad"
        assert response.calories == 350

    def test_missing_required_field(self):
        """Missing required field should fail."""
        data = {
            "food_name": "Chicken Caesar Salad",
            "calories": 350,
            "protein_g": 45.0,
            "carbs_g": 15.0,
            "fat_g": 14.0,
            "food_category": "salad",
            "cuisine_origin": "American",
            # Missing cat_roast (required field)
        }
        with pytest.raises(ValidationError):
            FoodAnalysisResponse(**data)

    def test_calories_out_of_range_too_high(self):
        """Calories > 5000 should fail."""
        data = {
            "food_name": "Huge Burger",
            "calories": 6000,  # Too high
            "protein_g": 45.0,
            "carbs_g": 15.0,
            "fat_g": 14.0,
            "food_category": "fast food",
            "cuisine_origin": "American",
            "cat_roast": "That's a lot.",
        }
        with pytest.raises(ValidationError):
            FoodAnalysisResponse(**data)

    def test_calories_negative(self):
        """Negative calories should fail."""
        data = {
            "food_name": "Salad",
            "calories": -100,
            "protein_g": 45.0,
            "carbs_g": 15.0,
            "fat_g": 14.0,
            "food_category": "salad",
            "cuisine_origin": "American",
            "cat_roast": "Negative calories?",
        }
        with pytest.raises(ValidationError):
            FoodAnalysisResponse(**data)

    def test_protein_out_of_range(self):
        """Protein > 500g should fail."""
        data = {
            "food_name": "Salad",
            "calories": 350,
            "protein_g": 600,  # Too high
            "carbs_g": 15.0,
            "fat_g": 14.0,
            "food_category": "salad",
            "cuisine_origin": "American",
            "cat_roast": "Really?",
        }
        with pytest.raises(ValidationError):
            FoodAnalysisResponse(**data)

    def test_carbs_negative(self):
        """Negative carbs should fail."""
        data = {
            "food_name": "Salad",
            "calories": 350,
            "protein_g": 45.0,
            "carbs_g": -50,  # Negative
            "fat_g": 14.0,
            "food_category": "salad",
            "cuisine_origin": "American",
            "cat_roast": "Negative carbs?",
        }
        with pytest.raises(ValidationError):
            FoodAnalysisResponse(**data)

    def test_fat_negative(self):
        """Negative fat should fail."""
        data = {
            "food_name": "Salad",
            "calories": 350,
            "protein_g": 45.0,
            "carbs_g": 15.0,
            "fat_g": -10,  # Negative
            "food_category": "salad",
            "cuisine_origin": "American",
            "cat_roast": "Negative fat?",
        }
        with pytest.raises(ValidationError):
            FoodAnalysisResponse(**data)

    def test_food_name_empty(self):
        """Empty food name should fail."""
        data = {
            "food_name": "",
            "calories": 350,
            "protein_g": 45.0,
            "carbs_g": 15.0,
            "fat_g": 14.0,
            "food_category": "salad",
            "cuisine_origin": "American",
            "cat_roast": "Something",
        }
        with pytest.raises(ValidationError):
            FoodAnalysisResponse(**data)

    def test_food_name_too_long(self):
        """Food name > 200 chars should fail."""
        data = {
            "food_name": "A" * 201,
            "calories": 350,
            "protein_g": 45.0,
            "carbs_g": 15.0,
            "fat_g": 14.0,
            "food_category": "salad",
            "cuisine_origin": "American",
            "cat_roast": "Something",
        }
        with pytest.raises(ValidationError):
            FoodAnalysisResponse(**data)

    def test_cat_roast_empty(self):
        """Empty roast should fail."""
        data = {
            "food_name": "Salad",
            "calories": 350,
            "protein_g": 45.0,
            "carbs_g": 15.0,
            "fat_g": 14.0,
            "food_category": "salad",
            "cuisine_origin": "American",
            "cat_roast": "",
        }
        with pytest.raises(ValidationError):
            FoodAnalysisResponse(**data)

    def test_cat_roast_too_long(self):
        """Roast > 500 chars should fail."""
        data = {
            "food_name": "Salad",
            "calories": 350,
            "protein_g": 45.0,
            "carbs_g": 15.0,
            "fat_g": 14.0,
            "food_category": "salad",
            "cuisine_origin": "American",
            "cat_roast": "A" * 501,
        }
        with pytest.raises(ValidationError):
            FoodAnalysisResponse(**data)

    def test_optional_fields(self):
        """Optional fields can be None."""
        data = {
            "food_name": "Salad",
            "calories": 350,
            "protein_g": 45.0,
            "carbs_g": 15.0,
            "fat_g": 14.0,
            "food_category": None,
            "cuisine_origin": None,
            "cat_roast": "Something",
        }
        response = FoodAnalysisResponse(**data)
        assert response.food_category is None
        assert response.cuisine_origin is None

    def test_edge_case_zero_calories(self):
        """Zero calories should be valid."""
        data = {
            "food_name": "Water",
            "calories": 0,
            "protein_g": 0.0,
            "carbs_g": 0.0,
            "fat_g": 0.0,
            "food_category": "drink",
            "cuisine_origin": "Universal",
            "cat_roast": "Boring.",
        }
        response = FoodAnalysisResponse(**data)
        assert response.calories == 0

    def test_edge_case_max_calories(self):
        """Max calories (5000) should be valid."""
        data = {
            "food_name": "Huge Meal",
            "calories": 5000,
            "protein_g": 500.0,
            "carbs_g": 500.0,
            "fat_g": 500.0,
            "food_category": "feast",
            "cuisine_origin": "American",
            "cat_roast": "That's a lot.",
        }
        response = FoodAnalysisResponse(**data)
        assert response.calories == 5000


class TestExtractToolUseResponse:
    """Test tool_use extraction from responses."""

    def test_extract_valid_tool_use(self):
        """Should extract tool_use block from response."""
        # Create mock response with tool_use block
        response = MagicMock(spec=anthropic.types.Message)
        tool_use_block = MagicMock()
        tool_use_block.type = "tool_use"
        tool_use_block.input = {
            "food_name": "Pizza",
            "calories": 500,
            "protein_g": 20,
            "carbs_g": 60,
            "fat_g": 20,
            "food_category": "fast food",
            "cuisine_origin": "Italian",
            "cat_roast": "Pizza again?",
        }
        response.content = [tool_use_block]

        result = extract_tool_use_response(response)
        assert result["food_name"] == "Pizza"
        assert result["calories"] == 500

    def test_extract_tool_use_with_text_block(self):
        """Should find tool_use even with text blocks."""
        response = MagicMock(spec=anthropic.types.Message)
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = "Analyzing..."

        tool_use_block = MagicMock()
        tool_use_block.type = "tool_use"
        tool_use_block.input = {"food_name": "Salad", "calories": 300, "protein_g": 30, "carbs_g": 20, "fat_g": 10, "food_category": "salad", "cuisine_origin": "American", "cat_roast": "Healthy!"}

        response.content = [text_block, tool_use_block]

        result = extract_tool_use_response(response)
        assert result["food_name"] == "Salad"

    def test_extract_no_tool_use_raises_error(self):
        """Should raise ParseError if no tool_use found."""
        response = MagicMock(spec=anthropic.types.Message)
        text_block = MagicMock()
        text_block.type = "text"
        response.content = [text_block]

        with pytest.raises(ParseError):
            extract_tool_use_response(response)


class TestValidateAndParse:
    """Test validate_and_parse function."""

    def test_valid_data_passes(self):
        """Valid data should pass validation."""
        data = {
            "food_name": "Pizza",
            "calories": 500,
            "protein_g": 20,
            "carbs_g": 60,
            "fat_g": 20,
            "food_category": "fast food",
            "cuisine_origin": "Italian",
            "cat_roast": "Pizza again?",
        }
        result = validate_and_parse(data, FoodAnalysisResponse)
        assert isinstance(result, FoodAnalysisResponse)
        assert result.food_name == "Pizza"

    def test_invalid_data_raises_error(self):
        """Invalid data should raise ValidationError."""
        data = {
            "food_name": "Pizza",
            "calories": 6000,  # Too high
            "protein_g": 20,
            "carbs_g": 60,
            "fat_g": 20,
            "food_category": "fast food",
            "cuisine_origin": "Italian",
            "cat_roast": "Pizza again?",
        }
        with pytest.raises(ValidationError):
            validate_and_parse(data, FoodAnalysisResponse)


class TestSafeParseJSON:
    """Test safe JSON parsing with markdown handling."""

    def test_parse_plain_json(self):
        """Should parse plain JSON."""
        text = '{"food_name": "Pizza", "calories": 500}'
        result = safe_parse_json(text)
        assert result["food_name"] == "Pizza"
        assert result["calories"] == 500

    def test_parse_json_with_markdown_fence(self):
        """Should strip markdown code fence."""
        text = """```json
{
  "food_name": "Pizza",
  "calories": 500
}
```"""
        result = safe_parse_json(text)
        assert result["food_name"] == "Pizza"
        assert result["calories"] == 500

    def test_parse_json_with_markdown_no_lang(self):
        """Should handle markdown fence without language."""
        text = """```
{"food_name": "Pizza", "calories": 500}
```"""
        result = safe_parse_json(text)
        assert result["food_name"] == "Pizza"

    def test_parse_json_with_whitespace(self):
        """Should handle leading/trailing whitespace."""
        text = '  {"food_name": "Pizza"}  '
        result = safe_parse_json(text)
        assert result["food_name"] == "Pizza"

    def test_parse_invalid_json_raises_error(self):
        """Should raise ParseError for invalid JSON."""
        text = "{invalid json}"
        with pytest.raises(ParseError):
            safe_parse_json(text)


class TestFoodAnalysisParser:
    """Test FoodAnalysisParser class."""

    @pytest.mark.asyncio
    async def test_parse_valid_response(self):
        """Should parse valid response."""
        response = MagicMock(spec=anthropic.types.Message)
        tool_use_block = MagicMock()
        tool_use_block.type = "tool_use"
        tool_use_block.input = {
            "food_name": "Pizza",
            "calories": 500,
            "protein_g": 20,
            "carbs_g": 60,
            "fat_g": 20,
            "food_category": "fast food",
            "cuisine_origin": "Italian",
            "cat_roast": "Pizza again?",
        }
        response.content = [tool_use_block]

        parser = FoodAnalysisParser()
        result = await parser.parse_response(response, FoodAnalysisResponse)

        assert isinstance(result, FoodAnalysisResponse)
        assert result.food_name == "Pizza"
        assert result.calories == 500

    @pytest.mark.asyncio
    async def test_parse_invalid_response_raises_error(self):
        """Should raise ParseError for invalid response."""
        response = MagicMock(spec=anthropic.types.Message)
        tool_use_block = MagicMock()
        tool_use_block.type = "tool_use"
        tool_use_block.input = {
            "food_name": "Pizza",
            "calories": 6000,  # Invalid
            "protein_g": 20,
            "carbs_g": 60,
            "fat_g": 20,
            "food_category": "fast food",
            "cuisine_origin": "Italian",
            "cat_roast": "Pizza again?",
        }
        response.content = [tool_use_block]

        parser = FoodAnalysisParser()
        with pytest.raises(ParseError):
            await parser.parse_response(response, FoodAnalysisResponse)
