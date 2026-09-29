POCKETSMART AI – SMART BUDGET & RECOMMENDATION ASSISTANT

PHASE 3: PROJECT DESIGN

System Architecture:
Frontend -> FastAPI Backend -> Services -> Database / Gemini AI

Frontend:

- HTML
- CSS
- JavaScript
- Jinja2 Templates

Backend:

- FastAPI
- Authentication
- Planner APIs
- Recommendation generation
- History management

Database:

- SQLite
- Stores user information
- Stores recommendation history

AI:

- Gemini API
- Local fallback recommendation engine

User Flow:
Register -> Login -> Choose Planner -> Enter Budget -> Generate Recommendations -> View Results -> View History

Project Structure:

- app/ - Backend application
- app/ai/ - AI integration and prompts
- app/routers/ - Application routes
- app/services/ - Business logic
- data/ - Local catalog data
- run.py - Application startup
- requirements.txt - Dependencies