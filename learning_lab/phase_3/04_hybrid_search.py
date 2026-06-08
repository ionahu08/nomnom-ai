#!/usr/bin/env python3
"""
Phase 3 Day 4: BM25 + Hybrid Search + RRF + Reranking

Key insight: Combine semantic search (dense) + keyword search (sparse)
for better recall. Merge rankings with RRF. Rerank with LLM.

Why Hybrid Search:
- Vector search: Finds "grilled chicken salad" for query "cooked poultry dish"
  ✓ Great semantic understanding, ✗ Misses exact keyword matches
- BM25 search: Finds "chicken with rice" for query "rice protein"
  ✓ Keyword precision, ✗ Misses synonyms
- Hybrid: Combines both, best of both worlds

Your RecSys Background:
RRF is the exact "multi-channel ranking" pattern from recommender systems:
- Channel 1: Semantic relevance (from embeddings)
- Channel 2: Keyword frequency (from BM25)
- Fusion: RRF merges signals without weights (robust to outliers)

The Pattern:
1. BM25 Index: Inverted index of terms (fast keyword search)
2. Vector Index: Embeddings stored for similarity (semantic search)
3. Query: Run on both indexes, get 2 result lists
4. RRF: Merge rankings using reciprocal formula
5. Reranking: Use LLM to reorder top-K results

Usage:
    python 04_hybrid_search.py

This script demonstrates the complete hybrid RAG pipeline.
Days 8-9 capstone will implement this at scale with citations.
"""

import json
import asyncio
import math
from collections import defaultdict


# ============================================================================
# PART 1: BM25 INDEX (Keyword-Based Search)
# ============================================================================

class BM25Index:
    """
    BM25 (Best Matching 25) — TF-IDF based ranking for keyword search.

    Algorithm:
    - Build inverted index (term → documents)
    - Score documents based on term frequency + IDF
    - BM25 formula: score = IDF(q_i) * (f(q_i, D) * (k1 + 1)) / (f(q_i, D) + k1 * (1 - b + b * |D| / avgdl))

    Why BM25:
    - Industry standard for full-text search
    - Handles term frequency saturation (doesn't overweight high frequencies)
    - Language-agnostic (works with any tokenization)
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 index.

        Args:
            k1: Term frequency saturation (default 1.5)
            b: Document length normalization (default 0.75)
        """
        self.k1 = k1
        self.b = b
        self.inverted_index = defaultdict(list)  # term → [(doc_id, frequency)]
        self.doc_lengths = {}  # doc_id → length
        self.doc_vectors = {}  # doc_id → document text
        self.idf = {}  # term → IDF value
        self.avg_doc_len = 0

    def add_document(self, doc_id: str, text: str):
        """Add a document to the BM25 index."""
        self.doc_vectors[doc_id] = text

        # Tokenize (simple: lowercase + split)
        tokens = text.lower().split()
        self.doc_lengths[doc_id] = len(tokens)

        # Count term frequencies
        term_freq = defaultdict(int)
        for token in tokens:
            term_freq[token] += 1

        # Build inverted index
        for term, freq in term_freq.items():
            self.inverted_index[term].append((doc_id, freq))

    def build(self):
        """Finalize the index (compute IDF and avg doc length)."""
        total_docs = len(self.doc_vectors)
        self.avg_doc_len = sum(self.doc_lengths.values()) / total_docs if total_docs > 0 else 0

        # Compute IDF for each term
        for term, postings in self.inverted_index.items():
            doc_freq = len(postings)
            # BM25 IDF: log((N - df + 0.5) / (df + 0.5))
            self.idf[term] = math.log((total_docs - doc_freq + 0.5) / (doc_freq + 0.5) + 1)

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        """
        Search for documents matching the query.

        Args:
            query: Search query
            top_k: Return top K results

        Returns:
            List of {doc_id, score, text} ranked by BM25 score
        """
        query_tokens = query.lower().split()

        # Score each document
        scores = defaultdict(float)

        for token in query_tokens:
            if token not in self.inverted_index:
                continue

            idf = self.idf.get(token, 0)

            for doc_id, freq in self.inverted_index[token]:
                doc_len = self.doc_lengths[doc_id]

                # BM25 formula
                numerator = idf * freq * (self.k1 + 1)
                denominator = freq + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_len))
                scores[doc_id] += numerator / denominator

        # Rank and return top K
        ranked = sorted(
            [(doc_id, score) for doc_id, score in scores.items()],
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {
                "doc_id": doc_id,
                "score": round(score, 3),
                "text": self.doc_vectors[doc_id],
                "rank": i + 1
            }
            for i, (doc_id, score) in enumerate(ranked[:top_k])
        ]


