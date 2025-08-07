"""
Tests for the soil analysis engine
"""

import pytest
from app.models.soil import SoilParameters, NutrientLevels, SoilTexture
from app.services.analysis_engine import SoilAnalysisEngine

@pytest.fixture
def analysis_engine():
    """Create analysis engine instance for testing"""
    return SoilAnalysisEngine()

@pytest.fixture
def excellent_soil():
    """Create soil parameters that should result in excellent rating"""
    return SoilParameters(
        ph=6.5,
        salinity=1.0,
        texture=SoilTexture.LOAM,
        bulk_density=1.2,
        nutrients=NutrientLevels(
            nitrogen=150.0,
            phosphorus=30.0,
            potassium=50.0,
            calcium=2000.0,
            magnesium=250.0,
            sulfur=15.0,
            iron=8.0,
            manganese=5.0,
            zinc=1.5,
            copper=0.5,
            boron=1.0
        )
    )

@pytest.fixture
def poor_soil():
    """Create soil parameters that should result in bad rating"""
    return SoilParameters(
        ph=4.0,
        salinity=8.0,
        texture=SoilTexture.SANDY,
        bulk_density=1.8,
        nutrients=NutrientLevels(
            nitrogen=20.0,
            phosphorus=5.0,
            potassium=10.0,
            calcium=200.0,
            magnesium=50.0,
            sulfur=2.0,
            iron=1.0,
            manganese=0.5,
            zinc=0.2,
            copper=0.1,
            boron=0.1
        )
    )

def test_excellent_soil_analysis(analysis_engine, excellent_soil):
    """Test analysis of excellent soil conditions"""
    result = analysis_engine.analyze_soil(excellent_soil, "wheat")
    
    assert result.category == "excellent"
    assert result.suitability_score >= 80
    assert len(result.cultivation_tips) > 0
    assert len(result.fertilizer_recommendations) == 0
    assert len(result.alternative_crops) == 0

def test_poor_soil_analysis(analysis_engine, poor_soil):
    """Test analysis of poor soil conditions"""
    result = analysis_engine.analyze_soil(poor_soil, "wheat")
    
    assert result.category == "bad"
    assert result.suitability_score < 60
    assert len(result.fertilizer_recommendations) > 0
    assert len(result.alternative_crops) > 0
    assert len(result.recommendations) > 0

def test_invalid_crop(analysis_engine, excellent_soil):
    """Test analysis with invalid crop name"""
    with pytest.raises(ValueError, match="not supported"):
        analysis_engine.analyze_soil(excellent_soil, "invalid_crop")

def test_suitability_score_calculation(analysis_engine, excellent_soil):
    """Test suitability score calculation"""
    from app.data.crop_requirements import get_crop_requirements
    
    requirements = get_crop_requirements("wheat")
    score = analysis_engine._calculate_suitability_score(excellent_soil, requirements)
    
    assert 0 <= score <= 100
    assert score >= 80  # Should be high for excellent soil

def test_different_crops(analysis_engine, excellent_soil):
    """Test analysis for different crops"""
    crops = ["wheat", "rice", "corn", "tomato"]
    
    for crop in crops:
        result = analysis_engine.analyze_soil(excellent_soil, crop)
        assert result.category in ["excellent", "average", "bad"]
        assert 0 <= result.suitability_score <= 100
