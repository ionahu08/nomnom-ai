# NomNom — Iteration 03: Guardrails, Observability & Cost Optimization

**Phase:** Phase 5 (full plan)

**Goal:** Add safety guardrails, semantic caching, AI call logging, rate limiting, and accuracy tracking.

**Resume Skills:** Guardrails, Cost Optimization, AI Observability, Model Evaluation

---

## What's Built

- LLM harness with retry, fallback, structured output
- Food photo analysis via Haiku (via harness)
- iOS camera + food logging

## What We're Building

**In Plain English:**

You now have a working AI system. But there are 5 problems:

1. **No safety checks** — Claude might return garbage (calories = 50,000)
2. **No cost optimization** — you pay for the same food photo analysis twice if someone takes the same lunch photo twice
3. **No visibility** — you have no idea how much money you're spending or how many API calls are happening
4. **No abuse protection** — a user could spam the camera button 1000 times and waste all your money
5. **No learning** — when a user corrects Claude's mistake, you don't track it or improve

This phase fixes all 5:

- **Guardrails:** Check Claude's response is sensible (calories 0-5000, not 50,000)
- **Semantic cache:** If someone eats pizza twice, use the cached result instead of calling Claude again (save money!)
- **AI call logging:** Log every call so you can see: "I spent $50 this week on Haiku calls"
- **Rate limiting:** Block users who spam the camera button (max 30 calls/hour)
- **Accuracy tracking:** When a user fixes Claude's mistake, record it. Track: "Claude was right 87% of the time"

## Phases

### Phase 5.1: Guardrails — Safety Checks

**In Plain English:**

Claude might return nonsense:
```
Photo of a salad
Claude says: "Calories: 50,000, Protein: -100g"
→ That's impossible!
```

Guardrails = safety checks. Before sending Claude's response to the user, verify it's sane:
```
Calories: between 0-5000? ✓ (no meal is 50k)
Protein: between 0-500g? ✓
Carbs: between 0-500g? ✓
Fat: between 0-500g? ✓
Food name: not empty, under 200 chars? ✓
Roast: not empty, under 500 chars? ✓

All checks pass → send to user
Any check fails → reject, try again (handled by parser)
```

#### 5.1.A: Create `src/llm/guardrails.py` — The Safety Checker

**What this does:**
```python
def validate_food_analysis(analysis):
  # Check 1: Calories reasonable?
  if analysis['calories'] < 0 or analysis['calories'] > 5000:
    return (False, "Calories out of range: " + analysis['calories'])
  
  # Check 2: Macros reasonable?
  if analysis['protein_g'] < 0 or analysis['protein_g'] > 500:
    return (False, "Protein out of range")
  
  # ... similar checks for carbs, fat, food name, roast ...
  
  # All checks passed!
  return (True, None)
```

If any check fails, the parser (Phase 3) knows to retry the AI call.

Files to create:
- `src/llm/guardrails.py` — output validation functions

#### 5.1.B: Test guardrails

What to test:
- Valid salad (350 cal, 20g protein) passes ✓
- Invalid pizza (50,000 cal) fails ✓
- Negative protein fails ✓
- Empty food name fails ✓

Files to create:
- `tests/unit/llm/test_guardrails.py` — test validation for valid/invalid inputs

Commands:
- `uv run pytest tests/unit/llm/test_guardrails.py -v`

---

### Phase 5.2: Semantic Caching — Save Money on Repeated Foods

**In Plain English:**

Problem: Users eat the same meals repeatedly.
- Monday: snap pizza photo → Claude analyzes → $0.01 cost
- Wednesday: snap same pizza photo → Claude analyzes again → another $0.01 cost
- Total: paid twice for the same analysis!

Solution: Cache the result. Next time you see similar pizza:
```
User takes pizza photo
  ↓
Check: Have we seen this pizza before? (similarity > 95%)
  ↓ Yes!
Return cached result (no API call, save money!)
  ↓ No
Call Claude, save embedding, return result
```

How it works:
- Convert photo to text embedding (using Phase 6 embeddings)
- Search past food logs for embeddings that match (>95% similarity)
- If found: use the cached analysis
- If not found: analyze with Claude, save embedding for future

**Note:** Phase 6 enables pgvector (vector database). For now, this is a stub that always calls the API. It becomes real in Phase 6.

#### 5.2.A: Create `src/llm/cache.py` — The Cache Lookup

**What this does:**
```python
def get_cached_analysis(photo_description):
  # Convert description to embedding (Phase 6)
  query_embedding = embed(photo_description)
  
  # Search past food_logs: "find embeddings 95%+ similar to this"
  similar_logs = database.search(
    table="food_logs",
    embedding=query_embedding,
    similarity_threshold=0.95
  )
  
  if similar_logs:
    return similar_logs[0].analysis  # Use cached result!
  else:
    return None  # Never seen before, need to analyze
```

