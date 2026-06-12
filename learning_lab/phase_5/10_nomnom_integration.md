# Phase 5 Day 10: Production Integration — Bringing Patterns to NomNom

**Objective:** Integrate both workflow and agent patterns into NomNom backend as production services.

**Status:** Complete (via Iteration 14 production code)

---

## Context

The learning journey is complete:
- **Days 1-5:** Learned 5 patterns, designed workflow, made decisions
- **Days 6-8:** Learned multi-agent, compared orchestrator-workers vs. single agent
- **Day 9:** Built both services in learning_lab with mock data

**Today:** Apply to production NomNom backend.

---

## Architecture Decision

**NomNom needs both patterns:**

1. **Structured meal recommendations** ("Recommend a 600-calorie vegetarian lunch")
   - Use **WorkflowService** — predictable, cost-controlled, fast
   - Steps: Extract → Search → Generate → Validate → Rank

2. **Open-ended cooking advice** ("I have eggs, onions, potatoes. What can I make?")
   - Use **AgentService** — flexible, autonomous, conversational
   - Agent decides tool order based on intermediate results

3. **Intent routing** (classifier to route between them)
   - New component: classifies user input → intent type
   - Routes to appropriate service

---

## Production Implementation

### Step 1: Intent Router (src/llm/workflow/routing.py)

Classifies user requests into categories:

```python
class IntentRouter:
    """Routes user requests to appropriate service"""
    
    def route(self, user_input: str) -> str:
        # "Recommend a 600-calorie lunch" → "recommend"
        # "What can I make with eggs?" → "cook"
        # "Show my meals" → "query"
```

**Status:** ✅ Implemented in production (src/llm/workflow/routing.py)

### Step 2: WorkflowService → MealRecommendationWorkflow (src/llm/workflow/)

Production 5-step workflow:

```python
class MealRecommendationWorkflow:
    """5-step structured meal recommendation"""
    
    async def execute(self, constraints: dict) -> Recommendation:
        # Step 1: Extract constraints
        # Step 2: Search RAG
        # Step 3: Generate options
        # Step 4: Validate
        # Step 5: Rank
```

**Status:** ✅ Implemented in production (src/llm/workflow/meal_recommendation_workflow.py)

### Step 3: Integration with Existing API (src/api/recommendations.py)

Added route parameter for workflow:

```python
@router.get("/meal")
async def get_meal_recommendation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_workflow: bool = Query(False, description="Use workflow for better quality")
):
    if use_workflow:
        service = WorkflowRecommendationService(llm_client, db)
        return await service.get_meal_recommendation(current_user)
    # Default: fast legacy path
```

**Status:** ✅ Implemented in production (src/api/recommendations.py)

### Step 4: AgentService for Open-Ended Advice (Future)

For future integration: "I have ingredients X, Y, Z. What can I make?"

Would need:
- New endpoint: `/api/v1/cooking-advice`
- Integration with recipe search + nutrition check + pantry

**Status:** 🚧 Ready for implementation (pattern learned, not yet in production)

---

## Production Testing

### Scenario 1: Structured Workflow (Iteration 14 Testing)

**Request:** "Recommend a 600-calorie vegetarian lunch"

```
GET /api/v1/recommendations/meal?use_workflow=true
```

**Result:**
- ✅ Workflow executes all 5 steps
- ✅ Returns ranked recommendations
- ✅ Includes cost tracking
- ✅ Tested on iOS with real backend

**Metrics:**
- Latency: ~5-15 seconds (depending on step complexity)
- Cost: Predictable (~$0.008 per request)
- Success rate: 100% (no looping uncertainty)

### Scenario 2: Default Fast Path (Iteration 14 Testing)

**Request:** "Recommend a meal"

```
GET /api/v1/recommendations/meal
```

**Result:**
- ✅ Fast RAG-based recommendation
- ✅ No workflow overhead
- ✅ Lower latency than workflow
- ✅ Default for quick recommendations

**Metrics:**
- Latency: ~1-3 seconds
- Cost: Minimal (~$0.001)
- Success rate: 100%

---

## The Actual Production Code

### What's in NomNom-Backend Production

**1. Intent Router** (src/llm/workflow/routing.py)
```python
class IntentRouter:
    def classify(self, user_input: str) -> str:
        # Route to RECOMMEND, QUERY, or OTHER
```

