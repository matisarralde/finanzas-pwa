# apps/backend/scripts/seed.py
"""Seed database with initial categories and demo data"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sqlmodel import Session, select
from src.core.database import engine
from src.models.models import Category, User, Account
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_categories(session: Session):
    """Create default categories (global, user_id=NULL)"""
    categories = [
        {"name": "Gustos", "parent_id": None},
        {"name": "Necesidades", "parent_id": None},
        {"name": "Inversiones", "parent_id": None},
        {"name": "Deudas/Préstamos", "parent_id": None},
        {"name": "Ingresos", "parent_id": None},
        # Subcategories
        {"name": "Alimentación", "parent_name": "Necesidades"},
        {"name": "Transporte", "parent_name": "Necesidades"},
        {"name": "Salud", "parent_name": "Necesidades"},
        {"name": "Vivienda", "parent_name": "Necesidades"},
        {"name": "Entretenimiento", "parent_name": "Gustos"},
        {"name": "Restaurantes", "parent_name": "Gustos"},
        {"name": "Compras", "parent_name": "Gustos"},
        {"name": "Ahorro", "parent_name": "Inversiones"},
        {"name": "Acciones", "parent_name": "Inversiones"},
        {"name": "Fondos", "parent_name": "Inversiones"},
    ]
    
    # Create parent categories first
    parent_map = {}
    for cat_data in categories:
        if "parent_name" not in cat_data:
            existing = session.exec(
                select(Category).where(
                    Category.name == cat_data["name"],
                    Category.user_id == None
                )
            ).first()
            
            if not existing:
                cat = Category(
                    name=cat_data["name"],
                    user_id=None,
                    parent_id=None
                )
                session.add(cat)
                session.commit()
                session.refresh(cat)
                parent_map[cat.name] = cat.id
                logger.info(f"Created category: {cat.name}")
            else:
                parent_map[existing.name] = existing.id
    
    # Create subcategories
    for cat_data in categories:
        if "parent_name" in cat_data:
            parent_id = parent_map.get(cat_data["parent_name"])
            if parent_id:
                existing = session.exec(
                    select(Category).where(
                        Category.name == cat_data["name"],
                        Category.parent_id == parent_id,
                        Category.user_id == None
                    )
                ).first()
                
                if not existing:
                    cat = Category(
                        name=cat_data["name"],
                        user_id=None,
                        parent_id=parent_id
                    )
                    session.add(cat)
                    session.commit()
                    logger.info(f"Created subcategory: {cat.name}")

def seed_demo_user(session: Session):
    """Create demo user and account"""
    demo_user_id = "demo-user-123"
    
    existing_user = session.get(User, demo_user_id)
    if not existing_user:
        user = User(
            id=demo_user_id,
            email="demo@example.com"
        )
        session.add(user)
        session.commit()
        logger.info(f"Created demo user: {user.email}")
    
    # Create demo account
    existing_account = session.exec(
        select(Account).where(
            Account.user_id == demo_user_id,
            Account.name == "Cuenta Demo"
        )
    ).first()
    
    if not existing_account:
        account = Account(
            user_id=demo_user_id,
            name="Cuenta Demo",
            institution="demo",
            type="credit",
            currency="CLP"
        )
        session.add(account)
        session.commit()
        logger.info(f"Created demo account")

def main():
    with Session(engine) as session:
        logger.info("Starting database seed...")
        seed_categories(session)
        seed_demo_user(session)
        logger.info("Seed completed successfully!")

if __name__ == "__main__":
    main()
