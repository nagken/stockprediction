import pandas as pd

# Load stock data
df = pd.read_csv("stock_data.csv")

# Remove any non-numeric rows (sometimes yfinance adds extra headers)
df = df[pd.to_datetime(df["Date"], errors="coerce").notna()]  # Keep only valid dates

# Convert numeric columns from strings to floats (force errors to NaN)
numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

# Drop any remaining NaN values (from conversion issues)
df = df.dropna()

# Ensure 'Date' is set as index
df["Date"] = pd.to_datetime(df["Date"])
df.set_index("Date", inplace=True)

# Feature Engineering: Add Moving Averages & Indicators
def add_features(df):
    df["MA_50"] = df["Close"].rolling(window=50).mean()
    df["MA_200"] = df["Close"].rolling(window=200).mean()
    
    # Relative Strength Index (RSI)
    delta = df["Close"].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # MACD Indicator
    short_ema = df["Close"].ewm(span=12, adjust=False).mean()
    long_ema = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = short_ema - long_ema

    return df.dropna()

df = add_features(df)

# Save processed data
df.to_csv("stock_data_features.csv")

print("✅ Feature Engineering Completed Successfully!")
