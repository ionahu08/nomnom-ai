# Iteration 12: Detailed Implementation Phases

## Phase 1: Critical Fixes (P1)

### Issue 1: ai_service.py — Hardcoded "food photo" Bug

**File:** `NomNom-Backend/src/services/ai_service.py`  
**Lines:** ~90-93  
**Severity:** CRITICAL — Makes entire semantic cache meaningless

**Problem:**
```python
# Current (broken):
food_description = "food photo"  # hardcoded!
cached = await SemanticCache.get_cached_analysis(db, food_description)
```

Every cache lookup embeds the literal string `"food photo"` instead of the actual food being analyzed. This means:
- User photos chicken → embeds "food photo"
- User photos salmon → embeds "food photo" (same embedding!)
- Cache hit when it shouldn't be, miss when it should be

**Root Cause:** Missing logic to extract or generate the actual food description from the request.

**Solution:** Use actual food name/description from the request context:
```python
# After fix:
# Extract food description from request or use placeholder if unavailable
food_description = request.food_name or request.food_description or "unknown food"
cached = await SemanticCache.get_cached_analysis(db, food_description)
```

**Verification:** Submit two different foods → should get different cache results, not identical.

---

### Issue 2: cache.py — SIMILARITY_THRESHOLD Never Enforced

**File:** `NomNom-Backend/src/llm/cache.py`  
**Lines:** 43 (declaration), 88-92 (retrieval logic)  
**Severity:** CRITICAL — Threshold is a no-op

**Problem:**
```python
# Line 43:
SIMILARITY_THRESHOLD = 0.95

# Lines 88-92 (get_cached_analysis):
results = collection.query(query_embedding=query_embedding, n_results=1)
if results['ids']:
    return results['documents'][0]  # Returns without checking distance!
return None
```

The threshold is declared but never checked. The method always returns the closest match, even if similarity is very low (0.4, 0.5, etc.).

**Solution:** Add distance check before returning:
```python
results = collection.query(query_embedding=query_embedding, n_results=1, where={"distance": {"$lte": 1 - SIMILARITY_THRESHOLD}})
if results['ids'] and results['distances'][0] <= 1 - SIMILARITY_THRESHOLD:
    return results['documents'][0]
return None
```

Or manually check after retrieval:
```python
results = collection.query(query_embedding=query_embedding, n_results=1)
if results['ids']:
    distance = results['distances'][0][0]  # pgvector: distance = 1 - cosine_similarity
    if distance <= (1 - SIMILARITY_THRESHOLD):
        return results['documents'][0]
return None
```

**Why 0.95 is too strict:** From Day 3 learning, we found that cosine similarity ≥ 0.82 catches real cache hits (same meal, different lighting) while filtering out false positives. 0.95 is only "nearly identical" embeddings.

---

### Issue 3: cache.py — Threshold Value Too High

**File:** `NomNom-Backend/src/llm/cache.py`  
**Line:** 43  
**Severity:** HIGH — When threshold is finally enforced (Issue 2), current value cuts real hits

**Current:**
```python
SIMILARITY_THRESHOLD = 0.95
```

**Change to:**
```python
SIMILARITY_THRESHOLD = 0.82
```

**Why:** Phase 3 Day 3 benchmarking showed:
- 0.95 threshold: 0% cache hits (too strict, misses legitimate duplicates)
- 0.82 threshold: 67% cache hits (catches same meal, different angles/lighting)
- 0.50 threshold: 92% hits (too loose, catches unrelated foods)

0.82 is the sweet spot balancing recall (find real duplicates) vs. precision (no false matches).

---

### Issue 4: seed_knowledge.py — No Error Handling

**File:** `NomNom-Backend/src/llm/seed_knowledge.py`  
**Lines:** All  
**Severity:** HIGH — Silent failure if seeding fails mid-way

