#!/usr/bin/env python3
"""
Test with extreme differences to verify system responsiveness
"""
import requests
import json

def test_extreme_cases():
    """Test with very different scenarios"""
    
    print("🧪 EXTREME DIFFERENCE TEST")
    print("=" * 60)
    
    # Test 1: Very recent irrigation (should delay next irrigation)
    recent_irrigation = {
        'farmSize': 1.0,
        'unit': 'hectares',
        'crop': 'wheat',
        'soil': 'sandy',
        'method': 'drip',
        'bulkDensity': 1.5,
        'lastIrrigation': '2025-08-07',  # Today/yesterday
        'location': 'Mumbai, India'
    }
    
    # Test 2: Very old irrigation (should need immediate irrigation)
    old_irrigation = {
        'farmSize': 1.0,
        'unit': 'hectares',
        'crop': 'wheat',
        'soil': 'sandy',
        'method': 'drip',
        'bulkDensity': 1.5,
        'lastIrrigation': '2025-07-25',  # 2+ weeks ago
        'location': 'Mumbai, India'
    }
    
    # Test 3: Tiny farm
    tiny_farm = {
        'farmSize': 0.1,
        'unit': 'hectares',
        'crop': 'rice',
        'soil': 'loamy',
        'method': 'drip',
        'bulkDensity': 1.3,
        'lastIrrigation': '2025-08-04',
        'location': 'Delhi, India'
    }
    
    # Test 4: Huge farm
    huge_farm = {
        'farmSize': 50.0,
        'unit': 'hectares',
        'crop': 'rice',
        'soil': 'loamy',
        'method': 'drip',
        'bulkDensity': 1.3,
        'lastIrrigation': '2025-08-04',
        'location': 'Delhi, India'
    }
    
    # Test 5: Different locations (should have different weather)
    hot_location = {
        'farmSize': 2.0,
        'unit': 'hectares',
        'crop': 'corn',
        'soil': 'sandy',
        'method': 'sprinkler',
        'bulkDensity': 1.4,
        'lastIrrigation': '2025-08-04',
        'location': 'Rajasthan, India'  # Hot, dry region
    }
    
    rainy_location = {
        'farmSize': 2.0,
        'unit': 'hectares',
        'crop': 'corn',
        'soil': 'sandy',
        'method': 'sprinkler',
        'bulkDensity': 1.4,
        'lastIrrigation': '2025-08-04',
        'location': 'Kerala, India'  # High rainfall region
    }
    
    tests = [
        ("Recent Irrigation", recent_irrigation),
        ("Old Irrigation", old_irrigation),
        ("Tiny Farm (0.1 ha)", tiny_farm),
        ("Huge Farm (50 ha)", huge_farm),
        ("Hot Location", hot_location),
        ("Rainy Location", rainy_location)
    ]
    
    results = []
    
    for name, test_data in tests:
        try:
            response = requests.post('http://localhost:8000/api/calculate-irrigation', 
                                   json=test_data, timeout=15)
            if response.status_code == 200:
                result = response.json()
                results.append({
                    'name': name,
                    'next_date': result['nextIrrigationDate'],
                    'water_liters': result['waterLiters'],
                    'tip': result['tip']
                })
                print(f"\n🧪 {name}:")
                print(f"   📅 Next: {result['nextIrrigationDate']}")
                print(f"   💧 Water: {result['waterLiters']:,.0f} L")
                print(f"   💡 Tip: {result['tip'][:50]}...")
            else:
                print(f"\n❌ {name}: ERROR {response.status_code}")
        except Exception as e:
            print(f"\n❌ {name}: FAILED - {e}")
    
    # Analysis
    if len(results) >= 2:
        print("\n" + "=" * 60)
        print("📊 SYSTEM RESPONSIVENESS ANALYSIS:")
        
        dates = [r['next_date'] for r in results]
        waters = [r['water_liters'] for r in results]
        
        print(f"📅 Date variation: {len(set(dates))} unique dates")
        print(f"💧 Water variation: {len(set(waters))} unique amounts")
        print(f"📈 Date range: {min(dates)} to {max(dates)}")
        print(f"💧 Water range: {min(waters):,.0f} to {max(waters):,.0f} L")
        
        # Check specific expectations
        recent_result = next((r for r in results if r['name'] == "Recent Irrigation"), None)
        old_result = next((r for r in results if r['name'] == "Old Irrigation"), None)
        tiny_result = next((r for r in results if r['name'] == "Tiny Farm (0.1 ha)"), None)
        huge_result = next((r for r in results if r['name'] == "Huge Farm (50 ha)"), None)
        
        print("\n🔍 LOGICAL CHECKS:")
        
        if recent_result and old_result:
            if recent_result['next_date'] >= old_result['next_date']:
                print("✅ Recent irrigation → Later next irrigation date")
            else:
                print("❌ Recent irrigation should delay next irrigation")
        
        if tiny_result and huge_result:
            if tiny_result['water_liters'] < huge_result['water_liters']:
                print("✅ Tiny farm → Less water than huge farm")
            else:
                print("❌ Farm size should affect water requirements")
        
        if len(set(waters)) > 1:
            print("✅ System produces different water amounts for different inputs")
        else:
            print("❌ System may not be responding to input variations")
            
        if len(set(dates)) > 1:
            print("✅ System produces different irrigation dates")
        else:
            print("❌ System may not be responding to timing variations")
    
    return results

if __name__ == "__main__":
    test_extreme_cases()
