# Phase 5 Day 6: Multi-Agent Concepts — When NOT to Use Them

**References:**
- Anthropic — How we built our multi-agent research system
- Cognition — Don't Build Multi-Agents (opposing view)

---

## Context: Why This Matters

You now know workflows and single agents. **Multi-agent is the next level.**

The critical insight: **Multi-agent adds significant complexity, and 95% of tasks don't need it.**

This day is about learning:
1. What multi-agent systems are
2. Why they're powerful (in rare cases)
3. Why they're dangerous (complexity, cost, eval difficulty)
4. When to use them (5% of cases)
5. How to argue against them (interview skill)

---

## Three Forms of Multi-Agent Systems

### Form 1: Orchestrator-Workers (Most Practical)

**Structure:**
```
Orchestrator (smart, expensive)
    ├─ Decides what work is needed
    ├─ Dispatches Task 1 → Worker A (cheap)
    ├─ Dispatches Task 2 → Worker B (cheap)
    └─ Dispatches Task 3 → Worker C (cheap)
        ↓
Aggregator (orchestrator or specialized)
    ├─ Collects results from workers
    └─ Synthesizes final output
```

**Example:**
- Task: Compare PyTorch vs. TensorFlow for production
- Orchestrator (Sonnet): "I need to research: performance, ecosystem, deployment"
- Worker A (Haiku + web search): Research performance metrics
- Worker B (Haiku + web search): Research ecosystem (community, libraries)
- Worker C (Haiku + web search): Research deployment (containers, scaling)
- Orchestrator: Synthesizes into comparison report

**When to use:**
- Work naturally decomposes into specialized subtasks
- Subtasks can run in parallel
- Cost efficiency matters (cheap workers, expensive orchestrator)

**Trade-offs:**
- ✅ Scales well (add more workers for more tasks)
- ✅ Cost-effective (workers are cheap)
- ❌ More complex than single agent
- ❌ Harder to debug (multiple agents)
- ❌ Context passing overhead

---

### Form 2: Conversational Multi-Agent

**Structure:**
```
Agent A (Claude instance)
    ↓ Message exchange
Agent B (Claude instance)
    ↓
Agent C (Claude instance)
```

**Example:**
- Agent A (Researcher): "What are the key differences?"
- Agent B (Critic): "That's incomplete. Consider X and Y."
- Agent A (Researcher): "Good point. Here's the revised analysis."
- Agent C (Synthesizer): "Here's the final report combining both views."

**When to use:**
- Task requires back-and-forth reasoning
- Different perspectives improve output
- Debate-style decision-making is valuable

**Trade-offs:**
- ✅ Can improve quality through debate
- ❌ Very expensive (multiple Claude calls)
- ❌ Hard to control (agents might talk past each other)
- ❌ Unpredictable latency (loops depend on agreement)

---

### Form 3: Hierarchical Multi-Agent

**Structure:**
```
Top-level orchestrator
    ├─ Mid-level orchestrator
    │   ├─ Worker A
    │   └─ Worker B
    └─ Mid-level orchestrator
        ├─ Worker C
        └─ Worker D
```

