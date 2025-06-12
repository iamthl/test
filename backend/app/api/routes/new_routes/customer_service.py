# customer_service.py

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict
from sqlmodel import Field, Session, SQLModel, create_engine, select

# --- Database Setup ---
# Use the host port mapped in docker-compose.yml
DATABASE_URL = "postgresql://user:password@localhost:5433/customer_db"

engine = create_engine(DATABASE_URL, echo=True) # echo=True for SQL logging

# --- SQLModel Models (Database Tables) ---
class DBCustomer(SQLModel, table=True):
    __tablename__ = "customers"

    id: Optional[str] = Field(default=None, primary_key=True, index=True)
    username: str = Field(index=True, unique=True, nullable=False)
    hashed_password: str = Field(nullable=False) # Store hashed password (for demo, plain)
    risk_appetite: str = Field(default="moderate") # e.g., "conservative", "moderate", "aggressive"
    email: str = Field(index=True, unique=True, nullable=False)

# --- Pydantic Models (API Request/Response Schemas) ---
class CustomerCreate(BaseModel):
    username: str
    password: str
    email: str
    risk_appetite: Optional[str] = "moderate"

class CustomerPublic(BaseModel):
    id: str
    username: str
    email: str
    risk_appetite: str

class CustomerLogin(BaseModel):
    username: str
    password: str

class AuthToken(BaseModel):
    user_id: str
    token: str

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Customer Service",
    description="Manages customer information, authentication, and risk appetite."
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
    print("Customer Service DB tables created/checked.")
    # Optional: Add a default user for testing if DB is empty
    # with Session(engine) as session:
    #     statement = select(DBCustomer).where(DBCustomer.username == "testuser")
    #     customer = session.exec(statement).first()
    #     if not customer:
    #         new_customer = DBCustomer(id="user_testuser", username="testuser", hashed_password="testpassword123", email="test@example.com")
    #         session.add(new_customer)
    #         session.commit()
    #         session.refresh(new_customer)

@app.on_event("shutdown")
async def shutdown_event():
    print("Customer Service shutting down.")

# --- API Endpoints ---

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Customer Service!"}

@app.post("/customers/register", response_model=CustomerPublic)
async def register_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """Registers a new customer."""
    statement = select(DBCustomer).where(
        (DBCustomer.username == customer.username) | (DBCustomer.email == customer.email)
    )
    existing_customer = db.exec(statement).first()

    if existing_customer:
        raise HTTPException(status_code=400, detail="Username or Email already registered")

    new_id = f"cust_{customer.username}"
    db_customer = DBCustomer(
        id=new_id,
        username=customer.username,
        hashed_password=customer.password,
        email=customer.email,
        risk_appetite=customer.risk_appetite
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@app.post("/customers/login", response_model=AuthToken)
async def login_customer(credentials: CustomerLogin, db: Session = Depends(get_db)):
    """Logs in a customer and returns an auth token."""
    statement = select(DBCustomer).where(DBCustomer.username == credentials.username)
    customer = db.exec(statement).first()

    if not customer or customer.hashed_password != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    mock_token = f"mock_jwt_for_{customer.id}"
    return AuthToken(user_id=customer.id, token=mock_token)

@app.get("/customers/{customer_id}", response_model=CustomerPublic)
async def get_customer_info(customer_id: str, db: Session = Depends(get_db)):
    """Retrieves customer information by ID."""
    statement = select(DBCustomer).where(DBCustomer.id == customer_id)
    customer = db.exec(statement).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# To run this:
# uvicorn customer_service:app --port 8001 --reload
