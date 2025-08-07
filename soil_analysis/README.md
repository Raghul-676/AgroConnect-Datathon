# Soil Analysis Backend API

A comprehensive backend system for soil analysis and crop suitability assessment using machine learning.

## Features

- **Soil Parameter Analysis**: Analyzes pH, salinity, texture, bulk density, and nutrient levels
- **Crop Suitability Assessment**: Evaluates soil suitability for specific crops
- **Machine Learning Classification**: Uses Random Forest classifier for intelligent recommendations
- **Three-Category Analysis**:
  - **Excellent**: Ideal soil conditions with cultivation tips
  - **Average**: Suitable with fertilizer recommendations
  - **Bad**: Poor conditions with alternative crop suggestions
- **Fertilizer Recommendations**: Specific fertilizer types and amounts
- **Alternative Crop Suggestions**: For unsuitable soil conditions

## Supported Crops

- Wheat
- Rice
- Corn
- Tomato
- Potato
- Soybean

## API Endpoints

### Core Analysis
- `POST /api/v1/analyze` - Analyze soil for crop suitability
- `GET /api/v1/crops` - Get supported crops
- `GET /api/v1/soil-textures` - Get supported soil textures
- `GET /api/v1/crop-requirements/{crop_name}` - Get crop requirements

### Model Management
- `POST /api/v1/train-model` - Train/retrain ML model
- `GET /api/v1/model-info` - Get model information

### Health Checks
- `GET /health` - API health check
- `GET /api/v1/health` - Service health check

## Quick Start

### 1. Start the Backend Server

**Windows:**
```bash
cd soil_analysis
start_server.bat
```

**Linux/Mac:**
```bash
cd soil_analysis
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The server will start on `http://localhost:8000`

### 2. Open the Frontend

Open `index.html` in your web browser or serve it through a web server.

### 3. Use the Application

1. Fill in the soil parameters form
2. Select a crop type
3. Click "Generate Analysis"
4. View the detailed analysis results
5. Download the professional PDF report

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## Usage Example

```python
import requests

# Soil analysis request
soil_data = {
    "soil_parameters": {
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
        }
    },
    "crop_name": "wheat"
}

response = requests.post("http://localhost:8000/api/v1/analyze", json=soil_data)
result = response.json()

print(f"Category: {result['category']}")
print(f"Score: {result['suitability_score']}")
print(f"Message: {result['message']}")
```

## Testing

Run tests with:
```bash
pytest
```

## Project Structure

```
soil_analysis/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── soil_analysis.py
│   ├── core/
│   │   └── config.py
│   ├── data/
│   │   ├── crop_requirements.py
│   │   └── fertilizer_recommendations.py
│   ├── ml/
│   │   └── soil_classifier.py
│   ├── models/
│   │   └── soil.py
│   └── services/
│       └── analysis_engine.py
├── tests/
├── models/  # ML model storage
├── main.py
└── requirements.txt
```

## Configuration

Environment variables can be set in `.env` file:
- `DEBUG`: Enable debug mode
- `HOST`: API host (default: 0.0.0.0)
- `PORT`: API port (default: 8000)
- `LOG_LEVEL`: Logging level
- `MODEL_PATH`: ML model storage path

## Machine Learning Model

The system uses a Random Forest classifier trained on synthetic data based on crop requirements. The model considers:
- Soil pH and salinity
- Soil texture and bulk density
- Macro, secondary, and micronutrient levels
- Crop-specific requirements

## Troubleshooting

**405 Method Not Allowed Error:**
- Make sure the backend server is running on port 8000
- Check that you're using the correct API endpoint (`/api/v1/analyze`)
- Ensure the request is being sent as JSON with proper headers

**Connection Error:**
- Ensure the backend server is started before using the frontend
- Check that no firewall is blocking port 8000
- Verify the server is accessible at `http://localhost:8000`

**Analysis Fails:**
- Check that all required form fields are filled
- Ensure numeric values are within valid ranges
- Verify the crop name is supported (check `/api/v1/crops` endpoint)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Run tests to ensure they pass
5. Submit a pull request

## License

This project is licensed under the MIT License.
