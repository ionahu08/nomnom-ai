#!/usr/bin/env python3
"""
NomNom v0.5 — Sandbox Capstone for Phase 1

This script demonstrates the full LLM pipeline learned in Phase 1:
1. Load an image from disk
2. Render a prompt using prompt_engine.py (with Jinja2 templates)
3. Call Claude via client.py (with retry, timeout, fallback)
4. Parse and display the nutrition JSON response

Usage:
    python nomnom_v0_5.py /path/to/food_photo.jpg [--cat-style sassy]

Example:
    python nomnom_v0_5.py ~/Photos/pizza.jpg --cat-style grumpy

This is sandbox code (learning_lab/) — not production.
No error handling, no logging, just focused learning.
"""

# ============================================================================
# 🎯 HIGH-LEVEL OVERVIEW: Program Structure
# ============================================================================
#
# This script has 5 main functions that work together:
#
# 1. load_image_as_base64()
#    Purpose: Convert image file to base64 string (Claude API needs this format)
#    Input: Path to image file
#    Output: Base64-encoded string
#
# 2. get_image_media_type()
#    Purpose: Detect image format (JPEG, PNG, etc.)
#    Input: Path to image file
#    Output: Media type string like "image/jpeg"
#
# 3. analyze_food_photo()
#    Purpose: THE MAIN PIPELINE — puts everything together
#    Input: Image path, cat style
#    Output: Dictionary with nutrition data
#
#    Inside this function, 5 steps happen:
#    - Step 1: Render prompt using prompt_engine.py (Jinja2 + templates)
#    - Step 2: Load and encode the image
#    - Step 3: Build the message structure Claude expects
#    - Step 4: Call Claude via client.py (with retry/timeout/fallback!)
#    - Step 5: Parse the JSON response
#
# 4. display_results()
#    Purpose: Pretty-print nutrition data for user to see
#    Input: Dictionary with nutrition data
#    Output: None (just prints to console)
#
# 5. main()
#    Purpose: Entry point — parse arguments and run analysis
#    Input: Command-line arguments
#    Output: Calls analyze_food_photo() and display_results()
#
# ============================================================================

import sys
import os
import json
import base64
import argparse
from pathlib import Path

# === IMPORTS FROM PRODUCTION CODE ===
# Add src to path so we can import the modules we learned about
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "NomNom-Backend" / "src"))

# Import client.py — the LLM wrapper with retry/timeout/fallback logic
from llm.client import LLMClient

# Import prompt_engine.py — renders Jinja2 templates to create prompts
from llm.prompt_engine import render_analyze_food_prompt


def load_image_as_base64(image_path: str) -> str:
    """
    Load an image file and encode it as base64.

    Why base64? Claude's API expects images to be encoded as base64 strings
    so they can be sent over HTTP. We can't send raw binary data.

    Args:
        image_path: Path to the image file (e.g., "/home/user/pizza.jpg")

    Returns:
        Base64-encoded image data (a long string of characters)
    """
    # Open the image file in binary mode ("rb")
    with open(image_path, "rb") as image_file:
        # Read all binary data, encode to base64, decode to string
        return base64.standard_b64encode(image_file.read()).decode("utf-8")


def get_image_media_type(image_path: str) -> str:
    """
    Guess the media type from file extension.

    Claude's API needs to know what format the image is (JPEG? PNG?).
    We figure this out by looking at the file extension.

    Args:
        image_path: Path to the image file

    Returns:
        Media type string like "image/jpeg" or "image/png"
    """
    # Get the file extension (e.g., ".jpg" from "photo.jpg")
    suffix = Path(image_path).suffix.lower()

    # Map file extensions to media types
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }

    # Return the media type, or default to JPEG if unknown
    return media_types.get(suffix, "image/jpeg")


