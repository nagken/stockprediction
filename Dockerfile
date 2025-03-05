# Use official Python image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy everything to /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Run FastAPI app
CMD ["uvicorn", "stock_api:app", "--host", "0.0.0.0", "--port", "8080"]
