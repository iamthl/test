import os
import uuid
from datetime import datetime, date, timedelta
import asyncio
from typing import List, Dict, Optional

import httpx
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import torch
import torch.nn as nn
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib # Import joblib for saving/loading scaler

from .models import UserPublic, PortfolioHolding, Portfolio, PriceData, Recommendation, LSTMModel  # Import all necessary models
from .data_processing import preprocess_data, inverse_transform_data
from .model_config import MODEL_CONFIG

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

async def fetch_historical_price_data(symbol: str, instrument_type: str, start_date: date, end_date: date) -> List[Dict]:
    async with httpx.AsyncClient() as client:
        try:
            # Adjust the endpoint based on how market_data_service exposes historical data
            # Assuming an endpoint like /market-data/historical/{instrument_type}/{symbol}?start_date=...&end_date=...
            response = await client.get(
                f"{MARKET_DATA_SERVICE_URL}/market-data/historical/{symbol}",
                params={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "instrument_type": instrument_type
                }
            )
            response.raise_for_status()
            return response.json()["data"]
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Market Data Service error: {e.response.text}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Network error with Market Data Service: {e}")

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

# --- Internal Helper for Model Training ---
async def _train_model(
    symbol: str,
    instrument_type: str,
    learning_rate: float,
    num_epochs: int,
    model_save_directory: str,
    end_date: Optional[date] = None # New argument for specifying training end date
):
    model_config = MODEL_CONFIG.get(instrument_type.lower())
    if not model_config:
        raise ValueError(f"No model configuration found for instrument type: {instrument_type}")

    sequence_length = model_config["sequence_length"]
    input_size = model_config["input_size"]
    hidden_size = model_config["hidden_size"]
    num_layers = model_config["num_layers"]
    output_size = model_config["output_size"]
    dropout = model_config["dropout"]
    
    print(f"Starting internal training for {symbol} ({instrument_type}) up to {end_date if end_date else 'today'}")
    
    # Fetch historical data
    actual_end_date = end_date if end_date else date.today()
    start_date = actual_end_date - timedelta(days=365 * 5) # Fetch 5 years of data
    historical_data_response = await fetch_historical_price_data(symbol, instrument_type, start_date, actual_end_date)
    
    if not historical_data_response:
        raise ValueError(f"No historical data found for {symbol} ({instrument_type}). Cannot train model.")

    df = pd.DataFrame(historical_data_response)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Use 'close' price for training
    dataset, scaler = preprocess_data(df, 'close', sequence_length)
    
    if len(dataset) == 0:
        raise ValueError(f"Not enough data after preprocessing for {symbol} ({instrument_type}). Cannot train model.")

    train_loader = torch.utils.data.DataLoader(dataset, batch_size=64, shuffle=True)

    model = LSTMModel(input_size, hidden_size, num_layers, output_size, dropout)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(num_epochs):
        for batch_idx, (data, target) in enumerate(train_loader):
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{num_epochs}, Loss: {loss.item():.4f}")

    # Create directory if it doesn't exist
    save_dir = os.path.join(model_save_directory, instrument_type)
    os.makedirs(save_dir, exist_ok=True)
    
    model_path = os.path.join(save_dir, f"{symbol}_lstm_model.pth")
    scaler_path = os.path.join(save_dir, f"{symbol}_scaler.joblib") # Define scaler path

    torch.save(model.state_dict(), model_path)
    joblib.dump(scaler, scaler_path) # Save the scaler

    print(f"Model for {symbol} ({instrument_type}) trained and saved to {model_path}")
    print(f"Scaler for {symbol} ({instrument_type}) saved to {scaler_path}")
    return model_path # Return the path to the saved model

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

class TrainingRequest(BaseModel):
    symbol: str
    instrument_type: str # e.g., "VN_STOCK", "VN_INDEX", "INTERNATIONAL_INDEX", "FOREX"
    learning_rate: float = 0.001
    num_epochs: int = 100
    model_save_directory: str = "./models" # Directory to save models
    end_date: Optional[date] = None # Optional training end date


class PredictionRequest(BaseModel):
    symbol: str
    instrument_type: str # e.g., "VN_STOCK", "VN_INDEX", "INTERNATIONAL_INDEX", "FOREX"


@app.post("/train")
async def train_model(request: TrainingRequest):
    try:
        await _train_model(
            request.symbol,
            request.instrument_type,
            request.learning_rate,
            request.num_epochs,
            request.model_save_directory,
            request.end_date # Pass the end_date from the request
        )
        return {"message": f"Model for {request.symbol} ({request.instrument_type}) trained and saved."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict")
async def predict_price(request: PredictionRequest):
    try:
        model_config = MODEL_CONFIG.get(request.instrument_type.lower())
        if not model_config:
            raise HTTPException(status_code=400, detail=f"No model configuration found for instrument type: {request.instrument_type}")

        sequence_length = model_config["sequence_length"]
        input_size = model_config["input_size"]
        hidden_size = model_config["hidden_size"]
        num_layers = model_config["num_layers"]
        output_size = model_config["output_size"]
        dropout = model_config["dropout"]

        model_path = os.path.join("./models", request.instrument_type, f"{request.symbol}_lstm_model.pth")
        scaler_path = os.path.join("./models", request.instrument_type, f"{request.symbol}_scaler.joblib")
        
        # If model or scaler not found, train it up to today's date
        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            print(f"Model or scaler not found for {request.symbol} ({request.instrument_type}). Initiating training...")
            try:
                # Use default training parameters for auto-training, ending today
                await _train_model(
                    request.symbol,
                    request.instrument_type,
                    learning_rate=0.001, # Default learning rate for auto-training
                    num_epochs=100,      # Default epochs for auto-training
                    model_save_directory="./models",
                    end_date=date.today() # Auto-train up to today
                )
                print(f"Training completed for {request.symbol} ({request.instrument_type}).")
            except Exception as train_e:
                raise HTTPException(status_code=500, detail=f"Failed to train model for prediction: {train_e}")

        model = LSTMModel(input_size, hidden_size, num_layers, output_size, dropout)
        model.load_state_dict(torch.load(model_path))
        model.eval()

        # Load the saved scaler
        scaler = joblib.load(scaler_path)

        # Fetch recent historical data for prediction input
        end_date = date.today()
        start_date = end_date - timedelta(days=sequence_length * 2) # Fetch enough data to form sequence
        historical_data = await fetch_historical_price_data(request.symbol, request.instrument_type, start_date, end_date)
        
        if not historical_data:
            raise HTTPException(status_code=400, detail="Not enough historical data to make a prediction.")

        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Use 'close' price for prediction
        price_data = df['close'].values.reshape(-1, 1)

        # Use the loaded scaler to transform the prediction input
        scaled_price_data = scaler.transform(price_data) # Use transform, not fit_transform
        
        if len(scaled_price_data) < sequence_length:
            raise HTTPException(status_code=400, detail="Not enough historical data to form a sequence for prediction.")

        input_sequence = scaled_price_data[-sequence_length:]
        input_tensor = torch.tensor(input_sequence, dtype=torch.float32).unsqueeze(0) # Add batch dimension

        with torch.no_grad():
            prediction = model(input_tensor)
        
        predicted_price = scaler.inverse_transform(prediction.numpy())

        return {"predicted_price": predicted_price[0][0]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 