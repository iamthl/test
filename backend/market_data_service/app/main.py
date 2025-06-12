import os
from datetime import datetime, date
from typing import List, Optional

import yfinance as yf
from fastapi import FastAPI, HTTPException, Depends, status
from sqlmodel import Field, Session, SQLModel, create_engine, select

from .models import DBPriceData, DBHistoricalPricePoint, PriceData, HistoricalData, HistoricalPricePointBase, Message  # Import all necessary models

# --- Database Setup ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5435/market_data_db")

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Market Data Service",
    description="Provides current and historical market data."
)

# --- Dependency to get DB Session ---
def get_db():
    with Session(engine) as session:
        yield session

# --- FastAPI Lifecycle Events ---
@app.on_event("startup")
async def startup_event():
    create_db_and_tables()
    print("Market Data Service DB tables created/checked.")

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
    ticker = yf.Ticker(symbol)
    try:
        current_info = ticker.info
        price = current_info.get('currentPrice')
        currency = current_info.get('currency')
        if price is None or currency is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Current price or currency not found for symbol '{symbol}'.")
        
        # Save or update in DB
        db_price_data = db.get(DBPriceData, symbol.upper())
        if db_price_data:
            db_price_data.price = price
            db_price_data.currency = currency
            db_price_data.timestamp = datetime.now()
        else:
            db_price_data = DBPriceData(symbol=symbol.upper(), price=price, currency=currency, timestamp=datetime.now())
        db.add(db_price_data)
        db.commit()
        db.refresh(db_price_data)

        return PriceData(symbol=symbol.upper(), price=price, currency=currency, timestamp=datetime.now())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching current price for {symbol}: {e}")

@app.get("/market-data/latest-price/{symbol}", response_model=PriceData)
async def get_latest_price_from_db(symbol: str, db: Session = Depends(get_db)):
    """Retrieves the latest price for a given financial instrument symbol from the database."""
    db_price_data = db.get(DBPriceData, symbol.upper())
    if not db_price_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Latest price for symbol '{symbol}' not found in database. Try fetching current price first.")
    return PriceData.model_validate(db_price_data)

@app.get("/market-data/historical/{symbol}", response_model=HistoricalData)
async def get_historical_data(
    symbol: str,
    db: Session = Depends(get_db),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> HistoricalData:
    """Retrieves historical price data for a given financial instrument symbol."""
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start_date, end=end_date)

    if df.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Historical data for symbol '{symbol}' not found or no data for the given date range."
        )

    historical_points = []
    for index, row in df.iterrows():
        hist_point = DBHistoricalPricePoint(
            symbol=symbol.upper(),
            date=index.date(),
            open=row['Open'],
            high=row['High'],
            low=row['Low'],
            close=row['Close'],
            volume=row['Volume']
        )
        historical_points.append(hist_point)
        db.add(hist_point) # Add to session for saving
    
    db.commit() # Commit all new historical points

    return HistoricalData(symbol=symbol.upper(), data=historical_points) 