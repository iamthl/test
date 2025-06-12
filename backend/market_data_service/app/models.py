import uuid
from datetime import datetime, date
from typing import List, Optional, Annotated

from sqlmodel import Field, SQLModel


class DBPriceData(SQLModel, table=True):
    __tablename__ = "current_prices"

    symbol: str = Field(primary_key=True, index=True)
    price: float
    currency: str
    timestamp: datetime = Field(default_factory=datetime.now)

class HistoricalPricePointBase(SQLModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int

class DBHistoricalPricePoint(HistoricalPricePointBase, table=True):
    __tablename__ = "historical_prices"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    symbol: str = Field(index=True, nullable=False)
    date: Annotated[date, Field(index=True, nullable=False)]


# Pydantic models for API responses
class PriceData(SQLModel):
    symbol: str
    price: float
    currency: str
    timestamp: datetime

class HistoricalData(SQLModel):
    symbol: str
    data: List[HistoricalPricePointBase]

# Generic message
class Message(SQLModel):
    message: str 