"""
Redis cache implementation for recommendations
"""
import json
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import timedelta
import redis
import structlog
from app.config import settings

logger = structlog.get_logger()


class RedisCache:
    """Redis cache for recommendations and metrics"""
    
    def __init__(self):
        try:
            self.client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            # Test connection
            self.client.ping()
            logger.info("Redis cache connected")
        except Exception as e:
            logger.warning("Redis not available, caching disabled", error=str(e))
            self.client = None
    
    def _key(self, prefix: str, *args) -> str:
        """Generate cache key"""
        parts = [prefix] + [str(arg) for arg in args]
        return ":".join(parts)
    
    def get_recommendations(
        self,
        user_id: UUID,
        limit: int = 10,
        tier: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Get cached recommendations"""
        if not self.client:
            return None
        
        try:
            key = self._key("recommendations", user_id, tier or "all", limit)
            data = self.client.get(key)
            
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error("Error getting recommendations from cache", error=str(e))
            return None
    
    def set_recommendations(
        self,
        user_id: UUID,
        recommendations: List[Dict[str, Any]],
        ttl: int = None,
        tier: Optional[str] = None,
        limit: int = 10
    ):
        """Cache recommendations"""
        if not self.client:
            return
        
        try:
            ttl = ttl or settings.RECOMMENDATION_CACHE_TTL
            key = self._key("recommendations", user_id, tier or "all", limit)
            self.client.setex(
                key,
                ttl,
                json.dumps(recommendations)
            )
            logger.debug("Cached recommendations", user_id=str(user_id), count=len(recommendations))
        except Exception as e:
            logger.error("Error caching recommendations", error=str(e))
    
    def get_company_metrics(self, company_id: UUID) -> Optional[Dict[str, Any]]:
        """Get cached company metrics"""
        if not self.client:
            return None
        
        try:
            key = self._key("company_metrics", company_id)
            data = self.client.get(key)
            
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error("Error getting company metrics from cache", error=str(e))
            return None
    
    def set_company_metrics(
        self,
        company_id: UUID,
        metrics: Dict[str, Any],
        ttl: int = 3600
    ):
        """Cache company metrics"""
        if not self.client:
            return
        
        try:
            key = self._key("company_metrics", company_id)
            self.client.setex(
                key,
                ttl,
                json.dumps(metrics)
            )
        except Exception as e:
            logger.error("Error caching company metrics", error=str(e))
    
    def get_user_metrics(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get cached user metrics"""
        if not self.client:
            return None
        
        try:
            key = self._key("user_metrics", user_id)
            data = self.client.get(key)
            
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error("Error getting user metrics from cache", error=str(e))
            return None
    
    def set_user_metrics(
        self,
        user_id: UUID,
        metrics: Dict[str, Any],
        ttl: int = 1800
    ):
        """Cache user metrics"""
        if not self.client:
            return
        
        try:
            key = self._key("user_metrics", user_id)
            self.client.setex(
                key,
                ttl,
                json.dumps(metrics)
            )
        except Exception as e:
            logger.error("Error caching user metrics", error=str(e))
    
    def invalidate_user(self, user_id: UUID):
        """Invalidate all cache for a user"""
        if not self.client:
            return
        
        try:
            pattern = self._key("recommendations", user_id, "*")
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
            
            pattern = self._key("user_metrics", user_id)
            self.client.delete(pattern)
            
            logger.debug("Invalidated cache for user", user_id=str(user_id))
        except Exception as e:
            logger.error("Error invalidating user cache", error=str(e))
    
    def invalidate_company(self, company_id: UUID):
        """Invalidate cache for a company"""
        if not self.client:
            return
        
        try:
            key = self._key("company_metrics", company_id)
            self.client.delete(key)
        except Exception as e:
            logger.error("Error invalidating company cache", error=str(e))

