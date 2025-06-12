# transaction_service.py

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from aiokafka import AIOKafkaProducer
import asyncio
import json

from sqlmodel import Field, Session, SQLModel, create_engine, select

# --- Database Setup ---
DATABASE_URL = "postgresql://user:password@localhost:5436/transaction_db"

engine = create_engine(DATABASE_URL, echo=True)

# --- SQLModel Models (Database Tables) ---
class DBTransaction(SQLModel, table=True):
    __tablename__ = "transactions"

    transaction_id: str = Field(primary_key=True, index=True)
    user_id: str = Field(index=True, nullable=False)
    type: str = Field(nullable=False) # e.g., "buy", "sell", "deposit", "withdrawal"
    symbol: Optional[str] = Field(default=None, index=True) # For buy/sell
    quantity: Optional[float] = None # For buy/sell
    amount: float = Field(nullable=False) # Total amount of transaction
    timestamp: datetime = Field(default_factory=datetime.now, index=True)

# --- Pydantic Models (API Request/Response Schemas) ---
class TransactionCreate(BaseModel):
    transaction_id: str
    user_id: str
    type: str
    symbol: Optional[str] = None
    quantity: Optional[float] = None
    amount: float

class TransactionPublic(BaseModel):
    transaction_id: str
    user_id: str
    type: str
    symbol: Optional[str] = None
    quantity: Optional[float] = None
    amount: float
    timestamp: datetime

# --- Kafka Producer Setup ---
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
TRANSACTION_EVENTS_TOPIC = "transaction_events"

producer: AIOKafkaProducer = None

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Transaction Service",
    description="Manages financial transactions and publishes events to Kafka."
)

# --- Dependency to get DB Session ---
def get_db():
    with Session(engine) as session:
        yield session

# --- FastAPI Lifecycle Events ---
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
async def startup_event():
    create_db_and_tables()
    print("Transaction Service DB tables created/checked.")
    global producer
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    print("Kafka Producer started")

@app.on_event("shutdown")
async def shutdown_event():
    if producer:
        await producer.stop()
        print("Kafka Producer stopped")
    print("Transaction Service shutting down.")

# --- API Endpoints ---

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Transaction Service!"}

@app.post("/transactions", response_model=TransactionPublic)
async def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    """
    Creates a new transaction, saves it to the database, and publishes a
    'transaction_completed' event to Kafka.
    """
    statement = select(DBTransaction).where(DBTransaction.transaction_id == transaction.transaction_id)
    existing_transaction = db.exec(statement).first()
    if existing_transaction:
        raise HTTPException(status_code=400, detail="Transaction ID already exists.")

    db_transaction = DBTransaction.model_validate(transaction)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction) # Refresh to get timestamp from DB

    # --- Publish event to Kafka ---
    try:
        event_payload = {
            "event_type": "transaction_completed",
            "transaction_data": db_transaction.model_dump_json() # Use model_dump_json for Pydantic v2
        }
        await producer.send_and_wait(
            TRANSACTION_EVENTS_TOPIC,
            json.dumps(event_payload).encode('utf-8'),
            key=db_transaction.user_id.encode('utf-8') # Use user_id as key for partitioning
        )
        print(f"Published transaction_completed event for user {db_transaction.user_id} to Kafka.")
    except Exception as e:
        print(f"Error publishing to Kafka: {e}")
        # Consider a transactional outbox pattern for robustness in production

    return db_transaction

@app.get("/transactions/{user_id}", response_model=List[TransactionPublic])
async def get_user_transactions(user_id: str, db: Session = Depends(get_db)):
    """Retrieves all transactions for a given user."""
    statement = select(DBTransaction).where(DBTransaction.user_id == user_id).order_by(DBTransaction.timestamp.desc())
    transactions = db.exec(statement).all()
    return transactions

# To run this:
# uvicorn transaction_service:app --port 8003 --reload
