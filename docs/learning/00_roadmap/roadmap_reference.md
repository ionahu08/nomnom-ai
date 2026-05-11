# Complete LLM Harnessing Learning Roadmap (12 Weeks)

> A systematic roadmap from zero to portfolio-ready
> Target audience: People with ML/MLE background aiming to build working agent systems and prepare for related interviews

---

## Table of Contents

- [Prologue: What Is LLM Harnessing](#prologue-what-is-llm-harnessing)
- [Stage 1: Building the Foundation (Week 1–2)](#stage-1-building-the-foundation-week-12)
- [Stage 2: Tool Use (Week 3–4)](#stage-2-tool-use-week-34)
- [Stage 3: Patterns + Multi-Agent + Eval (Week 5–7)](#stage-3-patterns--multi-agent--eval-week-57)
- [Stage 4: Studying Claude Code as a Reference Implementation (Week 8)](#stage-4-studying-claude-code-as-a-reference-implementation-week-8)
- [Stage 5: Multimodal + MCP (Week 9–10)](#stage-5-multimodal--mcp-week-910)
- [Stage 6: Capstone Projects (Week 11–12+)](#stage-6-capstone-projects-week-1112)
- [Appendix A: Skip List](#appendix-a-skip-list)
- [Appendix B: Reading List Summary](#appendix-b-reading-list-summary)

---

## Prologue: What Is LLM Harnessing

> This section is the map, not the details. Read it in half a day to one day. Every later stage will refer back to this map.

### Definition

**LLM Harnessing** = The **capability stack** for treating an LLM as an unreliable but powerful component, and using engineering techniques to "harness" it into a reliable system.

Breaking down the keywords:
- **Unreliable**: Same input produces different outputs, hallucinates, drifts, refuses.
- **Powerful**: Generalization, language understanding, code, reasoning.
- **Harness**: Constrain inputs/outputs, monitor, correct errors, compose.
- **Capability stack**: Not a single skill — a layered set of engineering capabilities.

### A Memorable Analogy

"Harness" originally means horse tack. **An LLM is a wild horse**: It can run, it can carry, but it isn't controllable. Harnessing means putting on the bridle (prompt engineering), saddle (output structure), horseshoes (error handling), shoes (caching), and training (eval) — turning a wild horse into a working draft animal.

### Capability Stack

```
┌─────────────────────────────────────┐
│  Layer 6: Multi-Agent Coordination  │  ← Multi-agent collaboration
├─────────────────────────────────────┤
│  Layer 5: Agent Engineering         │  ← Autonomous decisions, loops, memory
├─────────────────────────────────────┤
│  Layer 4: Reliability Engineering   │  ← Eval, monitoring, regression testing
├─────────────────────────────────────┤
│  Layer 3: Augmentation              │  ← Tool use, RAG, multimodal
├─────────────────────────────────────┤
│  Layer 2: Output Control            │  ← Structured output, stop seq, tool_choice
├─────────────────────────────────────┤
│  Layer 1: Prompt Engineering        │  ← Single-call input design
├─────────────────────────────────────┤
│  Layer 0: API Mastery               │  ← messages, parameters, streaming
└─────────────────────────────────────┘
```

**Key insights**:
- Higher layers depend on lower ones. If Layer 1 isn't solid, Layer 5 will crash.
- Each layer has its own engineering techniques, failure modes, and eval methods.
- "I work on LLMs" is vague. "I'm building a Layer 4 regression testing system" is engineering language.

### How This Roadmap Maps to the Capability Stack

| Stage | Primary Layers Covered |
|---|---|
| Stage 1 (Week 1–2) | Layer 0–2 |
| Stage 2 (Week 3–4) | Layer 3 (tool use part) |
| Stage 3 (Week 5–7) | Layer 4 + Layer 5 + Layer 6 |
| Stage 4 (Week 8) | Comprehensive observation (use Claude Code to see full-stack implementation) |
| Stage 5 (Week 9–10) | Layer 3 (multimodal, RAG, MCP) |
| Stage 6 (Week 11–12+) | Full-stack integrated application |

When entering a new stage, return to this table to know which layer of the capability stack you're at.

### LLM Harnessing vs. Adjacent Concepts

| Concept | Scope | Relationship |
|---|---|---|
| Prompt Engineering | Layer 1 | Subset of LLM Harnessing |
| Output Engineering | Layer 2 | Subset of LLM Harnessing |
| RAG Engineering | A subset of Layer 3 | Subset of LLM Harnessing |
| Agent Engineering | Layer 5–6 | Advanced phase of LLM Harnessing |
| **LLM Harnessing** | **Layer 0–6 full stack** | **Itself** |
| AI Engineering | LLM Harnessing + infra/deploy/cost | Includes LLM Harnessing |

**Stock interview line**:
> "I position my capability as full-stack LLM Harnessing — from API-layer details to multi-agent coordination. My differentiator is Layer 4 (reliability), because my ML/statistics background makes eval and grader design my strength."

### Reading List (only 3 readings for this stage)

Don't get greedy. This stage isn't about accumulating knowledge — it's about establishing a framework.

1. **Anthropic — Building Effective Agents** (30 minutes)
   - https://www.anthropic.com/research/building-effective-agents
   - First read: only look at the framework — workflow vs. agent, when not to use an agent.
2. **Chip Huyen — Building LLM Applications for Production** (45 minutes)
   - https://huyenchip.com/2023/04/11/llm-engineering.html
   - View the full LLM engineering stack from a production perspective.
3. **Karpathy — LLM OS Concept Diagram** (15 minutes)
   - Search "Karpathy LLM OS".
   - View LLMs as "the CPU of a new generation OS" — break out of the "chatbot" mindset.

### Prologue Exercises

**Exercise 0.1: Capability Stack Mapping (30 minutes)**

For each task below, label which layer it primarily falls in. This trains the muscle of "seeing a task and identifying its layer":

| Task | Layer? |
|---|---|
| Classify user input into 5 intents | _ |
| Make the LLM output valid JSON | _ |
| Add real-time weather to a chatbot | _ |
| Test a chatbot's accuracy on 100 cases | _ |
| Maintain context in a multi-turn conversation | _ |
| Let the LLM decide whether to search or compute first | _ |
| A PM agent assigning tasks to 3 engineer agents | _ |
| Handling event types when streaming | _ |
| Reduce token cost of system prompts | _ |
| Food image recognition + nutrition calculation | _ |

Answer key: 1, 2, 3, 4, 0–1, 5, 6, 0, 0–2, 3.

**Exercise 0.2: Build Your Capability Profile (30 minutes)**

In your notes, create `Chris's LLM Harnessing Capability Profile.md`:

```markdown
# Chris's LLM Harnessing Capability Profile

## Layer 0: API Mastery
- Current level: 0/5
- Target: 4/5
- Key skills to acquire: messages structure, parameters, streaming events

## Layer 1: Prompt Engineering
- Current level: ?/5
- ...

## Layer 6: Multi-Agent Coordination
- ...

## My differentiator
(One sentence about which layer you're stronger at than others, and why.)
```

Update the score and evidence ("Project X proved Layer 4 reached 4/5") as you complete each stage. **This profile is your "loadout" for interviews**.

**Exercise 0.3: Elevator Pitch (15 minutes)**

Write a 200-word answer to: "**What is LLM Harnessing? Why isn't it the same as Prompt Engineering?**"

Read it aloud after writing. This text will become a LinkedIn post or interview opening line.

### Two Disciplines That Span the Entire Roadmap

1. **Every project must be one you can explain on a whiteboard without Claude Code.** If an interviewer asks you to write the agent loop pseudo-code and you can't, you didn't learn it.
2. **At least one "hard mode" session per week**: Write a small demo from scratch without Claude Code. Claude Code is too capable — capable enough to give you the illusion of "I get it" when actually it wrote the code.

### Prologue Acceptance

- [ ] Can write the 7-layer capability stack from memory, with at least 2 specific skills per layer
- [ ] Can explain LLM Harnessing to a non-technical friend in 30 seconds
- [ ] Capability Profile document built, with current/target for each layer
- [ ] Finished reading the 3 must-read materials

---

## Stage 1: Building the Foundation (Week 1–2)

> **Capability Stack Position**: Layer 0 (API Mastery) + Layer 1 (Prompt Engineering) + Layer 2 (Output Control)

First, get familiar with the LLM as an API. The goal isn't learning frameworks — it's developing intuition for model behavior.

### Week 1: API Onboarding

#### Day 1–2: API Quickstart

- Sign up for Anthropic API, run through the Quickstart.
- Understand the messages structure, the separate `system` parameter, the required `max_tokens`, and the `stop_reason` field.
- **Model family selection**: Opus / Sonnet / Haiku. Mental model — for intelligence priority pick Opus, for speed Haiku, for balance Sonnet. **Key insight: real projects often use multiple models in one app** (Haiku for dataset generation, Sonnet for the main pipeline, Opus as grader).
- **Core parameters**: `temperature` (0–1), `max_tokens`, `stop_sequences`. Low temperature for extraction/classification, high temperature for creative work. Realize that temperature isn't a "creativity switch" — it's a shape modifier on the token probability distribution.

**Briefly look at the OpenAI API for comparison** (half a day): Understand interface design differences (system position, tool use schema, streaming format). In interviews, being able to articulate the differences between two providers sounds 100x more professional than "I prefer Claude."

#### Day 3: Multi-Turn Conversation Basics

This is prerequisite knowledge for the agent loop and must be solidified first.

- **Core fact**: The API stores no state — every request is independent. You must **manually maintain the messages list**.
- Write two helpers: `add_user_message(messages, text)` and `add_assistant_message(messages, response)`. Wrap them once and reuse everywhere.
- Write a CLI chat script with multi-turn conversations preserving context. **These 30 lines of code are the skeleton of every agent loop you'll write later**.

#### Day 4–5: Deep Read of Prompt Engineering Documentation

Read the [Anthropic Prompt Engineering documentation](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview) in this order. Validate each technique with your own example:

1. Be clear and direct
2. Use examples (multishot prompting)
3. Let Claude think (Chain of Thought)
4. Use XML tags
5. Give Claude a role (system prompts)
6. Prefill Claude's response
7. Chain complex prompts

**Mindset**: These techniques compose. A high-quality prompt is usually a combination — system prompt + XML structure + 2–3 examples + CoT guidance + prefill opener.

### Week 2: Treating the LLM as a Function

#### Day 6: The Output Control Trio

Practice these three closely related techniques together:

1. **Prefill assistant content**: Manually inject an assistant message to force a format.
2. **Stop sequences**: The model stops when it generates a specified string.
3. **Prefill + Stop sequence combo**: Classic structured-output pattern — prefill `` ```json ``, stop sequence `` ``` ``, the model only outputs the JSON in between.

#### Day 7: Streaming Basics

- Learn `client.messages.stream()` and event types (`message_start`, `content_block_delta`, `message_stop`).
- Write a streaming-version chat script.
- **Why learn this now**: When you write the agent loop later, event-type concepts will recur (`tool_use` is also a content block). Build the foundation now.

#### Day 8–10: Four Core Exercises

**Exercise 1.1: Strict JSON Output**

- Input a product review, output `{sentiment, aspects, summary}` JSON.
- Run 20 test cases, count parse failures.
- Use prompt engineering tricks to drive the failure rate to 0: prefill `{`, system prompt explicitly forbidding markdown, add examples.
- **Output**: A "JSON Output Best Practices" note.

**Exercise 1.2: Classification Task (Your First Eval)**

- Build an intent classifier (5 categories).
- Three versions: zero-shot / few-shot / CoT.
- Hand-craft 20 test cases (5 per category).
- Compare accuracy across versions.
- **Key**: This is your first encounter with eval. From this moment on, build the muscle memory of "evaluation".

**Exercise 1.3: Information Extraction**

- Input a job description, extract structured fields (company, role, salary, required skills, location, remote).
- Use XML tags to organize the prompt: `<job_description>`, `<output_format>`.
- Handle edge cases: salary missing → return `null` or empty?
- **The output of this exercise will be reused later in Project 5 (the job-search multi-agent)**.

**Exercise 1.4 (Optional): Brute-Force RAG Prototype**

- Stuff your full ML notes (markdown files) into the context. User asks questions, model answers.
- No embedding, no retrieval — just stuff the full text in.
- **Purpose**: Experience long-context behavior, build engineering intuition that "in many scenarios, stuffing everything beats RAG."

### Claude Code Collaboration Discipline (Stage 1)

**Use Claude Code for**:
- Project scaffolding (mkdir, pip install, .env config)
- Explaining specific SDK doc parameters
- Reviewing code you've written ("how could this prompt be improved?")
- Generating test cases (have it generate 20 product reviews of different sentiment)

**Do NOT use Claude Code for**:
- Writing the core code of practice exercises
- Paraphrasing the prompt engineering documentation (read it yourself, build raw intuition)

### Stage 1 Acceptance

- [ ] Can write a complete API call without consulting docs (system, messages, max_tokens, temperature)
- [ ] Can explain the difference between system prompt and user message
- [ ] Can explain the effect of temperature on generation
- [ ] Can write multi-turn chat scripts, including streaming version
- [ ] JSON output script: 100% parse success across 20 test cases
- [ ] Can list at least 5 prompt engineering techniques + examples
- [ ] Have a "Prompt Engineering Pitfalls" note
- [ ] Capability Profile: Layer 0–2 each at 3+/5

---

## Stage 2: Tool Use (Week 3–4)

> **Capability Stack Position**: Layer 3 (the core mechanism of Augmentation: tool use)

Tool use is the core mechanism of agents. This is the critical step from "calling an LLM" to "building an agent".

### Week 3: Single-Tool Foundation

#### Day 1–2: Tool Use Concepts and Schemas

- Read the Anthropic SDK tool use documentation.
- Understand how `tools` parameters, `tool_use` blocks, and `tool_result` blocks flow back and forth.
- Learn JSON Schema syntax. Naming convention: function `get_weather`, schema `get_weather_schema`, wrap in `ToolParam`.

#### Day 3: Tool Function Error Handling Design

A detail beginners most often overlook — call it out explicitly.

- **Core insight: error messages raised by tool functions are read by Claude**, not by developers.
- This means error messages should read like "instructions for use" — telling Claude what's wrong and how to fix it.

```python
# Bad
raise ValueError("invalid input")

# Good
raise ValueError("date_format cannot be empty, expected format like '%Y-%m-%d'")
```

- This design pattern is key to agent robustness — agents self-correct from these error messages.

#### Day 4–5: Write Your First Single-Tool Demo

- Define a `get_weather(city)` tool.
- **Hand-write a while loop, no frameworks**. Loop structure:
  ```
  while True:
      response = call_claude(messages, tools)
      messages.append(assistant_message)
      if response.stop_reason != "tool_use":
          break
      for tool_use in response.tool_use_blocks:
          result = run_tool(tool_use.name, tool_use.input)
          messages.append(tool_result_message(tool_use.id, result))
  ```
- **This is the most important exercise in the entire roadmap. Write it from scratch, no Claude Code.**
- After it works, ask Claude Code to review.

### Week 4: Multiple Tools and Advanced Usage

#### Day 6–7: Multi-Tool + Tool Chaining

- Add `calculator`, `search_web`, etc. Let Claude pick and combine them autonomously.
- Implement a `run_tool` dispatcher (if/elif routing to specific functions).
- Handle the case where one message contains multiple tool_use blocks (each tool_use needs a corresponding tool_result).

#### Day 8: Using Tools for Structured Output (More Reliable Way)

The upgraded version of Stage 1's prefill+stop:

- Define a schema describing the JSON structure you want.
- Register the schema as a tool.
- Use `tool_choice = {"type": "tool", "name": "your_schema"}` to **force** Claude to call it.
- The `input` Claude fills when calling the tool is JSON conforming to the schema — much more reliable than prefill.
- **Going forward, prefer this method for information extraction and data generation.**

#### Day 9–10: Built-in Tools and Advanced Features

- **Batch Tool**: Claude calls multiple tools in parallel within a single request. Understand the concept.
- **Web Search Tool** (built-in): No need to implement yourself. Note `max_uses` and `allowed_domains` — when working on health content, restrict to nih.gov, etc.
- **Text Editor Tool** (built-in): Claude's built-in file read/write tool, used directly when building coding agents.
- **Extended Thinking**: Enable for complex reasoning tasks. Note `thinking_budget` (minimum 1024) must be < `max_tokens`. **When to enable**: After exhausting prompt optimization without hitting target accuracy.

### Stage 2 Acceptance

- [ ] Can write the agent loop pseudo-code on a whiteboard from scratch
- [ ] Can explain the role of tool_use_id
- [ ] Know when to force a tool with tool_choice vs. let the model choose freely
- [ ] Know what built-in tools exist, avoiding reinventing the wheel
- [ ] Can explain the design logic of error messages in your tool functions
- [ ] Capability Profile: Layer 3 at 3/5

---

## Stage 3: Patterns + Multi-Agent + Eval (Week 5–7)

> **Capability Stack Position**: Layer 4 (Reliability) + Layer 5 (Agent Engineering) + Layer 6 (Multi-Agent)

These are the core three weeks. Patterns give you the "map" for agent design, Multi-Agent teaches you the advanced form of agents, and Eval is the differentiator from your MLE background.

### Week 5: Building Effective Agents (5 Patterns)

Carefully read [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — at least twice. Master 5 patterns:

1. **Prompt Chaining**: Break complex tasks into sequential steps.
2. **Routing**: Classify user input into different processing pipelines.
3. **Parallelization**: Execute subtasks in parallel, aggregate at the end.
4. **Orchestrator-Workers**: Dynamically split tasks, dispatch, and aggregate (the entry-level form of multi-agent).
5. **Evaluator-Optimizer**: Producer outputs result → evaluator scores → reproduce if not good enough.

Plus the design principles for full autonomous agents.

Companion: Run each pattern from [anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook).

**Week 5 Acceptance**: Can sketch the topology of all 5 patterns on a whiteboard and give a real-world example for each.

### Week 6: Multi-Agent (3-Day Intensive)

> Multi-Agent is Layer 6. But Anthropic's core position is: **first try workflow, then agent if not enough, then multi-agent only if a single agent isn't enough**. This week teaches you how to master multi-agent — **and when not to use it**.

#### Day 1: Concepts and Stance (2–3 hours)

**Three forms of Multi-Agent**:

**Form 1: Orchestrator-Workers (most practical)**
```
        Orchestrator
       /     |      \
      W1    W2      W3
       \     |      /
        Aggregator
```
- Suitable for: Decomposable tasks with relatively independent subtasks.
- Examples: Anthropic's multi-agent research system, Claude Code's subagent.

**Form 2: Conversational (multi-agent dialogues)**
```
   Agent A  ◄──►  Agent B
   (writer)       (critic)
```
- Suitable for: Multi-perspective, adversarial improvement.
- This is the extension of evaluator-optimizer.

**Form 3: Hierarchical**
```
  Manager → TeamLead → Workers
```
- Suitable for: Ultra-complex tasks, enterprise scale.
- **Most situations you don't need this**. The more layers, the harder error propagation, the more cost explodes, the more painful debugging becomes.

**Five engineering challenges** (memorize — frequently asked in interviews):

1. **Context passing**: How does what A knows reach B? Full pass is expensive, summary loses info, shared memory adds complexity.
2. **Coordination**: Hardcode vs. LLM-decided? In practice, often hybrid.
3. **Error propagation**: When a worker fails, what does the orchestrator do? Retry? Degrade? Mark as failed?
4. **Cost explosion**: Single agent ~5 LLM calls; 3-agent system 15+. Worker uses Haiku, orchestrator uses Sonnet/Opus, enable prompt caching, set hard limits.
5. **Eval is extremely hard**: Need to eval the whole + each worker + orchestrator decomposition quality.

**Day 1 Reading**:

1. **Building Effective Agents (re-read, multi-agent perspective)** (45 minutes)
2. **Anthropic — How we built our multi-agent research system** (1 hour, take notes)
   - Key: Their architecture, how many times the token usage of single-agent, context passing, what scenarios they **don't** recommend multi-agent for.
3. **Cognition — Don't Build Multi-Agents** (30 minutes, opposing view)
   - Read alongside Anthropic's article to build dialectical thinking.

**Day 1 Exercise**: Write a `multi_agent_decision_tree.md`:

```markdown
# Multi-Agent Decision Tree

1. Can a single LLM call solve this task?
   - Yes → don't make an agent
   - No → proceed to 2

2. Are the steps known and fixed?
   - Yes → use workflow (chain / route / parallelize)
   - No → proceed to 3

3. Does it require LLM autonomous path decisions?
   - Yes → use single agent
   - Single agent isn't enough → proceed to 4

4. Can the task be naturally decomposed into independent subtasks?
   - Yes → orchestrator-workers
   - Need multi-perspective adversarial → conversational multi-agent
   - Otherwise → re-examine, may still be single agent

## Reverse checklist (when NOT to do multi-agent)
- [ ] Doing it because it "looks fancy" — reconsider
- [ ] Single agent not fully tuned — debug single agent first
- [ ] Cost not budgeted — multi-agent burns money
- [ ] No eval plan — will become a black box
```

#### Day 2: Hands-On — Hand-Code Orchestrator-Workers (2–3 hours)

**Project name**: `tech_comparison_agent`

**User input**: "I'm an ML engineer doing production inference; compare PyTorch vs. TensorFlow."

**Architecture**:
```
User Input
    ▼
Orchestrator (Sonnet)  ── Decompose dimensions
    ├──► Worker 1: Performance research  (Haiku + web_search)
    ├──► Worker 2: Ecosystem research    (Haiku + web_search)
    └──► Worker 3: Deployment research   (Haiku + web_search)
    ▼
Aggregator (Sonnet)  ── Synthesize report
```

**Key design decisions**:
1. **How does the orchestrator decompose?**: Use tool use to force structured output, schema specifies output `{tasks: [{dimension, query}]}`. Don't free-text and parse.
2. **How do workers run in parallel?**: `asyncio.gather`. One core benefit of multi-agent is parallelism — if you go serial, you lose half the value.
3. **How much context to pass to workers?**: Don't pass full input to all workers. Have the orchestrator write a refined sub-prompt for each worker. **This is the core training in context engineering.**
4. **What does the aggregator see?**: Original question + 3 worker outputs. Don't let the aggregator web_search again — its job is synthesis.

**Code skeleton** (fill in yourself, **don't have Claude Code write it directly**):

```python
import anthropic
import asyncio
import json

client = anthropic.Anthropic()

ORCHESTRATOR_PROMPT = """..."""  # TODO write yourself
WORKER_PROMPT = """..."""        # TODO
AGGREGATOR_PROMPT = """..."""    # TODO

PLAN_TASK_SCHEMA = {
    "name": "plan_research",
    "description": "...",
    "input_schema": {
        "type": "object",
        "properties": {
            "tasks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "dimension": {"type": "string"},
                        "query": {"type": "string"}
                    },
                    "required": ["dimension", "query"]
                }
            }
        },
        "required": ["tasks"]
    }
}

def orchestrate(user_input: str) -> list[dict]:
    """Use tool_choice to force calling plan_research"""
    pass  # TODO

async def run_worker(task: dict) -> dict:
    """Haiku + web_search built-in tool, run agent loop"""
    pass  # TODO

def aggregate(user_input: str, worker_outputs: list[dict]) -> str:
    """Sonnet synthesizes report"""
    pass  # TODO

async def tech_comparison_agent(user_input: str) -> str:
    tasks = orchestrate(user_input)
    print(f"[ORCH] Decomposed into {len(tasks)} subtasks")
    worker_outputs = await asyncio.gather(*[run_worker(t) for t in tasks])
    return aggregate(user_input, worker_outputs)

if __name__ == "__main__":
    user_input = "I'm an ML engineer doing production inference; compare PyTorch vs. TensorFlow"
    print(asyncio.run(tech_comparison_agent(user_input)))
```

**Reflection exercise** (write in notes, 30 minutes):
1. How many tokens did this demo consume in one run? How many times that of a single agent doing the same task?
2. Total time? How much do parallel vs. serial differ?
3. Intentionally garble one worker's query — how does the orchestrator handle it?
4. Which information did you pass to each worker? What was necessary, what was redundant?
5. What if you used a workflow (hardcoded chain of 3 dimensions) instead? What scenarios does workflow win?

**The last question is the most important** — this is the concrete embodiment of Anthropic's stance.

#### Day 3: Multi-Agent Eval (2 hours)

Design a 4-dimensional eval for the Day 2 demo:

1. **Final report quality**: Opus model-based grading. Evaluate completeness, accuracy, depth, readability, scoring 1–10.
2. **Worker subtask quality**: Eval each worker individually.
3. **Orchestrator decomposition quality**: Use an LLM to judge "are the dimensions split reasonably to cover the user question?"
4. **Cost & latency**: Programmatic recording of total tokens, latency, num LLM calls.

**Key comparison experiment**: Implement a control group — same task with workflow (hardcoded 3 dimensions called serially). Run on the same 5 test cases:

| Metric | Multi-Agent | Workflow |
|---|---|---|
| Avg final quality | ? | ? |
| Avg cost (tokens) | ? | ? |
| Avg latency | ? | ? |
| Flexibility | ? | ? |

**This table will tell you the real value boundary of multi-agent — workflow may win on some cases**. This is engineering reality.

### Week 7: Eval Deep Dive (Your Differentiator)

> Your MLE / statistics background is a force multiplier here. **Many LLM engineers write prompts purely on intuition; systematic eval skill is rare**. This is your "loadout" for interviews.

#### Day 1: 6-Step Eval Workflow

1. Write initial prompt
2. Create eval dataset (test cases)
3. Insert dataset inputs into prompt template
4. Run LLM to get outputs
5. Use grader to score (1–10), compute average
6. Modify prompt based on scores, repeat

#### Day 2: Test Dataset Generation

- Hand-write vs. Claude-generated.
- **Use Haiku to bulk-generate test cases**: prompt + prefill `` ```json `` + stop `` ``` ``.
- Save generated dataset as JSON. Build the habit of "my own eval dataset".

#### Day 3: Code-Based Grading

- `validate_json()`: parse success returns 10
- `validate_python()`: `ast.parse()`
- `validate_regex()`: `re.compile()`
- Use cases: output formats that are programmatically verifiable

#### Day 4: Model-Based Grading (LLM-as-judge)

- Use an LLM call (recommended Opus as grader) to evaluate another LLM's output.
- **Key technique**: Have the grader output strengths / weaknesses / reasoning / score together — don't just output score. Models tend toward middle scores when asked for score alone.
- Force structured output via JSON tool.
- Use cases: subjective evaluations like quality, style, follow-instructions.

#### Day 5: Combined Grading

- `final_score = (model_score + code_score) / 2`
- Your RecSys background is useful here — **this is essentially multi-signal fusion ranking, the same idea as hybrid search**.

#### Day 6–7: Hands-On Exercise

Take the prompt from Stage 1 Exercise 1.2 (intent classifier) and run the full eval pipeline:

- Generate 50 test cases
- Three prompt versions (zero-shot / few-shot / CoT) running through eval
- Score with model-based grader
- Output a comparison report: which version is best, why, and where

**This report becomes your first eval case in your portfolio**. You can talk about it directly in interviews.

### Stage 3 Acceptance

- [ ] Can articulate the 5 patterns and when to use each
- [ ] Can articulate multi-agent's 3 forms + 5 challenges
- [ ] **Can explain in 60 seconds "when not to use multi-agent"** (interview kill question)
- [ ] GitHub has a `tech_comparison_agent` project with README covering architecture, cost, comparison-vs-workflow conclusion
- [ ] Have a complete eval pipeline (dataset gen + grader + report output)
- [ ] Intent classifier eval comparison report complete
- [ ] Read Anthropic multi-agent research article and can quote specific numbers
- [ ] Capability Profile: Layer 4 at 4/5, Layer 5–6 at 3/5

---

## Stage 4: Studying Claude Code as a Reference Implementation (Week 8)

> **Capability Stack Position**: Comprehensive observation. The previous three stages covered Layer 0–6. This week uses Claude Code, an industrial-grade autonomous coding agent, as a "reference implementation" to tie everything together.

| Claude Code Mechanism | Capability Stack Concept |
|---|---|
| `CLAUDE.md` | Layer 1: project-level system prompt |
| Slash commands | Layer 1: Prompt template engineering |
| Subagents | Layer 6: Orchestrator-workers pattern |
| Hooks | Layer 5: Agent lifecycle control plane |
| Plan mode / Thinking | Layer 5: ReAct / Plan-and-Execute |
| Memory (project / local / user) | Layer 5: Multi-tier context management |
| MCP servers | Layer 3: Standardized tool use |

**Practice approach**: Use Claude Code daily — LeetCode practice, organizing interview notes, writing BQ stories. **Consciously observe its behavior**: When does it call tools? When does it ask for confirmation? How does it recover from errors? These observations will become your intuition for designing agents.

**Advanced techniques**:

- **Git worktrees + multiple Claude Code in parallel**: For complex projects, give different tasks different worktrees. Each Claude instance works on an isolated branch and merges at the end. This skill lets you "command a virtual team of engineers".
- **Custom slash commands**: Write markdown templates in `.claude/commands/` to crystallize high-frequency workflows (e.g., "help me write a new NomNom endpoint") into commands.
- **Three-step prompting**: (1) Have Claude find relevant files (2) Have Claude produce a plan but no code (3) Have Claude implement the plan. Much better than diving straight into "write the code".

### Stage 4 Acceptance

- [ ] Your main project repo has a `CLAUDE.md`
- [ ] Have written at least 1 custom slash command
- [ ] Have used git worktree for parallel work at least once
- [ ] Can connect any Claude Code behavior to a specific capability layer

---

## Stage 5: Multimodal + MCP (Week 9–10)

> **Capability Stack Position**: Layer 3 extension (multimodal, files, citations) + Layer 5 engineering (caching, SDK, MCP)

### Week 9: Multimodal + Advanced API Features

#### Multimodal (NomNom essentials)

- **Image Support**: Base64 encoding + image block. **Key insight: image recognition accuracy is extremely dependent on prompt quality** — simple prompts fail. Use step-by-step instructions, one-shot examples, explicit analysis frameworks. NomNom's food recognition relies on this.
- **PDF Support**: document block + media_type `application/pdf`. Claude reads text, charts, and tables from PDFs directly — nutrition label PDF parsing uses this.
- **Citations**: `"citations": {"enabled": true}` + add title to source. Claude annotates each output segment with the source location (page number or character position). **This is the killer feature for hallucination prevention in RAG agents** — also the foundation of NomNom's "nutrition advice source" feature.

#### Cost and Latency Optimization

- **Prompt Caching**: Cache unchanged system prompts and tool schemas. Repeated requests read from cache — cheap and fast. Rules: cache lasts 1 hour; minimum 1024 tokens; max 4 breakpoints; any change before cached content invalidates the entire cache. **For an agent like NomNom with long system prompts and many tools, this is mandatory**.
- **Code Execution + Files API** (optional learning): Upload a file to get a file ID. Claude runs Python on it in a Docker container. May be useful for nutrition data computation later.

### Week 10: Agent SDK + MCP Deep Dive

#### Claude Agent SDK

- Anthropic's official agent library — saves work versus rolling your own loop, while preserving controllability.
- Claude Code itself is built around this set of ideas — once you're familiar with its behavior, learning the SDK is smooth.

#### The Full MCP Trio (not just tools)

- **Tools**: `@mcp.tool` decorator. Function signatures auto-generate JSON schemas. Same mechanism as the tool use you already learned — just standardized.
- **Resources**: `@mcp.resource` decorator. **Proactively expose data to clients**.
  - Difference from tools: tools are reactive (Claude decides when to call); resources are proactive (clients read directly).
  - URI types — direct (`docs://documents`) and templated (`docs://documents/{doc_id}`).
- **Prompts**: `@mcpserver.prompt` decorator. High-quality prompt templates pre-baked by server authors. Clients expose them as slash commands to users.
- **MCP Inspector**: `mcp dev server.py` launches a browser debugger — invaluable during development.

#### Hands-On: Write an MCP Server

- Expose your LeetCode solution records or NomNom food database as tools + resources.
- Let Claude Code query your MCP server directly.
- **This step gives you very concrete understanding of "how agents extend capabilities"**.

#### LangGraph (Optional)

- Graph-based agent workflow framework, mainstream choice for complex agent workflows.
- LangChain itself can be skipped — go straight to LangGraph.
- **Solidify Anthropic's native SDK and MCP first, then look at LangGraph so the framework doesn't kidnap your thinking**.

### Stage 5 Acceptance

- [ ] Can call multimodal with image + PDF blocks
- [ ] Can add citations to a RAG system
- [ ] Can add prompt caching to an agent with a long system prompt and verify cache hits
- [ ] Have written an MCP server with all 3 components (tool + resource + prompt)
- [ ] Capability Profile: Layer 3 at 4/5, Layer 5 at 4/5

---

## Stage 6: Capstone Projects (Week 11–12+)

> **Capability Stack Position**: Full-stack integrated application. Each project includes complete eval — this is what differentiates you from other candidates.

### Project 1: Personal RAG Assistant + Eval

**Use case**: Pairs with your MLE interview prep.

**Features**:
- Index your resume, interview notes, and ML concept notes.
- Full RAG pipeline: chunking → embedding → vector store → retrieval → reranking.
- Use BM25 + vector hybrid retrieval (hybrid search, aligned with your RecSys background).

**Eval**:
- Hand-craft 30 Q&A pairs
- Retrieval accuracy (NDCG@5) + answer quality (model-based grading)

### Project 2: Code Review Agent

**Features**:
- LeetCode solution → complexity analysis + bug detection + optimization suggestions
- Use tool use for structured output (JSON report)

**Eval**:
- Bug ground truth from intentionally inserted bugs
- Measure detection rate, false positive rate

### Project 3: NomNom Nutrition Analysis Agent (Your Main Project)

**Capstone of capstones** — uses everything learned:

- **Multimodal**: Photo of food → recognition → nutrition calculation (image support)
- **PDF parsing**: Nutrition label PDFs (PDF support)
- **RAG**: Nutrition knowledge base (with citations)
- **Tool use**: Nutrition database queries, user preference memory
- **Prompt caching**: Cache the static "nutrition expert" system prompt
- **3-dimensional eval**: Recognition accuracy + nutrition calculation correctness + recommendation reasonableness

### Project 4: BQ Interview Simulation Agent (Optional)

**Features**:
- Input your 5 STAR stories
- Agent plays interviewer, asks dynamic follow-ups, scores per leadership principles

**Eval**:
- Compare to real interviewer scoring; tune the grader prompt

**Bonus value**: Posting it on social media as "career switch journal" makes excellent content.

### Project 5: Job-Search Multi-Agent System (Capstone)

**Layer 6 mastery** — capstone of the entire roadmap:

- **Job Search Agent**: Search matching roles based on preferences (web_search built-in tool)
- **JD Analysis Agent**: Extract key skills, culture, salary from each JD (reuse the output from Stage 1 Exercise 1.3)
- **Resume Tailoring Agent**: Modify your resume bullets per JD
- **Cover Letter Agent**: Write customized cover letters
- **Orchestrator**: Coordinate the 4 agents, output the "Today's Job Search Action Pack"

**Eval**:
- Tailored resume vs. JD keyword match rate
- Bullet rewriting quality (model-based)
- Coverage of must-have skills

**This project simultaneously serves your MLE job search** — a true "learn-while-doing" benchmark.

### Stage 6 Acceptance

- [ ] Complete at least 3 projects (recommended 1, 3, 5)
- [ ] Each project has a README documenting architecture, eval results, and design tradeoffs
- [ ] At least 1 project can be a 30-minute deep-dive case in interviews
- [ ] Capability Profile: All layers at 4+/5

---

## Appendix A: Skip List

These topics are in the notes but **not included** in this roadmap — intentionally:

| Topic | Skip Reason | When to Come Back |
|---|---|---|
| Computer Use | Non-core, only for QA testing | When doing UI automation testing |
| Fine-Grained Tool Calling | Streaming micro-optimization | When doing real-time UI |
| Code Execution + Files API | Specific scenarios | When NomNom truly needs heavy data computation |
| Automated Debugging (GitHub Action + Claude Code) | DevOps-leaning | After deploying the project to production |

---

## Appendix B: Reading List Summary

In time order:

**Week 0 (Prologue)**:
1. Anthropic — Building Effective Agents (first read)
2. Chip Huyen — Building LLM Applications for Production
3. Karpathy — LLM OS Concept Diagram

**Week 1–4**:
4. Anthropic Prompt Engineering documentation
5. Anthropic Tool Use documentation

**Week 5–7**:
6. Anthropic — Building Effective Agents (re-read 2nd, 3rd time)
7. anthropic-cookbook (run each pattern)
8. Anthropic — How we built our multi-agent research system
9. Cognition — Don't Build Multi-Agents (opposing view)

**Week 8**:
10. Claude Code official documentation (read while using)

**Week 9–10**:
11. Anthropic Multimodal documentation
12. Claude Agent SDK documentation
13. MCP official spec

**Throughout**:
14. Lilian Weng — LLM Powered Autonomous Agents (academic-style overview)

---

## Timeline Overview

| Stage | Weeks | Topic | Primary Layer |
|---|---|---|---|
| Prologue | Week 0 | LLM Harnessing concept map | Global |
| 1 | Week 1–2 | API + Prompt + Output Control | Layer 0–2 |
| 2 | Week 3–4 | Tool Use + Agent Loop | Layer 3 |
| 3 | Week 5–7 | Patterns + Multi-Agent + Eval | Layer 4–6 |
| 4 | Week 8 | Claude Code as reference impl | Comprehensive |
| 5 | Week 9–10 | Multimodal + MCP | Layer 3 + 5 |
| 6 | Week 11–12+ | Capstone projects (5) | Full-stack |

**Total: 12 weeks**, fully parallelizable with your LeetCode + BQ prep.

---

## Final Notes

The design philosophy of this roadmap:

1. **Start with the cognitive map** (capability stack in the prologue) — so you know what you're learning and why.
2. **Each layer has dedicated training** — you won't be pushed onto Layer 6 with weak Layer 1.
3. **Each stage has hands-on projects** — learning and doing aren't separated.
4. **Eval runs throughout** — from Stage 1 Exercise 1.2 with eval, to Stage 6 every project with eval. This is your differentiator moat.
5. **Personalization embedded** — NomNom, interview prep, and job search are real scenarios for projects. Learn-and-use.

After 12 weeks, you should have:
- A whiteboard-explainable LLM Harnessing knowledge system
- 5 portfolio projects (each with eval)
- A continuously updated Capability Profile (your "loadout")
- Ability to articulate each layer in LLM Engineer / AI Engineer interviews

Good luck.

