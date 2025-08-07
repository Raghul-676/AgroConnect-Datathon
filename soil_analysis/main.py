"""
Soil Analysis Backend API
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import uvicorn

from app.api.routes import soil_analysis
from app.core.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Soil Analysis API",
    description="Backend API for soil analysis and crop suitability assessment",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(soil_analysis.router, prefix="/api/v1", tags=["soil-analysis"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Soil Analysis API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    logger.info("Starting Soil Analysis API...")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
