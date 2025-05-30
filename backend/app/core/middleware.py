# backend/app/core/middleware.py
"""
Application middleware
"""
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

def setup_cors(app):
    """Configure CORS middleware"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )