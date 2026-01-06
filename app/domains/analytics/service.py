"""
Analytics service for calculating metrics
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from app.database.models import CompanyMetrics, UserMetrics


class AnalyticsService:
    """Service for calculating and storing analytics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def update_company_metrics(
        self,
        company_id: UUID,
        applications: List[Dict[str, Any]]
    ) -> CompanyMetrics:
        """
        Update aggregated metrics for a company
        
        Args:
            company_id: Company ID
            applications: List of application dicts for this company
        
        Returns:
            Updated CompanyMetrics object
        """
        # Get or create company metrics
        metrics = self.db.get(CompanyMetrics, company_id)
        if not metrics:
            metrics = CompanyMetrics(company_id=company_id)
            self.db.add(metrics)
        
        if not applications:
            metrics.total_applications = 0
            self.db.commit()
            return metrics
        
        # Calculate metrics
        response_times = [
            app.get('response_time_days')
            for app in applications
            if app.get('response_time_days') is not None
        ]
        
        interview_times = [
            app.get('time_to_interview_days')
            for app in applications
            if app.get('time_to_interview_days') is not None
        ]
        
        interview_counts = [
            app.get('interview_count', 0)
            for app in applications
        ]
        
        salaries_min = [
            app.get('salary_min')
            for app in applications
            if app.get('salary_min') is not None
        ]
        
        salaries_max = [
            app.get('salary_max')
            for app in applications
            if app.get('salary_max') is not None
        ]
        
        # Count success (accepted)
        total = len(applications)
        accepted = sum(1 for app in applications if app.get('status') == 'accepted')
        
        # Update metrics
        metrics.total_applications = total
        metrics.avg_response_time_days = int(sum(response_times) / len(response_times)) if response_times else None
        metrics.avg_time_to_interview_days = int(sum(interview_times) / len(interview_times)) if interview_times else None
        metrics.avg_interview_count = sum(interview_counts) / len(interview_counts) if interview_counts else None
        metrics.success_rate = accepted / total if total > 0 else None
        metrics.avg_salary_min = int(sum(salaries_min) / len(salaries_min)) if salaries_min else None
        metrics.avg_salary_max = int(sum(salaries_max) / len(salaries_max)) if salaries_max else None
        metrics.last_updated = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(metrics)
        return metrics
    
    def update_user_metrics(
        self,
        user_id: UUID,
        applications: List[Dict[str, Any]]
    ) -> UserMetrics:
        """
        Update aggregated metrics for a user
        
        Args:
            user_id: User ID
            applications: List of application dicts for this user
        
        Returns:
            Updated UserMetrics object
        """
        # Get or create user metrics
        metrics = self.db.get(UserMetrics, user_id)
        if not metrics:
            metrics = UserMetrics(user_id=user_id)
            self.db.add(metrics)
        
        if not applications:
            metrics.total_applications = 0
            self.db.commit()
            return metrics
        
        # Calculate metrics
        response_times = [
            app.get('response_time_days')
            for app in applications
            if app.get('response_time_days') is not None
        ]
        
        salaries_min = [
            app.get('salary_min')
            for app in applications
            if app.get('salary_min') is not None
        ]
        
        salaries_max = [
            app.get('salary_max')
            for app in applications
            if app.get('salary_max') is not None
        ]
        
        # Count success
        total = len(applications)
        accepted = sum(1 for app in applications if app.get('status') == 'accepted')
        
        # Get preferred company sizes (most common)
        company_sizes = [
            app.get('company_size')
            for app in applications
            if app.get('company_size')
        ]
        from collections import Counter
        size_counts = Counter(company_sizes)
        preferred_sizes = [size for size, _ in size_counts.most_common(3)]
        
        # Update metrics
        metrics.total_applications = total
        metrics.avg_response_time_days = int(sum(response_times) / len(response_times)) if response_times else None
        metrics.success_rate = accepted / total if total > 0 else None
        metrics.avg_salary_range_min = int(sum(salaries_min) / len(salaries_min)) if salaries_min else None
        metrics.avg_salary_range_max = int(sum(salaries_max) / len(salaries_max)) if salaries_max else None
        metrics.preferred_company_sizes = preferred_sizes if preferred_sizes else None
        metrics.last_updated = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(metrics)
        return metrics
    
    def get_user_overview(
        self,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Get user analytics overview"""
        metrics = self.db.get(UserMetrics, user_id)
        
        if not metrics:
            return {
                "total_applications": 0,
                "success_rate": 0.0,
                "avg_response_time": 0,
                "insights": []
            }
        
        insights = []
        
        if metrics.avg_response_time_days:
            if metrics.avg_response_time_days <= 7:
                insights.append("You're getting fast responses from companies")
            elif metrics.avg_response_time_days > 21:
                insights.append("Consider following up on applications after 2 weeks")
        
        if metrics.success_rate:
            if metrics.success_rate >= 0.3:
                insights.append("Great success rate! Keep applying to similar opportunities")
            elif metrics.success_rate < 0.1:
                insights.append("Consider diversifying your application strategy")
        
        return {
            "total_applications": metrics.total_applications,
            "success_rate": float(metrics.success_rate) if metrics.success_rate else 0.0,
            "avg_response_time": metrics.avg_response_time_days or 0,
            "avg_salary_range": {
                "min": metrics.avg_salary_range_min,
                "max": metrics.avg_salary_range_max
            },
            "preferred_company_sizes": metrics.preferred_company_sizes or [],
            "insights": insights
        }
    
    def get_company_metrics(
        self,
        company_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get company metrics"""
        metrics = self.db.get(CompanyMetrics, company_id)
        
        if not metrics:
            return None
        
        return {
            "company_id": str(company_id),
            "total_applications": metrics.total_applications,
            "avg_response_time_days": metrics.avg_response_time_days,
            "avg_time_to_interview_days": metrics.avg_time_to_interview_days,
            "avg_interview_count": float(metrics.avg_interview_count) if metrics.avg_interview_count else None,
            "success_rate": float(metrics.success_rate) if metrics.success_rate else None,
            "avg_salary_range": {
                "min": metrics.avg_salary_min,
                "max": metrics.avg_salary_max
            },
            "last_updated": metrics.last_updated.isoformat() if metrics.last_updated else None
        }

