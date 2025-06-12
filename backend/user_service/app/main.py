import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Any

import jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Field, Session, SQLModel, create_engine, select

from .models import User, UserCreate, UserPublic, UserRegister, UpdatePassword, Message, Token, TokenPayload, NewPassword  # Import all necessary models

# --- Security Configuration ---
# Adjusted from app.core.security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secret_key_for_jwt_that_should_be_changed") # Replace with a strong secret key
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Can be moved to settings

def create_access_token(subject: str | uuid.UUID, expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# --- OAuth2 for token authentication ---
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/access-token")

# --- Database Setup ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://user:password@localhost:5433/customer_db")

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="User Service",
    description="Manages user information, authentication, and risk appetite."
)

# --- Dependency to get DB Session ---
def get_db():
    with Session(engine) as session:
        yield session

# --- Current User Dependency ---
def get_current_user(session: Session = Depends(get_db), token: str = Depends(reusable_oauth2)) -> User:
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, uuid.UUID(token_data.sub))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

CurrentUser = Depends(get_current_user)

def get_current_active_superuser(current_user: User = CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

# --- FastAPI Lifecycle Events ---
@app.on_event("startup")
async def startup_event():
    create_db_and_tables()
    print("User Service DB tables created/checked.")

@app.on_event("shutdown")
async def shutdown_event():
    print("User Service shutting down.")

# --- API Endpoints ---

@app.get("/")
async def read_root():
    return {"message": "Welcome to the User Service!"}

@app.post("/login/access-token", response_model=Token)
async def login_access_token(session: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=create_access_token(user.id, expires_delta=access_token_expires)
    )

@app.post("/login/test-token", response_model=UserPublic)
async def test_token(current_user: User = CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user

@app.post("/users/register", response_model=UserPublic)
async def register_user(*, session: Session = Depends(get_db), user_in: UserRegister) -> Any:
    """Register a new user."""
    user = session.exec(select(User).where(User.email == user_in.email)).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    hashed_password = get_password_hash(user_in.password)
    user_create = UserCreate(email=user_in.email, password=user_in.password, full_name=user_in.full_name, risk_appetite=user_in.risk_appetite)
    user_db = User.model_validate(user_create, update={"hashed_password": hashed_password})
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db

@app.get("/users/{user_id}", response_model=UserPublic)
async def get_user_info(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """Retrieves user information by ID."""
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=UserPublic)
async def update_user(
    user_id: uuid.UUID,
    user_in: UserCreate,
    current_user: User = CurrentUser,
    session: Session = Depends(get_db)
) -> Any:
    """Update a user by superuser."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_user.is_superuser and user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    if user_in.password is not None:
        hashed_password = get_password_hash(user_in.password)
        user_in.password = hashed_password
    else:
        user_in.password = user.hashed_password
    update_dict = user_in.model_dump(exclude_unset=True)
    user.sqlmodel_update(update_dict)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.post("/password-recovery/{email}", response_model=Message)
async def recover_password(email: str, session: Session = Depends(get_db)) -> Message:
    """
    Password Recovery
    """
    user = session.exec(select(User).where(User.email == email)).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    # Placeholder for sending email, in a real app this would call an email service
    # password_reset_token = generate_password_reset_token(email=email)
    # email_data = generate_reset_password_email(
    #     email_to=user.email, email=email, token=password_reset_token
    # )
    # send_email(
    #     email_to=user.email,
    #     subject=email_data.subject,
    #     html_content=email_data.html_content,
    # )
    return Message(message="Password recovery email sent (placeholder)")

@app.post("/reset-password/", response_model=Message)
async def reset_password(session: Session = Depends(get_db), body: NewPassword = Depends()) -> Message:
    """
    Reset password
    """
    # Placeholder for verifying token, in a real app this would use the generated token
    # email = verify_password_reset_token(token=body.token)
    # if not email:
    #     raise HTTPException(status_code=400, detail="Invalid token")
    
    # For now, let's assume the token verification passes for demo purposes and use a direct email (NOT FOR PRODUCTION)
    email = "test@example.com" # REPLACE WITH ACTUAL TOKEN VERIFICATION

    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(password=body.new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    return Message(message="Password updated successfully") 