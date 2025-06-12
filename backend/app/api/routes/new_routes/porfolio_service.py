# portfolio_service.py

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
import httpx
import asyncio
import json
from datetime import datetime
from aiokafka import AIOKafkaConsumer

from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship

# --- Database Setup ---
DATABASE_URL = "postgresql://user:password@localhost:5437/portfolio_db"

engine = create_engine(DATABASE_URL, echo=True)

# --- SQLModel Models (Database Tables) ---
class DBHolding(SQLModel, table=True):
    __tablename__ = "holdings"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    symbol: str = Field(index=True, nullable=False)
    quantity: float
    average_cost: float
    last_updated: datetime = Field(default_factory=datetime.now)

    # Optional: If you want a Portfolio header table, link to it
    # portfolio_id: Optional[int] = Field(default=None, foreign_key="portfolios.id")
    # portfolio: Optional["DBPortfolio"] = Relationship(back_populates="holdings")

# class DBPortfolio(SQLModel, table=True):
#     __tablename__ = "portfolios"
#     id: Optional[int] = Field(default=None, primary_key=True)
#     user_id: str = Field(index=True, unique=True, nullable=False)
#     # holdings: List["DBHolding"] = Relationship(back_populates="portfolio")
#     # For simplicity, we'll manage holdings directly under user_id without a separate portfolio header table for now.
#     # If you need portfolio-level attributes (e.g., total cash, last rebalance date), add this table back.

# --- Pydantic Models (API Request/Response Schemas) ---
class PortfolioHolding(BaseModel):
    symbol: str
    quantity: float
    average_cost: float
    last_updated: datetime

class Portfolio(BaseModel):
    user_id: str
    holdings: List[PortfolioHolding]
    total_value: Optional[float] = None

# Define Transaction model for Kafka consumer to validate incoming data
class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    type: str
    symbol: Optional[str] = None
    quantity: Optional[float] = None
    amount: float
    timestamp: datetime

# --- Kafka Consumer Setup ---
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
TRANSACTION_EVENTS_TOPIC = "transaction_events"
KAFKA_CONSUMER_GROUP_ID = "portfolio_service_group"

# --- External Service URLs ---
MARKET_DATA_SERVICE_URL = "http://localhost:8000"

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Portfolio Management Service",
    description="Manages user investment portfolios and consumes transaction events."
)

# --- Dependency to get DB Session ---
def get_db():
    with Session(engine) as session:
        yield session

# --- Consumer Loop Function ---
async def consume_messages():
    consumer = AIOKafkaConsumer(
        TRANSACTION_EVENTS_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_CONSUMER_GROUP_ID,
        auto_offset_reset='earliest'
    )

    print(f"Starting Kafka consumer for topic '{TRANSACTION_EVENTS_TOPIC}'...")
    try:
        await consumer.start()
        print("Kafka Consumer started successfully.")
        async for msg in consumer:
            print(f"Consumed message from topic {msg.topic} at offset {msg.offset}:")
            print(f"  Key: {msg.key.decode() if msg.key else 'N/A'}")
            print(f"  Value: {msg.value.decode('utf-8')}")

            db = Session(engine) # Get a new DB session for each message processing
            try:
                event_data = json.loads(msg.value.decode('utf-8'))
                event_type = event_data.get("event_type")
                transaction_data_str = event_data.get("transaction_data")

                if event_type == "transaction_completed" and transaction_data_str:
                    transaction = Transaction.model_validate_json(transaction_data_str)
                    print(f"Processing transaction for user: {transaction.user_id}, type: {transaction.type}")

                    # Find existing holding or create new
                    statement = select(DBHolding).where(
                        DBHolding.user_id == transaction.user_id,
                        DBHolding.symbol.ilike(transaction.symbol)
                    )
                    db_holding = db.exec(statement).first()

                    if transaction.type == "buy" and transaction.symbol and transaction.quantity:
                        if not db_holding:
                            # Create new holding
                            price_per_unit = transaction.amount / transaction.quantity if transaction.quantity else 0
                            new_holding = DBHolding(
                                user_id=transaction.user_id,
                                symbol=transaction.symbol.upper(), # Store symbol consistently
                                quantity=transaction.quantity,
                                average_cost=price_per_unit
                            )
                            db.add(new_holding)
                            print(f"New holding created for {transaction.user_id}: {transaction.quantity} of {transaction.symbol}")
                        else:
                            # Update existing holding
                            total_qty = db_holding.quantity + transaction.quantity
                            if total_qty > 0:
                                db_holding.average_cost = (
                                    (db_holding.quantity * db_holding.average_cost) +
                                    (transaction.quantity * (transaction.amount / transaction.quantity))
                                ) / total_qty
                            db_holding.quantity = total_qty
                            db_holding.last_updated = datetime.now()
                            db.add(db_holding) # Add back to session for update
                            print(f"Holding updated for {transaction.user_id}: Added {transaction.quantity} of {transaction.symbol}")

                    elif transaction.type == "sell" and transaction.symbol and transaction.quantity:
                        if db_holding:
                            if db_holding.quantity >= transaction.quantity:
                                db_holding.quantity -= transaction.quantity
                                if db_holding.quantity == 0:
                                    db.delete(db_holding) # Remove if quantity is zero
                                    print(f"Holding deleted for {transaction.user_id}: {transaction.symbol}")
                                else:
                                    db_holding.last_updated = datetime.now()
                                    db.add(db_holding) # Add back to session for update
                                    print(f"Holding updated for {transaction.user_id}: Sold {transaction.quantity} of {transaction.symbol}")
                            else:
                                print(f"Warning: Attempted to sell more {transaction.symbol} than available for {transaction.user_id}")
                        else:
                            print(f"Warning: No holding found for {transaction.symbol} to sell for {transaction.user_id}")

                    db.commit()
                    # db.refresh(db_holding) # If you need updated holding info for further processing

                else:
                    print(f"Unknown or incomplete event type: {event_type}")

            except json.JSONDecodeError:
                print(f"Could not decode JSON from message value: {msg.value}")
            except Exception as e:
                print(f"Error processing Kafka message: {e}")
                db.rollback()
            finally:
                db.close() # Close DB session

    except Exception as e:
        print(f"Kafka consumer error: {e}")
    finally:
        if consumer:
            await consumer.stop()
            print("Kafka Consumer stopped.")

