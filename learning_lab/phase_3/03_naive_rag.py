#!/usr/bin/env python3
"""
Phase 3 Day 3: Naive RAG Pipeline (End-to-End)

Key insight: Build a complete RAG system from scratch:
1. Chunking strategies (split knowledge base into semantic pieces)
2. Embeddings (convert chunks to vectors)
3. Vector search (retrieve similar chunks via cosine similarity)
4. Augmentation (add retrieved context to LLM prompt)

Why RAG matters for NomNom:
- USDA FoodData Central has 7,700+ foods (too large for context window)
- User asks "What's nutrition in chicken?" → RAG retrieves relevant matches
- LLM answers using retrieved context + citations
- Result: accurate, sourced answers without hallucination

The Pattern:
1. Chunking: Split knowledge base into semantic pieces
2. Embedding: Convert chunks to vectors
3. Indexing: Store vectors for fast search
4. Query: User question → embed → find similar chunks (cosine similarity)
5. Augmentation: Add retrieved context to prompt
6. Generation: LLM generates answer using augmented prompt

Usage:
    python 03_naive_rag.py

This script demonstrates complete naive RAG before optimization
(Days 4+: BM25, hybrid search, RRF, reranking).
"""

import json
import asyncio
import math


# ============================================================================
# PART 1: KNOWLEDGE BASE (Simulated USDA FoodData Central)
# ============================================================================

USDA_NUTRITION_KB = [
    {
        "id": "1001",
        "food_name": "Chicken, broilers, cooked, roasted, skin removed",
        "serving_size": "100g",
        "nutrition": {
            "calories": 165,
            "protein_g": 31,
            "carbs_g": 0,
            "fat_g": 3.6,
            "saturated_fat_g": 1,
        },
        "source": "USDA FoodData Central"
    },
    {
        "id": "1002",
        "food_name": "Eggs, chicken, whole, cooked, fried",
        "serving_size": "1 large (46g)",
        "nutrition": {
            "calories": 70,
            "protein_g": 6,
            "carbs_g": 0.4,
            "fat_g": 5,
            "saturated_fat_g": 1.6,
        },
        "source": "USDA FoodData Central"
    },
    {
        "id": "1003",
        "food_name": "Rice, white, medium-grain, cooked",
        "serving_size": "1 cup (186g)",
        "nutrition": {
            "calories": 242,
            "protein_g": 4.3,
            "carbs_g": 53,
            "fat_g": 0.3,
            "saturated_fat_g": 0.1,
        },
        "source": "USDA FoodData Central"
    },
    {
        "id": "1004",
        "food_name": "Broccoli, cooked, boiled, drained",
        "serving_size": "1 cup (156g)",
        "nutrition": {
            "calories": 55,
            "protein_g": 3.7,
            "carbs_g": 11,
            "fat_g": 0.6,
            "saturated_fat_g": 0.1,
        },
        "source": "USDA FoodData Central"
    },
    {
        "id": "1005",
        "food_name": "Salmon, cooked, baked or broiled",
        "serving_size": "100g",
        "nutrition": {
            "calories": 206,
            "protein_g": 22,
            "carbs_g": 0,
            "fat_g": 13,
            "saturated_fat_g": 3,
        },
        "source": "USDA FoodData Central"
    },
    {
        "id": "1006",
        "food_name": "Bread, whole-wheat",
        "serving_size": "1 slice (28g)",
        "nutrition": {
            "calories": 80,
            "protein_g": 4,
            "carbs_g": 14,
            "fat_g": 1,
            "saturated_fat_g": 0.2,
        },
        "source": "USDA FoodData Central"
    },
]


# ============================================================================
# PART 2: CHUNKING STRATEGIES (Three Approaches)
# ============================================================================

