"""FastAPI application entry point"""

import contextlib
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import api_router
from app.models import Base, DatabaseManager

# Create data directory
Path("data").mkdir(exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="High-performance RAG Intelligent Agent Assistant",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Database manager
db_manager = DatabaseManager(settings.database_url)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await db_manager.create_tables()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
    }


# Expose db_manager for dependency injection
@app.get("/db")  # Temporary for testing
async def get_db():
    """Get database manager (temporary)"""
    return db_manager


# Create a context manager for database sessions
@contextlib.asynccontextmanager
async def get_db_session():
    """Get database session"""
    async with db_manager.async_session() as session:
        yield session


# Export for dependency injection
__all__ = ["app", "db_manager", "get_db_session"]
