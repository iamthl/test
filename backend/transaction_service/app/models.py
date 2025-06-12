import uuid
from datetime import datetime
from typing import Literal, List, Optional
from enum import Enum

from sqlmodel import Field, SQLModel, Relationship

# Minimal User model for relationship, actual user data resides in User Service
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    transactions: List["DBTransaction"] = Relationship(back_populates="user")

class TransactionType(str, Enum):
    BUY = "buy"
    SELL = "sell"

class DBTransaction(SQLModel, table=True):
    __tablename__ = "transactions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(index=True, nullable=False, foreign_key="users.id")
    symbol: str = Field(index=True, nullable=False)
    quantity: float
    price: float
    transaction_type: TransactionType
    timestamp: datetime = Field(default_factory=datetime.now)
    user: User = Relationship(back_populates="transactions")

# Pydantic models for API interactions
class TransactionCreate(SQLModel):
    symbol: str
    quantity: float
    price: float
    transaction_type: TransactionType

class TransactionPublic(TransactionCreate):
    id: uuid.UUID
    user_id: uuid.UUID
    timestamp: datetime

class UserTransactionsPublic(SQLModel):
    user_id: uuid.UUID
    transactions: List[TransactionPublic]
    count: int

# Generic message
class Message(SQLModel):
    message: str 