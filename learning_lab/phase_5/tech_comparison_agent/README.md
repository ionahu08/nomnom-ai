# Tech Comparison Agent

**A multi-agent side project for interview preparation.**

This is a standalone orchestrator-workers system that compares technologies (e.g., PyTorch vs. TensorFlow) by decomposing the research task into independent worker agents.

---

## Use Case

**Input:** "Compare PyTorch vs. TensorFlow for production machine learning."

**Output:** A comprehensive comparison report covering:
- Performance metrics
- Ecosystem and community
- Deployment and scaling

---

## Architecture

```
User Input
    ↓
Orchestrator (Sonnet)
├─ Decides: What dimensions to research?
├─ Decomposes: 3 research tasks
│   ├─ Task 1: Performance (PyTorch vs. TensorFlow)
│   ├─ Task 2: Ecosystem (community, libraries, maturity)
│   └─ Task 3: Deployment (containers, scaling, ops)
│
└─ Dispatches to Workers (in parallel)
    ├─ Worker 1 (Haiku + web_search): Research performance
    ├─ Worker 2 (Haiku + web_search): Research ecosystem
    └─ Worker 3 (Haiku + web_search): Research deployment
        ↓ (Results come back)
Aggregator (Sonnet)
├─ Synthesizes results
├─ Writes comparison report
└─ Highlights key tradeoffs
    ↓
User Gets: Comprehensive report
```

---

## Key Design Decisions

### 1. Orchestrator Uses tool_choice

The orchestrator uses `tool_choice="required"` to force Claude to output a structured decomposition:

```json
{
  "research_tasks": [
    {"dimension": "Performance", "query": "PyTorch vs TensorFlow benchmarks"},
    {"dimension": "Ecosystem", "query": "PyTorch vs TensorFlow community"},
    {"dimension": "Deployment", "query": "PyTorch vs TensorFlow production scaling"}
  ]
}
```

This ensures the orchestrator doesn't go off-script.

### 2. Workers Get Sub-Prompts Only

Each worker receives ONLY its dimension and query, not the full user input. This keeps workers focused and reduces token overhead.

```
Worker 1 receives:
  "Research: PyTorch vs TensorFlow for performance metrics"
  
NOT:
  "User asked: Compare PyTorch vs. TensorFlow for production..."
```

### 3. Workers Run in Parallel

Use `asyncio.gather()` to run all workers simultaneously, reducing latency from ~45s (serial) to ~15s (parallel).

### 4. Aggregator Synthesizes (Doesn't Research)

The aggregator (Sonnet) reads worker results and writes a report. It does NOT call web search again; it synthesizes what workers found.

---

## Running the Agent

```bash
# Set up
export ANTHROPIC_API_KEY=your_key
pip install anthropic

# Run
python 07_tech_comparison_agent.py
```

---

## What This Teaches

- ✅ Orchestrator-workers pattern (most practical multi-agent form)
- ✅ How to decompose a task
- ✅ Context passing (what each agent sees)
- ✅ Parallel execution with asyncio
- ✅ When multi-agent actually makes sense
- ✅ How to design for debugging (clear worker roles)

---

## Interview Script

**Q: Describe your multi-agent side project.**

A: I built a tech comparison agent using orchestrator-workers. The user asks to compare two technologies (PyTorch vs. TensorFlow). The orchestrator (Sonnet) decomposes the research into 3 independent dimensions: performance, ecosystem, and deployment. Each dimension is researched by a cheap worker (Haiku with web search) in parallel. The orchestrator then synthesizes the results into a comprehensive report.

The key design decision is context isolation: each worker gets only its sub-task, not the full user input. This keeps workers focused and reduces token overhead. The orchestrator uses tool_choice to force structured decomposition, ensuring it doesn't go off-script.

**Q: Why is this better than a single agent researching everything?**

A: It's not always better. This is a case where multi-agent makes sense because:
1. The research naturally decomposes into independent subtasks (no coordination needed)
2. Workers can run in parallel (latency benefit)
3. Orchestrator is smart (decides decomposition), workers are cheap (just research)
4. Cost is justified because we're trading ~$0.15 for a much better report

But I would NOT build this if single agent could do it well, or if the tasks needed to coordinate.

**Q: What are the engineering challenges you had to solve?**

A: Three main ones:
1. **Context passing:** Each worker gets only its sub-prompt. This keeps it focused but means orchestrator has to decide what to share.
2. **Parallelization:** Used asyncio.gather() to run workers in parallel, reducing latency.
3. **Aggregation:** The aggregator doesn't research again; it synthesizes. This prevents redundant API calls.

---

## Files

- `README.md` — This file
- `07_tech_comparison_agent.py` — Main implementation
- `08_multi_agent_eval.md` — (Day 8) Evaluation report comparing orchestrator-workers vs. workflow

---

**Status:** Day 7 Implementation  
**Created:** Phase 5 Day 7
