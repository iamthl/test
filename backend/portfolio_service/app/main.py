import os
import uuid
from datetime import datetime
from typing import List, Optional, Any

from fastapi import FastAPI, HTTPException, Depends, status, Header
from sqlmodel import Field, Session, SQLModel, create_engine, select, func

from .models import DBHolding, Portfolio, PortfolioHolding, User  # Import all necessary models

# --- Pydantic Models for Holdings (for API request bodies) ---
class PortfolioHoldingCreate(SQLModel):
    symbol: str
    quantity: float
    average_cost: float

class PortfolioHoldingUpdate(SQLModel):
    quantity: Optional[float] = None
    average_cost: Optional[float] = None

# --- Database Setup ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5437/portfolio_db")

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Portfolio Service",
    description="Manages user portfolios and their holdings."
)

# --- Dependency to get DB Session ---
def get_db():
    with Session(engine) as session:
        yield session

# --- Dependencies for Authorization (Simplified) ---
# In a real microservice setup, this would validate a JWT or similar token
# issued by the User Service.
async def get_current_user_id(x_user_id: uuid.UUID = Header(..., alias="X-User-ID")) -> uuid.UUID:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-ID header missing")
    # In a real app, you'd validate this user_id against the User Service
    # For now, we assume it's valid if present
    return x_user_id

# --- FastAPI Lifecycle Events ---
@app.on_event("startup")
async def startup_event():
    create_db_and_tables()
    print("Portfolio Service DB tables created/checked.")

@app.on_event("shutdown")
async def shutdown_event():
    print("Portfolio Service shutting down.")

# --- API Endpoints ---

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Portfolio Service!"}

@app.post("/portfolio/{user_id}/holdings", response_model=PortfolioHolding)
async def create_holding(
    user_id: uuid.UUID,
    holding_in: PortfolioHoldingCreate,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id) # Ensure authorized user
) -> Any:
    """Adds a new holding to a user's portfolio."""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized: Cannot add holdings for another user.")
    
    # Ensure the user exists in this service's understanding of users
    user_in_db = db.get(User, user_id)
    if not user_in_db:
        db.add(User(id=user_id))
        db.commit()
        db.refresh(user_in_db)

    # Check if holding for this symbol already exists for the user
    existing_holding = db.exec(
        select(DBHolding)
        .where(DBHolding.user_id == user_id)
        .where(DBHolding.symbol == holding_in.symbol)
    ).first()

    if existing_holding:
        raise HTTPException(status_code=409, detail=f"Holding for symbol {holding_in.symbol} already exists for this user. Use PUT to update.")

    holding = DBHolding.model_validate(holding_in, update={
        "user_id": user_id,
        "last_updated": datetime.now()
    })
    db.add(holding)
    db.commit()
    db.refresh(holding)
    return holding

@app.put("/portfolio/{user_id}/holdings/{holding_id}", response_model=PortfolioHolding)
async def update_holding(
    user_id: uuid.UUID,
    holding_id: uuid.UUID,
    holding_in: PortfolioHoldingUpdate,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id) # Ensure authorized user
) -> Any:
    """Updates an existing holding in a user's portfolio."""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized: Cannot update holdings for another user.")

    holding = db.get(DBHolding, holding_id)
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found.")
    if holding.user_id != user_id:
        raise HTTPException(status_code=400, detail="Holding does not belong to the specified user.")
    
    update_data = holding_in.model_dump(exclude_unset=True)
    holding.sqlmodel_update(update_data)
    holding.last_updated = datetime.now()
    db.add(holding)
    db.commit()
    db.refresh(holding)
    return holding

@app.delete("/portfolio/{user_id}/holdings/{holding_id}")
async def delete_holding(
    user_id: uuid.UUID,
    holding_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id) # Ensure authorized user
):
    """Deletes a holding from a user's portfolio."""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized: Cannot delete holdings for another user.")

    holding = db.get(DBHolding, holding_id)
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found.")
    if holding.user_id != user_id:
        raise HTTPException(status_code=400, detail="Holding does not belong to the specified user.")
    
    db.delete(holding)
    db.commit()
    return {"message": "Holding deleted successfully"}

@app.get("/portfolio/{user_id}", response_model=Portfolio)
async def get_user_portfolio(
    user_id: uuid.UUID, 
    db: Session = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id) # Ensure authorized user
) -> Any:
    """Retrieves a user's portfolio and holdings."""
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized: Cannot view other users' portfolios.")
    
    # Ensure the user exists in this service's understanding of users
    user_in_db = db.get(User, user_id)
    if not user_in_db:
        db.add(User(id=user_id))
        db.commit()
        db.refresh(user_in_db)
        user_in_db = db.get(User, user_id)

    holdings = db.exec(select(DBHolding).where(DBHolding.user_id == user_id)).all()
    
    portfolio_holdings = [PortfolioHolding.model_validate(h) for h in holdings]
    
    # Calculate total value (mocked for now, would integrate with market data)
    total_value = sum(h.quantity * h.average_cost for h in holdings) # Simplified

    return Portfolio(user_id=user_id, holdings=portfolio_holdings, total_value=total_value) 