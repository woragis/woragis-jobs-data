"""
Configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    ML_DATABASE_URL: str = "postgresql://woragis:password@localhost:5450/ml_service"
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_GROUP_ID: str = "ml-recommendation-service"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6398/1"
    
    # API
    ML_SERVICE_PORT: int = 3020
    ML_SERVICE_HOST: str = "0.0.0.0"
    
    # Features
    ENABLE_ML_MODELS: bool = True
    RECOMMENDATION_CACHE_TTL: int = 3600
    
    # External Services
    AUTH_SERVICE_URL: str = "http://localhost:3010"
    JOBS_SERVICE_URL: str = "http://localhost:3011"
    
    # CORS
    CORS_ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

