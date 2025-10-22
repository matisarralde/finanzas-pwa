# apps/backend/src/api/exports.py
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from datetime import date
from io import StringIO
import csv

from src.core.database import get_session
from src.core.auth_jwt import get_current_user_id
from src.models.models import Transaction, Category, Account

router = APIRouter()

@router.get("/monthly.csv")
def export_monthly_csv(
    month: str = Query(..., regex=r"^\d{4}-\d{2}$"),
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """Export transactions as CSV with Spanish headers"""
    year, mon = map(int, month.split("-"))
    start_date = date(year, mon, 1)
    
    if mon == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, mon + 1, 1)
    
    # Fetch transactions
    query = select(Transaction).where(
        Transaction.user_id == user_id,
        Transaction.txn_date >= start_date,
        Transaction.txn_date < end_date
    ).order_by(Transaction.txn_date.desc())
    
    transactions = session.exec(query).all()
    
    # Build CSV
    output = StringIO()
    writer = csv.writer(output, delimiter=',')
    
    # Spanish headers
    writer.writerow([
        'Fecha',
        'Monto',
        'Moneda',
        'Descripción',
        'Comercio',
        'Categoría',
        'Cuenta',
        'Método de Pago',
        'Origen'
    ])
    
    # Write data
    for txn in transactions:
        # Get category name
        cat_name = ''
        if txn.category_id:
            cat = session.get(Category, txn.category_id)
            if cat:
                cat_name = cat.name
        
        # Get account name
        acc_name = ''
        if txn.account_id:
            acc = session.get(Account, txn.account_id)
            if acc:
                acc_name = acc.name
        
        writer.writerow([
            txn.txn_date.isoformat(),
            f"{txn.amount:.2f}",
            txn.currency,
            txn.description,
            txn.merchant or '',
            cat_name,
            acc_name,
            txn.payment_method or '',
            txn.source.value
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=transacciones_{month}.csv"
        }
    )