# --- FastAPI Startup/Shutdown Events ---
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
async def startup_event():
    create_db_and_tables()
    print("Portfolio Service DB tables created/checked.")
    asyncio.create_task(consume_messages())

@app.on_event("shutdown")
async def shutdown_event():
    print("Portfolio Management Service shutting down.")

# --- Dependencies for Authorization (Simplified) ---
async def get_current_user_id(x_user_id: str = Header(..., alias="X-User-ID")):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-ID header missing")
    return x_user_id

# --- API Endpoints ---

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Portfolio Management Service!"}

@app.get("/portfolio/{user_id}", response_model=Portfolio)
async def get_user_portfolio(user_id: str, current_user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Retrieves a user's portfolio, including current market values.
    Requires X-User-ID header for authorization.
    """
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized: Cannot access other users' portfolios.")

    statement = select(DBHolding).where(DBHolding.user_id == user_id)
    db_holdings = db.exec(statement).all()

    if not db_holdings:
        # Return an empty portfolio if no holdings found
        return Portfolio(user_id=user_id, holdings=[], total_value=0.0)

    holdings_list = []
    total_portfolio_value = 0.0

    async with httpx.AsyncClient() as client:
        for db_holding in db_holdings:
            try:
                # Call the Market Data Service to get the current price
                market_data_response = await client.get(
                    f"{MARKET_DATA_SERVICE_URL}/market-data/current/{db_holding.symbol}"
                )
                market_data_response.raise_for_status()
                price_data = market_data_response.json()

                current_price = price_data.get("price")
                if current_price is not None:
                    holding_value = db_holding.quantity * current_price
                    total_portfolio_value += holding_value

                pydantic_holding = PortfolioHolding.model_validate(db_holding) # Convert DBHolding to Pydantic
                holdings_list.append(pydantic_holding)

            except httpx.HTTPStatusError as e:
                print(f"Error fetching market data for {db_holding.symbol}: {e.response.status_code} - {e.response.text}")
                pydantic_holding = PortfolioHolding.model_validate(db_holding)
                holdings_list.append(pydantic_holding)
            except httpx.RequestError as e:
                print(f"Network error fetching market data for {db_holding.symbol}: {e}")
                pydantic_holding = PortfolioHolding.model_validate(db_holding)
                holdings_list.append(pydantic_holding)

    return Portfolio(
        user_id=user_id,
        holdings=holdings_list,
        total_value=round(total_portfolio_value, 2)
    )
