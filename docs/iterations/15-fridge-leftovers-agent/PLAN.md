# Iteration 15: Fridge Leftovers Agent

**Status:** Planning (Phase 5 Day 10)  
**Goal:** Implement a new "Fridge Assistant" agent feature for open-ended cooking advice.

---

## What We're Building

A **new feature** that lets users ask "What can I cook with these ingredients?" and get smart, personalized suggestions from an autonomous agent.

### User Experience

```
User: "I have eggs, onions, potatoes, and some butter. What can I make?"

Agent Loop:
  1. Checks user's pantry for what else is available
  2. Searches recipe knowledge base for matching meals
  3. Checks nutrition info for top recipes
  4. Estimates cooking time
  5. Generates personalized recommendation

Response: "You can make a Spanish Tortilla! It takes 20 minutes,
         has 350 calories, and uses your eggs and potatoes perfectly.
         Here's the recipe..."
```

### Why an Agent?
- User input is **open-ended** ("What can I make?" not "Recommend 600 calories")
- Agent **decides autonomously** what to search for (recipes, then nutrition, then timing)
- Agent **adapts** based on what it finds
- **No predetermined step order** (flexibility is the goal)

---

## Architecture

### New Module: `NomNom-Backend/src/llm/agent/`

```
src/llm/agent/
  ├─ __init__.py
  ├─ fridge_assistant.py       # Main agent loop
  └─ tools/
      ├─ __init__.py
      ├─ check_pantry.py       # List user's pantry contents
      ├─ search_recipes.py      # Search recipe knowledge base
      ├─ calculate_nutrition.py # Get nutrition for recipe
      └─ estimate_cooking_time.py # Estimate prep + cook time
```

### New API Endpoint: `src/api/fridge.py`

```python
@router.post("/api/v1/fridge/suggestion")
async def get_fridge_suggestion(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request: FridgeSuggestionRequest
):
    """
    Get a cooking suggestion based on available ingredients.

    Request:
        {
            "ingredients": ["eggs", "onions", "potatoes"],
            "constraints": {
                "time_minutes": 30,
                "dietary_restrictions": ["vegetarian"]
            }
        }

    Response:
        {
            "recommendation": "You can make a Spanish Tortilla...",
            "recipe": {...},
            "nutrition": {...},
            "cooking_time": 20
        }
    """
```

---

## Implementation Details

### Tools Implementation

Each tool is a real query against NomNom's systems:

**check_pantry.py:**
- Query: user's saved pantry list (or derive from recent meals)
- Returns: list of available ingredients with quantities

**search_recipes.py:**
- Query: recipe knowledge base by ingredients
- Uses: embedding similarity search (pgvector)
- Returns: top 5 matching recipes with names, ingredients, ratings

**calculate_nutrition.py:**
- Query: nutrition knowledge base by recipe name
- Uses: existing knowledge service
- Returns: calories, macros, micronutrients

**estimate_cooking_time.py:**
- Query: recipe database
- Returns: prep time + cooking time total

### Agent Loop

```python
class FridgeAssistant:
    async def suggest_meal(self, user_id, ingredients, constraints):
        client = anthropic.Anthropic()
        
        messages = [{"role": "user", "content": ...}]
        tools = [check_pantry, search_recipes, calculate_nutrition, estimate_cooking_time]
        
        while loop_count < max_loops:
            response = await client.messages.create(
                model="claude-haiku-4-5-20251001",
                tools=tools,
                messages=messages
            )
            
            if response.stop_reason == "end_turn":
                return extract_recommendation(response)
            
            if response.stop_reason == "tool_use":
                # Execute tool, feed back to agent
                # Agent sees result and decides next step
```

---

## Success Criteria

- [ ] `fridge_assistant.py` implements agent loop
- [ ] All 4 tools implemented against real DB/RAG
- [ ] New API endpoint at `/api/v1/fridge/suggestion`
- [ ] Agent produces valid FridgeSuggestionResponse
- [ ] Agent completes in <10 loops (no infinite loops)
- [ ] Cost per call is <$0.05
- [ ] Latency is <30 seconds
- [ ] iOS integration planned (out of scope for Phase 5)

---

## Testing Strategy

### Unit Tests
- Each tool tested independently
- Mock database returns for check_pantry
- Mock recipe search results
- Verify tool responses have correct schema

### Integration Tests
- Full agent loop with mock tools
- Verify agent terminates (doesn't loop infinitely)
- Verify final response is well-formed
- Test with various ingredient combinations

### Manual Testing
- Test with real user pantry
- Verify agent calls tools in reasonable order
- Verify recommendations are relevant
- Check latency + cost on real calls

---

## Effort Estimate

| Component | Effort | Notes |
|-----------|--------|-------|
| fridge_assistant.py (agent loop) | 3 hours | Modify from agent_service.py learning code |
| Tools implementation (4 tools) | 6 hours | Integrate with DB/RAG queries |
| API endpoint + schemas | 2 hours | Create /fridge/suggestion endpoint |
| Testing | 3 hours | Unit + integration + manual testing |
| **Total** | **14 hours** | ~1.5 work days |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Agent loops infinitely | High | Set max_loops=10, monitor loop count |
| Tool responses too slow | Medium | Cache frequent queries, optimize RAG search |
| Cost explodes (too many tool calls) | Medium | Use Haiku model, measure tokens per call |
| Tools don't integrate with real DB | Medium | Start with mocks, integrate with real DB incrementally |
| Agent doesn't terminate properly | Medium | Test with various inputs, add timeout |

---

## Timeline

- **Day 10 AM:** Implement fridge_assistant.py + all 4 tools
- **Day 10 Afternoon:** API endpoint + integration testing
- **Day 10 Evening:** Manual testing, cost/latency optimization
- **After Day 10:** iOS team can integrate endpoint (out of Phase 5 scope)

---

## Post-Implementation

### For iOS Team
- New endpoint: `POST /api/v1/fridge/suggestion`
- Can be integrated into Settings → Fridge Assistant tab
- No changes to backend auth/db needed

### Monitoring
- Track agent loop count (should average 2-4 loops)
- Monitor token usage per call
- Track latency percentiles (P50, P95)

---

## What This Teaches

✅ How to build agent loops in production FastAPI  
✅ How to integrate multiple real tools (DB, RAG, etc.)  
✅ How to handle agent autonomy responsibly (max loops, timeouts)  
✅ How to create new API features quickly  
✅ Interview-ready: "I built a conversational agent that helps users cook with leftover ingredients..."

---

## Related Files

- **Day 4 Learning:** `learning_lab/phase_5/04_agent_sandbox.py`
- **Existing Services:** `src/services/knowledge_service.py`, `src/services/profile_service.py`
- **Existing Tools:** `src/llm/tools.py`
- **API patterns:** `src/api/recommendations.py`

---

**Status:** ✏️ Planning (Ready to start Day 10)
