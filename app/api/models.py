"""
ML Models API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.domains.models.service import MLModelsService
from app.clients.jobs_client import JobsServiceClient

router = APIRouter()


@router.post("/train")
async def train_models(
    user_id: UUID,
    version: str = "1.0.0",
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """
    Train ML models with user's application data
    
    Args:
        user_id: User ID
        version: Model version
        authorization: Bearer token for jobs service
    """
    service = MLModelsService(db)
    token = authorization.replace("Bearer ", "") if authorization else None
    jobs_client = JobsServiceClient()
    
    try:
        # Fetch applications
        applications = await jobs_client.get_user_applications(user_id, token)
        
        if len(applications) < 10:
            raise HTTPException(
                status_code=400,
                detail="Need at least 10 applications to train models"
            )
        
        # Train models
        results = service.train_models(applications, version)
        
        return {
            "success": True,
            "results": results,
            "message": "Models trained successfully"
        }
    finally:
        await jobs_client.close()


@router.post("/predict/success/{application_id}")
async def predict_success(
    application_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Predict success for an application"""
    service = MLModelsService(db)
    token = authorization.replace("Bearer ", "") if authorization else None
    jobs_client = JobsServiceClient()
    
    try:
        application = await jobs_client.get_application(application_id, token)
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        prediction = service.predict_application_success(application, user_id, application_id)
        
        return {
            "success": True,
            "prediction": prediction
        }
    finally:
        await jobs_client.close()


@router.post("/predict/response-time/{application_id}")
async def predict_response_time(
    application_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    """Predict response time for an application"""
    service = MLModelsService(db)
    token = authorization.replace("Bearer ", "") if authorization else None
    jobs_client = JobsServiceClient()
    
    try:
        application = await jobs_client.get_application(application_id, token)
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        prediction = service.predict_response_time(application, user_id, application_id)
        
        return {
            "success": True,
            "prediction": prediction
        }
    finally:
        await jobs_client.close()

