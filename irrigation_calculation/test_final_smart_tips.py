#!/usr/bin/env python3
"""
Final comprehensive test of the improved smart tip system
"""
import requests
import json

def test_comprehensive_smart_tips():
    """Test comprehensive scenarios with valid crops to verify smart tip variety"""
    
    print("🎯 COMPREHENSIVE SMART TIP TEST")
    print("=" * 70)
    print("Testing improved smart tip system with various scenarios...")
    
    # Test scenarios designed to trigger different tip categories
    test_scenarios = [
        {
            'name': 'Recent Irrigation - Should delay',
            'data': {
                'farmSize': 2.0,
                'unit': 'hectares',
                'crop': 'wheat',
                'soil': 'sandy',
                'method': 'drip',
                'bulkDensity': 1.5,
                'lastIrrigation': '2025-08-07',  # Very recent
                'location': 'Delhi, India'
            }
        },
        {
            'name': 'Old Irrigation - Should need water',
            'data': {
                'farmSize': 2.0,
                'unit': 'hectares',
                'crop': 'wheat',
                'soil': 'sandy',
                'method': 'drip',
                'bulkDensity': 1.5,
                'lastIrrigation': '2025-07-28',  # 10+ days ago
                'location': 'Delhi, India'
            }
        },
        {
            'name': 'Rice Crop - Water loving',
            'data': {
                'farmSize': 3.0,
                'unit': 'hectares',
                'crop': 'rice',
                'soil': 'clay',
                'method': 'flood',
                'bulkDensity': 1.2,
                'lastIrrigation': '2025-08-04',
                'location': 'Chennai, India'
            }
        },
        {
            'name': 'Cotton Crop - Drought tolerant',
            'data': {
                'farmSize': 4.0,
                'unit': 'hectares',
                'crop': 'cotton',
                'soil': 'sandy',
                'method': 'drip',
                'bulkDensity': 1.6,
                'lastIrrigation': '2025-08-03',
                'location': 'Gujarat, India'
            }
        },
        {
            'name': 'Sugarcane - High water need',
            'data': {
                'farmSize': 5.0,
                'unit': 'hectares',
                'crop': 'sugarcane',
                'soil': 'loamy',
                'method': 'sprinkler',
                'bulkDensity': 1.3,
                'lastIrrigation': '2025-08-05',
                'location': 'Maharashtra, India'
            }
        },
        {
            'name': 'Sandy Soil - Fast drainage',
            'data': {
                'farmSize': 2.5,
                'unit': 'hectares',
                'crop': 'wheat',
                'soil': 'sandy',
                'method': 'drip',
                'bulkDensity': 1.7,
                'lastIrrigation': '2025-08-05',
                'location': 'Rajasthan, India'
            }
        },
        {
            'name': 'Clay Soil - Slow drainage',
            'data': {
                'farmSize': 2.5,
                'unit': 'hectares',
                'crop': 'wheat',
                'soil': 'clay',
                'method': 'drip',
                'bulkDensity': 1.0,
                'lastIrrigation': '2025-08-05',
                'location': 'Punjab, India'
            }
        },
        {
            'name': 'Sprinkler Method',
            'data': {
                'farmSize': 3.0,
                'unit': 'hectares',
                'crop': 'cotton',
                'soil': 'loamy',
                'method': 'sprinkler',
                'bulkDensity': 1.4,
                'lastIrrigation': '2025-08-05',
                'location': 'Karnataka, India'
            }
        },
        {
            'name': 'Flood Method',
            'data': {
                'farmSize': 3.0,
                'unit': 'hectares',
                'crop': 'rice',
                'soil': 'loamy',
                'method': 'flood',
                'bulkDensity': 1.3,
                'lastIrrigation': '2025-08-04',
                'location': 'West Bengal, India'
            }
        },
        {
            'name': 'High Rainfall Location',
            'data': {
                'farmSize': 2.0,
                'unit': 'hectares',
                'crop': 'rice',
                'soil': 'clay',
                'method': 'flood',
                'bulkDensity': 1.1,
                'lastIrrigation': '2025-08-04',
                'location': 'Kerala, India'
            }
        }
    ]
    
    results = []
    successful_tests = 0
    
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
                    'water': result['waterLiters'],
                    'crop': scenario['data']['crop'],
                    'soil': scenario['data']['soil'],
                    'method': scenario['data']['method']
                })
                successful_tests += 1
                print(f"\n✅ {scenario['name']}:")
                print(f"   💡 {tip}")
                print(f"   📅 Next: {result['nextIrrigationDate']} | 💧 {result['waterLiters']:,.0f} L")
            else:
                print(f"\n❌ {scenario['name']}: ERROR {response.status_code}")
                if response.status_code == 500:
                    error_detail = response.json().get('detail', 'Unknown error')
                    print(f"   Details: {error_detail}")
        except Exception as e:
            print(f"\n❌ {scenario['name']}: FAILED - {e}")
    
    # Comprehensive Analysis
    if len(results) >= 2:
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE SMART TIP ANALYSIS:")
        
        tips = [r['tip'] for r in results]
        unique_tips = set(tips)
        
        print(f"🎯 Total scenarios: {len(test_scenarios)}")
        print(f"✅ Successful tests: {successful_tests}")
        print(f"🔄 Unique tips generated: {len(unique_tips)}")
        print(f"📈 Success rate: {successful_tests/len(test_scenarios)*100:.1f}%")
        print(f"🎨 Tip variety: {len(unique_tips)/successful_tests*100:.1f}%")
        
        # Categorize tips
        tip_categories = {
            '🌧️ Weather-based': [],
            '💧 Soil Moisture': [],
            '🌾 Crop-specific': [],
            '💦 Irrigation Method': [],
            '🏖️ Soil Type': [],
            '⚠️ Priority/Urgency': [],
            '📊 General': []
        }
        
        for tip in unique_tips:
            tip_lower = tip.lower()
            categorized = False
            
            if any(word in tip_lower for word in ['rainfall', 'rain', 'weather', 'temperature', 'humidity', 'hot', 'dry']):
                tip_categories['🌧️ Weather-based'].append(tip[:60] + '...' if len(tip) > 60 else tip)
                categorized = True
            if any(word in tip_lower for word in ['soil moisture', 'moisture']):
                tip_categories['💧 Soil Moisture'].append(tip[:60] + '...' if len(tip) > 60 else tip)
                categorized = True
            if any(word in tip_lower for word in ['rice', 'wheat', 'cotton', 'sugarcane']):
                tip_categories['🌾 Crop-specific'].append(tip[:60] + '...' if len(tip) > 60 else tip)
                categorized = True
            if any(word in tip_lower for word in ['drip', 'sprinkler', 'flood']):
                tip_categories['💦 Irrigation Method'].append(tip[:60] + '...' if len(tip) > 60 else tip)
                categorized = True
            if any(word in tip_lower for word in ['sandy', 'clay', 'loamy']):
                tip_categories['🏖️ Soil Type'].append(tip[:60] + '...' if len(tip) > 60 else tip)
                categorized = True
            if any(word in tip_lower for word in ['priority', 'urgent', 'critical', 'high priority']):
                tip_categories['⚠️ Priority/Urgency'].append(tip[:60] + '...' if len(tip) > 60 else tip)
                categorized = True
            if not categorized:
                tip_categories['📊 General'].append(tip[:60] + '...' if len(tip) > 60 else tip)
        
        print(f"\n🏷️ TIP CATEGORIES:")
        for category, tips_in_category in tip_categories.items():
            if tips_in_category:
                print(f"\n{category} ({len(tips_in_category)} tips):")
                for tip in tips_in_category:
                    print(f"   • {tip}")
        
        # Success indicators
        print(f"\n🎯 SYSTEM PERFORMANCE:")
        if len(unique_tips)/successful_tests >= 0.7:
            print("✅ EXCELLENT: High tip variety (70%+ unique)")
        elif len(unique_tips)/successful_tests >= 0.5:
            print("✅ GOOD: Moderate tip variety (50%+ unique)")
        else:
            print("⚠️ NEEDS IMPROVEMENT: Low tip variety (<50% unique)")
            
        if successful_tests/len(test_scenarios) >= 0.8:
            print("✅ EXCELLENT: High success rate (80%+ working)")
        elif successful_tests/len(test_scenarios) >= 0.6:
            print("✅ GOOD: Moderate success rate (60%+ working)")
        else:
            print("⚠️ NEEDS IMPROVEMENT: Low success rate (<60% working)")
    
    return results

if __name__ == "__main__":
    test_comprehensive_smart_tips()
