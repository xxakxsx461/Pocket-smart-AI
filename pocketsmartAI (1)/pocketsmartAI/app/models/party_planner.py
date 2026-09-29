from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class PartyPlanRequest(BaseModel):
    budget: float = Field(..., gt=0, description='Total event budget')
    guest_count: int = Field(..., gt=0, description='Expected number of attendees')
    event_type: str = Field(default='Birthday Party', description='e.g. Birthday Party, Housewarming, Cocktail Evening')
    venue_required: bool = Field(default=False, description='Whether a rented venue or hotel stay is required')
    food_preference: str = Field(default='Starters & Multi-Cuisine Platters', description='Catering preference')
    theme_or_vibe: Optional[str] = Field(default='Lively & Festive', description='Party theme or aesthetic')

class CategoryBreakdown(BaseModel):
    category: str  # Food & Catering, Decor & Ambience, Music & Entertainment, Venue & Stay, Essentials
    allocated_budget: float
    percentage: float
    sources: List[str]  # e.g. Swiggy, Zomato, OYO, Amazon
    items_or_suggestions: List[str]

class PartnerRecommendation(BaseModel):
    partner: str       # Swiggy, Zomato, OYO, etc.
    service_type: str  # Catering, Venue, Decor, Drinks
    deal_title: str
    estimated_cost: float
    description: str
    action_url: Optional[str] = None

class PartyPlanResponse(BaseModel):
    plan_id: str
    total_budget: float
    guest_count: int
    cost_per_guest: float
    categories: List[CategoryBreakdown]
    partner_recommendations: List[PartnerRecommendation]
    itinerary_timeline: List[str]
    ai_tips: List[str]
    created_at: str
