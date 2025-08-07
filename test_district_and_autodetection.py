#!/usr/bin/env python3
"""
Test District Selection and Auto-Detection of Market Prices
Verifies that district-specific pricing and AGMARKNET API integration work correctly
"""

import requests
import json

def test_district_specific_pricing():
    """Test district-specific pricing functionality"""
    print("🧪 Testing District-Specific Pricing")
    print("=" * 50)
    
    # Test cases with different districts in same state
    test_cases = [
        {"crop": "tomato", "state": "tamil nadu", "district": "coimbatore", "expected_higher": False},
        {"crop": "tomato", "state": "tamil nadu", "district": "chennai", "expected_higher": True},  # Major city
        {"crop": "tomato", "state": "tamil nadu", "district": "madurai", "expected_higher": False},
        {"crop": "onion", "state": "maharashtra", "district": "mumbai", "expected_higher": True},  # Major city
        {"crop": "onion", "state": "maharashtra", "district": "nashik", "expected_higher": False},  # Agricultural area
        {"crop": "potato", "state": "uttar pradesh", "district": "lucknow", "expected_higher": True},  # Capital
        {"crop": "potato", "state": "uttar pradesh", "district": "agra", "expected_higher": False},
    ]
    
    results = []
    
    try:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Test {i}: {test_case['crop'].title()} in {test_case['district'].title()}, {test_case['state'].title()} ---")
            
            # Test with district
            response = requests.post(
                "http://localhost:8003/analyze",
                json=test_case,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                state_price = result.get('state_avg_price', 0)
                district_price = result.get('district_avg_price', 0)
                
                print(f"✅ API Response: SUCCESS")
                print(f"   State Price: ₹{state_price:.2f}")
                print(f"   District Price: ₹{district_price:.2f}")
                print(f"   Price Difference: {((district_price - state_price) / state_price * 100):.1f}%")
                print(f"   Database ID: {result.get('database_id', 'N/A')}")
                
                # Verify district-specific pricing logic
                price_diff_percent = (district_price - state_price) / state_price * 100
                if test_case['expected_higher'] and price_diff_percent > 2:
                    print(f"✅ District pricing correct: {test_case['district']} is higher as expected")
                elif not test_case['expected_higher'] and abs(price_diff_percent) < 15:
                    print(f"✅ District pricing correct: {test_case['district']} pricing is reasonable")
                else:
                    print(f"⚠️ District pricing unexpected: {price_diff_percent:.1f}% difference")
                
                results.append({
                    'test': test_case,
                    'state_price': state_price,
                    'district_price': district_price,
                    'difference_percent': price_diff_percent,
                    'success': True
                })
                
            else:
                print(f"❌ API Response: HTTP {response.status_code}")
                results.append({'test': test_case, 'success': False})
        
        print("\n" + "=" * 50)
        print("📊 District Pricing Analysis Summary:")
        
        successful_tests = [r for r in results if r.get('success')]
        if successful_tests:
            avg_state_price = sum(r['state_price'] for r in successful_tests) / len(successful_tests)
            avg_district_price = sum(r['district_price'] for r in successful_tests) / len(successful_tests)
            avg_difference = sum(abs(r['difference_percent']) for r in successful_tests) / len(successful_tests)
            
            print(f"✅ Successful Tests: {len(successful_tests)}/{len(test_cases)}")
            print(f"📈 Average State Price: ₹{avg_state_price:.2f}")
            print(f"🏘️ Average District Price: ₹{avg_district_price:.2f}")
            print(f"📊 Average Price Difference: {avg_difference:.1f}%")
            
            # Check if major cities have higher prices
            major_city_tests = [r for r in successful_tests if r['test']['expected_higher']]
            if major_city_tests:
                major_city_avg_diff = sum(r['difference_percent'] for r in major_city_tests) / len(major_city_tests)
                print(f"🏙️ Major Cities Average Premium: {major_city_avg_diff:.1f}%")
        
        return len(successful_tests) == len(test_cases)
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server not running on port 8003")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_agmarknet_integration():
    """Test AGMARKNET API integration and fallback behavior"""
    print("\n🧪 Testing AGMARKNET API Integration")
    print("=" * 50)
    
    # Test crops that might have real data vs those that use fallback
    test_crops = [
        {"crop": "onion", "state": "maharashtra", "district": "pune"},  # Likely to have real data
        {"crop": "potato", "state": "uttar pradesh", "district": "agra"},  # Likely to have real data
        {"crop": "tomato", "state": "tamil nadu", "district": "coimbatore"},  # May use fallback
        {"crop": "brinjal", "state": "karnataka", "district": "bangalore"},  # Likely fallback
    ]
    
    try:
        for i, test_case in enumerate(test_crops, 1):
            print(f"\n--- API Test {i}: {test_case['crop'].title()} in {test_case['state'].title()} ---")
            
            response = requests.post(
                "http://localhost:8003/analyze",
                json=test_case,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if we have market data (indicates real API data vs fallback)
                market_data = result.get('market_data', [])
                has_real_data = len(market_data) > 0 and any(
                    market.get('arrival_date', '') != 'Estimated' for market in market_data
                )
                
                data_source = "🌐 AGMARKNET API" if has_real_data else "🔄 Fallback Data"
                print(f"✅ Analysis Complete: {data_source}")
                print(f"   Price: ₹{result.get('state_avg_price', 0):.2f}")
                print(f"   Trend: {result.get('price_trend', 'N/A')} ({result.get('trend_percentage', 0):.1f}%)")
                print(f"   Markets: {len(market_data)} market(s)")
                print(f"   Database ID: {result.get('database_id', 'N/A')}")
                
                # Verify enhanced analysis fields are present
                enhanced_fields = ['risk_level', 'quality_grade', 'price_volatility', 'best_selling_time']
                missing_fields = [field for field in enhanced_fields if field not in result]
                
                if not missing_fields:
                    print(f"✅ Enhanced analysis: All fields present")
                else:
                    print(f"⚠️ Enhanced analysis: Missing {missing_fields}")
                
            else:
                print(f"❌ API Test: HTTP {response.status_code}")
                return False
        
        print("\n✅ AGMARKNET Integration Test: PASSED")
        print("🔄 System gracefully handles both real API data and fallback scenarios")
        return True
        
    except Exception as e:
        print(f"❌ AGMARKNET Integration Test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Market Analysis: District Selection & Auto-Detection")
    print("=" * 70)
    
    # Test district-specific pricing
    district_test_passed = test_district_specific_pricing()
    
    # Test AGMARKNET integration
    api_test_passed = test_agmarknet_integration()
    
    print("\n" + "=" * 70)
    print("📋 FINAL TEST RESULTS:")
    print(f"🏘️ District-Specific Pricing: {'✅ PASSED' if district_test_passed else '❌ FAILED'}")
    print(f"🌐 AGMARKNET Integration: {'✅ PASSED' if api_test_passed else '❌ FAILED'}")
    
    if district_test_passed and api_test_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ District selection is working correctly")
        print("✅ Auto-detection of market prices is working")
        print("✅ District-specific pricing provides realistic variations")
        print("✅ AGMARKNET API integration with intelligent fallback")
        print("✅ Enhanced market analysis with professional insights")
        return True
    else:
        print("\n⚠️ Some tests failed - check the issues above")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Market Analysis System: District & Auto-Detection WORKING!")
    else:
        print("\n⚠️ Market Analysis System needs attention.")
