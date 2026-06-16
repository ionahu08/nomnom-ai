# Technical Q&A — NomNom Interview Prep

25+ common technical questions with complete answers. Organized by topic. Each answer is 2-3 minutes of talking.

---

## Section 1: Semantic Caching & Embeddings

### Q1: Explain semantic caching. Why not just use Redis?

**Answer:**

"Semantic caching solves a problem Redis can't: similarity.

**The problem:** Food items aren't identical. 'Salmon bowl,' 'salmon with rice,' 'salmon & vegetables' are different dishes but nutritionally similar. Redis with exact matching has 15% hit rate—useless.

**The solution:** Embed meal photos semantically. When a new photo comes in:
1. Extract embedding (sentence-transformers, MiniLM-L6)
2. Query pgvector: 'Find embeddings similar to this (cosine similarity > 0.82)'
3. If found, return cached analysis instantly
4. If not found, call Claude, store result

**Why pgvector over Redis:**
- Redis: key → value lookup (exact match only)
- pgvector: vector → similar vectors (fuzzy match)
- Result: 85% hit rate vs. 15% with exact match

**Why pgvector over Pinecone/Weaviate:**
- One database instead of multiple services
- Simpler deployment
- Sufficient performance for scale

**Tradeoff:** Slightly higher latency on cache miss (embedding computation ~200ms), but 85% hit rate justifies it.

**In production:** 500+ meals, 85% cache hit rate, validated with human judgment on edge cases."

**Follow-ups likely:**
- "How do you validate the threshold is correct?" → See Talking Point 1 in INTERVIEW_STORY.md
- "What about cache invalidation?" → LRU with max 10K embeddings per user
- "How does embedding model affect accuracy?" → MiniLM-L6 is fast; considered larger models but not necessary

---

### Q2: Why threshold 0.82? How did you choose it?

**Answer:**

"Not arbitrary. Empirical validation.

**Process:**
1. Created dataset of 150 real meal photos (variety: sushi, pizza, salads, bowls, sandwiches)
2. Manually categorized meals into similarity groups (is 'salmon bowl' similar to 'salmon with rice'?)
3. Tested thresholds: 0.70, 0.75, 0.80, 0.82, 0.85, 0.90, 0.95
4. For each threshold, measured:
   - **Hit rate:** % of queries that find a match
   - **False positives:** % of matches that shouldn't be cached together
   - **Precision/recall tradeoff:** 

| Threshold | Hit Rate | False Positives | Decision |
|-----------|----------|-----------------|----------|
| 0.95 | 40% | <0.1% | Too strict |
| 0.82 | 85% | <1% | **Sweet spot** |
| 0.70 | 95% | 8% | Too loose |

**Why 0.82?**
- 85% hit rate is high enough to matter (reduces costs 60%)
- <1% false positives is acceptable (caching 'chicken' as 'salmon' is bad, but rare)
- Empirically validated, not just guessed

**Additional validation:**
- Deployed and monitored for 2 weeks
- Manually reviewed 50+ cached results to confirm they're sensible
- Added regression test: `test_semantic_cache_threshold_tuning`

**If asked 'couldn't you tune it further?'**
Yes, but diminishing returns. Moving from 0.82 to 0.80 might improve hit rate by 1%, but increases false positives from 1% to 3%. Not worth it."

**Follow-ups likely:**
- "What if threshold needs to change by cuisine type?" → Good idea for future (per-cuisine thresholds), current system is uniform
- "How do you measure false positives?" → Manual review + user feedback (none reported)
- "What embedding model did you consider?" → sentence-transformers MiniLM-L6 for speed; could use larger for better quality but not necessary

---

### Q3: How does the embedding model affect cache hit rate?

**Answer:**

"Good question. Embedding model is crucial.

**Model choice: sentence-transformers MiniLM-L6**
- Small: 22M parameters (vs. 335M for larger models)
- Fast: ~50ms per embedding (vs. 200ms for larger)
- Accurate enough: captures meal similarity well

**Why MiniLM-L6 and not larger?**
- Tested: MiniLM-L6 vs. paraphrase-MiniLM-L12 vs. sentence-transformers/all-mpnet-base-v2
- Results: All three achieve ~85% hit rate on meal recognition
- MiniLM-L6 is 5x faster and uses less GPU
- For food recognition, size doesn't matter much
- For poetry or legal documents, larger models might matter

**Impact on threshold:**
- Different embedding models produce different vector spaces
- MiniLM-L6's cosine similarity ~0.82 is optimal
- If you switched to all-mpnet, you'd need to retune threshold (maybe 0.80)

**In production:**
- Embeddings cached (precomputed, not recalculated)
- Model weights loaded once on startup
- Total inference time: 50ms per new photo

**If scaling:** 
- MiniLM-L6 is CPU-efficient; no GPU needed
- Could batch embeddings for throughput (process 10 photos in parallel)
- Didn't do this yet because latency is already low"

**Follow-ups likely:**
- "Would a larger model improve accuracy?" → Probably by 1-2%, not worth the cost/speed tradeoff
- "How do you handle new embedding models?" → Would need to recompute all cached embeddings and retune threshold (non-trivial migration)
- "What about fine-tuning the embedding model?" → Interesting idea, but would need labeled meal similarity data (expensive to collect)

---

### Q4: Walk me through the RAG pipeline. When does it retrieve vs. generate?

**Answer:**

"RAG powers personalized recommendations. Here's the flow:

**Trigger:** User asks 'What should I eat for better digestion?'

**Step 1: Retrieve relevant context**
```
Query: 'What should I eat for better digestion?'
Retrieve from knowledge base:
  - User's food history (past 30 days)
  - User's health profile (allergies, medical conditions)
  - Past meals user rated highly (5/5)
  - Foods that made user feel bad (logged as 'caused bloating')
```

**Step 2: Identify patterns**
Claude analyzes retrieved context:
- 'User logged dairy sensitivity last week'
- 'User rated grilled chicken 5/5'
- 'User's goal is 120g protein/day'

**Step 3: Generate personalized response**
Claude generates:
'Based on your digestion issues with dairy, I'd recommend: grilled chicken with steamed vegetables and fermented foods (tempeh, miso). You rated this pattern 5/5 before, and it hits your protein target.'

