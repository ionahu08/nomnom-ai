"""
Tests for tool definitions.
"""

import pytest

from src.llm.tools import ANALYZE_FOOD_TOOL, get_tools_for_task


class TestAnalyzeFoodTool:
    """Test the analyze_food tool definition."""

    def test_tool_has_name(self):
        """Tool should have a name."""
        assert ANALYZE_FOOD_TOOL["name"] == "analyze_food"

    def test_tool_has_description(self):
        """Tool should have a description."""
        assert "description" in ANALYZE_FOOD_TOOL
        assert len(ANALYZE_FOOD_TOOL["description"]) > 0

    def test_tool_has_input_schema(self):
        """Tool should have input_schema."""
        assert "input_schema" in ANALYZE_FOOD_TOOL
        schema = ANALYZE_FOOD_TOOL["input_schema"]
        assert schema["type"] == "object"

    def test_schema_has_properties(self):
        """Schema should define all properties."""
        schema = ANALYZE_FOOD_TOOL["input_schema"]
        props = schema["properties"]

        expected = [
            "food_name",
            "calories",
            "protein_g",
            "carbs_g",
            "fat_g",
            "food_category",
            "cuisine_origin",
            "cat_roast",
        ]

        for prop in expected:
            assert prop in props

    def test_schema_has_required_fields(self):
        """Schema should mark all fields as required."""
        schema = ANALYZE_FOOD_TOOL["input_schema"]
        required = schema["required"]

        expected = [
            "food_name",
            "calories",
            "protein_g",
            "carbs_g",
            "fat_g",
            "food_category",
            "cuisine_origin",
            "cat_roast",
        ]

        for field in expected:
            assert field in required

    def test_food_name_property(self):
        """food_name should be a string."""
        props = ANALYZE_FOOD_TOOL["input_schema"]["properties"]
        assert props["food_name"]["type"] == "string"

    def test_calories_property(self):
        """calories should be an integer."""
        props = ANALYZE_FOOD_TOOL["input_schema"]["properties"]
        assert props["calories"]["type"] == "integer"

    def test_protein_property(self):
        """protein_g should be a number."""
        props = ANALYZE_FOOD_TOOL["input_schema"]["properties"]
        assert props["protein_g"]["type"] == "number"

    def test_carbs_property(self):
        """carbs_g should be a number."""
        props = ANALYZE_FOOD_TOOL["input_schema"]["properties"]
        assert props["carbs_g"]["type"] == "number"

    def test_fat_property(self):
        """fat_g should be a number."""
        props = ANALYZE_FOOD_TOOL["input_schema"]["properties"]
        assert props["fat_g"]["type"] == "number"

    def test_food_category_property(self):
        """food_category should be a string."""
        props = ANALYZE_FOOD_TOOL["input_schema"]["properties"]
        assert props["food_category"]["type"] == "string"

    def test_cuisine_origin_property(self):
        """cuisine_origin should be a string."""
        props = ANALYZE_FOOD_TOOL["input_schema"]["properties"]
        assert props["cuisine_origin"]["type"] == "string"

    def test_cat_roast_property(self):
        """cat_roast should be a string."""
        props = ANALYZE_FOOD_TOOL["input_schema"]["properties"]
        assert props["cat_roast"]["type"] == "string"


class TestGetToolsForTask:
    """Test task-specific tool retrieval."""

    def test_analyze_food_task(self):
        """analyze_food task should return food analysis tool."""
        tools = get_tools_for_task("analyze_food")
        assert len(tools) == 1
        assert tools[0]["name"] == "analyze_food"

    def test_recommend_meal_task(self):
        """recommend_meal task should return no tools."""
        tools = get_tools_for_task("recommend_meal")
        assert tools == []

    def test_weekly_recap_task(self):
        """weekly_recap task should return no tools."""
        tools = get_tools_for_task("weekly_recap")
        assert tools == []

    def test_unknown_task(self):
        """Unknown task should return empty list."""
        tools = get_tools_for_task("unknown_task")
        assert tools == []

    def test_analyze_food_tool_is_same_as_constant(self):
        """analyze_food task should return the same tool as ANALYZE_FOOD_TOOL."""
        tools = get_tools_for_task("analyze_food")
        assert tools[0] == ANALYZE_FOOD_TOOL
