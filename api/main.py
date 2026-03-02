"""FastAPI application entry point for DataQuality Platform."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from api.config import settings
from api.dependencies import engine
from api.models.database import Base
from api.routers import jobs, metrics, rules, sources


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup: Create database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: Add any cleanup here if needed


app = FastAPI(
    title=settings.app_name,
    description="Enterprise Data Quality Platform with Spark-based profiling",
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rules.router)
app.include_router(sources.router)
app.include_router(jobs.router)
app.include_router(metrics.router)


@app.get("/api/health")
def health_check() -> dict:
    """Health check endpoint with version and database connectivity status."""
    # Test database connectivity
    database_status = "connected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        database_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "version": settings.app_version,
        "database": database_status
    }
