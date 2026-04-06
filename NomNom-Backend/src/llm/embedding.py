"""
Embedding Service — Generate vector embeddings for semantic search.

Uses sentence-transformers (all-MiniLM-L6-v2) for local, free embeddings.
No external API calls, works offline.

Dimension: 384
Model: sentence-transformers/all-MiniLM-L6-v2 (~90 MB, cached after first use)
"""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 384


class EmbeddingService:
    """Generate embeddings using sentence-transformers."""

    def __init__(self):
        """Initialize service with lazy model loading."""
        self._model: Optional["SentenceTransformer"] = None

    def _load_model(self) -> "SentenceTransformer":
        """Lazy-load the embedding model (only once per process)."""
        if self._model is None:
            logger.info("Loading sentence-transformers model (all-MiniLM-L6-v2)...")
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info(f"Model loaded. Embedding dimension: {EMBEDDING_DIM}")
            except ImportError:
                logger.error("sentence-transformers not installed")
                raise
        return self._model

    async def embed_text(self, text: str) -> list[float]:
        """
        Embed a text string to a vector.

        Args:
            text: The text to embed

        Returns:
            List of floats (embedding vector)
        """
        if not text or not text.strip():
            logger.warning("Empty text passed to embed_text")
            return [0.0] * EMBEDDING_DIM

        # Get event loop and run model inference in executor
        # (synchronous encode() doesn't block async handlers)
        loop = asyncio.get_event_loop()
        model = self._load_model()

        try:
            embedding = await loop.run_in_executor(
                None,
                lambda: model.encode(text, convert_to_tensor=False),
            )
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to embed text: {e}")
            raise

    async def embed_food(
        self, food_name: str, food_category: str = ""
    ) -> list[float]:
        """
        Embed a food item (name + category).

        Combines name and category for richer semantic meaning.
        Example: "Pizza (fast food)" embeds better than "Pizza" alone.

        Args:
            food_name: Name of the food
            food_category: Category (e.g., "Protein", "Grain", "Fast Food")

        Returns:
            List of floats (embedding vector)
        """
        if food_category:
            text = f"{food_name} ({food_category})"
        else:
            text = food_name
        return await self.embed_text(text)


# Module-level singleton instance
embedding_service = EmbeddingService()