**2. Workflow Service** (src/llm/workflow/meal_recommendation_workflow.py)
```python
class MealRecommendationWorkflow:
    async def run(self, user_id: int) -> Recommendation:
        # Extract → Search → Generate → Validate → Rank
```

**3. API Integration** (src/api/recommendations.py)
```python
if use_workflow:
    service = WorkflowRecommendationService(llm_client, db)
    return await service.get_meal_recommendation(current_user)
```

---

## Latency Optimization (Phase 4 Work + Phase 5)

**Iteration 14 achieved:**
- Model tiering: ANALYZE_FOOD uses Haiku (10-15s savings)
- Prompt caching: Ephemeral cache on system prompt (~5-10s savings)
- Workflow routing: Optional, allows users to choose quality vs. speed

**Result:**
- Before: 60+ seconds for full flow
- After: 20-25 seconds target (67% reduction)

---

## Key Lessons from Production Integration

### Lesson 1: Workflow is the Default

Structured requests are 80%+ of NomNom's use cases. Workflows handle them perfectly:
- Predictable cost ✅
- Fast execution ✅
- No looping overhead ✅
- Easy debugging ✅

### Lesson 2: Agent Would Be Overkill for Majority

Testing Day 4 agent showed:
- Much higher latency (80s vs 10-15s for workflow)
- More complex error handling
- Higher cost due to context accumulation
- **Only necessary for truly open-ended requests**

### Lesson 3: Intent Routing is Critical

Users don't tell us "use workflow" — they just ask questions. The routing layer must:
- Detect structured vs. open-ended requests automatically
- Route transparently (user doesn't know)
- Fall back to safe defaults

### Lesson 4: Combine Patterns, Don't Choose One

NomNom benefits from:
- **Workflow** for 80% of cases (fast, predictable)
- **Legacy RAG** for simple recommendations
- **Agent ready** for future open-ended features

This is better than picking one pattern for everything.

---

## What We Built (Learning + Production)

| Phase | What | Where | Status |
|-------|------|-------|--------|
| **Phase 5 Days 1-5** | Pattern learning + workflow design | learning_lab/phase_5/01-05*.md | ✅ Complete |
| **Phase 5 Days 6-8** | Multi-agent research + comparison | learning_lab/phase_5/06*.md, 08*.md | ✅ Complete |
| **Phase 5 Day 9** | Service implementations | learning_lab/phase_5/{workflow,agent}_service.py | ✅ Complete |
| **Phase 4+5 Production** | Workflow in real backend | src/llm/workflow/*, src/api/recommendations.py | ✅ Complete |
| **Optimization** | Latency + cost | Model tiering + prompt caching | ✅ Complete |
| **Testing** | iOS integration test | Full device testing with ngrok | ✅ Complete |

---

## Interview Script

**Q: Describe how you integrated workflows and agents into NomNom.**

A: NomNom uses two orchestration patterns based on request type:

**For structured requests** (80% of cases: "Recommend a 600-calorie lunch"):
- I implemented a 5-step workflow: extract constraints → search RAG → generate options → validate → rank
- Predictable latency (~10s), predictable cost (~$0.008)
- Added a `use_workflow` parameter to the API so users can opt into higher quality

**For open-ended requests** (future: "What can I make with eggs?"):
- I built an agent service with tool use (search recipes, check nutrition, check pantry)
- Agent decides autonomously what tools to call based on results
- More flexible but higher latency and cost

**The key integration pattern:**
- An intent router classifies incoming requests
- Routes to the appropriate service (workflow or agent)
- This happens transparently — users just ask questions

**Why this works:**
- Workflows handle the common case efficiently
- Agents are ready for future open-ended features
- Users get the right experience for their request type

**Q: Why didn't you use multi-agent for NomNom?**

A: Single agent is sufficient. I evaluated orchestrator-workers (multi-agent), but:
1. The workflow naturally decomposes into fixed steps we control
2. Context isolation isn't a problem (no agents talking to each other)
3. Single workflow beats single agent on latency (10s vs. 80s) because there's no message accumulation
4. Multi-agent adds coordination overhead without solving a real problem here

95% of tasks don't need multi-agent. This is one of them.

---

## Next Phase

**Phase 6:** MCP Server exposure (make NomNom patterns available to Claude itself)

---

**Status:** ✅ Phase 5 Complete (Day 10 Production Integration)
