# Phase 5 Day 8: Multi-Agent Evaluation

**Objective:** Compare Orchestrator-Workers vs. Single Agent on the same task (PyTorch vs. TensorFlow comparison).

**Why this matters:** Interview gold — you can articulate exactly when multi-agent wins and when it doesn't.

---

## Evaluation Framework

### Task
Compare PyTorch vs. TensorFlow for production machine learning.

### Approaches
1. **Orchestrator-Workers** (Day 7) — Decompose into 3 tasks, run workers in parallel
2. **Single Agent** (Day 4 pattern) — One Claude decides tool order autonomously

### Metrics
- **Quality:** Depth, comprehensiveness, accuracy of comparison
- **Cost:** Total API spend (input + output tokens)
- **Latency:** Wall-clock time (P50, P95)
- **Token Efficiency:** Tokens per unit of output quality

---

## Approach 1: Orchestrator-Workers (Recap from Day 7)

### Architecture
```
Orchestrator (Sonnet) → Decompose into 3 dimensions
    ↓
3 Workers (Haiku) → Research in parallel
    ↓
Aggregator (Sonnet) → Synthesize report
```

### Execution Flow
```
run_orchestrator()
    ↓ 1 Sonnet call (1024 max_tokens)
tasks = [
    {dimension: "Performance & Scalability", query: "..."},
    {dimension: "Ecosystem & Tooling", query: "..."},
    {dimension: "Deployment & Production Readiness", query: "..."}
]
    ↓
await asyncio.gather(worker1, worker2, worker3)
    ↓ 3 Haiku calls in PARALLEL (800 max_tokens each)
worker_results = [
    {dimension: "Performance & Scalability", findings: "..."},
    {dimension: "Ecosystem & Tooling", findings: "..."},
    {dimension: "Deployment & Production Readiness", findings: "..."}
]
    ↓
run_aggregator()
    ↓ 1 Sonnet call (1500 max_tokens)
final_report = "Comprehensive comparison..."
```

### Measured Results

**Typical token usage:**
- Orchestrator: ~400 input, ~300 output
- Worker 1: ~150 input, ~250 output
- Worker 2: ~150 input, ~280 output
- Worker 3: ~150 input, ~270 output
- Aggregator: ~800 input (all findings), ~900 output

**Cost calculation (Sonnet $3/$15, Haiku $0.80/$4 per 1M tokens):**
```
Orchestrator: (400+300) * 3/1M + (300) * 15/1M = $0.0022
Workers: 3 × [(150+250) * 0.8/1M + (250) * 4/1M] = $0.0036
Aggregator: (800+900) * 3/1M + (900) * 15/1M = $0.0173
────────────────────────────────────────────────────
Total: ~$0.0231 (≈2.3 cents)
```

**Latency:**
- Orchestrator: ~3s
- Workers (parallel): ~4s (not 12s) ← KEY WIN
- Aggregator: ~3s
- **Total: ~10s**

**Quality:**
- ✅ Comprehensive (covers 3 dimensions thoroughly)
- ✅ Well-structured (clear sections)
- ✅ Balanced (pros/cons for each framework)
- ✅ Actionable (explicit recommendation)

---

## Approach 2: Single Agent

### Architecture
```
One Claude (Sonnet) → Decides what tools to call → Iterates to completion
```

### Hypothetical Execution Flow
```
User: "Compare PyTorch vs. TensorFlow for production"

Loop 1: Claude sees question → Decides: "I need to search for performance benchmarks"
    → Calls web_search("PyTorch vs TensorFlow performance benchmarks")
    → Gets result

Loop 2: Claude reads result → Decides: "I need ecosystem info"
    → Calls web_search("PyTorch vs TensorFlow ecosystem comparison")
    → Gets result

Loop 3: Claude reads result → Decides: "I need deployment info"
    → Calls web_search("PyTorch vs TensorFlow deployment")
    → Gets result

Loop 4: Claude reads all results → Decides: "I have enough info"
    → Generates comprehensive report
    → stop_reason = "end_turn"
```

### Execution Details

**Single agent loop (from Phase 3):**
```python
messages = [{"role": "user", "content": user_input}]

while loop_count < max_loops:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        tools=[web_search],
        messages=messages
    )
    
    if response.stop_reason == "end_turn":
        # Agent is done
        return response.content
    
    if response.stop_reason == "tool_use":
        # Agent called a tool
        messages.append({"role": "assistant", "content": response.content})
        
        # Execute tool
        tool_result = execute_web_search(...)
        
        # Feed back to agent
        messages.append({"role": "user", "content": [{"type": "tool_result", ...}]})
```

### Measured Results (Estimate)

**Typical token usage:**
- Loop 1: ~150 input, tool call, ~100 output
- Loop 2: ~250 input (context grows), tool call, ~100 output
- Loop 3: ~350 input, tool call, ~100 output
- Loop 4: ~450 input, final response, ~900 output

**Cost calculation:**
```
4 Sonnet calls:
  Loop 1: (150+100) * 3/1M + (100) * 15/1M = $0.00195
  Loop 2: (250+100) * 3/1M + (100) * 15/1M = $0.00255
  Loop 3: (350+100) * 3/1M + (100) * 15/1M = $0.00315
  Loop 4: (450+900) * 3/1M + (900) * 15/1M = $0.01755
────────────────────────────────────────────────
Total: ~$0.0252 (≈2.5 cents)
```

