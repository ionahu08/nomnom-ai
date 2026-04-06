"""
Recommendation schemas — RAG-powered meal suggestions.
"""

from pydantic import BaseModel


class MealRecommendationResponse(BaseModel):
    """Response from meal recommendation endpoint."""

    recommendation: str
    kb_entries_used: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "recommendation": "Since you're low on protein (need 35g more), I suggest grilled salmon with quinoa. Both are protein-rich and will pair nicely with your Greek salad.",
                "kb_entries_used": 5,
            }
        }
