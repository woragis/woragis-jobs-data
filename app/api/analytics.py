"""
Analytics API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.domains.analytics.service import AnalyticsService

router = APIRouter()


@router.get("/{user_id}/overview")
async def get_user_overview(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get user analytics overview"""
    service = AnalyticsService(db)
    overview = service.get_user_overview(user_id)
    return overview


@router.get("/{user_id}/company/{company_id}")
async def get_company_metrics(
    user_id: UUID,
    company_id: UUID,
    db: Session = Depends(get_db)
):
    """Get company-specific metrics for a user"""
    service = AnalyticsService(db)
    metrics = service.get_company_metrics(company_id)
    
    if not metrics:
        raise HTTPException(status_code=404, detail="Company metrics not found")
    
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

