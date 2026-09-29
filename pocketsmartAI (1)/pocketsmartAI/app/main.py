from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes.auth import router as auth_router
from app.routes.planners import router as planners_router
from app.routes.history import router as history_router
from app.routes.views import router as views_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered Budget & Lifestyle Recommendation Platform",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

# Jinja2 Templates setup
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))

# Include API Routers
app.include_router(auth_router)
app.include_router(planners_router)
app.include_router(history_router)

# Include Frontend View Router
app.include_router(views_router)

@app.get("/startup")
async def startup_health():
    return {
        "status": "operational",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "ai_mode": "live-gemini" if settings.has_gemini_key else "mock-simulation-active",
        "modules": {
            "home_interior_planner": {
                "status": "available",
                "sources": ["IKEA", "Amazon", "Wayfair"]
            },
            "party_planner": {
                "status": "available",
                "sources": ["Swiggy", "Zomato", "OYO", "Blinkit"]
            },
            "jewelry_planner": {
                "status": "available",
                "multimodal_vision": True,
                "sources": ["Amazon", "Flipkart", "Tanishq"]
            }
        },
        "supported_routes": [
            "/startup",
            "/generate-home",
            "/generate-party",
            "/generate-jewelry",
            "/generate-jewelry-upload",
            "/register",
            "/login",
            "/logout",
            "/token",
            "/session-info",
            "/session-data",
            "/recommendations-details",
            "/history",
            "/dashboard",
            "/planner/home",
            "/planner/party",
            "/planner/jewelry",
            "/history-view"
        ]
    }
