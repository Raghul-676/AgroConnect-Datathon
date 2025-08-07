#!/usr/bin/env python3
"""
Test different locations with the irrigation system
"""

import requests

def test_locations():
    print("🌍 Testing Location-Based Weather API")
    print("=" * 50)
    
    locations = [
        'New York, USA',
        'London, UK', 
        'Mumbai, India',
        'Sydney, Australia',
        'Chennai, India',
        'California, USA'
    ]
    
    for location in locations:
        try:
            print(f"\n📍 Testing: {location}")
            response = requests.get(f'http://localhost:8000/api/weather/{location}')
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {response.status_code}")
                print(f"   🌡️  Temperature: {data.get('temperature', 'N/A')}°C")
                print(f"   💧 Humidity: {data.get('humidity', 'N/A')}%")
                print(f"   🌧️  Rainfall: {data.get('rainfall_forecast_3day', 'N/A')}mm")
                print(f"   📍 Location: {data.get('location', 'N/A')}")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Location testing complete!")

if __name__ == "__main__":
    test_locations()
