#!/usr/bin/env python3
"""
Simple Input Interface for Soil Analysis
Allows users to input their own soil parameters
"""

import json
import sys
from soil_analyzer import TerminalSoilAnalyzer

def get_user_input():
    """Get soil parameters from user input"""
    print("🌱 Soil Analysis - Enter Your Soil Parameters")
    print("=" * 50)
    
    try:
        # Basic soil parameters
        print("\n📊 Basic Soil Parameters:")
        ph = float(input("Enter pH value (0-14): "))
        salinity = float(input("Enter salinity (dS/m): "))
        
        print("\n🏔️ Soil Texture Options:")
        textures = ["clay", "sandy", "loam", "silt", "clay_loam", "sandy_loam", 
                   "silt_loam", "sandy_clay", "silty_clay", "sandy_clay_loam", "silty_clay_loam"]
        for i, texture in enumerate(textures, 1):
            print(f"{i}. {texture.replace('_', ' ').title()}")
        
        texture_choice = int(input(f"Choose texture (1-{len(textures)}): ")) - 1
        texture = textures[texture_choice]
        
        bulk_density = float(input("Enter bulk density (g/cm³): "))
        
        # Nutrient parameters
        print("\n🧪 Nutrient Levels:")
        print("Macro Nutrients (kg/ha):")
        nitrogen = float(input("  Nitrogen: "))
        phosphorus = float(input("  Phosphorus: "))
        potassium = float(input("  Potassium: "))
        
        print("Secondary Nutrients (mg/kg):")
        calcium = float(input("  Calcium: "))
        magnesium = float(input("  Magnesium: "))
        sulfur = float(input("  Sulfur: "))
        
        print("Micro Nutrients (mg/kg):")
        iron = float(input("  Iron: "))
        manganese = float(input("  Manganese: "))
        zinc = float(input("  Zinc: "))
        
        # Crop selection
        print("\n🌾 Crop Selection:")
        crops = ["wheat", "rice", "corn", "tomato", "potato", "soybean"]
        for i, crop in enumerate(crops, 1):
            print(f"{i}. {crop.title()}")
        
        crop_choice = int(input(f"Choose crop (1-{len(crops)}): ")) - 1
        crop = crops[crop_choice]
        
        # Create soil data dictionary
        soil_data = {
            "ph": ph,
            "salinity": salinity,
            "texture": texture,
            "bulk_density": bulk_density,
            "nutrients": {
                "nitrogen": nitrogen,
                "phosphorus": phosphorus,
                "potassium": potassium,
                "calcium": calcium,
                "magnesium": magnesium,
                "sulfur": sulfur,
                "iron": iron,
                "manganese": manganese,
                "zinc": zinc
            },
            "crop": crop
        }
        
        return soil_data
        
    except ValueError:
        print("❌ Error: Please enter valid numbers!")
        return None
    except (IndexError, KeyboardInterrupt):
        print("\n👋 Goodbye!")
        return None

def display_result(result):
    """Display analysis result in a user-friendly format"""
    print("\n" + "="*60)
    print("🌱 SOIL ANALYSIS RESULT")
    print("="*60)
    
    if not result.get("success"):
        print(f"❌ Error: {result.get('error')}")
        return
    
    # Main result
    category = result['category'].upper()
    score = result['suitability_score']
    crop = result['crop'].title()
    
    # Category with emoji
    category_emoji = {
        "EXCELLENT": "🟢",
        "AVERAGE": "🟡", 
        "BAD": "🔴"
    }
    
    print(f"{category_emoji.get(category, '⚪')} CATEGORY: {category}")
    print(f"📊 SUITABILITY SCORE: {score:.1f}/100")
    print(f"🌾 CROP: {crop}")
    print(f"\n💬 ANALYSIS:")
    print(f"   {result['message']}")
    
    # Recommendations
    if result['recommendations']:
        print(f"\n📋 GENERAL RECOMMENDATIONS:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"   {i}. {rec}")
    
    # Fertilizer recommendations
    if result['fertilizer_recommendations']:
        print(f"\n🧪 FERTILIZER RECOMMENDATIONS:")
        for i, fert in enumerate(result['fertilizer_recommendations'], 1):
            print(f"   {i}. {fert['name']}")
            print(f"      Amount: {fert['amount']} {fert['unit']}")
            print(f"      Method: {fert['application_method']}")
            print(f"      Timing: {fert['timing']}")
            print()
    
    # Alternative crops
    if result['alternative_crops']:
        print(f"🌱 ALTERNATIVE CROPS TO CONSIDER:")
        alt_crops = ", ".join([crop.title() for crop in result['alternative_crops']])
        print(f"   {alt_crops}")
    
    # Cultivation tips
    if result['cultivation_tips']:
        print(f"\n💡 CULTIVATION TIPS:")
        for i, tip in enumerate(result['cultivation_tips'], 1):
            print(f"   {i}. {tip}")

def quick_input_mode():
    """Quick input mode with simplified parameters"""
    print("🌱 Quick Soil Analysis - Simplified Input")
    print("=" * 45)
    
    try:
        # Basic parameters only
        ph = float(input("pH (6.0-7.0 is generally good): "))
        salinity = float(input("Salinity in dS/m (lower is better): "))
        
        print("\nSoil Texture:")
        print("1. Clay  2. Sandy  3. Loam  4. Silt")
        texture_map = {1: "clay", 2: "sandy", 3: "loam", 4: "silt"}
        texture_choice = int(input("Choose (1-4): "))
        texture = texture_map.get(texture_choice, "loam")
        
        bulk_density = float(input("Bulk density g/cm³ (1.0-1.5 is typical): "))
        
        print("\nCrop:")
        print("1. Wheat  2. Rice  3. Corn  4. Tomato  5. Potato  6. Soybean")
        crop_map = {1: "wheat", 2: "rice", 3: "corn", 4: "tomato", 5: "potato", 6: "soybean"}
        crop_choice = int(input("Choose (1-6): "))
        crop = crop_map.get(crop_choice, "wheat")
        
        # Use default nutrient values (moderate levels)
        soil_data = {
            "ph": ph,
            "salinity": salinity,
            "texture": texture,
            "bulk_density": bulk_density,
            "nutrients": {
                "nitrogen": 120.0,
                "phosphorus": 25.0,
                "potassium": 50.0,
                "calcium": 1500.0,
                "magnesium": 200.0,
                "sulfur": 12.0,
                "iron": 6.0,
                "manganese": 4.0,
                "zinc": 1.2
            },
            "crop": crop
        }
        
        return soil_data
        
    except (ValueError, KeyboardInterrupt):
        print("\n👋 Goodbye!")
        return None

def main():
    """Main function"""
    print("🌱 Welcome to Soil Analysis System!")
    print("Choose input mode:")
    print("1. Full Input (all parameters)")
    print("2. Quick Input (basic parameters)")
    print("3. Exit")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            soil_data = get_user_input()
        elif choice == "2":
            soil_data = quick_input_mode()
        elif choice == "3":
            print("👋 Goodbye!")
            return
        else:
            print("❌ Invalid choice!")
            return
        
        if soil_data is None:
            return
        
        # Analyze soil
        print("\n🔄 Analyzing soil... Please wait...")
        analyzer = TerminalSoilAnalyzer()
        result = analyzer.analyze_from_json(json.dumps(soil_data))
        
        # Display result
        display_result(result)
        
        # Ask if user wants to analyze again
        print("\n" + "="*60)
        again = input("Would you like to analyze another soil sample? (y/n): ").lower()
        if again == 'y':
            main()
        else:
            print("👋 Thank you for using Soil Analysis System!")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
