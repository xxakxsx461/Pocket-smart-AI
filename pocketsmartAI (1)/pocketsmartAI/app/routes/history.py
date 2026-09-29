from typing import Optional, List
from fastapi import APIRouter, Request, HTTPException, status
from app.models.history import PlanHistoryRecord, HistoryListResponse
from app.services.storage_service import storage
from app.services.auth_service import get_current_user_optional

router = APIRouter(tags=["History & Recommendation Details"])

@router.get("/recommendations-details")
async def recommendations_details(plan_id: str):
    record = storage.get_history_by_id(plan_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with id '{plan_id}' not found"
        )
    return record

@router.get("/history")
async def get_history_route(request: Request, planner_type: Optional[str] = None):
    user = get_current_user_optional(request)
    user_id = user["id"] if user else None
    
    # If user is logged in, show their plans; if guest, show recent plans or all unassigned plans
    records = storage.get_history(user_id=user_id, planner_type=planner_type)
    return {
        "total": len(records),
        "planner_type_filter": planner_type,
        "items": records
    }

@router.delete("/history/{plan_id}")
async def delete_history_item(plan_id: str, request: Request):
    user = get_current_user_optional(request)
    user_id = user["id"] if user else None
    
    deleted = storage.delete_history(plan_id, user_id=user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History item not found or you do not have permission to delete it"
        )
    return {"message": "Plan deleted successfully", "id": plan_id}
