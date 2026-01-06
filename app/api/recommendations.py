"""
Recommendations API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.domains.recommendations.service import RecommendationService

router = APIRouter()


@router.get("/{user_id}")
async def get_recommendations(
    user_id: UUID,
    limit: int = 10,
    tier: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get personalized recommendations for a user
    
    Args:
        user_id: User ID
        limit: Maximum number of recommendations
        tier: Filter by tier (S, A, B, C)
    
    Returns:
        List of recommended applications with scores and explanations
    """
    service = RecommendationService(db)
    recommendations = service.get_cached_recommendations(user_id, limit, tier)
    
    return {
        "recommendations": recommendations,
        "count": len(recommendations)
    }


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

