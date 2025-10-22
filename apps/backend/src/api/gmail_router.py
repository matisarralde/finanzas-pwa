# apps/backend/src/api/gmail.py
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlmodel import Session
from pydantic import BaseModel
from typing import Optional
import logging

from src.core.database import get_session
from src.core.auth_jwt import require_admin
from src.core.config import settings
from src.services.ingest import IngestService

router = APIRouter()
logger = logging.getLogger(__name__)

class WebhookPayload(BaseModel):
    historyId: str
    emailAddress: Optional[str] = None

class IngestResponse(BaseModel):
    processed: int
    created: int
    duplicates: int
    failed: int
    history_id: Optional[str]

@router.post("/webhook")
async def gmail_webhook(
    payload: WebhookPayload,
    x_webhook_secret: Optional[str] = Header(None),
    session: Session = Depends(get_session)
):
    """Receive Gmail push notifications"""
    # Validate webhook secret
    if x_webhook_secret != settings.GMAIL_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook secret"
        )
    
    logger.info(f"Received webhook with historyId: {payload.historyId}")
    
    # TODO: Queue background job to process this historyId
    # For now, just acknowledge
    return {"status": "received", "historyId": payload.historyId}

@router.post("/ingest/run", response_model=IngestResponse)
def run_ingest(
    credentials: dict,
    history_id: Optional[str] = None,
    user_id: str = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Manual/forced ingestion of Gmail transactions.
    Requires admin access.
    
    credentials format:
    {
        "token": "...",
        "refresh_token": "...",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "...",
        "client_secret": "...",
        "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
    }
    """
    try:
        ingest_service = IngestService(session)
        result = ingest_service.process_emails(
            user_id=user_id,
            gmail_credentials=credentials,
            history_id=history_id
        )
        
        logger.info(f"Ingest completed: {result}")
        
        return IngestResponse(**result)
        
    except Exception as e:
        logger.error(f"Ingest failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}"
        )
