"""
Opportunity score calculation for job applications
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID


class OpportunityScorer:
    """Calculate opportunity scores for job applications"""
    
    @staticmethod
    def calculate_score(
        application: Dict[str, Any],
        company_metrics: Optional[Dict[str, Any]] = None,
        user_metrics: Optional[Dict[str, Any]] = None
    ) -> tuple[int, Dict[str, Any]]:
        """
        Calculate opportunity score (0-100) and explanation
        
        Args:
            application: Application data dict
            company_metrics: Company metrics dict (optional)
            user_metrics: User metrics dict (optional)
        
        Returns:
            Tuple of (score, explanation_dict)
        """
        score = 0
        explanation = {
            "factors": [],
            "breakdown": {}
        }
        
        # Response speed (0-25 points)
        response_score, response_explanation = OpportunityScorer._score_response_speed(
            application, company_metrics
        )
        score += response_score
        explanation["breakdown"]["response_speed"] = response_score
        if response_explanation:
            explanation["factors"].append(response_explanation)
        
        # Salary range (0-25 points)
        salary_score, salary_explanation = OpportunityScorer._score_salary(
            application, user_metrics
        )
        score += salary_score
        explanation["breakdown"]["salary"] = salary_score
        if salary_explanation:
            explanation["factors"].append(salary_explanation)
        
        # Interest level (0-20 points)
        interest_score, interest_explanation = OpportunityScorer._score_interest(
            application
        )
        score += interest_score
        explanation["breakdown"]["interest"] = interest_score
        if interest_explanation:
            explanation["factors"].append(interest_explanation)
        
        # Interview progression (0-20 points)
        interview_score, interview_explanation = OpportunityScorer._score_interviews(
            application
        )
        score += interview_score
        explanation["breakdown"]["interviews"] = interview_score
        if interview_explanation:
            explanation["factors"].append(interview_explanation)
        
        # Time sensitivity (0-10 points)
        deadline_score, deadline_explanation = OpportunityScorer._score_deadline(
            application
        )
        score += deadline_score
        explanation["breakdown"]["deadline"] = deadline_score
        if deadline_explanation:
            explanation["factors"].append(deadline_explanation)
        
        # Cap at 100
        final_score = min(100, score)
        explanation["total_score"] = final_score
        
        return final_score, explanation
    
    @staticmethod
    def _score_response_speed(
        application: Dict[str, Any],
        company_metrics: Optional[Dict[str, Any]]
    ) -> tuple[int, Optional[str]]:
        """Score based on response speed (0-25 points)"""
        response_time = application.get('response_time_days')
        if response_time is None:
            return 0, None
        
        if company_metrics and company_metrics.get('avg_response_time_days'):
            avg_time = company_metrics['avg_response_time_days']
            if response_time < avg_time:
                # Faster than average - bonus points
                diff = avg_time - response_time
                score = min(25, 20 + (diff * 2))
                return int(score), f"Response {diff} days faster than average"
            else:
                # Slower than average - penalty
                diff = response_time - avg_time
                score = max(0, 20 - (diff * 2))
                return int(score), f"Response {diff} days slower than average"
        
        # No company average, use absolute scale
        if response_time <= 3:
            return 25, "Very fast response (≤3 days)"
        elif response_time <= 7:
            return 20, "Fast response (4-7 days)"
        elif response_time <= 14:
            return 15, "Average response (8-14 days)"
        elif response_time <= 21:
            return 10, "Slow response (15-21 days)"
        else:
            return 5, "Very slow response (>21 days)"
    
    @staticmethod
    def _score_salary(
        application: Dict[str, Any],
        user_metrics: Optional[Dict[str, Any]]
    ) -> tuple[int, Optional[str]]:
        """Score based on salary range (0-25 points)"""
        salary_max = application.get('salary_max')
        if salary_max is None:
            return 0, None
        
        # Normalize to 0-25 scale (assuming max reasonable salary is 200k)
        base_score = min(25, (salary_max / 200000) * 25)
        
        # Bonus if above user's average
        if user_metrics and user_metrics.get('avg_salary_range_max'):
            user_avg = user_metrics['avg_salary_range_max']
            if salary_max > user_avg:
                bonus = min(5, ((salary_max - user_avg) / 10000) * 1)
                base_score = min(25, base_score + bonus)
                return int(base_score), f"Salary above your average (${salary_max:,} vs ${user_avg:,})"
        
        return int(base_score), f"Salary range: ${application.get('salary_min', 0):,} - ${salary_max:,}"
    
    @staticmethod
    def _score_interest(
        application: Dict[str, Any]
    ) -> tuple[int, Optional[str]]:
        """Score based on interest level (0-20 points)"""
        interest_level = application.get('interest_level', '').lower()
        
        interest_scores = {
            'very-high': (20, "Very high interest"),
            'high': (15, "High interest"),
            'medium': (10, "Medium interest"),
            'low': (5, "Low interest"),
        }
        
        score, explanation = interest_scores.get(interest_level, (0, None))
        return score, explanation
    
    @staticmethod
    def _score_interviews(
        application: Dict[str, Any]
    ) -> tuple[int, Optional[str]]:
        """Score based on interview progression (0-20 points)"""
        interview_count = application.get('interview_count', 0)
        
        # More interviews = higher score (up to 20 points)
        score = min(20, interview_count * 5)
        
        if interview_count > 0:
            return score, f"{interview_count} interview(s) completed"
        return score, None
    
    @staticmethod
    def _score_deadline(
        application: Dict[str, Any]
    ) -> tuple[int, Optional[str]]:
        """Score based on deadline urgency (0-10 points)"""
        deadline_str = application.get('deadline')
        if not deadline_str:
            return 0, None
        
        try:
            if isinstance(deadline_str, str):
                deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
            else:
                deadline = deadline_str
            
            now = datetime.now(deadline.tzinfo) if deadline.tzinfo else datetime.now()
            days_until = (deadline - now).days
            
            if days_until < 0:
                return 0, "Deadline passed"
            elif 0 <= days_until <= 7:
                return 10, f"Deadline in {days_until} days (urgent)"
            elif 8 <= days_until <= 14:
                return 5, f"Deadline in {days_until} days"
            else:
                return 0, None
        except (ValueError, AttributeError):
            return 0, None
    
    @staticmethod
    def get_tier(score: int) -> str:
        """Get tier classification based on score"""
        if score >= 90:
            return "S"
        elif score >= 70:
            return "A"
        elif score >= 50:
            return "B"
        else:
            return "C"
    
    @staticmethod
    def get_recommendation_type(
        application: Dict[str, Any],
        score: int
    ) -> str:
        """Determine recommendation type"""
        if score >= 90:
            return "hot_opportunity"
        elif application.get('interview_count', 0) > 0:
            return "fast_mover"
        elif application.get('salary_max', 0) > 150000:
            return "high_value"
        elif application.get('response_time_days') is None:
            return "needs_attention"
        else:
            return "standard"