Files to create:
- `src/llm/cache.py` — semantic cache lookup (stub for now, Phase 6 makes it real)

#### 5.2.B: Test cache lookup

What to test:
- Similar pizza found → returns cached result ✓
- Different salad → cache miss ✓
- Threshold works (95% similarity) ✓

Files to create:
- `tests/unit/llm/test_cache.py` — test cache hit/miss (mocked)

Commands:
- `uv run pytest tests/unit/llm/test_cache.py -v`

---

### Phase 5.3: AI Call Logging — See What's Happening & How Much You're Spending

**In Plain Language:**

Problem: You have no visibility into your AI usage.
- How many API calls did I make today?
- How much money did I spend?
- How fast is Claude responding?
- What models am I using most?

Solution: Log every call to a database. Then you can check: "I spent $50 on Haiku and $100 on Sonnet this week."

**What gets logged:**
```
{
  model: "claude-haiku-4-5-20251001",
  task_type: "analyze_food",
  input_tokens: 500,
  output_tokens: 200,
  latency_ms: 1200,  (took 1.2 seconds)
  estimated_cost: $0.003,  (calculated from token prices)
  success: true,
  cached: false,  (was this a cache hit?)
  created_at: 2026-04-06T10:30:00Z
}
```

Later you can query: "Show me all Haiku calls this week" → see total cost, average latency, etc.

#### 5.3.A: Add AiCallLog model — Store the logs

Create `src/models/ai_call_log.py`:
```python
# Database table to store AI call logs
# Columns:
# - id: unique ID
# - user_id: whose call was this?
# - model: "claude-haiku..." or "claude-sonnet..."
# - task_type: "analyze_food", "recommend_meal", etc.
# - input_tokens, output_tokens: how many tokens?
# - latency_ms: how long did it take?
# - estimated_cost: how much did it cost?
# - success: did it work?
# - error_message: if it failed, why?
# - cached: was a cached result used?
# - created_at: when did this happen?
```

Files to create/update:
- `src/models/ai_call_log.py`
- Update `src/models/__init__.py` — add AiCallLog

#### 5.3.B: Create alembic migration

Commands:
```bash
uv run alembic revision --autogenerate -m "add ai_call_logs table"
uv run alembic upgrade head
```

#### 5.3.C: Create `src/llm/logger.py` — Write to the Log

**What this does:**
```python
def log_ai_call(model, task_type, input_tokens, output_tokens, latency_ms, success):
  # Calculate cost from token prices
  if model == "haiku":
    input_cost = input_tokens * (0.80 / 1_000_000)  # $0.80 per 1M tokens
    output_cost = output_tokens * (4 / 1_000_000)   # $4 per 1M tokens
  else:
    input_cost = input_tokens * (3 / 1_000_000)     # $3 per 1M tokens
    output_cost = output_tokens * (15 / 1_000_000)  # $15 per 1M tokens
  
  total_cost = input_cost + output_cost
  
  # Insert row into ai_call_logs table
  database.insert({
    "model": model,
    "task_type": task_type,
    "input_tokens": input_tokens,
    "output_tokens": output_tokens,
    "latency_ms": latency_ms,
    "estimated_cost": total_cost,
    "success": success
  })
```

Files to create:
- `src/llm/logger.py` — logging functions

#### 5.3.D: Wire logging into LLMClient

Update `src/llm/client.py`:
- After each API call: call `logger.log_ai_call(...)`
- Pass: model, task_type, token counts, latency, success/failure

#### 5.3.E: Test logging

What to test:
- Haiku call logged correctly ✓
- Cost calculated right ✓
- Sonnet cost different from Haiku ✓
- Successful calls marked as success=true ✓
- Failed calls marked as success=false with error message ✓

Files to create:
- `tests/integration/test_ai_logging.py` — test log_ai_call inserts and calculates correctly

Commands:
- `uv run pytest tests/integration/test_ai_logging.py -v`

---

### Phase 5.4: Rate Limiting — Block Spam

**In Plain Language:**

Problem: A user could spam the camera button 1000 times in a row.
- Each call costs money (even if cached)
- Ties up your API quota
- Wastes bandwidth

Solution: Rate limiting. "You can only analyze 30 photos per hour. After that, wait."

```
User 1: takes 30 photos in 1 hour → all work ✓
User 1: takes photo 31 → ERROR "Too many requests. Limit: 30/hour"
User 1: waits 1 hour
User 1: takes photo 31 → works ✓
```

Same limit per user per task type:
- 30 "analyze food" calls per hour (most common)
- 10 "recommend meal" calls per hour (less common, slower)

#### 5.4.A: Create `src/llm/rate_limiter.py` — The Quota Checker

