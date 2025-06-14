import uuid
from datetime import datetime, date
from typing import List, Optional, Annotated

from sqlmodel import Field, SQLModel, Relationship


class DBPriceData(SQLModel, table=True):
    __tablename__ = "price_data"

    symbol: str = Field(primary_key=True)
    instrument_type: str = Field(index=True)
    price: float
    currency: str
    timestamp: datetime = Field(default_factory=datetime.now)

class DBHistoricalPricePoint(SQLModel, table=True):
    __tablename__ = "historical_price_points"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    symbol: str = Field(index=True)
    instrument_type: str = Field(index=True)
    date: datetime
    open: float
    high: float
    low: float
    close: float
    created_at: datetime = Field(default_factory=datetime.now)

class HistoricalPricePointBase(SQLModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float

# Pydantic models for API responses
class PriceData(SQLModel):
    symbol: str
    instrument_type: str
    price: float
    currency: str
    timestamp: datetime

class HistoricalData(SQLModel):
    symbol: str
    instrument_type: str
    data: List[HistoricalPricePointBase]

# Generic message
class Message(SQLModel):
    message: str 
    