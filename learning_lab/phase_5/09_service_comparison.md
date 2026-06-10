# Phase 5 Day 9: Workflow vs. Agent Service Comparison

**Task:** Compare WorkflowService vs. AgentService on NomNom use cases.

---

## Use Case 1: Structured Meal Recommendation

**Request:** "Recommend a 600-calorie vegetarian lunch"

### WorkflowService (workflow_service.py)
```
Input: calories=600, diet_type=vegetarian

Step 1: Extract Constraints
  → {calories: 600, diet_type: vegetarian, max_prep_time: 30}

Step 2: Search RAG
  → Found 3 meals matching constraints

Step 3: Generate Menus
  → Generated 3 menu descriptions

Step 4: Validate Menus
  → Validated 3 menus (all passed)

Step 5: Rank by User Preference
  → Ranked and returned top 3 recommendations

Output: [Lentil Buddha Bowl, Vegetable Stir-Fry, Grilled Chicken Salad]
```

**Characteristics:**
- ✅ Predictable (always 5 steps)
- ✅ Cost-controlled (no looping, fixed steps)
- ✅ Fast (sequential but optimized)
- ❌ Rigid (can't adapt to user needs mid-way)

### AgentService (agent_service.py)
```
Input: "Recommend a 600-calorie vegetarian lunch"

Loop 1: Agent reads request
  → Decides: "I should search for recipes"
  → Calls search_recipes(ingredients)

Loop 2: Agent reads results
  → Decides: "I should check nutrition"
  → Calls check_nutrition(recipe_name)

Loop 3: Agent reads nutrition
  → Decides: "I have enough info"
  → Generates recommendation
  → stop_reason = end_turn

Output: "Based on your constraints, I recommend..."
```

**Characteristics:**
- ✅ Flexible (adapts to user needs)
- ✅ Conversational (can ask follow-up questions)
- ❌ Unpredictable (variable number of loops)
- ❌ Costly (loops can add up)

---

## Use Case 2: Open-Ended Cooking Advice

**Request:** "I have eggs, onions, potatoes. What can I make?"

### WorkflowService
```
Problem: This request doesn't fit the 5-step workflow.
- No fixed "calories" constraint
- No clear "extract → search → generate" flow
- User might need nutrition check, or recipe ideas, or both

❌ Not suitable
```

### AgentService
```
Input: "I have eggs, onions, potatoes. What can I make?"

Loop 1: Agent reads request
  → Decides: "I should check what else is in the pantry"
  → Calls check_pantry(user_id)

Loop 2: Agent reads pantry + input
  → Decides: "Now search for recipes with these ingredients"
  → Calls search_recipes(ingredients)

Loop 3: Agent reads recipes
  → Decides: "The user might care about nutrition"
  → Calls check_nutrition(best_recipe)

Loop 4: Agent has all info
  → Generates personalized recommendation
  → stop_reason = end_turn

Output: "You can make Spanish Tortilla! It's 350 calories, 
         uses your eggs/onions/potatoes, takes 20 minutes..."
```

**Characteristics:**
- ✅ Perfect for open-ended requests
- ✅ Adapts to user needs
- ✅ Can integrate multiple data sources (pantry, recipes, nutrition)
- ✅ Conversational

---

## Comparison Table

| Metric | WorkflowService | AgentService | When to Use |
|--------|-----------------|--------------|-----------|
| **Use Case** | Structured requests | Open-ended requests | See below |
| **Example** | "600 cal vegetarian" | "What can I make?" | Depends on user intent |
| **Latency** | Fast (sequential 5 steps) | Variable (depends on loops) | Workflow for speed |
| **Cost** | Predictable (~$0.01) | Variable (~$0.02-0.05) | Workflow for cost |
| **Flexibility** | Low (fixed steps) | High (adapts) | Agent for flexibility |
| **Code Complexity** | Simple (step-by-step) | Complex (loop logic) | Workflow is simpler |
| **Error Handling** | Easy (known steps) | Hard (unknown path) | Workflow is easier |
| **User Experience** | Direct answer | Conversational | Agent feels more natural |

---

## Decision Framework: Which Service to Use?

```
User request
    ↓
Is it a STRUCTURED REQUEST?
(Fixed format: "Recommend X calorie Y diet Z cuisine")

YES → WorkflowService
      Characteristics:
      - Known steps in advance
      - Input has clear structure
      - Output format is predictable
      - Cost is controlled
      Examples:
        ✓ "Recommend a 600-calorie vegetarian lunch"
        ✓ "Find a keto-friendly breakfast with 500 calories"
        ✓ "Suggest a vegan dessert under 300 calories"

NO → Is it OPEN-ENDED?
     (Agent decides what to do)

YES → AgentService
      Characteristics:
      - Path depends on intermediate results
      - User gives open-ended constraint
      - Agent decides what tools to call
      - More conversational
      Examples:
        ✓ "I have eggs, onions, potatoes. What can I make?"
        ✓ "Help me use up these ingredients"
        ✓ "Can you suggest something with chicken and rice?"

NO → Something is wrong. Re-examine request.
```

---

## NomNom Integration Strategy

### Intent Classifier (New Component)

Before deciding which service to use, classify the user's intent:

```python
class IntentClassifier:
    def classify(self, user_input: str) -> str:
        # "Recommend a 600-calorie lunch" → "structured_recommendation"
        # "What can I make with these ingredients?" → "open_cooking_advice"
        # "Show my meal history" → "query"
        pass
```

### NomNom Router (Update to ai_service.py)

```python
class NomNomAIService:
    def handle_request(self, user_input: str, user_id: int):
        # Step 1: Classify intent
        intent = self.intent_classifier.classify(user_input)
        
        # Step 2: Route to appropriate service
        if intent == "structured_recommendation":
            # Extract parameters from user_input
            # Call WorkflowService
            return self.workflow_service.recommend_meal(...)
        
        elif intent == "open_cooking_advice":
            # Extract ingredients/constraints
            # Call AgentService
            return self.agent_service.cook_with_ingredients(...)
        
        else:
            # Handle other intents (query, history, etc.)
            pass
```

---

## Interview Talking Point

"For NomNom, I implemented two LLM orchestration patterns based on the task:

**WorkflowService** for structured requests like 'Recommend a 600-calorie lunch':
- Follows a fixed 5-step pipeline: Extract → Search → Generate → Validate → Rank
- Predictable cost (~$0.01 per recommendation)
- Fast (5-10 seconds)
- Used when the user's intent is clear and the steps are known

**AgentService** for open-ended requests like 'What can I make with these ingredients?':
- Agent autonomously decides what tools to call (search recipes, check nutrition, check pantry)
- Adapts to what it learns (if recipes look expensive, it checks nutrition)
- More conversational and user-friendly
- Variable cost (~$0.02-0.05) depending on how many tools it uses

The key decision: I added an **IntentClassifier** that routes each user request to the right service. This way, NomNom gets the benefits of both patterns without the user noticing."

---

## What This Teaches

✅ How to decide between workflow vs. agent (structure vs. flexibility)  
✅ How to implement both patterns for production  
✅ How to route between them based on user intent  
✅ How to measure and compare performance  
✅ How to integrate into existing systems

---

**Status:** 📊 Day 9 Services Built & Ready for Testing
