# Phase 5 Day 4: Single Agent — When Workflow Isn't Enough

**Scenario:** "I have eggs, onions, potatoes, and rice in my fridge. What can I make?"

**Why Workflow Fails:** Fixed steps don't work. The path depends on what Claude discovers at each step.

**Solution:** Single Agent — Claude decides tool call order dynamically.

---

## Workflow vs. Agent: Side by Side

### Workflow (Deterministic)
```
User Input
    ↓
Step 1: Extract constraints (Haiku)
    ↓
Step 2: Search RAG (predetermined)
    ↓
Step 3: Generate menus (Sonnet)
    ↓
Step 4: Validate (Opus)
    ↓
Step 5: Rank (Sonnet)
    ↓
User Output

Control flow: You decide the order
Claude's role: Execute each step
Path: Always the same
Cost: Predictable
```

### Agent (Autonomous)
```
User Input + Tools
    ↓
Claude Loop:
  while stop_reason != "end_turn":
    1. Claude decides: which tool to call next?
    2. You execute the tool
    3. Claude reads the result
    4. Claude decides: more tools needed, or done?
    ↓
User Output

Control flow: Claude decides the order
Claude's role: Decide what to do next
Path: Emerges at runtime
Cost: Unpredictable
```

---

## The "Fridge Leftovers" Problem

**User:** "I have eggs, onions, potatoes, and rice. What can I make tonight?"

**Why Workflow Fails:**
- Unknown ingredients → can't predict next step
- Multiple possible paths:
  - Path A: List combos → judge nutrition → consider cook time
  - Path B: Check recipes first → see what matches → then nutrition
  - Path C: Ask for dietary preferences first → then search recipes
- Claude needs to decide, not you

**Why Agent Works:**
- Claude sees the tools available
- Claude decides: "I should search recipes first"
- Claude reads results
- Claude decides: "Now I need to check nutrition"
- Claude reads results
- Claude decides: "I have enough info, here's my recommendation"

---

## The Agent Loop (Hand-Written)

**From Phase 3 Day 1, adapted for this use case:**

```python
messages = [
    {
        "role": "user",
        "content": user_input
    }
]

while True:
    # Step 1: Call Claude with tools available
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=[
            # Tool definitions here
        ],
        messages=messages
    )

    # Step 2: Check stop reason
    if response.stop_reason == "end_turn":
        # Claude is done, return the answer
        break
    
    if response.stop_reason == "tool_use":
        # Claude wants to call a tool
        for block in response.content:
            if block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input
                
                # Step 3: Execute the tool
                result = run_tool(tool_name, tool_input)
                
                # Step 4: Add Claude's response to messages
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                
                # Step 5: Add tool result to messages
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        }
                    ]
                })
                # Loop continues, Claude sees the result and decides next step
```

---

## The "Fridge Leftovers" Agent Design

**User Story:** "I have eggs, onions, potatoes, and rice. What can I make?"

**Tools Available:**
1. `search_recipes(ingredients: list[str]) → list[Recipe]`
   - Input: ["eggs", "onions", "potatoes", "rice"]
   - Output: Recipes matching ingredients

2. `check_nutrition(dish_name: str) → NutritionInfo`
   - Input: "Fried Rice with Eggs"
   - Output: Calories, protein, carbs, fat

3. `estimate_cooking_time(dish_name: str) → int`
   - Input: "Fried Rice with Eggs"
   - Output: 20 (minutes)

4. `check_pantry(user_id: int) → dict`
   - Input: user_id
   - Output: {"eggs": 2, "onions": 1, "potatoes": 3, "rice": 1}

**Claude's Expected Behavior:**
1. Claude reads user input: "I have eggs, onions, potatoes, and rice. What can I make?"
2. Claude calls: `search_recipes(["eggs", "onions", "potatoes", "rice"])`
3. Claude reads: [Fried Rice with Eggs, Potato Omelette, Vegetable Stir-Fry]
4. Claude calls: `check_nutrition("Fried Rice with Eggs")`
5. Claude calls: `estimate_cooking_time("Fried Rice with Eggs")`
6. Claude reads results
7. Claude decides: "I have enough info"
8. Claude returns: "You should make Fried Rice with Eggs because..."

**Key Difference from Workflow:**
- You don't decide "search first, then check nutrition"
- Claude decides it
- Path emerges based on what Claude reads

---

## When to Use Agent vs. Workflow

| Scenario | Pattern | Why |
|----------|---------|-----|
| "Recommend a 600-cal lunch" | Workflow | Steps known: extract → search → generate → validate → rank |
| "I have eggs/onions/rice, what to make?" | Agent | Path unknown: search → nutrition → time → synthesis |
| "Analyze this image" | Workflow | Single step: call Claude with image |
| "Write an essay with sources" | Agent | Path unknown: search → read → synthesize → iterate |
| "Is this food healthy?" | Workflow | Single step: analyze + return boolean |
| "Help me plan a week of meals" | Agent | Path unknown: get preferences → search → check nutrition → iterate |

**Decision Rule:**
- **Workflow:** "I know the steps upfront"
- **Agent:** "I don't know the steps; Claude should decide based on tool results"

---

## Key Insight: Agent Loop is Simple

The agent loop is just:
```
while Claude hasn't said "end_turn":
    Claude decides which tool to call
    You execute the tool
    You show Claude the result
    Loop
```

No special framework needed. Just message passing and a loop.

---

## Common Agent Mistakes

**Mistake 1: Too many tools**
- Agent with 20 tools = confusing (Claude doesn't know which to use)
- Agent with 3-5 tools = clear

**Mistake 2: Tools that return too much data**
- Tool returns 1000 results
- Claude gets lost trying to process them
- Better: Tool returns top 10, let Claude ask for more if needed

**Mistake 3: No stop condition**
- Infinite loop because Claude keeps calling tools
- Fix: Define "done" clearly. Claude should stop when it has enough info.

**Mistake 4: Tools that are too smart**
- Tool does: search + filter + rank + summarize
- Claude loses control
- Better: Tool does: search only. Let Claude decide what to do with results.

---

## Interview Talking Points

**Q: When would you use an agent instead of a workflow?**

A: When you don't know the steps upfront. If the path depends on intermediate results and Claude needs to decide what to do next, use an agent. Example: "I have these ingredients, what can I make?" Claude needs to search, read results, then decide if it needs nutrition info. The path isn't predetermined.

**Q: How do you prevent infinite loops in an agent?**

A: Define "done" clearly. The agent should stop when it has enough information. Give tools that return focused data (top 10, not 1000). Let Claude reason about when it has enough.

**Q: What's the difference between an agent and a multi-agent system?**

A: Single agent = Claude (one intelligent actor) decides tool order. Multi-agent = multiple Claude instances or workers coordinating. Single agent is usually enough. Multi-agent adds complexity and cost without corresponding benefit 95% of the time.

---

## Next Steps

Day 5 will formalize this into a decision framework:
- Decision tree to choose between workflow and agent
- When each pattern wins
- Interview-ready explanation

---

**Key Takeaway:** 

Agents aren't magic. They're just loops:
```
while not done:
    Claude decides what to do
    You do it
    Show Claude the result
```

The power comes from Claude's ability to read tool results and decide next steps dynamically.

---

**Status:** ✅ Day 4 Design Complete  
**Next:** Day 4 Implementation (agent loop sandbox code)
