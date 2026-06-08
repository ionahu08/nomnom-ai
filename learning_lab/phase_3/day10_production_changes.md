# Phase 3 Day 10: Production Changes Summary

**Date:** June 8, 2026  
**Purpose:** Apply Phase 3 learnings (Days 1–9) to production code. Fix critical bugs blocking semantic cache functionality.

---

## Overview

Phase 3 deep-dived into RAG pipelines, semantic caching, hybrid search, and contextual retrieval. Days 6–7 reviewed four production LLM files. This document consolidates all findings into a prioritized action list for Day 10 implementation.

**Key Finding:** The semantic cache is completely broken due to TWO critical issues:
1. `ai_service.py` always passes literal string `"food photo"` to cache lookup
2. `cache.py` declares SIMILARITY_THRESHOLD but never enforces it

Both must be fixed for the cache to work correctly.

---

## Critical Issues (P1)

### 1. ai_service.py: Hardcoded "food photo" Bug

**File:** `NomNom-Backend/src/services/ai_service.py`  
**Lines:** ~90-93  
**Root Cause:** Missing logic to extract actual food description from request

**Current Code:**
```python
food_description = "food photo"  # Hardcoded!
cached = await SemanticCache.get_cached_analysis(db, food_description)
```

**Problem:** Every cache lookup embeds the literal string "food photo", regardless of what food was actually photographed. This means:
- Query 1: Chicken photo → embeds "food photo"
- Query 2: Salmon photo → embeds "food photo"
- Result: Identical embeddings, false cache hits

**Fix:**
```python
# Extract actual food description from request context
food_description = request.food_name or request.food_description or "unknown food"
cached = await SemanticCache.get_cached_analysis(db, food_description)
```

**Verification:**
- Submit chicken photo → gets analysis + caches result
- Submit salmon photo → should NOT return cached chicken result
- Submit same chicken photo again → should return cached chicken result

---

### 2. cache.py: SIMILARITY_THRESHOLD Never Enforced

**File:** `NomNom-Backend/src/llm/cache.py`  
**Lines:** 43 (declaration), 88-92 (retrieval without check)  
**Root Cause:** Threshold defined but not checked in similarity lookup

**Current Code:**
```python
# Line 43:
SIMILARITY_THRESHOLD = 0.95

# Lines 88-92:
results = collection.query(query_embedding=query_embedding, n_results=1)
if results['ids']:
    return results['documents'][0]  # Returns without distance check!
return None
```

**Problem:** The method always returns the closest match, regardless of distance. Even if the closest embedding has 0.4 similarity, it's still returned.

**Why This Matters:**
- Without threshold check: every query gets "cached" result (even unrelated foods)
- With threshold check: only truly similar foods return cached results

**Fix:**
```python
results = collection.query(query_embedding=query_embedding, n_results=1)
if results['ids']:
    distance = results['distances'][0][0]  # pgvector distance = 1 - cosine_similarity
    cosine_similarity = 1 - distance
    if cosine_similarity >= SIMILARITY_THRESHOLD:
        return results['documents'][0]
return None
```

**Verification:**
- Similar food (same meal, different angle) → cache hit
- Unrelated food → no cache hit
- Observe cache statistics increase with second identical query

---

### 3. cache.py: Threshold Value Too High (0.95 → 0.82)

**File:** `NomNom-Backend/src/llm/cache.py`  
**Line:** 43  
**Root Cause:** Threshold calibrated incorrectly; too strict

**Current:**
```python
SIMILARITY_THRESHOLD = 0.95
```

**Why 0.95 fails:** From Phase 3 Day 3 benchmarking (03_naive_rag.py):
- 0.95 threshold: catches only "nearly identical" embeddings (0% cache hits in practice)
- 0.82 threshold: catches same meal, different angles/lighting (67% cache hit rate)
- 0.50 threshold: too loose, false positives (92% hit rate but low quality)

**Change:**
```python
SIMILARITY_THRESHOLD = 0.82
```

**Why 0.82 is optimal:**
- Phase 3 Day 3 tested with USDA nutrition database
- Threshold = cosine similarity cutoff
- 0.82 = sweet spot balancing recall (find real duplicates) vs. precision (avoid false matches)

**Verification:**
- Same food, different photos → should hit cache
- Different foods → should NOT hit cache

---

### 4. seed_knowledge.py: No Error Handling

**File:** `NomNom-Backend/src/llm/seed_knowledge.py`  
**Lines:** All  
**Root Cause:** Missing try/except, no refresh mode

**Current Code:**
```python
async def seed_nutrition_kb(db):
    # Long operation, no error handling
    # If it crashes on line 30/40, silent failure
```

**Problem:** If seeding fails partway through, no error logged. Caller has no way to know KB is incomplete.

**Fix:** Add error handling + refresh mode:
```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def seed_nutrition_kb(db, refresh: bool = False):
    """
    Seed USDA nutrition knowledge base.
    
    Args:
        db: Database connection
        refresh: If True, delete existing KB and reseed from scratch
    """
    try:
        if refresh:
            logger.info("Clearing existing knowledge base...")
            await db.execute("DELETE FROM nutrition_chunks")
        
        logger.info("Seeding nutrition knowledge base...")
        # ... existing seeding logic ...
        
        logger.info("✅ Knowledge base seeded successfully")
        return True
    
    except Exception as e:
        logger.error(f"❌ Failed to seed knowledge base: {e}", exc_info=True)
        raise  # Re-raise so caller knows it failed


# Add CLI support:
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Delete and reseed KB")
    args = parser.parse_args()
    
    asyncio.run(seed_nutrition_kb(db, refresh=args.refresh))
```

