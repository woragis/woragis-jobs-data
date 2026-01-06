"""
Client for communicating with jobs service
"""
import httpx
from typing import List, Dict, Any, Optional
from uuid import UUID
import structlog
from app.config import settings

logger = structlog.get_logger()


class JobsServiceClient:
    """Client for fetching data from jobs service"""
    
    def __init__(self):
        self.base_url = settings.JOBS_SERVICE_URL
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0
        )
    
    async def get_user_applications(
        self,
        user_id: UUID,
        token: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch all applications for a user
        
        Args:
            user_id: User ID
            token: JWT token for authentication (optional for now)
        
        Returns:
            List of application dicts
        """
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            response = await self.client.get(
                "/api/v1/job-applications",
                headers=headers,
                params={"userId": str(user_id)}
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("success") and "data" in data:
                applications = data["data"].get("applications", [])
                logger.info(
                    "Fetched applications",
                    user_id=str(user_id),
                    count=len(applications)
                )
                return applications
            
            return []
        except httpx.HTTPError as e:
            logger.error(
                "Error fetching applications",
                user_id=str(user_id),
                error=str(e)
            )
            return []
    
    async def get_application(
        self,
        application_id: UUID,
        token: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch a single application by ID"""
        try:
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            response = await self.client.get(
                f"/api/v1/job-applications/{application_id}",
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get("success") and "data" in data:
                return data["data"].get("application")
            
            return None
        except httpx.HTTPError as e:
            logger.error(
                "Error fetching application",
                application_id=str(application_id),
                error=str(e)
            )
            return None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

