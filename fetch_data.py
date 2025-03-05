import yfinance as yf
import pandas as pd

# Select stock (Tesla - TSLA)
ticker = "TSLA"

# Download latest stock data (from 2020 to today)
df = yf.download(ticker, start="2020-01-01")  # No 'end' date ensures latest data is fetched

# Reset index so 'Date' is a normal column
df.reset_index(inplace=True)

# Keep only necessary columns & ensure correct ordering
df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]

# Save to CSV without extra headers
df.to_csv("stock_data.csv", index=False)

print("✅ Latest stock data (up to today) downloaded successfully!")
