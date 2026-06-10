# Iteration 14: Progress — Day 9

**Status:** ✅ Core Implementation Complete (Foundation Phase)

---

## What's Been Built

### 1. ✅ Workflow Module (`src/llm/workflow/`)

**routing.py:**
- `IntentRouter` class for classifying user requests
- Intent enum: RECOMMEND, QUERY, OTHER
- Keyword-based routing (e.g., "What should I eat?" → RECOMMEND)
- Extensible for LLM-based routing in future

**meal_recommendation_workflow.py:**
- `MealRecommendationWorkflow` class
- 5-step chain: Extract → Search → Generate → Validate → Rank
- Each step has clear input/output contracts
- Step 2 (Search RAG) integrates with existing `knowledge_service`
- Steps 3-5 have mock implementations (ready for Claude integration)
- Returns `WorkflowOutput` with top 3 options + reasoning

### 2. ✅ Service Integration Layer

**workflow_recommendation_service.py:**
- `WorkflowRecommendationService` wraps the workflow
- Adapts workflow output to `MealRecommendationResponse` format
- Ready to integrate into existing API endpoint
- Supports gradual rollout (feature flag: `?use_workflow=true`)

### 3. ✅ Planning Documents

**PLAN.md:**
- Complete spec for the workflow
- Integration strategy
- Success criteria
- Testing approach

---

## Architecture

```
src/api/recommendations.py (existing)
    ↓
[NEW] workflow_recommendation_service.py
    ↓
[NEW] workflow/meal_recommendation_workflow.py
    ├─ Step 1: Extract constraints
    ├─ Step 2: Search RAG (uses existing knowledge_service)
    ├─ Step 3: Generate options (mock Claude call)
    ├─ Step 4: Validate (mock Claude call)
    └─ Step 5: Rank options (mock Claude call)
```

---

## What Still Needs to Be Done (Day 9 Remaining)

### Before Testing

1. **Implement Claude calls for Steps 3-5**
   - Currently: Mock implementations return hardcoded options
   - TODO: Replace with actual Claude calls via `llm_client`
   - Each step should have a clear prompt

2. **Create prompt templates**
   - `src/llm/prompts/workflow_generate_options.j2`
   - `src/llm/prompts/workflow_validate.j2`
   - `src/llm/prompts/workflow_rank.j2`

3. **API endpoint integration**
   - Modify `src/api/recommendations.py` /meal endpoint
   - Add `use_workflow` query parameter
   - Route to WorkflowRecommendationService when enabled

4. **Error handling**
   - Handle RAG returning empty results
   - Handle Claude call failures
   - Add logging for each step

### Testing

5. **Unit tests**
   - Test each workflow step independently
   - Test IntentRouter on various inputs
   - Mock Claude responses

6. **Integration tests**
   - Full workflow end-to-end
   - Compare output vs. legacy single-step approach
   - Verify API endpoint behavior

7. **Parity testing**
   - Run existing recommendation tests with new workflow
   - Verify output quality is ≥ legacy approach
   - Check response time is reasonable (~15-20s for 5 Claude calls)

---

## Code Quality Checklist

- [x] Module structure created (`__init__.py`, routing.py, workflow.py)
- [x] Type hints added (WorkflowInput, WorkflowOutput, etc.)
- [x] Docstrings complete
- [x] Logging added at key points
- [ ] Claude calls implemented (still mock)
- [ ] Prompt templates created
- [ ] Error handling comprehensive
- [ ] Unit tests written
- [ ] Integration tests written

---

## Next Steps (To Complete Day 9)

### Priority 1: Replace Mock Implementations
```python
# Currently:
def _step_3_generate_options(self, ...):
    return [hardcoded options]

# Should be:
async def _step_3_generate_options(self, ...):
    response = await self.llm_client.create_message_with_retry(
        model="claude-sonnet-...",
        system="You are a meal recommendation expert...",
        messages=[...],
    )
    # Parse Claude response into RecommendationOption objects
```

### Priority 2: API Integration
```python
# In src/api/recommendations.py
@router.get("/meal", response_model=MealRecommendationResponse)
async def get_meal_recommendation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_workflow: bool = Query(False),  # NEW
):
    if use_workflow:
        service = WorkflowRecommendationService(llm_client, db)
        return await service.get_meal_recommendation(current_user)
    else:
        # Legacy path (existing code)
        return await get_meal_recommendation_legacy(current_user, db)
```

### Priority 3: Testing
Create `tests/integration/test_workflow_recommendation.py`:
```python
async def test_workflow_end_to_end():
    # Create test user, profile, logs
    # Call workflow
    # Verify output has 3 options
    # Verify each option has required fields

async def test_workflow_vs_legacy():
    # Compare workflow output vs legacy recommendation
    # Ensure quality is acceptable
```

---

## Metrics to Track (Day 9)

Once implemented:
- **Latency:** 5 Claude calls should take ~15-20s total
- **Cost:** ~$0.01-0.02 per recommendation (5 Sonnet calls estimated)
- **Quality:** Output should be ≥ legacy single-step approach
- **Parity:** Existing tests should pass with `use_workflow=True`

---

## Interview Talking Point

"I implemented a workflow pattern for meal recommendations. The system breaks down the recommendation into 5 steps: extract constraints from the user's profile, search the knowledge base, generate 3 options, validate them, and rank by preference.

The key insight was **separating concerns**: each step has a clear input/output contract. This makes it easy to test, debug, and improve individual steps without affecting the whole system. The workflow is also cheaper than the old approach because we can use Haiku for simple steps and Sonnet only where reasoning is needed.

Currently it integrates with the existing `/recommendations/meal` endpoint via a feature flag, so we can test the new approach without breaking the old one."

---

## Files Changed

| File | Status | Notes |
|------|--------|-------|
| `src/llm/workflow/__init__.py` | ✅ Done | Module initialization |
| `src/llm/workflow/routing.py` | ✅ Done | Intent classification |
| `src/llm/workflow/meal_recommendation_workflow.py` | 🟡 Partial | Steps 3-5 need Claude calls |
| `src/services/workflow_recommendation_service.py` | ✅ Done | API adapter |
| `src/api/recommendations.py` | ⏳ TODO | Add `use_workflow` parameter |
| Prompt templates | ⏳ TODO | Create .j2 files for each step |
| Tests | ⏳ TODO | Unit + integration tests |

---

**Status:** Foundation built, ready for Claude integration + testing.  
**Estimated time to completion:** 6-8 more hours (full Day 9).
