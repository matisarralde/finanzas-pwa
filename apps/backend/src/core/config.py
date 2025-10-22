# apps/backend/src/core/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Supabase Auth
    SUPABASE_URL: str
    SUPABASE_JWT_SECRET: str
    
    # Google/Gmail
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GMAIL_WEBHOOK_SECRET: str
    
    # App
    TZ: str = "America/Santiago"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Admin users (for /gmail/ingest/run)
    ADMIN_USER_IDS: List[str] = []
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
