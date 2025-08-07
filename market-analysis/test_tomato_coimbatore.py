#!/usr/bin/env python3
"""
Test script for the specific case: Tomato in Tamil Nadu, Coimbatore
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8003"

def test_specific_case():
    """Test the exact case that's failing"""
    print("🍅 Testing Tomato in Tamil Nadu, Coimbatore")
    print("=" * 50)
    
    test_data = {
        "crop": "tomato",
        "state": "tamil nadu", 
        "district": "coimbatore"
    }
    
    print(f"📤 Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        print("🌐 Making API call...")
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json=test_data,
            timeout=30
        )
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! Analysis completed")
            print(f"📊 Results:")
            print(f"   Crop: {data['crop']}")
            print(f"   State: {data['state']}")
            print(f"   District: {data['district']}")
            print(f"   State Avg Price: ₹{data['state_avg_price']}")
            print(f"   District Avg Price: ₹{data['district_avg_price']}")
            print(f"   Price Trend: {data['price_trend']} ({data['trend_percentage']}%)")
            print(f"   Recommendation: {data['recommendation']}")
            print(f"   Confidence: {data['prediction_confidence']}")
            print(f"   Market Data Points: {len(data['market_data'])}")
            
            if data['market_data']:
                print(f"\n📍 Market Data:")
                for market in data['market_data'][:3]:
                    print(f"   • {market['market']}, {market['district']}")
                    print(f"     Price: ₹{market['modal_price']} (Range: ₹{market['min_price']}-₹{market['max_price']})")
        else:
            print(f"❌ FAILED! Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR!")
        print("💡 Make sure the market analysis server is running:")
        print("   cd market-analysis")
        print("   python start_market_api.py")
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT ERROR!")
        print("💡 The API request took too long. This might be due to:")
        print("   • Slow internet connection")
        print("   • AGMARKNET API being slow")
        print("   • Server overload")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")

def test_server_health():
    """Test if the server is running"""
    print("🏥 Testing server health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and healthy")
            return True
        else:
            print(f"⚠️ Server responded with status {response.status_code}")
            return False
    except:
        print("❌ Server is not responding")
        return False

def test_alternative_cases():
    """Test some alternative cases to see if the issue is specific"""
    print("\n🧪 Testing alternative cases...")
    
    test_cases = [
        {"crop": "tomato", "state": "tamil nadu"},  # Without district
        {"crop": "onion", "state": "tamil nadu", "district": "coimbatore"},  # Different crop
        {"crop": "tomato", "state": "karnataka", "district": "bangalore"},  # Different state
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {case}")
        try:
            response = requests.post(f"{API_BASE_URL}/analyze", json=case, timeout=20)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: ₹{data['state_avg_price']} - {data['recommendation']}")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(1)

def main():
    print("🌾 AgroConnect Market Analysis - Troubleshooting")
    print("🎯 Testing: Tomato in Tamil Nadu, Coimbatore")
    print("=" * 60)
    
    # Check server health first
    if not test_server_health():
        print("\n💡 To start the server:")
        print("1. cd market-analysis")
        print("2. python start_market_api.py")
        print("3. Wait for 'Server started' message")
        print("4. Run this test again")
        return
    
    # Test the specific failing case
    test_specific_case()
    
    # Test alternative cases
    test_alternative_cases()
    
    print("\n" + "=" * 60)
    print("🔧 Troubleshooting Tips:")
    print("1. Make sure you have internet connection (for AGMARKNET API)")
    print("2. Check if the server logs show any errors")
    print("3. Try refreshing the browser page")
    print("4. Clear browser cache if needed")
    print("5. Check browser console for JavaScript errors (F12)")

if __name__ == "__main__":
    main()
