# Iteration 16: MCP Server Integration

**Goal:** Expose NomNom backend as Model Context Protocol (MCP) server, integrating with Claude Code.

**Duration:** Phase 6 (1 week)

**What's Built:** NomNom becomes a native service in Claude Code ecosystem.

---

## Goals

- [ ] Create MCP server exposing NomNom tools
- [ ] Integrate with Claude Code via `claude mcp add`
- [ ] Verify all tools work (analyze_food_image, lookup_nutrition, recommend_meal)
- [ ] Document for team

---

## What Already Exists

**Phase 5 Production Work:**
- Workflow + routing patterns implemented
- `src/llm/workflow/meal_recommendation_workflow.py` (5-step chaining)
- `src/llm/client.py` with retry logic
- `src/llm/router.py` with model tiering
- iOS app with full latency optimization (60s → 20-25s)

**Phase 5 Learning:**
- Decision framework (when to use workflow vs. agent)
- Orchestrator-workers vs. single agent comparison
- Multi-agent evaluation

---

## What We're Building (Iteration 16)

### 1. MCP Server
**File:** `learning_lab/phase_6/nomnom_mcp_server.py`

**Three tools exposed:**
1. **`recommend_meal(calories, diet_type)`** — Calls meal recommendation workflow
2. **`analyze_food_image(image_path)`** — Uses Claude vision to analyze food photos
3. **`lookup_nutrition(query)`** — Searches RAG knowledge base, returns cited results

### 2. Claude Code Integration
**Command:** 
```bash
claude mcp add nomnom python /Users/ionahu/sources/NomNom/learning_lab/phase_6/nomnom_mcp_server.py
```

Users can then use NomNom tools directly in Claude Code without HTTP boilerplate.

### 3. Documentation
**Files:**
- `learning_lab/phase_6/04_claude_code_integration.md` — Integration guide
- `docs/iterations/16-mcp-server/PLAN.md` — This file
- `docs/iterations/16-mcp-server/SUMMARY.md` — Retrospective

---

## Success Criteria

- [x] MCP server accepts 3 tools
- [x] Tools are properly typed and documented
- [x] Error handling in place
- [ ] Claude Code integration: `claude mcp add nomnom ...`
- [ ] Verification checklist: All tools tested
  - [ ] Claude Code can list tools
  - [ ] `analyze_food_image` works with local photo
  - [ ] `lookup_nutrition` returns RAG results with citations
  - [ ] `recommend_meal` invokes workflow
  - [ ] Resources can be browsed
- [ ] Iteration documentation complete
- [ ] Team can use NomNom via MCP in Claude Code

---

## Technical Details

### Architecture
```
Claude Code
    ↓ (MCP protocol)
MCP Client
    ↓ (stdio subprocess)
nomnom_mcp_server.py (server.run("stdio"))
    ├─ recommend_meal → MealRecommendationWorkflow
    ├─ analyze_food_image → Claude vision API
    └─ lookup_nutrition → RAG knowledge base
```

### Transport
**stdio:** Server runs as subprocess, Claude Code communicates via JSON-RPC on stdin/stdout.

### Error Handling
All tools return structured error responses on failure (not exceptions).

---

## Resume Skills

- MCP protocol and server implementation
- Integrating backend code with Claude ecosystem
- Tool design (input schema, return types, error handling)
- Claude Code / Claude API integration patterns

---

## Next Steps

1. Add `analyze_food_image` and `lookup_nutrition` tools ✅
2. Register server: `claude mcp add nomnom ...`
3. Test each tool in Claude Code notebook
4. Complete verification checklist
5. Document results
6. Create iteration summary

---

## References

- MCP Spec: https://modelcontextprotocol.io/
- Claude Code: https://claude.com/claude-code
- NomNom Phase 5: Workflow & Agent Orchestration
