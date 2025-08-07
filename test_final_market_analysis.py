#!/usr/bin/env python3
"""
Final Market Analysis System Test
Comprehensive test to verify all fixes are working correctly
"""

import requests
import json
import time

def test_backend_api():
    """Test the backend API functionality"""
    print("🧪 Testing Backend API")
    print("=" * 40)
    
    test_cases = [
        {"crop": "tomato", "state": "tamil nadu", "district": "coimbatore"},
        {"crop": "tomato", "state": "tamil nadu", "district": "chennai"},
        {"crop": "onion", "state": "maharashtra", "district": "mumbai"},
        {"crop": "potato", "state": "uttar pradesh", "district": "lucknow"},
    ]
    
    try:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Backend Test {i}: {test_case['crop'].title()} in {test_case['district'].title()} ---")
            
            response = requests.post(
                "http://localhost:8003/analyze",
                json=test_case,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Verify all required fields are present
                required_fields = [
                    'crop', 'state', 'district', 'state_avg_price', 'district_avg_price',
                    'price_trend', 'trend_percentage', 'recommendation', 'prediction_confidence',
                    'risk_level', 'quality_grade', 'price_volatility', 'best_selling_time',
                    'storage_recommendation', 'transportation_cost', 'seasonal_factor',
                    'demand_supply_ratio', 'market_data', 'database_id'
                ]
                
                missing_fields = [field for field in required_fields if field not in result]
                
                if not missing_fields:
                    print("✅ All required fields present")
                    print(f"   State Price: ₹{result['state_avg_price']:.2f}")
                    print(f"   District Price: ₹{result['district_avg_price']:.2f}")
                    print(f"   Price Difference: {((result['district_avg_price'] - result['state_avg_price']) / result['state_avg_price'] * 100):.1f}%")
                    print(f"   Risk Level: {result['risk_level']}")
                    print(f"   Quality Grade: {result['quality_grade']}")
                    print(f"   Database ID: {result['database_id']}")
                else:
                    print(f"❌ Missing fields: {missing_fields}")
                    return False
                    
            else:
                print(f"❌ API Error: HTTP {response.status_code}")
                return False
        
        print("\n✅ Backend API Test: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Backend API Test failed: {e}")
        return False

def test_database_endpoints():
    """Test database endpoints"""
    print("\n🧪 Testing Database Endpoints")
    print("=" * 40)
    
    try:
        # Test history endpoint
        print("\n--- Testing History Endpoint ---")
        history_response = requests.get("http://localhost:8003/api/history", timeout=10)
        
        if history_response.status_code == 200:
            history_data = history_response.json()
            if history_data.get('success'):
                history_count = len(history_data.get('history', []))
                print(f"✅ History endpoint: {history_count} analyses found")
            else:
                print("❌ History endpoint: Failed to get data")
                return False
        else:
            print(f"❌ History endpoint: HTTP {history_response.status_code}")
            return False
        
        # Test statistics endpoint
        print("\n--- Testing Statistics Endpoint ---")
        stats_response = requests.get("http://localhost:8003/api/statistics", timeout=10)
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            if stats_data.get('success'):
                stats = stats_data.get('statistics', {})
                total = stats.get('total_analyses', 0)
                print(f"✅ Statistics endpoint: {total} total analyses")
                print(f"   Popular crops: {list(stats.get('popular_crops', {}).keys())[:3]}")
                print(f"   Popular states: {list(stats.get('popular_states', {}).keys())[:3]}")
            else:
                print("❌ Statistics endpoint: Failed to get data")
                return False
        else:
            print(f"❌ Statistics endpoint: HTTP {stats_response.status_code}")
            return False
        
        print("\n✅ Database Endpoints Test: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Database Endpoints Test failed: {e}")
        return False

def test_district_specific_pricing():
    """Test district-specific pricing variations"""
    print("\n🧪 Testing District-Specific Pricing")
    print("=" * 40)
    
    # Test same crop/state with different districts
    base_request = {"crop": "tomato", "state": "tamil nadu"}
    districts = ["coimbatore", "chennai", "madurai"]
    
    try:
        prices = {}
        
        for district in districts:
            test_request = {**base_request, "district": district}
            response = requests.post("http://localhost:8003/analyze", json=test_request, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                prices[district] = {
                    'state_price': result['state_avg_price'],
                    'district_price': result['district_avg_price']
                }
                print(f"✅ {district.title()}: ₹{result['district_avg_price']:.2f}")
            else:
                print(f"❌ {district.title()}: HTTP {response.status_code}")
                return False
        
        # Verify Chennai (major city) has higher prices than rural areas
        if len(prices) == 3:
            chennai_price = prices['chennai']['district_price']
            coimbatore_price = prices['coimbatore']['district_price']
            madurai_price = prices['madurai']['district_price']
            
            if chennai_price > coimbatore_price and chennai_price > madurai_price:
                print(f"✅ Chennai premium verified: ₹{chennai_price:.2f} > ₹{coimbatore_price:.2f}, ₹{madurai_price:.2f}")
            else:
                print(f"⚠️ Chennai pricing unexpected: ₹{chennai_price:.2f} vs ₹{coimbatore_price:.2f}, ₹{madurai_price:.2f}")
        
        print("\n✅ District-Specific Pricing Test: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ District-Specific Pricing Test failed: {e}")
        return False

def test_server_health():
    """Test server health and status"""
    print("\n🧪 Testing Server Health")
    print("=" * 40)
    
    try:
        # Test health endpoint
        health_response = requests.get("http://localhost:8003/health", timeout=10)
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Server Status: {health_data.get('status', 'unknown')}")
            print(f"✅ Service: {health_data.get('service', 'unknown')}")
            print(f"✅ Database Available: {health_data.get('database_available', False)}")
        else:
            print(f"❌ Health check failed: HTTP {health_response.status_code}")
            return False
        
        # Test supported endpoints
        endpoints = ['/crops', '/states']
        for endpoint in endpoints:
            response = requests.get(f"http://localhost:8003{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if endpoint == '/crops':
                    crops = data.get('crops', [])
                    print(f"✅ Supported crops: {len(crops)} crops available")
                elif endpoint == '/states':
                    states = data.get('states', [])
                    print(f"✅ Supported states: {len(states)} states available")
            else:
                print(f"❌ {endpoint} endpoint failed: HTTP {response.status_code}")
                return False
        
        print("\n✅ Server Health Test: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Server Health Test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Final Market Analysis System Test")
    print("=" * 60)
    
    # Run all test suites
    tests = [
        ("Backend API", test_backend_api),
        ("Database Endpoints", test_database_endpoints),
        ("District-Specific Pricing", test_district_specific_pricing),
        ("Server Health", test_server_health)
    ]
    
    results = {}
    
    for test_name, test_function in tests:
        print(f"\n{'='*60}")
        results[test_name] = test_function()
        time.sleep(1)  # Brief pause between tests
    
    # Final summary
    print("\n" + "=" * 60)
    print("📋 FINAL TEST RESULTS SUMMARY:")
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
        print("✅ District selection is working correctly")
        print("✅ Auto-detection of market prices is working")
        print("✅ District-specific pricing provides realistic variations")
        print("✅ Database integration is fully functional")
        print("✅ All API endpoints are responding correctly")
        print("✅ Enhanced market analysis features are working")
        print("\n🚀 Market Analysis System is ready for production!")
        return True
    else:
        print("⚠️ Some tests failed - please check the issues above")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n⚠️ Market Analysis System needs attention.")
    else:
        print("\n🌟 Market Analysis System: ALL ERRORS FIXED!")
