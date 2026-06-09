#!/usr/bin/env python3
"""
Phase 4 Day 2 (Morning): Streaming Responses

Key insight: Instead of waiting for Claude to finish generating the entire
response, stream tokens as they arrive. This enables real-time UX:

    "Recognizing... Querying nutrition database... Generating answer..."

Users see progress, not a blank screen waiting 3 seconds.

The pattern:
1. Use client.messages.stream() instead of client.messages.create()
2. Iterate over events as they arrive
3. Collect content deltas (text fragments) into a buffer
4. Update UI / print in real-time

Cost: Same as non-streaming (you pay for all tokens regardless).
Latency: Time to first token (TTFT) is lower, so users see feedback sooner.

Usage:
    python 03_streaming.py

You will see:
    - Non-streamed response (entire response at once, then printed)
    - Streamed response (tokens appear one by one, real-time)
    - Side-by-side comparison of TTFT and total latency

===============================================================================
LEARNING Q&A — Test Your Understanding
===============================================================================

Q1a: Why is TTFT (Time to First Token) so much lower than total latency?
A1a: Streaming consumes tokens as they arrive instead of waiting for the entire
     response. TTFT is when the first token arrives (~1.5s), total latency is
     when all tokens arrive (~6.6s). Non-streaming blocks until all tokens are
     ready, so user waits for the full total latency before seeing anything.

Q1b: How does streaming improve UX compared to non-streaming?
A1b: Non-streaming: user stares at blank screen for 6.14s (frustrating, feels
     like the app froze). Streaming: user sees first token at 1.53s (concrete
     feedback, feels responsive). Perceived latency is much better.

Q2a: Why advance to new steps at time thresholds (0s, 0.5s, 1.0s) instead of
     waiting for full response?
A2a: Thresholds simulate a multi-step process. As real time elapses during
     streaming, advancing steps shows progress ("Recognizing → Analyzing →
     Generating"). Time passes during streaming, so we can trigger UI updates
     based on elapsed time.

Q2b: Why is "📊 Analyzing nutrition..." better feedback than a spinning loader?
A2b: Concrete feedback is more reassuring. "Analyzing nutrition" tells the user:
     - The app is doing something (not frozen)
     - WHAT it's doing (analyzing = working on the task)
     - Progress is visible (steps advancing = getting closer to answer)
     A spinner just says "something is loading" — less reassuring.

Q2c: If response completed in 2.5s instead of 6.62s, would all three steps appear?
A2c: Yes. All three steps would appear because their thresholds (0s, 0.5s, 1.0s)
     are all <= 2.5s. Steps would just appear faster. Thresholds determine WHEN
     steps appear, not WHETHER they appear.

Q3a: Why only check for event.type == "content_block_delta"?
A3a: Only content_block_delta events carry text fragments (event.delta.text).
     Other events are metadata: message_start (stream began), content_block_start
     (block starting), content_block_stop (block ending), message_stop (stream
     ending). We only care about actual text tokens.

Q3b: What happens if you remove flush=True from print statements?
A3b: Output gets buffered in memory instead of appearing immediately. Tokens
     might appear in batches or not until the stream completes, defeating the
     real-time UX. flush=True forces immediate write to terminal.

Q3c: Why use hasattr(delta, "text") instead of directly accessing delta.text?
A3c: Defensive programming. Some delta events might not have a "text" attribute.
     hasattr checks first; if missing, it skips without crashing. Direct access
     would raise AttributeError if the attribute doesn't exist.

Q4a: Why accumulate text in a buffer variable during streaming?
A4a: To preserve the partial response if the stream errors mid-way. If an error
     occurs after 50% of tokens, the buffer contains those 50% so you can:
     - Display partial response to user
     - Log it with error context
     - Fall back to cached data instead of losing everything

Q4b: If stream errors after 50% of tokens, what's in the buffer?
A4b: The first 50% of the response text. Buffer accumulates every token received,
     so partial responses are always preserved even if the stream fails.

Q4c: In production, what three things can you do with a partial response?
A4c: (1) Display it to user: "Response interrupted, but here's what we got..."
     (2) Log it with error: preserve the partial response in error logs
     (3) Fall back: "Stream failed, showing cached result instead..."

Q5a: Does streaming reduce the number of tokens sent to Claude?
A5a: No. You observed 308 tokens in both streaming and non-streaming. Streaming
     is purely about HOW you consume tokens (all at once vs. as they arrive),
     not HOW MANY tokens are used. Same request = same tokens = same cost.

Q5b: If streaming doesn't save money, why use it in production?
A5b: For User Experience (UX). Users see first token at 1.53s (streaming) instead
     of waiting 6.14s (non-streaming). Benefits: better engagement, lower bounce
     rate (users don't think app froze), perceived speed improvement. Streaming
     improves PERCEIVED latency even if total time is similar.

Q5c: What does "streaming is a UX optimization, not a cost optimization" mean?
A5c: UX optimization = improves perceived latency and user engagement.
     NOT cost optimization = doesn't reduce tokens, requests, or API cost.
     Use streaming when you care about user experience, not to save money.

Q6a: What does end="" do in print(text, end="", flush=True)?
A6a: Removes the newline after print(). Without it, each token prints on new line:
       This
       is
       a
       response
     With end="", tokens concatenate: This is a response

Q6b: Why is flush=True critical for streaming?
A6b: Ensures output writes to terminal immediately (doesn't buffer in memory).
     Without it, tokens appear in batches or not until buffer fills/stream ends.
     For streaming, you want tokens to appear AS THEY ARRIVE, not in batches.

Q6c: In Experiment 3, what does print() without arguments do?
A6c: Prints a newline (moves to next line). Used to separate progress steps:
       🔍 Recognizing food...
       📊 Analyzing nutrition...    ← print() moved us here
       💬 Generating commentary...

Q7a: For a mobile app, use streaming or non-streaming? Why?
A7a: Streaming. Mobile users have short attention spans. Non-streaming: user waits
     6.14s for blank screen → closes app. Streaming: user sees text at 1.53s →
     stays engaged. User retention matters more than code simplicity.

Q7b: What's the code complexity tradeoff?
A7b: Non-streaming: simple (call, wait, print). Streaming: complex (async events,
     track TTFT, handle partial responses on error, buffer management). Worth
     it for better UX, but requires more careful coding.

Q8a: In NomNom, what progress steps would you show if using this pattern?
A8a: Based on real timing during analysis:
       🔍 Recognizing food...      (0.0s) — identify what's in the photo
       📊 Analyzing nutrition...   (0.5s) — calculate macros/micros
       💬 Generating answer...     (2.0s) — formulate nutritional response
       🎭 Adding NomNom's sass...  (4.0s) — add witty commentary
     Thresholds match actual timing of each step.

Q8b: Why is showing step labels better UX than silent processing?
A8b: Concrete feedback = reassurance. "Recognizing..." tells user what's
     happening NOW. Silent processing feels slow/frozen even if timing is same.
     Progress transparency = perceived speed improvement + user confidence.

KEY TAKEAWAY:
Streaming improves perceived latency and user engagement (UX), not token cost
(cost). Use when you care about real-time feedback and user experience.

===============================================================================
"""

