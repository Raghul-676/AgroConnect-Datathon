#!/usr/bin/env python3
"""
Terminal-based Soil Analysis System
Simple interface without FastAPI for easy integration with frontend/website
"""

import json
import sys
from typing import Dict, Any, Optional
from loguru import logger

# Configure logger to only show errors to keep output clean
logger.remove()
logger.add(sys.stderr, level="ERROR")

from app.models.soil import SoilParameters, NutrientLevels, SoilTexture
from app.services.analysis_engine import SoilAnalysisEngine
from app.data.crop_requirements import get_all_crops

class TerminalSoilAnalyzer:
    """Terminal-based soil analyzer"""
    
    def __init__(self):
        self.engine = SoilAnalysisEngine()
        
    def analyze_from_json(self, json_input: str) -> Dict[str, Any]:
        """
        Analyze soil from JSON input and return JSON output
        
        Input format:
        {
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
                "zinc": 1.5,
                "copper": 0.5,
                "boron": 1.0
            },
            "crop": "wheat"
        }
        """
        try:
            # Parse input
            data = json.loads(json_input)
            
            # Validate required fields
            required_fields = ["ph", "salinity", "texture", "bulk_density", "nutrients", "crop"]
            for field in required_fields:
                if field not in data:
                    return {"error": f"Missing required field: {field}"}
            
            # Validate crop
            crop = data["crop"].lower().strip()
            if crop not in get_all_crops():
                return {
                    "error": f"Unsupported crop: {crop}",
                    "supported_crops": get_all_crops()
                }
            
            # Create soil parameters
            try:
                nutrients = NutrientLevels(**data["nutrients"])
                soil_params = SoilParameters(
                    ph=data["ph"],
                    salinity=data["salinity"],
                    texture=SoilTexture(data["texture"]),
                    bulk_density=data["bulk_density"],
                    nutrients=nutrients
                )
            except Exception as e:
                return {"error": f"Invalid soil parameters: {str(e)}"}
            
            # Perform analysis
            result = self.engine.analyze_soil(soil_params, crop)
            
            # Convert to dictionary for JSON output
            return {
                "success": True,
                "crop": crop,
                "suitability_score": result.suitability_score,
                "category": result.category,
                "message": result.message,
                "recommendations": result.recommendations,
                "fertilizer_recommendations": [
                    {
                        "name": fert.name,
                        "amount": fert.amount,
                        "unit": fert.unit,
                        "application_method": fert.application_method,
                        "timing": fert.timing
                    }
                    for fert in result.fertilizer_recommendations
                ],
                "alternative_crops": result.alternative_crops,
                "cultivation_tips": result.cultivation_tips
            }
            
        except json.JSONDecodeError:
            return {"error": "Invalid JSON input"}
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def analyze_from_params(self, ph: float, salinity: float, texture: str, 
                          bulk_density: float, nutrients: Dict[str, float], 
                          crop: str) -> Dict[str, Any]:
        """Analyze soil from individual parameters"""
        
        # Create JSON input
        json_input = json.dumps({
            "ph": ph,
            "salinity": salinity,
            "texture": texture,
            "bulk_density": bulk_density,
            "nutrients": nutrients,
            "crop": crop
        })
        
        return self.analyze_from_json(json_input)
    
    def get_supported_crops(self) -> Dict[str, Any]:
        """Get list of supported crops"""
        return {
            "success": True,
            "crops": get_all_crops()
        }
    
    def get_supported_textures(self) -> Dict[str, Any]:
        """Get list of supported soil textures"""
        return {
            "success": True,
            "textures": [texture.value for texture in SoilTexture]
        }