async def analyze_food_photo(image_path: str, cat_style: str = "sassy") -> dict:
    """
    Analyze a food photo and return nutrition data.

    This is the main function that puts everything together:
    - Renders prompt (prompt_engine.py)
    - Loads image (image encoding)
    - Calls Claude (client.py)
    - Parses JSON response

    Args:
        image_path: Path to the food photo
        cat_style: Which cat personality to use
                   (sassy, grumpy, wholesome, concerned, neutral)

    Returns:
        Dictionary with nutrition data (food_name, calories, protein_g, etc.)
    """

    # ===== STEP 1: RENDER THE PROMPT =====
    # This is prompt_engine.py in action!
    # We learned that prompt_engine renders Jinja2 templates with variables injected.
    print(f"📝 Rendering prompt with cat_style='{cat_style}'...")

    # Call the wrapper function from prompt_engine.py
    # This loads analyze_food.j2, injects cat_style, includes cat_personas.j2
    # Returns a fully rendered prompt string ready to send to Claude
    prompt = render_analyze_food_prompt(cat_style=cat_style)

    print(f"   Prompt length: {len(prompt)} chars")
    print()

    # ===== STEP 2: LOAD AND ENCODE THE IMAGE =====
    # Claude's API requires images to be base64-encoded
    print(f"📸 Loading image: {image_path}...")

    # Convert image file to base64 string
    image_base64 = load_image_as_base64(image_path)

    # Determine the image format (JPEG, PNG, etc.)
    media_type = get_image_media_type(image_path)

    print(f"   Media type: {media_type}")
    print(f"   Encoded size: {len(image_base64)} chars")
    print()

    # ===== STEP 3: BUILD THE MESSAGE ====
    # Claude's API expects messages in a specific format:
    # - A "role" (user or assistant)
    # - "content" which can be text, images, or both
    print("🔨 Building message with image and prompt...")

    # Build the message structure that Claude's API expects
    messages = [
        {
            "role": "user",  # We (the user) are sending this message
            "content": [
                # Part 1: The image (Claude will "see" this)
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": image_base64,
                    },
                },
                # Part 2: The text prompt (Claude will "read" this)
                {
                    "type": "text",
                    "text": prompt,
                },
            ],
        }
    ]

    print(f"   Message built with image + text prompt")
    print()

    # ===== STEP 4: CALL CLAUDE VIA CLIENT.PY =====
    # This is where client.py's magic happens!
    # Retry logic, timeout enforcement, fallback model
    print("🚀 Calling Claude via client.py...")

    # Get the API key from environment (you need to set ANTHROPIC_API_KEY)
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set. Please set your API key.")

    # Create an LLMClient instance (this is client.py)
    client = LLMClient(api_key=api_key)

    # Call create_message_with_retry (the core function from client.py)
    # This handles:
    # - Retry logic (2 retries with exponential backoff)
    # - Timeout enforcement (20s for Haiku)
    # - Fallback to Sonnet if Haiku fails
    response = await client.create_message_with_retry(
        model="claude-haiku-4-5-20251001",  # Fast, cheap model for simple task
        messages=messages,
        system="You are analyzing a food photo.",
        fallback_model="claude-sonnet-4-20250514",  # Fallback if Haiku fails
    )

    print(f"   ✅ Got response from Claude!")
    print(f"   Tokens used: {response.usage.input_tokens} input, {response.usage.output_tokens} output")
    print()

    # ===== STEP 5: PARSE THE JSON RESPONSE =====
    # Claude should return JSON (because our prompt template requested ONLY JSON)
    print("📊 Parsing JSON response...")

    # Extract the text response from Claude's message object
    response_text = response.content[0].text

    # Try to parse it as JSON
    try:
        # Try direct JSON parse first
        nutrition_data = json.loads(response_text)
    except json.JSONDecodeError:
        # If that fails, search for JSON in the response
        # (Sometimes Claude adds markdown backticks around JSON)
        print("   ⚠️  Response wasn't pure JSON, searching for JSON block...")

        # Find the first "{" and last "}"
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1

        if json_start >= 0 and json_end > json_start:
            # Extract the JSON substring and parse it
            nutrition_data = json.loads(response_text[json_start:json_end])
        else:
            raise ValueError("Could not find JSON in response")

    print(f"   ✅ Parsed successfully")
    print()

    return nutrition_data


def display_results(nutrition_data: dict) -> None:
    """
    Pretty-print the nutrition data for the user to see.

    Args:
        nutrition_data: Parsed JSON from Claude (contains food_name, calories, cat_roast, etc.)
    """
    print("=" * 60)
    print("🍽️  FOOD ANALYSIS RESULTS")
    print("=" * 60)

    # Display each piece of nutrition data
    print(f"\n📌 Food Name: {nutrition_data.get('food_name', 'Unknown')}")
    print(f"🏷️  Category: {nutrition_data.get('food_category', 'Unknown')}")
    print(f"🌍 Cuisine: {nutrition_data.get('cuisine_origin', 'Unknown')}")

    # Display macronutrients
    print(f"\n📊 Nutrition (per serving):")
    print(f"   • Calories: {nutrition_data.get('calories', '?')} kcal")
    print(f"   • Protein: {nutrition_data.get('protein_g', '?')}g")
    print(f"   • Carbs: {nutrition_data.get('carbs_g', '?')}g")
    print(f"   • Fat: {nutrition_data.get('fat_g', '?')}g")

    # Display the cat's commentary (generated by Claude using the cat persona)
    print(f"\n😼 Cat Says:")
    print(f"   \"{nutrition_data.get('cat_roast', 'No comment.')}\"")

    print("\n" + "=" * 60)


async def main():
    """
    Main entry point for the script.
    Parses command-line arguments and runs the analysis.
    """

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="NomNom v0.5 — Analyze a food photo and get nutrition data"
    )

    # Required: path to the image
    parser.add_argument(
        "image_path",
        help="Path to the food photo (jpg, png, gif, webp)",
    )

    # Optional: which cat personality to use
    parser.add_argument(
        "--cat-style",
        default="sassy",
        choices=["sassy", "grumpy", "wholesome", "concerned", "neutral"],
        help="Which cat personality to use (default: sassy)",
    )

    args = parser.parse_args()

    # Validate that the image file exists
    if not os.path.exists(args.image_path):
        print(f"❌ Error: File not found: {args.image_path}")
        sys.exit(1)

    # Print banner
    print("🎬 NomNom v0.5 Sandbox Capstone")
    print(f"   Image: {args.image_path}")
    print(f"   Cat style: {args.cat_style}")
    print()

    # Run the analysis
    try:
        # Call the main analysis function
        nutrition_data = await analyze_food_photo(args.image_path, args.cat_style)

        # Display results to user
        display_results(nutrition_data)

        # Also save raw JSON for inspection
        print(f"\n💾 Raw JSON saved to: ./nomnom_output.json")
        with open("nomnom_output.json", "w") as f:
            json.dump(nutrition_data, f, indent=2)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


# === ENTRY POINT ===
# This allows the script to be run from command line
if __name__ == "__main__":
    import asyncio

    # asyncio.run() starts the async event loop and runs main()
    # (We use async because client.py uses async/await)
    asyncio.run(main())
