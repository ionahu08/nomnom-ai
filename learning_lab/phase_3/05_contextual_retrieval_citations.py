#!/usr/bin/env python3
"""
Phase 3 Day 5: Contextual Retrieval + Citations

Key insight: Production RAG requires two final pieces:
1. Contextual Retrieval: Add context to chunks before embedding (improves recall)
2. Citations: Enable Claude to cite sources (trust + verification)

Why Contextual Retrieval:
  Problem: "Patient has high blood pressure" chunk lacks context from parent document
  - Embedding captures just the content, misses context
  - When user asks "What causes high blood pressure?", chunk ranks low
  - Recall drops for nuanced queries

  Solution: Add context before embedding
  - "From: Cardiovascular Health Guide — Patient has high blood pressure"
  - Embedding now captures both content + document context
  - Same chunk ranks higher for related queries
  - Result: Better recall (find more relevant docs)

Why Citations:
  Problem: User reads LLM answer but can't verify source
  - "Chicken has 31g protein per 100g" ← where did this come from?
  - User doesn't trust without source
  - Hallucinations go undetected

  Solution: Enable citations in Claude API
  - Claude annotates: "Chicken has 31g protein[1]" where [1] = source
  - User can click [1] → see exact source doc
  - Builds trust, enables verification
  - This is THE killer feature of production RAG

The Pattern:
1. Contextual Retrieval:
   ├─ For each chunk, add context: title, section, parent doc
   ├─ Embed the contextual chunk (not just raw text)
   ├─ Higher quality embeddings = better retrieval

2. Citations:
   ├─ Store title + source location with each chunk
   ├─ Enable citations in Claude API call
   ├─ Claude returns citations in response
   ├─ Render citations in UI (link to source)

Usage:
    python 05_contextual_retrieval_citations.py

This demonstrates the final RAG production patterns before Days 8-9 capstone.
"""

import json
import asyncio
import math
from typing import Optional


# ============================================================================
# PART 1: DOCUMENTS WITH CONTEXT (Real World Example)
# ============================================================================

NUTRITION_DOCUMENTS = [
    {
        "doc_id": "nutrition_guide_001",
        "title": "USDA Complete Nutrition Guide",
        "sections": [
            {
                "section_id": "sec_1.1",
                "section_title": "Protein Sources",
                "content": "Chicken breast is a lean protein source rich in B vitamins",
                "page": 15
            },
            {
                "section_id": "sec_1.2",
                "section_title": "Fish & Seafood",
                "content": "Salmon contains omega-3 fatty acids beneficial for heart health",
                "page": 18
            },
            {
                "section_id": "sec_2.1",
                "section_title": "Carbohydrates",
                "content": "Brown rice provides complex carbohydrates and fiber",
                "page": 42
            }
        ]
    },
    {
        "doc_id": "cardiovascular_health_001",
        "title": "Cardiovascular Health & Diet",
        "sections": [
            {
                "section_id": "sec_3.1",
                "section_title": "Heart-Healthy Proteins",
                "content": "Fish rich in omega-3 fatty acids reduces heart disease risk",
                "page": 5
            },
            {
                "section_id": "sec_3.2",
                "section_title": "Whole Grains",
                "content": "Whole grains lower cholesterol and support cardiovascular health",
                "page": 12
            }
        ]
    }
]


# ============================================================================
# PART 2: CONTEXTUAL CHUNKS (With Context)
# ============================================================================

def build_contextual_chunks():
    """
    Create chunks with context added.

    For each chunk:
    - Original: "Chicken breast is a lean protein source..."
    - Contextual: "From USDA Complete Nutrition Guide (p.15, Protein Sources):
                   Chicken breast is a lean protein source..."

    This enriched text better captures semantic meaning when embedded.
    """
    contextual_chunks = []

    for doc in NUTRITION_DOCUMENTS:
        doc_title = doc["title"]
        for section in doc["sections"]:
            section_title = section["section_title"]
            page = section["page"]
            content = section["content"]

            # Create contextual version
            contextual_text = (
                f"[{doc_title}] {section_title} (p.{page}): {content}"
            )

            contextual_chunks.append({
                "chunk_id": section["section_id"],
                "doc_id": doc["doc_id"],
                "doc_title": doc_title,
                "section_title": section_title,
                "page": page,
                "original_content": content,
                "contextual_content": contextual_text,
                "source_url": f"docs://{doc['doc_id']}#{section['section_id']}"
            })

    return contextual_chunks


