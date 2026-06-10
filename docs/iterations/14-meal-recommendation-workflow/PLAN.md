# Iteration 14: Meal Recommendation Workflow

**Status:** Planning (Phase 5 Day 9)  
**Goal:** Integrate prompt chaining workflow into NomNom's meal recommendation system.

---

## What We're Building

A **structured 5-step workflow** for meal recommendations that replaces the current single-step recommendation logic.

### Current State
```
API request → Get user profile → Build query → Search RAG → 
Call LLM once → Return recommendation
```

### Target State
```
API request → Intent router → Workflow pipeline
    Step 1: Extract constraints (targets, restrictions, preferences)
    Step 2: Search RAG (find relevant meals)
    Step 3: Generate options (create multiple recommendations)
    Step 4: Validate (check nutritional accuracy)
    Step 5: Rank (order by user preference)
    → Return top 3 recommendations
```

---

## Key Changes

### 1. New Module: `NomNom-Backend/src/llm/workflow/`

```
src/llm/workflow/
  ├─ __init__.py
  ├─ routing.py              # Intent classifier
  ├─ meal_recommendation_workflow.py   # 5-step chain
  └─ handlers/
      └─ default_handler.py   # Fallback for unclassified intents
```

### 2. New Components

**routing.py:**
- Classify user intent: "what did I eat?", "what should I eat?", "am I hitting goals?"
- Route to appropriate workflow (recommendation vs. query vs. progress check)

**meal_recommendation_workflow.py:**
- Step 1: Extract constraints (call Claude to parse user profile + targets)
- Step 2: Search RAG (retrieve relevant meals from knowledge base)
- Step 3: Generate options (call Claude to create 3 recommendation options)
- Step 4: Validate (call Claude to validate nutritional claims)
- Step 5: Rank (call Claude to rank by user preference)

### 3. Integration with Existing Code

**Keep existing:** `src/api/recommendations.py`
- Modify the `/meal` endpoint to use new workflow
- Preserve the same response format (MealRecommendationResponse)
- Add opt-in flag: `?use_workflow=true` to test new behavior

**What changes:**
```python
# Old (single-step)
response = await llm_client.create_message_with_retry(...)
return MealRecommendationResponse(recommendation=response.text)

# New (workflow)
workflow = MealRecommendationWorkflow(llm_client, db)
result = await workflow.execute(user_profile, today_logs)
return MealRecommendationResponse(
    recommendations=result.top_3_meals,
    reasoning=result.reasoning
)
```

---

## Success Criteria

- [ ] `routing.py` implemented and tested
- [ ] `meal_recommendation_workflow.py` implements all 5 steps
- [ ] Integration point added to `src/api/recommendations.py`
- [ ] Workflow produces valid MealRecommendationResponse
- [ ] Workflow output matches or exceeds Day 3 sandbox quality
- [ ] API endpoint callable with `?use_workflow=true` flag
- [ ] Tests pass (existing tests for recommendations)

---

## Testing Strategy

### Unit Tests
- Each step of workflow tested independently
- Mock LLM calls using cached responses
- Verify Step 2 (RAG search) returns meals
- Verify Step 3 (generation) produces valid JSON

### Integration Tests
- Full workflow end-to-end
- Compare workflow output vs. single-step recommendation
- Verify API endpoint returns proper response format
- Check that Day 3 sandbox tests still pass (parity)

### Manual Testing
- Call endpoint with real user data
- Verify 5-step workflow executes
- Check performance (should be 15-20s total)
- Verify cost is predictable (5 Claude calls)

---

## Effort Estimate

| Component | Effort | Notes |
|-----------|--------|-------|
| routing.py | 2 hours | Intent classification logic |
| meal_recommendation_workflow.py | 4 hours | 5-step chain implementation |
| Integration with API | 2 hours | Modify /recommendations/meal endpoint |
| Testing | 2 hours | Unit + integration + parity tests |
| **Total** | **10 hours** | ~1 work day |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Breaking existing /recommendations endpoint | High | Add feature flag (`use_workflow=true`), preserve old path |
| Workflow too slow (multiple Claude calls) | Medium | Cache intermediate results, measure latency |
| Parity with Day 3 sandbox | Medium | Run existing tests against new workflow |
| Token cost explodes | Medium | Use Haiku for Steps 1,2,4 and Sonnet for Step 3,5 |

---

## Timeline

- **Day 9 AM:** routing.py + meal_recommendation_workflow.py skeleton
- **Day 9 PM:** Implement all 5 steps, basic testing
- **Day 9 Evening:** Integration with API, parity testing
- **Day 10 AM:** Finalize, iterate on quality
- **Day 10 PM:** Create SUMMARY.md

---

## What This Teaches

✅ How to integrate workflow pattern into existing production code  
✅ How to maintain backward compatibility during refactors  
✅ How to measure workflow vs. single-step performance  
✅ How to structure multi-step LLM orchestration in FastAPI  
✅ Interview-ready: "I refactored the recommendation system to use prompt chaining..."

---

## Related Files

- **Day 2-3 Learning:** `learning_lab/phase_5/02_workflow_design.md`, `03_workflow_sandbox.py`
- **Existing Code:** `src/api/recommendations.py`, `src/services/knowledge_service.py`
- **Schemas:** `src/schemas/recommendation.py`

---

**Status:** ✏️ Planning (Ready to start Day 9)
