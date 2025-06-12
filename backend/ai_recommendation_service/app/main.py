import os
import uuid
from datetime import datetime, date
from typing import List, Dict, Optional

import httpx
from fastapi import FastAPI, HTTPException, Depends, Header

from .models import UserPublic, PortfolioHolding, Portfolio, PriceData, Recommendation  # Import all necessary models

# --- External Service URLs ---
CUSTOMER_SERVICE_URL = os.getenv("CUSTOMER_SERVICE_URL", "http://localhost:8001")
PORTFOLIO_SERVICE_URL = os.getenv("PORTFOLIO_SERVICE_URL", "http://localhost:8002")
MARKET_DATA_SERVICE_URL = os.getenv("MARKET_DATA_SERVICE_URL", "http://localhost:8003")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="AI Recommendation Service",
    description="Analyzes user data and market data to provide investment recommendations."
)

# --- Dependencies for Authorization (Simplified) ---
async def get_current_user_id(x_user_id: uuid.UUID = Header(..., alias="X-User-ID")) -> uuid.UUID:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-ID header missing")
    return x_user_id

# --- Helper functions to fetch data from other services ---
async def fetch_user_data(user_id: uuid.UUID, auth_header: Dict[str, str]) -> UserPublic:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{CUSTOMER_SERVICE_URL}/users/{user_id}", headers=auth_header)
            response.raise_for_status()
            return UserPublic(**response.json())
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"User Service error: {e.response.text}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Network error with User Service: {e}")

async def fetch_portfolio_data(user_id: uuid.UUID, auth_header: Dict[str, str]) -> Portfolio:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{PORTFOLIO_SERVICE_URL}/portfolio/{user_id}", headers=auth_header)
            response.raise_for_status()
            return Portfolio(**response.json())
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Portfolio Service error: {e.response.text}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Network error with Portfolio Service: {e}")

async def fetch_market_data(symbol: str) -> Optional[PriceData]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{MARKET_DATA_SERVICE_URL}/market-data/current/{symbol}")
            response.raise_for_status()
            return PriceData(**response.json())
        except httpx.HTTPStatusError as e:
            print(f"Warning: Could not fetch market data for {symbol}: {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"Warning: Network error fetching market data for {symbol}: {e}")
            return None

# --- Mock ML/Recommendation Logic (Replace with actual ML model) ---
async def generate_mock_recommendations(
    user: UserPublic,
    portfolio: Portfolio,
    market_data: Dict[str, PriceData]
) -> List[Recommendation]:
    """
    Simulates AI recommendation logic based on user's risk appetite, portfolio, and market data.
    This would be replaced by an actual LSTM model.
    """
    recommendations = []

    # Example: Simple logic for mock recommendations
    if user.risk_appetite == "conservative":
        if "MSFT" in market_data:
            recommendations.append(Recommendation(
                user_id=user.id,
                asset_symbol="MSFT",
                recommendation_type="buy",
                strength=0.8,
                reason="Stable tech stock, good for conservative growth."
            ))
    elif user.risk_appetite == "aggressive":
        if "ETH" in market_data:
            recommendations.append(Recommendation(
                user_id=user.id,
                asset_symbol="ETH",
                recommendation_type="buy",
                strength=0.9,
                reason="High growth potential in cryptocurrency market."
            ))

    # Mock a sell recommendation if user holds AAPL and its price is 'low' (mocked)
    for holding in portfolio.holdings:
        if holding.symbol == "AAPL" and holding.quantity > 0:
            current_aapl_price = market_data.get("AAPL")
            if current_aapl_price and current_aapl_price.price < 160: # Mock condition
                recommendations.append(Recommendation(
                    user_id=user.id,
                    asset_symbol="AAPL",
                    recommendation_type="sell",
                    strength=0.6,
                    reason="Potential short-term correction, consider re-entry later."
                ))

    return recommendations

# --- API Endpoints ---

@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Recommendation Service!"}

@app.get("/recommendations/{user_id}", response_model=List[Recommendation])
async def get_recommendations_for_user(user_id: uuid.UUID, current_user_id: uuid.UUID = Depends(get_current_user_id)):
    """
    Generates and retrieves investment recommendations for a specific user.
    Requires X-User-ID header for authorization.
    """
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized: Cannot access other users' recommendations.")

    auth_header = {"X-User-ID": str(user_id)} # Pass user ID in header for inter-service auth

    # Fetch necessary data from other services
    user_data = await fetch_user_data(user_id, auth_header)
    portfolio_data = await fetch_portfolio_data(user_id, auth_header)

    # Fetch market data for relevant symbols (e.g., from portfolio, or general interest)
    symbols_to_fetch = set([h.symbol for h in portfolio_data.holdings] + ["AAPL", "GOOGL", "MSFT", "BTC", "ETH"]) # Example symbols
    market_data_tasks = [fetch_market_data(s) for s in symbols_to_fetch]
    market_data_results = await asyncio.gather(*market_data_tasks)

    # Convert list of PriceData (some might be None) to a dictionary for easy lookup
    current_market_prices = {
        md.symbol: md for md in market_data_results if md is not None
    }

    # Generate recommendations using mock ML logic
    recommendations = await generate_mock_recommendations(
        user_data, portfolio_data, current_market_prices
    )

    if not recommendations:
        raise HTTPException(status_code=404, detail="No recommendations found for this user at this time.")

    return recommendations 