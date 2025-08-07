#!/usr/bin/env python3
"""
Test the improved smart tip system with various scenarios
"""
import requests
import json

def test_smart_tips():
    """Test different scenarios to verify smart tip variety"""
    
    print("🧪 SMART TIP VARIETY TEST")
    print("=" * 60)
    
    # Test scenarios designed to trigger different tip types
    test_scenarios = [
        {
            'name': 'Hot & Dry Location',
            'data': {
                'farmSize': 2.0,
                'unit': 'hectares',
                'crop': 'wheat',
                'soil': 'sandy',
                'method': 'sprinkler',
                'bulkDensity': 1.5,
                'lastIrrigation': '2025-08-04',
                'location': 'Phoenix, USA'  # Hot, dry climate
            }
        },
        {
            'name': 'High Rainfall Area',
            'data': {
                'farmSize': 2.0,
                'unit': 'hectares',
                'crop': 'rice',
                'soil': 'clay',
                'method': 'flood',
                'bulkDensity': 1.2,
                'lastIrrigation': '2025-08-04',
                'location': 'Seattle, USA'  # High rainfall
            }
        },
        {
            'name': 'Recent Irrigation',
            'data': {
                'farmSize': 3.0,
                'unit': 'hectares',
                'crop': 'corn',
                'soil': 'loamy',
                'method': 'drip',
                'bulkDensity': 1.3,
                'lastIrrigation': '2025-08-07',  # Very recent
                'location': 'Mumbai, India'
            }
        },
        {
            'name': 'Old Irrigation',
            'data': {
                'farmSize': 3.0,
                'unit': 'hectares',
                'crop': 'corn',
                'soil': 'loamy',
                'method': 'drip',
                'bulkDensity': 1.3,
                'lastIrrigation': '2025-07-28',  # 10+ days ago
                'location': 'Mumbai, India'
            }
        },
        {
            'name': 'Sandy Soil Farm',
            'data': {
                'farmSize': 1.5,
                'unit': 'hectares',
                'crop': 'wheat',
                'soil': 'sandy',
                'method': 'drip',
                'bulkDensity': 1.6,
                'lastIrrigation': '2025-08-05',
                'location': 'Delhi, India'
            }
        },
        {
            'name': 'Clay Soil Farm',
            'data': {
                'farmSize': 1.5,
                'unit': 'hectares',
                'crop': 'wheat',
                'soil': 'clay',
                'method': 'drip',
                'bulkDensity': 1.1,
                'lastIrrigation': '2025-08-05',
                'location': 'Delhi, India'
            }
        },
        {
            'name': 'Rice Crop',
            'data': {
                'farmSize': 2.5,
                'unit': 'hectares',
                'crop': 'rice',
                'soil': 'loamy',
                'method': 'flood',
                'bulkDensity': 1.3,
                'lastIrrigation': '2025-08-04',
                'location': 'Chennai, India'
            }
        },
        {
            'name': 'Sprinkler System',
            'data': {
                'farmSize': 2.0,
                'unit': 'hectares',
                'crop': 'corn',
                'soil': 'loamy',
                'method': 'sprinkler',
                'bulkDensity': 1.4,
                'lastIrrigation': '2025-08-05',
                'location': 'Bangalore, India'
            }
        }
    ]
    
    results = []
    
    for scenario in test_scenarios:
        try:
            response = requests.post('http://localhost:8000/api/calculate-irrigation', 
                                   json=scenario['data'], timeout=15)
            if response.status_code == 200:
                result = response.json()
                tip = result['tip']
                results.append({
                    'scenario': scenario['name'],
                    'tip': tip,
                    'next_date': result['nextIrrigationDate'],
                    'water': result['waterLiters']
                })
                print(f"\n🧪 {scenario['name']}:")
                print(f"   💡 Tip: {tip}")
                print(f"   📅 Next: {result['nextIrrigationDate']}")
                print(f"   💧 Water: {result['waterLiters']:,.0f} L")
            else:
                print(f"\n❌ {scenario['name']}: ERROR {response.status_code}")
                if response.status_code == 500:
                    print(f"   Details: {response.text[:100]}...")
        except Exception as e:
            print(f"\n❌ {scenario['name']}: FAILED - {e}")
    
    # Analysis
    if len(results) >= 2:
        print("\n" + "=" * 60)
        print("📊 SMART TIP ANALYSIS:")
        
        tips = [r['tip'] for r in results]
        unique_tips = set(tips)
        
        print(f"🎯 Total scenarios tested: {len(results)}")
        print(f"🔄 Unique tips generated: {len(unique_tips)}")
        print(f"📈 Tip variety ratio: {len(unique_tips)/len(results)*100:.1f}%")
        
        if len(unique_tips) > 1:
            print("✅ Smart tip system is generating varied responses!")
            
            print("\n🏷️ TIP CATEGORIES FOUND:")
            categories = {
                'Weather': 0,
                'Soil': 0,
                'Crop': 0,
                'Method': 0,
                'Moisture': 0,
                'General': 0
            }
            
            for tip in unique_tips:
                if any(word in tip.lower() for word in ['rain', 'temperature', 'weather', 'hot', 'dry', 'humidity']):
                    categories['Weather'] += 1
                elif any(word in tip.lower() for word in ['sandy', 'clay', 'loamy', 'soil']):
                    categories['Soil'] += 1
                elif any(word in tip.lower() for word in ['rice', 'wheat', 'corn']):
                    categories['Crop'] += 1
                elif any(word in tip.lower() for word in ['drip', 'sprinkler', 'flood']):
                    categories['Method'] += 1
                elif any(word in tip.lower() for word in ['moisture', 'irrigate', 'water']):
                    categories['Moisture'] += 1
                else:
                    categories['General'] += 1
            
            for category, count in categories.items():
                if count > 0:
                    print(f"   {category}: {count} tips")
                    
        else:
            print("⚠️ Smart tip system is still generating repetitive responses")
            
        print(f"\n📋 ALL UNIQUE TIPS:")
        for i, tip in enumerate(unique_tips, 1):
            print(f"   {i}. {tip[:80]}{'...' if len(tip) > 80 else ''}")
    
    return results

if __name__ == "__main__":
    test_smart_tips()
