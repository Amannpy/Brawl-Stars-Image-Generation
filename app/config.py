from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Brawl Stars AI Image Generator"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-powered image generator for Brawl Stars content"
    
    # Database
    MONGODB_URL: str
    DATABASE_NAME: str = "brawl_stars_db"
    
    # AI Services
    OPENAI_API_KEY: str
    REPLICATE_API_TOKEN: str
    
    # Social Media APIs
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    TWITTER_BEARER_TOKEN: Optional[str] = None
    
    # Storage
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10
    
    # Caching
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()