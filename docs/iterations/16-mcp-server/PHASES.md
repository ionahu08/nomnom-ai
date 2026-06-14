# Iteration 16: Phases — MCP Server & Claude Code Integration

---

## Overview

Iteration 16 exposes NomNom's core functionality (meal recommendations, food image analysis, nutrition lookup) as an MCP (Model Context Protocol) server, making NomNom a native service in the Claude ecosystem instead of just an external API.

---

## Phase 1: MCP Protocol Research & Design (Day 1)

**Goal:** Understand MCP and design tool interfaces

### 1.1 MCP Fundamentals

**What is MCP?**
- Protocol for exposing tools/resources to Claude and other LLM applications
- Runs as a subprocess communicating via stdio
- Tools are function signatures that Claude can call

**MCP Components:**
- **Tools:** Functions Claude can invoke (like `/tool-name(args)`)
- **Resources:** Browsable data sources (like `/database/users`)
- **Prompts:** Template-based requests (like `/templates/summarize`)

### 1.2 Tool Design

**Decision:** Expose 3 core NomNom functions as tools

| Tool | Purpose | Input | Output | Claude Model |
|------|---------|-------|--------|--------------|
| `recommend_meal` | Get personalized meal suggestion | calories, diet_type | {meal_name, nutrition, reasoning} | Vision + LLM |
| `analyze_food_image` | Analyze food photos | image_path | {food_name, calories, macros} | Vision |
| `lookup_nutrition` | Search knowledge base | query | {results: [food, calories, protein, ...]} | RAG search |

### 1.3 Architecture Decision

**Server Type:** Use FastMCP (newer implementation)  
**Reasoning:** Simpler API than original MCP spec, better documentation, active maintenance

**Data Flow:**
```
Claude Code
    ↓ (tool call)
MCP Server (stdio)
    ↓ (function call)
NomNom Backend (HTTP)
    ↓ (data)
Claude Code (result)
```

---

## Phase 2: MCP Server Implementation (Days 2-3)

**Goal:** Build the MCP server with all 3 tools

### 2.1 Project Structure

```
learning_lab/phase_6/
├── nomnom_mcp_server.py        # Main MCP server (285 lines)
├── test_mcp_server.py          # Local testing
├── 04_claude_code_integration.md # Usage guide
└── README.md                     # Setup instructions
```

### 2.2 Core Server Implementation

**File:** `learning_lab/phase_6/nomnom_mcp_server.py`

```python
from mcp.server.fastmcp import FastMCP

app = FastMCP("nomnom")

@app.tool()
def recommend_meal(calories: int, diet_type: str) -> dict:
    """Get a personalized meal recommendation."""
    # Call backend workflow service
    response = requests.post(
        "http://localhost:8000/api/v1/recommendations/meal",
        json={"calories": calories, "diet_type": diet_type}
    )
    return response.json()

@app.tool()
def analyze_food_image(image_path: str) -> dict:
    """Analyze a food photo and extract nutrition."""
    # Call backend food analysis endpoint
    with open(image_path, 'rb') as f:
        response = requests.post(
            "http://localhost:8000/api/v1/food/analyze",
            files={"image": f}
        )
    return response.json()

@app.tool()
def lookup_nutrition(query: str) -> dict:
    """Search the nutrition knowledge base."""
    # Call backend RAG search
    response = requests.get(
        "http://localhost:8000/api/v1/nutrition/search",
        params={"q": query}
    )
    return {
        "results": response.json()["results"],
        "citations": response.json().get("citations", [])
    }
```

### 2.3 Tool Specifications

**Tool 1: recommend_meal**
```
Name: recommend_meal
Parameters:
  - calories (int): target daily calories
  - diet_type (str): dietary preference ("vegetarian", "vegan", "omnivore", etc.)
Returns:
  {
    "meal_name": "Spanish Tortilla",
    "calories": 350,
    "protein_g": 12,
    "carbs_g": 25,
    "fat_g": 18,
    "reasoning": "High in protein, fits your calorie target..."
  }
```

**Tool 2: analyze_food_image**
```
Name: analyze_food_image
Parameters:
  - image_path (str): local path to food photo
Returns:
  {
    "food_name": "Grilled Chicken with Rice",
    "estimated_calories": 450,
    "protein_g": 35,
    "carbs_g": 40,
    "fat_g": 12,
    "confidence": 0.92
  }
```

**Tool 3: lookup_nutrition**
```
Name: lookup_nutrition
Parameters:
  - query (str): search term
Returns:
  {
    "results": [
      {
        "food": "Chicken Breast",
        "calories": 165,
        "protein_g": 31,
        "carbs_g": 0,
        "fat_g": 3.6,
        "source": "USDA FoodData Central"
      },
      ...
    ],
    "citations": ["[1] USDA FoodData Central", "[2] ..."]
  }
```

### 2.4 Error Handling

```python
try:
    response = requests.post(..., timeout=30)
    return response.json()
except requests.ConnectionError:
    return {"error": "Backend not running", "status": "offline"}
except requests.Timeout:
    return {"error": "Request timeout", "status": "slow"}
except json.JSONDecodeError:
    return {"error": "Invalid response format"}
```

---

## Phase 3: Local Testing (Day 4)

**Goal:** Verify server works before Claude Code registration

### 3.1 Test Server Startup

```bash
# Test 1: Server imports successfully
python learning_lab/phase_6/nomnom_mcp_server.py

# Output should show:
# Server running on stdio transport
# Ready for MCP initialization
```

### 3.2 Test MCP Protocol

**Manual Protocol Test:**
```
Client → Server: {"jsonrpc": "2.0", "id": 1, "method": "initialize", ...}
Server → Client: {"jsonrpc": "2.0", "id": 1, "result": {...tools: [...]}}
```

