#!/usr/bin/env python3
"""
Example usage of the Soil Analysis API
"""

import requests
import json
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"

def test_soil_analysis():
    """Test soil analysis with different scenarios"""
    
    print("🌱 Soil Analysis API Example Usage")
    print("=" * 40)
    
    # Test 1: Excellent soil for wheat
    print("\n1. Testing excellent soil for wheat:")
    excellent_soil = {
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
    
    analyze_soil(excellent_soil)
    
    # Test 2: Poor soil for tomato
    print("\n2. Testing poor soil for tomato:")
    poor_soil = {
        "soil_parameters": {
            "ph": 4.0,
            "salinity": 6.0,
            "texture": "sandy",
            "bulk_density": 1.8,
            "nutrients": {
                "nitrogen": 30.0,
                "phosphorus": 10.0,
                "potassium": 20.0,
                "calcium": 500.0,
                "magnesium": 80.0,
                "sulfur": 5.0,
                "iron": 2.0,
                "manganese": 1.0,
                "zinc": 0.3,
                "copper": 0.1,
                "boron": 0.2
            }
        },
        "crop_name": "tomato"
    }
    
    analyze_soil(poor_soil)
    
    # Test 3: Average soil for rice
    print("\n3. Testing average soil for rice:")
    average_soil = {
        "soil_parameters": {
            "ph": 6.8,
            "salinity": 2.5,
            "texture": "clay_loam",
            "bulk_density": 1.3,
            "nutrients": {
                "nitrogen": 100.0,
                "phosphorus": 20.0,
                "potassium": 45.0,
                "calcium": 1200.0,
                "magnesium": 180.0,
                "sulfur": 10.0,
                "iron": 6.0,
                "manganese": 4.0,
                "zinc": 1.2,
                "copper": 0.4,
                "boron": 0.6
            }
        },
        "crop_name": "rice"
    }
    
    analyze_soil(average_soil)

def analyze_soil(soil_data: Dict[str, Any]):
    """Analyze soil and display results"""
    try:
        response = requests.post(f"{BASE_URL}/api/v1/analyze", json=soil_data)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"   Category: {result['category'].upper()}")
            print(f"   Score: {result['suitability_score']:.1f}/100")
            print(f"   Message: {result['message']}")
            
            if result['fertilizer_recommendations']:
                print("   Fertilizer Recommendations:")
                for fert in result['fertilizer_recommendations']:
                    print(f"     - {fert['name']}: {fert['amount']} {fert['unit']}")
            
            if result['alternative_crops']:
                print(f"   Alternative Crops: {', '.join(result['alternative_crops'])}")
                
            if result['cultivation_tips']:
                print("   Cultivation Tips:")
                for tip in result['cultivation_tips'][:3]:  # Show first 3 tips
                    print(f"     - {tip}")
                    
        else:
            print(f"   Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Error: Could not connect to API. Make sure the server is running.")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def get_supported_crops():
    """Get and display supported crops"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/crops")
        if response.status_code == 200:
            crops = response.json()
            print(f"\n📋 Supported Crops ({len(crops)}):")
            for crop in crops:
                print(f"   - {crop.title()}")
        else:
            print(f"Error getting crops: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def get_soil_textures():
    """Get and display supported soil textures"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/soil-textures")
        if response.status_code == 200:
            textures = response.json()
            print(f"\n🏔️ Supported Soil Textures ({len(textures)}):")
            for texture in textures:
                print(f"   - {texture.replace('_', ' ').title()}")
        else:
            print(f"Error getting textures: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is running!")
            
            # Get supported crops and textures
            get_supported_crops()
            get_soil_textures()
            
            # Run soil analysis tests
            test_soil_analysis()
            
        else:
            print("❌ API is not responding correctly")
    except requests.exceptions.ConnectionError:
        print("❌ API is not running. Please start the server with: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
