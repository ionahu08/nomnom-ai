#!/usr/bin/env python3
"""
Phase 4 Day 2 (Afternoon): Cost & Latency Tracking

Key insight: Every API call has a cost (tokens) and latency (time).
To optimize, you must measure both per task type, per model, per user.

The pattern:
1. Log every API call: tokens, latency, model, task_type, cost_usd
2. Aggregate by task type and time window (hourly, daily, weekly)
3. Identify where you're spending money (which task? which model?)
4. Find optimization opportunities (can we downgrade the model? cache more?)

Cost tracking enables:
- Budget forecasting ("we'll spend $X/month at current usage")
- Anomaly detection ("task X usually costs $0.05, why is it $2 today?")
- Model tiering validation ("is Sonnet really worth the cost here?")
- Cache effectiveness ("we save $X/day with prompt caching")

Usage:
    python 04_cost_tracking.py

You will see:
    - 5 representative NomNom requests (image, JSON, RAG, etc.)
    - Cost breakdown per request
    - Aggregated cost per task type
    - Latency stats (p50, p95)
"""

import os
import asyncio
import time
import json
from dataclasses import dataclass, asdict
from typing import List
from anthropic import AsyncAnthropic

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set")

client = AsyncAnthropic(api_key=api_key)


# ============================================================================
# SYSTEM PROMPTS (Task-Specific)
# ============================================================================

SYSTEM_PROMPTS = {
    "image_recognition": """
You are a food recognition expert. Analyze the food description and identify:
- Food name
- Portion size estimate
- Primary ingredients
- Confidence level (HIGH/MEDIUM/LOW)

Be concise, factual.
""".strip(),

    "json_extraction": """
You are a data extraction specialist. Parse the food description into JSON.
Return ONLY valid JSON, no explanation.
""".strip(),

    "rag_answer": """
You are a nutrition expert. Answer the question using the retrieved knowledge base context.
Cite sources when relevant.
""".strip(),
}


# ============================================================================
# PRICING & COST CALCULATION
# ============================================================================

PRICING = {
    "haiku": {
        "input": 0.80,
        "output": 4.00,
        "cache_creation": 1.00,
        "cache_read": 0.08,
    },
    "sonnet": {
        "input": 3.00,
        "output": 15.00,
        "cache_creation": 3.75,
        "cache_read": 0.30,
    },
    "opus": {
        "input": 15.00,
        "output": 75.00,
        "cache_creation": 18.75,
        "cache_read": 1.50,
    },
}


@dataclass
class CallMetrics:
    """Metrics for a single API call."""
    task_type: str
    model: str
    input_tokens: int
    output_tokens: int
    cache_creation_tokens: int
    cache_read_tokens: int
    latency_ms: float
    cost_usd: float
    cached: bool  # Was this request served from cache?

    def to_dict(self):
        return asdict(self)


def calculate_cost(model: str, usage) -> float:
    """Calculate USD cost from token usage."""
    if model not in PRICING:
        raise ValueError(f"Unknown model: {model}")

    pricing = PRICING[model]

    input_tokens = getattr(usage, "input_tokens", 0)
    output_tokens = getattr(usage, "output_tokens", 0)
    cache_creation = getattr(usage, "cache_creation_input_tokens", 0)
    cache_read = getattr(usage, "cache_read_input_tokens", 0)

    cost = (
        input_tokens * pricing["input"] / 1_000_000 +
        output_tokens * pricing["output"] / 1_000_000 +
        cache_creation * pricing["cache_creation"] / 1_000_000 +
        cache_read * pricing["cache_read"] / 1_000_000
    )

    return round(cost, 6)


# ============================================================================
# REPRESENTATIVE NOMNOM REQUESTS (Baseline Measurement)
# ============================================================================

REQUESTS = [
    {
        "name": "Food Image Recognition",
        "task_type": "image_recognition",
        "model": "claude-sonnet-4-5",
        "user_message": "Analyze this food: a large bowl of ramen with pork belly, soft-boiled egg, bamboo shoots, nori, and miso broth.",
    },
    {
        "name": "JSON Extraction (Simple)",
        "task_type": "json_extraction",
        "model": "claude-haiku-4-5",  # Cheaper for simple extraction
        "user_message": "Extract the food name, calories, protein, carbs, fat from: Grilled chicken Caesar salad with croutons and parmesan, 450 kcal, 35g protein, 25g carbs, 18g fat.",
    },
    {
        "name": "Nutrition RAG Answer",
        "task_type": "rag_answer",
        "model": "claude-sonnet-4-5",  # Needs reasoning for synthesis
        "user_message": "Based on the USDA database: is grilled salmon healthier than fried tilapia? Explain the nutritional differences.",
    },
    {
        "name": "Complex Dietary Advice",
        "task_type": "complex_advice",
        "model": "claude-opus-4-7",  # High-stakes, needs depth
        "user_message": "I'm allergic to nuts and dairy. Suggest 3 high-protein, low-carb meals for the week that are safe for my allergies.",
    },
    {
        "name": "Test Dataset Generation",
        "task_type": "dataset_generation",
        "model": "claude-haiku-4-5",  # Fast, cheap, batch work
        "user_message": "Generate 5 diverse, challenging food descriptions for eval: include ambiguous items, mixed dishes, unusual angles.",
    },
]