**Verification:**
- Run: `python seed_knowledge.py` → completes without error
- Run: `python seed_knowledge.py --refresh` → clears and reseeds, completes without error

---

## High Priority Issues (P2)

### 5. tools.py: Silent Failure on Unknown task_type

**File:** `NomNom-Backend/src/llm/tools.py`  
**Lines:** ~40-50 (get_tools_for_task)  
**Root Cause:** Returns [] without warning

**Current:**
```python
def get_tools_for_task(task_type: str) -> list[dict]:
    if task_type == "analyze_food":
        return [ANALYZE_FOOD_TOOL]
    return []  # No warning
```

**Problem:** If caller typos task_type, they silently get no tools. Hard to debug.

**Fix:**
```python
import logging

logger = logging.getLogger(__name__)

def get_tools_for_task(task_type: str) -> list[dict]:
    if task_type == "analyze_food":
        return [ANALYZE_FOOD_TOOL]
    
    logger.warning(f"Unknown task_type: {task_type} — returning no tools")
    return []
```

**Verification:** Call with invalid task_type → warning appears in logs

---

### 6. tools.py: No Enum Constraints (food_category, cuisine_origin)

**File:** `NomNom-Backend/src/llm/tools.py`  
**Lines:** ANALYZE_FOOD_TOOL schema  
**Root Cause:** Accepts any string, no constraints

**Current:**
```python
"food_category": {
    "type": "string",
    "description": "Category of food (e.g., protein, vegetable)"
},
"cuisine_origin": {
    "type": "string",
    "description": "Origin cuisine (e.g., Italian, Chinese)"
}
```

**Problem:** Claude can return anything: "Chicken", "CHICKEN", "poultry", "bird" — inconsistent parsing downstream.

**Fix:** Add enum constraints:
```python
"food_category": {
    "type": "string",
    "enum": ["protein", "vegetable", "grain", "fruit", "dairy", "fat", "other"],
    "description": "Food category"
},
"cuisine_origin": {
    "type": "string",
    "enum": ["american", "italian", "chinese", "mexican", "indian", "mediterranean", "japanese", "other"],
    "description": "Cuisine origin"
}
```

**Verification:** Parser always receives valid categories (no more "poultry" vs "protein" inconsistencies)

---

## Polish Issues (P3)

### 7. embedding.py: Deprecated asyncio.get_event_loop()

**File:** `NomNom-Backend/src/llm/embedding.py`  
**Lines:** ~45  
**Root Cause:** Using deprecated API

**Current:**
```python
loop = asyncio.get_event_loop()  # Deprecated in Python 3.10+
```

**Problem:** Raises DeprecationWarning in Python 3.10+, will break in 3.12+.

**Fix:**
```python
loop = asyncio.get_running_loop()  # Works in 3.10+
```

**Verification:** No deprecation warnings in Python 3.10+ logs

---

## Summary Table

| Issue | File | Severity | Change Type |
|-------|------|----------|-------------|
| Hardcoded "food photo" | ai_service.py | P1 | Bug fix |
| Threshold never enforced | cache.py | P1 | Bug fix |
| Threshold too high (0.95) | cache.py | P1 | Tuning |
| No error handling | seed_knowledge.py | P1 | Robustness |
| Silent failure on bad task_type | tools.py | P2 | Logging |
| No enum constraints | tools.py | P2 | Schema validation |
| Deprecated asyncio call | embedding.py | P3 | Hygiene |

---

## Files to Modify

```
NomNom-Backend/src/
  ├── services/ai_service.py           (Issue 1)
  ├── llm/
  │   ├── cache.py                     (Issues 2, 3)
  │   ├── seed_knowledge.py            (Issue 4)
  │   ├── tools.py                     (Issues 5, 6)
  │   └── embedding.py                 (Issue 7)
```

---

## Verification Checklist

After all changes:

- [ ] All existing tests pass: `pytest tests/`
- [ ] Cache hit test: duplicate photo returns cached result
- [ ] Cache miss test: different food does NOT return previous cache result
- [ ] Threshold test: very low similarity (0.3) does NOT return as cache hit
- [ ] seed_knowledge.py runs: `python seed_knowledge.py --refresh` succeeds
- [ ] No asyncio deprecation warnings in logs (Python 3.10+)
- [ ] schema validation: food_category/cuisine_origin always from enum set
- [ ] Logging: unknown task_type produces warning in logs

---

## Implementation Notes

### Estimated Effort
- P1 fixes: 1–2 hours (mostly straightforward bug fixes)
- P2 fixes: 20 minutes (logging + schema updates)
- P3 fixes: 5 minutes (one-line changes)
- Testing: 30 minutes (write cache hit/miss tests)
- **Total: ~2.5 hours**

### Testing Strategy
1. Write regression test for "food photo" bug
2. Write threshold test (should hit for high similarity, miss for low)
3. Write seed_knowledge error handling test
4. Run full test suite
5. Manual smoke test on device (photo → analysis → cache)

### Commit Strategy
- **Commit 1:** P1 fixes (ai_service + cache + seed_knowledge)
- **Commit 2:** P2 fixes (tools.py logging + enums)
- **Commit 3:** P3 fixes (embedding.py deprecation)
- **Commit 4:** Tests + documentation updates

This allows easy rollback if P1 or P2 needs revision.
