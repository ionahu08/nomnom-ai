"""
Phase 5 Day 7: Tech Comparison Agent

Orchestrator-Workers multi-agent system.

User: "Compare PyTorch vs. TensorFlow for production"
Orchestrator decomposes → 3 workers research in parallel → Aggregator synthesizes

Run: python3 07_tech_comparison_agent.py
"""

import asyncio
import json
import sys
from typing import Optional

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic library not installed")
    print("Install with: pip install anthropic")
    sys.exit(1)


def get_orchestrator_tools():
    """Define the tool that orchestrator uses to decompose tasks"""
    return [
        {
            "name": "decompose_research",
            "description": "Decompose a research task into independent research dimensions",
            "input_schema": {
                "type": "object",
                "properties": {
                    "research_tasks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "dimension": {
                                    "type": "string",
                                    "description": "The aspect to research (e.g., Performance, Ecosystem, Deployment)"
                                },
                                "query": {
                                    "type": "string",
                                    "description": "The specific research query for this dimension"
                                }
                            },
                            "required": ["dimension", "query"]
                        },
                        "description": "List of research dimensions and queries"
                    }
                },
                "required": ["research_tasks"]
            }
        }
    ]


def get_worker_tools():
    """Define tools that workers can use (web search simulation)"""
    return [
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


def mock_web_search(query: str) -> str:
    """Mock web search (returns simulated results)"""
    print(f"    [Web Search] {query}")

    # Simulated search results
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


async def run_worker(dimension: str, query: str, worker_id: int) -> dict:
    """
    Run a single worker agent.
    Worker receives ONLY its sub-task, not the full user input.
    """
    print(f"\n{'─'*70}")
    print(f"Worker {worker_id}: {dimension}")
    print(f"{'─'*70}")

    client = anthropic.Anthropic()

    # Worker gets sub-prompt only (not full user input)
    messages = [
        {
            "role": "user",
            "content": f"""Research and summarize findings for this comparison dimension:

Dimension: {dimension}
Query: {query}

Use web search to find relevant information. Then provide a concise summary (2-3 paragraphs) with key findings."""
        }
    ]

    loop_count = 0
    while loop_count < 5:  # Max 5 loops per worker
        loop_count += 1

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800,
            tools=get_worker_tools(),
            messages=messages
        )

        if response.stop_reason == "end_turn":
            # Worker finished
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"\nFindings:\n{block.text[:300]}...")  # Print first 300 chars
                    return {
                        "dimension": dimension,
                        "findings": block.text,
                        "status": "complete"
                    }
            break

        if response.stop_reason == "tool_use":
            # Worker wants to search
            messages.append({"role": "assistant", "content": response.content})

            # Execute tool
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    if block.name == "web_search":
                        result = mock_web_search(block.input.get("query", ""))
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })

            messages.append({"role": "user", "content": tool_results})

    return {
        "dimension": dimension,
        "findings": "Research inconclusive",
        "status": "incomplete"
    }


def run_orchestrator(user_input: str) -> Optional[list]:
    """
    Orchestrator decides what research to do and decomposes into tasks.
    Returns list of (dimension, query) tuples.
    """
    print("\n" + "="*70)
    print("ORCHESTRATOR: Decomposing Research Task")
    print("="*70)

    client = anthropic.Anthropic()

    messages = [
        {
            "role": "user",
            "content": f"""You are an orchestrator for a research task.

User request: {user_input}

Decompose this into 3 independent research dimensions. Each dimension should:
1. Be independent (workers can research in parallel)
2. Have a specific, searchable query
3. Cover a distinct aspect of the comparison

Use the decompose_research tool to output your decomposition."""
        }
    ]

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=get_orchestrator_tools(),
        tool_choice="required",  # Force orchestrator to use the tool
        messages=messages
    )

    # Extract decomposition
    for block in response.content:
        if block.type == "tool_use":
            decomposition = block.input
            tasks = decomposition.get("research_tasks", [])
            print(f"\nOrchestrator decided on {len(tasks)} research dimensions:")
            for i, task in enumerate(tasks, 1):
                print(f"  {i}. {task['dimension']}: {task['query']}")
            return tasks

    return None


async def run_workers_parallel(tasks: list) -> list:
    """Run all workers in parallel using asyncio"""
    print("\n" + "="*70)
    print("WORKERS: Running Parallel Research")
    print("="*70)

    # Create worker coroutines
    worker_tasks = [
        run_worker(task["dimension"], task["query"], i+1)
        for i, task in enumerate(tasks)
    ]

    # Run all workers in parallel
    results = await asyncio.gather(*worker_tasks)
    return results


def run_aggregator(user_input: str, worker_results: list) -> str:
    """
    Aggregator reads worker results and writes final report.
    Does NOT search the web; only synthesizes.
    """
    print("\n" + "="*70)
    print("AGGREGATOR: Synthesizing Report")
    print("="*70)

    client = anthropic.Anthropic()

    # Format worker results for aggregator
    worker_summary = "\n\n".join([
        f"## {result['dimension']}\n{result['findings']}"
        for result in worker_results
    ])

    messages = [
        {
            "role": "user",
            "content": f"""You are a report synthesizer. The orchestrator decomposed the research into 3 dimensions.
Workers have completed their research. Now synthesize a comprehensive comparison report.

Original user request: {user_input}

Worker Research Results:
{worker_summary}

Write a professional comparison report (800-1000 words) that:
1. Synthesizes the worker findings
2. Highlights key tradeoffs
3. Provides a recommendation
4. Does NOT do additional research (just synthesize what workers found)"""
        }
    ]

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=messages
    )

    for block in response.content:
        if hasattr(block, "text"):
            return block.text

    return "Unable to generate report"


async def run_agent(user_input: str):
    """Run the complete orchestrator-workers system"""
    print("\n" + "#"*70)
    print("# TECH COMPARISON AGENT (Orchestrator-Workers)")
    print("#"*70)
    print(f"User: {user_input}\n")

    # Step 1: Orchestrator decomposes
    tasks = run_orchestrator(user_input)
    if not tasks:
        print("ERROR: Orchestrator failed to decompose task")
        return

    # Step 2: Workers research in parallel
    worker_results = await run_workers_parallel(tasks)

    # Step 3: Aggregator synthesizes
    report = run_aggregator(user_input, worker_results)

    # Output
    print("\n" + "#"*70)
    print("# FINAL REPORT")
    print("#"*70)
    print(report)
    print("\n" + "#"*70)


if __name__ == "__main__":
    user_input = "Compare PyTorch vs. TensorFlow for production machine learning."

    # Run the async orchestrator-workers system
    asyncio.run(run_agent(user_input))
