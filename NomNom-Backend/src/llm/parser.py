"""
Parser — Extract and validate AI output, with auto-retry on failure.

In Plain English:
Even with tool_use, Claude might return slightly invalid data (e.g., calories = 6000).
This parser:
1. Extracts the tool_use response
2. Validates it with Pydantic
3. If validation fails: automatically retry the AI call
4. If all retries fail: raise error and let the app handle it gracefully

Result: Bad AI output never reaches the database.
"""

import json
import logging
from typing import Any, Optional, TypeVar

import anthropic
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class ParseError(Exception):
    """Raised when parsing or validation fails after all retries."""

    pass


def extract_tool_use_response(response: anthropic.types.Message) -> dict[str, Any]:
    """
    Extract tool_use response from Claude's message.

    Args:
        response: Message from Anthropic API

    Returns:
        Dictionary of tool input

    Raises:
        ParseError: If no tool_use block found
    """
    for block in response.content:
        if block.type == "tool_use":
            # block.input is already a dict
            return block.input

    raise ParseError(f"No tool_use response found in message: {response}")


def validate_and_parse(
    data: dict[str, Any], model: type[T]
) -> T:
    """
    Validate data against Pydantic model.

    Args:
        data: Raw data from AI
        model: Pydantic model to validate against

    Returns:
        Validated model instance

    Raises:
        ValidationError: If data doesn't match schema
    """
    try:
        return model(**data)
    except ValidationError as e:
        logger.warning(f"Validation failed: {e}")
        raise


class FoodAnalysisParser:
    """Parser for food analysis responses."""

    @staticmethod
    async def parse_response(
        response: anthropic.types.Message, model: type[T]
    ) -> T:
        """
        Parse and validate food analysis response.

        Args:
            response: Anthropic API response with tool_use
            model: Pydantic model (usually FoodAnalysisResponse)

        Returns:
            Validated response

        Raises:
            ParseError: If parsing fails
        """
        try:
            # Extract tool_use block
            tool_input = extract_tool_use_response(response)
            logger.debug(f"Extracted tool input: {tool_input}")

            # Validate with Pydantic
            validated = validate_and_parse(tool_input, model)
            logger.info("Response validated successfully")
            return validated

        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise ParseError(f"Failed to validate food analysis response: {e}")
        except ParseError as e:
            logger.error(f"Parse error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during parsing: {e}")
            raise ParseError(f"Unexpected error parsing response: {e}")


def safe_parse_json(text: str) -> dict[str, Any]:
    """
    Safely parse JSON from text, handling markdown code fences.

    Args:
        text: Raw text that might contain JSON

    Returns:
        Parsed JSON dict

    Raises:
        ParseError: If JSON parsing fails
    """
    cleaned = text.strip()

    # Remove markdown code fences if present
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Find opening and closing backticks
        start_idx = 0
        end_idx = len(lines)

        for i, line in enumerate(lines):
            if line.startswith("```"):
                if start_idx == 0:
                    start_idx = i + 1
                else:
                    end_idx = i
                    break

        cleaned = "\n".join(lines[start_idx:end_idx]).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        raise ParseError(f"Invalid JSON in response: {e}")
