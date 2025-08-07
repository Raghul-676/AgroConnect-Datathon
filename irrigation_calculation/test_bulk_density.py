#!/usr/bin/env python3
"""
Test specifically for bulk density impact on irrigation calculations
"""
import requests
import json

def test_bulk_density_impact():
    """Test if different bulk densities give different results"""
    
    base_data = {
        'farmSize': 3.0,
        'unit': 'hectares',
        'crop': 'rice',
        'soil': 'loamy',
        'method': 'drip',
        'lastIrrigation': '2025-08-04',
        'location': 'Chennai, India'
    }
    
    bulk_densities = [1.0, 1.2, 1.4, 1.6, 1.8]  # Range from low to high
    
    print("🧪 BULK DENSITY IMPACT TEST")
    print("=" * 50)
    print("Testing same conditions with different bulk densities:")
    
    results = []
    
    for bd in bulk_densities:
        test_data = base_data.copy()
        test_data['bulkDensity'] = bd
        
        try:
            response = requests.post('http://localhost:8000/api/calculate-irrigation', 
                                   json=test_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                results.append({
                    'bulk_density': bd,
                    'next_date': result['nextIrrigationDate'],
                    'water_liters': result['waterLiters'],
                    'tip': result['tip'][:40] + "..."
                })
                print(f"\n📊 Bulk Density: {bd} g/cm³")
                print(f"   📅 Next: {result['nextIrrigationDate']}")
                print(f"   💧 Water: {result['waterLiters']:,.0f} L")
                print(f"   💡 Tip: {result['tip'][:40]}...")
            else:
                print(f"\n❌ BD {bd}: ERROR {response.status_code}")
        except Exception as e:
            print(f"\n❌ BD {bd}: FAILED - {e}")
    
    # Analysis
    if len(results) >= 2:
        print("\n" + "=" * 50)
        print("📈 ANALYSIS:")
        
        water_amounts = [r['water_liters'] for r in results]
        dates = [r['next_date'] for r in results]
        
        print(f"💧 Water range: {min(water_amounts):,.0f} - {max(water_amounts):,.0f} L")
        print(f"📅 Date range: {min(dates)} to {max(dates)}")
        print(f"🔄 Unique water amounts: {len(set(water_amounts))}")
        print(f"🔄 Unique dates: {len(set(dates))}")
        
        if len(set(water_amounts)) > 1:
            print("✅ Bulk density DOES affect water calculations")
            
            # Show trend
            print("\n📊 TREND ANALYSIS:")
            for i, result in enumerate(results):
                change = ""
                if i > 0:
                    prev_water = results[i-1]['water_liters']
                    curr_water = result['water_liters']
                    diff = curr_water - prev_water
                    change = f" ({diff:+,.0f} L)"
                
                print(f"   BD {result['bulk_density']}: {result['water_liters']:,.0f} L{change}")
        else:
            print("⚠️  Bulk density does NOT seem to affect calculations")
    
    return results

if __name__ == "__main__":
    test_bulk_density_impact()
