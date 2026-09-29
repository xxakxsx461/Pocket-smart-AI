from pydantic import BaseModel, Field
from typing import List, Optional

class JewelryPlanRequest(BaseModel):
    budget: float = Field(..., gt=0, description='Total jewelry shopping budget')
    occasion: str = Field(default='Wedding Guest', description='e.g. Wedding, Cocktail Party, Daily Wear, Festival')
    preferred_metal_or_style: str = Field(default='Gold Plated & Kundan', description='Preferred metal, stone, or style')
    outfit_description: Optional[str] = Field(default='', description='Description of attire (colors, neckline, embroidery)')
    image_filename: Optional[str] = Field(default=None, description='Uploaded outfit image path if any')

class JewelryItem(BaseModel):
    id: str
    name: str
    type: str             # Earrings, Necklace / Choker, Bangles / Bracelet, Ring, Maang Tikka
    estimated_price: float
    source: str           # Amazon, Flipkart, Tanishq, etc.
    metal_or_material: str
    matching_reason: str
    product_url: Optional[str] = None
    image_url: Optional[str] = None

class JewelryPlanResponse(BaseModel):
    plan_id: str
    total_budget: float
    total_estimated_price: float
    remaining_budget: float
    occasion: str
    outfit_analysis: Optional[str] = None  # AI visual or textual insight on outfit pairing
    jewelry_pieces: List[JewelryItem]
    styling_advice: List[str]
    created_at: str
