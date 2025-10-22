# apps/backend/src/api/health.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, text
from pydantic import BaseModel
from datetime import datetime

from src.core.database import get_session

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    database: str

@router.get("/health", response_model=HealthResponse)
def health_check(session: Session = Depends(get_session)):
    """Health check endpoint"""
    try:
        # Test database connection
        session.exec(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return HealthResponse(
        status="ok" if db_status == "ok" else "degraded",
        timestamp=datetime.utcnow().isoformat(),
        database=db_status
    )
