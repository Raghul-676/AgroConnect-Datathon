import pytest
import asyncio
import json
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
import numpy as np

from main import app
from irrigation_ml.models import IrrigationPredictor
from irrigation_ml.weather import WeatherService
from irrigation_ml.calculator import IrrigationCalculator
from irrigation_ml.data_model import IrrigationFeatures, CropType, SoilType, IrrigationMethod
from irrigation_ml.data_generator import IrrigationDataGenerator
from irrigation_ml.model_manager import ModelManager

# Test client for API testing
client = TestClient(app)

class TestDataGeneration:
    """Test data generation and ML models"""
    
    def test_data_generator(self):
        """Test synthetic data generation"""
        generator = IrrigationDataGenerator(seed=42)
        features_df, targets_df = generator.generate_training_data(n_samples=100)
        
        # Check data shape
        assert features_df.shape[0] == 100
        assert targets_df.shape[0] == 100
        assert features_df.shape[1] == len(IrrigationFeatures.get_feature_names())
        
        # Check data ranges
        assert features_df['temperature'].min() >= 15
        assert features_df['temperature'].max() <= 45
        assert features_df['humidity'].min() >= 20
        assert features_df['humidity'].max() <= 95
        
        # Check target ranges
        assert targets_df['days_until_next_irrigation'].min() >= 0
        assert targets_df['days_until_next_irrigation'].max() <= 10
        assert targets_df['water_requirement_per_hectare'].min() >= 1000
        assert targets_df['irrigation_priority'].isin([0, 1, 2]).all()
    
    def test_irrigation_features(self):
        """Test IrrigationFeatures data structure"""
        features = IrrigationFeatures(
            farm_size=5.0,
            crop_type_encoded=0,
            soil_type_encoded=1,
            irrigation_method_encoded=0,
            bulk_density=1.3,
            temperature=30.0,
            humidity=60.0,
            wind_speed=2.5,
            reference_et=4.5,
            rainfall_today=0.0,
            rainfall_forecast_3day=10.0,
            irrigation_urgency_encoded=1,
            days_since_last_irrigation=3,
            days_since_planting=45,
            season_encoded=1,
            estimated_soil_moisture=65.0,
            crop_coefficient=1.1,
            root_depth=0.8
        )
        
        # Test array conversion
        feature_array = features.to_array()
        assert len(feature_array) == len(IrrigationFeatures.get_feature_names())
        assert isinstance(feature_array, np.ndarray)

class TestMLModels:
    """Test machine learning models"""
    
    @pytest.fixture
    def trained_predictor(self):
        """Create a trained predictor for testing"""
        predictor = IrrigationPredictor(model_dir="test_models")
        predictor.train_models(n_samples=1000, retrain=True)
        return predictor
    
    def test_model_training(self, trained_predictor):
        """Test model training process"""
        assert trained_predictor.is_trained
        assert 'timing' in trained_predictor.models
        assert 'water' in trained_predictor.models
        assert 'priority' in trained_predictor.models
    
    def test_model_predictions(self, trained_predictor):
        """Test model predictions"""
        features = IrrigationFeatures(
            farm_size=2.5,
            crop_type_encoded=0,  # rice
            soil_type_encoded=1,  # loamy
            irrigation_method_encoded=0,  # drip
            bulk_density=1.4,  # loamy soil typical bulk density
            temperature=32.0,
            humidity=55.0,
            wind_speed=3.0,
            reference_et=5.2,
            rainfall_today=0.0,
            rainfall_forecast_3day=5.0,
            irrigation_urgency_encoded=1,
            days_since_last_irrigation=4,
            days_since_planting=60,
            season_encoded=1,
            estimated_soil_moisture=45.0,
            crop_coefficient=1.15,
            root_depth=0.9
        )
        
        predictions = trained_predictor.predict(features)
        
        # Check prediction structure
        assert 'days_until_irrigation' in predictions
        assert 'water_per_hectare' in predictions
        assert 'priority' in predictions
        
        # Check prediction ranges
        assert 0 <= predictions['days_until_irrigation'] <= 10
        assert predictions['water_per_hectare'] >= 1000
        assert predictions['priority'] in [0, 1, 2]

class TestWeatherService:
    """Test weather service functionality"""
    
    @pytest.fixture
    def weather_service(self):
        return WeatherService()
    
    def test_default_weather(self, weather_service):
        """Test default weather data when API is unavailable"""
        default_weather = weather_service._get_default_weather()
        
        required_keys = [
            'temperature', 'humidity', 'wind_speed', 'rainfall_today',
            'rainfall_forecast_3day', 'reference_et', 'irrigation_urgency',
            'weather_description', 'location'
        ]
        
        for key in required_keys:
            assert key in default_weather
        
        assert isinstance(default_weather['temperature'], (int, float))
        assert isinstance(default_weather['humidity'], (int, float))
    
    def test_et_calculation(self, weather_service):
        """Test reference evapotranspiration calculation"""
        et = weather_service._calculate_reference_et(30.0, 60.0, 2.5)
        assert isinstance(et, float)
        assert et >= 0
    
    def test_urgency_calculation(self, weather_service):
        """Test irrigation urgency calculation"""
        urgency = weather_service._calculate_irrigation_urgency(35.0, 40.0, 5.0, 6.0)
        assert urgency in ["low", "medium", "high"]

