# Iteration 04 — Embeddings, Vector Search & RAG (Phases 6-7)

## Goal

Add embeddings + pgvector support, build a nutrition knowledge base, and create RAG-powered recommendations with streaming.

## What's Built

- LLM harness with structured output
- Food photo analysis with guardrails + caching + logging
- Rate limiting + accuracy tracking

## What We're Building

**Part 1 (Phase 6): Embeddings & Vector Search**

Embeddings = convert text to 1024 numbers that represent meaning.
- Enable pgvector in PostgreSQL (vector database)
- Create embedding_service.py (text → embeddings)
- Build NutritionKB (knowledge base with embeddings)
- Implement semantic search (find similar meals + nutrition tips)

**Part 2 (Phase 7): RAG Recommendations + Streaming**

RAG = Retrieval-Augmented Generation. Instead of guessing, give Claude facts first.
- Retrieve nutrition tips + past meals relevant to user
- Build smart prompt with retrieved context
- Call Sonnet, stream response token-by-token (feels fast!)

## Resume Skills Demonstrated

- Embeddings & Vector Search (pgvector)
- RAG (Retrieval-Augmented Generation)
- Streaming (Server-Sent Events)
- Cost Optimization (cache prevents redundant calls)

## Success Criteria

- [x] pgvector enabled in PostgreSQL
- [x] Embeddings generated + stored
- [x] Similarity search works
- [x] Knowledge base seeded
- [x] RAG retrieval returns context
- [x] Recommendations endpoint works
- [x] Streaming SSE works end-to-end
- [x] All tests pass
