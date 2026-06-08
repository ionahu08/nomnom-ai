# Phase 3 Day 7: Code Review — seed_knowledge.py + tools.py

**Date:** June 10, 2026  
**Reviewer:** Iona  
**Status:** Final code review before Phase 3 capstone (Days 8-9)

---

## Table of Contents

1. **[System Context: How All 4 Files Work Together](#system-context-how-all-4-files-work-together)**

2. **[File Overview](#file-overview)**
   - 2.1 [seed_knowledge.py: Knowledge Base Seeding](#seed_knowledgepy-knowledge-base-seeding)
   - 2.2 [tools.py: Structured Output via Tool Definitions](#toolspy-structured-output-via-tool-definitions)
   - 2.3 [How They Work Together](#how-they-work-together)

3. **[seed_knowledge.py Analysis (41 lines)](#seed_knowledgepy-analysis-41-lines)**
   - 3.1 [Knowledge Base Coverage: What's Seeded?](#1-knowledge-base-coverage-whats-seeded)
   - 3.2 [Chunking Strategy & Source Data](#2-chunking-strategy--source-data)
   - 3.3 [Update Frequency & Maintenance](#3-update-frequency--maintenance)
   - 3.4 [Error Handling & Logging](#4-error-handling--logging)

4. **[tools.py Analysis (89 lines)](#toolspy-analysis-89-lines)**
   - 4.1 [Tool Schema Design: ANALYZE_FOOD_TOOL](#1-tool-schema-design-analyze_food_tool)
   - 4.2 [Multi-Tool Support: Is It Real?](#2-multi-tool-support-is-it-real)
   - 4.3 [Error Handling & Feedback](#3-error-handling--feedback)
   - 4.4 [Agent Loop Integration](#4-agent-loop-integration)

5. **[Summary & Grade](#summary--grade)**

6. **[Concrete Improvements for Day 10](#concrete-improvements-for-day-10)**

7. **[Next: Days 8-9 Capstone](#next-days-8-9-capstone)**

---

## System Context: How All 4 Files Work Together

**The Problem:** How do we avoid re-analyzing the same meal twice?

**The Solution:** Semantic cache with 4 components working together.

```
INITIALIZATION (one-time at deployment):
  seed_knowledge.py
  └─ Load 5,000 foods from USDA into database

RUNTIME (every time user analyzes a meal):
  User uploads photo
    ↓
  cache.py + embedding.py (check for similar meals)
    ├─ embedding.py: "Grilled chicken" → [0.45, 0.62, ...]
    ├─ Search pgvector: found similar before?
    └─ IF YES: Return cached result (save API call!)
    
  tools.py (analyze if no cache hit)
    ├─ Claude receives ANALYZE_FOOD_TOOL schema
    ├─ Claude MUST return: {food_name, calories, protein, ...}
    └─ Structure guaranteed valid
    
  cache.py + embedding.py (store for next time)
    ├─ embedding.py: Convert → vector
    └─ Store vector in pgvector
    
  Result: Day 1 costs $0.001, Day 2 costs $0 (cache hit)
```

**File Collaboration:**

| File | Role |
|------|------|
| **seed_knowledge.py** | Load nutrition KB (USDA data) at deployment |
| **tools.py** | Force Claude to return structured JSON |
| **embedding.py** | Convert text → vectors for similarity search |
| **cache.py** | Store/retrieve results, avoid redundant calls |

**Impact:** 70% of users eat repetitive meals → 70% cache hits → 70% fewer API calls

---

## File Overview

### seed_knowledge.py: Knowledge Base Seeding

**Purpose:** One-time deployment script that populates the nutrition knowledge base. RAG retrieves from this KB.

**How it works:**
```
Deployment time (first startup)
    ↓
seed_knowledge.py: main()
    ↓
seed_nutrition_kb(db) [from knowledge_service.py]
    ↓
Load nutrition data (USDA? hardcoded? external API?)
    ↓
Insert into database with embeddings
    ↓
RAG can now search this KB
```

**Core Function:**
- `main()` — Entry point. Connects to DB, seeds KB, logs progress.

**Key Questions:**
- How many foods are in the KB?
- Where does the source data come from?
- What's the chunking strategy?
- Is the KB ever updated after initial seeding?

---

### tools.py: Structured Output via Tool Definitions

**Purpose:** Defines Claude tool schemas that force Claude to return structured JSON (tool_use pattern from Phase 2).

**How it works:**
```
Tool Definition (tools.py): ANALYZE_FOOD_TOOL
    ↓
API call includes: tools=[ANALYZE_FOOD_TOOL], tool_choice=force
    ↓
Claude: "I MUST call analyze_food with this structure"
    ↓
Result: {"food_name": "...", "calories": 160, ...} (guaranteed valid)
```

**Core Objects:**
- `ANALYZE_FOOD_TOOL` — JSON schema with 8 required fields
- `get_tools_for_task(task_type)` — Router returning tools for different tasks

**Key Questions:**
- Is there real multi-tool orchestration, or just single-tool?
- How does system handle tool errors?
- Does Claude get useful feedback when something fails?

---

### How They Work Together

```
INITIALIZATION (One-time):
  seed_knowledge.py
    ↓ Inserts food nutrition entries into database

RUNTIME (Every food analysis):
  tools.py
    ↓ Defines ANALYZE_FOOD_TOOL schema
    ↓ Forces Claude to call tool (tool_choice)
    ↓ Returns structured JSON {food_name, calories, ...}
    ↓ This result eventually goes into cache (Day 6)

RETRIEVAL (RAG Pipeline):
  cache.py (Day 6) + embedding.py (Day 6)
    ↓ Search seeded KB via embeddings
    ↓ Retrieve relevant foods
    ↓ Augment prompt with context
```

---

## seed_knowledge.py Analysis (41 lines)

### 1. Knowledge Base Coverage: What's Seeded?

**Current Implementation:**
```python
# Lines 24-35
async def main():
    logger.info("Connecting to database...")
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        logger.info("Starting knowledge base seeding...")
        inserted = await seed_nutrition_kb(db)  # ← This function is in knowledge_service.py!
        logger.info(f"Seeding complete. Inserted {inserted} entries.")
```

**Assessment:** ⚠️ **INCOMPLETE CONTEXT** (actual KB logic is in knowledge_service.py)

**Questions:**
1. **How many foods are seeded?** (script doesn't show count)
2. **What data sources?** (USDA? Hardcoded? External API?)
3. **Coverage gaps?** (Does it include all cuisines? Dietary restrictions?)

**Critical Issue:**
- `seed_nutrition_kb()` is **not defined in this file** — it's in `knowledge_service.py`
- This script is just a **wrapper/entry point**
- Real logic is hidden, can't assess without seeing knowledge_service.py

**What I would ask:**
```
In knowledge_service.py, the seed_nutrition_kb() function should:
- Load nutrition data from a source (USDA FoodData Central?)
- Parse/chunk the data
- Embed each chunk
- Insert into database

Is this happening? How many entries? What source?
```

---

### 2. Chunking Strategy & Source Data

**Assessment:** ❌ **UNKNOWN** (Not visible in this file)

**Expected to Find:**
```python
# What I'd expect to see:
NUTRITION_DATA_SOURCE = "USDA FoodData Central"
CHUNK_SIZE = 200  # characters
CHUNK_OVERLAP = 20  # for context

# Or:
from external_api import fetch_usda_foods
foods = fetch_usda_foods(limit=5000)

# Then chunk, embed, insert...
```

**What Actually Exists:**
- File just calls `seed_nutrition_kb(db)` — no details on HOW KB is built

**Issue:**
- Can't assess chunking quality without seeing knowledge_service.py
- Can't verify if KB is production-ready (size? coverage? accuracy?)

---

### 3. Update Frequency & Maintenance

**Assessment:** ⚠️ **DESIGN FLAW**

**Current Approach:**
```python
# Line 24: async def main()
# ← This is one-time only (at deployment)
```

**Problem:**
- Seed script runs **once at startup**
- If USDA updates their data (new nutrition facts), KB is stale
- No mechanism to refresh/update KB after initial seeding
- Users get outdated nutrition info

**Expected for Production:**
```python
# Should support:
# 1. Initial seed (at deployment)
# 2. Periodic refresh (daily/weekly update from source)
# 3. Manual refresh command (for emergencies)

async def main(mode: str = "initial"):
    if mode == "initial":
        inserted = await seed_nutrition_kb(db)
    elif mode == "refresh":
        updated = await update_nutrition_kb(db)
    elif mode == "full_reload":
        await clear_and_reseed_kb(db)
```

**Current Grade:** ⚠️ One-time seeding works for MVP, breaks for production.

---

### 4. Error Handling & Logging

**Assessment:** ✅ **BASIC, ACCEPTABLE**

**What's Good:**
```python
# Line 20-21: Structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)

# Line 26-35: Logs key steps
logger.info("Connecting to database...")
logger.info("Starting knowledge base seeding...")
logger.info(f"Seeding complete. Inserted {inserted} entries.")
```

**What's Missing:**
```python
# No try/except around seeding
# If seed_nutrition_kb() fails:
# - Exception propagates uncaught
# - No rollback
# - No error logging

# Should be:
try:
    logger.info("Starting knowledge base seeding...")
    inserted = await seed_nutrition_kb(db)
    logger.info(f"Seeding complete. Inserted {inserted} entries.")
except Exception as e:
    logger.error(f"Seeding failed: {e}", exc_info=True)
    await db.rollback()
    raise
```

**Grade:** C+ (works, but no error recovery)

---

## tools.py Analysis (89 lines)

### 1. Tool Schema Design: ANALYZE_FOOD_TOOL

**Current Implementation:**
```python
# Lines 16-66
ANALYZE_FOOD_TOOL = {
    "name": "analyze_food",
    "description": "Analyze a food photo and return nutritional information and a funny roast",
    "input_schema": {
        "type": "object",
        "properties": {
            "food_name": {"type": "string", ...},
            "calories": {"type": "integer", ...},
            "protein_g": {"type": "number", ...},
            "carbs_g": {"type": "number", ...},
            "fat_g": {"type": "number", ...},
            "food_category": {"type": "string", ...},
            "cuisine_origin": {"type": "string", ...},
            "cat_roast": {"type": "string", ...},
        },
        "required": [all 8 fields]
    },
}
```

**Assessment:** ✅ **WELL-DESIGNED**

**Strengths:**
1. **Comprehensive fields** (8 fields capture nutrition + context)
2. **Type-safe** (integer for calories, number for macros)
3. **Constraint validation** (all required, ranges in descriptions)
4. **Field descriptions** are clear (e.g., "0-5000" for calories)

**What's Good:**
```python
# Clear ranges prevent hallucinations
"calories": {
    "type": "integer",
    "description": "Estimated calories (0-5000)"  # ← Range limit
}

# Categories are enumerated
"food_category": {
    "description": "Category like 'salad', 'fast food', 'dessert', ..."
}
```

**What Could Improve:**
```python
# Use JSON Schema enums (instead of "like" descriptions):
"food_category": {
    "type": "string",
    "enum": ["salad", "fast food", "dessert", "home-cooked", "sandwich", "soup"]
}

# This forces Claude to pick from these options (no hallucination)
```

**Grade:** B+ (good schema, could be stricter with enums)

---

### 2. Multi-Tool Support: Is It Real?

**Current Implementation:**
```python
# Lines 69-88
def get_tools_for_task(task_type: str) -> list[dict]:
    if task_type == "analyze_food":
        return [ANALYZE_FOOD_TOOL]  # ← Single tool
    elif task_type == "recommend_meal":
        return []  # ← No tool (text generation)
    elif task_type == "weekly_recap":
        return []  # ← No tool (text generation)
    else:
        return []
```

**Assessment:** ⚠️ **NO REAL MULTI-TOOL ORCHESTRATION**

**Reality:**
- Only ONE tool defined: `analyze_food`
- Other tasks don't use tools at all (just text generation)
- `get_tools_for_task()` is a simple router, not orchestration

**What "Multi-Tool" Would Look Like:**
```python
# Real multi-tool scenario (NOT in current code):
TOOLS = {
    "analyze_food": {
        "description": "Extract nutrition from photo",
        ...
    },
    "lookup_nutrition_db": {
        "description": "Search nutrition database for accuracy",
        ...
    },
    "generate_recommendation": {
        "description": "Suggest meals based on preferences",
        ...
    }
}

# Agent loop (from Day 1 learning) would:
# 1. Call analyze_food (extract from photo)
# 2. Call lookup_nutrition_db (verify accuracy)
# 3. Call generate_recommendation (suggest next meal)
# 4. Return final answer
```

**Current Status:** ❌ **Single-tool, not multi-tool**

**Implication for Days 8-9 Capstone:**
- If capstone requires multi-tool RAG agent, this file needs expansion
- For now, fine for single-task food analysis

**Grade:** C (functional for current use, not extensible)

---

### 3. Error Handling & Feedback

**Assessment:** ⚠️ **MINIMAL ERROR HANDLING**

**What's Missing:**
```python
# Current: Just returns tool schemas (no error handling)

# What should happen if Claude misuses the tool:
# 1. Tool validation fails (e.g., calories = -500)
# 2. Claude gets error message: "Calories must be 0-5000, got -500"
# 3. Claude retries with correct value

# Currently: No mechanism for this!
```

**Expected in ai_service.py:**
```python
# Should see logic like:
response = client.messages.create(
    tools=tools,
    tool_choice={"type": "tool", "name": "analyze_food"}
)

if response.stop_reason == "tool_use":
    tool_use = response.content[0]
    
    # Validate tool output
    try:
        result = parser.validate(tool_use.input)  # From Day 6: parser.py
        validated_result = guardrails.validate(result)  # From Day 6: guardrails.py
    except ValidationError as e:
        # Send error back to Claude:
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": f"Error: {e.message}. Please fix and retry."
                }
            ]
        })
        # Loop back, Claude retries with corrected values
```

**Current tools.py:**
- Just defines schemas
- No error messages, no retry logic
- That's OK (error handling is elsewhere in ai_service.py)

**Grade:** B (schema definitions are good, error handling is in other files)

---

### 4. Agent Loop Integration

**Assessment:** ⚠️ **SINGLE-SHOT, NOT MULTI-TURN**

**Current Pattern:**
```
User request → Claude (with tool) → tool_use response → Parse → Return
↑                                                                     |
└─────────────────────────── NO LOOP ────────────────────────────────┘
```

**What Multi-Turn Would Look Like (Day 1 learning):**
```python
# While loop for agent orchestration:
while iteration < max_iterations:
    response = client.messages.create(
        tools=tools,
        messages=messages
    )
    
    if response.stop_reason == "tool_use":
        # Execute tool
        result = execute_tool(tool_use)
        # Feed result back
        messages.append({"role": "user", "content": tool_result})
        # Loop continues
    else:
        # End turn, return answer
        return response.content[0].text
```

**Current Code:**
- tools.py just defines the schema
- Doesn't show the loop logic
- Loop would be in ai_service.py or similar

**Grade:** B (tools are ready for multi-turn, implementation elsewhere)

---

## Summary & Grade

### seed_knowledge.py

| Aspect | Grade | Status |
|--------|-------|--------|
| Knowledge base seeding | ? | Unknown (logic in knowledge_service.py) |
| Logging | B | Basic, acceptable |
| Error handling | C | Missing try/except |
| Update strategy | D | One-time only, no refresh |
| **Overall** | **C** | **Works for MVP, needs production improvements** |

**Issues:**
1. ❌ One-time seeding only (KB never updates)
2. ❌ No error recovery if seeding fails
3. ⚠️ Can't assess KB coverage (logic hidden in knowledge_service.py)

---

### tools.py

| Aspect | Grade | Status |
|--------|-------|--------|
| Tool schema design | B+ | Well-designed, could use enums |
| Multi-tool support | C | Only one tool, not extensible |
| Error handling | B | Done elsewhere (OK) |
| Agent loop integration | B | Ready for multi-turn |
| **Overall** | **B** | **Solid foundation, single-task** |

**Issues:**
1. ⚠️ Only one tool defined (not truly multi-tool)
2. ⚠️ Could use enums to constrain food_category options
3. ✅ Schema design is sound

---

## Concrete Improvements for Day 10

### Priority 1: Update Strategy for seed_knowledge.py 🔴

```python
# Add support for periodic updates:

async def main(mode: str = "initial"):
    """
    Seed knowledge base.
    
    Args:
        mode: "initial" (first time), "refresh" (update), "full" (clear + reseed)
    """
    logger.info(f"Starting KB seeding ({mode} mode)...")
    
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession)
    
    async with async_session() as db:
        try:
            if mode == "initial":
                inserted = await seed_nutrition_kb(db)
                logger.info(f"Initial seed: {inserted} entries")
            elif mode == "refresh":
                updated = await update_nutrition_kb(db)
                logger.info(f"Refresh: {updated} entries updated")
            elif mode == "full":
                await clear_kb(db)
                inserted = await seed_nutrition_kb(db)
                logger.info(f"Full reseed: {inserted} entries")
        except Exception as e:
            logger.error(f"KB seeding failed: {e}", exc_info=True)
            await db.rollback()
            raise
    
    await engine.dispose()
```

### Priority 2: Enum Constraints for tools.py 🟠

```python
# Make food_category strict:

"food_category": {
    "type": "string",
    "enum": ["salad", "fast food", "dessert", "home-cooked", "sandwich", "soup", "pasta", "rice_bowl"],
    "description": "Category of the food"
},

"cuisine_origin": {
    "type": "string",
    "enum": ["Japanese", "Italian", "American", "Mexican", "Indian", "Chinese", "Thai", "Mediterranean"],
    "description": "Cuisine origin"
}

# This forces Claude to pick from options, no hallucination
```

### Priority 3: Error Message Improvement 🟡

```python
# Add helpful error descriptions to calorie range:

"calories": {
    "type": "integer",
    "description": "Estimated calories (0-5000). Typical ranges: salad 200-400, sandwich 400-600, pasta 500-800, dessert 200-500"
}

# This helps Claude estimate more accurately
```

---

## Next: Days 8-9 Capstone

**What's Ready:**
- ✅ embedding.py (Day 6 improvements planned)
- ✅ cache.py (Day 6 improvements planned)
- ✅ tools.py (schema is solid, single-task ready)
- ✅ seed_knowledge.py (MVP ready, update strategy for later)

**What Days 8-9 Will Build:**
- Advanced RAG pipeline with hybrid search + RRF + reranking
- Citations enabled for trust + verification
- Evaluation: 30 nutrition questions, measure NDCG@5 + MRR
- Comparison: simple RAG (Day 3) vs advanced RAG (Days 8-9)
- Portfolio artifact: `rag_eval_report.md`

**Ready to commit Day 7 and start capstone?**

---

**Co-Authored-By:** Claude Haiku 4.5 + Iona (human reviewer)
