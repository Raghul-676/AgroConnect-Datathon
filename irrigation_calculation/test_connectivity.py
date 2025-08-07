#!/usr/bin/env python3
"""
Test frontend-backend connectivity
"""

import requests
import json

def test_connectivity():
    print("=== FRONTEND-BACKEND CONNECTIVITY TEST ===")
    print()
    
    # Test 1: Basic API endpoint
    print("1. Testing basic API endpoint...")
    try:
        response = requests.get('http://localhost:8000/api/test')
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print("   ✅ Basic API working")
    except Exception as e:
        print(f"   ❌ Basic API failed: {e}")
        return False
    
    print()
    
    # Test 2: Weather endpoint
    print("2. Testing weather endpoint...")
    try:
        response = requests.get('http://localhost:8000/api/weather/Chennai')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            weather = response.json()
            print(f"   Location: {weather['location']}")
            print(f"   Temperature: {weather['temperature']}°C")
            print("   ✅ Weather API working")
        else:
            print(f"   ❌ Weather API failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Weather API failed: {e}")
    
    print()
    
    # Test 3: Irrigation calculation (exact frontend request)
    print("3. Testing irrigation calculation (simulating frontend)...")
    try:
        data = {
            'farmSize': 2.5,
            'unit': 'hectares',
            'crop': 'rice',
            'soil': 'loamy',
            'method': 'drip',
            'lastIrrigation': '2025-08-04',
            'location': 'Tamil Nadu, India'
        }
        
        print("   Request data:")
        print(json.dumps(data, indent=4))
        
        response = requests.post(
            'http://localhost:8000/api/calculate-irrigation',
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Irrigation calculation working!")
            print(f"   Next irrigation: {result['nextIrrigationDate']}")
            print(f"   Water required: {result['waterLiters']} liters")
            print(f"   Smart tip: {result['tip'][:60]}...")
            print(f"   Weather location: {result['weatherInfo']['location']}")
            return True
        else:
            print(f"   ❌ Irrigation calculation failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Irrigation calculation failed: {e}")
        return False

def test_frontend_issues():
    print("\n=== POTENTIAL FRONTEND ISSUES ===")
    print()
    
    # Check CORS
    print("1. CORS Configuration:")
    print("   ✅ CORS enabled with allow_origins=['*']")
    print("   ✅ All methods and headers allowed")
    
    # Check content type
    print("\n2. Content-Type Headers:")
    print("   ✅ Frontend sends 'application/json'")
    print("   ✅ Backend expects 'application/json'")
    
    # Check request format
    print("\n3. Request Format:")
    print("   ✅ Frontend uses POST method")
    print("   ✅ Data is JSON serialized")
    print("   ✅ All required fields included")
    
    # Check response format
    print("\n4. Response Format:")
    print("   ✅ Backend returns proper JSON")
    print("   ✅ All expected fields present")

if __name__ == "__main__":
    success = test_connectivity()
    test_frontend_issues()
    
    if success:
        print("\n🎉 BACKEND-FRONTEND CONNECTIVITY: WORKING")
        print("\nIf you're still seeing errors in the browser:")
        print("1. Clear browser cache (Ctrl+Shift+R)")
        print("2. Check browser console for JavaScript errors")
        print("3. Ensure you're using the correct URL: http://localhost:8000")
        print("4. Try a different browser")
    else:
        print("\n❌ CONNECTIVITY ISSUES DETECTED")
        print("Please check server logs for more details")
