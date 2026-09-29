from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class HomePlanRequest(BaseModel):
    budget: float = Field(..., gt=0, description='Total allocated budget')
    rooms: List[str] = Field(..., min_length=1, description='List of rooms e.g. Living Room, Bedroom')
    room_quantities: Optional[Dict[str, int]] = Field(default_factory=dict, description='Count per room')
    style_preference: str = Field(default='Modern Minimalist', description='Style e.g. Bohemian, Scandinavian, Industrial')
    color_palette: Optional[str] = Field(default='Neutral & Warm Woods', description='Desired color palette')
    special_requirements: Optional[str] = Field(default='', description='Any notes like pet-friendly or eco-materials')

class RecommendedProduct(BaseModel):
    id: str
    name: str
    category: str  # Furniture, Lighting, Decor, Storage, Textiles
    room: str
    estimated_price: float
    source: str    # IKEA, Amazon, Wayfair, etc.
    product_url: Optional[str] = None
    reasoning: str
    image_url: Optional[str] = None

class HomePlanResponse(BaseModel):
    plan_id: str
    total_budget: float
    estimated_total_cost: float
    remaining_budget: float
    style_summary: str
    room_breakdown: Dict[str, List[RecommendedProduct]]
    all_products: List[RecommendedProduct]
    ai_tips: List[str]
    created_at: str
