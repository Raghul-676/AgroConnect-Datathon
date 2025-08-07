"""
Soil analysis API routes
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from loguru import logger

from app.models.soil import CropRequest, AnalysisResult, SoilTexture
from app.services.analysis_engine import SoilAnalysisEngine
from app.data.crop_requirements import get_all_crops
from app.ml.soil_classifier import SoilSuitabilityClassifier

router = APIRouter()

# Global analysis engine instance
analysis_engine = SoilAnalysisEngine()

@router.post("/analyze", response_model=AnalysisResult)
async def analyze_soil(request: CropRequest) -> AnalysisResult:
    """
    Analyze soil parameters for crop suitability
    
    Returns analysis with recommendations in three categories:
    - excellent: Soil is ideal for the crop with cultivation tips
    - average: Soil is suitable with fertilizer recommendations
    - bad: Soil needs major improvement with alternative crop suggestions
    """
    try:
        logger.info(f"Analyzing soil for crop: {request.crop_name}")
        
        result = analysis_engine.analyze_soil(
            soil_params=request.soil_parameters,
            crop_name=request.crop_name
        )
        
        logger.info(f"Analysis completed. Category: {result.category}, Score: {result.suitability_score:.1f}")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during analysis")

@router.get("/crops", response_model=List[str])
async def get_supported_crops() -> List[str]:
    """Get list of all supported crops"""
    try:
        crops = get_all_crops()
        logger.info(f"Retrieved {len(crops)} supported crops")
        return sorted(crops)
    except Exception as e:
        logger.error(f"Error retrieving crops: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving supported crops")

@router.get("/soil-textures", response_model=List[str])
async def get_soil_textures() -> List[str]:
    """Get list of all supported soil textures"""
    try:
        textures = [texture.value for texture in SoilTexture]
        logger.info(f"Retrieved {len(textures)} soil textures")
        return sorted(textures)
    except Exception as e:
        logger.error(f"Error retrieving soil textures: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving soil textures")

@router.get("/crop-requirements/{crop_name}")
async def get_crop_requirements(crop_name: str) -> Dict[str, Any]:
    """Get detailed requirements for a specific crop"""
    try:
        from app.data.crop_requirements import get_crop_requirements
        
        requirements = get_crop_requirements(crop_name.lower())
        if not requirements:
            raise HTTPException(status_code=404, detail=f"Crop '{crop_name}' not found")
        
        logger.info(f"Retrieved requirements for crop: {crop_name}")
        return {
            "crop": crop_name.lower(),
            "requirements": requirements
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving crop requirements: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving crop requirements")

@router.post("/train-model")
async def train_model(n_samples: int = 10000) -> Dict[str, Any]:
    """
    Train/retrain the machine learning model
    
    This endpoint allows retraining the model with new data.
    Use with caution in production environments.
    """
    try:
        logger.info(f"Starting model training with {n_samples} samples...")
        
        classifier = SoilSuitabilityClassifier()
        results = classifier.train(n_samples=n_samples)
        
        logger.info("Model training completed successfully")
        return {
            "message": "Model trained successfully",
            "training_results": results,
            "samples_used": n_samples
        }
    except Exception as e:
        logger.error(f"Model training error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model training failed: {str(e)}")

@router.get("/model-info")
async def get_model_info() -> Dict[str, Any]:
    """Get information about the current ML model"""
    try:
        classifier = SoilSuitabilityClassifier()
        
        # Try to load model to check if it exists
        try:
            classifier.load_model()
            feature_importance = classifier.get_feature_importance()
            model_loaded = True
        except:
            feature_importance = {}
            model_loaded = False
        
        return {
            "model_loaded": model_loaded,
            "model_type": "Random Forest Classifier",
            "feature_importance": feature_importance,
            "supported_crops": get_all_crops(),
            "supported_textures": [texture.value for texture in SoilTexture]
        }
    except Exception as e:
        logger.error(f"Error retrieving model info: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving model information")

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for the soil analysis service"""
    try:
        # Basic health checks
        crops_available = len(get_all_crops()) > 0
        textures_available = len([texture.value for texture in SoilTexture]) > 0
        
        if crops_available and textures_available:
            return {"status": "healthy", "service": "soil_analysis"}
        else:
            return {"status": "degraded", "service": "soil_analysis"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")
