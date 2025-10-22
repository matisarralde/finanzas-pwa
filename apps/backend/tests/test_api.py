# apps/backend/src/tests/test_transactions.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from datetime import date

from src.main import app
from src.core.database import get_session
from src.models.models import User, Account, Transaction, TransactionSource, Category
import hashlib

# Test database
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    user = User(id="test-user-1", email="test@example.com")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture(name="test_account")
def test_account_fixture(session: Session, test_user: User):
    account = Account(
        user_id=test_user.id,
        name="Test Account",
        institution="test_bank",
        type="credit",
        currency="CLP"
    )
    session.add(account)
    session.commit()
    session.refresh(account)
    return account

@pytest.fixture(name="test_category")
def test_category_fixture(session: Session):
    category = Category(name="Gustos", user_id=None)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

def test_create_transaction(client: TestClient, test_account: Account, test_user: User):
    """Test creating a manual transaction"""
    # Mock auth
    from src.core.auth_jwt import get_current_user_id
    app.dependency_overrides[get_current_user_id] = lambda: test_user.id
    
    response = client.post(
        "/transactions",
        json={
            "account_id": test_account.id,
            "txn_date": "2025-01-15",
            "amount": -50000.0,
            "currency": "CLP",
            "description": "Test transaction",
            "merchant": "Test Store"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == -50000.0
    assert data["merchant"] == "Test Store"
    assert data["source"] == "manual"

def test_list_transactions(
    client: TestClient, 
    session: Session,
    test_account: Account, 
    test_user: User
):
    """Test listing transactions with filters"""
    # Create test transactions
    for i in range(5):
        hash_input = f"2025-01-15|{-10000 * (i+1)}||test|manual{i}"
        hash_dedupe = hashlib.sha256(hash_input.encode()).hexdigest()
        
        txn = Transaction(
            user_id=test_user.id,
            account_id=test_account.id,
            txn_date=date(2025, 1, 15 + i),
            amount=-10000 * (i + 1),
            currency="CLP",
            description=f"Test transaction {i}",
            source=TransactionSource.MANUAL,
            hash_dedupe=hash_dedupe
        )
        session.add(txn)
    session.commit()
    
    # Mock auth
    from src.core.auth_jwt import get_current_user_id
    app.dependency_overrides[get_current_user_id] = lambda: test_user.id
    
    # Test filtering by month
    response = client.get("/transactions?month=2025-01")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    
    # Test pagination
    response = client.get("/transactions?limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_monthly_report(
    client: TestClient,
    session: Session,
    test_account: Account,
    test_user: User,
    test_category: Category
):
    """Test monthly report generation"""
    # Create transactions
    transactions_data = [
        {"amount": -50000, "category_id": test_category.id},
        {"amount": -30000, "category_id": test_category.id},
        {"amount": 200000, "category_id": None},  # Income
    ]
    
    for i, txn_data in enumerate(transactions_data):
        hash_input = f"2025-01-15|{txn_data['amount']}||report|test{i}"
        hash_dedupe = hashlib.sha256(hash_input.encode()).hexdigest()
        
        txn = Transaction(
            user_id=test_user.id,
            account_id=test_account.id,
            txn_date=date(2025, 1, 15),
            amount=txn_data["amount"],
            currency="CLP",
            description=f"Report test {i}",
            source=TransactionSource.MANUAL,
            category_id=txn_data.get("category_id"),
            hash_dedupe=hash_dedupe
        )
        session.add(txn)
    session.commit()
    
    # Mock auth
    from src.core.auth_jwt import get_current_user_id
    app.dependency_overrides[get_current_user_id] = lambda: test_user.id
    
    response = client.get("/reports/monthly?month=2025-01")
    assert response.status_code == 200
    data = response.json()
    
    assert data["month"] == "2025-01"
    assert data["total_income"] == 200000
    assert data["total_expenses"] == -80000
    assert data["net"] == 120000
    assert len(data["by_category"]) >= 1

def test_export_csv(
    client: TestClient,
    session: Session,
    test_account: Account,
    test_user: User
):
    """Test CSV export"""
    # Create transaction
    hash_input = "2025-01-15|-25000||csv|test"
    hash_dedupe = hashlib.sha256(hash_input.encode()).hexdigest()
    
    txn = Transaction(
        user_id=test_user.id,
        account_id=test_account.id,
        txn_date=date(2025, 1, 15),
        amount=-25000,
        currency="CLP",
        description="CSV test",
        source=TransactionSource.MANUAL,
        hash_dedupe=hash_dedupe
    )
    session.add(txn)
    session.commit()
    
    # Mock auth
    from src.core.auth_jwt import get_current_user_id
    app.dependency_overrides[get_current_user_id] = lambda: test_user.id
    
    response = client.get("/exports/monthly.csv?month=2025-01")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    
    content = response.text
    assert "Fecha,Monto" in content  # Spanish headers
    assert "2025-01-15" in content

def test_health_check(client: TestClient):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ok", "degraded"]
    assert "database" in data
