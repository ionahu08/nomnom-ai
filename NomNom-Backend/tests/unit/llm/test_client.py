"""
Tests for LLMClient retry, timeout, and fallback logic.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import anthropic
import httpx
import pytest

from src.llm.client import LLMClient


@pytest.fixture
def mock_response():
    """Create a mock Anthropic message response."""
    response = MagicMock(spec=anthropic.types.Message)
    response.content = [MagicMock(type="text", text="Test response")]
    response.usage = MagicMock(input_tokens=10, output_tokens=5)
    return response


@pytest.fixture
def llm_client():
    """Create an LLMClient instance with a mocked Anthropic client."""
    client = LLMClient(api_key="test-key")
    return client


@pytest.fixture
def mock_request():
    """Create a mock httpx.Request for APIError."""
    return MagicMock(spec=httpx.Request)


def create_mock_api_error(message: str = "API Error") -> anthropic.APIError:
    """Helper to create a properly initialized APIError for testing."""
    request = MagicMock(spec=httpx.Request)
    response = MagicMock(spec=httpx.Response)
    response.status_code = 500
    response.content = b'{"error": "test error"}'
    return anthropic.APIError(message=message, request=request, body={"error": message})


class TestSuccessfulCall:
    """Test successful calls without retries."""

    @pytest.mark.asyncio
    async def test_successful_call_on_first_attempt(self, llm_client, mock_response):
        """Successful call should return immediately."""
        with patch.object(
            llm_client.client.messages, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = mock_response

            response = await llm_client.create_message_with_retry(
                model="claude-haiku-4-5-20251001",
                messages=[{"role": "user", "content": "Hello"}],
                system="You are a helpful assistant",
            )

            assert response == mock_response
            mock_create.assert_called_once()


class TestRetryLogic:
    """Test retry logic with exponential backoff."""

    @pytest.mark.asyncio
    async def test_retry_on_api_error_then_succeed(
        self, llm_client, mock_response
    ):
        """API error on first attempt, succeed on retry."""
        with patch.object(
            llm_client.client.messages, "create", new_callable=AsyncMock
        ) as mock_create:
            # Fail once, succeed on second attempt
            mock_create.side_effect = [
                create_mock_api_error("Server error"),
                mock_response,
            ]

            response = await llm_client.create_message_with_retry(
                model="claude-haiku-4-5-20251001",
                messages=[{"role": "user", "content": "Hello"}],
            )

            assert response == mock_response
            assert mock_create.call_count == 2

    @pytest.mark.asyncio
    async def test_retry_on_timeout_then_succeed(
        self, llm_client, mock_response
    ):
        """Timeout on first attempt, succeed on retry."""
        with patch("asyncio.wait_for", new_callable=AsyncMock) as mock_wait_for:
            # Fail once with timeout, succeed on second attempt
            mock_wait_for.side_effect = [
                asyncio.TimeoutError(),
                mock_response,
            ]

            response = await llm_client.create_message_with_retry(
                model="claude-haiku-4-5-20251001",
                messages=[{"role": "user", "content": "Hello"}],
            )

            assert response == mock_response
            assert mock_wait_for.call_count == 2

    @pytest.mark.asyncio
    async def test_all_retries_fail_raises_error(self, llm_client):
        """If both attempts fail, should raise error."""
        with patch.object(
            llm_client.client.messages, "create", new_callable=AsyncMock
        ) as mock_create:
            # Both attempts fail
            mock_create.side_effect = create_mock_api_error("Server error")

            with pytest.raises(anthropic.APIError):
                await llm_client.create_message_with_retry(
                    model="claude-haiku-4-5-20251001",
                    messages=[{"role": "user", "content": "Hello"}],
                )

            assert mock_create.call_count == 2


class TestFallbackModel:
    """Test fallback to alternate model."""

    @pytest.mark.asyncio
    async def test_fallback_to_sonnet_on_haiku_failure(
        self, llm_client, mock_response
    ):
        """Haiku fails twice, fallback to Sonnet succeeds."""
        call_count = 0

        async def mock_create(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            model = kwargs.get("model")
            if model == "claude-haiku-4-5-20251001":
                raise create_mock_api_error("Haiku failed")
            elif model == "claude-sonnet-4-20250514":
                return mock_response
            return mock_response

        with patch.object(
            llm_client.client.messages, "create", new_callable=AsyncMock
        ) as mock_create_patch:
            mock_create_patch.side_effect = mock_create

            response = await llm_client.create_message_with_retry(
                model="claude-haiku-4-5-20251001",
                messages=[{"role": "user", "content": "Hello"}],
                fallback_model="claude-sonnet-4-20250514",
            )

            assert response == mock_response
            # Should try Haiku twice, then Sonnet once
            assert call_count == 3

    @pytest.mark.asyncio
    async def test_fallback_not_used_on_first_success(
        self, llm_client, mock_response
    ):
        """If primary model succeeds, fallback is not used."""
        with patch.object(
            llm_client.client.messages, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = mock_response

            response = await llm_client.create_message_with_retry(
                model="claude-haiku-4-5-20251001",
                messages=[{"role": "user", "content": "Hello"}],
                fallback_model="claude-sonnet-4-20250514",
            )

            assert response == mock_response
            # Only one call to primary model
            assert mock_create.call_count == 1


class TestModelConfiguration:
    """Test timeout and max_tokens per model."""

    @pytest.mark.asyncio
    async def test_haiku_uses_10_second_timeout(
        self, llm_client, mock_response
    ):
        """Haiku should use 10s timeout."""
        with patch("asyncio.wait_for", new_callable=AsyncMock) as mock_wait_for:
            mock_wait_for.return_value = mock_response

            await llm_client.create_message_with_retry(
                model="claude-haiku-4-5-20251001",
                messages=[{"role": "user", "content": "Hello"}],
            )

            # Check timeout was 10s
            call_args = mock_wait_for.call_args
            assert call_args[1]["timeout"] == 10

    @pytest.mark.asyncio
    async def test_sonnet_uses_30_second_timeout(
        self, llm_client, mock_response
    ):
        """Sonnet should use 30s timeout."""
        with patch("asyncio.wait_for", new_callable=AsyncMock) as mock_wait_for:
            mock_wait_for.return_value = mock_response

            await llm_client.create_message_with_retry(
                model="claude-sonnet-4-20250514",
                messages=[{"role": "user", "content": "Hello"}],
            )

            # Check timeout was 30s
            call_args = mock_wait_for.call_args
            assert call_args[1]["timeout"] == 30

    @pytest.mark.asyncio
    async def test_max_tokens_uses_model_default(
        self, llm_client, mock_response
    ):
        """max_tokens should use model default if not provided."""
        with patch.object(
            llm_client.client.messages, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = mock_response

            await llm_client.create_message_with_retry(
                model="claude-haiku-4-5-20251001",
                messages=[{"role": "user", "content": "Hello"}],
            )

            # Check max_tokens was set to Haiku default (500)
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["max_tokens"] == 500

    @pytest.mark.asyncio
    async def test_max_tokens_override(self, llm_client, mock_response):
        """Should use provided max_tokens over model default."""
        with patch.object(
            llm_client.client.messages, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = mock_response

            await llm_client.create_message_with_retry(
                model="claude-haiku-4-5-20251001",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=1000,
            )

            # Check max_tokens was overridden
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["max_tokens"] == 1000


class TestSystemPrompt:
    """Test system prompt handling."""

    @pytest.mark.asyncio
    async def test_system_prompt_passed_to_api(
        self, llm_client, mock_response
    ):
        """System prompt should be passed to Anthropic API."""
        with patch.object(
            llm_client.client.messages, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = mock_response
            system_prompt = "You are a helpful assistant"

            await llm_client.create_message_with_retry(
                model="claude-haiku-4-5-20251001",
                messages=[{"role": "user", "content": "Hello"}],
                system=system_prompt,
            )

            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["system"] == system_prompt
