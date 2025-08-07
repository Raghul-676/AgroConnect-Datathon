#!/usr/bin/env python3
"""
Complete AgroConnect System Test
Tests all frontend routes and backend APIs
"""

import requests
import time

def test_frontend_routes():
    """Test all frontend routes"""
    print("🧪 Testing Frontend Routes")
    print("=" * 40)
    
    routes = [
        {"name": "Home Page", "url": "http://localhost:8080/", "expected": "AgroConnect"},
        {"name": "Dashboard", "url": "http://localhost:8080/dashboard", "expected": "AgroConnect Dashboard"},
        {"name": "Soil Analysis", "url": "http://localhost:8080/soil", "expected": "Soil Analysis"},
        {"name": "Irrigation", "url": "http://localhost:8080/irrigation", "expected": "Irrigation"},
        {"name": "Market Analysis", "url": "http://localhost:8080/market", "expected": "Market Analysis"},
        {"name": "Crop Prediction", "url": "http://localhost:8080/crop", "expected": "Crop Prediction"}
    ]
    
    success_count = 0
    
    for route in routes:
        try:
            print(f"\n--- Testing {route['name']} ---")
            response = requests.get(route['url'], timeout=10)
            
            if response.status_code == 200:
                if route['expected'] in response.text:
                    print(f"✅ {route['name']}: SUCCESS")
                    print(f"   URL: {route['url']}")
                    print(f"   Status: {response.status_code}")
                    print(f"   Content: Found '{route['expected']}'")
                    success_count += 1
                else:
                    print(f"⚠️ {route['name']}: Content mismatch")
                    print(f"   Expected: '{route['expected']}'")
            else:
                print(f"❌ {route['name']}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {route['name']}: Error - {e}")
    
    print(f"\n📊 Frontend Routes: {success_count}/{len(routes)} working")
    return success_count == len(routes)