class TestIrrigationCalculator:
    """Test irrigation calculator"""
    
    @pytest.fixture
    def calculator(self):
        predictor = IrrigationPredictor(model_dir="test_models")
        predictor.train_models(n_samples=500, retrain=True)
        weather_service = WeatherService()
        return IrrigationCalculator(predictor, weather_service)
    
    def test_unit_conversion(self, calculator):
        """Test farm size unit conversion"""
        # Test hectares
        assert calculator._convert_to_hectares(5.0, "hectares") == 5.0
        
        # Test acres
        acres_to_hectares = calculator._convert_to_hectares(10.0, "acres")
        assert abs(acres_to_hectares - 4.04686) < 0.001
        
        # Test square meters
        sqm_to_hectares = calculator._convert_to_hectares(50000, "sqmeters")
        assert sqm_to_hectares == 5.0
    
    def test_irrigation_calculation(self, calculator):
        """Test complete irrigation calculation"""
        weather_data = {
            'temperature': 30.0,
            'humidity': 60.0,
            'wind_speed': 2.5,
            'reference_et': 4.5,
            'rainfall_today': 0.0,
            'rainfall_forecast_3day': 8.0,
            'irrigation_urgency': 'medium',
            'weather_description': 'partly cloudy',
            'location': 'Test Location'
        }
        
        result = calculator.calculate_irrigation(
            farm_size=2.5,
            unit="hectares",
            crop="rice",
            soil="loamy",
            method="drip",
            last_irrigation=(datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            weather_data=weather_data
        )
        
        # Check result structure
        assert 'next_irrigation_date' in result
        assert 'water_liters' in result
        assert 'tip' in result
        
        # Check result types
        assert isinstance(result['next_irrigation_date'], str)
        assert isinstance(result['water_liters'], (int, float))
        assert isinstance(result['tip'], str)
        
        # Validate date format
        datetime.strptime(result['next_irrigation_date'], "%Y-%m-%d")

class TestAPI:
    """Test API endpoints"""
    
    def test_serve_html(self):
        """Test HTML serving"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_weather_endpoint(self):
        """Test weather API endpoint"""
        response = client.get("/api/weather/Test Location")
        assert response.status_code == 200
        
        weather_data = response.json()
        required_keys = ['temperature', 'humidity', 'wind_speed', 'reference_et']
        for key in required_keys:
            assert key in weather_data
    
    def test_irrigation_calculation_endpoint(self):
        """Test irrigation calculation API endpoint"""
        request_data = {
            "farmSize": 2.5,
            "unit": "hectares",
            "crop": "rice",
            "soil": "loamy",
            "method": "drip",
            "bulkDensity": 1.3,
            "lastIrrigation": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "location": "Test Location"
        }
        
        response = client.post("/api/calculate-irrigation", json=request_data)
        assert response.status_code == 200
        
        result = response.json()
        assert 'nextIrrigationDate' in result
        assert 'waterLiters' in result
        assert 'tip' in result
        assert 'weatherInfo' in result
    
    def test_invalid_irrigation_request(self):
        """Test API with invalid request data"""
        invalid_request = {
            "farmSize": "invalid",
            "unit": "hectares",
            "crop": "rice"
            # Missing required fields
        }
        
        response = client.post("/api/calculate-irrigation", json=invalid_request)
        assert response.status_code == 422  # Validation error

class TestModelManager:
    """Test model management functionality"""
    
    def test_model_manager_initialization(self):
        """Test model manager initialization"""
        manager = ModelManager(model_dir="test_models", data_dir="test_data")
        assert manager.model_dir == "test_models"
        assert manager.data_dir == "test_data"
        assert isinstance(manager.metadata, dict)
    
    def test_model_info(self):
        """Test model information retrieval"""
        manager = ModelManager(model_dir="test_models")
        info = manager.get_model_info()
        
        required_keys = ['is_trained', 'version', 'should_retrain']
        for key in required_keys:
            assert key in info

def run_integration_test():
    """Run a complete integration test"""
    print("Running integration test...")
    
    # Test complete workflow
    request_data = {
        "farmSize": 3.0,
        "unit": "hectares",
        "crop": "wheat",
        "soil": "clay",
        "method": "sprinkler",
        "lastIrrigation": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
        "location": "Tamil Nadu, India"
    }
    
    response = client.post("/api/calculate-irrigation", json=request_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Integration test passed!")
        print(f"Next irrigation: {result['nextIrrigationDate']}")
        print(f"Water required: {result['waterLiters']} liters")
        print(f"Smart tip: {result['tip']}")
        return True
    else:
        print(f"❌ Integration test failed: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    # Run integration test
    success = run_integration_test()
    
    if success:
        print("\n🎉 All systems operational!")
        print("Your irrigation calculation system is ready to use.")
    else:
        print("\n⚠️ System needs attention.")
