# Phase 5 Day 5: Workflow vs. Agent Decision Framework

**Purpose:** Given a task, decide which pattern to use.

This is **interview gold** — the ability to make this judgment distinguishes senior LLM engineers.

---

## The Decision Tree

Ask these questions **in order**:

```
Task → Need orchestration?

NO → Single LLM call (no workflow, no agent)
     Example: "Analyze this image"
     Cost: ~$0.001-0.01
     Latency: 1-5s
     Complexity: Low
     ✓ Done

YES → Steps known and fixed upfront?

  NO → Need LLM to decide tool order autonomously?
  
    NO → Something is wrong; re-examine task
    
    YES → Single Agent
          Example: "I have eggs/onions/rice, what to make?"
          Cost: Unpredictable (depends on tools called)
          Latency: 5-30s (multiple rounds)
          Complexity: Medium
          ✓ Done
  
  YES → One of the 5 workflow patterns
        ├─ Chaining: sequential fixed steps
        ├─ Routing: classify input, then path
        ├─ Parallelization: multiple independent tasks
        ├─ Orchestrator-Workers: smart + cheap
        └─ Evaluator-Optimizer: iterate for quality
        
        Cost: Predictable (sum of steps)
        Latency: Predictable (sum or max)
        Complexity: Low-Medium
        ✓ Done
```

---

## Decision Flowchart (Verbose Version)

### Level 0: Do I Need Orchestration?

**Question:** Can a single Claude call solve this?

**Examples:**
- "Analyze this food image" → Single call (NO orchestration)
- "Extract calories from this label" → Single call (NO)
- "Is this food vegetarian?" → Single call (NO)
- "Recommend a meal" → Multiple steps (YES, need orchestration)
- "I have these ingredients, suggest a dish" → Multiple steps (YES)

**If NO:** Just call Claude once. Done. No workflow, no agent.

**If YES:** Continue to Level 1.

---

### Level 1: Are the Steps Known and Fixed?

**Question:** Do you know the exact steps upfront? Will they always be the same?

**Examples of KNOWN steps:**
- "Recommend a meal" → Extract constraints → Search RAG → Generate → Validate → Rank (always these 5)
- "Analyze today's nutrition" → Extract logs → Summarize → Compare to targets (always 3 steps)
- "Grade student essay" → Extract thesis → Check evidence → Evaluate argument → Return grade (always 4 steps)

**Examples of UNKNOWN steps:**
- "I have ingredients, make something" → Path depends on results (unknown order)
- "Help me plan a week of meals" → May need preferences, then search, then nutrition check (depends on what Claude reads)
- "Optimize this code" → May refactor, test, refactor again (path emerges)

**If UNKNOWN:** Continue to Level 2 (Agent decision).

**If KNOWN:** Continue to Level 1b (Which workflow pattern?).

---

### Level 1b: Which Workflow Pattern?

You know steps are fixed. Now decide which of 5 patterns:

**Pattern 1: Prompt Chaining**
- Use when: Sequential steps, each with clear input/output, no parallelization
- Example: Extract → Search → Generate → Validate → Rank
- Cost: Predictable
- Latency: Sum of steps

**Pattern 2: Routing**
- Use when: Input can be classified into categories, each with different logic
- Example: User asks "what did I eat?" vs. "what should I eat?" vs. "am I hitting my goals?"
- Cost: Router + one path (not all paths)
- Latency: Router + one path

**Pattern 3: Parallelization**
- Use when: Multiple independent tasks, need results from all, latency matters
- Example: Summarize today's meals + analyze nutrients + generate commentary (all in parallel)
- Cost: Sum of all tasks
- Latency: Max (not sum)

**Pattern 4: Orchestrator-Workers**
- Use when: Smart orchestrator decides what work, cheap workers execute
- Example: Orchestrator decides "I need performance research + ecosystem research + deployment research" → dispatch to 3 workers
- Cost: Expensive orchestrator + cheap workers
- Latency: Orchestrator + max(workers)

**Pattern 5: Evaluator-Optimizer**
- Use when: Quality-critical, iterate until threshold
- Example: Generate → evaluate → improve if score < 0.8
- Cost: Unpredictable (depends on iterations)
- Latency: Higher (loops)

---

### Level 2: Should I Use an Agent?

**Question:** Does Claude need to autonomously decide the tool order?

**Indicators you need an Agent:**
- Path depends on intermediate results
- User input is open-ended
- "What to do next" changes based on what Claude reads
- Multiple possible valid paths, Claude should pick

**Indicators you DON'T need an Agent:**
- Steps are predetermined
- Path is always the same
- You already decided the order
- Tools are just data fetching (use workflow instead)

**If YES:** Single Agent (hand-written loop from Phase 3)

**If NO:** Something is wrong. You said steps were unknown, but Claude doesn't need autonomy? Re-examine.

---

## NomNom Examples

### Example 1: "Recommend a 600-calorie lunch"

```
Level 0: Do I need orchestration?
  → YES, multiple steps needed

Level 1: Steps known and fixed?
  → YES: Extract → Search → Generate → Validate → Rank

Level 1b: Which pattern?
  → Prompt Chaining (sequential, clear inputs/outputs)
  
Decision: WORKFLOW (Chaining)
Code: learning_lab/phase_5/03_workflow_sandbox.py
```

### Example 2: "I have eggs, onions, potatoes, rice. What can I make?"

```
Level 0: Do I need orchestration?
  → YES, multiple decisions needed

Level 1: Steps known and fixed?
  → NO, path depends on results
  
Level 2: Need LLM autonomy?
  → YES, Claude should decide tool order
  
Decision: SINGLE AGENT
Code: learning_lab/phase_5/04_agent_sandbox.py
```

### Example 3: "Is this food allergenic for my profile?"

