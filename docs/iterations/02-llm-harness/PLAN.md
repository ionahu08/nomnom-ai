# Iteration 02 — LLM Harness Engineering (Phase 3)

## Goal

Build a production-grade LLM harness with retry logic, fallback models, structured output, and prompt templates — before wiring it to the API.

## What's Built

- Basic AI photo analysis via Haiku (no harness, raw calls)
- iOS camera + food logging working end-to-end
- All backend food log CRUD endpoints

## What We're Building

**In Plain English:**

Right now your app calls Claude and hopes it works. If Claude is slow or breaks, your app crashes.

An **LLM Harness** is a safety net that wraps around Claude and makes it reliable:

1. **Retry Logic** — If Claude fails, try again automatically (up to 2 times)
2. **Fallback Model** — If Haiku keeps failing, use Sonnet (smarter, more reliable) instead
3. **Structured Output** — Force Claude to return JSON in the exact shape you need (not random text)
4. **Validation** — Check the response is actually good (e.g., calories aren't 50,000), and auto-retry if it's garbage
5. **Prompt Templates** — Store prompts in files (not hardcoded in Python) so you can change them without editing code
6. **Timeouts** — Don't wait forever for Claude to respond (10s max for Haiku, 30s for Sonnet)
7. **Token Budget** — Don't spend too much money on one call (cap max_tokens)

**Result:** Your app is 10x more reliable and doesn't crash when Claude has a bad day.

## Resume Skills Demonstrated

- LLM Harness Engineering
- Structured Output (tool_use)
- Prompt Engineering (Jinja2 templates)
- Error handling & fallbacks
- Async Python

## Success Criteria

- [x] LLMClient wraps Anthropic with retry, timeout, fallback
- [x] Router maps tasks to correct models (Haiku vs Sonnet)
- [x] Jinja2 templates render with cat personas
- [x] Tool definitions enforce structured output schema
- [x] Parser validates output, retries on failure
- [x] All unit tests pass
- [x] No direct Anthropic calls anywhere else — all go through LLMClient