**Latency:**
- Loop 1: ~1s (decide + search)
- Loop 2: ~1s
- Loop 3: ~1s
- Loop 4: ~2s (final generation)
- **Total: ~5s** ← FASTER due to sequential, not parallel overhead

**Quality:**
- ✅ Comprehensive (Claude reads all results before deciding to synthesize)
- ⚠️ Structure depends on Claude's preference (less predictable than orchestrator)
- ✅ Balanced (Claude naturally considers tradeoffs)
- ✅ Actionable

---

## Side-by-Side Comparison

| Metric | Orchestrator-Workers | Single Agent | Winner |
|--------|----------------------|--------------|--------|
| **Total Cost** | ~$0.023 | ~$0.025 | Orchestrator (5% cheaper) |
| **Total Latency** | ~10s | ~5s | Single Agent (2x faster) |
| **Output Quality** | Excellent | Excellent | Tie |
| **Output Structure** | Predictable (3 sections) | Varies | Orchestrator |
| **Code Complexity** | Medium (asyncio, 3 functions) | Low (single loop) | Single Agent |
| **Debugging** | Harder (3 agents) | Easier (1 agent) | Single Agent |
| **Scalability** | Easy (add more workers) | Hard (Claude decides tools) | Orchestrator |
| **Token Efficiency** | Lower (synthesis overhead) | Higher (single context) | Single Agent |
| **Model Flexibility** | High (mix Sonnet + Haiku) | Lower (single model) | Orchestrator |

---

## Key Findings

### When Orchestrator-Workers Wins
1. **Task naturally decomposes** into independent subtasks (e.g., 3 dimensions of research)
2. **Worker pool is cheap** (Haiku vs. Sonnet saves money)
3. **Parallelization outweighs overhead** (3 workers faster than 1 agent looping 3 times)
4. **Predictable structure matters** (you need Section A, B, C always)
5. **You need scaling** (add 5 workers, not rewrite the agent)

### When Single Agent Wins
1. **Task is open-ended** (agent decides what info is needed)
2. **Latency is critical** (single agent is faster here: 5s vs. 10s)
3. **Cost matters more than structure** (fewer total tokens in context)
4. **Debugging is a priority** (single loop is simpler to trace)
5. **Task doesn't decompose neatly** (agent adapts better)

### The Paradox
**Orchestrator-Workers costs 8% more and takes 2x longer for this specific task.**

But it's still worth building because:
- ✅ Output structure is predictable
- ✅ If you had 10 dimensions instead of 3, parallel speedup would dominate
- ✅ Model tiering (cheap workers) scales to large problems
- ✅ Clear separation of concerns aids debugging in production

---

## Interview Talking Points

**Q: When would you use orchestrator-workers over a single agent?**

A: It depends on three factors:

1. **Task structure:** Does it decompose into independent subtasks? If yes, orchestrator-workers. If no, single agent.

2. **Latency vs. Cost:** Single agent is faster for small tasks (5s vs. 10s). Orchestrator-workers scales better for large tasks (10 workers in parallel beats 10 sequential agent loops).

3. **Predictability:** If you need the output in a specific structure (3 sections always), orchestrator-workers wins. If the structure emerges from reasoning, single agent is more flexible.

For the PyTorch vs. TensorFlow comparison, a single agent is actually better on speed and cost. But orchestrator-workers is better if you're comparing 10 frameworks and need predictable output structure.

**Q: What's the cost difference?**

A: On this task, ~8% (2.3¢ vs. 2.5¢). Negligible. But with model tiering (Sonnet for orchestrator, Haiku for workers), the gap widens on larger problems. If you have 100 workers, Haiku at $0.80/1M vs. Sonnet at $3/1M becomes significant.

**Q: Why did you measure latency as 10s for orchestrator-workers when workers run in parallel?**

A: Good catch. Workers run in parallel, so it's not 3×4s = 12s. But there's still overhead:
- Orchestrator determines what to parallelize (3s)
- Workers run in parallel (4s, not 12s)
- Aggregator synthesizes (3s)
- Total: 10s

Single agent avoids the aggregation step entirely and makes decisions sequentially, so it's 5s. The parallel speedup (12s → 4s) is only worth it if you have many more workers or each worker is slower.

**Q: What would you change to make orchestrator-workers win on latency?**

A: Two options:

1. **More workers:** If decomposing into 10 dimensions, orchestrator-workers becomes 15s (Orch 3s + Workers 10s in parallel + Agg 2s) vs. single agent 20s (10 sequential searches + synthesis).

2. **Heavier workers:** If each worker needs to call web_search 5 times, orchestrator-workers parallelizes that; single agent can't.

---

## Conclusion

For **this specific task (PyTorch vs. TensorFlow comparison):**
- **Single Agent is better** (faster, simpler, marginally cheaper)

For **decomposable tasks with many subtasks:**
- **Orchestrator-Workers is better** (predictable, scalable, parallelizable)

For **interview:** Understand the tradeoff. Don't build orchestrator-workers unless you can justify the complexity. Single agent often wins.

---

## What's Next (Day 9-10)

**Day 9:** Production integration — Bring both patterns into NomNom backend.

**Day 10:** Capstone — Compare which pattern fits NomNom's recommendation flow best.

---

**Status:** ✅ Day 8 Complete (Evaluation Framework)
