#!/usr/bin/env python3
"""
Comprehensive Test Script for AgroConnect System
Tests all backend APIs and reports their status
"""

import requests
import json
import time

def test_api(name, url, method='GET', data=None, timeout=10):
    """Test an API endpoint and return status"""
    try:
        print(f"🧪 Testing {name}...")
        
        if method == 'GET':
            response = requests.get(url, timeout=timeout)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=timeout)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {name}: SUCCESS")
            return True, result
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Connection failed - server not running")
        return False, None
    except requests.exceptions.Timeout:
        print(f"❌ {name}: Request timeout")
        return False, None
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return False, None

def main():
    """Run comprehensive system tests"""
    print("🚀 AgroConnect System Test Suite")
    print("=" * 50)
    
    tests = []
    
    # Test 1: Frontend Server
    print("\n📱 Testing Frontend Server...")
    success, _ = test_api("Frontend Server", "http://localhost:8080")
    tests.append(("Frontend Server", success))
    
    # Test 2: Soil Analysis
    print("\n🌱 Testing Soil Analysis...")
    soil_data = {
        "ph": 6.5,
        "salinity": 1.2,
        "texture": "loam",
        "bulk_density": 1.3,
        "nutrients": {
            "nitrogen": 120,
            "phosphorus": 25,
            "potassium": 45
        },
        "crop": "tomato"
    }
    success, result = test_api("Soil Analysis", "http://localhost:8000/api/v1/analyze", "POST", soil_data)
    if success and result:
        print(f"   Score: {result.get('suitability_score', 'N/A')}/100")
        print(f"   Category: {result.get('category', 'N/A')}")
    tests.append(("Soil Analysis", success))
    
    # Test 3: Irrigation Calculator
    print("\n💧 Testing Irrigation Calculator...")
    irrigation_data = {
        "fieldSize": 2.0,
        "crop": "rice",
        "soilType": "loam",
        "irrigationType": "drip",
        "lastIrrigation": "2025-08-05",
        "location": "Tamil Nadu"
    }
    success, result = test_api("Irrigation Calculator", "http://localhost:8001/api/calculate-irrigation", "POST", irrigation_data)
    if success and result:
        print(f"   Water needed: {result.get('waterLiters', 'N/A')} liters")
        print(f"   Next irrigation: {result.get('nextIrrigationDate', 'N/A')}")
    tests.append(("Irrigation Calculator", success))
    
    # Test 4: Crop Prediction
    print("\n🌾 Testing Crop Prediction...")
    crop_data = {
        "crop": "rice",
        "soilType": "loam",
        "season": "kharif",
        "irrigationType": "drip",
        "fieldSize": 3.0
    }
    success, result = test_api("Crop Prediction", "http://localhost:8002/predict", "POST", crop_data)
    if success and result:
        predictions = result.get('predictions', {})
        market = result.get('market_analysis', {})
        print(f"   Expected yield: {predictions.get('expected_yield_tons', 'N/A')} tons")
        print(f"   Estimated revenue: ₹{market.get('estimated_revenue', 'N/A')}")
    tests.append(("Crop Prediction", success))
    
    # Test 5: Market Analysis
    print("\n📊 Testing Market Analysis...")
    market_data = {
        "crop": "tomato",
        "state": "tamil nadu",
        "district": "coimbatore"
    }
    success, result = test_api("Market Analysis", "http://localhost:8003/analyze", "POST", market_data)
    if success and result:
        print(f"   State avg price: ₹{result.get('state_avg_price', 'N/A')}")
        print(f"   District avg price: ₹{result.get('district_avg_price', 'N/A')}")
        print(f"   Trend: {result.get('price_trend', 'N/A')}")
    tests.append(("Market Analysis", success))
    
    # Test 6: AgroBot
    print("\n🤖 Testing AgroBot...")
    agrobot_data = {
        "message": "What is the market price of rice?"
    }
    success, result = test_api("AgroBot", "http://localhost:5000/chat", "POST", agrobot_data)
    if success and result:
        response_text = result.get('response', '')
        print(f"   Response: {response_text[:100]}...")
    tests.append(("AgroBot", success))
    
    # Test 7: Weather API
    print("\n🌤️ Testing Weather API...")
    success, result = test_api("Weather API", "http://localhost:8001/api/weather/Tamil%20Nadu")
    if success and result:
        print(f"   Temperature: {result.get('temperature', 'N/A')}°C")
        print(f"   Humidity: {result.get('humidity', 'N/A')}%")
        print(f"   Rainfall forecast: {result.get('rainfall_forecast_3day', 'N/A')}mm")
    tests.append(("Weather API", success))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, success in tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All systems operational! AgroConnect is ready to use.")
    else:
        print("⚠️ Some systems need attention. Check failed tests above.")
    
    return passed == total

if __name__ == "__main__":
    main()