def main():
    """Main function for command line usage"""
    analyzer = TerminalSoilAnalyzer()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python soil_analyzer.py analyze '<json_input>'")
        print("  python soil_analyzer.py crops")
        print("  python soil_analyzer.py textures")
        print("  python soil_analyzer.py interactive")
        print("\nExample JSON input:")
        example = {
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
                "zinc": 1.5,
                "copper": 0.5,
                "boron": 1.0
            },
            "crop": "wheat"
        }
        print(json.dumps(example, indent=2))
        return
    
    command = sys.argv[1].lower()
    
    if command == "analyze":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Missing JSON input for analysis"}))
            return
        
        json_input = sys.argv[2]
        result = analyzer.analyze_from_json(json_input)
        print(json.dumps(result, indent=2))
        
    elif command == "crops":
        result = analyzer.get_supported_crops()
        print(json.dumps(result, indent=2))
        
    elif command == "textures":
        result = analyzer.get_supported_textures()
        print(json.dumps(result, indent=2))
        
    elif command == "interactive":
        interactive_mode(analyzer)
        
    else:
        print(json.dumps({"error": f"Unknown command: {command}"}))

def interactive_mode(analyzer: TerminalSoilAnalyzer):
    """Interactive mode for testing"""
    print("🌱 Soil Analysis - Interactive Mode")
    print("=" * 40)
    
    # Example data for quick testing
    examples = {
        "1": {
            "name": "Excellent Wheat Soil",
            "data": {
                "ph": 6.5,
                "salinity": 1.0,
                "texture": "loam",
                "bulk_density": 1.2,
                "nutrients": {
                    "nitrogen": 150.0, "phosphorus": 30.0, "potassium": 50.0,
                    "calcium": 2000.0, "magnesium": 250.0, "sulfur": 15.0,
                    "iron": 8.0, "manganese": 5.0, "zinc": 1.5,
                    "copper": 0.5, "boron": 1.0
                },
                "crop": "wheat"
            }
        },
        "2": {
            "name": "Poor Tomato Soil",
            "data": {
                "ph": 4.0,
                "salinity": 6.0,
                "texture": "sandy",
                "bulk_density": 1.8,
                "nutrients": {
                    "nitrogen": 30.0, "phosphorus": 10.0, "potassium": 20.0,
                    "calcium": 500.0, "magnesium": 80.0, "sulfur": 5.0,
                    "iron": 2.0, "manganese": 1.0, "zinc": 0.3,
                    "copper": 0.1, "boron": 0.2
                },
                "crop": "tomato"
            }
        }
    }
    
    while True:
        print("\nOptions:")
        print("1. Test excellent wheat soil")
        print("2. Test poor tomato soil")
        print("3. Enter custom JSON")
        print("4. Show supported crops")
        print("5. Show supported textures")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice in ["1", "2"]:
            example = examples[choice]
            print(f"\n🧪 Testing: {example['name']}")
            json_input = json.dumps(example['data'])
            result = analyzer.analyze_from_json(json_input)
            
            if result.get("success"):
                print(f"✅ Category: {result['category'].upper()}")
                print(f"📊 Score: {result['suitability_score']:.1f}/100")
                print(f"💬 Message: {result['message']}")
                
                if result['fertilizer_recommendations']:
                    print("\n🧪 Fertilizer Recommendations:")
                    for fert in result['fertilizer_recommendations'][:3]:  # Show first 3
                        print(f"  • {fert['name']}: {fert['amount']} {fert['unit']}")
                
                if result['alternative_crops']:
                    print(f"\n🌾 Alternative Crops: {', '.join(result['alternative_crops'][:5])}")
                    
                if result['cultivation_tips']:
                    print("\n💡 Tips:")
                    for tip in result['cultivation_tips'][:2]:  # Show first 2
                        print(f"  • {tip}")
            else:
                print(f"❌ Error: {result.get('error')}")
                
        elif choice == "3":
            print("\nEnter JSON input (or 'back' to return):")
            json_input = input().strip()
            if json_input.lower() != 'back':
                result = analyzer.analyze_from_json(json_input)
                print(json.dumps(result, indent=2))
                
        elif choice == "4":
            result = analyzer.get_supported_crops()
            print(f"\n📋 Supported Crops: {', '.join(result['crops'])}")
            
        elif choice == "5":
            result = analyzer.get_supported_textures()
            print(f"\n🏔️ Supported Textures: {', '.join(result['textures'])}")
            
        elif choice == "6":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-6.")

if __name__ == "__main__":
    main()
