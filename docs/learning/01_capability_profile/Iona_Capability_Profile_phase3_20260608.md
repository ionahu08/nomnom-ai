# Iona's LLM Harnessing Capability Profile — Phase 3 Snapshot

**Date:** June 8, 2026 (End of Phase 3)

> This is a historical snapshot of capability progression. See `Iona_Capability_Profile.md` for the forward-looking living profile.

---

## Phase 3 Summary

**What was accomplished:**
- **Days 1-5:** Concept learning (learning_lab/phase_3/01-05_*.py scripts)
  - 01_agent_loop.py: Multi-tool agent orchestration (while-loop pattern)
  - 02_pdf_parsing.py: Claude native PDF parsing (base64, media_type)
  - 03_naive_rag.py: Complete RAG pipeline (chunking, embeddings, vector search, USDA KB)
  - 04_hybrid_search.py: BM25 + vector search + RRF fusion + reranking
  - 05_contextual_retrieval_citations.py: Contextual enrichment + citations for trust
- **Days 6-7:** Code reviews (embedding.py, cache.py, seed_knowledge.py, tools.py)
  - Identified 6 issues in production code
  - Semantic cache threshold tuning (0.95 → 0.82)
  - Discovered hardcoded "food photo" bug (Day 10 catch)
- **Days 8-9:** Capstone advanced RAG (full pipeline with evaluation)
  - SimpleRAG baseline vs AdvancedRAG (hybrid + RRF)
  - Evaluation metrics: NDCG@5, MRR
  - Demonstrated 15-20% improvement with advanced RAG
- **Day 10:** Production integration (7 bugs fixed, 5 files updated)
  - P1 Critical: semantic cache bugs, seed knowledge error handling
  - P2 High: tool schema improvements
  - P3 Polish: deprecation fix

**Key metrics:**
- Cache threshold tuned: 0.95 → 0.82 (+67% hit rate improvement)
- Hybrid RAG vs naive: +15-20% improvement (NDCG@5, MRR)
- Production fixes: 7 issues across 5 files
- Code quality: 100% compile, 0 deprecation warnings
- Evaluation scale: 30+ nutrition questions with full metrics

**Duration:** June 9–8, 2026 (10 working days)

---

## Layer-by-Layer Capability at Phase 3 End

### Layer 0: API Mastery
- **Phase 2 → Phase 3:** 4/5 → **4/5** (Stable)
- **Target:** 4/5
- **Status:** MAINTAINED
- **Evidence:**
  - Solid API knowledge from Phase 1-2
  - Understand: tool_use, prefill+stop, streaming, multimodal
  - No new API concepts in Phase 3 (focus was augmentation, not API)

---

### Layer 1: Prompt Engineering
- **Phase 2 → Phase 3:** 3/5 → **3/5** (Deferred)
- **Target:** 4/5
- **Status:** STABLE, NOT FOCUS OF PHASE 3
- **Evidence:**
  - Phase 3 focused on retrieval (embedding, cache, RAG), not prompts
  - Prompt engineering will advance in Phase 4+ (prompt caching, tier-specific prompts)
  - Current understanding sufficient for RAG augmentation

---

### Layer 2: Output Control
- **Phase 2 → Phase 3:** 4/5 → **4/5** (Stable)
- **Target:** 4/5
- **Status:** MAINTAINED, BASELINE FOR PHASE 3
- **Evidence:**
  - tool_choice integration from Phase 2 enables all Phase 3 work
  - Phase 3 assumed structured output (tool_choice from Day 1 agent loop)
  - No new output control concepts learned

---

### Layer 3: Augmentation ⭐ MAJOR PROGRESS
- **Phase 2 → Phase 3:** 1/5 → **4/5** ✅✅✅
- **Target:** 5/5
- **Status:** STRONG PROGRESS, APPROACHING TARGET
- **Evidence:**
  - **Chunking strategies (Day 3):** Understand fixed-size, semantic, overlap-aware
    - Trade-off: precision vs recall (smaller chunks = more retrieval, larger = more context)
    - Implemented: 3 chunking strategies with comparison metrics
  - **Embeddings (Days 3-4):** Model selection, dimensionality, local vs. API
    - Chose: all-MiniLM-L6-v2 (384-dim, free, fast)
    - Justified: Sufficient for food domain, 4x cheaper than commercial
    - Key insight: Model choice < threshold tuning + chunking strategy
  - **Vector similarity (Days 3-4):** Cosine distance, threshold tuning, normalization
    - Empirically tuned: 0.95 → 0.82 (67% hit rate improvement)
    - Understand: Threshold is domain-specific, must be benchmarked
    - Key insight: Bad threshold kills entire cache (0% vs 67% hit rate)
  - **BM25 + Hybrid search (Day 4):** Keyword search + semantic search fusion
    - Implemented: BM25 inverted index, term frequency scoring
    - Implemented: RRF (Reciprocal Rank Fusion) from RecSys patterns
    - Key insight: Multi-channel ranking beats single signal
  - **Contextual retrieval (Day 5):** Adding document context before embedding
    - Understand: "From: Title, Section: X" before embedding improves recall
    - Implemented: Context-enriched chunks with higher relevance scores
  - **Citations (Day 5):** Claude annotations [1], [2], [3] with source mapping
    - Understand: Citations = trust + verification feature
    - Key insight: Production RAG requires citations for legal/trust reasons
  - **RAG evaluation (Days 8-9):** NDCG@5, MRR ranking metrics
    - Implemented: Full eval pipeline (simple vs advanced comparison)
    - Understand: NDCG@5 measures ranking quality without labeled data
  - **Production integration (Day 10):** Fixed semantic cache, integrated retrieval
    - Understand: How cache threshold, query embedding, distance checks work together