### 3.3 Test Tool Responses

**Test recommend_meal:**
```python
# Simulate Claude calling the tool
result = recommend_meal(calories=600, diet_type="vegetarian")
assert "meal_name" in result
assert "calories" in result
assert result["calories"] <= 700  # Within margin
```

**Test analyze_food_image:**
```python
# Use a local test image
result = analyze_food_image("/tmp/test_food.jpg")
assert "food_name" in result
assert 0 <= result.get("confidence", 0.9) <= 1.0
```

**Test lookup_nutrition:**
```python
result = lookup_nutrition("high protein vegan")
assert len(result["results"]) > 0
assert all("calories" in r for r in result["results"])
assert len(result.get("citations", [])) > 0
```

### 3.4 Test Checklist

- [x] Server starts without errors
- [x] MCP initialization protocol works
- [x] All 3 tools respond
- [x] JSON responses are valid
- [x] Error handling works (backend offline, timeouts)
- [x] Backend integration verified

---

## Phase 4: Claude Code Registration & Verification (Day 5)

**Goal:** Register MCP server with Claude Code and verify tools work

### 4.1 Registration

```bash
# Add to Claude Code
claude mcp add nomnom python /Users/ionahu/sources/NomNom/learning_lab/phase_6/nomnom_mcp_server.py

# Verify registration
claude mcp list  # Should show "nomnom" in output
```

### 4.2 Tool Verification in Claude Code

**Verification Test 1: Tool Discovery**
```python
# In Claude Code, tools should be discoverable
# You should see nomnom tools in the tools panel

# Expected tools:
# - nomnom:recommend_meal
# - nomnom:analyze_food_image
# - nomnom:lookup_nutrition
```

**Verification Test 2: Basic Tool Call**
```python
# Call recommend_meal
result = recommend_meal(calories=600, diet_type="vegetarian")
print(f"Recommendation: {result['meal_name']}")
```

**Verification Test 3: Image Analysis**
```python
# Upload a food photo and analyze
result = analyze_food_image("/Users/you/lunch.jpg")
print(f"That's {result['food_name']} ({result['estimated_calories']} cal)")
```

**Verification Test 4: Knowledge Base Search**
```python
# Search nutrition database
result = lookup_nutrition("protein sources for athletes")
for item in result["results"]:
    print(f"{item['food']}: {item['protein_g']}g protein")
```

### 4.3 Verification Checklist

- [ ] Claude Code lists nomnom tools
- [ ] `recommend_meal` works and returns valid JSON
- [ ] `analyze_food_image` works with real photos
- [ ] `lookup_nutrition` returns RAG results with citations
- [ ] Error messages are helpful when backend is offline

---

## Architecture: Before vs After

### Before MCP

Claude Code had to make HTTP calls directly:
```python
import requests
response = requests.get("http://localhost:8000/api/v1/recommendations/meal?...")
meal = response.json()
```

Problems:
- Manual URL construction
- Error handling verbose
- No tool discovery
- Authentication complex

### After MCP

Claude Code uses tools natively:
```python
result = recommend_meal(calories=600, diet_type="vegetarian")
meal = result["meal_name"]
```

Benefits:
- Natural function interface
- Automatic tool discovery
- Built-in error handling
- Type hints visible to Claude

---

## Files Created

- ✅ `learning_lab/phase_6/nomnom_mcp_server.py` (285 lines)
- ✅ `learning_lab/phase_6/test_mcp_server.py` (local testing)
- ✅ `learning_lab/phase_6/04_claude_code_integration.md` (usage guide)
- ✅ `docs/iterations/16-mcp-server/PLAN.md`

---

## Success Criteria

- ✅ MCP server imports and starts without errors
- ✅ All 3 tools defined with correct signatures
- ✅ Backend integration working (HTTP calls succeed)
- ✅ JSON responses valid and complete
- ✅ Error handling for offline backend
- ✅ Local testing passes
- ⏳ Claude Code registration (pending `claude mcp add`)
- ⏳ Tool verification in Claude Code (pending registration)

---

## Key Insights

### 1. MCP Makes Claude a Better Client

**Discovery:** Exposing tools via MCP is simpler than HTTP APIs for Claude.  
**Impact:** Claude can call `recommend_meal()` instead of constructing URLs.  
**Principle:** LLM applications work better with tool-first interfaces.

### 2. Backend-as-Service vs Backend-as-Tool

**Backend-as-Service:** External HTTP API, Claude calls it with `requests.get()`  
**Backend-as-Tool:** Native tools, Claude calls it with `function_name(args)`

**Advantage:** Tools are discoverable, type-safe, and feel native to Claude.

### 3. Gradual Exposure

**Design:** Expose only the 3 most useful functions first.  
**Benefit:** Easier to test, maintain, and extend incrementally.  
**Future:** Add more tools (schedule recommendations, shopping lists, etc.) as needed.

---

## Next Steps

1. **Register with Claude Code** (5 min)
   - Run `claude mcp add nomnom ...`
   
2. **Verify in Claude Code** (30 min)
   - Test each tool with real requests
   - Verify citations in RAG results
   - Check error handling

3. **Expand Tools** (Future)
   - Add `schedule_meal_plan` (7-day recommendations)
   - Add `generate_shopping_list` (from meal plan)
   - Add `track_daily_nutrition` (log today's meals)

4. **Add Resources** (Future)
   - Browse available meals in knowledge base
   - Browse user's past recommendations
   - Browse nutritional databases

---

## Status: Server Complete, Claude Code Integration Pending

The MCP server is fully functional and tested locally. Next: register with Claude Code and verify all tools work within Claude's environment.