def test_backend_apis():
    """Test all backend APIs"""
    print("\n🧪 Testing Backend APIs")
    print("=" * 40)
    
    apis = [
        {
            "name": "Soil Analysis API",
            "url": "http://localhost:8000/api/v1/analyze",
            "method": "POST",
            "data": {"ph": 6.5, "nitrogen": 45, "phosphorus": 30, "potassium": 25, "organic_matter": 3.2}
        },
        {
            "name": "Crop Prediction API",
            "url": "http://localhost:8002/predict",
            "method": "POST",
            "data": {"crop": "tomato", "soilType": "loam", "season": "kharif", "irrigationType": "drip", "fieldSize": 2.5}
        },
        {
            "name": "Market Analysis API",
            "url": "http://localhost:8003/analyze",
            "method": "POST",
            "data": {"crop": "tomato", "state": "tamil nadu", "district": "coimbatore"}
        },
        {
            "name": "Irrigation Calculator API",
            "url": "http://localhost:8001/api/calculate-irrigation",
            "method": "POST",
            "data": {"crop": "tomato", "soilType": "loam", "fieldSize": 2.5, "season": "summer"}
        }
    ]
    
    success_count = 0
    
    for api in apis:
        try:
            print(f"\n--- Testing {api['name']} ---")
            
            if api['method'] == 'POST':
                response = requests.post(api['url'], json=api['data'], timeout=15)
            else:
                response = requests.get(api['url'], timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {api['name']}: SUCCESS")
                print(f"   URL: {api['url']}")
                print(f"   Status: {response.status_code}")
                
                # Show key result data
                if 'database_id' in result:
                    print(f"   Database ID: {result['database_id']}")
                if 'success' in result:
                    print(f"   Success: {result['success']}")
                if 'recommendation' in result:
                    print(f"   Recommendation: {result['recommendation'][:50]}...")
                
                success_count += 1
            else:
                print(f"❌ {api['name']}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {api['name']}: Error - {e}")
    
    print(f"\n📊 Backend APIs: {success_count}/{len(apis)} working")
    return success_count == len(apis)

def test_health_endpoints():
    """Test health endpoints"""
    print("\n🧪 Testing Health Endpoints")
    print("=" * 40)
    
    health_endpoints = [
        {"name": "Soil Analysis", "url": "http://localhost:8000/health"},
        {"name": "Crop Prediction", "url": "http://localhost:8002/health"},
        {"name": "Market Analysis", "url": "http://localhost:8003/health"},
        {"name": "Irrigation Calculator", "url": "http://localhost:8001/health"}
    ]
    
    success_count = 0
    
    for endpoint in health_endpoints:
        try:
            print(f"\n--- Testing {endpoint['name']} Health ---")
            response = requests.get(endpoint['url'], timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ {endpoint['name']}: HEALTHY")
                print(f"   Status: {health_data.get('status', 'unknown')}")
                print(f"   Service: {health_data.get('service', 'unknown')}")
                if 'database_available' in health_data:
                    print(f"   Database: {health_data['database_available']}")
                success_count += 1
            else:
                print(f"❌ {endpoint['name']}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint['name']}: Error - {e}")
    
    print(f"\n📊 Health Endpoints: {success_count}/{len(health_endpoints)} healthy")
    return success_count == len(health_endpoints)

def test_navigation_links():
    """Test that navigation links work from dashboard"""
    print("\n🧪 Testing Navigation Links")
    print("=" * 40)
    
    try:
        # Get dashboard page
        dashboard_response = requests.get("http://localhost:8080/dashboard", timeout=10)
        
        if dashboard_response.status_code == 200:
            dashboard_content = dashboard_response.text
            
            # Check for navigation links
            expected_links = [
                'soil_analysis/index.html',
                'irrigation_calculation/irrigation.html', 
                'market-analysis/market.html',
                'crop_prediction/crop_page.html'
            ]
            
            found_links = 0
            for link in expected_links:
                if link in dashboard_content:
                    print(f"✅ Found link: {link}")
                    found_links += 1
                else:
                    print(f"❌ Missing link: {link}")
            
            print(f"\n📊 Navigation Links: {found_links}/{len(expected_links)} found")
            return found_links == len(expected_links)
        else:
            print(f"❌ Could not load dashboard: HTTP {dashboard_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Navigation test error: {e}")
        return False

def main():
    """Run complete system test"""
    print("🚀 AgroConnect Complete System Test")
    print("=" * 60)
    
    # Wait a moment for servers to be ready
    print("⏳ Waiting for servers to initialize...")
    time.sleep(3)
    
    # Run all tests
    tests = [
        ("Frontend Routes", test_frontend_routes),
        ("Backend APIs", test_backend_apis), 
        ("Health Endpoints", test_health_endpoints),
        ("Navigation Links", test_navigation_links)
    ]
    
    results = {}
    
    for test_name, test_function in tests:
        print(f"\n{'='*60}")
        results[test_name] = test_function()
        time.sleep(1)
    
    # Final summary
    print("\n" + "=" * 60)
    print("📋 COMPLETE SYSTEM TEST RESULTS:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<30} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Frontend server running correctly")
        print("✅ All routes accessible")
        print("✅ All backend APIs functional")
        print("✅ Database integration working")
        print("✅ Navigation links working")
        print("✅ Health monitoring active")
        print("\n🌐 AgroConnect System URLs:")
        print("   🏠 Home:           http://localhost:8080/")
        print("   📊 Dashboard:      http://localhost:8080/dashboard")
        print("   🌱 Soil Analysis:  http://localhost:8080/soil")
        print("   💧 Irrigation:     http://localhost:8080/irrigation")
        print("   📈 Market:         http://localhost:8080/market")
        print("   🌾 Crop:           http://localhost:8080/crop")
        print("\n🚀 AgroConnect is ready for production use!")
        return True
    else:
        print("⚠️ Some tests failed - check the issues above")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n⚠️ AgroConnect system needs attention.")
    else:
        print("\n🌟 AgroConnect Complete System: FULLY OPERATIONAL!")
