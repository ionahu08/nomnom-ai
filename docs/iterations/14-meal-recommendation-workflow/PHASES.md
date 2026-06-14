# Iteration 14: Phases — Meal Recommendation Workflow

---

## Overview

Iteration 14 implements a 5-step structured workflow for meal recommendations, replacing a single-call approach with a modular orchestration pattern that improves quality, debuggability, and testing.

---

## Phase 1: Workflow Architecture Design (Days 1-2)

**Goal:** Design the 5-step workflow pattern and data flow

### 1.1 Define Workflow Steps

**Step 1: Extract Constraints (No Claude)**
- Input: User profile (age, allergies, medical conditions, goals)
- Logic: Direct extraction from database
- Output: Constraints object (dietary_restrictions, allergies, macro_targets)

**Step 2: Search RAG (Database Query)**
- Input: Constraints
- Logic: Query knowledge_service for matching meals
- Output: List of candidate meals with nutrition info

**Step 3: Generate Options (Claude Sonnet)**
- Input: Constraints + RAG results
- Logic: Generate 3 meal options with reasoning
- Output: JSON with meal names, macros, reasoning
- Model: Sonnet (quality > cost for generation)

**Step 4: Validate Options (Claude Haiku)**
- Input: Generated options + constraints
- Logic: Validate nutritional accuracy and allergen safety
- Output: JSON with validation status, confidence, issues per option
- Model: Haiku (cost optimization, validation doesn't need reasoning)

**Step 5: Rank Options (Claude Haiku)**
- Input: Validated options + user preferences
- Logic: Rank by fit to user goals
- Output: JSON with rank (1-3), score, rationale per option
- Model: Haiku (cost optimization)

### 1.2 Define Data Contracts

```python
class WorkflowInput:
    user_id: int
    current_profile: UserProfile
    
class Constraints:
    allergies: list[str]
    medical_conditions: list[str]
    calorie_target: int
    macro_targets: dict

class WorkflowOutput:
    top_3_options: list[MealOption]
    reasoning: str
    validation_score: float

class MealOption:
    name: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    reasoning: str
    validation_status: str
    rank: int
    score: float
```

### 1.3 Define Error Handling Strategy

- JSON parsing failures → Fallback to defaults
- Claude failures → Skip step, continue with what we have
- Validation failures → Keep options anyway (graceful degradation)
- All failures logged for monitoring

---

## Phase 2: Core Module Implementation (Days 3-5)

**Goal:** Implement workflow module with all steps

### 2.1 Create Workflow Module Structure

**File:** `src/llm/workflow/__init__.py`
```python
from .routing import IntentRouter, Intent
from .meal_recommendation_workflow import MealRecommendationWorkflow
```

**File:** `src/llm/workflow/routing.py`
```python
class Intent(Enum):
    RECOMMEND = "recommend"      # "What should I eat?"
    QUERY = "query"              # "What's the nutrition in chicken?"
    OTHER = "other"              # "Tell me a recipe"

class IntentRouter:
    def classify(self, user_input: str) -> Intent:
        # Keyword-based routing (extensible for LLM-based in future)
        if any(word in user_input.lower() for word in ["eat", "meal", "recipe"]):
            return Intent.RECOMMEND
        if any(word in user_input.lower() for word in ["nutrition", "calories", "macro"]):
            return Intent.QUERY
        return Intent.OTHER
```

### 2.2 Implement Meal Recommendation Workflow

**File:** `src/llm/workflow/meal_recommendation_workflow.py`

```python
class MealRecommendationWorkflow:
    def __init__(self, llm_client, knowledge_service, logger):
        self.llm = llm_client
        self.knowledge = knowledge_service
        self.logger = logger

    async def run(self, user: User, profile: UserProfile) -> WorkflowOutput:
        # Step 1: Extract constraints
        constraints = self._extract_constraints(profile)
        
        # Step 2: Search RAG
        candidates = await self.knowledge.search(constraints)
        
        # Step 3: Generate options (Sonnet)
        options = await self._generate_options(constraints, candidates)
        
        # Step 4: Validate (Haiku)
        validated = await self._validate_options(options, constraints)
        
        # Step 5: Rank (Haiku)
        ranked = await self._rank_options(validated, profile)
        
        return WorkflowOutput(
            top_3_options=ranked[:3],
            reasoning="Generated with structured workflow",
            validation_score=self._calculate_confidence(validated)
        )

    async def _generate_options(self, constraints, candidates):
        # Uses workflow_generate_options.j2 template
        # Calls Claude Sonnet
        # Returns list of MealOption objects
        pass

    async def _validate_options(self, options, constraints):
        # Uses workflow_validate.j2 template
        # Calls Claude Haiku
        # Returns MealOption with validation_status added
        pass

    async def _rank_options(self, options, profile):
        # Uses workflow_rank.j2 template
        # Calls Claude Haiku
        # Returns MealOption with rank and score added
        pass
```

### 2.3 Create Prompt Templates

**File:** `src/llm/prompts/workflow_generate_options.j2`
```jinja2
You are a nutritionist generating meal recommendations.

User constraints:
- Allergies: {{ constraints.allergies | join(', ') }}
- Medical conditions: {{ constraints.medical_conditions | join(', ') }}
- Calorie target: {{ constraints.calorie_target }}

RAG results (candidate meals):
{% for meal in candidates %}
- {{ meal.name }}: {{ meal.calories }} cal, {{ meal.protein }}g protein
{% endfor %}

Generate 3 meal options that best fit the constraints.
Return JSON: [{"name": "...", "reasoning": "...", "calories": ..., "protein_g": ...}, ...]
```

**File:** `src/llm/prompts/workflow_validate.j2`
```jinja2
Validate these meal options for safety and accuracy:

{% for option in options %}
- {{ option.name }}: {{ option.calories }} cal, {{option.protein_g}}g protein
{% endfor %}

User constraints:
- Allergies: {{ constraints.allergies | join(', ') }}
- Medical conditions: {{ constraints.medical_conditions | join(', ') }}

Return JSON: [{"meal_name": "...", "valid": true/false, "confidence": 0.9, "issues": [...]}, ...]
```

**File:** `src/llm/prompts/workflow_rank.j2`
```jinja2
Rank these validated meal options by fit to user goals:

{% for option in options %}
- {{ option.name }}: {{ option.calories }} cal, validated: {{ option.valid }}
{% endfor %}

User goal: {{ profile.goal }}
Macro targets: Protein {{ profile.protein_target }}g, Carbs {{ profile.carb_target }}g

Return JSON: [{"meal_name": "...", "rank": 1-3, "score": 0.0-1.0, "rationale": "..."}, ...]
```

---

## Phase 3: Service Integration Layer (Days 6-7)

**Goal:** Wrap workflow for API consumption

### 3.1 Create Service Adapter

**File:** `src/services/workflow_recommendation_service.py`

```python
class WorkflowRecommendationService:
    def __init__(self, llm_client, knowledge_service, db):
        self.workflow = MealRecommendationWorkflow(llm_client, knowledge_service)
        self.db = db

    async def get_meal_recommendation(self, user: User) -> MealRecommendationResponse:
        # Fetch profile
        profile = await get_profile(self.db, user.id)
        
        # Run workflow
        output = await self.workflow.run(user, profile)
        
        # Adapt to existing API response format
        return MealRecommendationResponse(
            meal=output.top_3_options[0].name,
            calories=output.top_3_options[0].calories,
            protein_g=output.top_3_options[0].protein_g,
            # ... other fields
            alternatives=[option.name for option in output.top_3_options[1:3]]
        )
```

### 3.2 Design API Integration

**File:** `src/api/recommendations.py` (modify)

```python
@router.get("/meal", response_model=MealRecommendationResponse)
async def get_meal_recommendation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_workflow: bool = Query(False),  # Feature flag
):
    if use_workflow:
        # NEW: Use workflow
        service = WorkflowRecommendationService(llm_client, knowledge_service, db)
        return await service.get_meal_recommendation(current_user)
    else:
        # LEGACY: Keep existing code
        return await get_recommendation_legacy(current_user, db)
```

---

## Phase 4: Error Handling & Robustness (Days 7-8)

**Goal:** Make workflow production-ready

### 4.1 Implement Error Recovery

```python
async def _generate_options(self, constraints, candidates):
    try:
        response = await self.llm.call("sonnet", prompt, tool_choice="required")
        return self._parse_options(response)
    except JSONDecodeError:
        self.logger.warning("Failed to parse options, returning defaults")
        return [self._create_default_option()]
    except APIError as e:
        self.logger.error(f"Claude call failed: {e}")
        raise  # Let service handle it

async def _validate_options(self, options, constraints):
    try:
        response = await self.llm.call("haiku", prompt)
        return self._apply_validation(options, response)
    except Exception as e:
        self.logger.warning(f"Validation failed: {e}, keeping options anyway")
        # Graceful degradation: keep options without validation
        return options
```

### 4.2 Add Comprehensive Logging

```python
self.logger.info(f"Workflow started for user {user.id}")
self.logger.debug(f"Constraints: {constraints}")
self.logger.info(f"Step 3: Generating options with Sonnet")
self.logger.debug(f"Generated {len(options)} options")
self.logger.info(f"Step 4: Validating with Haiku")
self.logger.info(f"Workflow complete: {len(ranked)} ranked options")
```

---

## Phase 5: Local Testing & Verification (Day 9)

**Goal:** Verify workflow works before API integration

### 5.1 Manual Testing

- Create sample user profile
- Run workflow with different constraints
- Verify each step produces expected output
- Check error handling with simulated Claude failures
- Measure latency and estimate costs

### 5.2 Test Coverage Plan

**Unit tests:**
- Extract constraints
- Parse Claude responses (with markdown, without, errors)
- JSON schema validation

**Integration tests:**
- Full workflow with mocked Claude calls
- Full workflow with real Claude calls (local sandbox)
- Error recovery paths

---

## Cost & Performance Summary

**Per Recommendation:**
```
Step 1: 0ms (direct extraction)
Step 2: ~100ms (database query)
Step 3: ~3000ms, 1000 tokens input/output (Sonnet)
Step 4: ~2000ms, 400 tokens (Haiku)
Step 5: ~2000ms, 400 tokens (Haiku)

Total Latency: 7-8 seconds
Total Cost: ~$0.012-0.015

vs. Legacy (single call):
Latency: 3-5 seconds
Cost: ~$0.003-0.005
```

**Trade-off:** +2-3s latency, +$0.007-0.010 cost for better quality (3 ranked options + validation)

---

## Files Created

- ✅ `src/llm/workflow/__init__.py`
- ✅ `src/llm/workflow/routing.py`
- ✅ `src/llm/workflow/meal_recommendation_workflow.py`
- ✅ `src/services/workflow_recommendation_service.py`
- ✅ `src/llm/prompts/workflow_generate_options.j2`
- ✅ `src/llm/prompts/workflow_validate.j2`
- ✅ `src/llm/prompts/workflow_rank.j2`

## Files Modified

- 📝 `src/api/recommendations.py` (API integration, pending)

---

## Success Criteria

- ✅ Workflow module created and importable
- ✅ All 5 steps implemented
- ✅ Claude calls integrated (Steps 3, 4, 5)
- ✅ Prompt templates created
- ✅ Error handling comprehensive
- ✅ Logging at key points
- ⏳ API endpoint integration (pending)
- ⏳ Unit/integration tests (pending)
- ⏳ Production verification (pending)