**Implementation:**
- RAG retrieval: SQL queries on PostgreSQL (food history, health profile)
- Context injection: Passed to Claude as system context
- Generation: Claude uses context to generate response

**Why RAG vs. fine-tuning?**
- RAG is dynamic (changes with user data)
- Fine-tuning is static (needs retraining)
- RAG scales better (add new user, no retraining needed)

**Tradeoff:**
- RAG requires real-time retrieval (adds ~1s latency)
- Fine-tuning would be faster but stale
- Current approach: acceptable latency, dynamic updates

**In production:**
- Retrieval latency: <500ms
- Generation latency: 1-2s
- Total: <2.5s response time"

**Follow-ups likely:**
- "How do you rank retrieved results?" → Keyword + semantic similarity (hybrid search)
- "What if retrieval returns irrelevant results?" → Guardrails validate output, if bad we fallback to generic advice
- "How do you handle queries outside your knowledge base?" → RAG gracefully degrades; Claude generates reasonable advice with less context
- "How would you scale retrieval to 1M users?" → Partition by user, shard database, or use specialized vector DB

---

## Section 2: Multi-Turn Conversation & Context

### Q5: How do you maintain conversation context across multiple turns?

**Answer:**

"This was a challenge. The naive approach (pass only current message to Claude) loses context.

**Problem example:**
```
Turn 1: User: 'I'm allergic to dairy.' Claude remembers.
Turn 2: User: 'What should I eat?' Claude forgets dairy allergy.
Turn 3: Claude suggests milk-based foods. Wrong.
```

**Solution: Conversation history threading**

Server maintains full conversation history:
```python
conversation = [
    {'role': 'user', 'content': "I'm allergic to dairy."},
    {'role': 'assistant', 'content': "Got it, no dairy..."},
    {'role': 'user', 'content': 'What should I eat?'},
    {'role': 'assistant', 'content': 'Grilled chicken...'},
    {'role': 'user', 'content': 'Vegetarian options?'},
]

# Every request includes full history
response = claude.messages.create(
    model='claude-3-5-sonnet',
    system=system_prompt,
    messages=conversation  # All 10 turns, not just current
)
```

**Token economy:**
- Conversation history uses tokens (cost increases with longer chats)
- Solution: Keep last 10 messages + dynamically retrieve user health profile
- Result: ~3.2K tokens per request (acceptable)

**Cache invalidation:**
- Store conversation in PostgreSQL
- Lazy-load history on every request
- If user deletes a message, all subsequent messages are invalidated (ensures consistency)

**Stateless API:**
- API itself is stateless (no in-memory conversation state)
- Database is source of truth
- Multiple API instances can handle the same conversation (scales horizontally)

**In production:**
- 20+ turn conversations maintain perfect context
- Regression test: `test_nutrition_coach_context_preservation_20_turns`
- User feedback: 'App remembers my preferences'"

**Follow-ups likely:**
- "Why not use memory components?" → Tried, but explicit history is simpler and more controllable
- "How do you handle very long conversations?" → Archive old messages after 100 turns, keep recent in memory
- "What if user edits a message?" → Invalidate all subsequent messages (ensures consistency)

---

### Q6: How does tool use work in your nutrition coach?

**Answer:**

"Tool use lets Claude dynamically request data instead of pre-loading everything.

**Example:**
```
User: 'I want meals similar to what I ate last week'

Claude thinks: 'I need to know what user ate last week'
Claude uses tool: 'retrieve_food_history(start_date=7_days_ago, limit=10)'
Server responds: [salmon bowl, grilled chicken, ...]

Claude thinks: 'I also need protein targets'
Claude uses tool: 'get_user_health_profile()'
Server responds: {protein_goal: 120g, tdee: 2400, ...}

Claude generates: 'You ate salmon (5/5 rating) and chicken (4/5). Both meet your 120g protein target...'
```

**Why tool use vs. pre-fetching?**
- Pre-fetch everything: Wastes tokens if Claude doesn't need it
- Tool use: Claude decides what data it needs
- Result: Fewer tokens, faster response

**Tools defined:**
- `retrieve_food_history(start_date, end_date, limit)`
- `get_user_health_profile()`
- `search_nutrition_database(query, filters)`
- `get_meal_ratings(meal_id)` — What the user rated this meal

**Implementation:**
```python
tools = [
    {
        'name': 'retrieve_food_history',
        'description': '...',
        'input_schema': {...}
    }
]

response = claude.messages.create(
    model='claude-3-5-sonnet',
    tools=tools,
    tool_choice='auto'  # Let Claude decide when to use tools
)

if response.stop_reason == 'tool_use':
    # Claude requested a tool
    tool_result = execute_tool(response.tool_use_block)
    # Pass result back to Claude
```

**Structured output validation:**
- Tool outputs validated against schema (Pydantic)
- If Claude generates bad tool use, we reject it and ask for clarification

**In production:**
- Avg 2-3 tool calls per request
- Each tool call latency: <200ms
- Total: well under 2s response time"

**Follow-ups likely:**
- "What if Claude uses wrong tool?" → Guardrails catch it, we send error back with schema
- "How do you prevent infinite loops?" → Set max_iterations = 10 (Claude can make up to 10 tool calls per request)
- "Can Claude hallucinate tool results?" → No, we don't use tool_use_message; we return actual data

---

## Section 3: Architecture & System Design

### Q7: Explain the orchestrator-worker pattern. Why not single agent?

**Answer:**

"This pattern parallelizes independent tasks. Reduced latency 60s → 25s (67% improvement).

**Workflow without orchestration (sequential):**
```
User uploads photo
  ↓ Claude analyzes photo (2s)
  ↓ RAG searches food history (1s)
  ↓ Claude generates recommendations (2s)
  ↓ Log cost & metrics (0.5s)
Total: 5.5s
```

**With orchestrator-worker (parallel):**
```
User uploads photo
  ├─ Worker 1: Claude analyzes photo (2s)
  ├─ Worker 2: RAG searches food history (1s)
  ├─ Worker 3: Log cost & metrics (0.5s)
  └─ All complete in: 2s (bottleneck)
Orchestrator: Gather results, format response (0.5s)
Total: 2.5s
```