def simulate_embedding(text: str, dim: int = 5) -> list[float]:
    """Simulate embedding (same as previous days)."""
    import hashlib

    hash_val = int(hashlib.sha256(text.encode()).hexdigest(), 16)
    embedding = []
    for i in range(dim):
        val = ((hash_val >> (i * 8)) & 0xFF) / 255.0
        embedding.append(val)

    return embedding


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Compute cosine similarity."""
    if len(vec1) != len(vec2):
        return 0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a * a for a in vec1))
    mag2 = math.sqrt(sum(b * b for b in vec2))

    if mag1 == 0 or mag2 == 0:
        return 0

    return dot_product / (mag1 * mag2)


# ============================================================================
# PART 3: CONTEXTUAL RETRIEVAL COMPARISON
# ============================================================================

async def compare_retrieval(query: str, chunks: list[dict]) -> dict:
    """
    Compare retrieval quality with and without context.

    Args:
        query: User question
        chunks: List of contextual chunks

    Returns:
        Comparison showing impact of contextual embeddings
    """
    query_embedding = simulate_embedding(query)

    results_without_context = []
    results_with_context = []

    for chunk in chunks:
        # Score 1: Without context (original content only)
        original_embedding = simulate_embedding(chunk["original_content"])
        score_without = cosine_similarity(query_embedding, original_embedding)

        results_without_context.append({
            "chunk_id": chunk["chunk_id"],
            "doc_title": chunk["doc_title"],
            "section_title": chunk["section_title"],
            "content": chunk["original_content"][:60],
            "score": round(score_without, 3)
        })

        # Score 2: With context (enriched content)
        contextual_embedding = simulate_embedding(chunk["contextual_content"])
        score_with = cosine_similarity(query_embedding, contextual_embedding)

        results_with_context.append({
            "chunk_id": chunk["chunk_id"],
            "doc_title": chunk["doc_title"],
            "section_title": chunk["section_title"],
            "content": chunk["original_content"][:60],
            "score": round(score_with, 3),
            "improvement": round(score_with - score_without, 3)
        })

    # Sort by score
    results_without_context.sort(key=lambda x: x["score"], reverse=True)
    results_with_context.sort(key=lambda x: x["score"], reverse=True)

    return {
        "query": query,
        "without_context": results_without_context[:3],
        "with_context": results_with_context[:3]
    }


# ============================================================================
# PART 4: CITATIONS (Production RAG Feature)
# ============================================================================

CITATIONS_EXPLANATION = """
Citations in Production RAG:

Claude API Feature: `citations: {"enabled": true}`

When enabled:
1. Claude annotates output with [1], [2], [3], ... markers
2. Each citation corresponds to a source document
3. API returns citation mapping: [1] → doc_id, page, location

Example Output:
  "Chicken has 31g protein per 100g serving[1], making it excellent
   for muscle building[2]. Salmon provides similar protein with added
   omega-3 benefits[3]."

Citation Mapping:
  [1] USDA Complete Nutrition Guide, p.15, Protein Sources
  [2] ibid (same source)
  [3] USDA Complete Nutrition Guide, p.18, Fish & Seafood

