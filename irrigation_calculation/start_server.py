#!/usr/bin/env python3
"""
Startup script for the Irrigation Calculation System
"""

import os
import sys
import logging
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from irrigation_ml.model_manager import model_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up the environment for the irrigation system"""
    
    # Create necessary directories
    directories = ['models', 'data', 'logs']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    # Check for .env file
    if not os.path.exists('.env'):
        logger.warning("No .env file found. Creating from template...")
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            logger.info("Created .env file from template. Please configure your API keys.")
        else:
            logger.warning("No .env.example found. Please create .env file manually.")

def initialize_models():
    """Initialize and train ML models if needed"""
    
    logger.info("Checking model status...")
    
    if model_manager.should_retrain():
        logger.info("Training/retraining models...")
        
        if not model_manager.predictor.is_trained:
            # First time training
            model_manager.train_initial_models(n_samples=10000)
        else:
            # Retrain existing models
            model_manager.retrain_models(n_samples=15000)
    else:
        logger.info("Models are up to date")
    
    # Display model info
    info = model_manager.get_model_info()
    logger.info(f"Model version: {info['version']}")
    logger.info(f"Last trained: {info['last_trained']}")
    logger.info(f"Training samples: {info['training_samples']}")

def start_server():
    """Start the FastAPI server"""
    
    import uvicorn
    from main import app
    
    logger.info("Starting irrigation calculation server...")
    logger.info("Server will be available at: http://localhost:8001")
    logger.info("API documentation at: http://localhost:8001/docs")

    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=False,  # Set to True for development
        log_level="info"
    )

def main():
    """Main startup function"""
    
    print("🌿 Irrigation Calculation System")
    print("=" * 40)
    
    try:
        # Setup environment
        setup_environment()
        
        # Initialize models
        initialize_models()
        
        # Start server
        start_server()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
