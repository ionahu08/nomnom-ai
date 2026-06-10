"""
Phase 5 Day 8: Single Agent Comparison

Single agent approach to the same task: Compare PyTorch vs. TensorFlow for production.

ARCHITECTURE:
  user_input
      ↓
  Single Claude Agent (Sonnet) with web_search tool
      ├─ Loop 1: "I need performance data" → web_search → reads result
      ├─ Loop 2: "I need ecosystem info" → web_search → reads result
      ├─ Loop 3: "I need deployment info" → web_search → reads result
      └─ Loop 4: "I have enough info" → generates report → end_turn

vs. Day 7 Orchestrator-Workers:
  - Day 7: Orchestrator decomposes → 3 workers in parallel → Aggregator synthesizes
  - Day 8: Single agent decides autonomously → iterates → completes

COMPARISON:
  Metric                 | Day 7 (Orch-Workers) | Day 8 (Single Agent)
  ─────────────────────────────────────────────────────────────────
  Latency                | ~10s                 | ~5-8s (faster)
  Total Cost             | ~$0.023              | ~$0.025 (2% more)
  Output Structure       | Predictable (3 sec)  | Varies (flexible)
  Code Complexity        | Medium (asyncio)     | Low (simple loop)
  Parallelization        | Yes (3 workers)      | No (sequential)

Run: python3 08_single_agent_comparison.py
"""

import json
import sys
import time
from typing import Optional

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic library not installed")
    print("Install with: pip install anthropic")
    sys.exit(1)


def mock_web_search(query: str) -> str:
    """Mock web search (simulated results)"""
    print(f"    [Web Search] {query}")

    # Simulated search results database
    results_db = {
        "pytorch performance": "PyTorch shows 15-20% faster training on typical CNN models. Good GPU optimization.",
        "tensorflow performance": "TensorFlow is competitive, with better inference optimization on TPUs.",
        "pytorch ecosystem": "PyTorch has strong research community, lots of papers. Hugging Face built on PyTorch.",
        "tensorflow ecosystem": "TensorFlow has more production deployments. Better ops tooling (TFX).",
        "pytorch deployment": "PyTorch deployment: TorchServe, ONNX export. Growing production use.",
        "tensorflow deployment": "TensorFlow has TF Serving, more mature ops. Better mobile support.",
    }

    for key, result in results_db.items():
        if key.split()[0].lower() in query.lower() and key.split()[1].lower() in query.lower():
            return result

    return f"Research on '{query}' shows competitive advantages for both frameworks."


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool and return the result as a string"""
    if tool_name == "web_search":
        result = mock_web_search(tool_input.get("query", ""))
        return result
    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})


def run_single_agent(user_input: str):
    """
    Run a single agent that autonomously decides what tools to call.

    The agent reads the user input and decides:
    - Do I need performance data?
    - Do I need ecosystem info?
    - Do I need deployment info?
    - Do I have enough to write a report?

    It loops until it decides it has enough info and generates the final report.
    """
    print("\n" + "#"*70)
    print("# SINGLE AGENT: PyTorch vs. TensorFlow Comparison")
    print("#"*70)
    print(f"User: {user_input}\n")

    client = anthropic.Anthropic()

    # Define tools the agent can use
    tools = [
        {
            "name": "web_search",
            "description": "Search the web for information about a topic",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    ]

    # Initialize message history
    messages = [
        {
            "role": "user",
            "content": user_input
        }
    ]

    # Agent loop
    loop_count = 0
    max_loops = 10
    start_time = time.time()

    while loop_count < max_loops:
        loop_count += 1
        print(f"\n{'─'*70}")
        print(f"Loop #{loop_count}: Agent decides what to do")
        print(f"{'─'*70}")

        # Call Claude with tools
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,  # Increased to allow synthesis after multiple searches
            tools=tools,
            messages=messages
        )

        print(f"Stop reason: {response.stop_reason}")

        # Check if agent is done
        if response.stop_reason == "end_turn":
            print("\n✓ Agent finished (end_turn)")
            # Extract and print final response
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"\nFinal Answer:\n{block.text}")
            break

        # Handle tool use
        if response.stop_reason == "tool_use":
            # Add agent's response to messages (including tool calls)
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            # Process each tool call
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

                    print(f"\n{'='*70}")
                    print(f"Tool Call: {tool_name}")
                    print(f"{'='*70}")

                    # Execute the tool
                    result = execute_tool(tool_name, tool_input)

                    print(f"Tool Result: {result}")

                    # Record the tool result
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            # Add all tool results in a single user message
            messages.append({
                "role": "user",
                "content": tool_results
            })

            print(f"↻ Agent will consider {len(tool_results)} tool result(s) and decide next step")
        else:
            print(f"Unexpected stop reason: {response.stop_reason}")
            break

    elapsed = time.time() - start_time

    if loop_count >= max_loops:
        print(f"\n⚠ Reached max loops ({max_loops})")

    print(f"\n{'='*70}")
    print(f"METRICS")
    print(f"{'='*70}")
    print(f"Loops: {loop_count}")
    print(f"Total Latency: {elapsed:.2f}s")
    print(f"\nComparison with Day 7 (Orchestrator-Workers):")
    print(f"  Day 7 latency: ~10s (orchestrator 3s + workers 4s parallel + aggregator 3s)")
    print(f"  Day 8 latency: ~{elapsed:.1f}s (single agent sequential)")
    if elapsed < 10:
        print(f"  ✓ Day 8 is {10/elapsed:.1f}x faster")
    else:
        print(f"  ✗ Day 8 is slower (depends on agent's research choices)")


if __name__ == "__main__":
    user_input = "Compare PyTorch vs. TensorFlow for production machine learning. Be comprehensive."

    # Run the single agent
    run_single_agent(user_input)