def chunk_by_size(text: str, chunk_size: int = 100, overlap: int = 20) -> list[str]:
    """
    Size-based chunking with overlap.

    Strategy: Split text into fixed-size chunks with overlap to preserve context.
    Best for: Uniform content (e.g., long nutrition manuals).
    Tradeoff: Simple but may split sentences awkwardly.

    Args:
        text: Text to chunk
        chunk_size: Characters per chunk
        overlap: Characters to overlap between chunks

    Returns:
        List of overlapping chunks
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def chunk_by_structure(food_entry: dict) -> list[str]:
    """
    Structure-based chunking.

    Strategy: Split by semantic boundaries (food identity, nutrition, source).
    Best for: Structured data (nutrition labels, JSON).
    Tradeoff: Requires understanding the data format.

    Args:
        food_entry: A USDA food entry

    Returns:
        List of semantic chunks
    """
    chunks = []

    # Chunk 1: Food identity
    chunks.append(f"Food: {food_entry['food_name']}\nServing: {food_entry['serving_size']}")

    # Chunk 2: Macronutrients
    nutrition = food_entry["nutrition"]
    macros = (
        f"Nutrition facts: "
        f"{nutrition['calories']} cal, "
        f"{nutrition['protein_g']}g protein, "
        f"{nutrition['carbs_g']}g carbs, "
        f"{nutrition['fat_g']}g fat"
    )
    chunks.append(macros)

    return chunks


def chunk_by_semantic_similarity(text: str, target_chunk_size: int = 200) -> list[str]:
    """
    Semantic-based chunking (concept).

    Strategy: Split by semantic boundaries detected via LLM or sentence embeddings.
    Best for: Long documents where structure is implicit.
    Tradeoff: More expensive (requires embeddings or LLM calls).

    Example: Use Claude to identify paragraph boundaries, then split there.
    In this demo: We show the concept with manual sentence-based splitting.

    Args:
        text: Text to chunk
        target_chunk_size: Target size (characters)

    Returns:
        List of semantically coherent chunks
    """
    # Simplified: split by sentences and group into target size
    sentences = text.split('. ')
    chunks = []
    current_chunk = []
    current_size = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        sentence_size = len(sentence) + 2  # +2 for ". "
        if current_size + sentence_size > target_chunk_size and current_chunk:
            # Start new chunk
            chunks.append('. '.join(current_chunk) + '.')
            current_chunk = [sentence]
            current_size = sentence_size
        else:
            current_chunk.append(sentence)
            current_size += sentence_size

    if current_chunk:
        chunks.append('. '.join(current_chunk) + '.')

    return chunks


# ============================================================================
# PART 3: EMBEDDINGS + EMBEDDING MODEL TRADEOFFS
# ============================================================================

EMBEDDING_MODEL_COMPARISON = """
Embedding Model Tradeoffs (for NomNom):

| Model | Provider | Dimension | Speed | Cost | Quality | Use Case |
|-------|----------|-----------|-------|------|---------|----------|
| sentence-transformers/all-MiniLM-L6-v2 | Local (free) | 384 | Fast | Free | Good | NomNom choice (production) |
| OpenAI text-embedding-3-small | OpenAI API | 1536 | Medium | $0.02/M tokens | Better | When quality is critical |
| OpenAI text-embedding-3-large | OpenAI API | 3072 | Medium | $0.13/M tokens | Best | High-accuracy retrieval |
| Voyage AI voyage-large-2-instruct | Voyage API | 1024 | Medium | $0.10/M tokens | Best | Industry standard |
| BAAI/bge-small-en-v1.5 | Local (free) | 384 | Fast | Free | Good | Resource-constrained |

NomNom Decision Rationale (Phase 3):
- Use sentence-transformers/all-MiniLM-L6-v2 (local, free, good enough)
- 384 dimensions is efficient (cache cost)
- If recall degrades, upgrade to text-embedding-3-small (small cost increase)
- Save Voyage AI for enterprise version (if needed)
"""

def simulate_embedding(text: str, dim: int = 5) -> list[float]:
    """
    Simulate text embedding using hash-based vectors.

    In production: Use actual embedding models:
    - sentence-transformers (local, free, good quality)
    - OpenAI embeddings (cloud, paid, higher quality)
    - Voyage AI (cloud, paid, industry-standard)

    For learning: Hash-based simulation demonstrates the concept.

    Args:
        text: Text to embed
        dim: Embedding dimension

    Returns:
        List of floats representing the text
    """
    import hashlib

    hash_val = int(hashlib.sha256(text.encode()).hexdigest(), 16)

    # Generate dim values from hash
    embedding = []
    for i in range(dim):
        val = ((hash_val >> (i * 8)) & 0xFF) / 255.0
        embedding.append(val)

    return embedding


# ============================================================================
# PART 4: VECTOR STORE + COSINE SIMILARITY SEARCH
# ============================================================================

VECTOR_STORE_OPTIONS = """
Vector Store Concept (for RAG):

When you have millions of embeddings, you need fast retrieval. Options:

| Store | Speed | Memory | Scalability | Use Case |
|-------|-------|--------|-------------|----------|
| List (this demo) | O(n) | Low | < 10K vectors | Learning, prototypes |
| NumPy arrays | O(n) | Low-Med | < 100K vectors | Local prototypes |
| pgvector (PostgreSQL) | O(log n) | Med | 100M+ vectors | NomNom production ✅ |
| FAISS (Facebook AI) | O(log n) | Med | 1B+ vectors | Scale-up option |
| Pinecone (cloud) | O(log n) | Cloud | Unlimited | Managed service |
| Weaviate (open source) | O(log n) | Med | 100M+ vectors | Alternative to pgvector |