**Why this works:**
- Workers are independent (don't need results from each other)
- Bottleneck is longest task (photo analysis, 2s)
- Other workers finish before bottleneck (no idle time)

**Implementation:**
```python
class MealRecommendationOrchestrator:
    async def orchestrate(self, photo):
        # Launch 3 workers in parallel
        analysis_task = asyncio.create_task(
            worker_analyze_photo(photo)
        )
        rag_task = asyncio.create_task(
            worker_retrieve_context(user_id)
        )
        cost_task = asyncio.create_task(
            worker_track_cost(user_id, model)
        )
        
        # Wait for all to complete
        analysis, context, cost = await asyncio.gather(
            analysis_task, rag_task, cost_task
        )
        
        # Orchestrator: combine results
        recommendation = claude.generate_recommendation(
            analysis, context
        )
        return recommendation
```

**Tradeoffs:**
- Slightly more complex (asyncio, error handling)
- Harder to debug (three things running at once)
- Worth it: 2.5x faster response

**Real-world result:**
- v1 (sequential): 60s average
- v2 (orchestrated): 25s average
- Measured: end-to-end timing on 100+ real requests

**If scaled to 1M users:**
- Would need more workers (photo analysis is slow at scale)
- Could add worker pool + job queue (Celery)
- Pattern stays the same, just more workers"

**Follow-ups likely:**
- "What if one worker fails?" → Timeout after 10s, return partial results
- "How do you balance workers?" → Load-balanced via async queue
- "Could you add more workers?" → Yes, pattern is extensible

---

### Q8: How do you handle API rate limiting?

**Answer:**

"Rate limiting prevents cost explosions and abuse.

**Problem:** Without limits, users could spam requests and explode API costs.

**Solution: Token bucket algorithm**
```
Each user gets a 'bucket' with tokens:
- Bucket capacity: 20 tokens
- Refill rate: 1 token / 60 seconds
- Cost per request: 1 token

User action:
- Request 1: 20 → 19 tokens (allowed)
- Request 2 (10s later): 19 tokens (allowed)
- Request 3 (15s later): 19 tokens (allowed, not enough time to refill)
- Request 4 (immediately): Denied (no tokens)
- Wait 60s: 1 token refilled, now 20
```

**Implementation:**
```python
from fastapi_limiter import FastAPILimiter

@app.post('/api/photos/analyze')
@limiter.limit('20/hour')  # 20 requests per hour per user
async def analyze_photo(photo):
    # Process request
    return recommendation
```

**Why 20 requests/hour?**
- Average user: 3 meals/day = 3 requests/day
- Peak user: 10 meals/day = 10 requests/day
- Overhead for typos, retries: 20 is safe limit
- Prevents abuse (not restricting legitimate use)

**Monitoring:**
- Track usage per user
- Alert if user exceeds 15 requests/hour (early warning)
- Hard limit at 20 (requests rejected)

**Cost impact:**
- Prevents rogue users from bankrupting system
- Fair use: keeps costs proportional to users

**In production:**
- No users hitting limits yet (traffic is small)
- Monitored and ready to scale"

**Follow-ups likely:**
- "Why not unlimited?" → Cost; unbounded API calls = unbounded costs
- "How do you handle burst traffic?" → Token bucket allows bursts (if user has 20 tokens, they can make 20 instant requests)
- "What if legitimate user hits limit?" → They contact support, we increase limit

---

### Q9: Describe your error handling strategy

**Answer:**

"Production systems need graceful degradation. Here's my approach:

**Layers of error handling:**

**Layer 1: Input validation**
```python
@app.post('/api/photos/analyze')
async def analyze_photo(photo: UploadFile):
    # Validate file size
    if photo.size > 10MB:
        raise HTTPException(413, 'Photo too large')
    
    # Validate file type
    if photo.content_type not in ALLOWED_TYPES:
        raise HTTPException(415, 'Unsupported file type')
```

**Layer 2: API client errors**
```python
try:
    response = claude.messages.create(
        model='claude-3-5-sonnet',
        messages=[...]
    )
except APIConnectionError:
    # Network issue
    return cached_result or generic_fallback()
except RateLimitError:
    # Claude API limit hit
    queue_request_for_later()
except APIStatusError as e:
    # 5xx error on Claude side
    log_error(e)
    return generic_fallback()
```

**Layer 3: Output validation**
```python
try:
    result = parser.parse(claude_response)
    # Validate against schema
    nutrition_data = NutritionSchema(**result)
except ValidationError:
    # Claude returned malformed JSON
    log_error(f'Parsing failed: {claude_response}')
    return generic_fallback()
```

**Layer 4: Timeouts**
```python
response = await asyncio.wait_for(
    claude_request(),
    timeout=10.0  # 10 second timeout
)
# If exceeds 10s, TimeoutError, return cached result
```

**Fallback strategy:**
- **Cache hit?** Return cached analysis (instant, free)
- **No cache?** Return generic fallback ('This meal has mixed macros. Log in your food diary and adjust based on your goals.')
- **User impact:** Slightly worse UX, but service stays up

**In production:**
- Log every error with context (user_id, request_id, timestamp)
- Alert on error rate > 1% (something is broken)
- Graceful degradation: users get *something*, not 500 error

**Monitoring:**
- Track error types (APIConnectionError, ValidationError, TimeoutError)
- Trend over time (are errors increasing?)
- Route to on-call engineer if critical error"

**Follow-ups likely:**
- "How do you test error paths?" → Integration tests with mock Claude API failures
- "What if Claude API is down?" → Return cached results or generic advice
- "How do you prevent cascading failures?" → Circuit breaker pattern (stop calling Claude if 50% of requests fail)

---

## Section 4: Data & Testing

### Q10: How do you test an LLM-based system?

**Answer:**

"Testing LLMs is hard because outputs are non-deterministic. Here's my approach:

**Deterministic tests (90% of tests):**
```python
def test_semantic_cache_hit_rate():
    # Load 150 real meal photos
    meals = load_test_dataset()
    
    # Run through cache
    cache = SemanticCache(threshold=0.82)
    hits = 0
    for meal in meals:
        if cache.find_similar(meal.embedding):
            hits += 1
    
    # Assert hit rate
    assert hits / len(meals) == 0.85
    # This is deterministic: same input → same output
```

**Output validation tests:**
```python
def test_nutrition_coach_output_schema():
    response = coach.chat('What should I eat?')
    
    # Validate structure
    assert 'recommendations' in response
    assert 'reasoning' in response
    
    # Validate types
    for rec in response['recommendations']:
        assert isinstance(rec['meal'], str)
        assert isinstance(rec['protein_g'], float)
    
    # Validate ranges
    assert 0 < rec['protein_g'] < 500  # Reasonable bounds
```

**Model grading tests (for quality metrics):**
```python
def test_nutrition_coach_quality():
    # Golden dataset: (input, expected_quality_score)
    test_cases = [
        ('I want to gain weight', 4),  # Should score 4/5 (good advice)
        ('What's the weather?', 1),    # Should score 1/5 (off-topic)
    ]
    
    for query, expected_quality in test_cases:
        response = coach.chat(query)
        
        # Use grader (another Claude call) to evaluate
        score = grader.grade_response(query, response)
        assert score >= expected_quality - 0.5  # Allow some variance
```

**Integration tests:**
```python
def test_end_to_end_recommendation():
    # User uploads photo
    photo = load_test_photo('salmon_bowl.jpg')
    analysis = analyzer.analyze(photo)
    
    # Check analysis makes sense
    assert 'protein' in analysis
    assert analysis['protein'] > 0
    
    # Get recommendation
    recommendation = recommender.get_recommendation(user_id, analysis)
    
    # Check recommendation is relevant
    assert any(meal in recommendation for meal in ['grilled chicken', 'salmon'])
```

**Regression tests (for production bugs):**
```python
def test_conversation_context_preserved():
    # Regression test for 'context loss' bug
    coach.chat('I am allergic to dairy')  # Turn 1
    coach.chat('What should I eat?')      # Turn 2
    response = coach.chat('Any vegetarian options?')  # Turn 3
    
    # Should NOT suggest milk-based foods
    assert 'milk' not in response.lower()
    assert 'cheese' not in response.lower()
    # (This test failed before the fix, passes after)
```

**Test coverage:**
- Unit tests: 40+ (semantic cache, parser, guardrails)
- Integration tests: 60+ (API endpoints, E2E workflows)
- Manual QA: Periodic review of real outputs
- Total: 100+ tests, all passing

**Why not 100% test coverage?**
- LLM outputs are non-deterministic (can't unit test the prose)
- Testing prose quality requires human judgment or expensive graders
- Trade-off: test structure + validate quality with graders"

**Follow-ups likely:**
- "How do you handle flaky tests?" → Deterministic tests don't flake; model graders have tolerance ranges
- "How do you test cost tracking?" → Mock Claude API calls and verify cost calculations
- "Do you A/B test?" → Not yet (too small user base), but architecture supports it

---

### Q11: Walk me through your deployment and testing pipeline

**Answer:**

"Every commit goes through this pipeline:

**Local development:**
```bash
# Write code + tests
git add .

# Run tests locally
pytest tests/

# Check code quality
ruff check src/
ruff format src/

# Commit if all pass
git commit -m '...'
git push origin main
```

**CI/CD pipeline (GitHub Actions):**
```yaml
on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - checkout code
      - install dependencies (pytest, ruff)
      - run tests (timeout 5 min)
      - run linting (ruff check)
      - report coverage
      
  deploy:
    needs: test  # Only deploy if tests pass
    runs-on: ubuntu-latest
    steps:
      - build Docker image
      - push to registry
      - deploy to staging
      - smoke test (basic health check)
      - deploy to production
```

**Gates before deployment:**
1. All tests pass ✅
2. No linting errors ✅
3. Code coverage > 80% ✅
4. Manual code review ✅ (for changes to llm/ or api/)
5. Staging smoke test passes ✅

**What prevents deployment:**
- Test failures → Fix and resubmit
- Linting errors → Fix and resubmit
- Coverage drop → Add tests or exclude files
- Code review feedback → Address and resubmit
- Staging smoke test fails → Investigate before deploying to production

**Rollback strategy:**
- Production deployment is tagged (v1.0, v1.1, etc)
- If something breaks, revert to previous tag
- Investigate root cause, fix, redeploy
- Max rollback time: ~5 minutes (we have monitoring alerts)

**Monitoring in production:**
- Error rate dashboard (alert if > 1%)
- Latency dashboard (alert if p95 > 5s)
- Cost dashboard (alert if daily cost > $5)
- Logs aggregated (DataDog or similar)

**In practice:**
- Deploy 1-2x per day
- Avg deployment time: 5 minutes
- Rollback rate: ~1% of deployments (something unexpected)
- MTTR (mean time to recovery): ~10 minutes"

**Follow-ups likely:**
- "What if a deployment breaks production?" → Rollback to previous version, investigate, fix in staging, redeploy
- "How do you handle database migrations?" → Backward compatible migrations (add column, then deploy code, then remove old column)
- "Do you do blue-green deployment?" → Not yet, but infrastructure supports it

---

## Section 5: LLM-Specific Decisions

### Q12: Why Claude Sonnet instead of Opus or GPT-4?

**Answer:**

"This was a rigorous model selection process, not just picking the cheapest.

**Evaluation criteria:**
- Accuracy on meal recognition (% correct macros)
- Latency (response time)
- Cost per request
- Quality of recommendations (subjective, but important)

**Testing methodology:**
1. Created 150 real meal photos (variety: sushi, pizza, salads, bowls)
2. Tested each model on same 50 photos
3. Measured accuracy: did it correctly identify protein, carbs, fat?
4. Timed each request
5. Calculated cost per request

**Results:**

| Model | Accuracy | Latency | Cost/Request |
|-------|----------|---------|--------------|
| Opus | 98% | 2.3s | $0.12 |
| Sonnet | 96% | 0.8s | $0.04 |
| GPT-4V | 97% | 1.8s | $0.015 (unavailable) |

**Analysis:**

- **Accuracy:** 98% vs 96% is 2% difference. In nutrition, 2% macro error (~3g) is immaterial for advice. Acceptable tradeoff.

- **Latency:** 2.3s vs 0.8s is 3x faster. User experience is significantly better. Worth the 2% accuracy hit.

- **Cost:** $0.12 vs $0.04 is 70% cheaper. Per-request cost is fundamental (scales to millions of users). More important than per-model accuracy.

**Decision:** Sonnet

**Why not Opus?**
- Not 2% better quality for 3x cost
- Latency is worse (users abandon slow apps)
- Semantic caching makes up any quality difference

**Why not GPT-4V?**
- Unavailable when I started
- OpenAI's Vision API is worse than Claude's for food
- Would need API key change (vendor lock-in)

**Post-launch validation:**
- User feedback: zero complaints about accuracy
- Engagement increased 3.2x (likely due to faster response time)
- Cost: $2/day for 100 users (sustainable)

**If accuracy mattered more:**
- Medical diagnosis → need 99%+ accuracy → use Opus despite cost
- Legal document review → need 99%+ accuracy → use Opus
- Food tracking → 96% is fine → use Sonnet

**The lesson:** Don't optimize for one variable. Consider accuracy, speed, cost holistically."

**Follow-ups likely:**
- "Would fine-tuning Sonnet on food photos improve accuracy?" → Possibly, but would need labeled data (expensive)
- "What if users complain about accuracy?" → We have monitoring; if error rate spikes, we can A/B test Opus
- "How would you A/B test model choice?" → Route 10% of traffic to Opus, measure accuracy + satisfaction

---

### Q13: How do you manage prompt versioning?

**Answer:**

"Prompts are product assets, not code. They change constantly.

**Problem:** Without versioning, you can't track why output changed or rollback bad prompts.

**Solution: Prompt versioning system**

```python
# Current prompt (v3)
NUTRITION_COACH_PROMPT_V3 = """
You are a nutrition coach. Analyze user food logs and provide personalized advice.

Guidelines:
- Consider user's health profile (allergies, medical conditions, goals)
- Reference specific meals user ate (grounding, not generic)
- Suggest realistic swaps (not just 'eat salad')
- Acknowledge constraints (budget, taste preferences)
"""

# Previous prompt (v2) - archived but trackable
NUTRITION_COACH_PROMPT_V2 = """
You are a nutrition coach. Provide meal advice.
...
"""

# Usage:
response = claude.messages.create(
    model='claude-3-5-sonnet',
    system=NUTRITION_COACH_PROMPT_V3,
    messages=[...]
)
```

**Tracking changes:**
```python
PROMPT_HISTORY = {
    'v1': {'date': '2026-05-15', 'change': 'Initial version'},
    'v2': {'date': '2026-05-22', 'change': 'Added constraint handling'},
    'v3': {'date': '2026-06-01', 'change': 'Emphasize specific meal swaps'},
}
```

**Why versioning matters:**
- User gets worse output → check git log, see which prompt changed
- Want to rollback → revert to v2 with one line change
- Compare approaches → A/B test v2 vs v3 (10% of traffic each)
- Document decisions → why did we change from v2 to v3?

**In practice:**
- Tried 7 prompt versions (currently on v3)
- v1: Generic advice (users complained 'you don't know me')
- v2: Added context retrieval (better but cold responses)
- v3: Emphasized specific meal swaps (current version, best engagement)

**Testing prompts:**
```python
def test_nutrition_coach_mentions_specific_meals():
    response = coach.chat('What should I eat for weight loss?')
    
    # Prompt v1: Fails (generic advice)
    # Prompt v2: Passes (mentions user meals)
    # Prompt v3: Passes (specific swaps: 'swap pasta for chicken')
    
    assert any(meal in response for meal in user.past_meals)
```

**A/B testing:**
- Prompt v2 for 10% of users
- Prompt v3 for 90% of users
- Track engagement metrics (do they rate advice as helpful?)
- If v2 performs better, revert
- If v3 is better, switch to 100%

**Lesson:** Treat prompts like features. Version, test, iterate."

**Follow-ups likely:**
- "How do you evaluate which prompt is better?" → User satisfaction ratings (would A/B test in production)
- "Do you automate prompt optimization?" → Interesting idea, but haven't done it (human-in-the-loop is safer)
- "How many prompts do you maintain?" → ~5 active (coach, analyzer, recommender, etc) + archive of past versions

---

## Section 6: Production & Operations

### Q14: How do you monitor cost in production?

**Answer:**

"Cost is a business metric, not just engineering. I track it obsessively.

**Cost tracking implementation:**

```python
from datetime import datetime

async def track_cost(
    user_id: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_hit: bool = False
):
    # Calculate cost
    if cache_hit:
        cost = 0  # Cached results are free
    else:
        # Sonnet pricing: $3/1M input, $15/1M output
        cost = (input_tokens * 3 / 1_000_000) + (output_tokens * 15 / 1_000_000)
    
    # Log to database
    db.create(AICallLog(
        user_id=user_id,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost=cost,
        cache_hit=cache_hit,
        timestamp=datetime.utcnow()
    ))
    
    # Update daily total
    db.update_daily_cost(cost)
```

**Dashboards:**

**Real-time dashboard:**
- Current daily cost: $2.15 (updated every 5 min)
- Cost trend (past 7 days)
- Cost per feature (photo analysis, recommendations, chat)
- Cost per user
- Cache hit rate

**Alerts:**
- If daily cost > $5 → Email ops team
- If cache hit rate < 70% → Something changed, investigate
- If cost per request > $0.10 → Possible infinite loop, investigate

**Cost breakdown (current):**
- Photo analysis: 70% of cost
- RAG retrieval: 20%
- Chat: 10%

**Weekly review:**
- Trends: going up or down?
- Anomalies: sudden spikes?
- Forecasting: if we 10x users, cost would be $20/day (sustainable?)

**In practice:**
- Noticed cost spike after Sonnet switch (explained in Talking Point 2 of INTERVIEW_STORY)
- Tracked down to higher volume (positive signal of engagement)
- Mitigated with semantic caching (reduced cost to $2)

**Lesson:** Measure costs early. Surprises at scale are expensive."

**Follow-ups likely:**
- "What's your target cost per user?" → $0.02/user/day (20M users = $400K/day, which is breakeven for mid-tier SaaS)
- "How do you reduce costs?" → Semantic caching (85% hit rate), model selection, batch processing
- "What if costs spike?" → Alert, investigate root cause, adjust rate limiting if needed

---

### Q15: Describe your logging and debugging strategy

**Answer:**

"Production bugs are discovered via logs, not local testing. Logging is crucial.

**Logging levels:**

```python
import logging

logger = logging.getLogger(__name__)

# DEBUG: Everything (local development only)
logger.debug(f'User {user_id} requested photo analysis')

# INFO: Important events
logger.info(f'Photo analyzed in {duration}ms')

# WARNING: Something unexpected
logger.warning(f'Cache hit rate below 70% (currently {hit_rate}%)')

# ERROR: Something failed
logger.error(f'Claude API call failed: {error}')

# CRITICAL: System down
logger.critical(f'Database connection lost')
```

**What to log:**

```python
async def analyze_photo(photo, user_id):
    start_time = time.time()
    request_id = uuid.uuid4()  # Trace requests end-to-end
    
    logger.info(
        f'Analyzing photo',
        extra={
            'request_id': request_id,
            'user_id': user_id,
            'photo_size': len(photo),
            'timestamp': datetime.utcnow().isoformat()
        }
    )
    
    try:
        # Check cache
        cached = cache.find_similar(photo)
        if cached:
            logger.info(
                'Cache hit',
                extra={'request_id': request_id, 'cache_age_days': 3}
            )
            return cached
        
        # Call Claude
        analysis = await claude.analyze(photo)
        
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            'Analysis complete',
            extra={
                'request_id': request_id,
                'duration_ms': duration_ms,
                'model': 'claude-3-5-sonnet'
            }
        )
        
    except APIConnectionError as e:
        logger.error(
            'API connection failed',
            extra={'request_id': request_id, 'error': str(e)},
            exc_info=True
        )
        # Return cached result or fallback
        return fallback_analysis
```

**Aggregation:**

- Logs sent to centralized system (DataDog, CloudWatch, etc)
- Searchable by: request_id, user_id, error_type, timestamp
- Alerts on error patterns (if errors spike, wake up on-call engineer)

**Debugging workflow:**

User reports: 'Photo analysis returned wrong macros'
```
1. Search logs by user_id
2. Find request_id from that timestamp
3. Filter logs by request_id (see entire flow)
4. Check: cache hit or cold call?
5. If cold call: check Claude's response (in logs)
6. If parsing error: check guardrails output
7. Root cause found: prompt ambiguity → fix prompt → redeploy
```

**Sensitive data:**

- Never log user's food photos (privacy)
- Never log API keys (security)
- Do log request_id, user_id, timing, error codes (debugging)

**In production:**
- ~1000 log lines/day (for 100 users)
- Average log query: 30 seconds to find root cause
- MTTR: ~10 minutes (find issue, understand it, decide on fix)"

**Follow-ups likely:**
- "How do you balance logging and performance?" → Structured logging is fast; concern is disk I/O, mitigated with async writes
- "How long do you retain logs?" → 30 days hot, 1 year archived
- "Do you log every API call?" → Yes, essential for debugging and cost tracking

---

## Section 7: Tradeoffs & Decision-Making

### Q16: What's a design decision you changed your mind about?

**Answer:**

"The cache threshold is a good example. And also conversation history threading.

**Example 1: Cache threshold**
- Initial: threshold = 0.95 (safe, minimize false positives)
- Result: 40% hit rate (not good enough)
- Lesson: Safety is good, but useless if it doesn't work
- Changed to 0.82: 85% hit rate, <1% false positives
- New tradeoff: slightly accept false positives to get real cache benefit

**Example 2: Conversation history threading**
- Initial: pass only current message to Claude (simple, fast)
- Result: context loss after 3 turns (users complain)
- Changed: store full history, pass last 10 messages
- New tradeoff: slightly higher cost (more tokens), but much better UX

**Example 3: Not yet decided: personalization vs. privacy**
- Currently: store all user meals in database (enables RAG)
- Tradeoff: user privacy (data could leak)
- Options:
  1. Encrypt at-rest (current approach, partial)
  2. End-to-end encryption (more private, harder to analyze)
  3. Federated learning (analyze without centralizing data, cutting-edge)
- Haven't decided yet because users don't care (scale is small)
- But would revisit at scale

**Meta-lesson:** Decisions aren't permanent. Revisit assumptions when data shows they're wrong."

**Follow-ups likely:**
- "Would you make different decisions now?" → Probably; with hindsight I'd start with semantic caching day 1, not week 6
- "How do you avoid bikeshedding on decisions?" → Set decision deadline, measure, move on. Don't ruminate.

---

### Q17: How would you approach debugging a production issue?

**Answer:**

"Structured troubleshooting.

**Scenario:** Users report 'recommendations are bad' (vague complaint)

**Step 1: Quantify the problem**
- How many users affected? (1 or 100?)
- Since when? (Today or this week?)
- Specific examples? (E.g., 'suggested milk despite dairy allergy')

**Step 2: Isolate the failure point**
```
Recommendation flow:
User profile → RAG retrieval → Claude generation → Response

Is the issue:
a) Bad user profile data? (Check database)
b) Bad RAG retrieval? (Check relevance scores)
c) Bad Claude generation? (Check prompt, check token usage)
d) Bad response formatting? (Check parsing)
```

Use logs to pinpoint which step failed.

**Step 3: Check recent changes**
- Did we deploy anything recently? (Check git log)
- Did we change the prompt? (Check prompt versioning)
- Did we change the retrieval logic? (Check schema changes)

**Step 4: Create a minimal reproduction**
```python
# If possible, reproduce locally
user = db.get_user('affected_user_id')
recommendation = recommender.get_recommendation(user)

# Does it still fail? If yes:
# - Problem is deterministic (good for debugging)
# - Can iterate locally without affecting users
```

**Step 5: Root cause analysis**
Example:
- Reproduction confirmed
- Logs show: Claude generated good advice but guardrails rejected it
- Reason: Schema mismatch (expected 'meal_name', got 'name')
- Root cause: Prompt change on June 15 broke schema
- Fix: Revert prompt to v2 or update guardrails to accept both fields

**Step 6: Deploy fix**
- Fix locally
- Run tests (regression test for this specific bug)
- Deploy to staging
- Smoke test
- Deploy to production
- Monitor error rate

**Step 7: Post-mortem**
- Why didn't we catch this before production?
- How do we prevent it again?
- (Could add test for prompt schema compatibility)

**Timeline:**
- Discovery: 5 min (user report)
- Triage: 5 min (quantify problem)
- Root cause: 15 min (logs + reproduction)
- Fix: 10 min (code change + tests)
- Deployment: 5 min
- MTTR: ~45 min

**Prevention:**
- Regression tests for common issues
- Staging smoke tests before production
- Monitoring alerts on error rates"

**Follow-ups likely:**
- "What if you can't reproduce locally?" → Use production logs, shadow traffic, A/B test fix
- "How do you avoid breaking things again?" → Add regression test, update documentation

---

## Section 8: Scaling & Future Work

### Q18: How would you scale this to handle 10x traffic?

**Answer:**

"Current system handles ~100 users. 10x = 1,000 users. Bottlenecks:

**Bottleneck 1: Claude API rate limits**
- Current: ~200 API calls/day
- 10x: ~2,000 API calls/day
- Claude's limit: 1,000,000 API calls/day (plenty of headroom)
- Action needed: None immediately, but monitor

**Bottleneck 2: Database queries**
- Current: ~1,000 queries/day (small)
- 10x: ~10,000 queries/day
- PostgreSQL handles millions/day
- Action needed: Add indexes on frequently queried columns, monitor query performance

**Bottleneck 3: Semantic similarity search (pgvector)**
- Current: 10K embeddings (1,000 users × 10 meals each)
- 10x: 100K embeddings
- pgvector can handle millions
- Action needed: Add index on embeddings (IVFFLAT or HNSW), monitor search latency

**Bottleneck 4: File storage (photos)**
- Current: ~1,000 photos × 5MB = 5GB
- 10x: 50GB
- Action needed: Migrate from local storage to S3, set up auto-cleanup (delete photos older than 1 year)

**Bottleneck 5: Cost**
- Current: $2/day
- 10x: $20/day
- Action needed: Monitor and optimize

**Infrastructure changes:**

1. **Database:**
   - Current: Single PostgreSQL instance
   - 10x: Same instance (sufficient), but add read replicas for analytics queries

2. **API server:**
   - Current: Single FastAPI instance
   - 10x: Load balancer + 2-3 instances (can scale horizontally, stateless)

3. **Cache:**
   - Current: pgvector (in PostgreSQL)
   - 10x: Add Redis cache in front (faster reads for hot data)

4. **Async tasks:**
   - Current: Synchronous (analysis happens in request)
   - 10x: Add job queue (Celery) for slow tasks (optional)

**What wouldn't change:**
- Core architecture (semantic caching, RAG, multi-turn loops)
- Model choice (Sonnet still cost-effective)
- API design (stateless, scalable)

**Timeline to 10x:**
- No changes needed immediately (current infra handles 10x)
- Optimize when actually hitting 10x load
- Premature optimization is bad"

**Follow-ups likely:**
- "What if you need to scale to 1M users?" → Different story (see INTERVIEW_STORY.md, Talking Point 4)
- "How would you estimate when you'd hit bottlenecks?" → Monitor metrics (latency, error rate, cost) and trending

---

### Q19: What are the biggest technical debt items?

**Answer:**

"Technical debt I know about (and accepted):

**Debt 1: Synchronous API for slow operations**
- Currently: Photo analysis happens in request (2-3s latency)
- Ideal: Async job queue (user gets immediate 'processing' response)
- Impact: Users wait for analysis
- Why I haven't fixed it: Latency is already acceptable (2.5s); job queue adds complexity
- When to fix: If latency becomes complaint (at scale)

**Debt 2: Conversation history in database**
- Currently: Stored in PostgreSQL, lazy-loaded
- Ideal: Cached in Redis (faster reads)
- Impact: Slight latency for multi-turn conversations
- Why I haven't fixed it: Acceptable latency; Redis adds infrastructure
- When to fix: When database becomes bottleneck

**Debt 3: Embedding model is frozen**
- Currently: MiniLM-L6 embeddings are precomputed
- Ideal: Allow model updates without recomputing all embeddings
- Impact: If we switch to new embedding model, would need to recompute 100K+ embeddings
- Why I haven't fixed it: Model is good enough; embedding migration is complex
- When to fix: If model performance degrades

**Debt 4: Prompt management is manual**
- Currently: Prompts in Python files, versioned by hand
- Ideal: Prompt management system (track changes, A/B test, rollback)
- Impact: Hard to track which prompt caused output quality change
- Why I haven't fixed it: Small enough to manage by hand; system would be overkill
- When to fix: When experimenting with 10+ prompt versions

**Debt 5: Limited error recovery**
- Currently: If Claude API fails, return cached/generic result
- Ideal: Retry with exponential backoff, queue failed requests, etc.
- Impact: Some users get degraded experience if API is down
- Why I haven't fixed it: Claude API is reliable; over-engineering for rare failure
- When to fix: If production incidents increase

**Total debt:** Low. System is clean. These are acceptable tradeoffs, not architectural problems.

**When I'd worry:**
- Tests failing regularly
- Code is hard to understand
- Performance is degrading
- Users complaining about reliability

None of these are happening."

**Follow-ups likely:**
- "How do you prevent debt from accumulating?" → Regular code reviews, retire features that don't work, refactor early
- "When do you pay down debt?" → When it starts impacting velocity or user experience, not preemptively

---

### Q20: What would you do differently if building this again?

**Answer:**

"With hindsight:

**1. Start with semantic caching (Day 1)**
- Currently: Added in week 6
- Should have: Started on day 1
- Why: Cache is foundational; everything else builds on it
- Impact: Would have discovered threshold tuning early, not week 6

**2. Start with output validation (Day 1)**
- Currently: Added in week 2-3 (Phase 2)
- Should have: Started immediately
- Why: Prevents 30% of bugs
- Impact: Would have caught parsing errors early

**3. Build monitoring first**
- Currently: Added after features
- Should have: Monitoring dashboard on day 1
- Why: Can't improve what you don't measure
- Impact: Would have caught cost spike earlier

**4. Test on real user data earlier**
- Currently: Tested on synthetic data, then real users
- Should have: Involve real users in private beta by week 2
- Why: Real data reveals assumptions that synthetic data misses
- Impact: Would have discovered prompt quality issues earlier

**5. Keep a decision log**
- Currently: Decisions scattered in BUGLOG.md files
- Should have: Centralized decision log (why was X chosen over Y?)
- Why: Helps onboard new people and avoid re-debating
- Impact: Would have clear record of 'why Sonnet over Opus'

**Overall approach:**
- Same architecture (semantic caching, RAG, orchestration)
- Same tech stack (FastAPI, PostgreSQL, Claude)
- Different emphasis (monitoring first, real user data earlier)

**The meta-lesson:** Don't solve the problem differently. Solve it faster with better visibility."

**Follow-ups likely:**
- "Would you use a different tech stack?" → Maybe use Supabase for PostgreSQL (less ops), but architecture is the same
- "Would you use a different LLM?" → GPT-4 Vision over Claude if available; Claude's Vision is good, but evaluating both is smart

---

## Section 9: Rapid-Fire Questions

Quick answers for edge cases:

### Q21: How do you handle schema migration with data?

**Schema change:** Add `allergies` column to user_profile table

```python
# Step 1: Add column (backward compatible)
alembic revision --autogenerate -m "Add allergies column"

# Step 2: Deploy code that handles both old (no allergies) and new (allergies) data
if user.allergies:
    # Use allergies in RAG
else:
    # Fallback to generic advice

# Step 3: Backfill old users (set allergies = null or ask them)
# Step 4: Remove fallback code in next deployment
```

**Key:** Migrations are backward compatible (deploy schema change, deploy code, remove old code)

---

### Q22: How would you implement A/B testing?

```python
# Route users to different experiences
if user_id % 10 < 5:  # 50% of users
    prompt = PROMPT_V2
else:
    prompt = PROMPT_V3

response = claude.messages.create(system=prompt, ...)

# Log which variant user saw
db.log_experiment('prompt', user_id, variant, timestamp)

# After 1 week, analyze results
results = db.query_experiment_results('prompt')
# Compare: satisfaction scores, engagement, cost per variant
```

---

### Q23: How do you test the prompt without deploying?

```python
# Local evaluation
def evaluate_prompt(prompt, test_cases):
    results = []
    for query, expected_quality in test_cases:
        response = claude.messages.create(system=prompt, messages=[...])
        score = grader.grade(response, query)  # Use another Claude call to grade
        results.append({
            'query': query,
            'response': response,
            'expected_quality': expected_quality,
            'actual_score': score
        })
    
    avg_score = sum(r['actual_score'] for r in results) / len(results)
    print(f"Prompt quality: {avg_score:.2f}/5")
    
    return results

# Before committing:
results = evaluate_prompt(NEW_PROMPT_V4, test_cases=GOLDEN_DATASET)
if avg_score >= 4.0:  # Good enough
    commit(NEW_PROMPT_V4)
```

---

### Q24: How do you handle user data deletion (GDPR)?

```python
async def delete_user(user_id):
    # Delete user data
    db.delete_user_profile(user_id)
    db.delete_food_logs(user_id)
    db.delete_chat_history(user_id)
    db.delete_photos(user_id)  # Or anonymize if backups
    
    # Delete embeddings
    cache.delete_user_embeddings(user_id)
    
    # Verify deletion
    remaining = db.query(f"SELECT * FROM users WHERE user_id = {user_id}")
    assert remaining is None
    
    logger.info(f"User {user_id} deleted (GDPR compliance)")
```

---

### Q25: How would you price this if it were a product?

**Pricing options:**

**Option 1: Per-request**
- Free tier: 5 requests/day
- Paid: $5/month for 100 requests/day
- Pro: $20/month for unlimited
- Risk: High-usage users break model (one person using 10x average)

**Option 2: Per-feature**
- Photo analysis: Free (attracts users)
- Recommendations: $5/month
- Nutrition coach: $10/month
- Risk: Fragmented experience

**Option 3: Freemium + subscription**
- Free: Photo analysis only (no caching, generic advice)
- Premium: $10/month (personalized, full features, priority support)
- Risk: Free tier users convert poorly

**My choice:** Freemium + subscription
- Free: 5 photo analyses/day (basic)
- $10/month: Unlimited photos + recommendations + nutrition coach

**Economics:**
- User acquisition: $5 CAC (customer acquisition cost)
- Lifetime value: 10 months × $10 = $100
- Payback period: 1 month (healthy)
- Infrastructure cost: $0.02/user/month (sustainable)"

---

## Recap: Key Numbers to Memorize

Before your interview, memorize these numbers:

| Metric | Value | Why |
|--------|-------|-----|
| Cache hit rate | 85% | Semantic caching works |
| Latency reduction | 60s → 25s (67%) | Orchestration works |
| Cost savings | 83% ($12 → $2/day) | Architecture > model |
| Semantic threshold | 0.82 (tuned 0.70-0.95) | Empirically chosen |
| Meal dataset | 150 photos | Validation sample size |
| Integration tests | 100+ | Production-ready |
| Accuracy drop (Sonnet) | 2% (98% → 96%) | Acceptable tradeoff |
| False positive rate | <1% | Caching is reliable |

---

## Last Thoughts

If you can explain these 25 questions with confidence, you'll crush the technical interview. The key is connecting each answer back to the core lesson:

**"I built an LLM system not by using a bigger model, but by architecting better. Semantic caching, orchestration, and monitoring unlock real performance."**

Good luck!

---

**Last Updated:** June 16, 2026  
**Status:** Ready for technical interviews  
**Reading Time:** ~30 minutes (all 25 Q&As)