**Problem:**
```python
# Current:
async def seed_nutrition_kb(db):
    # Long process: download USDA data, chunk, embed, insert to DB
    # If it crashes on line 30/40, no error handling
    # Caller has no way to know it failed
```

**Solution:** Wrap in try/except and add --refresh mode:
```python
import asyncio
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
        raise


# Add CLI support:
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Delete and reseed KB")
    args = parser.parse_args()
    
    asyncio.run(seed_nutrition_kb(db, refresh=args.refresh))
```

**Verification:** Run `python seed_knowledge.py --refresh` → should complete without crashing.

---

## Phase 2: High Priority Fixes (P2)

### Issue 5: tools.py — Silent Failure on Unknown task_type

**File:** `NomNom-Backend/src/llm/tools.py`  
**Lines:** ~40-50 (get_tools_for_task)  
**Severity:** MEDIUM — Silently returns [] when task is unrecognized

**Problem:**
```python
def get_tools_for_task(task_type: str) -> list[dict]:
    if task_type == "analyze_food":
        return [ANALYZE_FOOD_TOOL]
    return []  # Silent failure for unknown tasks
```

If caller passes `task_type="something_invalid"`, they get an empty list with no warning. Hard to debug.

**Solution:** Add warning log:
```python
import logging

logger = logging.getLogger(__name__)

def get_tools_for_task(task_type: str) -> list[dict]:
    if task_type == "analyze_food":
        return [ANALYZE_FOOD_TOOL]
    
    logger.warning(f"Unknown task_type: {task_type} — returning no tools")
    return []
```

**Verification:** Call with invalid task → should see warning in logs.

---

### Issue 6: tools.py — No Enum Constraints on food_category/cuisine_origin

**File:** `NomNom-Backend/src/llm/tools.py`  
**Lines:** ANALYZE_FOOD_TOOL schema definition  
**Severity:** MEDIUM — Allows any string, reduces consistency

**Problem:**
```python
ANALYZE_FOOD_TOOL = {
    "name": "analyze_food",
    "input_schema": {
        "properties": {
            "food_category": {
                "type": "string",
                "description": "..."
            },
            "cuisine_origin": {
                "type": "string",
                "description": "..."
            },
            # ...
        }
    }
}
```

Claude can return anything: "Chicken", "CHICKEN", "poultry", "bird", etc. Reduces parsing consistency.

**Solution:** Add enum constraints:
```python
"food_category": {
    "type": "string",
    "enum": ["protein", "vegetable", "grain", "fruit", "dairy", "fat", "other"],
    "description": "..."
},
"cuisine_origin": {
    "type": "string",
    "enum": ["american", "italian", "chinese", "mexican", "indian", "mediterranean", "japanese", "other"],
    "description": "..."
}
```

**Verification:** Claude now returns structured categories consistently (parseable by downstream services).

---

## Phase 3: Polish (P3)

### Issue 7: embedding.py — Deprecated asyncio.get_event_loop()

**File:** `NomNom-Backend/src/llm/embedding.py`  
**Lines:** ~45  
**Severity:** LOW — Works now, will break in Python 3.12+

**Problem:**
```python
loop = asyncio.get_event_loop()  # Deprecated in Python 3.10+
```

In Python 3.10+, this warns; in 3.12+, it may raise an error.

**Solution:** Replace with `asyncio.get_running_loop()`:
```python
loop = asyncio.get_running_loop()  # Works in 3.10+, cleaner
```

**Note:** Only use within an async context. If calling from sync code, use `asyncio.new_event_loop()` instead.

**Verification:** No deprecation warnings in Python 3.10+ logs.

---

## Testing Strategy

1. **Unit Tests:** Test each function independently (threshold check, error handling)
2. **Integration Tests:** Cache hit/miss scenarios with actual DB
3. **Smoke Test:** Full pipeline: photo → LLM → cache → response
4. **Regression Test:** Ensure existing tests still pass

See `tests/integration/test_semantic_cache.py` for test patterns.