NomNom uses pgvector (PostgreSQL extension) because:
- Vectors stored in same database as food_logs
- No separate infrastructure
- Scales to millions of food logs
- Supports cosine distance + other metrics
"""

def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    Formula: cos(θ) = (A · B) / (||A|| × ||B||)
    Range: 0.0 (opposite) to 1.0 (identical)
    """
    if len(vec1) != len(vec2):
        return 0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a * a for a in vec1))
    mag2 = math.sqrt(sum(b * b for b in vec2))

    if mag1 == 0 or mag2 == 0:
        return 0

    return dot_product / (mag1 * mag2)


def naive_retrieve(query_embedding: list[float],
                   chunk_index: list[dict],
                   top_k: int = 3) -> list[dict]:
    """
    Retrieve top-K chunks using naive cosine similarity.

    Args:
        query_embedding: Query vector
        chunk_index: List of {text, embedding, source} dicts
        top_k: Number of results to return

    Returns:
        Top-K chunks sorted by similarity (highest first)
    """
    results = []

    for chunk_dict in chunk_index:
        similarity = cosine_similarity(query_embedding, chunk_dict["embedding"])
        results.append({
            "text": chunk_dict["text"],
            "similarity": round(similarity, 3),
            "source": chunk_dict.get("source", "")
        })

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]


# ============================================================================
# PART 5: NAIVE RAG PIPELINE
# ============================================================================

async def build_rag_index() -> list[dict]:
    """
    Build knowledge base index from USDA data.

    Pipeline:
    1. Take each food entry
    2. Chunk using structure-based strategy (semantic boundaries)
    3. Embed each chunk
    4. Store in index

    Returns:
        Index: list of {text, embedding, source} dicts
    """
    print("📚 Building RAG Index from USDA FoodData Central...")
    print(f"   Loading {len(USDA_NUTRITION_KB)} food entries\n")

    index = []

    for food_entry in USDA_NUTRITION_KB:
        # Strategy: Structure-based chunking (semantic boundaries)
        chunks = chunk_by_structure(food_entry)

        for chunk_text in chunks:
            # Embed the chunk
            embedding = simulate_embedding(chunk_text)

            index.append({
                "text": chunk_text,
                "embedding": embedding,
                "source": food_entry["source"],
                "food_id": food_entry["id"]
            })

    print(f"✅ Index built: {len(index)} chunks from {len(USDA_NUTRITION_KB)} foods\n")
    return index


async def rag_query(question: str, rag_index: list[dict]) -> dict:
    """
    Execute a naive RAG query.

    Pipeline:
    1. Embed the question
    2. Retrieve top-3 similar chunks
    3. Augment prompt with retrieved context
    4. (In production: send to Claude for generation)

    Args:
        question: User's nutrition question
        rag_index: Knowledge base index

    Returns:
        RAG response with retrieved chunks + augmented prompt
    """
    print(f"\n{'='*70}")
    print(f"Query: {question}")
    print('='*70)

    # Step 1: Embed the question
    question_embedding = simulate_embedding(question)

    # Step 2: Retrieve top-3 chunks
    retrieved = naive_retrieve(question_embedding, rag_index, top_k=3)

    print("\n📖 Retrieved chunks:")
    for i, chunk in enumerate(retrieved, 1):
        print(f"   {i}. [Similarity: {chunk['similarity']:.3f}]")
        print(f"      {chunk['text']}")
    print()

    # Step 3: Augment prompt with retrieved context
    context_blocks = "\n\n".join([
        f"[CHUNK {i}] {chunk['text']}"
        for i, chunk in enumerate(retrieved, 1)
    ])

    augmented_prompt = f"""You are a nutrition expert. Answer the user's question using the
following nutrition information from USDA FoodData Central:

{context_blocks}

User Question: {question}

Provide an accurate, concise answer based ONLY on the retrieved information above."""

    print("📝 Augmented Prompt (what gets sent to Claude):")
    print("-" * 70)
    print(augmented_prompt)
    print("-" * 70)
    print()

    # Simulated answer (in production: Claude generates this)
    answer = f"""Based on the USDA FoodData Central data:

{retrieved[0]['text']}

Key insight: The retrieved information shows accurate nutrition facts that help
provide sourced, hallucination-free answers. This is the core RAG benefit."""

    return {
        "question": question,
        "retrieved_chunks": retrieved,
        "augmented_prompt": augmented_prompt,
        "answer": answer
    }


# ============================================================================
# DEMO: NAIVE RAG IN ACTION
# ============================================================================

