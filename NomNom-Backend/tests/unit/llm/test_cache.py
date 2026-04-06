"""
Tests for semantic caching.
"""

import pytest

from src.llm.cache import CacheStats, SemanticCache
from src.schemas.food_log import FoodAnalysisResponse


class TestSemanticCache:
    """Test semantic cache interface."""

    @pytest.mark.asyncio
    async def test_cache_miss_returns_none(self):
        """Cache should return None when no cached result exists."""
        result = await SemanticCache.get_cached_analysis("pizza")
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_analysis_doesnt_crash(self):
        """Caching an analysis should not raise errors."""
        analysis = FoodAnalysisResponse(
            food_name="Pizza",
            calories=500,
            protein_g=20,
            carbs_g=60,
            fat_g=20,
            food_category="fast food",
            cuisine_origin="Italian",
            cat_roast="Classic.",
        )
        # Should not raise
        await SemanticCache.cache_analysis("pizza photo", analysis)

    def test_similarity_threshold_is_reasonable(self):
        """Similarity threshold should be between 0 and 1."""
        assert 0 <= SemanticCache.SIMILARITY_THRESHOLD <= 1
        # Higher threshold = fewer false positives
        assert SemanticCache.SIMILARITY_THRESHOLD > 0.9


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
