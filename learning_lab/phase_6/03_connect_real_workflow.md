# Phase 6 Day 3: Connect Real Workflow to MCP Tool

**Objective:** Replace hardcoded tool with real `MealRecommendationWorkflow` from production.

**Outcome:** MCP tool calls actual NomNom backend code.

---

## What Changed from Day 2 → Day 3

### Day 2 (Skeleton)
```python
@server.tool()
def recommend_meal(calories: int, diet_type: str) -> dict:
    # Hardcoded responses
    recommendations = { "vegetarian": { 600: "Lentil Buddha Bowl" } }
    return recommendations.get(...)
```

**Purpose:** Verify MCP protocol works.

### Day 3 (Real)
```python
@server.tool()
def recommend_meal(calories: int, diet_type: str) -> dict:
    # Import real workflow
    from src.llm.workflow.meal_recommendation_workflow import MealRecommendationWorkflow
    
    # Call real code
    workflow = MealRecommendationWorkflow()
    result = workflow.execute(calories, diet_type)
    
    # Return structured response
    return {
        "meal_name": result.meal_name,
        "calories": result.calories,
        "nutrition": result.nutrition
    }
```

**Purpose:** Use real NomNom code via MCP.

---

## The Implementation

### Step 1: Import the Real Workflow

At the top of `nomnom_mcp_server.py`:

```python
import sys
from pathlib import Path

# Add NomNom backend to path so we can import src
nomnom_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(nomnom_root / "NomNom-Backend"))

# Now we can import
from src.llm.workflow.meal_recommendation_workflow import MealRecommendationWorkflow
from src.llm.client import LLMClient
from src.config import settings
```

**Why this path manipulation?**

The MCP server runs from `learning_lab/phase_6/`. NomNom backend code is at `NomNom-Backend/src/`. We need to make `src` importable from the server.

```
/Users/ionahu/sources/NomNom/
├── NomNom-Backend/
│   └── src/
│       ├── llm/
│       │   └── workflow/
│       │       └── meal_recommendation_workflow.py ← We want to import this
│       └── config.py
└── learning_lab/
    └── phase_6/
        └── nomnom_mcp_server.py ← Running from here
```

### Step 2: Initialize the Workflow

In the tool function:

```python
@server.tool()
def recommend_meal(calories: int, diet_type: str) -> dict:
    """
    Recommend a meal matching calorie and diet constraints.
    
    Calls the real NomNom meal recommendation workflow.
    """
    try:
        # Initialize LLM client and workflow
        llm_client = LLMClient(api_key=settings.anthropic_api_key)
        workflow = MealRecommendationWorkflow(llm_client)
        
        # Execute the real workflow
        result = workflow.execute(
            calories=calories,
            diet_type=diet_type
        )
        
        # Convert result to JSON-serializable dict
        return {
            "meal_name": result.meal_name,
            "calories": result.calories,
            "protein_g": result.protein_g,
            "carbs_g": result.carbs_g,
            "fat_g": result.fat_g,
            "prep_time_minutes": result.prep_time_minutes,
            "reasoning": result.reasoning
        }
    
    except Exception as e:
        # Return error in structured format
        return {
            "error": str(e),
            "error_type": type(e).__name__
        }
```

**Key details:**
- Initialize `LLMClient` with API key from config
- Call `workflow.execute()` (adapts to actual method name)
- Convert result object to dict (MCP needs JSON-serializable data)
- Wrap in try/except (production servers need error handling)

### Step 3: Handle Configuration

The workflow needs environment variables (API key). Make sure they're available:

**Option A: Load from .env file**

```python
from dotenv import load_dotenv
load_dotenv()  # Loads NomNom-Backend/.env
```

**Option B: Pass API key explicitly**

```python
import os
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set")
llm_client = LLMClient(api_key=api_key)
```

**Recommendation:** Use .env file (same approach as production).

---

## What Could Break (And How to Fix It)

### Issue 1: ImportError on `src.llm.workflow`

**Symptom:** `ModuleNotFoundError: No module named 'src'`

**Cause:** sys.path doesn't include NomNom-Backend.

**Fix:** Verify the path insertion:
```python
import sys
from pathlib import Path

nomnom_root = Path(__file__).parent.parent.parent
backend_path = nomnom_root / "NomNom-Backend"
print(f"Adding to path: {backend_path}")  # Debug print
sys.path.insert(0, str(backend_path))
```

### Issue 2: Missing ANTHROPIC_API_KEY

**Symptom:** `ValueError: ANTHROPIC_API_KEY not set`

**Cause:** Environment variable not available.

**Fix:** 
```bash
export ANTHROPIC_API_KEY="sk-..."
python nomnom_mcp_server.py
```

Or use .env file:
```python
from dotenv import load_dotenv
load_dotenv(nomnom_root / "NomNom-Backend" / ".env")
```

### Issue 3: Workflow Takes Too Long (MCP Timeout)

**Symptom:** Tool call times out (MCP has default timeout).

