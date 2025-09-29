from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from src.api.routers import trading, health, llm, chart
from src.core.market.service import MarketService
from src.integrations.iq_option.service import IQOptionService
import logging

# Set up logging
logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LLM Trading Bot API",
    description="An AI-powered trading bot using LLMs to make trading decisions",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
market_service = MarketService()
iq_option_service = IQOptionService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting up LLM Trading Bot API")
    await market_service.startup()
    await iq_option_service.connect()
    
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up services on shutdown"""
    logger.info("Shutting down LLM Trading Bot API")
    await market_service.shutdown()
    await iq_option_service.disconnect()


# Include routers
app.include_router(trading.router, prefix="/api/v1", tags=["trading"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(llm.router, prefix="/api/v1", tags=["llm"])
app.include_router(chart.router, prefix="/api/v1", tags=["chart"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the LLM Trading Bot API"}