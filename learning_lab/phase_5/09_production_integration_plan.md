# Phase 5 Day 9: Production Integration

**Objective:** Bring both Workflow and Agent patterns into NomNom backend as reusable services.

**Context:** NomNom needs to handle two different user intents:
1. **Structured meal recommendations** (known steps) → Use Workflow pattern
2. **Open-ended cooking advice** (unknown path) → Use Agent pattern

---

## NomNom Use Cases

### Use Case 1: "Recommend a 600-calorie lunch"
```
Structured steps (always same):
  1. Extract constraints (600 cal, lunch)
  2. Search RAG for matching meals
  3. Generate 3 options with nutrition
  4. Validate each option
  5. Rank by user preferences

→ Use WORKFLOW (predictable, cost-controlled)
```

### Use Case 2: "I have eggs, onions, potatoes. What can I make?"
```
Open-ended (path unknown):
  - Agent might search recipes first OR check nutrition first
  - Agent decides based on intermediate results
  - No predetermined step order

→ Use AGENT (flexible, autonomous)
```

---

## Architecture

```
NomNom-Backend/src/
  services/
    ai_service.py (existing)
      ├─ Orchestrates LLM calls
      ├─ Handles retries, caching
      └─ Delegates to workflow/agent services
    
    workflow_service.py (NEW - Day 9)
      ├─ Meal recommendation workflow
      ├─ 5-step prompt chaining
      └─ Predictable, cost-controlled
    
    agent_service.py (NEW - Day 9)
      ├─ Open-ended cooking advice
      ├─ Agent loop with tool use
      └─ Flexible, autonomous
```

### Service Interfaces

**WorkflowService:**
```python
def recommend_meal(
    calories: int,
    diet_type: str,  # vegetarian, vegan, keto, etc.
    cuisine: str,
    user_id: int
) -> RecommendationResult:
    # Extract → Search → Generate → Validate → Rank
    # Returns: [meal1, meal2, meal3] with nutrition + reasoning
```

**AgentService:**
```python
def cook_with_ingredients(
    ingredients: list[str],
    constraints: dict,  # allergies, diet, time, etc.
    user_id: int
) -> CookingAdviceResult:
    # Agent loop: search recipes → check nutrition → suggest dish
    # Returns: reasoning + recommendation + alternative options
```

---

## Implementation Plan (Day 9)

### Phase 1: Create WorkflowService
```python
# learning_lab/phase_5/workflow_service.py

class WorkflowService:
    def recommend_meal(self, calories, diet_type, cuisine, user_id):
        # Step 1: Extract constraints
        constraints = self._extract_constraints(calories, diet_type, cuisine)
        
        # Step 2: Search RAG
        candidates = self._search_rag(constraints, user_id)
        
        # Step 3: Generate menus
        menus = self._generate_menus(candidates, user_id)
        
        # Step 4: Validate
        validated = self._validate_menus(menus, constraints)
        
        # Step 5: Rank
        ranked = self._rank_menus(validated, user_id)
        
        return ranked
```

### Phase 2: Create AgentService
```python
# learning_lab/phase_5/agent_service.py

class AgentService:
    def cook_with_ingredients(self, ingredients, constraints, user_id):
        client = anthropic.Anthropic()
        
        messages = [{"role": "user", "content": f"...{ingredients}..."}]
        
        while loop_count < max_loops:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                tools=[search_recipes, check_nutrition],
                messages=messages
            )
            
            if response.stop_reason == "end_turn":
                return extract_final_answer(response)
            
            if response.stop_reason == "tool_use":
                # Execute tool, accumulate results
                # Feed back to agent
```

### Phase 3: Integration Layer
```python
# learning_lab/phase_5/ai_service_integration.py

class AIServiceIntegration:
    def __init__(self):
        self.workflow = WorkflowService()
        self.agent = AgentService()
    
    def handle_user_request(self, user_input, user_id, intent):
        if intent == "recommend":
            # Structured request → Workflow
            return self.workflow.recommend_meal(...)
        
        elif intent == "cook":
            # Open-ended request → Agent
            return self.agent.cook_with_ingredients(...)
```

---

## What Gets Built (Day 9)

| File | Purpose |
|------|---------|
| `workflow_service.py` | Full implementation of 5-step workflow |
| `agent_service.py` | Full implementation of agent loop |
| `nomnom_tools.py` | Mock/real tools (search RAG, check nutrition, etc.) |
| `09_integration_test.py` | Test both services on real NomNom use cases |
| `09_comparison.md` | Compare performance on NomNom tasks |

---

## Success Criteria (Day 9)

- [ ] WorkflowService fully implemented
- [ ] AgentService fully implemented
- [ ] Both services tested on NomNom use cases
- [ ] Cost + latency measured for each
- [ ] Clear documentation on when to use each

---

## What Gets Built (Day 10)

Day 10 is the **capstone**: integrate the winning pattern into actual NomNom backend.

Likely outcome:
- **Workflow wins for recommendations** (predictable, cheaper)
- **Agent wins for open-ended advice** (flexible, user-friendly)
- **Both coexist** in backend, routed by intent classifier

---

## Interview Talking Point

"I built two LLM orchestration patterns and integrated them into NomNom. The workflow pattern handles structured tasks like meal recommendations (5 steps: extract → search → generate → validate → rank). The agent pattern handles open-ended requests like 'what can I cook with these ingredients?' where the path depends on intermediate results.

The key decision: I measured both on real NomNom use cases and found workflows are cheaper (predictable costs) while agents are more flexible (adapt to user needs). The backend uses an intent classifier to route between them."

---

**Status:** 🚀 Day 9 Starting (Production Integration)  
**Next:** Day 10 (Capstone + Production Merge)
