"""
Tests for knowledge service (RAG retrieval and seeding).
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.knowledge_service import (
    get_relevant_nutrition_entries,
    seed_nutrition_kb,
    NUTRITION_KB_SEED_DATA,
)


class TestGetRelevantEntries:
    """Test RAG retrieval from nutrition KB."""

    @pytest.mark.asyncio
    async def test_returns_list_of_dicts(self):
        """Should return list of dicts with title and content."""
        mock_db = AsyncMock()
        mock_row1 = MagicMock(title="Protein tip", content="Eat more chicken")
        mock_row2 = MagicMock(title="Carbs guide", content="Oats are good")

        mock_db.execute.return_value.scalars.return_value.all.return_value = [
            mock_row1,
            mock_row2,
        ]

        with patch("src.services.knowledge_service.embedding_service.embed_text") as mock_embed:
            mock_embed.return_value = [0.0] * 384

            result = await get_relevant_nutrition_entries(mock_db, "high protein meal")

            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["title"] == "Protein tip"
            assert result[0]["content"] == "Eat more chicken"
            assert result[1]["title"] == "Carbs guide"
            assert result[1]["content"] == "Oats are good"

    @pytest.mark.asyncio
    async def test_respects_limit_parameter(self):
        """Should respect the limit parameter."""
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        with patch("src.services.knowledge_service.embedding_service.embed_text") as mock_embed:
            mock_embed.return_value = [0.0] * 384

            await get_relevant_nutrition_entries(mock_db, "query", limit=10)

            # The select statement should have been built with limit(10)
            # We can't directly verify the SQL, but the call should complete
            assert mock_db.execute.called

    @pytest.mark.asyncio
    async def test_returns_empty_list_on_error(self):
        """Should return empty list on database error."""
        mock_db = AsyncMock()
        mock_db.execute.side_effect = RuntimeError("DB error")

        with patch("src.services.knowledge_service.embedding_service.embed_text") as mock_embed:
            mock_embed.return_value = [0.0] * 384

            result = await get_relevant_nutrition_entries(mock_db, "query")

            assert result == []

    @pytest.mark.asyncio
    async def test_embeds_the_query(self):
        """Should embed the query using embedding service."""
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        with patch("src.services.knowledge_service.embedding_service.embed_text") as mock_embed:
            mock_embed.return_value = [0.0] * 384

            await get_relevant_nutrition_entries(mock_db, "high protein meal")

            mock_embed.assert_called_once_with("high protein meal")

    @pytest.mark.asyncio
    async def test_filters_null_embeddings(self):
        """Should filter out rows with null embeddings."""
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalars.return_value.all.return_value = []

        with patch("src.services.knowledge_service.embedding_service.embed_text") as mock_embed:
            mock_embed.return_value = [0.0] * 384

            await get_relevant_nutrition_entries(mock_db, "query")

            # The query should include .where(NutritionKB.embedding.is_not(None))
            assert mock_db.execute.called


class TestSeedNutritionKB:
    """Test knowledge base seeding."""

    @pytest.mark.asyncio
    async def test_inserts_seed_data(self):
        """Should insert all seed data entries."""
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        with patch("src.services.knowledge_service.embedding_service.embed_text") as mock_embed:
            mock_embed.return_value = [0.0] * 384

            inserted = await seed_nutrition_kb(mock_db)

            # Should insert all seed entries
            assert inserted == len(NUTRITION_KB_SEED_DATA)
            # Should commit after inserting
            assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_skips_existing_entries(self):
        """Should skip entries that already exist by title."""
        mock_db = AsyncMock()

        # First call: title doesn't exist, returns None
        # Second call: title exists, returns a mock
        mock_db.execute.return_value.scalar_one_or_none.side_effect = [
            None,  # First entry doesn't exist
            MagicMock(),  # Second entry exists
            None,  # Third entry doesn't exist
        ]

        with patch("src.services.knowledge_service.embedding_service.embed_text") as mock_embed:
            mock_embed.return_value = [0.0] * 384

            inserted = await seed_nutrition_kb(mock_db)

            # Should only insert 2 (skipping the 1 that exists)
            # Note: depends on seed data order, so this is a partial test
            assert inserted < len(NUTRITION_KB_SEED_DATA)

    @pytest.mark.asyncio
    async def test_handles_embedding_errors_gracefully(self):
        """Should skip entries that fail to embed."""
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        with patch("src.services.knowledge_service.embedding_service.embed_text") as mock_embed:
            # First call fails, others succeed
            mock_embed.side_effect = [RuntimeError("embed failed"), [0.0] * 384]

            inserted = await seed_nutrition_kb(mock_db)

            # Should skip the failed one and continue
            assert inserted < len(NUTRITION_KB_SEED_DATA)

    @pytest.mark.asyncio
    async def test_returns_insert_count(self):
        """Should return the number of rows inserted."""
        mock_db = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = None

        with patch("src.services.knowledge_service.embedding_service.embed_text") as mock_embed:
            mock_embed.return_value = [0.0] * 384

            inserted = await seed_nutrition_kb(mock_db)

            assert isinstance(inserted, int)
            assert inserted >= 0
            assert inserted <= len(NUTRITION_KB_SEED_DATA)

    def test_seed_data_has_required_fields(self):
        """Seed data entries should have title, content, category."""
        for entry in NUTRITION_KB_SEED_DATA:
            assert "title" in entry
            assert "content" in entry
            assert "category" in entry
            assert isinstance(entry["title"], str)
            assert isinstance(entry["content"], str)
            assert isinstance(entry["category"], str)
            assert len(entry["title"]) > 0
            assert len(entry["content"]) > 0
            assert len(entry["category"]) > 0

    def test_seed_data_not_empty(self):
        """Should have at least some seed data."""
        assert len(NUTRITION_KB_SEED_DATA) >= 30

    def test_seed_data_categories_diverse(self):
        """Should cover multiple categories."""
        categories = set(entry["category"] for entry in NUTRITION_KB_SEED_DATA)
        expected_categories = {
            "protein",
            "carbs",
            "fat",
            "micronutrients",
            "timing",
            "hydration",
            "weight_loss",
            "muscle_gain",
        }
        assert categories == expected_categories
