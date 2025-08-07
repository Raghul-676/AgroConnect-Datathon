#!/usr/bin/env python3
"""
Verification test to check if irrigation system gives different results for different inputs
"""
import requests
import json

def test_irrigation(name, test_data):
    """Test irrigation calculation with given data"""
    try:
        response = requests.post('http://localhost:8000/api/calculate-irrigation', 
                               json=test_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"\n🧪 {name}:")
            print(f"   📅 Next Irrigation: {result['nextIrrigationDate']}")
            print(f"   💧 Water Required: {result['waterLiters']:,.0f} liters")
            print(f"   💡 Tip: {result['tip'][:60]}...")
            return result
        else:
            print(f"\n❌ {name}: ERROR {response.status_code}")
            return None
    except Exception as e:
        print(f"\n❌ {name}: FAILED - {e}")
        return None

if __name__ == "__main__":
    print("🔍 VERIFICATION TEST - Different Inputs Should Give Different Results")
    print("=" * 70)
    
    # Test Case 1: Sandy soil, high bulk density, recent irrigation
    test1 = {
        'farmSize': 2.0,
        'unit': 'hectares', 
        'crop': 'wheat',
        'soil': 'sandy',
        'method': 'sprinkler',
        'bulkDensity': 1.6,  # High bulk density
        'lastIrrigation': '2025-08-06',  # 1 day ago - recent
        'location': 'Delhi, India'
    }
    
    # Test Case 2: Clay soil, low bulk density, older irrigation  
    test2 = {
        'farmSize': 2.0,
        'unit': 'hectares',
        'crop': 'wheat', 
        'soil': 'clay',
        'method': 'drip',
        'bulkDensity': 1.1,  # Low bulk density
        'lastIrrigation': '2025-08-02',  # 5 days ago - older
        'location': 'Delhi, India'
    }
    
    # Test Case 3: Large farm, different crop
    test3 = {
        'farmSize': 10.0,  # Much larger farm
        'unit': 'hectares',
        'crop': 'rice',  # Different crop
        'soil': 'loamy', 
        'method': 'flood',  # Different method
        'bulkDensity': 1.3,
        'lastIrrigation': '2025-08-04',  # 3 days ago
        'location': 'Delhi, India'
    }
    
    # Test Case 4: Same as test1 but different bulk density
    test4 = {
        'farmSize': 2.0,
        'unit': 'hectares', 
        'crop': 'wheat',
        'soil': 'sandy',
        'method': 'sprinkler',
        'bulkDensity': 1.2,  # Lower bulk density than test1
        'lastIrrigation': '2025-08-06',  # Same as test1
        'location': 'Delhi, India'
    }
    
    # Run tests
    result1 = test_irrigation("Sandy/High BD/Recent", test1)
    result2 = test_irrigation("Clay/Low BD/Old", test2) 
    result3 = test_irrigation("Large Farm/Rice/Flood", test3)
    result4 = test_irrigation("Sandy/Low BD/Recent", test4)
    
    # Analysis
    print("\n" + "=" * 70)
    print("📊 ANALYSIS:")
    
    if all([result1, result2, result3, result4]):
        dates = [r['nextIrrigationDate'] for r in [result1, result2, result3, result4]]
        waters = [r['waterLiters'] for r in [result1, result2, result3, result4]]
        
        print(f"✅ All tests completed successfully")
        print(f"📅 Irrigation dates vary: {len(set(dates)) > 1}")
        print(f"💧 Water amounts vary: {len(set(waters)) > 1}")
        print(f"📈 Date range: {min(dates)} to {max(dates)}")
        print(f"💧 Water range: {min(waters):,.0f} to {max(waters):,.0f} liters")
        
        # Check if bulk density affects results (test1 vs test4)
        if result1['waterLiters'] != result4['waterLiters']:
            print(f"✅ Bulk density affects results: {result1['waterLiters']:,.0f} vs {result4['waterLiters']:,.0f}")
        else:
            print(f"⚠️  Bulk density may not be affecting results significantly")
            
    else:
        print("❌ Some tests failed")
