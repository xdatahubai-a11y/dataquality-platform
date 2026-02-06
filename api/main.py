"""FastAPI application entry point for DataQuality Platform."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.dependencies import engine
from api.models.database import Base
from api.routers import jobs, metrics, rules, sources

app = FastAPI(
    title=settings.app_name,
    description="Enterprise Data Quality Platform with Spark-based profiling",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rules.router)
app.include_router(sources.router)
app.include_router(jobs.router)
app.include_router(metrics.router)


@app.on_event("startup")
def on_startup() -> None:
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}
