# Iteration 03 — Guardrails, Observability & Cost Optimization (Phase 5)

## Goal

Add safety guardrails, semantic caching, AI call logging, rate limiting, and accuracy tracking.

## What's Built

- LLM harness with retry, fallback, structured output
- Food photo analysis via Haiku (via harness)
- iOS camera + food logging

## What We're Building

**Five problems being solved:**

1. **No safety checks** — Claude might return garbage (calories = 50,000)
2. **No cost optimization** — Pay twice for same pizza photo analysis
3. **No visibility** — Don't know how much money you're spending on API calls
4. **No abuse protection** — Users could spam camera button 1000 times and waste budget
5. **No learning** — Don't track when Claude gets food wrong

**Solutions:**
- **Guardrails:** Validate output (calories 0-5000, realistic macros)
- **Semantic cache:** If similar photo seen before, reuse cached result (save money!)
- **AI call logging:** Log every call (model, tokens, latency, cost)
- **Rate limiting:** Block users who exceed limits (30/hour for analyze)
- **Accuracy tracking:** Track user corrections to measure Claude performance

## Resume Skills Demonstrated

- Guardrails
- Cost Optimization
- AI Observability
- Model Evaluation
- Database design

## Success Criteria

- [x] Guardrails validate all AI output
- [x] Semantic cache prevents redundant API calls
- [x] Every AI call logged with metadata
- [x] Rate limiting blocks abusive users
- [x] Accuracy tracking measures Claude's performance
- [x] AI stats endpoints expose metrics
- [x] All tests pass
