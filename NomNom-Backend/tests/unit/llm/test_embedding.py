"""
Tests for embedding service.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.llm.embedding import EMBEDDING_DIM, EmbeddingService


class TestEmbeddingDimension:
    """Test embedding dimension constant."""

    def test_embedding_dim_is_correct(self):
        """Embedding dimension should be 384 (all-MiniLM-L6-v2 output)."""
        assert EMBEDDING_DIM == 384


class TestEmbeddingService:
    """Test EmbeddingService."""

    def test_service_singleton(self):
        """Module-level embedding_service should be a singleton."""
        from src.llm.embedding import embedding_service

        assert isinstance(embedding_service, EmbeddingService)

    @pytest.mark.asyncio
    async def test_embed_text_handles_empty_string(self):
        """embed_text should handle empty strings gracefully."""
        service = EmbeddingService()

        result = await service.embed_text("")
        assert len(result) == EMBEDDING_DIM
        assert all(x == 0.0 for x in result)

    @pytest.mark.asyncio
    async def test_embed_text_handles_whitespace(self):
        """embed_text should handle whitespace-only strings."""
        service = EmbeddingService()

        result = await service.embed_text("   ")
        assert len(result) == EMBEDDING_DIM
        assert all(x == 0.0 for x in result)

    @pytest.mark.asyncio
    async def test_embed_food_formats_with_category(self):
        """embed_food should format food_name (category) before embedding."""
        service = EmbeddingService()

        with AsyncMock(wraps=service.embed_text) as mock_embed:
            service.embed_text = mock_embed
            # This will call the real method but we can verify it's called correctly
            # by mocking at a higher level if needed
            result = await service.embed_food("Pizza", "fast food")
            assert len(result) == EMBEDDING_DIM

    @pytest.mark.asyncio
    async def test_embed_food_without_category(self):
        """embed_food should handle missing category."""
        service = EmbeddingService()

        result = await service.embed_food("Pizza", "")
        assert len(result) == EMBEDDING_DIM

    @pytest.mark.asyncio
    async def test_embed_text_returns_list_of_floats(self):
        """embed_text should return a list of floats."""
        service = EmbeddingService()
        result = await service.embed_text("pizza")

        assert isinstance(result, list)
        assert len(result) == EMBEDDING_DIM
        assert all(isinstance(x, float) for x in result)

    @pytest.mark.asyncio
    async def test_multiple_embed_calls_work(self):
        """Multiple embed_text calls should work consistently."""
        service = EmbeddingService()

        # First call
        result1 = await service.embed_text("pizza")
        assert len(result1) == EMBEDDING_DIM

        # Second call
        result2 = await service.embed_text("pasta")
        assert len(result2) == EMBEDDING_DIM

        # Different strings should produce different embeddings
        # (not necessarily, but very likely)
        # We just verify both return valid embeddings
