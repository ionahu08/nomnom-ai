"""
Tests for semantic caching.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.llm.cache import CacheStats, SemanticCache, cache_stats
from src.schemas.food_log import FoodAnalysisResponse


class TestSemanticCache:
    """Test semantic cache interface."""

    def test_similarity_threshold_is_reasonable(self):
        """Similarity threshold should be between 0 and 1."""
        assert 0 <= SemanticCache.SIMILARITY_THRESHOLD <= 1
        # Higher threshold = fewer false positives
        assert SemanticCache.SIMILARITY_THRESHOLD > 0.9

    @pytest.mark.asyncio
    async def test_get_cached_analysis_returns_none_on_empty_db(self):
        """Should return None when no cached result exists."""
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        with patch("src.llm.cache.embedding_service.embed_text") as mock_embed:
            mock_embed.return_value = [0.0] * 384

            result = await SemanticCache.get_cached_analysis(mock_db, "pizza")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_cached_analysis_returns_foodlog_on_hit(self):
        """Should return FoodAnalysisResponse when match found."""
        mock_db = AsyncMock()
        mock_food_log = MagicMock(
            food_name="Pizza",
            calories=500,
            protein_g=20,
            carbs_g=60,
            fat_g=20,
            photo_path="/photos/pizza.jpg",
            food_category="fast food",
            cuisine_origin="Italian",
            cat_roast="Yum yum.",
        )
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_food_log

        with patch("src.llm.cache.embedding_service.embed_text") as mock_embed:
            mock_embed.return_value = [0.0] * 384

            result = await SemanticCache.get_cached_analysis(mock_db, "pizza")

            assert isinstance(result, FoodAnalysisResponse)
            assert result.food_name == "Pizza"
            assert result.calories == 500

    @pytest.mark.asyncio
    async def test_get_cached_analysis_records_hit(self):
        """Should record a cache hit."""
        mock_db = AsyncMock()
        mock_food_log = MagicMock(
            food_name="Pizza",
            calories=500,
            protein_g=20,
            carbs_g=60,
            fat_g=20,
            photo_path="/photos/pizza.jpg",
            food_category="fast food",
            cuisine_origin="Italian",
            cat_roast="Yum yum.",
        )
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_food_log

        initial_hits = cache_stats.hits

        with patch("src.llm.cache.embedding_service.embed_text") as mock_embed:
            mock_embed.return_value = [0.0] * 384

            await SemanticCache.get_cached_analysis(mock_db, "pizza")

            # Should have recorded a hit
            assert cache_stats.hits == initial_hits + 1

    @pytest.mark.asyncio
    async def test_get_cached_analysis_handles_empty_description(self):
        """Should return None for empty descriptions."""
        mock_db = AsyncMock()

        result = await SemanticCache.get_cached_analysis(mock_db, "")

        assert result is None
        # Should not have called the database
        assert not mock_db.execute.called

    @pytest.mark.asyncio
    async def test_cache_analysis_updates_embedding(self):
        """Should embed food and update FoodLog record."""
        mock_db = AsyncMock()
        mock_food_log = MagicMock(food_name="Pizza")
        mock_db.execute.return_value.scalar_one_or_none.return_value = mock_food_log

        with patch("src.llm.cache.embedding_service.embed_text") as mock_embed:
            mock_embed.return_value = [0.1, 0.2, 0.3]

            await SemanticCache.cache_analysis(mock_db, "pizza photo", food_log_id=123)

            # Should have embedded the description
            mock_embed.assert_called_once_with("pizza photo")
            # Should have set embedding on the food log
            assert mock_food_log.embedding == [0.1, 0.2, 0.3]
            # Should have committed
            assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_cache_analysis_handles_missing_log(self):
        """Should handle case where food log doesn't exist."""
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        with patch("src.llm.cache.embedding_service.embed_text") as mock_embed:
            mock_embed.return_value = [0.0] * 384

            # Should not raise
            await SemanticCache.cache_analysis(mock_db, "pizza", food_log_id=999)

            # Should have embedded
            mock_embed.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_analysis_handles_empty_description(self):
        """Should handle empty descriptions gracefully."""
        mock_db = AsyncMock()

        await SemanticCache.cache_analysis(mock_db, "", food_log_id=123)

        # Should not have called embedding service
        assert not mock_db.execute.called


class TestCacheStats:
    """Test cache statistics tracking."""

    def test_initial_stats(self):
        """Initial cache stats should be zero."""
        stats = CacheStats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.hit_rate == 0.0

    def test_record_hit(self):
        """Recording a hit should increment hit count."""
        stats = CacheStats()
        stats.record_hit()
        assert stats.hits == 1
        assert stats.misses == 0

    def test_record_miss(self):
        """Recording a miss should increment miss count."""
        stats = CacheStats()
        stats.record_miss()
        assert stats.hits == 0
        assert stats.misses == 1

    def test_hit_rate_calculation(self):
        """Hit rate should be hits / (hits + misses)."""
        stats = CacheStats()
        stats.record_hit()
        stats.record_hit()
        stats.record_miss()
        assert stats.hit_rate == 2 / 3

    def test_hit_rate_edge_cases(self):
        """Hit rate should handle edge cases."""
        stats = CacheStats()
        # No requests yet
        assert stats.hit_rate == 0.0

        # All hits
        stats.record_hit()
        stats.record_hit()
        assert stats.hit_rate == 1.0

        # All misses
        stats2 = CacheStats()
        stats2.record_miss()
        stats2.record_miss()
        assert stats2.hit_rate == 0.0

    def test_stats_string_representation(self):
        """Stats should have readable string representation."""
        stats = CacheStats()
        stats.record_hit()
        stats.record_hit()
        stats.record_miss()
        stats_str = str(stats)
        assert "hits=2" in stats_str
        assert "misses=1" in stats_str
        assert "66.67%" in stats_str or "66.67" in stats_str

    def test_multiple_operations(self):
        """Stats should correctly track multiple operations."""
        stats = CacheStats()
        # Simulate 100 requests: 75 hits, 25 misses
        for _ in range(75):
            stats.record_hit()
        for _ in range(25):
            stats.record_miss()

        assert stats.hits == 75
        assert stats.misses == 25
        assert stats.hit_rate == 0.75
