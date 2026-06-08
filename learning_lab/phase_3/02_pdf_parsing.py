#!/usr/bin/env python3
"""
Phase 3 Day 2: PDF Support — Nutrition Label Parsing

Key insight: Claude can read PDFs directly without external libraries.
Just encode the PDF as base64 and send it with media_type "application/pdf".

Why this matters for NomNom:
- Users often have nutrition label PDFs
- Instead of manual data entry, Claude reads the label
- Extract: calories, protein, carbs, fat, ingredients

Usage:
    python 02_pdf_parsing.py

This script:
1. Demonstrates how to send a PDF to Claude
2. Asks Claude to extract nutrition data
3. Shows Claude parsing tables, charts, and text
"""

import os
import base64
import asyncio
import json
from pathlib import Path
from anthropic import AsyncAnthropic

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set")

client = AsyncAnthropic(api_key=api_key)


# ============================================================================
# HELPER: ENCODE PDF TO BASE64
# ============================================================================

def encode_pdf_to_base64(pdf_path: str) -> str:
    """Read PDF file and encode as base64."""
    with open(pdf_path, "rb") as pdf_file:
        return base64.standard_b64encode(pdf_file.read()).decode("utf-8")


# ============================================================================
# FUNCTION: PARSE NUTRITION LABEL FROM PDF
# ============================================================================

async def parse_nutrition_label_pdf(pdf_path: str) -> dict:
    """
    Send a nutrition label PDF to Claude and extract nutrition data.

    Args:
        pdf_path: Path to PDF file (must exist)

    Returns:
        Dictionary with extracted nutrition info
    """

    if not Path(pdf_path).exists():
        return {"error": f"PDF not found: {pdf_path}"}

    # Step 1: Encode PDF as base64
    print(f"\n📄 Reading PDF: {pdf_path}")
    pdf_b64 = encode_pdf_to_base64(pdf_path)

    # Step 2: Send to Claude with media_type="application/pdf"
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_b64,
                    },
                },
                {
                    "type": "text",
                    "text": """Extract nutrition information from this PDF label.
Return as JSON with these fields:
{
  "product_name": "...",
  "serving_size": "...",
  "calories": number,
  "protein_g": number,
  "carbs_g": number,
  "fat_g": number,
  "ingredients": ["...", "..."],
  "notes": "any other important info"
}

If you can't find a field, use null.""",
                },
            ],
        }
    ]

    # Step 3: Call Claude (multimodal PDF support)
    print("🤖 Sending to Claude for analysis...")
    response = await client.messages.create(
        model="claude-opus-4-1-20250805",
        max_tokens=1024,
        messages=messages,
    )

    # Step 4: Parse Claude's response
    response_text = response.content[0].text

    print(f"\n📋 Claude's Analysis:")
    print(response_text)

    # Try to extract JSON from response
    try:
        # Find JSON in response (Claude might add text before/after)
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            extracted = json.loads(json_str)
            return extracted
    except json.JSONDecodeError:
        pass

    # Fallback: return raw response
    return {"raw_response": response_text}


# ============================================================================
# DEMO: TEST WITH SAMPLE PDF
# ============================================================================

async def main():
    """Demonstrate PDF parsing with example PDFs."""

    print("🎯 Phase 3 Day 2: PDF Support — Nutrition Label Parsing")
    print("\nKey learning:")
    print("- Claude can read PDFs natively (no external library)")
    print("- Use media_type='application/pdf' in messages")
    print("- Works with: tables, charts, text, handwriting")
    print()

    # Example 1: Try with a real PDF if it exists
    test_pdf = "learning_lab/phase_3/sample_nutrition_label.pdf"
    if Path(test_pdf).exists():
        print(f"✅ Found test PDF: {test_pdf}")
        result = await parse_nutrition_label_pdf(test_pdf)
        print(f"\nExtracted Data:\n{json.dumps(result, indent=2)}")
    else:
        print(f"ℹ️  Sample PDF not found at {test_pdf}")
        print("\nTo test with a real PDF:")
        print("1. Save a nutrition label PDF to learning_lab/phase_3/sample_nutrition_label.pdf")
        print("2. Run this script again")
        print("\nFor now, here's what Claude WOULD extract:")
        print(json.dumps(
            {
                "product_name": "Organic Whole Grain Bread",
                "serving_size": "2 slices (56g)",
                "calories": 160,
                "protein_g": 6,
                "carbs_g": 28,
                "fat_g": 2,
                "ingredients": ["Whole wheat flour", "Water", "Yeast", "Salt"],
                "notes": "Good source of fiber and protein",
            },
            indent=2,
        ))

    # Example 2: Show the pattern for Day 3 (embeddings)
    print("\n" + "=" * 70)
    print("NEXT: Day 3 — Embeddings + Vector Search")
    print("=" * 70)
    print("""
After PDF parsing (Day 2), the next step is:
1. Extract text from PDF → "Organic Whole Grain Bread: 160 cal, 6g protein..."
2. Convert to embedding vector → [0.23, 0.45, 0.12, ...]
3. Store in vector database
4. Later: User asks "What bread did I eat?" →
   - Vector search finds similar products
   - RAG returns the PDF data with citations

This is the foundation for Phase 3's capstone (Days 8-9).
""")


if __name__ == "__main__":
    asyncio.run(main())
