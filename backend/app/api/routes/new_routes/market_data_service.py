# market_data_service.py

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
# from datetime import datetime, date
import datetime
from sqlmodel import Field, Session, SQLModel, create_engine, select

# --- Database Setup ---
DATABASE_URL = "postgresql://user:password@localhost:5435/market_data_db"
engine = create_engine(DATABASE_URL, echo=True)

# --- SQLModel Models (Database Tables) ---
class DBPriceData(SQLModel, table=True):
    __tablename__ = "current_prices"

    symbol: str = Field(primary_key=True, index=True) # Symbol is primary key for current prices
    price: float
    currency: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)

class HistoricalPricePointBase(SQLModel):
    date: datetime.date
    open: float
    high: float
    low: float
    close: float
    volume: int

class DBHistoricalPricePoint(HistoricalPricePointBase, table=True):
    __tablename__ = "historical_prices"

    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(index=True, nullable=False)
    date: datetime.date = Field(index=True, nullable=False)

# --- Pydantic Models (API Request/Response Schemas) ---
class PriceData(BaseModel):
    symbol: str
    price: float
    currency: str
    timestamp: datetime.datetime

# class HistoricalPricePoint(BaseModel):
#     date: datetime.date
#     open: float
#     high: float
#     low: float
#     close: float
#     volume: int

class HistoricalData(BaseModel):
    symbol: str
    data: list[HistoricalPricePointBase]

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Market Data Service",
    description="Provides real-time and historical financial market data."
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
    print("Market Data Service DB tables created/checked.")
    # Optional: Add some mock data for initial testing
    with Session(engine) as session:
        if not session.exec(select(DBPriceData)).first():
            mock_current_prices_data = [
                DBPriceData(symbol="AAPL", price=170.25, currency="USD"),
                DBPriceData(symbol="GOOGL", price=180.50, currency="USD"),
                DBPriceData(symbol="MSFT", price=420.10, currency="USD"),
                DBPriceData(symbol="BTC", price=68000.00, currency="USD"),
                DBPriceData(symbol="ETH", price=3800.00, currency="USD"),
                DBPriceData(symbol="BANK_A_SAVINGS", price=0.035, currency="PERCENT"), # Example for bank rate
            ]
            session.add_all(mock_current_prices_data)
            session.commit()
            print("Mock current prices added.")

        if not session.exec(select(DBHistoricalPricePoint)).first():
            mock_historical_data_points = [
                DBHistoricalPricePoint(symbol="AAPL", date=datetime.date(2025, 5, 27), open=165.00, high=170.50, low=164.80, close=169.90, volume=10000000),
                DBHistoricalPricePoint(symbol="AAPL", date=datetime.date(2025, 5, 28), open=170.00, high=171.20, low=169.50, close=170.25, volume=12000000),
                DBHistoricalPricePoint(symbol="BTC", date=datetime.date(2025, 5, 27), open=67000.00, high=68500.00, low=66800.00, close=68200.00, volume=50000),
                DBHistoricalPricePoint(symbol="BTC", date=datetime.date(2025, 5, 28), open=68200.00, high=68300.00, low=67900.00, close=68000.00, volume=60000),
            ]
            session.add_all(mock_historical_data_points)
            session.commit()
            print("Mock historical data added.")

@app.on_event("shutdown")
async def shutdown_event():
    print("Market Data Service shutting down.")

# --- API Endpoints ---

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Market Data Service!"}

@app.get("/market-data/current/{symbol}", response_model=PriceData)
async def get_current_price(symbol: str, db: Session = Depends(get_db)):
    """Retrieves the current price for a given financial instrument symbol."""
    statement = select(DBPriceData).where(DBPriceData.symbol.ilike(symbol)) # Case-insensitive search
    price_data = db.exec(statement).first()

    if not price_data:
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found.")
    return price_data

@app.get("/market-data/historical/{symbol}", response_model=HistoricalData)
async def get_historical_data(
    symbol: str,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    db: Session = Depends(get_db)
):
    """Retrieves historical price data for a given financial instrument symbol."""
    statement = select(DBHistoricalPricePoint).where(DBHistoricalPricePoint.symbol.ilike(symbol))

    if start_date:
        statement = statement.where(DBHistoricalPricePoint.date >= start_date)
    if end_date:
        statement = statement.where(DBHistoricalPricePoint.date <= end_date)

    # Order by date to get chronological data
    statement = statement.order_by(DBHistoricalPricePoint.date)

    historical_points = db.exec(statement).all()

    if not historical_points:
        raise HTTPException(status_code=404, detail=f"Historical data for symbol '{symbol}' not found or no data for the given date range.")
    return HistoricalData(symbol=symbol.upper(), data=historical_points)

# To run this:
# uvicorn market_data_service:app --port 8000 --reload