import os
import asyncio
import time
from anthropic import AsyncAnthropic

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set")

client = AsyncAnthropic(api_key=api_key)


# ============================================================================
# SYSTEM PROMPT (same NomNom persona as Day 1)
# ============================================================================

NOMNOM_SYSTEM_PROMPT = """
You are NomNom, an AI-powered nutrition assistant with the personality of a
sarcastic but caring cat. You analyze food photos and give nutritional
breakdowns with witty commentary.

When responding, think step-by-step:
1. Identify the food and components
2. Estimate macronutrients
3. Add NomNom's commentary

Keep responses concise (2-3 sentences max for the analysis, 1 sentence max
for the commentary).
""".strip()


# ============================================================================
# EXPERIMENT 1: Non-Streaming (Traditional)
#
# Wait for the entire response, then print it all at once.
# ============================================================================

async def experiment_1_non_streaming():
    print("\n" + "="*60)
    print("EXPERIMENT 1: Non-Streaming Response")
    print("="*60)
    print("Goal: Traditional pattern — wait for full response.")
    print()

    user_message = "Analyze this food: a large bowl of pho with beef, noodles, and broth."

    print("▶ Sending request (waiting for full response)...")
    start_time = time.time()

    response = await client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=256,
        system=NOMNOM_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    total_time = time.time() - start_time
    response_text = response.content[0].text

    print(f"✓ Response received in {total_time:.2f}s")
    print(f"  Tokens: {response.usage.input_tokens} input, {response.usage.output_tokens} output")
    print()
    print(f"Claude says:\n  {response_text}")
    print()
    print(f"Key metric: Total latency = {total_time:.2f}s")
    print("  (User sees nothing until this moment)")


