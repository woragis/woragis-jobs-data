"""
Company deduplication service
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database.models import CompanyMetrics
from app.domains.company_dedup.normalizer import (
    normalize_company_name,
    normalize_location,
    match_company
)


class CompanyDeduplicationService:
    """Service for company deduplication and matching"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_or_create_company(
        self,
        company_name: str,
        location: str,
        company_size: Optional[str] = None
    ) -> tuple[UUID, bool]:
        """
        Find existing company or create new one
        
        Returns:
            Tuple of (company_id, is_new)
        """
        normalized_name = normalize_company_name(company_name)
        normalized_location = normalize_location(location)
        
        if not normalized_name:
            # Can't create company without name
            raise ValueError("Company name is required")
        
        # Get all existing companies
        existing = self.db.execute(
            select(CompanyMetrics).where(
                CompanyMetrics.company_id.isnot(None)
            )
        ).scalars().all()
        
        existing_companies = [
            {
                'company_id': str(comp.company_id),
                'normalized_name': getattr(comp, 'normalized_name', ''),
                'normalized_location': getattr(comp, 'normalized_location', '')
            }
            for comp in existing
        ]
        
        # Try to match
        matched_id, matched = match_company(
            company_name,
            location,
            existing_companies
        )
        
        if matched and matched_id:
            return UUID(matched_id), False
        
        # Create new company
        new_company = CompanyMetrics(
            company_id=UUID(),
            total_applications=0
        )
        # Store normalized values (we'll need to add these columns)
        # For now, we'll match based on metrics table
        self.db.add(new_company)
        self.db.commit()
        self.db.refresh(new_company)
        
        return new_company.company_id, True