```
Level 0: Do I need orchestration?
  → NO, single analysis call
  
Decision: SINGLE LLM CALL (no orchestration)
Code: just call Claude directly
```

### Example 4: "Show me today's meals + nutrition + how I'm trending"

```
Level 0: Do I need orchestration?
  → YES, multiple summaries

Level 1: Steps known and fixed?
  → YES: Always 3 things (meals, nutrition, trend)

Level 1b: Which pattern?
  → Parallelization (all independent, run in parallel)
  
Decision: WORKFLOW (Parallelization)
```

---

## Interview Script

**Q: Walk me through how you'd decide between a workflow and an agent.**

A: I use a decision tree. First, I ask: "Do I know the steps upfront?" 

If yes, it's a workflow. Then I ask which of 5 patterns: chaining (sequential), routing (classify input), parallelization (independent tasks), orchestrator-workers (smart coordinator), or evaluator-optimizer (iterate for quality).

If no, I ask: "Does Claude need autonomy to decide the tool order?" If yes, it's an agent. The agent loop is simple: Claude decides which tool to call, I execute it, Claude sees the result and decides next step.

If the path is known, a workflow is better because costs are predictable and debugging is easier. If the path is unknown, an agent is necessary because Claude needs to respond to what it learns.

**Q: Give me an example where you'd use each pattern.**

A:
- **Chaining:** Meal recommendation (extract constraints → search → generate → validate → rank)
- **Routing:** User intent classifier (different downstream logic per intent)
- **Parallelization:** Daily summary (summarize meals + analyze nutrition + trend check, all in parallel)
- **Orchestrator-Workers:** Research task (orchestrator decides dimensions, workers research independently)
- **Evaluator-Optimizer:** Quality-critical generation (generate → evaluate → improve if needed)
- **Agent:** Fridge leftovers (open-ended, Claude decides whether to search recipes first or check nutrition first)

**Q: When would you NOT use an agent?**

A: Most of the time. Agents add complexity without benefit. Use them only when:
1. Path genuinely depends on intermediate results, AND
2. Claude needs autonomy to decide

If you know the steps upfront, a workflow is better (predictable cost, easier debugging). If there's only one step, just call Claude directly.

---

## Common Traps

### Trap 1: Overcomplicating with Agents

**Wrong:** "I'll build an agent because agents are powerful"

**Right:** Ask: "Do I know the steps?" If yes, use workflow. Agents are for when you don't know.

### Trap 2: Over-Engineering Simple Tasks

**Wrong:** Building a workflow for "analyze this image"

**Right:** Single Claude call. No orchestration needed.

### Trap 3: Fixed Steps, Using an Agent

**Wrong:** "Extract → search → generate → validate → rank" as an agent

**Right:** This is Prompt Chaining (workflow). Costs are predictable. Agent adds unnecessary complexity.

### Trap 4: Unknown Path, Using Workflow

**Wrong:** Trying to design a workflow for "I have ingredients, make something"

**Right:** You can't predict the steps. Use an agent. Claude decides.

### Trap 5: Multi-Agent by Default

**Wrong:** "I'll build a multi-agent system"

**Right:** Single agent (or workflow) solves 95% of problems. Multi-agent is the 5% exception (multiple specialized agents coordinating). Most tasks are better with a single smart agent or a fixed workflow.

---

## Quick Reference Card

| Need | Pattern | Cost | Latency | When |
|------|---------|------|---------|------|
| Single analysis | Single call | Low | 1-5s | "Analyze image" |
| Sequential known steps | Chaining | Predictable | Sum | "Extract → Search → Generate" |
| Classify input | Routing | Low + one path | Fast | "Intent: what did I eat?" |
| Multiple independent | Parallelization | Sum | Max | "Summarize + Analyze + Report" |
| Smart + cheap workers | Orchestrator-Workers | Medium | Fast | "Orchestrate research tasks" |
| Iterate for quality | Evaluator-Optimizer | Variable | High | "Generate → Evaluate → Improve" |
| Unknown path | Agent | Variable | 5-30s | "I have ingredients, suggest dish" |
| Multiple agents | Multi-Agent | Very High | Very High | **Rare (5% of cases)** |

---

## The Meta-Pattern

All these patterns answer the same question: **"How do I get Claude to solve a multi-step problem reliably?"**

The answer is: **"It depends on whether you or Claude decides the steps."**

- **You decide steps** → Workflow (predictable, debuggable)
- **Claude decides steps** → Agent (flexible, autonomous)

That's it. Everything else is details.

---

## Interview Gold

This decision tree is **exactly** what senior LLM engineers are hired for. The ability to:
1. Recognize when orchestration is needed
2. Decide between workflow and agent
3. Pick the right workflow pattern
4. Justify the choice

This judgment separates:
- **Junior:** "I'll just use an agent because it's flexible"
- **Senior:** "This is a workflow because steps are fixed, which pattern? Chaining."

---

## Resources for Next Steps

**If building a workflow:** Use the 5 patterns as templates (Days 1-3 covered this)

**If building an agent:** Use the agent loop from Phase 3 Day 1 + Phase 5 Day 4

**If building multi-agent:** Read Anthropic's research paper, but first ask: "Is single agent not enough?"

---

## Closing Thought

The best system is the simplest one that works.

- Can a single call solve it? → Single call.
- Can a workflow solve it? → Workflow.
- Does it need agent autonomy? → Agent.
- Do you genuinely need multiple agents? → (Rare)

Complexity is a cost. Pay it only when you have to.

---

**Status:** ✅ Day 5 Complete  
**Phase 5 Complete:** All 5 days done (patterns → design → workflow code → agent design → agent code → decision framework)

**Next:** Phase 5 Days 6-10 (Multi-agent side project + production integration) or take a break?
