#!/usr/bin/env python3
"""
Test Coimbatore, Tamil Nadu specifically
"""

import requests
import json

def test_coimbatore():
    print("🧪 Testing Coimbatore, Tamil Nadu")
    print("=" * 40)
    
    # Test weather API
    print("\n1. Testing Weather API:")
    try:
        response = requests.get('http://localhost:8000/api/weather/Coimbatore, Tamil Nadu')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Location: {data.get('location')}")
            print(f"   🌡️  Temperature: {data.get('temperature')}°C")
            print(f"   💧 Humidity: {data.get('humidity')}%")
            print(f"   🌧️  Rainfall: {data.get('rainfall_forecast_3day')}mm")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test irrigation calculation
    print("\n2. Testing Irrigation Calculation:")
    try:
        data = {
            'farmSize': 2.5,
            'unit': 'hectares',
            'crop': 'rice',
            'soil': 'loamy',
            'method': 'drip',
            'bulkDensity': 1.3,
            'lastIrrigation': '2025-08-04',
            'location': 'Coimbatore, Tamil Nadu'
        }
        
        print(f"   Request data: {json.dumps(data, indent=2)}")
        
        response = requests.post('http://localhost:8000/api/calculate-irrigation', json=data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Next irrigation: {result.get('nextIrrigationDate')}")
            print(f"   💧 Water needed: {result.get('waterLiters')} liters")
            print(f"   💡 Tip: {result.get('tip')[:60]}...")
            print(f"   📍 Weather location: {result.get('weatherInfo', {}).get('location')}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    test_coimbatore()