async def main():
    """Demonstrate complete end-to-end naive RAG pipeline."""

    print("🎯 Phase 3 Day 3: Naive RAG Pipeline (End-to-End)\n")
    print("Key Learning:")
    print("- Chunking: Break knowledge base into semantic pieces")
    print("- Embedding Model Tradeoffs: sentence-transformers vs OpenAI vs Voyage")
    print("- Vector Store Concept: where to store millions of embeddings")
    print("- Cosine Similarity: retrieval metric (0.0 = opposite, 1.0 = identical)")
    print("- Augmentation: add retrieved context to LLM prompt")
    print()

    # ======================================================================
    # DEMO 1: Chunking Strategies Comparison
    # ======================================================================
    print("="*70)
    print("DEMO 1: Chunking Strategies")
    print("="*70)

    sample_text = """Salmon is a fatty fish rich in omega-3 fatty acids.
It provides high-quality protein and essential nutrients.
Salmon is excellent for heart health."""

    print(f"\nOriginal text:\n{sample_text}\n")

    print("Strategy 1: Size-based (100 chars, 20 overlap)")
    size_chunks = chunk_by_size(sample_text, chunk_size=100, overlap=20)
    for i, chunk in enumerate(size_chunks, 1):
        print(f"  Chunk {i}: {chunk[:50]}...")

    print("\nStrategy 2: Semantic-based (by sentences)")
    semantic_chunks = chunk_by_semantic_similarity(sample_text)
    for i, chunk in enumerate(semantic_chunks, 1):
        print(f"  Chunk {i}: {chunk[:50]}...")

    print("\n📊 Summary:")
    print(f"  Size-based: {len(size_chunks)} chunks (fixed size, may split mid-sentence)")
    print(f"  Semantic-based: {len(semantic_chunks)} chunks (respects boundaries)")
    print()

    # ======================================================================
    # DEMO 2: Embedding Model Comparison
    # ======================================================================
    print("="*70)
    print("DEMO 2: Embedding Model Tradeoffs")
    print("="*70)
    print(EMBEDDING_MODEL_COMPARISON)
    print()

    # ======================================================================
    # DEMO 3: Vector Store Options
    # ======================================================================
    print("="*70)
    print("DEMO 3: Vector Store Concept")
    print("="*70)
    print(VECTOR_STORE_OPTIONS)
    print()

    # ======================================================================
    # STEP 4: Build RAG Index (Full Pipeline)
    # ======================================================================
    print("="*70)
    print("DEMO 4: Complete RAG Pipeline")
    print("="*70)
    rag_index = await build_rag_index()

    # ======================================================================
    # STEP 2: Example RAG Queries
    # ======================================================================
    queries = [
        "What's the nutrition in cooked chicken?",
        "How many calories in whole wheat bread?",
        "Is salmon high in protein?",
    ]

    for query in queries:
        result = await rag_query(query, rag_index)
        print(f"✅ Answer:\n{result['answer']}\n")

    # ======================================================================
    # KEY INSIGHTS
    # ======================================================================
    print("\n" + "="*70)
    print("🔑 Why RAG Matters for NomNom")
    print("="*70)
    print("""
1. Scalability
   - USDA FoodData Central: 7,700+ foods (too large for context)
   - RAG retrieves only relevant foods for the user's question

2. Accuracy
   - LLM answers based on retrieved USDA data, not hallucination
   - Sources can be cited: "According to USDA FoodData Central..."

3. Freshness
   - Knowledge base updated without retraining
   - Add new foods → re-index → users see new results immediately

4. Cost
   - Retrieval is cheap (cosine similarity)
   - Only augmented prompts sent to LLM
   - With semantic caching, repeated questions cost even less

5. Citations (Next: Day 5)
   - Enable citations in Claude API
   - Users can verify sources
   - Builds trust in food recommendations
""")

    # ======================================================================
    # WHAT'S NEXT
    # ======================================================================
    print("\n" + "="*70)
    print("🚀 Next: Days 4-5 (Advanced RAG Techniques)")
    print("="*70)
    print("""
Day 4: BM25 + Hybrid Search + RRF + Reranking
  - BM25: keyword-based (sparse) retrieval
  - Hybrid: combine semantic (dense) + keyword (sparse)
  - RRF: merge multiple ranking signals (RecSys pattern)
  - Reranking: use LLM to rerank top-10 → top-3

Day 5: Contextual Retrieval + Citations
  - Add context to chunks before embedding (improves accuracy)
  - Enable citations in Claude API (transparency)
  - Measure recall lift from contextual retrieval

Why these matter: Simple cosine search sometimes misses keyword matches
(e.g., "fish oil supplement" vs. "salmon"). Hybrid + reranking fixes this.
""")


if __name__ == "__main__":
    asyncio.run(main())