---

### Layer 4: Reliability Engineering
- **Phase 2 → Phase 3:** 4/5 → **4/5** (Enhanced)
- **Target:** 5/5 (My differentiator)
- **Status:** STRONG MAINTENANCE + NEW SKILLS
- **Evidence:**
  - **Semantic caching as reliability (Days 3-4 + Day 10):**
    - Understand: Cache threshold is reliability parameter (hit rate affects cost)
    - Fixed: Threshold enforcement bug (declared but never checked)
    - Fixed: Hardcoded "food photo" bug (makes cache meaningless)
    - Key insight: Cache bugs cascade (one bad parameter = entire system fails)
  - **Error handling (Day 10, seed_knowledge.py):**
    - Added: try/except with logging for knowledge base seeding
    - Added: --refresh mode for KB maintenance
    - Key insight: One-time seeding breaks in production (data updates, user preferences change)
  - **Observability (Days 3-4):**
    - Implemented: Cache hit/miss logging with similarity scores
    - Understand: Cache statistics are production monitoring signal
    - Know: CacheStats is in-memory only (deferred to Phase 4)
  - **Knowledge base robustness (Day 3-4 + Day 10):**
    - Understand: KB construction (chunking, embedding, storage) is reliability concern
    - Know: Stale cache (TTL) is reliability issue (deferred to Phase 4)

---

### Layer 5: Agent Engineering
- **Phase 2 → Phase 3:** 1/5 → **2/5** ⭐
- **Target:** 4/5
- **Status:** FOUNDATION STRENGTHENED, READY FOR PHASE 5
- **Evidence:**
  - **Multi-tool agent loops (Day 1):** Hand-wrote while-loop orchestration
    - Understand: Tool execution, result feedback, termination conditions
    - Key insight: Agent loop is exactly the pattern from Phase 2 tool_use
  - **Agent integration with RAG:** Did not combine in Phase 3 (capstone was RAG-only)
    - Will implement: Agent + RAG combined in Phase 5

---

### Layer 6: Multi-Agent Coordination
- **Phase 2 → Phase 3:** 0/5 → **0/5** (Not in scope)
- **Target:** 3/5
- **Status:** NOT STARTED
- **Notes:** Deferred to Phase 5-6

---

## Key Insights from Phase 3

### 1. Threshold tuning is more important than model choice
- Spent hours analyzing embedding models (OpenAI vs Voyage vs local)
- Outcome: Model choice ~5% impact
- Real impact: Threshold tuning (0.95 vs 0.82) = 67% hit rate difference
- **Takeaway:** Don't over-engineer model selection. Tune the parameters on your domain.

---

### 2. Semantic cache is foundational but fragile
- Cache threshold was declared (0.95) but never enforced (returns closest match)
- Cache query was hardcoded ("food photo") instead of actual food
- Result: Entire cache system was non-functional
- Fix: Explicit threshold check + actual query description
- **Takeaway:** Declarative configs must be enforced. Code reviews catch what spec misses.

---

### 3. RRF (RecSys multi-channel ranking) applies to RAG
- Vector search captures semantics (synonyms, similar dishes)
- BM25 captures keywords (exact matches)
- Combining both with RRF: better recall than either alone
- **Takeaway:** Your RecSys background directly applies. Multi-channel fusion is universal pattern.

---

### 4. Bootstrapping eval data with Claude saves effort
- Hand-writing 30 test cases: tedious, limited diversity
- Claude-generated: Fast, covers edge cases (ambiguous photos, mixed dishes)
- **Takeaway:** Use Claude as tool for test generation. Specify edge cases clearly in prompt.

---

### 5. Contextual retrieval improves recall significantly
- Plain: "Grilled chicken Caesar salad" → embedding misses related meals
- With context: "[USDA Guide] Protein Sources: Grilled chicken Caesar salad" → finds similar meals
- Simple trick with big impact
- **Takeaway:** Add context before embedding. Title + section + text improves semantic matching.

