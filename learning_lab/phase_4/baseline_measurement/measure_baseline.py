#!/usr/bin/env python3
"""
Phase 4 Day 4: Baseline Measurement

Measure pre-optimization costs and latency for a representative workload.
This is the BEFORE snapshot. After Day 5 fixes, we'll re-measure for AFTER.

What we're measuring:
- Cost per call (will be inaccurate due to logger.py cache pricing bug)
- p50, p95, p99 latency
- Cache hit rate
- Cost by task type

20 requests across 3 task types:
- 8× image_recognition (ANALYZE_FOOD) — currently Haiku (wrong), should be Sonnet
- 7× json_extraction — currently Haiku (correct)
- 5× rag_answer — currently Sonnet (correct)

Usage:
    python measure_baseline.py > baseline_output.txt
    (then review output, run again to collect multiple samples)
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
# PRICING (For cost calculation — note: ignores cache pricing, will be fixed Day 5)
# ============================================================================

PRICING = {
    "haiku": {"input": 0.80, "output": 4.00},
    "sonnet": {"input": 3.00, "output": 15.00},
}


@dataclass
class CallMetrics:
    """Metrics for a single API call."""
    task_type: str
    model: str
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    latency_ms: float
    cost_usd: float
    cached: bool


def calculate_cost(model: str, usage) -> float:
    """Calculate USD cost from token usage (note: ignores cache pricing)."""
    if "sonnet" in model:
        model_key = "sonnet"
    elif "haiku" in model:
        model_key = "haiku"
    else:
        raise ValueError(f"Unknown model: {model}")

    pricing = PRICING[model_key]
    input_tokens = getattr(usage, "input_tokens", 0)
    output_tokens = getattr(usage, "output_tokens", 0)

    cost = (
        input_tokens * pricing["input"] / 1_000_000 +
        output_tokens * pricing["output"] / 1_000_000
    )

    return round(cost, 6)


# ============================================================================
# REPRESENTATIVE REQUESTS (20 across 3 task types)
# ============================================================================

REQUESTS = [
    # Task Type: image_recognition (8 requests) — currently Haiku, should be Sonnet
    {
        "name": "Food recognition 1: ramen bowl",
        "task_type": "image_recognition",
        "model": "claude-haiku-4-5-20251001",
        "user_message": "Analyze this food: a large bowl of ramen with pork belly, soft-boiled egg, bamboo shoots, nori, and miso broth.",
    },
    {
        "name": "Food recognition 2: caesar salad",
        "task_type": "image_recognition",
        "model": "claude-haiku-4-5-20251001",
        "user_message": "Analyze this food: grilled chicken Caesar salad with croutons, parmesan, and creamy dressing.",
    },
    {
        "name": "Food recognition 3: sushi platter",
        "task_type": "image_recognition",
        "model": "claude-haiku-4-5-20251001",
        "user_message": "Analyze this food: assorted nigiri sushi platter with salmon, tuna, yellowtail, cucumber, and wasabi.",
    },
    {
        "name": "Food recognition 4: pasta carbonara",
        "task_type": "image_recognition",
        "model": "claude-haiku-4-5-20251001",
        "user_message": "Analyze this food: creamy pasta carbonara with pancetta, egg yolk, pecorino cheese, and cracked black pepper.",
    },
    {
        "name": "Food recognition 5: avocado toast",
        "task_type": "image_recognition",
        "model": "claude-haiku-4-5-20251001",
        "user_message": "Analyze this food: whole grain toast with mashed avocado, lemon juice, sea salt, olive oil, and red pepper flakes.",
    },
    {
        "name": "Food recognition 6: thai curry",
        "task_type": "image_recognition",
        "model": "claude-haiku-4-5-20251001",
        "user_message": "Analyze this food: red thai curry with chicken, coconut milk, bamboo shoots, basil, and jasmine rice.",
    },
    {
        "name": "Food recognition 7: greek salad",
        "task_type": "image_recognition",
        "model": "claude-haiku-4-5-20251001",
        "user_message": "Analyze this food: greek salad with feta cheese, olives, tomatoes, cucumbers, red onion, and olive oil vinaigrette.",
    },
    {
        "name": "Food recognition 8: burger with fries",
        "task_type": "image_recognition",
        "model": "claude-haiku-4-5-20251001",
        "user_message": "Analyze this food: double cheeseburger with lettuce, tomato, onion, pickles, and a side of crispy french fries.",
    },

    # Task Type: json_extraction (7 requests) — currently Haiku (correct)
    {
        "name": "JSON extraction 1: simple protein",
        "task_type": "json_extraction",
        "model": "claude-haiku-4-5-20251001",
        "user_message": "Extract into JSON: grilled chicken breast, 165 kcal, 31g protein, 0g carbs, 3.6g fat.",
    },
    {
        "name": "JSON extraction 2: dessert",
        "task_type": "json_extraction",
        "model": "claude-haiku-4-5-20251001",
        "user_message": "Extract into JSON: chocolate cake slice, 450 kcal, 6g protein, 55g carbs, 22g fat.",
    },
    {
        "name": "JSON extraction 3: fruit",
        "task_type": "json_extraction",
        "model": "claude-haiku-4-5-20251001",
        "user_message": "Extract into JSON: one medium banana, 105 kcal, 1.3g protein, 27g carbs, 0.3g fat.",
    },
    {
        "name": "JSON extraction 4: vegetable",
        "task_type": "json_extraction",
        "model": "claude-haiku-4-5-20251001",
        "user_message": "Extract into JSON: steamed broccoli, 55 kcal per cup, 3.7g protein, 11g carbs, 0.6g fat.",
    },
    {
        "name": "JSON extraction 5: dairy",
        "task_type": "json_extraction",
        "model": "claude-haiku-4-5-20251001",
        "user_message": "Extract into JSON: greek yogurt 200g, 220 kcal, 20g protein, 10g carbs, 5g fat.",
    },
    {
        "name": "JSON extraction 6: nuts",
        "task_type": "json_extraction",
        "model": "claude-haiku-4-5-20251001",
        "user_message": "Extract into JSON: almonds handful (23 nuts), 164 kcal, 6g protein, 6g carbs, 14g fat.",
    },
    {
        "name": "JSON extraction 7: grain",
        "task_type": "json_extraction",
        "model": "claude-haiku-4-5-20251001",
        "user_message": "Extract into JSON: brown rice 1 cup cooked, 215 kcal, 5g protein, 45g carbs, 1.8g fat.",
    },

    # Task Type: rag_answer (5 requests) — currently Sonnet (correct)
    {
        "name": "RAG answer 1: salmon vs tilapia",
        "task_type": "rag_answer",
        "model": "claude-sonnet-4-20250514",
        "user_message": "Based on USDA nutrition database: is grilled salmon healthier than fried tilapia? Compare omega-3, mercury, and protein content.",
    },
    {
        "name": "RAG answer 2: whole wheat bread",
        "task_type": "rag_answer",
        "model": "claude-sonnet-4-20250514",
        "user_message": "From nutrition research: does whole wheat bread offer real benefits over white bread? Consider fiber, glycemic index, and micronutrients.",
    },
    {
        "name": "RAG answer 3: olive oil benefits",
        "task_type": "rag_answer",
        "model": "claude-sonnet-4-20250514",
        "user_message": "Based on Mediterranean diet studies: what are the science-backed health benefits of olive oil consumption?",
    },
    {
        "name": "RAG answer 4: protein timing",
        "task_type": "rag_answer",
        "model": "claude-sonnet-4-20250514",
        "user_message": "From exercise physiology research: does protein timing (immediately after workout) matter for muscle recovery?",
    },
    {
        "name": "RAG answer 5: intermittent fasting",
        "task_type": "rag_answer",
        "model": "claude-sonnet-4-20250514",
        "user_message": "Based on clinical studies: what are the actual metabolic effects of 16:8 intermittent fasting vs. traditional calorie restriction?",
    },
]


# ============================================================================
# MAIN MEASUREMENT
# ============================================================================

async def measure_baseline():
    print("\n" + "="*80)
    print("PHASE 4 DAY 4: BASELINE MEASUREMENT")
    print("="*80)
    print(f"Measuring {len(REQUESTS)} representative requests across 3 task types")
    print("(This is the BEFORE snapshot — will re-measure after Day 5 fixes)")
    print()

    metrics: List[CallMetrics] = []

    for i, request in enumerate(REQUESTS, 1):
        print(f"▶ Request {i}/{len(REQUESTS)}: {request['name']}")
        print(f"  Task: {request['task_type']:20} | Model: {request['model']}")

        start_time = time.time()

        try:
            response = await client.messages.create(
                model=request["model"],
                max_tokens=256,
                system=SYSTEM_PROMPTS.get(request["task_type"], ""),
                messages=[{"role": "user", "content": request["user_message"]}],
            )

            latency_ms = (time.time() - start_time) * 1000
            cost = calculate_cost(request["model"], response.usage)

            cached = getattr(response.usage, "cache_read_input_tokens", 0) > 0
            cache_read_tokens = getattr(response.usage, "cache_read_input_tokens", 0)

            metric = CallMetrics(
                task_type=request["task_type"],
                model=request["model"],
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                cache_read_tokens=cache_read_tokens,
                latency_ms=latency_ms,
                cost_usd=cost,
                cached=cached,
            )
            metrics.append(metric)

            cache_status = " [CACHED]" if cached else ""
            print(f"  Cost: ${cost:.6f} | Latency: {latency_ms:.0f}ms{cache_status}")
            print()

        except Exception as e:
            print(f"  ERROR: {e}")
            print()

    # ========================================================================
    # ANALYSIS
    # ========================================================================

    print("\n" + "="*80)
    print("BASELINE RESULTS")
    print("="*80)

    # By task type
    print("\nCOST & LATENCY BY TASK TYPE:")
    print("-" * 80)

    by_task = {}
    for metric in metrics:
        if metric.task_type not in by_task:
            by_task[metric.task_type] = []
        by_task[metric.task_type].append(metric)

    total_cost = 0
    all_latencies = []

    for task_type in sorted(by_task.keys()):
        task_metrics = by_task[task_type]
        count = len(task_metrics)
        avg_cost = sum(m.cost_usd for m in task_metrics) / count
        total_task_cost = sum(m.cost_usd for m in task_metrics)
        avg_latency = sum(m.latency_ms for m in task_metrics) / count
        cache_hits = sum(1 for m in task_metrics if m.cached)

        total_cost += total_task_cost
        all_latencies.extend([m.latency_ms for m in task_metrics])

        print(f"{task_type:20} | Count: {count:2} | Avg Cost: ${avg_cost:.6f} | Total: ${total_task_cost:.6f} | Avg Latency: {avg_latency:.0f}ms | Cached: {cache_hits}")

    print("-" * 80)
    avg_overall = total_cost / len(metrics) if metrics else 0
    print(f"{'TOTAL':20} | Count: {len(metrics):2} | Avg Cost: ${avg_overall:.6f} | Total: ${total_cost:.6f}")

    # Latency percentiles
    print("\nLATENCY PERCENTILES:")
    print("-" * 80)

    if all_latencies:
        sorted_latencies = sorted(all_latencies)

        def percentile(data, p):
            index = int(len(data) * (p / 100))
            return data[min(index, len(data) - 1)]

        p50 = percentile(sorted_latencies, 50)
        p95 = percentile(sorted_latencies, 95)
        p99 = percentile(sorted_latencies, 99)

        print(f"p50 (median): {p50:.0f}ms")
        print(f"p95:          {p95:.0f}ms (SLA target)")
        print(f"p99:          {p99:.0f}ms (long tail)")

    # Cost forecast
    print("\nCOST FORECAST (at current pricing):")
    print("-" * 80)

    daily_requests = 1000
    monthly_requests = daily_requests * 30

    daily_cost = daily_requests * avg_overall
    monthly_cost = monthly_requests * avg_overall

    print(f"Baseline: {len(metrics)} requests at ${total_cost:.6f} total")
    print(f"Average per request: ${avg_overall:.6f}")
    print(f"At {daily_requests:,} daily requests:")
    print(f"  Daily:   ${daily_cost:.2f}/day")
    print(f"  Monthly: ${monthly_cost:.2f}/month")

    # Cache hit rate
    print("\nCACHE HIT RATE:")
    print("-" * 80)

    cache_hits = sum(1 for m in metrics if m.cached)
    cache_hit_rate = (cache_hits / len(metrics) * 100) if metrics else 0

    print(f"Cache hits: {cache_hits}/{len(metrics)} ({cache_hit_rate:.1f}%)")
    print("(Expected: ~0% on first run, higher on repeated requests)")

    print("\n" + "="*80)
    print("END BASELINE MEASUREMENT")
    print("="*80)
    print("\nSave this output as baseline_report.md for Day 5 comparison.")
    print("After Day 5 fixes (Sonnet for ANALYZE_FOOD + cache pricing), re-run this script.")


if __name__ == "__main__":
    asyncio.run(measure_baseline())
