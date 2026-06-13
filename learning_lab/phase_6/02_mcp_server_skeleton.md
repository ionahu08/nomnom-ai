# Phase 6 Day 2: MCP Server Skeleton Implementation

**Objective:** Build a working MCP server with one hardcoded tool. Test locally with stdio transport.

**Outcome:** Runnable server that Claude can connect to and invoke.

---

## Setup: Python MCP SDK

### Step 1: Install Dependencies

```bash
pip install mcp anthropic
```

What you're installing:
- **mcp**: Anthropic's MCP server library (handles protocol, transport, tool registration)
- **anthropic**: Claude API client (for testing from within the server)

### Step 2: Understand the SDK Structure

```python
from mcp.server import Server
from mcp.types import Tool, Resource, Prompt

# Server is the main class
# Tool, Resource, Prompt are data types
```

**Key insight:** The SDK handles the MCP protocol. You just:
1. Create a Server instance
2. Register tools/resources/prompts via decorators
3. Call `server.run()` with a transport

---

## Building a Skeleton Server

### Minimal MCP Server (< 50 lines)

```python
"""
Skeleton MCP Server for NomNom
Exposes one hardcoded tool for testing
"""

import json
from mcp.server import Server
from mcp.types import Tool

# Create server instance
server = Server("NomNom")

# Register one tool
@server.tool()
def recommend_meal(calories: int, diet_type: str) -> dict:
    """
    Recommend a meal matching calorie and diet constraints.
    
    Args:
        calories: Target calorie count
        diet_type: vegetarian, vegan, keto, etc.
    
    Returns:
        Meal recommendation with nutrition info
    """
    # Hardcoded for testing (replace with real workflow later)
    recommendations = {
        "vegetarian": {
            600: "Lentil Buddha Bowl",
            400: "Vegetable Stir-Fry",
            800: "Pasta Primavera"
        }
    }
    
    meal = recommendations.get(diet_type, {}).get(calories, "No match found")
    
    return {
        "meal_name": meal,
        "calories": calories,
        "diet_type": diet_type,
        "protein_g": 20,
        "prep_time_minutes": 15
    }


# Run the server
if __name__ == "__main__":
    # stdio transport: server reads from stdin, writes to stdout
    # Claude's client sends tool calls via stdin
    # Server sends responses via stdout
    server.run(transport="stdio")
```

---

## Understanding the Decorator Pattern

### What `@server.tool()` Does

```python
@server.tool()
def recommend_meal(calories: int, diet_type: str) -> dict:
    ...
```

The decorator:
1. **Registers** the function with the server
2. **Extracts** the signature (parameters, return type, docstring)
3. **Creates** a Tool definition (name, description, input schema)
4. **Exposes** it to Claude's MCP client

Claude sees:
```json
{
  "name": "recommend_meal",
  "description": "Recommend a meal matching calorie and diet constraints.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "calories": {"type": "integer"},
      "diet_type": {"type": "string"}
    },
    "required": ["calories", "diet_type"]
  }
}
```

All automatic from your function signature + docstring.

---

## Testing Locally with stdio

### Step 1: Create the Server File

Save the skeleton above as `learning_lab/phase_6/nomnom_mcp_server.py`

### Step 2: Start the Server

```bash
cd /Users/ionahu/sources/NomNom
python learning_lab/phase_6/nomnom_mcp_server.py
```

The server starts, waiting for input on stdin. It prints nothing (MCP is binary/JSON protocol).

### Step 3: Test with Claude Code

In Claude Code, create a test script:

```python
import json
import subprocess

# Start the MCP server as subprocess
proc = subprocess.Popen(
    ["python", "learning_lab/phase_6/nomnom_mcp_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Send MCP initialize request (JSON)
init_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "test-client",
            "version": "1.0"
        }
    }
}

proc.stdin.write(json.dumps(init_request) + "\n")
proc.stdin.flush()

# Read response
response = proc.stdout.readline()
print("Server response:", response)

# Send tool call request
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

# Read tool response
result = proc.stdout.readline()
print("Tool result:", result)

proc.terminate()
```

**What happens:**
1. Server starts (stdio transport waits for JSON on stdin)
2. Test client sends MCP initialize message
3. Server responds with capabilities (available tools)
4. Test client calls `recommend_meal` tool
5. Server returns result

---

## MCP Protocol Flow (What's Happening Under the Hood)

### The Dialog

**Client → Server (Initialize):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": { ... }
}
```

**Server → Client (Capabilities):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": [
        {
          "name": "recommend_meal",
          "description": "Recommend a meal...",
          "inputSchema": { ... }
        }
      ]
    },
    "serverInfo": { "name": "NomNom", "version": "1.0" }
  }
}
```

**Client → Server (Tool Call):**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "recommend_meal",
    "arguments": { "calories": 600, "diet_type": "vegetarian" }
  }
}
```

**Server → Client (Tool Result):**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"meal_name\": \"Lentil Buddha Bowl\", ...}"
      }
    ]
  }
}
```

