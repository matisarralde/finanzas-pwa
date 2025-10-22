# apps/backend/src/models/models.py
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional
from datetime import datetime, date
from enum import Enum

class AccountType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    CASH = "cash"
    INVESTMENT = "investment"
    LOAN = "loan"

class TransactionSource(str, Enum):
    EMAIL = "email"
    MANUAL = "manual"
    IMPORT = "import"

class BudgetPeriod(str, Enum):
    MONTHLY = "monthly"

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: str = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Account(SQLModel, table=True):
    __tablename__ = "accounts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    name: str
    institution: str
    type: AccountType
    currency: str = "CLP"
    last_sync_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Category(SQLModel, table=True):
    __tablename__ = "categories"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[str] = Field(default=None, foreign_key="users.id", index=True)
    name: str
    parent_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Budget(SQLModel, table=True):
    __tablename__ = "budgets"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    name: str
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    amount: float
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    start_month: date
    end_month: Optional[date] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    account_id: int = Field(foreign_key="accounts.id", index=True)
    txn_date: date = Field(index=True)
    posted_at: datetime = Field(default_factory=datetime.utcnow)
    amount: float
    currency: str = "CLP"
    description: str
    raw_payload: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    source: TransactionSource
    merchant: Optional[str] = None
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id", index=True)
    subcategory_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    payment_method: Optional[str] = None
    is_transfer: bool = False
    hash_dedupe: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

class Rule(SQLModel, table=True):
    __tablename__ = "rules"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    pattern: str  # regex pattern
    field: str  # merchant, description, amount
    action: str  # set_category, set_subcategory
    value: str  # category_id or value to set
    priority: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