---

### 6. Citations are production feature, not afterthought
- Phase 1-2: Focused on getting answers
- Phase 3: Realized answers without sources = not trustworthy
- Citations enable: Verification, feedback loops, legal compliance
- **Takeaway:** Production RAG requires citations. Build it in from Day 1.

---

### 7. Knowledge base maintenance is operational work
- Current: One-time seeding (seed_knowledge.py runs once)
- Reality: USDA data updates, user preferences change, cache gets stale
- Fix: --refresh mode, error handling, logging
- Deferred: TTL invalidation (Phase 4)
- **Takeaway:** KB isn't static. Plan for updates, refreshes, and maintenance modes.

---

## Readiness Assessment for Phase 4

| Skill | Ready? | Notes |
|-------|--------|-------|
| API fundamentals | ✅ Yes | Solid from Phases 1-2 |
| Tool use patterns | ✅ Yes | Implemented agents, understand loops |
| Output control | ✅ Yes | tool_choice + validation |
| Eval infrastructure | ✅ Yes | Built NDCG@5, MRR metrics |
| Error handling | ✅ Yes | Improved error messages, logging |
| Embeddings | ✅ Yes | Understand models, dimensionality, thresholds |
| Vector search | ✅ Yes | Cosine similarity, threshold tuning |
| Semantic cache | ✅ Yes | Built + debugged, understand trade-offs |
| Hybrid search (BM25 + RRF) | ✅ Yes | Implemented + evaluated |
| Contextual retrieval | ✅ Yes | Understand impact, implemented |
| Citations | ✅ Yes | Understand feature, ready for integration |
| Prompt caching | ⏳ Ready to learn | Next focus in Phase 4 |
| Model tiering | ⏳ Ready to learn | Next focus in Phase 4 |
| Rate limiting | ⏳ Ready to learn | Next focus in Phase 4 |

---

## Summary: Layer Progression

```
Layer 0 (API):           4/5 ─→ 4/5 ─→ 4/5    [STABLE]
Layer 1 (Prompts):       3/5 ─→ 3/5 ─→ 3/5    [DEFERRED TO PHASE 4+]
Layer 2 (Output):        4/5 ─→ 4/5 ─→ 4/5    [STABLE, FOUNDATION]
Layer 3 (Augmentation):  1/5 ─→ 1/5 ─→ 4/5    [✅ MAJOR PROGRESS]
Layer 4 (Reliability):   4/5 ─→ 4/5 ─→ 4/5    [✅ ENHANCED]
Layer 5 (Agents):        1/5 ─→ 1/5 ─→ 2/5    [✅ FOUNDATION LAID]
Layer 6 (Multi-Agent):   0/5 ─→ 0/5 ─→ 0/5    [NOT STARTED]
```

**Strongest areas:** API (4/5), Output Control (4/5), Reliability (4/5), Augmentation (4/5)  
**Growth areas ready for Phase 4:** Caching optimization, Rate limiting, Cost control  
**Deferred to later phases:** Agents (Phase 5), Multi-Agent (Phase 6)

---

## Differentiator Development

**Phase 0-1:** Recognized Reliability Engineering as differentiator (Layer 4)  
**Phase 2:** Strengthened Layer 4 with eval infrastructure, error handling, logging  
**Phase 3:** Enhanced Layer 4 with semantic caching, KB maintenance, observability  

**Current differentiator strength:** 4/5 across layers 2, 3, 4, 0

Combined with RecSys background:
- Multi-channel fusion (RRF) for ranking
- Signal fusion (code score + model score) for decisions
- Cost optimization (cache hit rate, model tiering)

**Unique combination:** RecSys patterns + LLM harnessing + reliability engineering

---

## Next Steps (Phase 4 & Beyond)

### Immediate (Phase 4: Request Routing + Rate Limiting + Logging)
1. Review router.py — request routing and model tiering
2. Review rate_limiter.py — API abuse prevention
3. Review logger.py — observability infrastructure
4. Implement prompt caching for cost reduction
5. Implement per-model and per-task cost tracking

### Short-term (Phase 4.5: CacheStats → Database)
1. Persist cache metrics to database
2. Query cache hit rates by user, food type, time range
3. Build monitoring dashboard

### Medium-term (Phase 5: Agent Engineering)
1. Hand-code multi-agent workflows
2. Agent + RAG integration (retrieve → analyze → recommend)
3. Feedback loops (user corrections → retrain/recalibrate)

### Long-term (Phase 6: Multi-Agent + MCP)
1. Multi-agent coordination patterns
2. MCP server exposure for extensibility

---

**Phase 3 complete. Capability progression: 1/5 → 4/5 in Layer 3 (Augmentation). Ready for Phase 4: Request Routing + Rate Limiting + Logging**
