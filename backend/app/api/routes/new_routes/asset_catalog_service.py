# asset_catalog_service.py

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlmodel import Field, Session, SQLModel, create_engine, select

# --- Database Setup ---
DATABASE_URL = "postgresql://user:password@localhost:5434/asset_catalog_db"

engine = create_engine(DATABASE_URL, echo=True)

# --- SQLModel Models (Database Tables) ---
class DBAsset(SQLModel, table=True):
    __tablename__ = "assets"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, nullable=False)
    type: str = Field(index=True) # e.g., "ETF", "Savings Account", "Fund Certificate"
    description: Optional[str] = None
    symbol: Optional[str] = Field(index=True, unique=True) # For ETFs, stocks
    interest_rate: Optional[float] = None # For savings accounts
    min_investment: Optional[float] = None
    # Add other relevant fields for different asset types

# --- Pydantic Models (API Request/Response Schemas) ---
class AssetCreate(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    symbol: Optional[str] = None
    interest_rate: Optional[float] = None
    min_investment: Optional[float] = None

class AssetPublic(BaseModel):
    id: int
    name: str
    type: str
    description: Optional[str] = None
    symbol: Optional[str] = None
    interest_rate: Optional[float] = None
    min_investment: Optional[float] = None

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Asset Catalog Service",
    description="Manages a catalog of available financial assets/products."
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
    print("Asset Catalog Service DB tables created/checked.")
    # Optional: Add some mock assets for initial testing
    # with Session(engine) as session:
    #     if not session.exec(select(DBAsset)).first():
    #         assets_to_add = [
    #             DBAsset(name="S&P 500 ETF", type="ETF", symbol="SPY", description="Tracks S&P 500 index"),
    #             DBAsset(name="High Yield Savings", type="Savings Account", interest_rate=0.045, description="High interest savings account"),
    #             DBAsset(name="Tech Growth Fund", type="Fund Certificate", description="Aggressive tech fund")
    #         ]
    #         session.add_all(assets_to_add)
    #         session.commit()
    #         print("Mock assets added to catalog.")

@app.on_event("shutdown")
async def shutdown_event():
    print("Asset Catalog Service shutting down.")

# --- API Endpoints ---

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Asset Catalog Service!"}

@app.post("/assets", response_model=AssetPublic)
async def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    """Adds a new asset to the catalog."""
    db_asset = DBAsset.model_validate(asset) # Convert Pydantic model to SQLModel
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset

@app.get("/assets", response_model=List[AssetPublic])
async def get_all_assets(db: Session = Depends(get_db)):
    """Retrieves all assets from the catalog."""
    statement = select(DBAsset)
    assets = db.exec(statement).all()
    return assets

@app.get("/assets/{asset_id}", response_model=AssetPublic)
async def get_asset_by_id(asset_id: int, db: Session = Depends(get_db)):
    """Retrieves an asset by its ID."""
    asset = db.get(DBAsset, asset_id) # Direct get by primary key
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@app.get("/assets/search", response_model=List[AssetPublic])
async def search_assets(query: str, db: Session = Depends(get_db)):
    """Searches for assets by name, type, or symbol."""
    statement = select(DBAsset).where(
        (DBAsset.name.ilike(f"%{query}%")) |
        (DBAsset.type.ilike(f"%{query}%")) |
        (DBAsset.symbol.ilike(f"%{query}%"))
    )
    assets = db.exec(statement).all()
    return assets

# To run this:
# uvicorn asset_catalog_service:app --port 8004 --reload