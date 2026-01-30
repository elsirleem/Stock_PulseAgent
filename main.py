"""
StockPulse WhatsApp Agent - Main Application Entry Point

A personal AI financial agent that allows users to track their stock portfolios
and watchlists via WhatsApp.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.api import router
from app.config import get_settings
from app.database import init_db
from app.agent import create_agent
from app.scheduler import start_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting StockPulse WhatsApp Agent...")
    
    # Initialize database
    logger.info("📦 Initializing database...")
    init_db()
    
    # Initialize the agent
    logger.info("🤖 Initializing AI agent...")
    create_agent()
    
    # Start the scheduler for daily updates
    logger.info("⏰ Starting scheduler...")
    start_scheduler()
    
    logger.info("✅ StockPulse is ready!")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down StockPulse...")


# Create FastAPI application
app = FastAPI(
    title="StockPulse WhatsApp Agent",
    description="A personal AI financial agent for tracking stock portfolios via WhatsApp",
    version="1.0.0",
    lifespan=lifespan
)

# Include API routes
app.include_router(router)


if __name__ == "__main__":
    settings = get_settings()
    
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
