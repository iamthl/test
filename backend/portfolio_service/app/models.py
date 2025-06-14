import uuid
from datetime import datetime
from typing import List, Optional
from enum import Enum

from sqlmodel import Field, SQLModel, Relationship

class InstrumentType(str, Enum):
    VNSTOCK = "vnstock"
    INTERNATIONAL_STOCK = "international_stock"
    CRYPTO = "crypto"
    FOREX = "forex"
    COMMODITY = "commodity"
    FUND = "fund"

# Minimal User model for relationship, actual user data resides in User Service
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    holdings: List["DBHolding"] = Relationship(back_populates="user")

class DBHolding(SQLModel, table=True):
    __tablename__ = "holdings"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(index=True, nullable=False, foreign_key="users.id")
    symbol: str = Field(index=True, nullable=False)
    instrument_type: InstrumentType = Field(nullable=False)
    quantity: float
    average_cost: float
    last_updated: datetime = Field(default_factory=datetime.now)
    user: User = Relationship(back_populates="holdings")


# Pydantic models for API responses
class PortfolioHolding(SQLModel):
    id: uuid.UUID
    symbol: str
    instrument_type: InstrumentType
    quantity: float
    average_cost: float
    last_updated: datetime

class Portfolio(SQLModel):
    user_id: uuid.UUID
    holdings: List[PortfolioHolding]
    total_value: Optional[float] = None 