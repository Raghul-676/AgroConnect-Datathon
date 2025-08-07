"""
Soil analysis data models
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum

class SoilTexture(str, Enum):
    """Soil texture classifications"""
    CLAY = "clay"
    SANDY = "sandy"
    LOAM = "loam"
    SILT = "silt"
    CLAY_LOAM = "clay_loam"
    SANDY_LOAM = "sandy_loam"
    SILT_LOAM = "silt_loam"
    SANDY_CLAY = "sandy_clay"
    SILTY_CLAY = "silty_clay"
    SANDY_CLAY_LOAM = "sandy_clay_loam"
    SILTY_CLAY_LOAM = "silty_clay_loam"

class NutrientLevels(BaseModel):
    """Nutrient levels in soil"""
    # Macro nutrients (kg/ha)
    nitrogen: float = Field(..., ge=0, description="Nitrogen content in kg/ha")
    phosphorus: float = Field(..., ge=0, description="Phosphorus content in kg/ha")
    potassium: float = Field(..., ge=0, description="Potassium content in kg/ha")
    
    # Secondary nutrients (mg/kg)
    calcium: float = Field(..., ge=0, description="Calcium content in mg/kg")
    magnesium: float = Field(..., ge=0, description="Magnesium content in mg/kg")
    sulfur: float = Field(..., ge=0, description="Sulfur content in mg/kg")
    
    # Micro nutrients (mg/kg)
    iron: float = Field(..., ge=0, description="Iron content in mg/kg")
    manganese: float = Field(..., ge=0, description="Manganese content in mg/kg")
    zinc: float = Field(..., ge=0, description="Zinc content in mg/kg")

class SoilParameters(BaseModel):
    """Complete soil parameters for analysis"""
    ph: float = Field(..., ge=0, le=14, description="Soil pH value (0-14)")
    salinity: float = Field(..., ge=0, description="Soil salinity (dS/m)")
    texture: SoilTexture = Field(..., description="Soil texture type")
    bulk_density: float = Field(..., ge=0, le=3.0, description="Bulk density in g/cm³")
    nutrients: NutrientLevels = Field(..., description="Nutrient levels in soil")
    
    @validator('ph')
    def validate_ph(cls, v):
        if not 0 <= v <= 14:
            raise ValueError('pH must be between 0 and 14')
        return v
    
    @validator('bulk_density')
    def validate_bulk_density(cls, v):
        if not 0.5 <= v <= 2.5:
            raise ValueError('Bulk density must be between 0.5 and 2.5 g/cm³')
        return v

class CropRequest(BaseModel):
    """Request model for soil analysis"""
    soil_parameters: SoilParameters = Field(..., description="Soil parameters")
    crop_name: str = Field(..., min_length=1, description="Name of the crop to analyze")
    
    @validator('crop_name')
    def validate_crop_name(cls, v):
        return v.strip().lower()

class FertilizerRecommendation(BaseModel):
    """Fertilizer recommendation model"""
    name: str = Field(..., description="Fertilizer name")
    amount: float = Field(..., ge=0, description="Recommended amount")
    unit: str = Field(..., description="Unit of measurement (kg/ha, g/m², etc.)")
    application_method: str = Field(..., description="How to apply the fertilizer")
    timing: str = Field(..., description="When to apply the fertilizer")

class AnalysisResult(BaseModel):
    """Soil analysis result model"""
    suitability_score: float = Field(..., ge=0, le=100, description="Suitability score (0-100)")
    category: str = Field(..., description="Analysis category: excellent, average, or bad")
    message: str = Field(..., description="Detailed analysis message")
    recommendations: List[str] = Field(default=[], description="General recommendations")
    fertilizer_recommendations: List[FertilizerRecommendation] = Field(
        default=[], description="Specific fertilizer recommendations"
    )
    alternative_crops: List[str] = Field(
        default=[], description="Alternative crop suggestions (for 'bad' category)"
    )
    cultivation_tips: List[str] = Field(
        default=[], description="Cultivation tips (for 'excellent' category)"
    )