**When to use:**
- Extremely complex task with nested decomposition
- (Rare. 99% of problems don't need this.)

**Trade-offs:**
- ❌ Very complex
- ❌ Very expensive
- ❌ Very hard to debug
- ✅ Can handle extreme complexity (if you really have it)

**Honest take:** If you're considering hierarchical multi-agent, you probably don't need it. Rethink the problem.

---

## Five Engineering Challenges

### Challenge 1: Context Passing

**Problem:** How much context does each agent see?

**Options:**

Option A: Full context
- Each agent sees everything
- ✅ Agents are well-informed
- ❌ Huge token overhead
- ❌ Agents get distracted by irrelevant info

Option B: Sub-context (recommended)
- Each agent sees only its sub-task context
- ✅ Lower token cost
- ✅ Agents stay focused
- ❌ Workers might miss important details
- ❌ Need orchestrator to decide what to share

Option C: Minimal context
- Each agent sees only its immediate task
- ✅ Lowest token cost
- ❌ Risk of workers making wrong assumptions

**Lesson:** Context passing is a cost/quality tradeoff. There's no free lunch.

---

### Challenge 2: Coordination

**Problem:** How do agents coordinate when they need to?

**Scenarios:**

Scenario A: Independent workers (easy)
- Workers don't need to communicate
- Orchestrator just gathers results
- ✅ Simple, parallelizable

Scenario B: Dependent workers (hard)
- Worker A's result affects what Worker B should do
- Need synchronization, communication, retries
- ❌ Complex, hard to get right

**Lesson:** If workers need to coordinate, complexity explodes. Consider single agent instead.

---

### Challenge 3: Error Propagation

**Problem:** What happens when one agent fails?

**Options:**

Option A: Fail fast
- One worker fails → whole system fails
- ✅ Simple semantics
- ❌ Brittle (one failure breaks everything)

Option B: Retry the worker
- Worker fails → retry with new context
- ✅ More robust
- ❌ More cost, more latency

Option C: Degrade gracefully
- Worker fails → use best-effort result or skip
- ✅ Robust
- ❌ Complex (what's "good enough" output?)

**Lesson:** Error handling in multi-agent is hard. Single agent is simpler.

---

### Challenge 4: Cost Explosion

**Problem:** Multi-agent systems cost way more than single agent.

**Example:**
- Single agent: 3 tool calls, 1 Sonnet call = $0.02
- Orchestrator-workers: 1 orchestrator (Opus) + 3 workers (each calls Haiku + web search) = $0.15 (7.5× more expensive)

**Mitigation:**
- Use cheap models for workers (Haiku)
- Use expensive model only for orchestrator (Sonnet/Opus)
- Minimize API calls per worker
- Parallelize workers to save latency (but not cost)

**Lesson:** If cost isn't justified by quality improvement, don't use multi-agent.

---

### Challenge 5: Evaluation is Extremely Hard

**Problem:** How do you know if your multi-agent system works?

**Single agent eval:**
- Input: one test case
- Output: one result
- Grade: one score
- Simple!

**Multi-agent eval:**
- Input: one test case
- Output: multiple intermediate results + final result
- Grade: do the intermediate results make sense? Does the final result use them correctly?
- Very hard!

**Additional problem:** Multi-agent systems have more variance (randomness in agent decisions).

**Lesson:** If you can't easily evaluate it, don't build it.

---

## The Anthropic Stance

**Anthropic's findings (from their research system):**

1. **Orchestrator-workers is most practical**
   - Works well for decomposable tasks
   - Cost can be justified in some cases
   - Easier to debug than other forms

2. **Context passing is the #1 challenge**
   - Get it wrong, and workers make bad decisions
   - Get it right, and token cost explodes
   - No perfect solution

3. **Single agent often wins on latency**
   - Orchestrator-workers wait for all workers to finish (max latency)
   - Single agent streams responses (lower latency)

4. **When NOT to use multi-agent**
   - When steps are predetermined (use workflow)
   - When single agent can do it (add more tools)
   - When evaluation is unclear
   - When cost matters and improvement is marginal

---

## The Cognition Opposing View

**Cognition's argument (simplified):**

> "We built multi-agent systems, and they were more complex, more expensive, and not better than single agent. Most companies don't need them. Use single agent. If single agent isn't enough, the problem is the problem statement, not the architecture."

**Their key points:**
1. Single agent with good tools beats multi-agent with bad coordination
2. Multi-agent introduces failure modes (agents contradicting each other, context confusion)
3. Evaluation is too hard to justify multi-agent
4. Orchestrator-workers sounds good in theory; in practice, context passing ruins it

**Their recommendation:** Build single agent first. Only go multi-agent if you've genuinely exhausted single agent options.

---

## Decision Tree: Single Agent vs. Multi-Agent

```
Can single agent solve it?
  → YES: Use single agent. Done.
  
  → NO: Does the task decompose into independent subtasks?
    → NO: You don't need multi-agent. Re-examine your task.
    
    → YES: Do the subtasks need to communicate/coordinate?
      → YES: Coordination is hard. Reconsider single agent with more tools.
      
      → NO: Can you evaluate the quality easily?
        → NO: Too risky. Start with single agent.
        
        → YES: Is the cost justified by the quality improvement?
          → NO: Use single agent.
          
          → YES: Multi-agent (orchestrator-workers) might be worth it.
```

---

## When Multi-Agent Actually Wins

Multi-agent is worth considering when **all** of these are true:

1. ✅ Task doesn't decompose into predetermined steps (not a workflow)
2. ✅ Single agent can't handle it (you've tried and failed)
3. ✅ Subtasks are independent (no complex coordination)
4. ✅ You can evaluate quality clearly
5. ✅ Cost improvement justifies the complexity
6. ✅ Your team has 2+ people (one person + multi-agent = nightmare)

**Real-world frequency:** ~5% of LLM tasks.

---

## Interview Talking Points

**Q: When would you use a multi-agent system?**

A: Rarely. I'd first try a single agent with more tools. If that doesn't work, I'd consider orchestrator-workers — where a smart orchestrator decomposes the task and dispatches to cheap workers. But I'd be very careful about context passing and coordination. The Cognition team's finding is important: most companies over-engineer with multi-agent when single agent would work.

**Q: What's the biggest challenge in multi-agent systems?**

A: Context passing. If you share too much context, token cost explodes. If you share too little, workers make mistakes. Getting it right is hard. This is why Anthropic recommends starting simple (workflow or single agent) and only going multi-agent if truly necessary.

**Q: How do you know when to stop adding tools to a single agent and switch to multi-agent?**

A: When the single agent is making correlated mistakes. Example: the agent is calling tools in the wrong order, or using tool results incorrectly. If adding more tools or tweaking the system prompt doesn't help, then multi-agent might be worth exploring. But first, verify that it's a capability problem, not a context/coordination problem.

**Q: What's the difference between your "orchestrator-workers" and what Cognition is warning about?**

A: Orchestrator-workers is one form of multi-agent, and it's the most practical one. But even orchestrator-workers can fail if context passing is wrong or if workers need to coordinate. Cognition's warning is: don't assume multi-agent solves everything. It adds complexity, and the burden of proof is on you to show it's necessary.

---

## Key Takeaway

**The golden rule:** 

> Use the simplest architecture that works.
> 
> Single agent beats multi-agent 95% of the time.
> 
> If you're building multi-agent, you'd better have a really good reason.

---

**Status:** ✅ Day 6 Complete (Concepts & Research)  
**Next:** Day 7 — Hands-on Implementation (tech_comparison_agent side project)
