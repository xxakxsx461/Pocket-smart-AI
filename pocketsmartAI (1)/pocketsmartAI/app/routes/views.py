from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import settings
from app.services.auth_service import get_current_user_optional
from app.services.storage_service import storage

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))
templates.env.globals["max"] = max
templates.env.globals["min"] = min

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    user = get_current_user_optional(request)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user": user,
            "project_name": settings.PROJECT_NAME
        }
    )

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = get_current_user_optional(request)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "user": user,
            "project_name": settings.PROJECT_NAME
        }
    )

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    user = get_current_user_optional(request)
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "user": user,
            "project_name": settings.PROJECT_NAME
        }
    )

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    user = get_current_user_optional(request)
    user_id = user["id"] if user else None
    plans = storage.get_history(user_id=user_id)
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": user,
            "plans": plans[:6],
            "project_name": settings.PROJECT_NAME
        }
    )

@router.get("/planner/home", response_class=HTMLResponse)
async def home_planner_page(request: Request):
    user = get_current_user_optional(request)
    return templates.TemplateResponse(
        request=request,
        name="planners/home.html",
        context={
            "user": user,
            "project_name": settings.PROJECT_NAME
        }
    )

@router.get("/planner/party", response_class=HTMLResponse)
async def party_planner_page(request: Request):
    user = get_current_user_optional(request)
    return templates.TemplateResponse(
        request=request,
        name="planners/party.html",
        context={
            "user": user,
            "project_name": settings.PROJECT_NAME
        }
    )

@router.get("/planner/jewelry", response_class=HTMLResponse)
async def jewelry_planner_page(request: Request):
    user = get_current_user_optional(request)
    return templates.TemplateResponse(
        request=request,
        name="planners/jewelry.html",
        context={
            "user": user,
            "project_name": settings.PROJECT_NAME
        }
    )

@router.get("/recommendations/{plan_id}", response_class=HTMLResponse)
async def recommendations_page(request: Request, plan_id: str):
    user = get_current_user_optional(request)
    plan_record = storage.get_history_by_id(plan_id)
    return templates.TemplateResponse(
        request=request,
        name="recommendations.html",
        context={
            "user": user,
            "plan": plan_record,
            "plan_id": plan_id,
            "project_name": settings.PROJECT_NAME
        }
    )

@router.get("/history-view", response_class=HTMLResponse)
async def history_page(request: Request):
    user = get_current_user_optional(request)
    user_id = user["id"] if user else None
    plans = storage.get_history(user_id=user_id)
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "user": user,
            "plans": plans,
            "project_name": settings.PROJECT_NAME
        }
    )
