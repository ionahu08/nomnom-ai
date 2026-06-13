# Phase 6 Day 1: MCP Concepts & Protocol Overview

**Reference:** Anthropic's MCP Specification (https://modelcontextprotocol.io/)

**Context:** You've mastered workflows and agents (Layer 5-6). MCP is the next level: making NomNom's patterns available to Claude itself, and to other LLM systems.

---

## Quick Self-Check: Q&A

**Q1: What are the three types of MCP exports?**

A: Tools (callable actions), Resources (read-only data), Prompts (reusable templates with variables).
- Tools: Claude decides when to call based on user request
- Resources: Static or semi-static data Claude can reference
- Prompts: System prompts with variable injection (e.g., user context)

**Q2: How should you expose NomNom's meal recommendation workflow to Claude via MCP?**

A: As a **Tool**. Here's why:
- It's callable (takes input: calories, diet_type; returns output: recommendation)
- Claude decides **when** to call it based on what the user asks
- Tools are for actions; Resources would be static data; Prompts would be system instructions

**Q3: When would you use REST API vs MCP for NomNom?**

A: **Both, for different clients:**
- **REST API** (for iOS app, web browsers): Traditional HTTP calls. You control the client code.
  ```
  iPhone → HTTP GET /api/v1/recommendations/meal → Backend → Response
  ```
- **MCP** (for Claude, notebooks, other LLMs): Standard protocol for LLM integration. Claude's client knows how to invoke tools.
  ```
  Claude → Calls MCP tool "recommend_meal" → Backend → Response
  ```

Why both? REST API for traditional clients. MCP for LLM integration.

**Q4: What transport should you use for local dev vs. production?**

A: 
- **Local development:** Use **stdio** (simplest, no network needed, server runs as subprocess)
- **Production remote:** Use **HTTP/WebSocket** (persistent connection, scalable, authentication-ready)

Trade-off: stdio is simpler for dev, HTTP is better for remote production servers.

---

## Why MCP Matters

**Current state of NomNom:**
- Backend API: FastAPI (REST endpoints)
- iOS client: Makes HTTP calls to backend
- Claude integration: Limited to what we hard-code in prompts

**What if Claude could invoke NomNom directly?**
- Claude in a notebook could call: "Get meal recommendations"
- Claude in an agentic context could: "Route user request → workflow → return result"
- Other LLM systems could: Use NomNom's patterns via standard protocol

**That's what MCP enables:** A standard protocol for LLMs to access external tools, resources, and services.

---

## What is MCP?

**Model Context Protocol** is a standard for connecting Claude (or any LLM) to external systems.

Think of it as:
- **API contract:** How tools/resources are defined
- **Bidirectional:** Client (Claude) ↔ Server (NomNom backend)
- **Composable:** Stack multiple servers (NomNom + GitHub + Slack + custom services)
- **Standards-based:** Not proprietary to Anthropic (or any one vendor)

**Key insight:** Unlike REST API (client calls server), MCP is **Claude calls server via a standard protocol**.

---

## Core Concepts

### 1. MCP Server vs. Client

```
Claude Desktop App / Claude Code / Claude API
    ↓ (connects to)
MCP Client
    ↓ (manages)
MCP Server (NomNom Backend)
    ├─ Resources (read-only data)
    ├─ Tools (callable actions)
    └─ Prompts (reusable prompt templates)
```

**Server:** Your application (NomNom backend)  
**Client:** Claude's MCP client (built-in or custom)

### 2. Three Types of Server Exports

#### A. **Tools** (Claude can call them)

```
Tool: recommend_meal
  Input: {calories: int, diet_type: str}
  Output: {recommendation: str, nutrition: {...}}
```

Claude decides when to call the tool based on user request.

**Example in NomNom:**
- `recommend_meal` → Calls our workflow
- `analyze_food_image` → Calls ANALYZE_FOOD task
- `get_meal_history` → Calls RAG search

#### B. **Resources** (Claude can read them)

