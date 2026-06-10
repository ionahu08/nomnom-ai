# Phase 5 Day 1: The 5 Workflow Patterns

**Reference:** Anthropic — Building Effective Agents (2nd read)

---

## Context

You've already read this article in Phase 0 for the framework view (workflow vs. agent). This time, focus on the **5 specific patterns** Anthropic recommends for orchestrating LLM calls into reliable systems.

All 5 patterns are **workflows** (fixed control flow). An agent is different: the path is determined by LLM at runtime.

---

## The 5 Patterns

### 1. Prompt Chaining

**Core Idea:** Break a complex task into sequential steps, each with its own LLM call.

**When to use:**
- Task naturally decomposes into steps
- Each step has clear input/output
- Order matters and is known upfront

**Example:**
```
Step 1: Extract user constraints (Haiku)
  ↓
Step 2: Search knowledge base (no LLM)
  ↓
Step 3: Generate options (Sonnet)
  ↓
Step 4: Validate (Opus)
  ↓
Step 5: Rank & explain (Sonnet)
```

**Key properties:**
- Cost: Predictable (sum of step costs)
- Latency: Predictable (sum of step latencies)
- Debugging: Easy (inspect each step)
- Tokens: Efficient (each step uses only what it needs)

**Interview angle:** "Chaining is the default. Most multi-step problems are just chaining with different models per step."

---

### 2. Routing

**Core Idea:** Classify input into categories, then follow a category-specific path.

**When to use:**
- Input naturally falls into categories
- Each category needs different logic
- Routing decision is clear

**Example:**
```
User intent: "What did I eat today?"
  → Retrieve logs + summarize
  
User intent: "Should I eat this food?"
  → Analyze food + compare to goals
  
User intent: "What should I eat?"
  → Recommendation workflow (chaining)
```

**Key properties:**
- Router: lightweight (Haiku)
- Downstream: each path is custom
- Cost: one router + one path (not all paths)
- Flexibility: easy to add new intents

**Interview angle:** "Routing separates concerns. Router decides what; downstream workflow decides how."

---

### 3. Parallelization

**Core Idea:** Run multiple independent subtasks in parallel, aggregate results.

**When to use:**
- Subtasks are independent
- You need results from all of them
- Latency matters more than cost

**Example:**
```
Input → Task A ─┐
      → Task B ─┼→ Aggregate → Output
      → Task C ─┘
```

**Key properties:**
- Latency: max(A, B, C) not sum
- Cost: sum of all costs (all run)
- Requires async/await or threading
- Failure in one task breaks whole pipeline

**Interview angle:** "Parallelization trades cost for latency. Good when response time is critical."

---

### 4. Orchestrator-Workers

**Core Idea:** Smart orchestrator decides what work, dispatches to specialized workers.

**When to use:**
- Work naturally decomposes into subtasks
- Orchestrator makes decisions, workers execute
- Workers run in parallel
- Cost efficiency matters (expensive orchestrator, cheap workers)

**Example:**
```
Orchestrator (Sonnet): "I need to research 3 dimensions"
    ├─ Dispatch → Worker 1 (Haiku + web search) ──┐
    ├─ Dispatch → Worker 2 (Haiku + web search) ──┼→ Orchestrator synthesizes
    └─ Dispatch → Worker 3 (Haiku + web search) ──┘
```

**Key properties:**
- Orchestrator: expensive (makes decisions)
- Workers: cheap (execute tasks)
- Context: workers typically get only sub-prompt
- Aggregation: orchestrator synthesizes final result

**Interview angle:** "Orchestrator-Workers scales better than single agent. More control than full agent, cheaper than all-expensive-models."

---

### 5. Evaluator-Optimizer

**Core Idea:** Producer generates, evaluator scores, optimizer improves if needed. Loop.

**When to use:**
- Quality is critical
- You can define "good enough" threshold
- Re-generation cost is justified
- Simple evaluation metric exists

**Example:**
```
Producer (Sonnet) → Recommendation
    ↓
Evaluator (Opus) → Score
    ↓
Score < 0.7?
  YES → Optimizer (Sonnet) → improved recommendation → back to Evaluator
  NO → Return recommendation
```

