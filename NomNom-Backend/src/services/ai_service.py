import base64
import json
import logging

import anthropic

from src.config import settings
from src.schemas.food_log import FoodAnalysisResponse

logger = logging.getLogger(__name__)

client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

SYSTEM_PROMPT = """You are a funny, {cat_style} cat who judges people's food choices.

When shown a food photo, you must:
1. Identify the food
2. Estimate its nutritional content
3. Write a short, funny roast about the food (1-2 sentences, in character as a {cat_style} cat)

Respond with ONLY valid JSON in this exact format (no markdown, no extra text):
{{
  "food_name": "name of the food",
  "calories": estimated calories as integer,
  "protein_g": estimated protein in grams as number,
  "carbs_g": estimated carbs in grams as number,
  "fat_g": estimated fat in grams as number,
  "food_category": "category like salad, fast food, dessert, home-cooked, etc",
  "cuisine_origin": "cuisine like Japanese, Italian, American, etc",
  "cat_roast": "your funny roast about this food"
}}"""


async def analyze_food_photo(image_bytes: bytes, cat_style: str = "sassy") -> FoodAnalysisResponse:
    """Send a food photo to Haiku vision and get analysis + roast."""
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    prompt = SYSTEM_PROMPT.format(cat_style=cat_style)

    message = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        system=prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": "What food is this? Analyze it and roast me.",
                    },
                ],
            }
        ],
    )

    raw_text = message.content[0].text
    logger.info("Haiku response: %s", raw_text)

    # Strip markdown code fences if present (e.g. ```json ... ```)
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.error("Failed to parse Haiku response as JSON: %s", raw_text)
        return FoodAnalysisResponse(
            food_name="Unknown Food",
            calories=0,
            protein_g=0,
            carbs_g=0,
            fat_g=0,
            food_category="unknown",
            cuisine_origin="unknown",
            cat_roast="I tried to judge your food but my brain broke. Try again.",
        )

    return FoodAnalysisResponse(
        food_name=data.get("food_name", "Unknown Food"),
        calories=int(data.get("calories", 0)),
        protein_g=float(data.get("protein_g", 0)),
        carbs_g=float(data.get("carbs_g", 0)),
        fat_g=float(data.get("fat_g", 0)),
        food_category=data.get("food_category"),
        cuisine_origin=data.get("cuisine_origin"),
        cat_roast=data.get("cat_roast", "No comment."),
    )