**What this does:**
```python
def check_rate_limit(user_id, task_type):
  current_count = get_call_count_this_hour(user_id, task_type)
  
  if task_type == "analyze_food":
    limit = 30
  elif task_type == "recommend_meal":
    limit = 10
  
  if current_count >= limit:
    return False  # User has hit their limit!
  else:
    increment_call_count(user_id, task_type)
    return True  # OK to proceed
```

Files to create:
- `src/llm/rate_limiter.py` — per-user rate limiting

#### 5.4.B: Wire rate limiting into API

Update `src/api/food_logs.py`:
```python
# In POST /analyze endpoint:
if not rate_limiter.check_rate_limit(user_id, "analyze_food"):
  return 429 error "Too many requests. Limit: 30/hour"

# If we get here, user is within limit
# Proceed with analysis...
```

#### 5.4.C: Test rate limiter

What to test:
- User 1-30: calls succeed ✓
- User 31: call fails with 429 error ✓
- Different users have separate limits ✓
- Hour passes → counter resets ✓

Files to create:
- `tests/unit/llm/test_rate_limiter.py` — test quota enforcement

Commands:
- `uv run pytest tests/unit/llm/test_rate_limiter.py -v`

---

### Phase 5.5: Accuracy Tracking — Measure How Good Claude Is

**In Plain Language:**

Problem: You don't know if Claude is getting better or worse over time.
- It said the pizza was 450 calories, but the user changed it to 350
- Was that a mistake by Claude, or was the user wrong?
- How often does Claude make mistakes?

Solution: Track user corrections. When a user edits a food log, that's data showing Claude was wrong.

```
Claude says pizza: 450 cal, 20g protein
User edits to: 350 cal, 25g protein
→ Record this as a "correction"
→ Can later calculate: "Claude was right 87% of the time"
```

**How it works:**
```
Metrics you can calculate:
- Total food logs analyzed: 100
- User corrected: 13
- Accuracy: (100 - 13) / 100 = 87%
```

#### 5.5.A: Add evaluation columns to FoodLog

Update `src/models/food_log.py`:
- Add `is_user_corrected` (bool) — did the user change this log?
- Add `ai_raw_response` (JSON) — store what Claude originally said

Alembic migration:
```bash
uv run alembic revision --autogenerate -m "add food_log columns for eval"
uv run alembic upgrade head
```

#### 5.5.B: Create `src/llm/evaluator.py` — Track Corrections

**What this does:**
```python
def record_correction(food_log, user_corrected_values):
  # Store what the user changed
  food_log.is_user_corrected = True
  food_log.ai_raw_response = {  # What Claude originally said
    "food_name": "pizza",
    "calories": 450
  }
  # What user changed it to is already in the FoodLog (user submitted new values)
  
  database.save(food_log)

def get_accuracy_metrics(user_id):
  total_logs = count logs for this user
  corrected_count = count logs where is_user_corrected = True
  accuracy = (total_logs - corrected_count) / total_logs * 100
  
  return {
    "total_logs": total_logs,
    "corrected": corrected_count,
    "accuracy_percentage": accuracy
  }
```

Files to create:
- `src/llm/evaluator.py` — correction tracking

#### 5.5.C: Wire evaluator into PATCH endpoint

Update `src/api/food_logs.py`:
```python
# When user edits a food log:
@router.patch("/{log_id}")
async def update_food_log(log_id, updated_data):
  food_log = get_food_log(log_id)
  old_values = {
    "food_name": food_log.food_name,
    "calories": food_log.calories
  }
  
  # User is changing something
  evaluator.record_correction(food_log, updated_data)
  
  # Save the changes
  food_log.food_name = updated_data.food_name
  food_log.calories = updated_data.calories
  database.save(food_log)
```

---

### Phase 5.6: AI Stats Endpoints — Dashboard to See Your Metrics

**In Plain English:**

You've logged all the data (calls, costs, corrections). Now expose it via API endpoints so the iOS app (or you) can see:
- "I spent $150 this week"
- "Claude was 89% accurate"
- "30% of my calls used the cache (saved money!)"

Endpoints:
```
GET /api/v1/ai-stats/summary?start_date=2026-01-01&end_date=2026-01-31
→ Returns: total calls, total tokens, total cost, average latency

GET /api/v1/ai-stats/accuracy
→ Returns: accuracy_percentage (87%), total_logs, corrected_count

GET /api/v1/ai-stats/cache-hit-rate
→ Returns: cache_hit_percentage (30%), total_cached_calls
```

#### 5.6.A: Create `src/schemas/ai_stats.py` — Response Format

