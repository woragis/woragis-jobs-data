"""
Unit tests for recommendation scoring
"""
import pytest
from app.domains.recommendations.scoring import OpportunityScorer


def test_calculate_score_basic():
    """Test basic score calculation"""
    scorer = OpportunityScorer()
    
    application = {
        "id": "test-id",
        "salary_max": 150000,
        "interest_level": "high",
        "interview_count": 2,
    }
    
    score, explanation = scorer.calculate_score(application)
    
    assert 0 <= score <= 100
    assert "total_score" in explanation
    assert "breakdown" in explanation


def test_get_tier():
    """Test tier classification"""
    scorer = OpportunityScorer()
    
    assert scorer.get_tier(95) == "S"
    assert scorer.get_tier(75) == "A"
    assert scorer.get_tier(55) == "B"
    assert scorer.get_tier(30) == "C"


def test_score_salary():
    """Test salary scoring"""
    scorer = OpportunityScorer()
    
    application = {"salary_max": 200000}
    score, _ = scorer._score_salary(application, None)
    
    assert score > 0
    assert score <= 25

