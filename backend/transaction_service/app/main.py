import os
import uuid
from datetime import datetime
from typing import List, Optional, Any

from fastapi import FastAPI, HTTPException, Depends, status, Header
from sqlmodel import Field, Session, SQLModel, create_engine, select, func

from .models import DBTransaction, TransactionCreate, TransactionPublic, UserTransactionsPublic, User, Message  # Import all necessary models

# --- Database Setup ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://user:password@localhost:5436/transaction_db")

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Transaction Service",
    description="Manages user transactions (buy/sell actions)."
)

# --- Dependency to get DB Session ---
def get_db():
    with Session(engine) as session:
        yield session

# --- Dependencies for Authorization (Simplified) ---
# In a real microservice setup, this would validate a JWT or similar token
# issued by the User Service.
async def get_current_user_id(x_user_id: uuid.UUID = Header(..., alias="X-User-ID")) -> uuid.UUID:
    if not x_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-User-ID header missing")
    # In a real app, you'd validate this user_id against the User Service
    # For now, we assume it's valid if present
    return x_user_id

# --- FastAPI Lifecycle Events ---
@app.on_event("startup")
async def startup_event():
    create_db_and_tables()
    print("Transaction Service DB tables created/checked.")

@app.on_event("shutdown")
async def shutdown_event():
    print("Transaction Service shutting down.")

# --- API Endpoints ---

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Transaction Service!"}

@app.post("/transactions/{user_id}", response_model=TransactionPublic)
async def create_transaction(
    user_id: uuid.UUID,
    transaction_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id)
) -> Any:
    """Records a new buy or sell transaction for a user."""
    if user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized: Cannot create transactions for another user.")

    # Ensure the user exists in this service's understanding of users
    user_in_db = db.get(User, user_id)
    if not user_in_db:
        # For now, we assume user creation handles this relationship or a placeholder User exists
        db.add(User(id=user_id))
        db.commit()
        db.refresh(user_in_db)
        user_in_db = db.get(User, user_id)

    transaction = DBTransaction.model_validate(transaction_in, update={
        "user_id": user_id,
        "timestamp": datetime.now()
    })
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@app.get("/transactions/{user_id}", response_model=UserTransactionsPublic)
async def get_user_transactions(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user_id: uuid.UUID = Depends(get_current_user_id)
) -> Any:
    """Retrieves all transactions for a specific user."""
    if user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized: Cannot view other users' transactions.")

    count_statement = select(func.count()).select_from(DBTransaction).where(DBTransaction.user_id == user_id)
    count = db.exec(count_statement).one()

    transactions = db.exec(
        select(DBTransaction)
        .where(DBTransaction.user_id == user_id)
        .offset(skip)
        .limit(limit)
    ).all()

    return UserTransactionsPublic(user_id=user_id, transactions=transactions, count=count)

@app.get("/transactions/detail/{transaction_id}", response_model=TransactionPublic)
async def get_transaction_detail(
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id)
) -> Any:
    """Retrieves details of a specific transaction by ID."""
    transaction = db.get(DBTransaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    if transaction.user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized: Cannot view other users' transactions.")
    return transaction

@app.delete("/transactions/{transaction_id}", response_model=Message)
async def delete_transaction(
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id)
) -> Message:
    """Deletes a transaction."""
    transaction = db.get(DBTransaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    if transaction.user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized: Cannot delete other users' transactions.")

    db.delete(transaction)
    db.commit()
    return Message(message="Transaction deleted successfully") 