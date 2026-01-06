"""
Analytics API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.domains.analytics.service import AnalyticsService
from app.clients.jobs_client import JobsServiceClient
from app.cache.redis_cache import RedisCache

router = APIRouter()


@router.get("/{user_id}/overview")
async def get_user_overview(
    user_id: UUID,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Get user analytics overview"""
    cache = RedisCache()
    service = AnalyticsService(db)
    
    # Try Redis cache first
    cached = cache.get_user_metrics(user_id)
    if cached:
        return cached
    
    # Try to get from database
    overview = service.get_user_overview(user_id)
    
    # If no data or stale, fetch from jobs service and update
    if overview["total_applications"] == 0:
        token = authorization.replace("Bearer ", "") if authorization else None
        jobs_client = JobsServiceClient()
        
        try:
            applications = await jobs_client.get_user_applications(user_id, token)
            if applications:
                # Update metrics
                service.update_user_metrics(user_id, applications)
                overview = service.get_user_overview(user_id)
                # Cache the updated metrics
                cache.set_user_metrics(user_id, overview)
        finally:
            await jobs_client.close()
    
    return overview


@router.get("/{user_id}/company/{company_id}")
async def get_company_metrics(
    user_id: UUID,
    company_id: UUID,
    db: Session = Depends(get_db)
):
    """Get company-specific metrics for a user"""
    cache = RedisCache()
    service = AnalyticsService(db)
    
    # Try Redis cache first
    cached = cache.get_company_metrics(company_id)
    if cached:
        return cached
    
    # Get from database
    metrics = service.get_company_metrics(company_id)
    
    if not metrics:
        raise HTTPException(status_code=404, detail="Company metrics not found")
    
    # Cache the metrics
    cache.set_company_metrics(company_id, metrics)
    
    return metrics


@router.get("/{user_id}/trends")
async def get_user_trends(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get time-series trends for a user"""
    # TODO: Implement trends with time-series data
    # For now, return empty trends
    return {
        "trends": [],
        "message": "Trends feature coming soon"
    }