Define what the API returns:
```python
# Response schemas:
# - AiStatsSummary
#   {
#     "total_calls": 500,
#     "total_input_tokens": 50000,
#     "total_output_tokens": 20000,
#     "total_cost": 0.25,
#     "avg_latency_ms": 1200
#   }
# - AiAccuracy
#   {
#     "accuracy_percentage": 87.0,
#     "total_logs": 100,
#     "corrected_count": 13
#   }
# - CacheHitRate
#   {
#     "cache_hit_percentage": 30.0,
#     "total_cached_calls": 150,
#     "total_calls": 500
#   }
```

Files to create:
- `src/schemas/ai_stats.py` — response schemas

#### 5.6.B: Create `src/api/ai_stats.py` — The Endpoints

**What this does:**

```python
@router.get("/summary")
async def get_stats_summary(
  start_date: date = None,
  end_date: date = None,
  current_user = Depends(get_current_user)
):
  # Query ai_call_logs for this user in date range
  calls = database.query(AiCallLog).filter(
    AiCallLog.user_id == current_user.id,
    AiCallLog.created_at >= start_date,
    AiCallLog.created_at <= end_date
  )
  
  # Calculate totals
  total_cost = sum(call.estimated_cost for call in calls)
  total_calls = len(calls)
  avg_latency = average(call.latency_ms for call in calls)
  
  return {
    "total_calls": total_calls,
    "total_cost": total_cost,
    "avg_latency_ms": avg_latency
  }
```

Files to create:
- `src/api/ai_stats.py` — stats endpoints

#### 5.6.C: Test AI stats endpoints

What to test:
- /summary returns correct totals ✓
- Date filtering works ✓
- /accuracy calculates percentage correctly ✓
- /cache-hit-rate counts cached vs uncached calls ✓
- Different users see only their own stats ✓

Files to create:
- `tests/integration/test_ai_stats.py` — test all stats endpoints

Commands:
- `uv run pytest tests/integration/test_ai_stats.py -v`

---

### Phase 5.7: Integration — Wire Everything Together

**In Plain Language:**

When a user takes a food photo, here's the complete flow:

```
User taps camera
  ↓
Backend receives photo
  ↓
1. Check rate limit → "Is this user within their 30/hour limit?"
   If no → return 429 error
  ↓
2. Check cache → "Have we seen this food before?"
   If yes → return cached result (skip steps 3-5!)
  ↓
3. Call Claude with retry/fallback → "Analyze this photo"
  ↓
4. Validate guardrails → "Are the calories realistic?"
   If no → reject, return error
  ↓
5. Log the call → "Record: Haiku, 500 tokens, $0.003, 1.2s latency"
  ↓
6. Return result to iOS app
```

#### 5.7.A: Update POST /analyze endpoint

Update `src/api/food_logs.py`:
```python
@router.post("/analyze")
async def analyze_food_photo(file, current_user = Depends(get_current_user)):
  # Step 1: Rate limiting
  if not rate_limiter.check_rate_limit(current_user.id, "analyze_food"):
    return 429 error "Too many requests"
  
  # Step 2: Cache check
  cached_result = cache.get_cached_analysis(file)
  if cached_result:
    logger.log_ai_call(..., cached=True)
    return cached_result
  
  # Step 3: Call Claude
  result = llm_client.create_message_with_retry(
    model="haiku",
    image_bytes=file,
    tools=food_analysis_tool
  )
  
  # Step 4: Guardrails
  is_valid, error = guardrails.validate_food_analysis(result)
  if not is_valid:
    return error
  
  # Step 5: Logging
  logger.log_ai_call(
    model="haiku",
    task_type="analyze_food",
    input_tokens=...,
    output_tokens=...,
    latency_ms=...,
    success=True,
    cached=False
  )
  
  return result
```

#### 5.7.B: Integration test — Test the whole flow

What to test:
- Rate limit blocks on 31st call ✓
- Cache hit returns cached result ✓
- Invalid guardrails rejected and retried ✓
- Logging records correct cost ✓
- All 5 steps work together ✓

Files to create:
- `tests/integration/test_analyze_with_guardrails.py` — full end-to-end flow

Commands:
- `uv run pytest tests/integration/ -v` — all integration tests pass

---

## Success Criteria

- [x] Guardrails validate all AI output before sending to user
- [x] Semantic cache prevents redundant API calls (stub now, functional in Phase 6)
- [x] Every AI call logged with cost, latency, tokens, success/failure
- [x] Rate limiting blocks users who exceed limits (30/hour for analyze, 10/hour for recommend)
- [x] User corrections tracked for accuracy measurement
- [x] AI stats endpoints show: summary, accuracy %, cache hit rate
- [x] All unit + integration tests pass
- [x] No AI calls reach users without going through: rate limiter → cache → LLMClient → guardrails → logger

## Next After Phase 5

Phase 6 enables pgvector (vector database) and makes semantic caching actually work. Phase 7 adds RAG recommendations with streaming.
