#!/usr/bin/env python3
"""
Test script for Market Analysis API
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8003"

def test_health_check():
    """Test API health endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_market_analysis():
    """Test market analysis endpoint"""
    print("\n📊 Testing market analysis...")
    
    test_cases = [
        {
            "name": "Tomato in Tamil Nadu",
            "data": {"crop": "tomato", "state": "tamil nadu", "district": "erode"}
        },
        {
            "name": "Onion in Karnataka", 
            "data": {"crop": "onion", "state": "karnataka"}
        },
        {
            "name": "Potato in Punjab",
            "data": {"crop": "potato", "state": "punjab"}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        try:
            response = requests.post(
                f"{API_BASE_URL}/analyze",
                json=test_case['data'],
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Analysis successful")
                print(f"   Crop: {data['crop']}")
                print(f"   State: {data['state']}")
                print(f"   State Avg Price: ₹{data['state_avg_price']}")
                print(f"   Price Trend: {data['price_trend']} ({data['trend_percentage']}%)")
                print(f"   Recommendation: {data['recommendation']}")
                print(f"   Confidence: {data['prediction_confidence']}")
                print(f"   Market Data Points: {len(data['market_data'])}")
            else:
                print(f"❌ Analysis failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Analysis error: {e}")
        
        time.sleep(2)  # Rate limiting

def test_utility_endpoints():
    """Test utility endpoints"""
    print("\n🛠️ Testing utility endpoints...")
    
    # Test crops endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/crops", timeout=5)
        if response.status_code == 200:
            crops = response.json()
            print(f"✅ Crops endpoint: {len(crops['crops'])} crops supported")
            print(f"   Crops: {', '.join(crops['crops'][:5])}...")
        else:
            print(f"❌ Crops endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Crops endpoint error: {e}")
    
    # Test states endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/states", timeout=5)
        if response.status_code == 200:
            states = response.json()
            print(f"✅ States endpoint: {len(states['states'])} states supported")
            print(f"   States: {', '.join(states['states'][:3])}...")
        else:
            print(f"❌ States endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ States endpoint error: {e}")

def test_error_handling():
    """Test error handling"""
    print("\n🚨 Testing error handling...")
    
    # Test invalid crop
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json={"crop": "invalid_crop", "state": "tamil nadu"},
            timeout=10
        )
        print(f"📝 Invalid crop test: {response.status_code}")
        if response.status_code != 200:
            print("✅ Properly handled invalid crop")
        else:
            print("⚠️ Invalid crop was processed (might be fallback data)")
    except Exception as e:
        print(f"❌ Invalid crop test error: {e}")
    
    # Test missing required fields
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json={"crop": "tomato"},  # Missing state
            timeout=10
        )
        print(f"📝 Missing field test: {response.status_code}")
        if response.status_code != 200:
            print("✅ Properly handled missing required field")
    except Exception as e:
        print(f"❌ Missing field test error: {e}")

def main():
    print("🌾 AgroConnect Market Analysis API Test Suite")
    print("=" * 50)
    
    # Check if API server is running
    if not test_health_check():
        print("\n❌ API server is not running!")
        print("💡 Please start the server first:")
        print("   python start_market_api.py")
        return
    
    # Run all tests
    test_market_analysis()
    test_utility_endpoints()
    test_error_handling()
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")
    print("\n💡 Next steps:")
    print("1. Open market.html in your browser")
    print("2. Select crop, state, and district")
    print("3. Click 'Analyze Market' to see results")
    print("4. Download PDF report for detailed analysis")

if __name__ == "__main__":
    main()
