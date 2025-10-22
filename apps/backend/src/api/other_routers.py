# apps/backend/src/api/budgets.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from pydantic import BaseModel
from datetime import date

from src.core.database import get_session
from src.core.auth_jwt import get_current_user_id
from src.core.errors import NotFoundError
from src.models.models import Budget, BudgetPeriod

router = APIRouter()

class BudgetCreate(BaseModel):
    name: str
    amount: float
    category_id: int
    start_month: date

@router.get("")
def list_budgets(
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    return session.exec(select(Budget).where(Budget.user_id == user_id)).all()

@router.post("", status_code=201)
def create_budget(
    data: BudgetCreate,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    budget = Budget(user_id=user_id, **data.dict())
    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget

# apps/backend/src/api/categories.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional

from src.core.database import get_session
from src.core.auth_jwt import get_current_user_id
from src.models.models import Category

router = APIRouter()

class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None

@router.get("")
def list_categories(
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    # Include global categories (user_id is NULL) and user's own
    return session.exec(
        select(Category).where(
            (Category.user_id == user_id) | (Category.user_id == None)
        )
    ).all()

@router.post("", status_code=201)
def create_category(
    data: CategoryCreate,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    category = Category(user_id=user_id, **data.dict())
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

# apps/backend/src/api/accounts.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional

from src.core.database import get_session
from src.core.auth_jwt import get_current_user_id
from src.models.models import Account, AccountType

router = APIRouter()

class AccountCreate(BaseModel):
    name: str
    institution: str
    type: AccountType
    currency: str = "CLP"

@router.get("")
def list_accounts(
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    return session.exec(select(Account).where(Account.user_id == user_id)).all()

@router.post("", status_code=201)
def create_account(
    data: AccountCreate,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    account = Account(user_id=user_id, **data.dict())
    session.add(account)
    session.commit()
    session.refresh(account)
    return account

# apps/backend/src/api/rules.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List
import re
import logging

from src.core.database import get_session
from src.core.auth_jwt import get_current_user_id
from src.models.models import Rule, Transaction

router = APIRouter()
logger = logging.getLogger(__name__)

class RuleCreate(BaseModel):
    pattern: str
    field: str  # merchant, description, amount
    action: str  # set_category, set_subcategory
    value: str
    priority: int = 0

class ApplyRulesResponse(BaseModel):
    updated: int

@router.get("")
def list_rules(
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    return session.exec(
        select(Rule).where(Rule.user_id == user_id).order_by(Rule.priority.desc())
    ).all()

@router.post("", status_code=201)
def create_rule(
    data: RuleCreate,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    rule = Rule(user_id=user_id, **data.dict())
    session.add(rule)
    session.commit()
    session.refresh(rule)
    return rule

@router.post("/apply", response_model=ApplyRulesResponse)
def apply_rules(
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """Apply all rules to existing transactions"""
    rules = session.exec(
        select(Rule).where(Rule.user_id == user_id).order_by(Rule.priority.desc())
    ).all()
    
    transactions = session.exec(
        select(Transaction).where(Transaction.user_id == user_id)
    ).all()
    
    updated = 0
    
    for txn in transactions:
        for rule in rules:
            # Get field value
            field_value = getattr(txn, rule.field, None)
            if not field_value:
                continue
            
            # Check if pattern matches
            if re.search(rule.pattern, str(field_value), re.IGNORECASE):
                # Apply action
                if rule.action == "set_category":
                    txn.category_id = int(rule.value)
                    updated += 1
                elif rule.action == "set_subcategory":
                    txn.subcategory_id = int(rule.value)
                    updated += 1
                
                break  # Apply only first matching rule
    
    session.commit()
    logger.info(f"Applied rules, updated {updated} transactions")
    
    return ApplyRulesResponse(updated=updated)
