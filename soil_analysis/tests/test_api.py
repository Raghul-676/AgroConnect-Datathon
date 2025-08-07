"""
Tests for the API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def sample_soil_request():
    """Sample soil analysis request"""
    return {
        "soil_parameters": {
            "ph": 6.5,
            "salinity": 1.0,
            "texture": "loam",
            "bulk_density": 1.2,
            "nutrients": {
                "nitrogen": 150.0,
                "phosphorus": 30.0,
                "potassium": 50.0,
                "calcium": 2000.0,
                "magnesium": 250.0,
                "sulfur": 15.0,
                "iron": 8.0,
                "manganese": 5.0,
                "zinc": 1.5,
                "copper": 0.5,
                "boron": 1.0
            }
        },
        "crop_name": "wheat"
    }

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Soil Analysis API is running" in response.json()["message"]

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_analyze_soil_endpoint(sample_soil_request):
    """Test soil analysis endpoint"""
    response = client.post("/api/v1/analyze", json=sample_soil_request)
    assert response.status_code == 200
    
    data = response.json()
    assert "suitability_score" in data
    assert "category" in data
    assert "message" in data
    assert data["category"] in ["excellent", "average", "bad"]
    assert 0 <= data["suitability_score"] <= 100

def test_get_crops_endpoint():
    """Test get supported crops endpoint"""
    response = client.get("/api/v1/crops")
    assert response.status_code == 200
    
    crops = response.json()
    assert isinstance(crops, list)
    assert len(crops) > 0
    assert "wheat" in crops

def test_get_soil_textures_endpoint():
    """Test get soil textures endpoint"""
    response = client.get("/api/v1/soil-textures")
    assert response.status_code == 200
    
    textures = response.json()
    assert isinstance(textures, list)
    assert len(textures) > 0
    assert "loam" in textures

def test_get_crop_requirements_endpoint():
    """Test get crop requirements endpoint"""
    response = client.get("/api/v1/crop-requirements/wheat")
    assert response.status_code == 200
    
    data = response.json()
    assert "crop" in data
    assert "requirements" in data
    assert data["crop"] == "wheat"

def test_invalid_crop_requirements():
    """Test crop requirements for invalid crop"""
    response = client.get("/api/v1/crop-requirements/invalid_crop")
    assert response.status_code == 404

def test_invalid_soil_parameters():
    """Test analysis with invalid soil parameters"""
    invalid_request = {
        "soil_parameters": {
            "ph": 15.0,  # Invalid pH
            "salinity": 1.0,
            "texture": "loam",
            "bulk_density": 1.2,
            "nutrients": {
                "nitrogen": -10.0,  # Invalid negative value
                "phosphorus": 30.0,
                "potassium": 50.0,
                "calcium": 2000.0,
                "magnesium": 250.0,
                "sulfur": 15.0,
                "iron": 8.0,
                "manganese": 5.0,
                "zinc": 1.5,
                "copper": 0.5,
                "boron": 1.0
            }
        },
        "crop_name": "wheat"
    }
    
    response = client.post("/api/v1/analyze", json=invalid_request)
    assert response.status_code == 422  # Validation error

def test_model_info_endpoint():
    """Test model info endpoint"""
    response = client.get("/api/v1/model-info")
    assert response.status_code == 200
    
    data = response.json()
    assert "model_type" in data
    assert "supported_crops" in data
    assert "supported_textures" in data

def test_service_health_endpoint():
    """Test service health endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "service" in data
    assert data["service"] == "soil_analysis"