```
Resource: meal_database
  Type: text/plain
  Content: [All meals in our KB]
```

Resources are static or semi-static data that Claude can reference. Not called—just read.

**Example in NomNom:**
- Nutrition knowledge base (read-only)
- User's meal history (snapshot)
- Dietary guidelines

#### C. **Prompts** (Claude can use as templates)

```
Prompt: nutrition_advisor
  Description: "Act as a nutrition expert"
  Arguments: {user_profile, recent_meals}
  Template: "You are a nutrition expert. User profile: {{user_profile}}. Recent meals: {{recent_meals}}"
```

Prompts let you bake in system instructions + context.

**Example in NomNom:**
- `nutrition_advisor` prompt (with user profile injected)
- `meal_critic` prompt (roasting cat personality)
- `dietary_validator` prompt (check constraints)

---

## How MCP Works: The Protocol

### Step 1: Client → Server Initialization

Claude connects to NomNom MCP server. Handshake:
- Server describes: What tools, resources, prompts it exposes
- Client confirms: Ready to use them

### Step 2: Tool Use

```
Claude thinks: "User asked for meal recommendations"
Claude → Server: call_tool("recommend_meal", {calories: 600, diet: "vegetarian"})
Server → Claude: {recommendation: "Lentil Buddha Bowl", ...}
Claude → User: "I recommend the Lentil Buddha Bowl because..."
```

### Step 3: Resource Access

```
Claude thinks: "I need context on the user's dietary restrictions"
Claude → Server: read_resource("user_dietary_guidelines")
Server → Claude: [content of resource]
Claude: [continues reasoning with this context]
```

### Step 4: Prompt Template

```
Claude → Server: use_prompt("nutrition_advisor", {user_profile: {...}, recent_meals: [...]})
Server → Claude: [Rendered prompt with variables filled in]
Claude: [Uses as system prompt for reasoning]
```

---

## Transport: How Does the Connection Work?

MCP doesn't specify transport. It can run over:

### Option 1: **stdio** (Simplest)
- MCP server runs as a subprocess
- Claude talks to it via stdin/stdout
- Perfect for local development

### Option 2: **HTTP/WebSocket**
- Server runs on a remote machine
- Claude connects via HTTP or WebSocket
- Good for production (persistent connection)

### Option 3: **Custom** (Rare)
- You implement the transport yourself

**For NomNom:** Start with stdio (local development), move to HTTP (production).

---

## NomNom's MCP Server Plan

### What We'll Expose

**Tools:**
1. `recommend_meal` — Calls our 5-step workflow
2. `analyze_food_image` — Calls ANALYZE_FOOD task (image → nutrition)
3. `check_user_profile` — Fetches dietary restrictions, preferences
4. `search_meal_history` — Query user's past meals (RAG)

**Resources:**
1. `nutrition_kb` — Knowledge base (read-only snapshot of top meals)
2. `user_dietary_guidelines` — User's restrictions, allergies, goals

**Prompts:**
1. `nutrition_advisor` — System prompt with user context injected
2. `meal_critic` — NomNom's roasting cat personality

### Benefits

- **Claude in Claude Code** can call: `@mcp recommend_meal(calories=600, diet="vegetarian")`
- **Claude in notebooks** can use NomNom as a tool without HTTP calls
- **Other systems** can implement MCP client and use NomNom
- **Composable:** NomNom + GitHub MCP + Slack MCP = multi-system agent

---

## Architecture: MCP Server Implementation

### Minimal MCP Server (Pseudocode)

```python
from mcp.server import Server

server = Server("NomNom")

# Register a tool
@server.tool()
def recommend_meal(calories: int, diet_type: str) -> dict:
    """Recommend a meal matching constraints"""
    # Call our workflow
    workflow = MealRecommendationWorkflow(...)
    return workflow.recommend(calories, diet_type)

# Register a resource
@server.resource()
def nutrition_kb() -> str:
    """Nutrition knowledge base"""
    return load_kb_snapshot()

# Register a prompt
@server.prompt()
def nutrition_advisor(user_profile: dict) -> str:
    """Nutrition expert prompt with user context"""
    return f"You are a nutrition expert for {user_profile['name']}..."

# Start server
server.run(transport="stdio")  # or transport="http"
```

