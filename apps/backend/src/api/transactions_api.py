# apps/backend/src/api/transactions.py
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from typing import Optional, List
from datetime import date
import hashlib

from src.core.database import get_session
from src.core.auth_jwt import get_current_user_id
from src.core.errors import NotFoundError
from src.models.models import Transaction, TransactionSource
from pydantic import BaseModel

router = APIRouter()

class TransactionCreate(BaseModel):
    account_id: int
    txn_date: date
    amount: float
    currency: str = "CLP"
    description: str
    merchant: Optional[str] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    payment_method: Optional[str] = None
    is_transfer: bool = False

class TransactionResponse(BaseModel):
    id: int
    account_id: int
    txn_date: date
    amount: float
    currency: str
    description: str
    merchant: Optional[str]
    category_id: Optional[int]
    payment_method: Optional[str]
    is_transfer: bool
    source: str

@router.get("", response_model=List[TransactionResponse])
def list_transactions(
    month: Optional[str] = Query(None, regex=r"^\d{4}-\d{2}$"),
    category_id: Optional[int] = None,
    account_id: Optional[int] = None,
    method: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(100, le=500),
    offset: int = 0,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """List transactions with filters"""
    query = select(Transaction).where(Transaction.user_id == user_id)
    
    if month:
        year, mon = month.split("-")
        query = query.where(
            Transaction.txn_date >= date(int(year), int(mon), 1)
        )
        # Simple month end (could improve)
        if int(mon) == 12:
            query = query.where(Transaction.txn_date < date(int(year) + 1, 1, 1))
        else:
            query = query.where(Transaction.txn_date < date(int(year), int(mon) + 1, 1))
    
    if category_id:
        query = query.where(Transaction.category_id == category_id)
    
    if account_id:
        query = query.where(Transaction.account_id == account_id)
    
    if method:
        query = query.where(Transaction.payment_method == method)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (Transaction.description.ilike(search_term)) | 
            (Transaction.merchant.ilike(search_term))
        )
    
    query = query.order_by(Transaction.txn_date.desc(), Transaction.created_at.desc())
    query = query.offset(offset).limit(limit)
    
    transactions = session.exec(query).all()
    
    return [TransactionResponse(
        id=t.id,
        account_id=t.account_id,
        txn_date=t.txn_date,
        amount=t.amount,
        currency=t.currency,
        description=t.description,
        merchant=t.merchant,
        category_id=t.category_id,
        payment_method=t.payment_method,
        is_transfer=t.is_transfer,
        source=t.source.value
    ) for t in transactions]

@router.post("", response_model=TransactionResponse, status_code=201)
def create_transaction(
    data: TransactionCreate,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """Create manual transaction"""
    # Generate dedupe hash
    hash_input = f"{data.txn_date}|{data.amount}|{data.merchant or ''}||manual"
    hash_dedupe = hashlib.sha256(hash_input.encode()).hexdigest()
    
    txn = Transaction(
        user_id=user_id,
        account_id=data.account_id,
        txn_date=data.txn_date,
        amount=data.amount,
        currency=data.currency,
        description=data.description,
        merchant=data.merchant,
        category_id=data.category_id,
        subcategory_id=data.subcategory_id,
        payment_method=data.payment_method,
        is_transfer=data.is_transfer,
        source=TransactionSource.MANUAL,
        hash_dedupe=hash_dedupe
    )
    
    session.add(txn)
    session.commit()
    session.refresh(txn)
    
    return TransactionResponse(
        id=txn.id,
        account_id=txn.account_id,
        txn_date=txn.txn_date,
        amount=txn.amount,
        currency=txn.currency,
        description=txn.description,
        merchant=txn.merchant,
        category_id=txn.category_id,
        payment_method=txn.payment_method,
        is_transfer=txn.is_transfer,
        source=txn.source.value
    )

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """Get single transaction"""
    txn = session.exec(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        )
    ).first()
    
    if not txn:
        raise NotFoundError("Transaction not found")
    
    return TransactionResponse(
        id=txn.id,
        account_id=txn.account_id,
        txn_date=txn.txn_date,
        amount=txn.amount,
        currency=txn.currency,
        description=txn.description,
        merchant=txn.merchant,
        category_id=txn.category_id,
        payment_method=txn.payment_method,
        is_transfer=txn.is_transfer,
        source=txn.source.value
    )