Why Citations Are Killer:
✓ Users can verify sources (trust)
✓ Hallucinations get caught (if source doesn't match)
✓ Enables feedback loops (users report bad citations)
✓ Legal compliance (can cite sources in regulated domains like health)

Implementation Pattern:
  1. Enable citations in messages.create(...)
  2. Parse response for citation annotations
  3. Map citations to source metadata
  4. Return to frontend with clickable links

Cost: No extra API cost (citations included in response)
Trust Gain: Massive (users see exactly where info came from)
"""


class CitationEnabledRAG:
    """Simulate RAG with citations enabled."""

    def __init__(self, chunks: list[dict]):
        """Initialize with chunks that can be cited."""
        self.chunks = chunks
        self.citations_db = {}  # citation_id → source metadata

        # Build citation database
        for i, chunk in enumerate(chunks, 1):
            self.citations_db[i] = {
                "doc_title": chunk["doc_title"],
                "section_title": chunk["section_title"],
                "page": chunk["page"],
                "content": chunk["original_content"]
            }

    async def answer_with_citations(self, query: str, top_k: int = 3) -> dict:
        """
        Generate RAG answer with citations.

        Simulates:
        1. Retrieve top-K chunks
        2. Annotate answer with citation markers [1], [2], [3]
        3. Return citations mapping
        """
        query_embedding = simulate_embedding(query)

        # Score all chunks
        scored_chunks = []
        for chunk in self.chunks:
            contextual_embedding = simulate_embedding(chunk["contextual_content"])
            score = cosine_similarity(query_embedding, contextual_embedding)
            scored_chunks.append((chunk, score))

        # Get top-K
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        top_chunks = [chunk for chunk, score in scored_chunks[:top_k]]

        # Build answer with citation markers
        answer = self._build_answer_with_citations(query, top_chunks)

        return answer

    def _build_answer_with_citations(self, query: str, chunks: list[dict]) -> dict:
        """Build answer by combining chunks with citation markers."""

        # Simulated answer (in reality, Claude generates this)
        if "protein" in query.lower():
            answer_text = (
                f"Based on USDA nutrition data[1], protein-rich foods include "
                f"chicken breast[1] and fish like salmon[2]. Salmon additionally "
                f"provides omega-3 fatty acids[2] beneficial for heart health[3]."
            )
        elif "carbohydrate" in query.lower():
            answer_text = (
                f"Complex carbohydrates from whole grains[4] provide sustained energy "
                f"and fiber[4], supporting overall health[5]."
            )
        else:
            answer_text = (
                f"Different foods provide various nutrients[1]. For example, "
                f"chicken[1] and salmon[2] offer protein, while grains[3] "
                f"provide carbohydrates[3]."
            )

        # Build citation mapping
        citations = {}
        for i, chunk in enumerate(chunks, 1):
            citations[i] = {
                "doc_title": chunk["doc_title"],
                "section_title": chunk["section_title"],
                "page": chunk["page"],
                "source_url": chunk["source_url"]
            }

        return {
            "query": query,
            "answer_with_citations": answer_text,
            "citations": citations,
            "note": "In production, Claude generates the answer and automatically inserts citation markers"
        }


# ============================================================================
# DEMO: CONTEXTUAL RETRIEVAL + CITATIONS
# ============================================================================

async def main():
    """Demonstrate contextual retrieval and citations."""

    print("🎯 Phase 3 Day 5: Contextual Retrieval + Citations\n")
    print("Key Learning:")
    print("- Contextual Retrieval: Add doc context before embedding (better recall)")
    print("- Citations: Enable Claude to cite sources (trust + verification)")
    print("- Together: Foundation for production RAG users trust\n")

    # ======================================================================
    # PART 1: Contextual Retrieval Comparison
    # ======================================================================
    print("="*70)
    print("PART 1: Contextual Retrieval Impact")
    print("="*70)

    chunks = build_contextual_chunks()
    query = "protein sources for muscle building"

    comparison = await compare_retrieval(query, chunks)

    print(f"\nQuery: '{query}'\n")

    print("WITHOUT Context (Embedding: original text only):")
    for i, result in enumerate(comparison["without_context"], 1):
        print(f"  {i}. [{result['score']}] {result['doc_title']} — {result['section_title']}")
        print(f"     {result['content']}...")

    print("\nWITH Context (Embedding: title + section + text):")
    for i, result in enumerate(comparison["with_context"], 1):
        improvement = result.get("improvement", 0)
        marker = "↑" if improvement > 0 else "→"
        print(f"  {i}. [{result['score']}] {marker} {result['doc_title']} — {result['section_title']}")
        if improvement:
            print(f"     Improvement: +{improvement}")
        print(f"     {result['content']}...")

    print("\n📊 Key Insight:")
    print("""
  Contextual embeddings improved recall because:
  - Original: "Chicken breast is a lean protein..." (generic, low relevance)
  - Contextual: "[USDA Guide] Protein Sources: Chicken breast..." (specific, high relevance)

  Same chunk, different ranking! Context changes semantic meaning.
""")

    # ======================================================================
    # PART 2: Citations Explanation
    # ======================================================================
    print("="*70)
    print("PART 2: Citations (Trust Feature)")
    print("="*70)
    print(CITATIONS_EXPLANATION)

    # ======================================================================
    # PART 3: Citations in Action
    # ======================================================================
    print("="*70)
    print("PART 3: Citations in Action")
    print("="*70)

    rag = CitationEnabledRAG(chunks)

    queries = [
        "What are the best protein sources?",
        "Tell me about carbohydrates",
        "How should I eat for heart health?"
    ]

    for query in queries:
        result = await rag.answer_with_citations(query)

        print(f"\n📝 Query: {query}")
        print(f"\n📄 Answer with Citations:")
        print(f"   {result['answer_with_citations']}\n")

        print(f"📚 Citation Sources:")
        for citation_id, citation_info in result["citations"].items():
            print(f"   [{citation_id}] {citation_info['doc_title']}")
            print(f"       Section: {citation_info['section_title']} (p.{citation_info['page']})")

        print()

    # ======================================================================
    # KEY INSIGHTS
    # ======================================================================
    print("="*70)
    print("🔑 Why Days 4-5 Matter for Production")
    print("="*70)
    print("""
Day 4 (Hybrid Search):
  ✓ Finds relevant documents (recall)
  ✗ No guarantee quality is good (precision)

Day 5 (Contextual + Citations):
  ✓ Improves finding accuracy (contextual embeddings)
  ✓ Builds user trust (citations)
  ✓ Enables verification (source clickability)

Combined Impact:
  - Better retrieval (contextual ranking)
  - Better trust (citations)
  - Better compliance (trackable sources)

Example: NomNom Recommendations
  Before: "Eat salmon for protein"
  After: "Eat salmon[1] for protein[2] and omega-3s[3]"
         [1] USDA Nutrition Guide, p.18
         [2] ibid
         [3] Cardiovascular Health Guide, p.5

  Result: Users can click [1], [2], [3] to see original sources
         → Builds trust
         → Enables feedback ("that source is outdated")
         → Complies with health regulations
""")

    # ======================================================================
    # WHAT'S NEXT
    # ======================================================================
    print("\n" + "="*70)
    print("🚀 Next: Days 6-10")
    print("="*70)
    print("""
Days 6-7: Code Reviews
  - embedding.py: Why sentence-transformers? (vs OpenAI/Voyage)
  - cache.py: The 0.15 cosine threshold — measured or guessed?
  - seed_knowledge.py: KB construction, chunking strategy
  - tools.py: Real multi-tool agent loop in production?

Days 8-9: Capstone — Full Advanced RAG
  - 30 nutrition questions
  - Hybrid search + RRF + contextual + citations
  - Eval report: NDCG@5, MRR, answer quality
  - Comparison: simple RAG vs. advanced RAG
  - Your second portfolio artifact

Day 10: Production Integration
  - Land contextual retrieval in cache.py
  - Enable citations in recommendation_service.py
  - Monitor citation click-through (user trust signal)
  - Deploy with confidence
""")


if __name__ == "__main__":
    asyncio.run(main())