### Real Implementation Will Need

1. **Authentication** — How does Claude authenticate with NomNom?
2. **Rate limiting** — Protect against abuse
3. **Error handling** — What if tool fails?
4. **Logging** — Track what Claude is calling
5. **Versioning** — Evolution of tools/resources

---

## Key Differences: MCP vs. REST API

| Aspect | REST API | MCP |
|--------|----------|-----|
| **Who initiates?** | Client calls server | Server describes, client calls |
| **Discovery** | Documentation or OpenAPI | Server sends capabilities |
| **Type safety** | HTTP status codes | Structured responses + errors |
| **Streaming** | Long polling or WebSockets | Built-in streaming |
| **Composition** | Manual (multiple API calls) | Automatic (one client, many servers) |
| **Transport** | HTTP/HTTPS | stdio, HTTP, WebSocket, custom |

**For NomNom:** Keep REST API for iOS/web clients. Add MCP for Claude access.

---

## Interview Talking Points

**Q: Why would you use MCP instead of just exposing a REST API?**

A: REST API is great for web clients and mobile apps. MCP is better for LLM integration because:

1. **Discovery:** Claude can query what tools/resources are available (no manual documentation reading)
2. **Composability:** One Claude instance can talk to multiple MCP servers (NomNom + GitHub + Slack)
3. **Streaming:** Built-in support for streaming responses (important for long-running operations)
4. **Semantics:** Tools/Resources/Prompts are first-class concepts — Claude understands the difference, not just "HTTP endpoint"

For NomNom: We use BOTH. REST API for iOS app, MCP for Claude access. They share the same backend code.

**Q: What's in an MCP server?**

A: Three types of exports:

1. **Tools** — Callable actions. Claude decides when to invoke them. Example: `recommend_meal`
2. **Resources** — Read-only data Claude can reference. Example: Nutrition knowledge base
3. **Prompts** — Reusable system prompts with variable injection. Example: "Nutrition advisor" prompt with user context

**Q: How does Claude know what tools are available?**

A: MCP server sends a capabilities list during initialization. Claude's client reads it and knows what it can call. It's automatic discovery.

---

## What We'll Build (Days 1-10)

| Day | Focus | Outcome |
|-----|-------|---------|
| **1** (Today) | MCP concepts + protocol | Understand fundamentals |
| **2** | MCP server implementation | Build skeleton NomNom MCP server |
| **3** | Tools (recommend_meal, analyze_food) | Expose core functions as tools |
| **4** | Resources (nutrition_kb, user_guidelines) | Expose static/semi-static data |
| **5** | Prompts (nutrition_advisor, meal_critic) | Expose system prompts with context |
| **6** | Local testing (stdio transport) | Test server locally with Claude Code |
| **7** | HTTP transport + authentication | Production-ready remote connection |
| **8** | Integration with Claude Code | Use @mcp decorator in notebooks |
| **9** | Multi-server composition | Stack NomNom + other MCPs |
| **10** | Production deployment | Ship MCP server alongside API |

---

## Next Steps

**Day 1 (Today) - Done:** Understand MCP concepts, protocol, architecture

**Day 2 (Tomorrow):** Build skeleton MCP server
- Set up python-mcp library
- Implement minimal tool (hardcoded for testing)
- Test stdio transport locally
- Document server definition

---

## Resources

- **Spec:** https://modelcontextprotocol.io/
- **Python SDK:** https://github.com/anthropics/python-mcp-sdk
- **Anthropic Docs:** https://docs.anthropic.com/en/docs/build-with-claude/mcp (when available)
- **Examples:** Anthropic provides example servers (GitHub, filesystem, etc.)

---

**Status:** ✅ Day 1 Complete (Concepts)  
**Next:** Day 2 — MCP Server Skeleton Implementation
