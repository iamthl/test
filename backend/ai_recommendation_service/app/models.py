import uuid
from datetime import datetime, date
from typing import List, Optional

from pydantic import BaseModel, EmailStr

# Pydantic models for inter-service communication (simplified versions of other services' public models)
class UserPublic(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    risk_appetite: str

class PortfolioHolding(BaseModel):
    symbol: str
    quantity: float
    average_cost: float
    last_updated: datetime

class Portfolio(BaseModel):
    user_id: uuid.UUID
    holdings: List[PortfolioHolding]
    total_value: Optional[float] = None

class PriceData(BaseModel):
    symbol: str
    price: float
    currency: str
    timestamp: datetime

class HistoricalPricePointBase(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


# Recommendation model for this service
class Recommendation(BaseModel):
    user_id: uuid.UUID
    asset_symbol: str
    recommendation_type: str  # e.g., "buy", "hold", "sell"
    strength: float  # e.g., 0.0 to 1.0
    reason: str
    timestamp: datetime = datetime.now()

# Generic message
class Message(BaseModel):
    message: str 