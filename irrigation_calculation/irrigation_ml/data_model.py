from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
import pandas as pd
import numpy as np

class CropType(Enum):
    RICE = "rice"
    WHEAT = "wheat"
    SUGARCANE = "sugarcane"
    COTTON = "cotton"

class SoilType(Enum):
    SANDY = "sandy"
    LOAMY = "loamy"
    CLAY = "clay"

class IrrigationMethod(Enum):
    DRIP = "drip"
    SPRINKLER = "sprinkler"
    FLOOD = "flood"

@dataclass
class CropCoefficients:
    """Crop coefficients for different growth stages"""
    initial: float  # Initial stage (Kc_ini)
    development: float  # Development stage (Kc_dev)
    mid_season: float  # Mid-season stage (Kc_mid)
    late_season: float  # Late season stage (Kc_end)
    
    # Growth stage durations in days
    initial_days: int
    development_days: int
    mid_season_days: int
    late_season_days: int
    
    # Root depth progression
    max_root_depth: float  # in meters
    
    # Water stress sensitivity
    stress_factor: float  # 0-1, higher means more sensitive

@dataclass
class SoilProperties:
    """Soil hydraulic properties"""
    field_capacity: float  # mm/m
    wilting_point: float  # mm/m
    bulk_density: float  # g/cm³
    infiltration_rate: float  # mm/hour
    water_holding_capacity: float  # mm/m
    drainage_coefficient: float  # 0-1

@dataclass
class IrrigationEfficiency:
    """Irrigation method efficiency factors"""
    application_efficiency: float  # 0-1
    distribution_uniformity: float  # 0-1
    water_loss_factor: float  # 0-1

class AgriculturalDatabase:
    """Database of agricultural parameters for irrigation calculations"""
    
    def __init__(self):
        self.crop_coefficients = self._initialize_crop_coefficients()
        self.soil_properties = self._initialize_soil_properties()
        self.irrigation_efficiency = self._initialize_irrigation_efficiency()
    
    def _initialize_crop_coefficients(self) -> Dict[CropType, CropCoefficients]:
        """Initialize crop coefficient database based on FAO guidelines"""
        return {
            CropType.RICE: CropCoefficients(
                initial=1.05, development=1.20, mid_season=1.20, late_season=0.90,
                initial_days=30, development_days=30, mid_season_days=60, late_season_days=30,
                max_root_depth=0.5, stress_factor=0.8
            ),
            CropType.WHEAT: CropCoefficients(
                initial=0.40, development=0.70, mid_season=1.15, late_season=0.40,
                initial_days=15, development_days=25, mid_season_days=50, late_season_days=30,
                max_root_depth=1.5, stress_factor=0.6
            ),
            CropType.SUGARCANE: CropCoefficients(
                initial=0.40, development=0.80, mid_season=1.25, late_season=0.75,
                initial_days=35, development_days=60, mid_season_days=180, late_season_days=60,
                max_root_depth=1.2, stress_factor=0.7
            ),
            CropType.COTTON: CropCoefficients(
                initial=0.35, development=0.70, mid_season=1.15, late_season=0.50,
                initial_days=30, development_days=50, mid_season_days=55, late_season_days=45,
                max_root_depth=1.0, stress_factor=0.65
            )
        }
    
    def _initialize_soil_properties(self) -> Dict[SoilType, SoilProperties]:
        """Initialize soil properties database"""
        return {
            SoilType.SANDY: SoilProperties(
                field_capacity=120, wilting_point=60, bulk_density=1.6,
                infiltration_rate=30, water_holding_capacity=60, drainage_coefficient=0.8
            ),
            SoilType.LOAMY: SoilProperties(
                field_capacity=250, wilting_point=120, bulk_density=1.4,
                infiltration_rate=15, water_holding_capacity=130, drainage_coefficient=0.6
            ),
            SoilType.CLAY: SoilProperties(
                field_capacity=350, wilting_point=200, bulk_density=1.3,
                infiltration_rate=5, water_holding_capacity=150, drainage_coefficient=0.3
            )
        }
    
    def _initialize_irrigation_efficiency(self) -> Dict[IrrigationMethod, IrrigationEfficiency]:
        """Initialize irrigation efficiency database"""
        return {
            IrrigationMethod.DRIP: IrrigationEfficiency(
                application_efficiency=0.90, distribution_uniformity=0.85, water_loss_factor=0.05
            ),
            IrrigationMethod.SPRINKLER: IrrigationEfficiency(
                application_efficiency=0.75, distribution_uniformity=0.70, water_loss_factor=0.15
            ),
            IrrigationMethod.FLOOD: IrrigationEfficiency(
                application_efficiency=0.60, distribution_uniformity=0.60, water_loss_factor=0.25
            )
        }
    
    def get_crop_coefficient(self, crop: CropType, days_since_planting: int) -> float:
        """Get crop coefficient based on growth stage"""
        coeff = self.crop_coefficients[crop]
        
        if days_since_planting <= coeff.initial_days:
            return coeff.initial
        elif days_since_planting <= coeff.initial_days + coeff.development_days:
            # Linear interpolation during development stage
            progress = (days_since_planting - coeff.initial_days) / coeff.development_days
            return coeff.initial + (coeff.mid_season - coeff.initial) * progress
        elif days_since_planting <= (coeff.initial_days + coeff.development_days + coeff.mid_season_days):
            return coeff.mid_season
        else:
            # Linear interpolation during late season
            late_start = coeff.initial_days + coeff.development_days + coeff.mid_season_days
            progress = min(1.0, (days_since_planting - late_start) / coeff.late_season_days)
            return coeff.mid_season + (coeff.late_season - coeff.mid_season) * progress

