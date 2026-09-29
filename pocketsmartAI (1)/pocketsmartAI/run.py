"""
PocketSmart AI — Application Runner Entrypoint
Launches the FastAPI ASGI application with Uvicorn and displays local access ports.
"""
import sys
import uvicorn
from app.config import settings

def main():
    host = settings.HOST
    port = settings.PORT
    url = f"http://{host}:{port}"
    
    print("=" * 65)
    print(" ✨  PocketSmart AI — Intelligent Lifestyle & Budget Platform  ✨")
    print("=" * 65)
    print(f"  • Application Server : {url}")
    print(f"  • Interactive Web UI : {url}/")
    print(f"  • Dashboard View     : {url}/dashboard")
    print(f"  • Swagger API Docs   : {url}/docs")
    print(f"  • Startup Health API : {url}/startup")
    print(f"  • AI Engine Mode     : {'Live Gemini API' if settings.has_gemini_key else 'Simulation/Mock Fallback Engine'}")
    print("=" * 65)
    print("Press CTRL+C to stop the server.\n")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True
    )

if __name__ == "__main__":
    main()