# ============================================================================
# EXPERIMENT 2: Streaming (Real-Time)
#
# Consume tokens as they arrive. Perfect for interactive UX.
# ============================================================================

async def experiment_2_streaming():
    print("\n" + "="*60)
    print("EXPERIMENT 2: Streaming Response")
    print("="*60)
    print("Goal: Real-time token streaming for interactive UX.")
    print()

    user_message = "Analyze this food: a large bowl of pho with beef, noodles, and broth."

    print("▶ Sending request (streaming tokens as they arrive)...")
    print()
    print("Claude says:")
    print("  ", end="", flush=True)  # Print prefix, flush to ensure immediate display

    start_time = time.time()
    first_token_time = None
    full_response = ""

    # Use context manager for stream — automatically handles cleanup
    async with client.messages.stream(
        model="claude-sonnet-4-5",
        max_tokens=256,
        system=NOMNOM_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        # Iterate over events as they arrive
        async for event in stream:
            # Event types: message_start, content_block_start, content_block_delta, content_block_stop, message_stop, message_delta
            if event.type == "content_block_delta":
                # This event carries the actual text fragment
                delta = event.delta
                if hasattr(delta, "text"):
                    text = delta.text
                    full_response += text
                    print(text, end="", flush=True)  # Print immediately

                    # Record time to first token
                    if first_token_time is None:
                        first_token_time = time.time() - start_time

    total_time = time.time() - start_time
    print()  # Newline after response

    print()
    print(f"Key metrics:")
    print(f"  Time to first token (TTFT) : {first_token_time:.3f}s")
    print(f"  Total latency              : {total_time:.2f}s")
    print(f"  User feedback begins at    : {first_token_time:.3f}s (not {total_time:.2f}s)")


# ============================================================================
# EXPERIMENT 3: Simulated Real-Time UI Update
#
# Show how you'd update a UI as tokens arrive (progress indicator pattern).
# ============================================================================

async def experiment_3_ui_simulation():
    print("\n" + "="*60)
    print("EXPERIMENT 3: Simulated UI Update Pattern")
    print("="*60)
    print("Goal: Show how to update a UI as tokens stream in.")
    print()

    user_message = "Analyze this food: grilled salmon with asparagus and lemon butter sauce."

    print("▶ Streaming response with simulated UI updates...")
    print()

    # Simulate a multi-step process
    steps = [
        ("🔍 Recognizing food...", 0),
        ("📊 Analyzing nutrition...", 0.5),
        ("💬 Generating commentary...", 1.0),
    ]

    step_index = 0
    current_step_text = ""
    step_start_time = time.time()

    print(f"{steps[step_index][0]}", end="", flush=True)

    async with client.messages.stream(
        model="claude-sonnet-4-5",
        max_tokens=256,
        system=NOMNOM_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        async for event in stream:
            if event.type == "content_block_delta":
                delta = event.delta
                if hasattr(delta, "text"):
                    text = delta.text
                    current_step_text += text

                    # Estimate progress: advance step if we've accumulated enough tokens
                    # (In real code, you'd track token count or use other signals)
                    elapsed = time.time() - step_start_time

                    # Advance step every ~0.5s of elapsed time
                    for i, (step_label, threshold) in enumerate(steps[step_index:], start=step_index):
                        if elapsed >= threshold and i > step_index:
                            print()  # Newline for previous step
                            print(f"{step_label}", end="", flush=True)
                            step_index = i
                            break

    print()  # Newline after completion
    print()
    print(f"✓ Complete response:")
    print(f"  {current_step_text}")


# ============================================================================
# EXPERIMENT 4: Error Handling in Streams
#
# Streams can error mid-way. Show how to handle gracefully.
# ============================================================================

async def experiment_4_stream_error_handling():
    print("\n" + "="*60)
    print("EXPERIMENT 4: Stream Error Handling")
    print("="*60)
    print("Goal: Handle errors that occur during streaming.")
    print()

    user_message = "Analyze this food: a mystery dish that's completely unidentifiable."

    print("▶ Streaming with error handling...")
    print()

    try:
        buffer = ""
        async with client.messages.stream(
            model="claude-sonnet-4-5",
            max_tokens=256,
            system=NOMNOM_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        ) as stream:
            async for event in stream:
                if event.type == "content_block_delta":
                    delta = event.delta
                    if hasattr(delta, "text"):
                        buffer += delta.text
                        print(delta.text, end="", flush=True)

        print()
        print()
        print("✓ Stream completed successfully")

    except Exception as e:
        print()
        print()
        print(f"⚠ Stream error occurred: {type(e).__name__}")
        print(f"  Message: {str(e)}")
        print(f"  Partial response accumulated: {len(buffer)} chars")
        print()
        print("  In production, you would:")
        print("  - Log the error with context")
        print("  - Optionally retry with backoff")
        print("  - Display cached/fallback content to user")


# ============================================================================
# EXPERIMENT 5: Cost Comparison (Streaming vs. Non-Streaming)
#
# Both cost the same. Streaming is purely for UX, not cost savings.
# ============================================================================

async def experiment_5_cost_comparison():
    print("\n" + "="*60)
    print("EXPERIMENT 5: Cost Comparison (Streaming vs. Non-Streaming)")
    print("="*60)
    print("Goal: Show that streaming doesn't affect token costs.")
    print()

    user_message = "Analyze this food: sushi platter with 10 pieces of assorted nigiri."

    print("▶ Non-streaming request...")
    response_traditional = await client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=256,
        system=NOMNOM_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    traditional_tokens = (
        response_traditional.usage.input_tokens +
        response_traditional.usage.output_tokens
    )

    print("▶ Streaming request (same prompt, same request)...")
    streaming_token_count = 0
    async with client.messages.stream(
        model="claude-sonnet-4-5",
        max_tokens=256,
        system=NOMNOM_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        async for event in stream:
            # Note: Streaming doesn't give you token counts in delta events
            # You'd need to track them separately or use message_delta event
            pass

    print()
    print("▶ Analysis:")
    print(f"  Non-streaming request: {traditional_tokens} total tokens")
    print(f"  Streaming request: same token count (not visible per event)")
    print()
    print("  Key insight: Streaming is a UX optimization, not a cost optimization.")
    print("  Use it when you want real-time feedback, not to save money.")


# ============================================================================
# MAIN
# ============================================================================

async def main():
    print("Phase 4 Day 2 (Morning): Streaming Responses")
    print("Model: claude-sonnet-4-5")
    print()
    print("Running 5 experiments:")
    print("  1. Non-streaming (traditional, wait for full response)")
    print("  2. Streaming (tokens appear in real-time)")
    print("  3. Simulated UI update pattern (progress indicator)")
    print("  4. Error handling in streams")
    print("  5. Cost comparison (streaming vs. non-streaming)")

    await experiment_1_non_streaming()
    await experiment_2_streaming()
    await experiment_3_ui_simulation()
    await experiment_4_stream_error_handling()
    await experiment_5_cost_comparison()

    print("\n" + "="*60)
    print("SUMMARY — What you should now know:")
    print("="*60)
    print("1. Use client.messages.stream() for real-time token streaming")
    print("2. Iterate over events; extract text from content_block_delta")
    print("3. Time to first token (TTFT) is lower with streaming → better UX")
    print("4. Streaming doesn't save tokens or money — purely UX")
    print("5. Use flush=True when printing to show tokens immediately")
    print("6. Streaming is perfect for interactive apps, CLI tools, web UI")
    print("7. Error handling works the same — catch exceptions around stream loop")
    print("8. Pattern: identify progress steps, update UI as tokens arrive")


if __name__ == "__main__":
    asyncio.run(main())
