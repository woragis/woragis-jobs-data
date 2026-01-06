"""
Company deduplication and metrics API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.domains.company_dedup.service import CompanyDeduplicationService
from app.domains.company_dedup.normalizer import normalize_company_name, normalize_location
from app.domains.analytics.service import AnalyticsService

router = APIRouter()


class DeduplicateRequest(BaseModel):
    name: str
    location: str
    company_size: Optional[str] = None


class DeduplicateResponse(BaseModel):
    company_id: UUID
    matched: bool
    normalized_name: str
    normalized_location: str


@router.post("/deduplicate", response_model=DeduplicateResponse)
async def deduplicate_company(
    request: DeduplicateRequest,
    db: Session = Depends(get_db)
) -> DeduplicateResponse:
    """
    Deduplicate and match a company name and location
    
    Returns the matched company ID or creates a new one
    """
    service = CompanyDeduplicationService(db)
    company_id, is_new = service.find_or_create_company(
        request.name,
        request.location,
        request.company_size
    )
    
    return DeduplicateResponse(
        company_id=company_id,
        matched=not is_new,
        normalized_name=normalize_company_name(request.name),
        normalized_location=normalize_location(request.location)
    )


@router.get("/{company_id}/metrics")
async def get_company_metrics(
    company_id: UUID,
    db: Session = Depends(get_db)
):
    """Get aggregated metrics for a company"""
    service = AnalyticsService(db)
    metrics = service.get_company_metrics(company_id)
    
    if not metrics:
        raise HTTPException(status_code=404, detail="Company metrics not found")
    
    return metrics

