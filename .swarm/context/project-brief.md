# Project Brief

## What is this project?
Enterprise data quality platform — profiling, rule evaluation, and reporting for structured data sources.

## Who uses it?
Data engineers and analysts who need to monitor data quality across multiple sources (PostgreSQL, SQLite, CSV, etc.)

## Key decisions made
- FastAPI for the API layer
- SQLAlchemy for ORM
- Pydantic for validation
- Local-first execution (no Spark dependency for basic operation)

## What matters most right now
- API reliability and correctness
- Test coverage for all endpoints
- Clean deprecation cleanup (Python 3.12+ compatibility)