# ============================================================================
# EXPERIMENT 1: Individual Request Cost Tracking
# ============================================================================

async def experiment_1_individual_costs():
    print("\n" + "="*60)
    print("EXPERIMENT 1: Individual Request Cost Tracking")
    print("="*60)
    print("Goal: Track cost and latency for 5 representative requests.")
    print()

    metrics: List[CallMetrics] = []

    for i, request in enumerate(REQUESTS, 1):
        print(f"▶ Request {i}: {request['name']}")
        print(f"  Model: {request['model']}")
        print(f"  Task: {request['task_type']}")

        start_time = time.time()

        response = await client.messages.create(
            model=request["model"],
            max_tokens=256,
            system=SYSTEM_PROMPTS.get(request["task_type"], ""),
            messages=[{"role": "user", "content": request["user_message"]}],
        )

        latency_ms = (time.time() - start_time) * 1000
        cost = calculate_cost(request["model"], response.usage)

        # Determine if cached (cache_read_tokens > 0)
        cached = getattr(response.usage, "cache_read_input_tokens", 0) > 0

        metric = CallMetrics(
            task_type=request["task_type"],
            model=request["model"],
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            cache_creation_tokens=getattr(response.usage, "cache_creation_input_tokens", 0),
            cache_read_tokens=getattr(response.usage, "cache_read_input_tokens", 0),
            latency_ms=latency_ms,
            cost_usd=cost,
            cached=cached,
        )
        metrics.append(metric)

        cache_status = " (CACHED)" if cached else ""
        print(f"  Cost: ${cost:.6f}")
        print(f"  Latency: {latency_ms:.0f}ms")
        print(f"  Tokens: {response.usage.input_tokens} input, {response.usage.output_tokens} output{cache_status}")
        print()

    return metrics


# ============================================================================
# EXPERIMENT 2: Cost Aggregation by Task Type
# ============================================================================

def experiment_2_aggregation(metrics: List[CallMetrics]):
    print("\n" + "="*60)
    print("EXPERIMENT 2: Cost Aggregation by Task Type")
    print("="*60)
    print("Goal: Summarize costs and latency per task type.")
    print()

    # Group by task type
    by_task = {}
    for metric in metrics:
        if metric.task_type not in by_task:
            by_task[metric.task_type] = []
        by_task[metric.task_type].append(metric)

    print(f"{'Task Type':<25} | {'Count':<6} | {'Avg Cost':<12} | {'Total Cost':<12} | {'Avg Latency':<12}")
    print("-" * 80)

    total_cost = 0
    total_latency = 0

    for task_type, task_metrics in sorted(by_task.items()):
        count = len(task_metrics)
        avg_cost = sum(m.cost_usd for m in task_metrics) / count
        total_task_cost = sum(m.cost_usd for m in task_metrics)
        avg_latency = sum(m.latency_ms for m in task_metrics) / count

        total_cost += total_task_cost
        total_latency += avg_latency

        print(f"{task_type:<25} | {count:<6} | ${avg_cost:<11.6f} | ${total_task_cost:<11.6f} | {avg_latency:<11.0f}ms")

    print("-" * 80)
    print(f"{'TOTAL':<25} | {len(metrics):<6} | ${total_cost/len(metrics):<11.6f} | ${total_cost:<11.6f} | {total_latency/len(metrics):<11.0f}ms")
    print()


# ============================================================================
# EXPERIMENT 3: Latency Percentiles (p50, p95, p99)
# ============================================================================

def experiment_3_latency_percentiles(metrics: List[CallMetrics]):
    print("\n" + "="*60)
    print("EXPERIMENT 3: Latency Percentiles")
    print("="*60)
    print("Goal: Understand latency distribution (p50, p95, p99).")
    print()

    latencies = sorted([m.latency_ms for m in metrics])

    def percentile(data, p):
        index = int(len(data) * (p / 100))
        return data[min(index, len(data) - 1)]

    p50 = percentile(latencies, 50)
    p95 = percentile(latencies, 95)
    p99 = percentile(latencies, 99)

    print(f"Latency Distribution (n={len(metrics)} requests):")
    print(f"  p50 (median)    : {p50:.0f}ms")
    print(f"  p95             : {p95:.0f}ms")
    print(f"  p99             : {p99:.0f}ms")
    print()
    print("Interpretation:")
    print(f"  - 50% of requests finish in ≤ {p50:.0f}ms")
    print(f"  - 95% of requests finish in ≤ {p95:.0f}ms (SLA target)")
    print(f"  - 99% of requests finish in ≤ {p99:.0f}ms (long tail)")


# ============================================================================
# EXPERIMENT 4: Cost Forecast (Daily, Monthly)
# ============================================================================

