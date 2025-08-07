import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Tuple
import random
from .data_model import (
    IrrigationFeatures, IrrigationTarget, AgriculturalDatabase,
    CropType, SoilType, IrrigationMethod
)

class IrrigationDataGenerator:
    """Generate synthetic training data for irrigation ML models"""
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        random.seed(seed)
        self.agri_db = AgriculturalDatabase()
    
    def generate_training_data(self, n_samples: int = 10000) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generate synthetic training data based on agricultural principles
        
        Args:
            n_samples: Number of training samples to generate
            
        Returns:
            Tuple of (features_df, targets_df)
        """
        features = []
        targets = []
        
        for _ in range(n_samples):
            # Generate random farm scenario
            feature, target = self._generate_sample()
            features.append(feature)
            targets.append(target)
        
        # Convert to DataFrames
        feature_arrays = [f.to_array() for f in features]
        features_df = pd.DataFrame(feature_arrays, columns=IrrigationFeatures.get_feature_names())
        
        target_dicts = [t.to_dict() for t in targets]
        targets_df = pd.DataFrame(target_dicts)
        
        return features_df, targets_df
    
    def _generate_sample(self) -> Tuple[IrrigationFeatures, IrrigationTarget]:
        """Generate a single training sample"""
        
        # Random farm characteristics
        farm_size = np.random.uniform(0.5, 50.0)  # 0.5 to 50 hectares
        crop_type = np.random.choice(list(CropType))
        soil_type = np.random.choice(list(SoilType))
        irrigation_method = np.random.choice(list(IrrigationMethod))
        
        # Random temporal characteristics
        days_since_planting = np.random.randint(1, 200)
        days_since_last_irrigation = np.random.randint(0, 15)
        season = np.random.randint(0, 4)  # 0=winter, 1=summer, 2=monsoon, 3=post-monsoon
        
        # Generate weather based on season
        weather = self._generate_seasonal_weather(season)
        
        # Calculate crop coefficient
        crop_coeff = self.agri_db.get_crop_coefficient(crop_type, days_since_planting)
        
        # Estimate root depth based on crop and growth stage
        max_root_depth = self.agri_db.crop_coefficients[crop_type].max_root_depth
        root_depth = min(max_root_depth, max_root_depth * (days_since_planting / 100))
        
        # Estimate soil moisture based on various factors
        soil_moisture = self._estimate_soil_moisture(
            soil_type, days_since_last_irrigation, weather['rainfall_today'],
            weather['temperature'], weather['reference_et']
        )
        
        # Generate bulk density based on soil type with some variation
        soil_props = self.agri_db.soil_properties[soil_type]
        base_bulk_density = soil_props.bulk_density
        bulk_density = np.random.normal(base_bulk_density, 0.1)  # Add some variation
        bulk_density = np.clip(bulk_density, 0.8, 2.0)  # Keep within realistic range

        # Create feature vector
        features = IrrigationFeatures(
            farm_size=farm_size,
            crop_type_encoded=list(CropType).index(crop_type),
            soil_type_encoded=list(SoilType).index(soil_type),
            irrigation_method_encoded=list(IrrigationMethod).index(irrigation_method),
            bulk_density=bulk_density,
            temperature=weather['temperature'],
            humidity=weather['humidity'],
            wind_speed=weather['wind_speed'],
            reference_et=weather['reference_et'],
            rainfall_today=weather['rainfall_today'],
            rainfall_forecast_3day=weather['rainfall_forecast_3day'],
            irrigation_urgency_encoded=weather['irrigation_urgency_encoded'],
            days_since_last_irrigation=days_since_last_irrigation,
            days_since_planting=days_since_planting,
            season_encoded=season,
            estimated_soil_moisture=soil_moisture,
            crop_coefficient=crop_coeff,
            root_depth=root_depth
        )
        
        # Calculate target variables based on agricultural principles
        targets = self._calculate_irrigation_targets(features, crop_type, soil_type, irrigation_method)
        
        return features, targets
    
    def _generate_seasonal_weather(self, season: int) -> dict:
        """Generate weather data based on season"""
        
        if season == 0:  # Winter
            temp = np.random.normal(20, 5)
            humidity = np.random.normal(70, 15)
            rainfall_today = np.random.exponential(2)
            rainfall_forecast = np.random.exponential(8)
        elif season == 1:  # Summer
            temp = np.random.normal(35, 8)
            humidity = np.random.normal(45, 15)
            rainfall_today = np.random.exponential(1)
            rainfall_forecast = np.random.exponential(3)
        elif season == 2:  # Monsoon
            temp = np.random.normal(28, 5)
            humidity = np.random.normal(85, 10)
            rainfall_today = np.random.exponential(15)
            rainfall_forecast = np.random.exponential(40)
        else:  # Post-monsoon
            temp = np.random.normal(25, 6)
            humidity = np.random.normal(65, 15)
            rainfall_today = np.random.exponential(5)
            rainfall_forecast = np.random.exponential(15)
        
        # Ensure realistic ranges
        temp = np.clip(temp, 15, 45)
        humidity = np.clip(humidity, 20, 95)
        rainfall_today = np.clip(rainfall_today, 0, 50)
        rainfall_forecast = np.clip(rainfall_forecast, 0, 100)
        
        wind_speed = np.random.uniform(0.5, 8.0)
        
        # Calculate reference ET based on temperature and humidity
        reference_et = self._calculate_reference_et(temp, humidity, wind_speed)
        
        # Determine irrigation urgency
        urgency_score = 0
        if temp > 35: urgency_score += 3
        elif temp > 30: urgency_score += 2
        elif temp > 25: urgency_score += 1
        
        if humidity < 30: urgency_score += 3
        elif humidity < 50: urgency_score += 2
        elif humidity < 70: urgency_score += 1
        
        if rainfall_forecast > 20: urgency_score -= 3
        elif rainfall_forecast > 10: urgency_score -= 2
        elif rainfall_forecast > 5: urgency_score -= 1
        
        if urgency_score >= 6: urgency_encoded = 2  # high
        elif urgency_score >= 3: urgency_encoded = 1  # medium
        else: urgency_encoded = 0  # low
        
        return {
            'temperature': temp,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'reference_et': reference_et,
            'rainfall_today': rainfall_today,
            'rainfall_forecast_3day': rainfall_forecast,
            'irrigation_urgency_encoded': urgency_encoded
        }
    
    def _calculate_reference_et(self, temp: float, humidity: float, wind_speed: float) -> float:
        """Calculate reference evapotranspiration"""
        es = 0.6108 * (2.71828 ** ((17.27 * temp) / (temp + 237.3)))
        ea = es * (humidity / 100)
        vpd = es - ea
        et0 = (0.0023 * (temp + 17.8) * (vpd ** 0.5) * (wind_speed + 1)) * 1.2
        return max(0, et0)
    
    def _estimate_soil_moisture(self, soil_type: SoilType, days_since_irrigation: int,
                              rainfall_today: float, temperature: float, reference_et: float) -> float:
        """Estimate current soil moisture percentage"""
        
        soil_props = self.agri_db.soil_properties[soil_type]
        
        # Start with field capacity after irrigation
        initial_moisture = 100.0
        
        # Decrease based on days since irrigation
        daily_depletion = reference_et * 0.8  # Simplified depletion rate
        moisture_loss = daily_depletion * days_since_irrigation
        
        # Add moisture from rainfall
        rainfall_contribution = rainfall_today * 2  # Simplified conversion
        
        # Calculate current moisture
        current_moisture = initial_moisture - moisture_loss + rainfall_contribution
        
        # Apply soil-specific constraints
        if soil_type == SoilType.SANDY:
            current_moisture *= 0.8  # Sandy soil drains faster
        elif soil_type == SoilType.CLAY:
            current_moisture *= 1.2  # Clay soil retains more water
        
        return np.clip(current_moisture, 10, 100)
    
    def _calculate_irrigation_targets(self, features: IrrigationFeatures, 
                                    crop_type: CropType, soil_type: SoilType,
                                    irrigation_method: IrrigationMethod) -> IrrigationTarget:
        """Calculate target variables based on agricultural principles"""
        
        # Get agricultural parameters
        crop_coeff = self.agri_db.crop_coefficients[crop_type]
        soil_props = self.agri_db.soil_properties[soil_type]
        irrigation_eff = self.agri_db.irrigation_efficiency[irrigation_method]
        
        # Calculate days until next irrigation
        if features.estimated_soil_moisture < 30:
            days_until_irrigation = 0  # Immediate irrigation needed
        elif features.estimated_soil_moisture < 50:
            days_until_irrigation = np.random.randint(1, 3)
        elif features.estimated_soil_moisture < 70:
            days_until_irrigation = np.random.randint(2, 5)
        else:
            days_until_irrigation = np.random.randint(3, 8)
        
        # Adjust based on weather forecast
        if features.rainfall_forecast_3day > 20:
            days_until_irrigation += 2
        elif features.rainfall_forecast_3day > 10:
            days_until_irrigation += 1
        
        # Adjust based on crop water stress sensitivity
        if crop_coeff.stress_factor > 0.7:  # Sensitive crops
            days_until_irrigation = max(0, days_until_irrigation - 1)
        
        days_until_irrigation = np.clip(days_until_irrigation, 0, 10)
        
        # Calculate water requirement per hectare
        crop_et = features.reference_et * features.crop_coefficient
        net_irrigation = crop_et * 10  # Convert to liters per m²
        gross_irrigation = net_irrigation / irrigation_eff.application_efficiency
        water_per_hectare = gross_irrigation * 10000  # Convert to liters per hectare
        
        # Adjust for soil type
        if soil_type == SoilType.SANDY:
            water_per_hectare *= 1.2  # Sandy soil needs more frequent, smaller applications
        elif soil_type == SoilType.CLAY:
            water_per_hectare *= 0.9  # Clay soil can hold more water
        
        water_per_hectare = np.clip(water_per_hectare, 1000, 50000)
        
        # Calculate irrigation priority
        if features.estimated_soil_moisture < 30 or features.irrigation_urgency_encoded == 2:
            priority = 2  # High
        elif features.estimated_soil_moisture < 60 or features.irrigation_urgency_encoded == 1:
            priority = 1  # Medium
        else:
            priority = 0  # Low
        
        return IrrigationTarget(
            days_until_next_irrigation=int(days_until_irrigation),
            water_requirement_per_hectare=float(water_per_hectare),
            irrigation_priority=int(priority)
        )