@dataclass
class IrrigationFeatures:
    """Feature vector for machine learning models"""
    # Farm characteristics
    farm_size: float
    crop_type_encoded: int
    soil_type_encoded: int
    irrigation_method_encoded: int

    # Soil characteristics
    bulk_density: float  # g/cm³

    # Weather features
    temperature: float
    humidity: float
    wind_speed: float
    reference_et: float
    rainfall_today: float
    rainfall_forecast_3day: float
    irrigation_urgency_encoded: int

    # Temporal features
    days_since_last_irrigation: int
    days_since_planting: int
    season_encoded: int  # 0=winter, 1=summer, 2=monsoon, 3=post-monsoon

    # Soil moisture estimation
    estimated_soil_moisture: float

    # Crop stage
    crop_coefficient: float
    root_depth: float
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array for ML models"""
        return np.array([
            self.farm_size, self.crop_type_encoded, self.soil_type_encoded,
            self.irrigation_method_encoded, self.temperature, self.humidity,
            self.wind_speed, self.reference_et, self.rainfall_today,
            self.rainfall_forecast_3day, self.irrigation_urgency_encoded,
            self.days_since_last_irrigation, self.days_since_planting,
            self.season_encoded, self.estimated_soil_moisture,
            self.crop_coefficient, self.root_depth
        ])
    
    @classmethod
    def get_feature_names(cls) -> List[str]:
        """Get feature names for model training"""
        return [
            'farm_size', 'crop_type_encoded', 'soil_type_encoded',
            'irrigation_method_encoded', 'bulk_density', 'temperature', 'humidity',
            'wind_speed', 'reference_et', 'rainfall_today',
            'rainfall_forecast_3day', 'irrigation_urgency_encoded',
            'days_since_last_irrigation', 'days_since_planting',
            'season_encoded', 'estimated_soil_moisture',
            'crop_coefficient', 'root_depth'
        ]

@dataclass
class IrrigationTarget:
    """Target variables for machine learning models"""
    days_until_next_irrigation: int
    water_requirement_per_hectare: float  # liters per hectare
    irrigation_priority: int  # 0=low, 1=medium, 2=high
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'days_until_next_irrigation': self.days_until_next_irrigation,
            'water_requirement_per_hectare': self.water_requirement_per_hectare,
            'irrigation_priority': self.irrigation_priority
        }
