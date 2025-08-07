# 🌱 Terminal Soil Analyzer - Integration Guide

This is a **terminal-based** soil analysis system without FastAPI, designed for easy integration with frontend applications and websites.

## 🚀 Quick Start

### 1. Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements_terminal.txt
```

### 2. Usage Options

#### **Option A: Interactive Mode (for testing)**
```bash
python soil_analyzer.py interactive
```

#### **Option B: Command Line JSON**
```bash
# Analyze soil
python soil_analyzer.py analyze '{"ph": 6.5, "salinity": 1.0, "texture": "loam", "bulk_density": 1.2, "nutrients": {"nitrogen": 150.0, "phosphorus": 30.0, "potassium": 50.0, "calcium": 2000.0, "magnesium": 250.0, "sulfur": 15.0, "iron": 8.0, "manganese": 5.0, "zinc": 1.5, "copper": 0.5, "boron": 1.0}, "crop": "wheat"}'

# Get supported crops
python soil_analyzer.py crops

# Get supported textures
python soil_analyzer.py textures
```

#### **Option C: Python Integration**
```python
from soil_analyzer import TerminalSoilAnalyzer
import json

analyzer = TerminalSoilAnalyzer()

# Analyze soil
result = analyzer.analyze_from_json(json_input)
print(json.dumps(result, indent=2))
```

## 📊 Input/Output Format

### **Input JSON Format**
```json
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
```

### **Output JSON Format**
```json
{
  "success": true,
  "crop": "wheat",
  "suitability_score": 98.9,
  "category": "excellent",
  "message": "Excellent! Your soil conditions are ideal for wheat cultivation...",
  "recommendations": [
    "Continue current soil management practices",
    "Regular soil testing every 6 months"
  ],
  "fertilizer_recommendations": [
    {
      "name": "Urea (46-0-0)",
      "amount": 217.0,
      "unit": "kg/ha",
      "application_method": "Broadcast and incorporate into soil",
      "timing": "Split application: 50% at planting, 50% at tillering"
    }
  ],
  "alternative_crops": ["barley", "sugar_beet"],
  "cultivation_tips": [
    "Your soil is excellent for wheat cultivation!",
    "Maintain current soil conditions through regular monitoring"
  ]
}
```

## 🔧 Integration Methods

### **Method 1: Subprocess (Recommended)**
```python
import subprocess
import json

def analyze_soil(soil_data):
    """Analyze soil using subprocess"""
    json_input = json.dumps(soil_data)
    
    result = subprocess.run([
        'python', 'soil_analyzer.py', 'analyze', json_input
    ], capture_output=True, text=True, cwd='path/to/soil_analysis')
    
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        return {"error": "Analysis failed"}

# Usage
soil_data = {
    "ph": 6.5,
    "salinity": 1.0,
    "texture": "loam",
    "bulk_density": 1.2,
    "nutrients": {...},
    "crop": "wheat"
}

result = analyze_soil(soil_data)
print(result['category'])  # excellent/average/bad
```

### **Method 2: Direct Import**
```python
import sys
sys.path.append('path/to/soil_analysis')

from soil_analyzer import TerminalSoilAnalyzer
import json

analyzer = TerminalSoilAnalyzer()

def analyze_soil(soil_data):
    """Analyze soil directly"""
    json_input = json.dumps(soil_data)
    return analyzer.analyze_from_json(json_input)

# Usage
result = analyze_soil(soil_data)
```

### **Method 3: Web Integration (Flask/Django)**
```python
# Flask example
from flask import Flask, request, jsonify
from soil_analyzer import TerminalSoilAnalyzer
import json

app = Flask(__name__)
analyzer = TerminalSoilAnalyzer()

@app.route('/analyze', methods=['POST'])
def analyze_soil():
    try:
        soil_data = request.json
        json_input = json.dumps(soil_data)
        result = analyzer.analyze_from_json(json_input)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
```

## 📋 Supported Values

### **Crops**
- wheat, rice, corn, tomato, potato, soybean

### **Soil Textures**
- clay, sandy, loam, silt, clay_loam, sandy_loam, silt_loam, sandy_clay, silty_clay, sandy_clay_loam, silty_clay_loam

### **Parameter Ranges**
- **pH**: 0-14 (optimal varies by crop)
- **Salinity**: 0+ dS/m (tolerance varies by crop)
- **Bulk Density**: 0.5-2.5 g/cm³
- **Nutrients**: All values ≥ 0
  - Macro (kg/ha): nitrogen, phosphorus, potassium
  - Secondary (mg/kg): calcium, magnesium, sulfur
  - Micro (mg/kg): iron, manganese, zinc, copper, boron

## 🎯 Analysis Categories

### **Excellent (Score: 80-100)**
- Ideal soil conditions
- Provides cultivation tips
- No fertilizer recommendations needed

### **Average (Score: 60-79)**
- Suitable with improvements
- Specific fertilizer recommendations with amounts
- Actionable improvement suggestions

### **Bad (Score: 0-59)**
- Poor soil conditions
- Comprehensive fertilizer recommendations
- Alternative crop suggestions
- Major improvement required

## 🧪 Testing

```bash
# Run comprehensive tests
python test_terminal.py

# Interactive testing
python soil_analyzer.py interactive
```

## 📁 File Structure

```
soil_analysis/
├── soil_analyzer.py           # Main terminal interface
├── test_terminal.py           # Test script
├── requirements_terminal.txt  # Minimal dependencies
├── app/                       # Core analysis engine
│   ├── models/               # Data models
│   ├── services/             # Analysis logic
│   ├── data/                 # Crop requirements & fertilizers
│   └── ml/                   # Machine learning models
└── models/                   # Trained ML models (auto-generated)
```

## 🔄 Error Handling

The system returns structured error responses:

```json
{
  "error": "Missing required field: ph",
  "supported_crops": ["wheat", "rice", "corn", "tomato", "potato", "soybean"]
}
```

Common errors:
- Invalid JSON input
- Missing required fields
- Unsupported crop names
- Invalid parameter values
- Analysis failures

## 💡 Integration Tips

1. **Always validate input** before sending to analyzer
2. **Handle errors gracefully** - check for "success" field
3. **Cache results** for identical inputs to improve performance
4. **Use subprocess method** for web applications to avoid import conflicts
5. **Set timeouts** for subprocess calls to prevent hanging
6. **Log analysis requests** for debugging and monitoring

This terminal-based system is perfect for integration with any frontend framework, web application, or automated system! 🚀
