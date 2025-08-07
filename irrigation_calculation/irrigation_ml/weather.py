import os
import requests
import asyncio
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
    async def get_weather_data(self, location: str) -> Dict:
        """
        Fetch current weather and forecast data for irrigation calculations
        
        Args:
            location: Location string (e.g., "Tamil Nadu, India")
            
        Returns:
            Dictionary containing weather data relevant for irrigation
        """
        try:
            # Get current weather
            current_weather = await self._get_current_weather(location)
            
            # Get 5-day forecast
            forecast = await self._get_forecast(location)
            
            # Calculate derived metrics for irrigation
            irrigation_weather = self._calculate_irrigation_metrics(current_weather, forecast)
            
            return irrigation_weather
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            # Return default values if API fails
            return self._get_default_weather()
    
    async def _get_current_weather(self, location: str) -> Dict:
        """Fetch current weather data"""
        if not self.api_key:
            raise ValueError("OpenWeather API key not configured")
            
        url = f"{self.base_url}/weather"
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    async def _get_forecast(self, location: str) -> Dict:
        """Fetch 5-day weather forecast"""
        if not self.api_key:
            raise ValueError("OpenWeather API key not configured")
            
        url = f"{self.base_url}/forecast"
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def _calculate_irrigation_metrics(self, current: Dict, forecast: Dict) -> Dict:
        """Calculate irrigation-relevant metrics from weather data"""
        
        # Extract current conditions
        temp = current["main"]["temp"]
        humidity = current["main"]["humidity"]
        wind_speed = current["wind"]["speed"]
        
        # Calculate reference evapotranspiration (simplified Penman-Monteith)
        et0 = self._calculate_reference_et(temp, humidity, wind_speed)
        
        # Calculate rainfall forecast for next 3 days
        rainfall_forecast = self._calculate_rainfall_forecast(forecast)
        
        # Determine irrigation urgency based on weather conditions
        irrigation_urgency = self._calculate_irrigation_urgency(
            temp, humidity, rainfall_forecast, et0
        )
        
        return {
            "temperature": temp,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "rainfall_today": current.get("rain", {}).get("1h", 0),
            "rainfall_forecast_3day": rainfall_forecast,
            "reference_et": et0,
            "irrigation_urgency": irrigation_urgency,
            "weather_description": current["weather"][0]["description"],
            "location": current["name"]
        }
    
    def _calculate_reference_et(self, temp: float, humidity: float, wind_speed: float) -> float:
        """
        Calculate reference evapotranspiration using simplified Penman-Monteith equation
        
        Args:
            temp: Temperature in Celsius
            humidity: Relative humidity in %
            wind_speed: Wind speed in m/s
            
        Returns:
            Reference ET in mm/day
        """
        # Simplified ET calculation for demonstration
        # In production, use full Penman-Monteith equation with solar radiation data
        
        # Saturation vapor pressure
        es = 0.6108 * (2.71828 ** ((17.27 * temp) / (temp + 237.3)))
        
        # Actual vapor pressure
        ea = es * (humidity / 100)
        
        # Vapor pressure deficit
        vpd = es - ea
        
        # Simplified ET calculation
        et0 = (0.0023 * (temp + 17.8) * (vpd ** 0.5) * (wind_speed + 1)) * 1.2
        
        return max(0, et0)
    
    def _calculate_rainfall_forecast(self, forecast: Dict) -> float:
        """Calculate total rainfall forecast for next 3 days"""
        total_rainfall = 0
        current_time = datetime.now()
        cutoff_time = current_time + timedelta(days=3)
        
        for item in forecast.get("list", []):
            forecast_time = datetime.fromtimestamp(item["dt"])
            if forecast_time <= cutoff_time:
                rain = item.get("rain", {}).get("3h", 0)
                total_rainfall += rain
        
        return total_rainfall
    
    def _calculate_irrigation_urgency(self, temp: float, humidity: float, 
                                    rainfall_forecast: float, et0: float) -> str:
        """
        Calculate irrigation urgency based on weather conditions
        
        Returns:
            "high", "medium", or "low"
        """
        urgency_score = 0
        
        # High temperature increases urgency
        if temp > 35:
            urgency_score += 3
        elif temp > 30:
            urgency_score += 2
        elif temp > 25:
            urgency_score += 1
        
        # Low humidity increases urgency
        if humidity < 30:
            urgency_score += 3
        elif humidity < 50:
            urgency_score += 2
        elif humidity < 70:
            urgency_score += 1
        
        # High ET increases urgency
        if et0 > 7:
            urgency_score += 3
        elif et0 > 5:
            urgency_score += 2
        elif et0 > 3:
            urgency_score += 1
        
        # Rainfall reduces urgency
        if rainfall_forecast > 20:
            urgency_score -= 3
        elif rainfall_forecast > 10:
            urgency_score -= 2
        elif rainfall_forecast > 5:
            urgency_score -= 1
        
        if urgency_score >= 6:
            return "high"
        elif urgency_score >= 3:
            return "medium"
        else:
            return "low"
    
    def _get_default_weather(self) -> Dict:
        """Return default weather data when API is unavailable"""
        return {
            "temperature": 30,
            "humidity": 60,
            "wind_speed": 2.5,
            "rainfall_today": 0,
            "rainfall_forecast_3day": 5,
            "reference_et": 4.5,
            "irrigation_urgency": "medium",
            "weather_description": "partly cloudy",
            "location": "Default Location"
        }