# ============================================================================
# PART 2: VECTOR INDEX (From Day 3)
# ============================================================================

def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if len(vec1) != len(vec2):
        return 0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a * a for a in vec1))
    mag2 = math.sqrt(sum(b * b for b in vec2))

    if mag1 == 0 or mag2 == 0:
        return 0

    return dot_product / (mag1 * mag2)


def simulate_embedding(text: str, dim: int = 5) -> list[float]:
    """Simulate embedding (same as Day 3)."""
    import hashlib

    hash_val = int(hashlib.sha256(text.encode()).hexdigest(), 16)
    embedding = []
    for i in range(dim):
        val = ((hash_val >> (i * 8)) & 0xFF) / 255.0
        embedding.append(val)

    return embedding


class VectorIndex:
    """Simple vector search index."""

    def __init__(self):
        self.vectors = {}  # doc_id → embedding
        self.documents = {}  # doc_id → text

    def add_document(self, doc_id: str, text: str):
        """Add document with embedding."""
        embedding = simulate_embedding(text)
        self.vectors[doc_id] = embedding
        self.documents[doc_id] = text

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        """Search by cosine similarity."""
        query_embedding = simulate_embedding(query)

        scores = []
        for doc_id, vec in self.vectors.items():
            similarity = cosine_similarity(query_embedding, vec)
            scores.append({
                "doc_id": doc_id,
                "score": round(similarity, 3),
                "text": self.documents[doc_id],
                "rank": 0  # Will be set after ranking
            })

        # Rank by score
        scores.sort(key=lambda x: x["score"], reverse=True)
        for i, result in enumerate(scores[:top_k]):
            result["rank"] = i + 1

        return scores[:top_k]


# ============================================================================
# PART 3: RRF (Reciprocal Rank Fusion)
# ============================================================================

def reciprocal_rank_fusion(
    vector_results: list[dict],
    bm25_results: list[dict],
    k: float = 60.0
) -> list[dict]:
    """
    Merge two ranked lists using RRF (Reciprocal Rank Fusion).

    Formula: RRF(d) = Σ(1 / (k + rank(d)))
    where rank(d) is the document's rank in each list (or infinity if not in list).

    Why RRF:
    - Robust: doesn't require parameter tuning (unlike weighted fusion)
    - Multi-channel: combines signals without weighting
    - Used in: modern search engines, recommendation systems

    Args:
        vector_results: Ranked list from vector search
        bm25_results: Ranked list from BM25 search
        k: RRF parameter (higher k = less weight to lower-ranked items)

    Returns:
        Fused ranking: list of {doc_id, vector_rank, bm25_rank, rrf_score}
    """
    # Build rank lookup tables
    vector_ranks = {r["doc_id"]: r["rank"] for r in vector_results}
    bm25_ranks = {r["doc_id"]: r["rank"] for r in bm25_results}

    # Collect all unique documents
    all_docs = set(vector_ranks.keys()) | set(bm25_ranks.keys())

    # Compute RRF scores
    rrf_scores = {}
    for doc_id in all_docs:
        vector_rank = vector_ranks.get(doc_id, float('inf'))
        bm25_rank = bm25_ranks.get(doc_id, float('inf'))

        # RRF formula: sum of reciprocals
        rrf_score = 0
        if vector_rank != float('inf'):
            rrf_score += 1 / (k + vector_rank)
        if bm25_rank != float('inf'):
            rrf_score += 1 / (k + bm25_rank)

        rrf_scores[doc_id] = {
            "doc_id": doc_id,
            "vector_rank": vector_rank if vector_rank != float('inf') else "—",
            "bm25_rank": bm25_rank if bm25_rank != float('inf') else "—",
            "rrf_score": round(rrf_score, 4)
        }

    # Rank by RRF score
    ranked = sorted(rrf_scores.values(), key=lambda x: x["rrf_score"], reverse=True)
    return ranked


# ============================================================================
# PART 4: DEMO
# ============================================================================

