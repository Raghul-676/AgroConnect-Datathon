"""
Application configuration settings
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # ML Model Settings
    MODEL_PATH: str = "models/"
    ENABLE_MODEL_TRAINING: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Database (for future use)
    DATABASE_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
