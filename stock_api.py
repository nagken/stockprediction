from fastapi import FastAPI, HTTPException, Query
import numpy as np
import tensorflow as tf
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import os
import uvicorn

app = FastAPI()

# Load trained model
try:
    model = tf.keras.models.load_model("stock_model.h5")
except Exception as e:
    raise RuntimeError(f"Error loading model: {str(e)}")

# Initialize Scaler
scaler = MinMaxScaler(feature_range=(0, 1))

@app.get("/")
def health_check():
    """Health check endpoint to verify if API is running."""
    return {"message": "Stock Market Prediction API is running!"}

@app.get("/predict/")
def predict_stocks(tickers: str = Query(..., description="Comma-separated stock tickers")):
    try:
        tickers_list = [t.strip().upper() for t in tickers.split(",")]

        if not tickers_list:
            raise HTTPException(status_code=400, detail="No valid stock tickers provided.")

        predictions = {}

        for ticker in tickers_list:
            try:
                # Fetch stock data (365 days to ensure sufficient data)
                df = yf.download(ticker, period="365d", auto_adjust=True)

                # Debugging Output
                print(f"Fetched Data for {ticker}:\n", df.tail())

                # Ensure data is valid
                if df.empty:
                    predictions[ticker] = {"error": "No stock data found"}
                    continue

                # Feature Engineering
                df["MA_50"] = df["Close"].rolling(window=50).mean()
                df["MA_200"] = df["Close"].rolling(window=200).mean()

                # RSI Calculation
                delta = df["Close"].diff(1)
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df["RSI"] = 100 - (100 / (1 + rs))

                # MACD Calculation
                short_ema = df["Close"].ewm(span=12, adjust=False).mean()
                long_ema = df["Close"].ewm(span=26, adjust=False).mean()
                df["MACD"] = short_ema - long_ema

                # Drop NaN values but check if enough data remains
                df.dropna(inplace=True)

                if len(df) < 100:  # Ensure at least 100 days of valid data
                    predictions[ticker] = {"error": "Not enough valid data for prediction"}
                    continue

                # Normalize the data
                try:
                    scaled_data = scaler.fit_transform(df[["Close", "MA_50", "MA_200", "RSI", "MACD"]])
                    X_input = np.array([scaled_data[-50:]])  # Last 50 days for prediction
                except ValueError:
                    predictions[ticker] = {"error": "Data scaling failed, insufficient historical data"}
                    continue

                # Make Prediction
                prediction = model.predict(X_input)[0][0]
                predicted_price = scaler.inverse_transform([[prediction, 0, 0, 0, 0]])[0][0]

                predictions[ticker] = {"Predicted Price": round(predicted_price, 2)}

            except Exception as e:
                predictions[ticker] = {"error": f"Failed to predict: {str(e)}"}

        return {"Predictions": predictions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

if __name__ == "__main__":
    """Run API using Uvicorn when executing locally or in Cloud Run"""
    port = int(os.getenv("PORT", 8080))  # Ensure Cloud Run uses the correct port
    uvicorn.run(app, host="0.0.0.0", port=port)
