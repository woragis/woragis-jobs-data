FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create models directory (will be populated at runtime or by training)
RUN mkdir -p models

# Expose port
EXPOSE 3020

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3020", "--reload"]

