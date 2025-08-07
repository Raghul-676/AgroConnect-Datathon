#!/usr/bin/env python3
"""
Test script for terminal soil analyzer
"""

import json
from soil_analyzer import TerminalSoilAnalyzer

def test_analyzer():
    """Test the terminal analyzer with different scenarios"""
    
    analyzer = TerminalSoilAnalyzer()
    
    print("🌱 Terminal Soil Analyzer Test")
    print("=" * 40)
    
    # Test 1: Excellent soil
    print("\n1. Testing Excellent Wheat Soil:")
    excellent_data = {
        "ph": 6.5,
        "salinity": 1.0,
        "texture": "loam",
        "bulk_density": 1.2,
        "nutrients": {
            "nitrogen": 150.0,
            "phosphorus": 30.0,
            "potassium": 50.0,
            "calcium": 2000.0,
            "magnesium": 250.0,
            "sulfur": 15.0,
            "iron": 8.0,
            "manganese": 5.0,
            "zinc": 1.5
        },
        "crop": "wheat"
    }
    
    result = analyzer.analyze_from_json(json.dumps(excellent_data))
    print_result(result)
    
    # Test 2: Poor soil
    print("\n2. Testing Poor Tomato Soil:")
    poor_data = {
        "ph": 4.0,
        "salinity": 6.0,
        "texture": "sandy",
        "bulk_density": 1.8,
        "nutrients": {
            "nitrogen": 30.0,
            "phosphorus": 10.0,
            "potassium": 20.0,
            "calcium": 500.0,
            "magnesium": 80.0,
            "sulfur": 5.0,
            "iron": 2.0,
            "manganese": 1.0,
            "zinc": 0.3
        },
        "crop": "tomato"
    }
    
    result = analyzer.analyze_from_json(json.dumps(poor_data))
    print_result(result)
    
    # Test 3: Using individual parameters
    print("\n3. Testing with Individual Parameters (Rice):")
    nutrients = {
        "nitrogen": 120.0,
        "phosphorus": 25.0,
        "potassium": 60.0,
        "calcium": 1500.0,
        "magnesium": 200.0,
        "sulfur": 12.0,
        "iron": 10.0,
        "manganese": 8.0,
        "zinc": 2.0
    }
    
    result = analyzer.analyze_from_params(
        ph=6.0,
        salinity=2.0,
        texture="clay",
        bulk_density=1.1,
        nutrients=nutrients,
        crop="rice"
    )
    print_result(result)
    
    # Test 4: Get supported crops and textures
    print("\n4. Supported Crops:")
    crops = analyzer.get_supported_crops()
    print(f"   {', '.join(crops['crops'])}")
    
    print("\n5. Supported Textures:")
    textures = analyzer.get_supported_textures()
    print(f"   {', '.join(textures['textures'])}")

def print_result(result):
    """Print analysis result in a formatted way"""
    if result.get("success"):
        print(f"   ✅ Category: {result['category'].upper()}")
        print(f"   📊 Score: {result['suitability_score']:.1f}/100")
        print(f"   🌾 Crop: {result['crop'].title()}")
        print(f"   💬 {result['message']}")
        
        if result['fertilizer_recommendations']:
            print(f"   🧪 Fertilizers ({len(result['fertilizer_recommendations'])}):")
            for fert in result['fertilizer_recommendations'][:3]:  # Show first 3
                print(f"      • {fert['name']}: {fert['amount']} {fert['unit']}")
            if len(result['fertilizer_recommendations']) > 3:
                print(f"      ... and {len(result['fertilizer_recommendations']) - 3} more")
        
        if result['alternative_crops']:
            print(f"   🌱 Alternatives: {', '.join(result['alternative_crops'][:5])}")
            
        if result['cultivation_tips']:
            print(f"   💡 Tips:")
            for tip in result['cultivation_tips'][:2]:  # Show first 2
                print(f"      • {tip}")
    else:
        print(f"   ❌ Error: {result.get('error')}")

def demo_json_output():
    """Demonstrate pure JSON output for integration"""
    print("\n" + "="*50)
    print("JSON OUTPUT FOR INTEGRATION")
    print("="*50)
    
    analyzer = TerminalSoilAnalyzer()
    
    # Sample input
    sample_input = {
        "ph": 6.5,
        "salinity": 1.0,
        "texture": "loam",
        "bulk_density": 1.2,
        "nutrients": {
            "nitrogen": 150.0, "phosphorus": 30.0, "potassium": 50.0,
            "calcium": 2000.0, "magnesium": 250.0, "sulfur": 15.0,
            "iron": 8.0, "manganese": 5.0, "zinc": 1.5
        },
        "crop": "wheat"
    }
    
    print("\nInput JSON:")
    print(json.dumps(sample_input, indent=2))
    
    print("\nOutput JSON:")
    result = analyzer.analyze_from_json(json.dumps(sample_input))
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_analyzer()
    demo_json_output()
