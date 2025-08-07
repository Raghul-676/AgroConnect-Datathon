from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

from .models import IrrigationPredictor
from .weather import WeatherService
from .data_model import (
    IrrigationFeatures, AgriculturalDatabase, 
    CropType, SoilType, IrrigationMethod
)

logger = logging.getLogger(__name__)

class IrrigationCalculator:
    """Main irrigation calculation engine combining ML predictions with agronomic principles"""
    
    def __init__(self, predictor: IrrigationPredictor, weather_service: WeatherService):
        self.predictor = predictor
        self.weather_service = weather_service
        self.agri_db = AgriculturalDatabase()
        
        # Ensure models are trained
        if not self.predictor.is_trained:
            logger.info("Training ML models...")
            self.predictor.train_models()
    
    def calculate_irrigation(self, farm_size: float, unit: str, crop: str,
                           soil: str, method: str, bulk_density: float,
                           last_irrigation: str, weather_data: Dict) -> Dict:
        """
        Calculate comprehensive irrigation recommendations

        Args:
            farm_size: Size of the farm
            unit: Unit of measurement (acres, hectares, sqmeters)
            crop: Crop type
            soil: Soil type
            method: Irrigation method
            bulk_density: Soil bulk density in g/cm³
            last_irrigation: Last irrigation date (YYYY-MM-DD)
            weather_data: Current weather data

        Returns:
            Dictionary with irrigation recommendations
        """
        
        # Convert inputs to standard formats
        farm_size_hectares = self._convert_to_hectares(farm_size, unit)
        crop_type = CropType(crop)
        soil_type = SoilType(soil)
        irrigation_method = IrrigationMethod(method)
        
        # Calculate temporal features
        last_irrigation_date = datetime.strptime(last_irrigation, "%Y-%m-%d")
        days_since_irrigation = (datetime.now() - last_irrigation_date).days
        
        # Estimate days since planting (simplified - in real app, this would be user input)
        days_since_planting = self._estimate_days_since_planting(crop_type, days_since_irrigation)
        
        # Get current season
        season = self._get_current_season()
        
        # Calculate crop coefficient
        crop_coeff = self.agri_db.get_crop_coefficient(crop_type, days_since_planting)
        
        # Estimate root depth
        max_root_depth = self.agri_db.crop_coefficients[crop_type].max_root_depth
        root_depth = min(max_root_depth, max_root_depth * (days_since_planting / 100))
        
        # Estimate soil moisture
        soil_moisture = self._estimate_soil_moisture(
            soil_type, days_since_irrigation, weather_data
        )
        
        # Create feature vector for ML prediction
        features = IrrigationFeatures(
            farm_size=farm_size_hectares,
            crop_type_encoded=list(CropType).index(crop_type),
            soil_type_encoded=list(SoilType).index(soil_type),
            irrigation_method_encoded=list(IrrigationMethod).index(irrigation_method),
            bulk_density=bulk_density,
            temperature=weather_data['temperature'],
            humidity=weather_data['humidity'],
            wind_speed=weather_data['wind_speed'],
            reference_et=weather_data['reference_et'],
            rainfall_today=weather_data['rainfall_today'],
            rainfall_forecast_3day=weather_data['rainfall_forecast_3day'],
            irrigation_urgency_encoded=self._encode_urgency(weather_data['irrigation_urgency']),
            days_since_last_irrigation=days_since_irrigation,
            days_since_planting=days_since_planting,
            season_encoded=season,
            estimated_soil_moisture=soil_moisture,
            crop_coefficient=crop_coeff,
            root_depth=root_depth
        )
        
        # Get ML predictions
        ml_predictions = self.predictor.predict(features)
        
        # Calculate final recommendations
        next_irrigation_date = self._calculate_next_irrigation_date(
            ml_predictions['days_until_irrigation']
        )
        
        total_water_liters = self._calculate_total_water_requirement(
            ml_predictions['water_per_hectare'], farm_size_hectares
        )
        
        smart_tip = self._generate_smart_tip(
            crop_type, soil_type, irrigation_method, weather_data,
            ml_predictions, soil_moisture
        )
        
        return {
            "next_irrigation_date": next_irrigation_date,
            "water_liters": total_water_liters,
            "tip": smart_tip
        }
    
    def _convert_to_hectares(self, size: float, unit: str) -> float:
        """Convert farm size to hectares"""
        if unit == "hectares":
            return size
        elif unit == "acres":
            return size * 0.404686  # 1 acre = 0.404686 hectares
        elif unit == "sqmeters":
            return size / 10000  # 1 hectare = 10,000 sq meters
        else:
            raise ValueError(f"Unknown unit: {unit}")
    
    def _estimate_days_since_planting(self, crop_type: CropType, days_since_irrigation: int) -> int:
        """Estimate days since planting based on crop type and irrigation history"""
        # Simplified estimation - in real app, this would be user input
        crop_coeff = self.agri_db.crop_coefficients[crop_type]
        total_crop_days = (crop_coeff.initial_days + crop_coeff.development_days + 
                          crop_coeff.mid_season_days + crop_coeff.late_season_days)
        
        # Assume we're somewhere in the middle of the crop cycle
        estimated_days = min(total_crop_days // 2 + days_since_irrigation * 2, total_crop_days)
        return max(1, estimated_days)
    
    def _get_current_season(self) -> int:
        """Get current season (0=winter, 1=summer, 2=monsoon, 3=post-monsoon)"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return 0  # Winter
        elif month in [3, 4, 5]:
            return 1  # Summer
        elif month in [6, 7, 8, 9]:
            return 2  # Monsoon
        else:
            return 3  # Post-monsoon
    
    def _estimate_soil_moisture(self, soil_type: SoilType, days_since_irrigation: int,
                              weather_data: Dict) -> float:
        """Estimate current soil moisture percentage"""
        
        soil_props = self.agri_db.soil_properties[soil_type]
        
        # Start with field capacity after irrigation
        initial_moisture = 100.0
        
        # Decrease based on days since irrigation and ET
        daily_depletion = weather_data['reference_et'] * 0.8
        moisture_loss = daily_depletion * days_since_irrigation
        
        # Add moisture from recent rainfall
        rainfall_contribution = weather_data['rainfall_today'] * 2
        
        # Calculate current moisture
        current_moisture = initial_moisture - moisture_loss + rainfall_contribution
        
        # Apply soil-specific adjustments
        if soil_type == SoilType.SANDY:
            current_moisture *= 0.8  # Sandy soil drains faster
        elif soil_type == SoilType.CLAY:
            current_moisture *= 1.2  # Clay soil retains more water
        
        return max(10, min(100, current_moisture))
    
    def _encode_urgency(self, urgency: str) -> int:
        """Encode irrigation urgency to integer"""
        urgency_map = {"low": 0, "medium": 1, "high": 2}
        return urgency_map.get(urgency, 1)
    
    def _calculate_next_irrigation_date(self, days_until: int) -> str:
        """Calculate next irrigation date"""
        next_date = datetime.now() + timedelta(days=days_until)
        return next_date.strftime("%Y-%m-%d")
    
    def _calculate_total_water_requirement(self, water_per_hectare: float, 
                                         farm_size_hectares: float) -> float:
        """Calculate total water requirement in liters"""
        total_liters = water_per_hectare * farm_size_hectares
        return round(total_liters, 0)
    
    def _generate_smart_tip(self, crop_type: CropType, soil_type: SoilType,
                          irrigation_method: IrrigationMethod, weather_data: Dict,
                          ml_predictions: Dict, soil_moisture: float) -> str:
        """Generate smart irrigation tip based on all available data with improved logic"""

        # Priority scoring system for dynamic tip selection
        tip_candidates = []

        # 1. CRITICAL CONDITIONS (Highest Priority)
        if soil_moisture < 25:
            tip_candidates.append({
                'priority': 10,
                'tip': f"🚨 CRITICAL: Soil moisture at {soil_moisture:.0f}% - irrigate immediately to prevent crop damage"
            })

        if ml_predictions.get('priority', 1) == 2:
            tip_candidates.append({
                'priority': 9,
                'tip': "⚠️ HIGH PRIORITY: ML model indicates urgent irrigation needed based on current conditions"
            })

        # 2. WEATHER-BASED TIPS (High Priority)
        rainfall_3day = weather_data.get('rainfall_forecast_3day', 0)
        temperature = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 60)

        if rainfall_3day > 50:
            tip_candidates.append({
                'priority': 8,
                'tip': f"🌧️ Heavy rainfall expected ({rainfall_3day:.0f}mm) - delay irrigation for 2-3 days"
            })
        elif rainfall_3day > 15:
            tip_candidates.append({
                'priority': 6,
                'tip': f"🌦️ Moderate rainfall expected ({rainfall_3day:.0f}mm) - reduce irrigation amount by 30-40%"
            })
        elif rainfall_3day < 2 and temperature > 32:
            tip_candidates.append({
                'priority': 7,
                'tip': f"☀️ Hot & dry conditions ({temperature:.0f}°C, {rainfall_3day:.0f}mm rain) - increase irrigation frequency"
            })

        if temperature > 38:
            tip_candidates.append({
                'priority': 8,
                'tip': f"🔥 Extreme heat ({temperature:.0f}°C) - irrigate early morning/late evening, increase frequency"
            })
        elif temperature < 15:
            tip_candidates.append({
                'priority': 5,
                'tip': f"❄️ Cool weather ({temperature:.0f}°C) - reduce irrigation frequency, water retention is higher"
            })

        if humidity < 30:
            tip_candidates.append({
                'priority': 6,
                'tip': f"🏜️ Very low humidity ({humidity}%) - increase irrigation to compensate for high evaporation"
            })
        elif humidity > 85:
            tip_candidates.append({
                'priority': 5,
                'tip': f"💨 High humidity ({humidity}%) - reduce irrigation frequency, lower evaporation rates"
            })

        # 3. SOIL MOISTURE TIPS (Medium-High Priority)
        if soil_moisture < 40:
            tip_candidates.append({
                'priority': 7,
                'tip': f"💧 Low soil moisture ({soil_moisture:.0f}%) - schedule irrigation within 1-2 days"
            })
        elif soil_moisture > 75:
            tip_candidates.append({
                'priority': 6,
                'tip': f"💦 High soil moisture ({soil_moisture:.0f}%) - delay next irrigation, monitor for waterlogging"
            })
        elif 50 <= soil_moisture <= 70:
            tip_candidates.append({
                'priority': 4,
                'tip': f"✅ Optimal soil moisture ({soil_moisture:.0f}%) - maintain current irrigation schedule"
            })

        # 4. CROP-SPECIFIC TIPS (Medium Priority)
        crop_coeff = self.agri_db.crop_coefficients[crop_type]
        days_since_irrigation = ml_predictions.get('days_until_irrigation', 3)

        if crop_type == CropType.RICE:
            if soil_moisture < 60:
                tip_candidates.append({
                    'priority': 6,
                    'tip': "🌾 Rice requires consistent moisture - maintain soil saturation, especially during flowering"
                })
            else:
                tip_candidates.append({
                    'priority': 3,
                    'tip': "🌾 Rice: Maintain 2-5cm standing water depth for optimal growth"
                })
        elif crop_type == CropType.WHEAT:
            if days_since_irrigation > 7:
                tip_candidates.append({
                    'priority': 5,
                    'tip': "🌾 Wheat: Deep, infrequent irrigation promotes strong root development"
                })
            else:
                tip_candidates.append({
                    'priority': 3,
                    'tip': "🌾 Wheat: Avoid overwatering during tillering stage to prevent lodging"
                })
        elif crop_type == CropType.CORN:
            if temperature > 30:
                tip_candidates.append({
                    'priority': 5,
                    'tip': "🌽 Corn in hot weather: Ensure adequate moisture during tasseling and silking stages"
                })
            else:
                tip_candidates.append({
                    'priority': 3,
                    'tip': "🌽 Corn: Deep irrigation every 5-7 days promotes deep root growth"
                })

        # 5. SOIL-SPECIFIC TIPS (Medium Priority)
        if soil_type == SoilType.SANDY:
            if days_since_irrigation > 3:
                tip_candidates.append({
                    'priority': 5,
                    'tip': "🏖️ Sandy soil: Irrigate every 2-3 days with smaller amounts to prevent nutrient leaching"
                })
            else:
                tip_candidates.append({
                    'priority': 3,
                    'tip': "🏖️ Sandy soil: Light, frequent irrigation works best - avoid heavy watering"
                })
        elif soil_type == SoilType.CLAY:
            if soil_moisture > 70:
                tip_candidates.append({
                    'priority': 5,
                    'tip': "🧱 Clay soil: Allow longer drying periods between irrigations to prevent waterlogging"
                })
            else:
                tip_candidates.append({
                    'priority': 3,
                    'tip': "🧱 Clay soil: Deep, infrequent irrigation allows better water penetration"
                })
        elif soil_type == SoilType.LOAMY:
            tip_candidates.append({
                'priority': 2,
                'tip': "🌱 Loamy soil: Ideal water retention - follow standard irrigation practices"
            })

        # 6. IRRIGATION METHOD TIPS (Lower Priority)
        if irrigation_method == IrrigationMethod.DRIP:
            tip_candidates.append({
                'priority': 2,
                'tip': "💧 Drip system: Run for longer durations at lower flow rates for deep water penetration"
            })
        elif irrigation_method == IrrigationMethod.SPRINKLER:
            if humidity < 50:
                tip_candidates.append({
                    'priority': 3,
                    'tip': "💦 Sprinkler: Irrigate early morning (4-6 AM) to minimize evaporation losses"
                })
            else:
                tip_candidates.append({
                    'priority': 2,
                    'tip': "💦 Sprinkler: Ensure uniform coverage, check for clogged nozzles regularly"
                })
        elif irrigation_method == IrrigationMethod.FLOOD:
            tip_candidates.append({
                'priority': 2,
                'tip': "🌊 Flood irrigation: Level fields properly and use laser leveling for uniform water distribution"
            })

        # 7. SEASONAL/GENERAL TIPS (Lowest Priority)
        if ml_predictions.get('priority', 1) == 0:
            tip_candidates.append({
                'priority': 1,
                'tip': "📊 Current conditions are favorable - continue monitoring soil moisture and weather"
            })

        # Select the highest priority tip
        if tip_candidates:
            # Sort by priority (highest first) and return the best tip
            best_tip = max(tip_candidates, key=lambda x: x['priority'])
            return best_tip['tip']
        else:
            return "📋 Monitor soil moisture, weather conditions, and crop growth stage for optimal irrigation timing"
