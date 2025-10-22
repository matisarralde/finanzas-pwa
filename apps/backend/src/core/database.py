# apps/backend/src/core/database.py
from sqlmodel import Session, create_engine
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)

def get_session():
    with Session(engine) as session:
        yield session
