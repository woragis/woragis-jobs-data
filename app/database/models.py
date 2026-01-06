"""
Database models for ML service
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from app.database.base import Base
import uuid


class CompanyMetrics(Base):
    """Aggregated company statistics"""
    __tablename__ = "company_metrics"
    
    company_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    total_applications = Column(Integer, default=0)
    avg_response_time_days = Column(Integer, nullable=True)
    avg_time_to_interview_days = Column(Integer, nullable=True)
    avg_interview_count = Column(Float, nullable=True)
    success_rate = Column(Float, nullable=True)  # accepted / total
    avg_salary_min = Column(Integer, nullable=True)
    avg_salary_max = Column(Integer, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_company_metrics_updated', 'last_updated'),
    )


class UserMetrics(Base):
    """User-level statistics"""
    __tablename__ = "user_metrics"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True)
    total_applications = Column(Integer, default=0)
    avg_response_time_days = Column(Integer, nullable=True)
    success_rate = Column(Float, nullable=True)
    avg_salary_range_min = Column(Integer, nullable=True)
    avg_salary_range_max = Column(Integer, nullable=True)
    preferred_company_sizes = Column(ARRAY(String), nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Recommendation(Base):
    """Cached recommendations per user"""
    __tablename__ = "recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    application_id = Column(UUID(as_uuid=True), nullable=False)
    opportunity_score = Column(Integer, nullable=False)  # 0-100
    tier = Column(String(10), nullable=False)  # S, A, B, C
    recommendation_type = Column(String(50), nullable=False)  # hot_opportunity, fast_mover, etc.
    explanation = Column(JSON, nullable=True)  # Score breakdown and factors
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    __table_args__ = (
        Index('idx_user_recommendations', 'user_id', 'created_at'),
        Index('idx_recommendations_expires', 'expires_at'),
    )


class RecommendationHistory(Base):
    """Track what was recommended and user actions (for learning)"""
    __tablename__ = "recommendation_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    application_id = Column(UUID(as_uuid=True), nullable=False)
    recommended_at = Column(DateTime(timezone=True), server_default=func.now())
    user_action = Column(String(50), nullable=True)  # viewed, applied, ignored, etc.
    action_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index('idx_history_user_action', 'user_id', 'user_action'),
    )


class MLModel(Base):
    """ML model metadata and versions"""
    __tablename__ = "ml_models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(100), nullable=False, unique=True)
    model_type = Column(String(50), nullable=False)  # success_prediction, response_time, etc.
    version = Column(String(20), nullable=False)
    file_path = Column(String(255), nullable=False)
    accuracy = Column(Float, nullable=True)
    trained_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(String(10), default='false')  # 'true' or 'false'
    metadata = Column(JSON, nullable=True)  # Model parameters, features, etc.
    
    __table_args__ = (
        Index('idx_models_active', 'model_name', 'is_active'),
    )


class ModelPrediction(Base):
    """Store predictions for analysis"""
    __tablename__ = "model_predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    application_id = Column(UUID(as_uuid=True), nullable=False)
    prediction = Column(JSON, nullable=False)  # Prediction data
    actual_outcome = Column(String(50), nullable=True)  # Filled in later
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_predictions_user', 'user_id', 'created_at'),
    )

