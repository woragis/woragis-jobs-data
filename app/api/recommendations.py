"""
Recommendations API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.domains.recommendations.service import RecommendationService
from app.domains.analytics.service import AnalyticsService
from app.clients.jobs_client import JobsServiceClient
from app.cache.redis_cache import RedisCache

router = APIRouter()


@router.get("/{user_id}")
async def get_recommendations(
    user_id: UUID,
    limit: int = 10,
    tier: Optional[str] = None,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Get personalized recommendations for a user
    
    Args:
        user_id: User ID
        limit: Maximum number of recommendations
        tier: Filter by tier (S, A, B, C)
        authorization: Bearer token for jobs service
    
    Returns:
        List of recommended applications with scores and explanations
    """
    # Initialize cache and service
    cache = RedisCache()
    rec_service = RecommendationService(db, cache)
    
    # Try to get cached recommendations first
    cached = rec_service.get_cached_recommendations(user_id, limit, tier)
    
    if cached and len(cached) >= limit:
        return {
            "recommendations": cached,
            "count": len(cached),
            "source": "cache"
        }
    
    # If not enough cached, fetch from jobs service and generate new recommendations
    token = authorization.replace("Bearer ", "") if authorization else None
    jobs_client = JobsServiceClient()
    
    try:
        applications = await jobs_client.get_user_applications(user_id, token)
        
        if not applications:
            return {
                "recommendations": cached,
                "count": len(cached),
                "source": "cache"
            }
        
        # Get company metrics
        analytics_service = AnalyticsService(db)
        company_metrics = {}
        for app in applications:
            company_id = app.get('company_id')
            if company_id:
                comp_metrics = analytics_service.get_company_metrics(UUID(company_id))
                if comp_metrics:
                    company_metrics[UUID(company_id)] = comp_metrics
        
        # Get user metrics
        user_metrics = analytics_service.get_user_overview(user_id)
        
        # Generate recommendations
        recommendations = rec_service.generate_recommendations(
            user_id,
            applications,
            company_metrics,
            user_metrics
        )
        
        return {
            "recommendations": recommendations[:limit],
            "count": len(recommendations),
            "source": "generated"
        }
    finally:
        await jobs_client.close()


@router.get("/{user_id}/hot-opportunities")
async def get_hot_opportunities(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get top hot opportunities for a user"""
    service = RecommendationService(db)
    recommendations = service.get_cached_recommendations(user_id, limit=10, tier="S")
    
    # Filter for hot opportunities
    hot_ops = [r for r in recommendations if r.get("type") == "hot_opportunity"]
    
    return {"opportunities": hot_ops}


@router.get("/{user_id}/needs-attention")
async def get_needs_attention(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """Get applications that need user attention"""
    service = RecommendationService(db)
    recommendations = service.get_cached_recommendations(user_id, limit=20)
    
    # Filter for needs attention
    needs_attention = [r for r in recommendations if r.get("type") == "needs_attention"]
    
    return {"applications": needs_attention}