**Cause:** Real workflow makes LLM API calls (5-15 seconds).

**Fix:** This is expected. MCP timeouts are configurable in the client (Claude Code handles it).

### Issue 4: Result Object Not JSON-Serializable

**Symptom:** `TypeError: Object of type X is not JSON serializable`

**Cause:** Workflow returns a custom class, not a dict.

**Fix:** Explicitly convert to dict in the return statement:
```python
return {
    "meal_name": result.meal_name,
    "calories": result.calories,
    # ... other fields
}
```

Don't return `result` directly.

---

## Testing with Real Workflow

### Update the Test Script

Modify `test_nomnom_server.py` to verify real workflow is being called:

```python
# In the tool call request
tool_call = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "recommend_meal",
        "arguments": {
            "calories": 600,
            "diet_type": "vegetarian"
        }
    }
}

proc.stdin.write(json.dumps(tool_call) + "\n")
proc.stdin.flush()

# Read response
result_line = proc.stdout.readline()
tool_result = json.loads(result_line)

# Check for errors
if "error" in tool_result["result"]["content"][0]["text"]:
    print("✗ Workflow error:", tool_result["result"]["content"][0]["text"])
else:
    print("✓ Real workflow executed successfully")
    result_data = json.loads(tool_result["result"]["content"][0]["text"])
    print("  Meal:", result_data.get("meal_name"))
    print("  Calories:", result_data.get("calories"))
```

### Expected Output (with Real Workflow)

```
[3/4] Calling recommend_meal tool...
✓ Tool call successful
  Meal: Lentil Buddha Bowl (generated by Claude based on constraints)
  Calories: 600
  Prep time: 15 minutes
```

vs. Day 2 (hardcoded):

```
[3/4] Calling recommend_meal tool...
✓ Tool call successful
  Meal: Lentil Buddha Bowl (from hardcoded dict)
  Calories: 600
  Prep time: 15 minutes
```

The meal name will be the same by coincidence, but the reasoning behind it is different.

---

## Implementation Checklist

- [ ] Add sys.path manipulation to import `src` from NomNom-Backend
- [ ] Import `MealRecommendationWorkflow` and `LLMClient`
- [ ] Update `recommend_meal` function to call real workflow
- [ ] Add error handling (try/except)
- [ ] Convert result to JSON-serializable dict
- [ ] Test with `test_nomnom_server.py`
- [ ] Verify real LLM API is being called (check Claude API logs)

---

## Key Differences: Hardcoded → Real

| Aspect | Day 2 (Hardcoded) | Day 3 (Real) |
|--------|-------------------|--------------|
| **Tool logic** | Dictionary lookup | Calls MealRecommendationWorkflow |
| **LLM calls** | None | Yes (Sonnet for generation) |
| **Latency** | <100ms | 5-15 seconds (real API call) |
| **Dependencies** | Only mcp library | mcp + anthropic + NomNom backend code |
| **Error handling** | Simple (key not found) | Rich (API errors, parsing errors, etc.) |
| **Result quality** | Hardcoded examples | Claude-generated, personalized recommendations |

---

## What This Proves

After Day 3, you've demonstrated:

1. **MCP protocol works** (Day 2 hardcoded)
2. **Real code integrates via MCP** (Day 3 real workflow)
3. **Claude can access NomNom backend** through standard protocol
4. **Error handling for production** (try/except, structured errors)
5. **Separation of concerns** (protocol layer ≠ business logic layer)

This is interview-ready: "I built an MCP server that exposes NomNom's workflows to Claude. Started with hardcoded responses to verify the protocol, then swapped in real code. Tool takes calories and diet type, calls the actual workflow, returns structured JSON."

---

## Interview Talking Points

**Q: How do you integrate production code with MCP?**

A: The MCP decorator handles all the protocol work. I just write a normal Python function that imports and calls the real code. In NomNom's case:

1. Day 2: Hardcoded responses (test the protocol works)
2. Day 3: Call real `MealRecommendationWorkflow` (same function signature, different body)
3. Result: Claude can invoke NomNom's backend via MCP without knowing about HTTP, authentication, or the API layer

The MCP server becomes a "translator" between Claude's tool calls and NomNom's internal code.

**Q: What breaks when you move from hardcoded to real?**

A: Import paths (need to add NomNom-Backend to sys.path), environment variables (API key), and latency (real API calls take time). Error handling becomes more complex (API errors, not just missing keys). But the tool interface stays the same.

---

## Next Steps

### Today (Day 3):
1. Update `nomnom_mcp_server.py` with real workflow imports
2. Replace hardcoded recommendations with `workflow.execute()`
3. Add error handling
4. Test with `test_nomnom_server.py`

### Tomorrow (Day 4):
Add more tools: `analyze_food_image`, `search_meal_history`, etc.

---

**Status:** ✅ Day 3 Ready to Implement  
**Implementation:** Update `nomnom_mcp_server.py` (swap out ~20 lines in the tool function)
