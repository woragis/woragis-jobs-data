"""
Company deduplication and metrics API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

router = APIRouter()


class DeduplicateRequest(BaseModel):
    name: str
    location: str


class DeduplicateResponse(BaseModel):
    company_id: UUID
    matched: bool
    normalized_name: str
    normalized_location: str


@router.post("/deduplicate")
async def deduplicate_company(request: DeduplicateRequest) -> DeduplicateResponse:
    """
    Deduplicate and match a company name and location
    
    Returns the matched company ID or creates a new one
    """
    # TODO: Implement company deduplication
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("/{company_id}/metrics")
async def get_company_metrics(company_id: UUID):
    """Get aggregated metrics for a company"""
    # TODO: Implement company metrics retrieval
    return {
        "company_id": str(company_id),
        "metrics": {}
    }