**Key insight:** Everything is JSON-RPC over stdin/stdout. The SDK handles serialization; you just write Python.

---

## Iteration: From Skeleton to Real

### Today (Day 2): Hardcoded Tool

```python
@server.tool()
def recommend_meal(calories: int, diet_type: str) -> dict:
    # Hardcoded responses
    recommendations = { ... }
    return recommendations.get(diet_type, {}).get(calories, "No match")
```

**Purpose:** Verify server architecture works, MCP protocol is correct, tool invocation succeeds.

### Tomorrow (Day 3): Connect to Real Workflow

```python
@server.tool()
def recommend_meal(calories: int, diet_type: str) -> dict:
    # Call real workflow
    from src.llm.workflow.meal_recommendation_workflow import MealRecommendationWorkflow
    workflow = MealRecommendationWorkflow()
    result = workflow.execute(calories, diet_type)
    return result
```

**Progress:** Same tool signature, real implementation. Server API unchanged.

### Day 4-5: Add More Tools & Resources

```python
@server.tool()
def analyze_food_image(image_path: str) -> dict:
    ...

@server.resource()
def nutrition_kb() -> str:
    ...

@server.prompt()
def nutrition_advisor(user_profile: dict) -> str:
    ...
```

---

## Debugging Tips

### Issue: Server starts but doesn't respond

**Symptom:** You run the server, it hangs silently.

**Cause:** stdio transport is reading stdin. The server is waiting for a client to connect.

**Fix:** Don't run the server directly. Either:
1. Use the test script above (sends MCP messages)
2. Use Claude Code with MCP integration (handled automatically)
3. Use a proper MCP client library

### Issue: Tool call returns error

**Symptom:** `method error: Unknown tool`

**Cause:** Tool name doesn't match what server registered.

**Fix:** Check function name matches what you're calling in tool/call request.

### Issue: Server crashes on tool execution

**Symptom:** Server process exits unexpectedly.

**Cause:** Exception in your tool function.

**Fix:** Add try/except in your tool, return error response.

```python
@server.tool()
def recommend_meal(calories: int, diet_type: str) -> dict:
    try:
        # ... your code
        return result
    except Exception as e:
        return {"error": str(e)}
```

---

## What You'll Build Today

**Filename:** `learning_lab/phase_6/nomnom_mcp_server.py`

**Structure:**
```python
# 1. Imports (mcp.server, mcp.types)
# 2. Server instance creation
# 3. One @server.tool() function (hardcoded)
# 4. Main: server.run(transport="stdio")
```

**Lines of code:** ~40

**What it does:**
- Exposes `recommend_meal` tool
- Takes calories + diet_type as input
- Returns hardcoded meal recommendation
- Runs on stdio transport (ready for Claude to call)

---

## Next Steps

### Step 1: Write the Server (Today)

Create `nomnom_mcp_server.py` with the skeleton above.

### Step 2: Test It (Today)

Use the test script to send MCP messages and verify tool calls work.

### Step 3: Document (Today)

Write a README explaining:
- How to start the server
- What tools it exposes
- How to test it

### Step 4: Prepare for Day 3 (Tomorrow)

Think about how to call real NomNom code from the tool.

---

## Server Anatomy Cheat Sheet

| Part | Purpose | Example |
|------|---------|---------|
| **Server instance** | Main class managing tools/resources | `server = Server("NomNom")` |
| **@server.tool()** | Register callable action | `@server.tool()` decorator |
| **@server.resource()** | Register read-only data | `@server.resource()` decorator |
| **@server.prompt()** | Register reusable prompt | `@server.prompt()` decorator |
| **transport** | How server communicates | stdio, http, websocket |
| **run()** | Start listening | `server.run(transport="stdio")` |
| **Function signature** | Defines tool schema | `def recommend_meal(calories: int, diet_type: str) -> dict` |
| **Docstring** | Becomes tool description | `"""Recommend a meal..."""` |

---

## Interview Talking Points

**Q: How does the MCP server SDK make it easy to expose tools?**

A: The decorator pattern. You write a normal Python function, add `@server.tool()`, and the SDK automatically:
1. Extracts the function signature (parameter names, types)
2. Parses the docstring (becomes tool description)
3. Generates JSON schema for inputs
4. Registers it with the server

Claude sees the tool as a structured object (name, description, input schema). You just wrote Python.

**Q: What's the difference between hardcoding the tool (Day 2) vs. calling real code (Day 3)?**

A: Hardcoding verifies the server architecture and MCP protocol work. Calling real code swaps the implementation, not the interface. Same tool signature, different body. This separation (skeleton → real) is how you debug protocol issues before mixing in application logic.

---

**Status:** ✅ Day 2 Ready to Build  
**Next:** Implement `nomnom_mcp_server.py` and test with MCP messages
