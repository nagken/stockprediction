import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# Load processed stock data
df = pd.read_csv("stock_data_features.csv", index_col="Date", parse_dates=True)

# Select features for training
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(df[["Close", "MA_50", "MA_200", "RSI", "MACD"]])

# Create training sequences
def create_sequences(data, time_steps=50):
    X, y = [], []
    for i in range(len(data) - time_steps):
        X.append(data[i:i+time_steps])
        y.append(data[i+time_steps, 0])  # Predicting 'Close' price
    return np.array(X), np.array(y)

X, y = create_sequences(scaled_data)
X_train, y_train = X[:-50], y[:-50]  # Last 50 days for testing
X_test, y_test = X[-50:], y[-50:]

# Build LSTM Model
model = Sequential([
    LSTM(64, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
    Dropout(0.2),
    LSTM(64, return_sequences=False),
    Dropout(0.2),
    Dense(32, activation='relu'),
    Dense(1)  # Predicting a single value
])

model.compile(optimizer="adam", loss="mean_squared_error")

# Train Model
model.fit(X_train, y_train, epochs=50, batch_size=16, validation_data=(X_test, y_test))

# Save Model
model.save("stock_model.h5")

print("✅ Model training completed and saved successfully!")
