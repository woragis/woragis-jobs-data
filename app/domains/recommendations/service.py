"""
Recommendation service
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.database.models import Recommendation
from app.domains.recommendations.scoring import OpportunityScorer
from app.cache.redis_cache import RedisCache


class RecommendationService:
    """Service for generating and managing recommendations"""
    
    def __init__(self, db: Session, cache: Optional[RedisCache] = None):
        self.db = db
        self.cache = cache
        self.scorer = OpportunityScorer()
    
    def generate_recommendations(
        self,
        user_id: UUID,
        applications: List[Dict[str, Any]],
        company_metrics: Dict[UUID, Dict[str, Any]],
        user_metrics: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations for a list of applications
        
        Args:
            user_id: User ID
            applications: List of application dicts
            company_metrics: Dict mapping company_id to metrics
            user_metrics: User metrics dict (optional)
        
        Returns:
            List of recommendation dicts with scores
        """
        recommendations = []
        cache_ttl = timedelta(hours=1)  # 1 hour cache
        
        for app in applications:
            app_id = UUID(app['id'])
            company_id = app.get('company_id')
            
            # Get company metrics if available
            comp_metrics = None
            if company_id:
                comp_metrics = company_metrics.get(UUID(company_id))
            
            # Calculate score
            score, explanation = self.scorer.calculate_score(
                app,
                comp_metrics,
                user_metrics
            )
            
            tier = self.scorer.get_tier(score)
            rec_type = self.scorer.get_recommendation_type(app, score)
            
        # Store in database
        recommendation = Recommendation(
            id=UUID(),
            user_id=user_id,
            application_id=app_id,
            opportunity_score=score,
            tier=tier,
            recommendation_type=rec_type,
            explanation=explanation,
            expires_at=datetime.utcnow() + cache_ttl
        )
        self.db.add(recommendation)
        
        rec_dict = {
            "application_id": str(app_id),
            "score": score,
            "tier": tier,
            "type": rec_type,
            "explanation": explanation
        }
        recommendations.append(rec_dict)
        
        self.db.commit()
        
        # Cache in Redis
        if self.cache:
            self.cache.set_recommendations(user_id, recommendations)
        
        return recommendations
    
    def get_cached_recommendations(
        self,
        user_id: UUID,
        limit: int = 10,
        tier: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get cached recommendations for a user"""
        # Try Redis cache first
        if self.cache:
            cached = self.cache.get_recommendations(user_id, limit, tier)
            if cached:
                return cached
        
        # Fallback to database
        query = select(Recommendation).where(
            and_(
                Recommendation.user_id == user_id,
                Recommendation.expires_at > datetime.utcnow()
            )
        )
        
        if tier:
            query = query.where(Recommendation.tier == tier)
        
        query = query.order_by(Recommendation.opportunity_score.desc()).limit(limit)
        
        results = self.db.execute(query).scalars().all()
        
        recommendations = [
            {
                "application_id": str(rec.application_id),
                "score": rec.opportunity_score,
                "tier": rec.tier,
                "type": rec.recommendation_type,
                "explanation": rec.explanation or {}
            }
            for rec in results
        ]
        
        # Cache in Redis
        if self.cache and recommendations:
            self.cache.set_recommendations(user_id, recommendations, tier=tier, limit=limit)
        
        return recommendations

