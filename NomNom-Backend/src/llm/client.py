"""
LLM Client Wrapper — Anthropic API with retry, timeout, and fallback logic.

This is the core safety net that makes AI calls reliable:
- Retries failed calls with exponential backoff
- Fallback to a more reliable model if the first one keeps failing
- Enforces timeouts so the app doesn't hang forever
- Caps token usage to prevent runaway costs
"""

import asyncio
import logging
from typing import Any, Optional

import anthropic

logger = logging.getLogger(__name__)


# Model configuration: timeout (seconds) and max_tokens per model
MODEL_CONFIG = {
    "claude-haiku-4-5-20251001": {"timeout": 10, "max_tokens": 500},
    "claude-sonnet-4-20250514": {"timeout": 30, "max_tokens": 2000},
}


class LLMClient:
    """
    Wraps AsyncAnthropic with retry, timeout, and fallback logic.

    Usage:
        client = LLMClient(api_key="...")
        response = await client.create_message_with_retry(
            model="claude-haiku-4-5-20251001",
            messages=[{"role": "user", "content": "..."}],
            system="You are a helpful assistant",
            fallback_model="claude-sonnet-4-20250514"
        )
    """

    def __init__(self, api_key: str):
        """Initialize with Anthropic API key."""
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def create_message_with_retry(
        self,
        model: str,
        messages: list[dict],
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
        fallback_model: Optional[str] = None,
        **kwargs,
    ) -> anthropic.types.Message:
        """
        Create a message with retry logic, timeout, and fallback.

        Args:
            model: Primary model to use
            messages: List of message dicts with role and content
            system: System prompt
            max_tokens: Override default max_tokens for this model
            fallback_model: If primary model fails twice, try this model
            **kwargs: Additional arguments passed to create()

        Returns:
            anthropic.types.Message response

        Raises:
            anthropic.APIError: If all attempts fail
        """
        # Get config for primary model
        config = MODEL_CONFIG.get(model, {"timeout": 30, "max_tokens": 2000})
        timeout = config["timeout"]
        default_max_tokens = config["max_tokens"]

        # Use provided max_tokens or model default
        effective_max_tokens = max_tokens or default_max_tokens

        last_error: Optional[Exception] = None

        # Try primary model up to 2 times
        for attempt in range(2):
            try:
                response = await asyncio.wait_for(
                    self.client.messages.create(
                        model=model,
                        max_tokens=effective_max_tokens,
                        system=system,
                        messages=messages,
                        **kwargs,
                    ),
                    timeout=timeout,
                )
                logger.info(
                    "LLM call succeeded",
                    extra={
                        "model": model,
                        "attempt": attempt + 1,
                        "usage": {
                            "input_tokens": response.usage.input_tokens,
                            "output_tokens": response.usage.output_tokens,
                        },
                    },
                )
                return response
            except asyncio.TimeoutError as e:
                last_error = e
                logger.warning(
                    f"LLM call timed out ({model}, attempt {attempt + 1}/{2})",
                    extra={"model": model, "attempt": attempt + 1},
                )
                if attempt == 0:
                    await asyncio.sleep(1)  # Exponential backoff: 1s
                else:
                    await asyncio.sleep(2)  # Exponential backoff: 2s
                    # If second attempt times out, try fallback model
                    if fallback_model:
                        logger.info(
                            f"Primary model {model} failed, trying fallback {fallback_model}"
                        )
                        return await self.create_message_with_retry(
                            model=fallback_model,
                            messages=messages,
                            system=system,
                            max_tokens=max_tokens,
                            **kwargs,
                        )
            except anthropic.APIError as e:
                last_error = e
                logger.warning(
                    f"LLM call failed ({model}, attempt {attempt + 1}/{2}): {str(e)}",
                    extra={"model": model, "attempt": attempt + 1, "error": str(e)},
                )
                if attempt == 0:
                    await asyncio.sleep(1)  # Exponential backoff: 1s
                else:
                    await asyncio.sleep(2)  # Exponential backoff: 2s
                    # If second attempt fails, try fallback model
                    if fallback_model:
                        logger.info(
                            f"Primary model {model} failed, trying fallback {fallback_model}"
                        )
                        return await self.create_message_with_retry(
                            model=fallback_model,
                            messages=messages,
                            system=system,
                            max_tokens=max_tokens,
                            **kwargs,
                        )

        # All retries failed — re-raise last error
        if last_error:
            raise last_error
        raise RuntimeError(f"Failed to get response from {model} after 2 attempts")
