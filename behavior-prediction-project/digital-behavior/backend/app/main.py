"""
Digital Behavior Twin API

Main FastAPI application that orchestrates the behavioral modeling system.
Provides endpoints for:
- Event ingestion from Chrome extension
- Session management and analysis
- Feature engineering
- Abandonment risk predictions
- Intervention recommendations
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.events import router as events_router
from .api.v1.sessions import router as sessions_router
from .api.v1.predictions import router as predictions_router

# Initialize FastAPI app
app = FastAPI(
    title="Digital Behavior Twin API",
    description="API for behavioral modeling and task abandonment prediction",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Get allowed origins from environment variable or use defaults
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# Configure CORS for frontend and extension access
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS + ["chrome-extension://*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
def root():
    """API root endpoint."""
    return {
        "message": "Digital Behavior Twin API",
        "version": "0.1.0",
        "docs": "/api/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "ok", "service": "digital-behavior-twin"}


# Include API route modules
app.include_router(events_router, prefix="/api/v1")
app.include_router(sessions_router, prefix="/api/v1")
app.include_router(predictions_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