async def main():
    """Demonstrate hybrid search with RRF and reranking."""

    print("🎯 Phase 3 Day 4: BM25 + Hybrid Search + RRF + Reranking\n")
    print("Key Learning:")
    print("- BM25: Keyword-based (sparse) search")
    print("- Vector Search: Semantic (dense) search")
    print("- RRF: Merge rankings using reciprocal formula (RecSys pattern)")
    print("- Reranking: LLM reorders top results")
    print()

    # ======================================================================
    # Step 1: Index Documents
    # ======================================================================
    print("="*70)
    print("Step 1: Build BM25 + Vector Indexes")
    print("="*70)

    documents = [
        ("doc1", "Chicken breast is a lean protein source rich in B vitamins"),
        ("doc2", "Salmon contains omega-3 fatty acids beneficial for heart health"),
        ("doc3", "Brown rice provides complex carbohydrates and fiber"),
        ("doc4", "Eggs are an excellent source of complete protein and choline"),
        ("doc5", "Broccoli is a cruciferous vegetable high in vitamin C"),
    ]

    # BM25 Index
    bm25_index = BM25Index()
    for doc_id, text in documents:
        bm25_index.add_document(doc_id, text)
    bm25_index.build()

    # Vector Index
    vector_index = VectorIndex()
    for doc_id, text in documents:
        vector_index.add_document(doc_id, text)

    print(f"✅ Indexed {len(documents)} documents\n")

    # ======================================================================
    # Step 2: Search with Both Indexes
    # ======================================================================
    print("="*70)
    print("Step 2: Hybrid Search (Vector + BM25)")
    print("="*70)

    query = "protein rich food healthy"
    print(f"\nQuery: '{query}'\n")

    # Vector search
    vector_results = vector_index.search(query, top_k=5)
    print("Vector Search Results (Semantic):")
    for result in vector_results:
        print(f"  Rank {result['rank']}: {result['doc_id']} (score: {result['score']})")
        print(f"           {result['text'][:60]}...")

    # BM25 search
    bm25_results = bm25_index.search(query, top_k=5)
    print("\nBM25 Search Results (Keyword):")
    for result in bm25_results:
        print(f"  Rank {result['rank']}: {result['doc_id']} (score: {result['score']})")
        print(f"           {result['text'][:60]}...")

    # ======================================================================
    # Step 3: RRF Fusion
    # ======================================================================
    print("\n" + "="*70)
    print("Step 3: RRF Fusion (Merge Rankings)")
    print("="*70)

    fused_ranking = reciprocal_rank_fusion(vector_results, bm25_results, k=60.0)

    print("\nRRF Fused Ranking:")
    print(f"{'Rank':<6} {'Doc ID':<8} {'Vector':<8} {'BM25':<8} {'RRF Score':<10} {'Text':<40}")
    print("-" * 80)

    for i, result in enumerate(fused_ranking[:5], 1):
        vector_rank = str(result['vector_rank'])
        bm25_rank = str(result['bm25_rank'])
        doc_id = result['doc_id']

        # Get text
        text = next((doc[1] for doc in documents if doc[0] == doc_id), "")[:40]

        print(f"{i:<6} {doc_id:<8} {vector_rank:<8} {bm25_rank:<8} {result['rrf_score']:<10} {text:<40}")

    # ======================================================================
    # Step 4: LLM Reranking
    # ======================================================================
    print("\n" + "="*70)
    print("Step 4: LLM Reranking (Top-10 → Top-3)")
    print("="*70)

    print("""
LLM Reranking Process (simulated):

Input: Top 10 results from RRF
Prompt: "Given these 10 nutrition documents and the query '{query}',
         which 3 are most relevant? Consider:
         - Direct answer to the query
         - Nutritional completeness
         - Practical usefulness"

Output: Reranked top-3 with LLM reasoning

This is different from simple ranking because:
✓ Considers query intent, not just keyword/semantic match
✓ Can catch edge cases (e.g., "protein supplement" beats "chicken" for some queries)
✓ Enables multi-stage ranking (recall → precision pipeline)

Tradeoff: LLM reranking costs ~$0.001 per query (Haiku)
When to use: High-stakes queries or when precision matters
""")

    # ======================================================================
    # Comparison: Simple RAG vs Hybrid RAG
    # ======================================================================
    print("\n" + "="*70)
    print("Comparison: Day 3 (Simple) vs Day 4 (Hybrid)")
    print("="*70)

    comparison = """
Scenario: User asks "What has protein and healthy fats?"

Day 3 (Vector Search Only):
  - Query embedding: [0.45, 0.62, 0.18, ...]
  - Retrieves: doc2 (salmon, high semantic match)
  - Miss: doc4 (eggs) — has protein+fat but different keywords

Day 4 (Hybrid + RRF):
  - Vector search: doc2 (salmon) ranks #1
  - BM25 search: doc4 (eggs) ranks #1 (keyword match: "source protein")
  - RRF fusion: doc2=0.0167, doc4=0.0167 (tied, both important!)
  - Result: Both returned, user gets complete answer

Cost/Benefit:
  Day 3: Fast, cheap, good for semantic synonyms
  Day 4: Slower, more expensive, better for mixed intent queries

Your Next Challenge (Days 8-9):
  Implement at scale with 10,000+ foods
  Add citations so users know where info came from
  Measure NDCG@5 (ranking quality metric from IR)
"""

    print(comparison)


if __name__ == "__main__":
    asyncio.run(main())
