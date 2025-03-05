import requests

url = "http://localhost:8080/predict/"
params = {"tickers": "AAPL,GOOGL,TSLA"}

response = requests.get(url, params=params)
print(response.json())  # Should return stock predictions
