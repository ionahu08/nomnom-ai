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
