import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import init_db
from .routes import chat, algorithms, puzzles, probabilistic, planner

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="CampusMind AI – Intelligent College Student Assistant & AI Algorithm Laboratory API"
)

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables
@app.on_event("startup")
def on_startup():
    init_db()

# Include routers
app.include_router(chat.router)
app.include_router(algorithms.router)
app.include_router(puzzles.router)
app.include_router(probabilistic.router)
app.include_router(planner.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.version,
        "llm_gemini_configured": bool(settings.gemini_api_key),
        "llm_openai_configured": bool(settings.openai_api_key)
    }

# Mount static frontend build if it exists
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
