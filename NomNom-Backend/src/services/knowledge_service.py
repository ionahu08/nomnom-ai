"""
Knowledge Service — RAG retrieval and nutrition knowledge base management.

Handles:
1. Semantic search over nutrition KB (for RAG context injection)
2. Seeding the KB with initial nutrition data
"""

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.llm.embedding import embedding_service
from src.models.nutrition_kb import NutritionKB

logger = logging.getLogger(__name__)

# Nutrition KB seed data: ~40 entries covering various topics
NUTRITION_KB_SEED_DATA = [
    {
        "title": "Greek yogurt protein",
        "content": "Non-fat Greek yogurt provides 17g protein per 170g serving (100 calories), making it one of the best protein-per-calorie foods for muscle building.",
        "category": "protein",
    },
    {
        "title": "Chicken breast macros",
        "content": "Boneless skinless chicken breast provides 31g protein per 100g cooked weight, with minimal fat (3.6g). A staple lean protein source.",
        "category": "protein",
    },
    {
        "title": "Eggs for breakfast",
        "content": "One large egg contains 6g protein and all 9 essential amino acids. The yolk has choline for brain health. Boiled or scrambled, a complete breakfast.",
        "category": "protein",
    },
    {
        "title": "Salmon omega-3s",
        "content": "Wild-caught salmon provides 25g protein per 100g and 2.3g omega-3 fatty acids per serving. Reduces inflammation and supports heart health.",
        "category": "protein",
    },
    {
        "title": "Lentils plant protein",
        "content": "Dried lentils have 25g protein per 100g dry weight (cooked: 9g per cup). High in fiber and iron, ideal for vegetarian meal planning.",
        "category": "protein",
    },
    {
        "title": "Oats for sustained energy",
        "content": "Rolled oats have a low glycemic index (55) and provide 27g carbs per 40g dry serving, with 8g protein. Keeps blood sugar stable for 3-4 hours.",
        "category": "carbs",
    },
    {
        "title": "Brown rice whole grain",
        "content": "Brown rice has 45g carbs and 4g protein per cooked cup, with 3.5g fiber. More nutritious than white rice due to retained bran and germ.",
        "category": "carbs",
    },
    {
        "title": "Sweet potato nutrition",
        "content": "One medium sweet potato has 27g carbs, 4g fiber, and high vitamin A (beta-carotene). Low glycemic index despite moderate carb content.",
        "category": "carbs",
    },
    {
        "title": "Quinoa complete carb",
        "content": "Quinoa contains all 9 essential amino acids (15g protein per cooked cup) and 39g carbs. A complete protein grain for vegetarians.",
        "category": "carbs",
    },
    {
        "title": "Banana quick carbs",
        "content": "One medium banana has 27g carbs (23g simple sugars) and 3g fiber. Fast energy source, 12mg magnesium for muscle recovery post-workout.",
        "category": "carbs",
    },
    {
        "title": "Olive oil healthy fat",
        "content": "Extra virgin olive oil has 10g fat per tablespoon (120 kcal), rich in oleic acid and polyphenols. Use for salads, not high-heat cooking.",
        "category": "fat",
    },
    {
        "title": "Avocado monounsaturated fat",
        "content": "One avocado has 21g fat (mostly monounsaturated), 10g fiber, and 3g protein. Supports cholesterol health and fat-soluble vitamin absorption.",
        "category": "fat",
    },
    {
        "title": "Nuts healthy fats snack",
        "content": "Almonds have 14g fat and 6g protein per ounce. Walnuts add 2.5g omega-3 per ounce. Best unsalted for sodium control.",
        "category": "fat",
    },
    {
        "title": "Coconut oil MCT fat",
        "content": "Coconut oil has 12g saturated fat per tablespoon. MCTs (medium-chain triglycerides) are metabolized faster than other fats, though total fat calories still count.",
        "category": "fat",
    },
    {
        "title": "Iron in red meat",
        "content": "Beef provides heme iron (highly absorbable), 25g protein per 100g, and B vitamins (B12, niacin). 3-4 oz servings 2-3x weekly for iron stores.",
        "category": "micronutrients",
    },
    {
        "title": "Calcium for bones",
        "content": "Dairy products provide 300mg calcium per cup (plus vitamin D for absorption). Non-dairy: leafy greens, fortified plant milks, almonds.",
        "category": "micronutrients",
    },
    {
        "title": "Zinc immune function",
        "content": "Oysters have 5.5mg zinc per serving, beef 5.5mg per 100g, pumpkin seeds 2mg per tablespoon. Essential for immune system and wound healing.",
        "category": "micronutrients",
    },
    {
        "title": "Vitamin C fruit sources",
        "content": "Oranges have 53mg vitamin C per fruit, kiwis 64mg, strawberries 50mg per cup. Supports collagen formation and immune health.",
        "category": "micronutrients",
    },
    {
        "title": "Pre-workout carbs timing",
        "content": "Consume 30-60g carbs 30-60 minutes before exercise (banana, oatmeal, rice cakes). Provides glucose for muscles without heavy digestion.",
        "category": "timing",
    },
    {
        "title": "Post-workout protein window",
        "content": "Eat 20-40g protein within 2 hours after training (chicken, protein shake, eggs). Muscle protein synthesis peaks within 4-6 hours post-exercise.",
        "category": "timing",
    },
    {
        "title": "Breakfast sets metabolism",
        "content": "Eating within 1-2 hours of waking activates metabolism and stabilizes blood sugar. Include protein and complex carbs for sustained energy.",
        "category": "timing",
    },
    {
        "title": "Evening light meals",
        "content": "Eat lighter 2-3 hours before bed to avoid sleep disruption. Light protein (Greek yogurt, turkey) with low sugar helps maintain stable sleep.",
        "category": "timing",
    },
    {
        "title": "Water daily intake",
        "content": "Aim for 30-35 mL water per kg body weight (or 8-10 cups/day). Mild dehydration impairs cognition and performance; increase with exercise intensity.",
        "category": "hydration",
    },
    {
        "title": "Hydration during exercise",
        "content": "Drink 200-300 mL (7-10 oz) every 10-20 minutes during intense exercise lasting >1 hour. For >90 min, add 4-8% carbs (sports drinks) for energy.",
        "category": "hydration",
    },
    {
        "title": "Electrolytes sweat loss",
        "content": "Intense sweating loses 500-1500mg sodium and potassium. Sports drinks, coconut water, or bananas with salt restore electrolytes and hydration.",
        "category": "hydration",
    },
    {
        "title": "Calorie deficit weight loss",
        "content": "Create 500 kcal daily deficit = 0.5 kg (1 lb) weight loss per week. Too aggressive (<1200 kcal) reduces metabolism and muscle. Aim for 0.5-1 kg/week.",
        "category": "weight_loss",
    },
    {
        "title": "Fiber fills without calories",
        "content": "Soluble fiber (oats, beans) and insoluble fiber (vegetables) promote satiety with minimal calories. Aim for 25-30g daily to support weight loss.",
        "category": "weight_loss",
    },
    {
        "title": "Protein preserves muscle loss",
        "content": "During calorie deficit, high protein (1.6-2.2g per kg) preserves lean muscle while burning fat. Prevents metabolic slowdown from muscle loss.",
        "category": "weight_loss",
    },
    {
        "title": "Strength training retention",
        "content": "Resistance training 3-4x weekly during weight loss maintains muscle mass. 60-80% of your max effort for 6-8 reps with 48hr recovery.",
        "category": "weight_loss",
    },
    {
        "title": "Muscle growth protein",
        "content": "Build muscle with 1.6-2.2g protein per kg body weight daily, distributed across 4-5 meals. Allows 20-30g protein per meal for muscle protein synthesis.",
        "category": "muscle_gain",
    },
    {
        "title": "Calorie surplus muscle",
        "content": "Create +300-500 kcal daily surplus for muscle gains. 1g protein per kg, 4-5g carbs per kg, 1-1.5g fat per kg. More calories = more muscle but also fat gain.",
        "category": "muscle_gain",
    },
    {
        "title": "Progressive overload training",
        "content": "Gradually increase weight, reps, or sets each week. Muscles adapt in 2-3 weeks; progressively challenge them to continue growing.",
        "category": "muscle_gain",
    },
    {
        "title": "Recovery sleep gains",
        "content": "Sleep 7-9 hours nightly for muscle growth. Growth hormone peaks during deep sleep (90-120 min cycles). Poor sleep reduces muscle protein synthesis 20-30%.",
        "category": "muscle_gain",
    },
]