**Key properties:**
- Producer: usually Sonnet
- Evaluator: usually Opus (critical judgment)
- Optimizer: usually Sonnet (guided improvement)
- Cost: unpredictable (depends on iterations)
- Latency: higher due to loops

**Interview angle:** "Evaluator-Optimizer is for quality-critical apps. You're paying for correctness, not speed."

---

## Decision Framework

```
Need to orchestrate multiple LLM calls?

Is the task naturally decomposable into 
fixed steps in a known order?
  → YES: Prompt Chaining

Do different input categories need 
different downstream logic?
  → YES: Routing

Are there multiple independent subtasks 
that could run in parallel?
  → YES: 
    Can a smart orchestrator decide 
    what work is needed?
      → YES: Orchestrator-Workers
      → NO: Parallelization

Do you need to iterate on quality 
until a threshold?
  → YES: Evaluator-Optimizer (wraps others)

Does the path depend on intermediate results 
and Claude needs autonomy?
  → YES: Use AGENT (not a workflow pattern)
  → NO: re-examine your task decomposition
```

---

## Key Insight: Workflows vs. Agents

All 5 patterns = **workflows**: fixed control flow, predictable.

**Agent** = different: Claude decides what to do at each step, path emerges at runtime.

**When to choose:**
- Workflow: "I know the steps upfront"
- Agent: "I don't know the steps; Claude should decide"

**Example:**
- "Recommend a meal" → Workflow (routing + chaining)
- "I have ingredients; make something" → Agent (Claude decides order of tool calls)

---

## Q&A: Understanding the 5 Patterns

**Q: Why does each pattern need different models (Haiku, Sonnet, Opus)?**

A: Cost-benefit tradeoff. Haiku is cheap for simple tasks (routing, web search). Sonnet is balanced for reasoning + generation. Opus is expensive but best for critical judgment (validation, evaluation). Match the model to the task's requirements.

**Q: Why is Prompt Chaining the default?**

A: It's the simplest. You know the steps upfront, order is fixed, each step is straightforward. Routing is just chaining with a classification step first. Parallelization is chaining with multiple paths in parallel.

**Q: When would I NOT use Prompt Chaining?**

A: When you don't know the steps upfront (use Agent). When steps need to run in parallel (Parallelization). When you need an expensive orchestrator to decide work (Orchestrator-Workers).

**Q: What's the cost difference between Chaining and Orchestrator-Workers?**

A: Chaining: predictable (sum of steps). Orchestrator-Workers: orchestrator cost + sum of worker costs (workers are usually cheap). Orchestrator-Workers is more expensive upfront but scales better.

**Q: Why would I use Parallelization instead of just doing things sequentially?**

A: Latency. If Task A takes 5s and Task B takes 5s, doing them sequentially takes 10s. In parallel, it's 5s. The tradeoff: cost is higher (both run), but response time is better.

**Q: How do you decide: Evaluator-Optimizer or just better prompting?**

A: If the task is quality-critical and the improvement cost < value of being right, use Evaluator-Optimizer. If you can fix it by tweaking the prompt, do that first. Evaluator-Optimizer is for when prompt tweaking isn't enough.

---

## Interview Gold

**Q: Describe when you'd use a workflow vs. an agent.**

A: Workflows are the default. Use them when you know the steps upfront (chaining + routing). Agents are the exception — only when the path genuinely depends on intermediate results and Claude needs autonomy. Most problems solve with workflows. Multi-agent is the 5% exception to multi-agent.

**Q: Walk through the 5 patterns and give an example for each.**

A: [Refer to examples above]

**Q: How do you choose between Orchestrator-Workers and Parallelization?**

A: If all tasks are independent and identical (calculate metrics, transform data), Parallelization. If you need a smart orchestrator to decide what work to dispatch to specialized workers, Orchestrator-Workers.

---

## Resources

- **Anthropic — Building Effective Agents**: https://www.anthropic.com/research/building-effective-agents
- **Anthropic Cookbook**: https://github.com/anthropics/anthropic-cookbook (examples of each pattern)

---

## Next

Day 2: Design a specific workflow for NomNom (meal recommendation using Chaining + Routing)
