# Jobs ML Recommendation Service

ML/Analytics service for job application recommendations and data analysis.

## Overview

This service provides:
- Personalized job application recommendations
- Company-level analytics and metrics
- User-level insights and trends
- Company and location deduplication
- Machine learning models for predictions

## Architecture

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL (separate from jobs service)
- **Message Queue**: Kafka (consumes events from jobs service)
- **Cache**: Redis (optional, for recommendation caching)

## Project Structure

```
data/jobs/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── domains/
│   │   ├── analytics/          # Analytics domain
│   │   ├── recommendations/    # Recommendation domain
│   │   ├── company_dedup/      # Company deduplication
│   │   └── models/             # ML models
│   ├── consumers/              # Kafka consumers
│   ├── api/                    # REST API routes
│   └── database/               # Database models and migrations
├── tests/
├── models/                     # Trained ML models storage
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── ARCHITECTURE.md             # Link to detailed architecture
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL
- Kafka (or use docker-compose)
- Redis (optional)

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run database migrations:**
   ```bash
   # TODO: Add Alembic migrations
   ```

4. **Start the service:**
   ```bash
   # Development
   uvicorn app.main:app --reload --port 3020
   
   # Or with Docker
   docker-compose up
   ```

## API Endpoints

### Recommendations
- `GET /api/v1/recommendations/{user_id}` - Get recommendations
- `GET /api/v1/recommendations/{user_id}/hot-opportunities` - Hot opportunities
- `GET /api/v1/recommendations/{user_id}/needs-attention` - Needs attention

### Analytics
- `GET /api/v1/analytics/{user_id}/overview` - User overview
- `GET /api/v1/analytics/{user_id}/company/{company_id}` - Company metrics
- `GET /api/v1/analytics/{user_id}/trends` - Time-series trends

### Companies
- `POST /api/v1/companies/deduplicate` - Deduplicate company
- `GET /api/v1/companies/{company_id}/metrics` - Company metrics

## Development Status

🚧 **In Development** - This service is currently being implemented.

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed architecture and implementation plan.