async def get_relevant_nutrition_entries(
    db: AsyncSession, query: str, limit: int = 5
) -> list[dict]:
    """
    Retrieve nutrition KB entries most similar to the query (RAG retrieval).

    Uses semantic search via pgvector cosine distance to find relevant nutrition facts.

    Args:
        db: Database session
        query: User query or deficit description (e.g., "need more protein")
        limit: Max entries to return

    Returns:
        List of dicts with 'title' and 'content' keys (suitable for RAG injection)
    """
    try:
        # Embed the query
        query_embedding = await embedding_service.embed_text(query)

        # Find nearest neighbors by cosine distance
        stmt = (
            select(NutritionKB)
            .where(NutritionKB.embedding.is_not(None))
            .order_by(NutritionKB.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )

        result = await db.execute(stmt)
        rows = result.scalars().all()

        return [{"title": row.title, "content": row.content} for row in rows]

    except Exception as e:
        logger.error(f"Failed to retrieve nutrition entries: {e}")
        return []


async def seed_nutrition_kb(db: AsyncSession) -> int:
    """
    Populate the nutrition KB with seed data (idempotent by title).

    Embeds each entry and inserts if not already present.

    Args:
        db: Database session

    Returns:
        Number of rows inserted
    """
    inserted = 0

    for entry in NUTRITION_KB_SEED_DATA:
        # Check if already exists by title
        existing = await db.execute(
            select(NutritionKB).where(NutritionKB.title == entry["title"])
        )
        if existing.scalar_one_or_none() is not None:
            logger.debug(f"Skipping existing entry: {entry['title']}")
            continue

        # Embed the content
        try:
            embedding = await embedding_service.embed_text(entry["content"])
        except Exception as e:
            logger.error(
                f"Failed to embed KB entry '{entry['title']}': {e}, skipping"
            )
            continue

        # Create and insert row
        kb_entry = NutritionKB(
            title=entry["title"],
            content=entry["content"],
            category=entry["category"],
            embedding=embedding,
        )
        db.add(kb_entry)
        inserted += 1

    if inserted > 0:
        await db.commit()
        logger.info(f"Seeded {inserted} nutrition KB entries")

    return inserted