def experiment_4_cost_forecast(metrics: List[CallMetrics]):
    print("\n" + "="*60)
    print("EXPERIMENT 4: Cost Forecast (Daily & Monthly)")
    print("="*60)
    print("Goal: Extrapolate baseline costs to daily/monthly projections.")
    print()

    # Assumptions
    daily_requests = 1000  # Expected daily food photo requests
    monthly_requests = daily_requests * 30

    # Average cost per request from baseline
    avg_cost_per_request = sum(m.cost_usd for m in metrics) / len(metrics)

    daily_cost = daily_requests * avg_cost_per_request
    monthly_cost = monthly_requests * avg_cost_per_request

    print(f"Assumptions:")
    print(f"  - Baseline: {len(metrics)} requests at ${sum(m.cost_usd for m in metrics):.6f} total")
    print(f"  - Average per request: ${avg_cost_per_request:.6f}")
    print(f"  - Projected daily usage: {daily_requests:,} requests")
    print()
    print(f"Forecast:")
    print(f"  Daily  : {daily_requests:,} requests × ${avg_cost_per_request:.6f} = ${daily_cost:.2f}/day")
    print(f"  Monthly: {monthly_requests:,} requests × ${avg_cost_per_request:.6f} = ${monthly_cost:.2f}/month")
    print()
    print("Optimization Impact:")
    print(f"  - Prompt caching: save ~$X/day (cache 90% of system prompt)")
    print(f"  - Model downgrade (Sonnet→Haiku for simple tasks): save ~$Y/day")
    print(f"  - Streaming (faster TTFT, less user re-submissions): save ~$Z/day")


# ============================================================================
# EXPERIMENT 5: Cache Effectiveness Simulation
# ============================================================================

async def experiment_5_cache_simulation():
    print("\n" + "="*60)
    print("EXPERIMENT 5: Cache Effectiveness Simulation")
    print("="*60)
    print("Goal: Show cost savings from prompt caching.")
    print()

    # Simulate 10 identical requests (cache HIT pattern)
    print("Scenario: 10 identical food photo requests (same system prompt + tool)")
    print()

    cached_costs = []

    for i in range(10):
        # Simplified: assume after request 1, all others are cache HIT
        # (In reality, you'd need to track cache_read_input_tokens from the API)
        if i == 0:
            # First request: pays full cache_creation premium
            cost = 0.006  # Approx cost for ~2000 token system + tools
            status = "MISS"
        else:
            # Subsequent: pays cache_read discount (~90% cheaper)
            cost = 0.0006
            status = "HIT"

        cached_costs.append(cost)
        print(f"  Request {i+1:2d}: ${cost:.6f} ({status})")

    print()
    print(f"Total cost (with caching): ${sum(cached_costs):.6f}")

    # Compare to non-cached
    non_cached = sum([0.006] * 10)
    print(f"Total cost (no caching)   : ${non_cached:.6f}")
    print(f"Savings from caching      : ${non_cached - sum(cached_costs):.6f} ({(1 - sum(cached_costs)/non_cached)*100:.1f}%)")
    print()
    print(f"At 1000 daily requests:")
    print(f"  - With caching  : ~${(sum(cached_costs) / 10) * 1000:.2f}/day")
    print(f"  - No caching    : ${non_cached / 10 * 1000:.2f}/day")
    print(f"  - Daily savings : ${(non_cached - sum(cached_costs)) / 10 * 1000:.2f}")


# ============================================================================
# MAIN
# ============================================================================

async def main():
    print("Phase 4 Day 2 (Afternoon): Cost & Latency Tracking")
    print("Model: Haiku, Sonnet, Opus")
    print()
    print("Running 5 experiments:")
    print("  1. Individual request cost tracking (5 representatives)")
    print("  2. Aggregation by task type (average, total)")
    print("  3. Latency percentiles (p50, p95, p99)")
    print("  4. Cost forecast (daily, monthly projections)")
    print("  5. Cache effectiveness simulation")

    # Run experiments
    metrics = await experiment_1_individual_costs()
    experiment_2_aggregation(metrics)
    experiment_3_latency_percentiles(metrics)
    experiment_4_cost_forecast(metrics)
    await experiment_5_cache_simulation()

    print("\n" + "="*60)
    print("SUMMARY — What you should now know:")
    print("="*60)
    print("1. Log every API call: tokens, latency, model, task_type, cost")
    print("2. Calculate cost per call: (tokens × price/1M)")
    print("3. Aggregate per task type to find spending patterns")
    print("4. Track latency percentiles (p50, p95, p99) for SLA monitoring")
    print("5. Forecast daily/monthly costs from baseline")
    print("6. Cache can save 80-90% on repeated system prompts")
    print("7. Model tiering (Haiku vs Sonnet) can save 3-5x on simple tasks")
    print("8. Cost + Latency together tell the optimization story")
    print("9. Store metrics in a database for historical analysis")
    print("10. Use this data to make model/cache/streaming decisions")


if __name__ == "__main__":
    asyncio.run(main())
