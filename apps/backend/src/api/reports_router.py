# apps/backend/src/api/reports.py
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from src.core.database import get_session
from src.core.auth_jwt import get_current_user_id
from src.models.models import Transaction, Category

router = APIRouter()

class CategoryTotal(BaseModel):
    category_id: Optional[int]
    category_name: Optional[str]
    total: float
    count: int

class MonthlyReport(BaseModel):
    month: str
    total_income: float
    total_expenses: float
    net: float
    by_category: List[CategoryTotal]
    previous_month_delta: Optional[float]

@router.get("/monthly", response_model=MonthlyReport)
def monthly_report(
    month: str = Query(..., regex=r"^\d{4}-\d{2}$"),
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Generate monthly financial report.
    Optimized with aggregations and indices.
    """
    year, mon = map(int, month.split("-"))
    start_date = date(year, mon, 1)
    
    # Calculate end date
    if mon == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, mon + 1, 1)
    
    # Get transactions for this month
    query = select(
        Transaction.category_id,
        func.sum(Transaction.amount).label('total'),
        func.count(Transaction.id).label('count')
    ).where(
        Transaction.user_id == user_id,
        Transaction.txn_date >= start_date,
        Transaction.txn_date < end_date
    ).group_by(Transaction.category_id)
    
    results = session.exec(query).all()
    
    # Calculate totals
    total_expenses = sum(r.total for r in results if r.total < 0)
    total_income = sum(r.total for r in results if r.total > 0)
    
    # Get category names
    by_category = []
    for r in results:
        cat_name = None
        if r.category_id:
            cat = session.get(Category, r.category_id)
            if cat:
                cat_name = cat.name
        
        by_category.append(CategoryTotal(
            category_id=r.category_id,
            category_name=cat_name,
            total=r.total,
            count=r.count
        ))
    
    # Calculate delta vs previous month
    prev_month = start_date - relativedelta(months=1)
    prev_end = start_date
    
    prev_query = select(
        func.sum(Transaction.amount).label('total')
    ).where(
        Transaction.user_id == user_id,
        Transaction.txn_date >= prev_month,
        Transaction.txn_date < prev_end
    )
    
    prev_result = session.exec(prev_query).first()
    prev_net = prev_result if prev_result else 0
    
    current_net = total_income + total_expenses
    delta = current_net - prev_net if prev_net else None
    
    return MonthlyReport(
        month=month,
        total_income=total_income,
        total_expenses=total_expenses,
        net=current_net,
        by_category=by_category,
        previous_month_delta=delta
    )
