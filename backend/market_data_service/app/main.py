import os
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict

from vnstock import *
from fastapi import FastAPI, HTTPException, Depends, status
from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import BaseModel

# Import specific Quote classes from their modules
from vnstock.explorer.vci import Quote as VCIQuote
from vnstock.explorer.msn import Quote as MSNQuote
from vnstock.explorer.msn.const import _CURRENCY_ID_MAP, _CRYPTO_ID_MAP, _GLOBAL_INDICES

from .models import DBPriceData, DBHistoricalPricePoint, PriceData, HistoricalData, HistoricalPricePointBase, Message  # Import all necessary models

# --- Database Setup ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5435/market_data_db")

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Market Data Service",
    description="Provides current and historical market data for Vietnamese stocks."
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

class PriceResponse(BaseModel):
    symbol: str
    price: float
    currency: str
    timestamp: datetime
    instrument_type: str

class HistoricalDataResponse(BaseModel):
    symbol: str
    data: List[Dict]
    instrument_type: str

def get_quote_source(instrument_type: str):
    """Get the appropriate Quote class based on instrument type"""
    source_map = {
        "vnstock": VCIQuote,  # Vietnamese stocks
        "crypto": MSNQuote,   # Cryptocurrencies
        "forex": MSNQuote,    # Forex pairs
        "commodity": MSNQuote, # Commodities
        "fund": VCIQuote,     # Funds
        "derivative": VCIQuote, # Derivatives
        "index": MSNQuote # Indexes
    }
    return source_map.get(instrument_type.lower(), VCIQuote)

@app.get("/market-data/")
async def read_root():
    return {"message": "Welcome to the Market Data Service!"}

@app.get("/market-data/current-price/{symbol}")
async def get_current_price(symbol: str, instrument_type: str = "vnstock", db: Session = Depends(get_db)):
    try:
        # Check if we have recent data in DB (within last 5 minutes)
        recent_data = db.get(DBPriceData, symbol.upper())
        if recent_data and (datetime.now() - recent_data.timestamp) < timedelta(minutes=5):
            return PriceData(
                symbol=recent_data.symbol,
                instrument_type=recent_data.instrument_type,
                price=recent_data.price,
                currency=recent_data.currency,
                timestamp=recent_data.timestamp
            )

        # If no recent data, fetch from API
        QuoteClass = get_quote_source(instrument_type)
        symbol = symbol.upper()
        if QuoteClass == MSNQuote:
            symbol = _CRYPTO_ID_MAP.get(symbol, symbol)
            symbol = _GLOBAL_INDICES.get(symbol, symbol)
            symbol = _CURRENCY_ID_MAP.get(symbol, symbol)
        quote = QuoteClass(symbol)
        
        # Get current price
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        data = quote.history(start=start_date, end=end_date)
        if data.empty:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        # Get the latest price
        latest = data.iloc[-1]
        price = latest['close']
        
        # Determine currency based on instrument type
        currency = "USD" if instrument_type.lower() in ["crypto", "forex", "commodity"] else "VND"

        # Save to database
        db_price = DBPriceData(
            symbol=symbol.upper(),
            instrument_type=instrument_type,
            price=price,
            currency=currency,
            timestamp=datetime.now()
        )
        db.merge(db_price)  # Use merge instead of add to handle updates
        db.commit()

        return PriceData(
            symbol=symbol.upper(),
            instrument_type=instrument_type,
            price=price,
            currency=currency,
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market-data/historical/{symbol}")
async def get_historical_data(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    instrument_type: str = "vnstock",
    db: Session = Depends(get_db)
):
    try:
        # Set default dates if not provided
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        # Convert string dates to datetime
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        # Check if we have the data in DB
        query = select(DBHistoricalPricePoint).where(
            DBHistoricalPricePoint.symbol == symbol.upper(),
            DBHistoricalPricePoint.instrument_type == instrument_type,
            DBHistoricalPricePoint.date >= start_dt,
            DBHistoricalPricePoint.date <= end_dt
        )
        db_data = db.exec(query).all()

        # If we have all the data in DB, return it
        if db_data and len(db_data) == (end_dt - start_dt).days + 1:
            return HistoricalData(
                symbol=symbol.upper(),
                instrument_type=instrument_type,
                data=[
                    HistoricalPricePointBase(
                        date=point.date,
                        open=point.open,
                        high=point.high,
                        low=point.low,
                        close=point.close
                    ) for point in db_data
                ]
            )

        # If not all data is in DB, fetch from API
        QuoteClass = get_quote_source(instrument_type)
        symbol = symbol.upper()
        if QuoteClass == MSNQuote:
            symbol = _CRYPTO_ID_MAP.get(symbol, symbol)
            symbol = _GLOBAL_INDICES.get(symbol, symbol)
            symbol = _CURRENCY_ID_MAP.get(symbol, symbol)
        quote = QuoteClass(symbol)

        # Get historical data
        data = quote.history(
            start=start_date,
            end=end_date
        )

        if data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")

        # Save to database
        for _, row in data.iterrows():
            hist_point = DBHistoricalPricePoint(
                symbol=symbol,
                instrument_type=instrument_type,
                date=row['time'],
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close']
            )
            db.merge(hist_point)  # Use merge to handle updates
        
        db.commit()

        # Convert DataFrame to list of dictionaries
        historical_data = [
            HistoricalPricePointBase(
                date=row['time'],
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close']
            ) for _, row in data.iterrows()
        ]

        return HistoricalData(
            symbol=symbol,
            instrument_type=instrument_type,
            data=historical_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 