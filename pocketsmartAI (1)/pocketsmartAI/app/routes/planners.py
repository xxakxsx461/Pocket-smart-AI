import os
import uuid
import json
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException, Depends

from app.models.home_planner import HomePlanRequest, HomePlanResponse
from app.models.party_planner import PartyPlanRequest, PartyPlanResponse
from app.models.jewelry_planner import JewelryPlanRequest, JewelryPlanResponse
from app.services.gemini_utils import (
    generate_home_recommendations,
    generate_party_recommendations,
    generate_jewelry_recommendations
)
from app.services.storage_service import storage
from app.services.auth_service import get_current_user_optional
from app.config import settings

router = APIRouter(tags=["Planners & AI Recommendations"])

# ------------------------------------------------------------------------------
# 1. HOME PLANNER
# ------------------------------------------------------------------------------
@router.post("/generate-home", response_model=HomePlanResponse)
async def generate_home(req: HomePlanRequest, request: Request):
    user = get_current_user_optional(request)
    user_id = user["id"] if user else None
    
    plan = generate_home_recommendations(req)
    
    # Save to history
    record = {
        "id": plan.plan_id,
        "user_id": user_id,
        "planner_type": "home",
        "title": f"{req.style_preference} Interior ({', '.join(req.rooms)})",
        "budget": req.budget,
        "spent_or_allocated": plan.estimated_total_cost,
        "created_at": plan.created_at,
        "input_parameters": req.model_dump(),
        "recommendation_summary": plan.model_dump()
    }
    storage.save_history(record)
    
    return plan

# ------------------------------------------------------------------------------
# 2. PARTY PLANNER
# ------------------------------------------------------------------------------
@router.post("/generate-party", response_model=PartyPlanResponse)
async def generate_party(req: PartyPlanRequest, request: Request):
    user = get_current_user_optional(request)
    user_id = user["id"] if user else None
    
    plan = generate_party_recommendations(req)
    
    # Save to history
    record = {
        "id": plan.plan_id,
        "user_id": user_id,
        "planner_type": "party",
        "title": f"{req.event_type} for {req.guest_count} Guests",
        "budget": req.budget,
        "spent_or_allocated": plan.total_budget,
        "created_at": plan.created_at,
        "input_parameters": req.model_dump(),
        "recommendation_summary": plan.model_dump()
    }
    storage.save_history(record)
    
    return plan

# ------------------------------------------------------------------------------
# 3. JEWELRY PLANNER (JSON & Multimodal Upload)
# ------------------------------------------------------------------------------
@router.post("/generate-jewelry", response_model=JewelryPlanResponse)
async def generate_jewelry(req: JewelryPlanRequest, request: Request):
    user = get_current_user_optional(request)
    user_id = user["id"] if user else None
    
    image_path = None
    if req.image_filename:
        candidate_path = settings.UPLOADS_DIR / req.image_filename
        if candidate_path.exists():
            image_path = str(candidate_path)
            
    plan = generate_jewelry_recommendations(req, image_path=image_path)
    
    # Save to history
    record = {
        "id": plan.plan_id,
        "user_id": user_id,
        "planner_type": "jewelry",
        "title": f"{req.preferred_metal_or_style} for {req.occasion}",
        "budget": req.budget,
        "spent_or_allocated": plan.total_estimated_price,
        "created_at": plan.created_at,
        "input_parameters": req.model_dump(),
        "recommendation_summary": plan.model_dump()
    }
    storage.save_history(record)
    
    return plan

@router.post("/generate-jewelry-upload", response_model=JewelryPlanResponse)
async def generate_jewelry_with_upload(
    request: Request,
    budget: float = Form(...),
    occasion: str = Form(...),
    preferred_metal_or_style: str = Form(...),
    outfit_description: Optional[str] = Form(None),
    outfit_image: Optional[UploadFile] = File(None)
):
    user = get_current_user_optional(request)
    user_id = user["id"] if user else None
    
    saved_filename = None
    image_full_path = None
    
    if outfit_image and outfit_image.filename:
        ext = Path(outfit_image.filename).suffix or ".jpg"
        unique_name = f"outfit_{uuid.uuid4().hex[:10]}{ext}"
        target_path = settings.UPLOADS_DIR / unique_name
        
        contents = await outfit_image.read()
        with open(target_path, "wb") as f:
            f.write(contents)
            
        saved_filename = unique_name
        image_full_path = str(target_path)
        
    req = JewelryPlanRequest(
        budget=budget,
        occasion=occasion,
        preferred_metal_or_style=preferred_metal_or_style,
        outfit_description=outfit_description,
        image_filename=saved_filename
    )
    
    plan = generate_jewelry_recommendations(req, image_path=image_full_path)
    
    # Save to history
    record = {
        "id": plan.plan_id,
        "user_id": user_id,
        "planner_type": "jewelry",
        "title": f"{req.preferred_metal_or_style} for {req.occasion}",
        "budget": req.budget,
        "spent_or_allocated": plan.total_estimated_price,
        "created_at": plan.created_at,
        "input_parameters": req.model_dump(),
        "recommendation_summary": plan.model_dump()
    }
    storage.save_history(record)
    
    return plan
