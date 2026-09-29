from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class PlanHistoryRecord(BaseModel):
    id: str
    user_id: Optional[str] = None
    planner_type: str  # 'home', 'party', 'jewelry'
    title: str
    budget: float
    spent_or_allocated: float
    created_at: str
    input_parameters: Dict[str, Any]
    recommendation_summary: Dict[str, Any]

class HistoryListResponse(BaseModel):
    total: int
    items: List[PlanHistoryRecord]
