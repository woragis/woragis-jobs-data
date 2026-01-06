"""
ML Recommendation Service - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.config import settings
from app.api import recommendations, analytics, companies

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

app = FastAPI(
    title="ML Recommendation Service",
    description="Job application recommendations and analytics",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["recommendations"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(companies.router, prefix="/api/v1/companies", tags=["companies"])


@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ml-recommendation-service"}


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("ML Recommendation Service starting up")
    # TODO: Start Kafka consumer in background thread if needed
    # from app.consumers import start_consumer
    # import threading
    # consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    # consumer_thread.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("ML Recommendation Service shutting down")
    # TODO: Close database connections, Kafka consumers, etc.

