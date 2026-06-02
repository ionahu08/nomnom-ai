# Code Review: `src/llm/client.py`

## What This File Does

This module wraps the Anthropic API to make LLM calls reliable by adding retry logic, timeout enforcement, and fallback to a secondary model. It takes a model name, messages, and system prompt, then returns a Claude response or raises an error after exhausting all retry attempts.

## Before and After: The Problem It Solves

**Without `client.py` (naive approach):**
```python
client = anthropic.AsyncAnthropic(api_key=api_key)
response = await client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[...]
)
```

Problems:
- If the API call times out or fails, the entire request fails (no retry)
- No timeout enforcement → app could hang forever
- No fallback model → one slow model brings everything down
- Hardcoded model and token limits → can't tune per model

**With `client.py` (improved approach):**
```python
llm_client = LLMClient(api_key=api_key)
response = await llm_client.create_message_with_retry(
    model="claude-sonnet-4-20250514",
    messages=[...],
    fallback_model="claude-haiku-4-5-20251001"
)
```

Improvements:
- Automatic retry with exponential backoff (catches transient failures)
- Timeout enforcement (20s for Haiku, 30s for Sonnet)
- Fallback model (if Sonnet fails, try Haiku)
- Per-model configuration (different timeouts and token limits)
- Structured logging (track token usage, retry attempts)

## Design Choices I Can Defend

### Why 2 retries, not 3 or 5?

This is a latency vs. reliability tradeoff. Each retry adds 1s + 2s = 3s minimum wait before fallback. If you do 5 retries, that's 15+ seconds of waiting. For a user taking a food photo, they'd abandon the app.

2 retries catches transient issues (network blip, brief API overload) without being too stubborn. If Claude is down or rate-limited, you want to fall back fast.

**Philosophy:** Retry quickly to catch blips, but don't waste time if it's a real problem.

### Why exponential backoff (1s → 2s)?

Standard pattern to avoid "thundering herd" — if 1000 clients all retry at the same second, they hammer the server at once. Exponential spread is gentler.

But 1s → 2s is very short. This assumes: if Claude recovers, it'll be quick. If not, waiting longer won't help.

**Philosophy:** Optimized for user-facing latency, not for "be maximally gentle to the API."

### Why recursive fallback, not a loop?

Simpler code: reuses the entire retry logic instead of refactoring it into a separate function. You only fallback once (fallback_model doesn't have its own fallback), so recursion doesn't spiral.

**Tradeoff:** Another stack frame, but negligible for one fallback.

### Why `MODEL_CONFIG` per model?

Different models have different characteristics:
- Haiku is fast & cheap → short timeout (20s), fewer tokens (400)
- Sonnet is slower & more capable → longer timeout (30s), more tokens (2000)

This design is future-proof: when Claude 5 ships, just add it to the dict instead of hardcoding timeouts everywhere.

**Philosophy:** Tune behavior by model capability, not one-size-fits-all.

### What happens if both primary and fallback fail?

The method raises `last_error` (whatever the last exception was). If fallback is tried, the fallback's error gets raised, not the primary's.

**Reasoning:** The most recent error is usually most relevant for debugging.

## Design Choices I Still Don't Understand

- Would jitter on the exponential backoff help? (Currently 1s → 2s is deterministic; adding randomness would spread retries even more, but the code doesn't do this.)
- Is there a risk of stack overflow if someone passes a fallback_model that itself has a fallback? (The code assumes fallback_model is a terminal model, but there's no guard against a circular reference.)

## Things I Would Change

None yet. The design feels well-reasoned for the constraints (user-facing latency, simple code, per-model tuning).
