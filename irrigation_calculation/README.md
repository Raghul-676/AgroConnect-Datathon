# 🌿 Smart Irrigation Calculation System

An AI-powered irrigation calculator that uses machine learning to provide intelligent irrigation recommendations based on crop type, soil conditions, weather data, and farm characteristics.

## Features

- **Machine Learning Predictions**: Uses Random Forest and XGBoost models to predict optimal irrigation timing and water requirements
- **Real-time Weather Integration**: Fetches current weather data and forecasts to adjust recommendations
- **Smart Tips**: Provides context-aware irrigation advice based on multiple factors
- **Multiple Crop Support**: Rice, Wheat, Sugarcane, and Cotton with specific crop coefficients
- **Soil Type Optimization**: Tailored recommendations for Sandy, Loamy, and Clay soils
- **Irrigation Method Efficiency**: Accounts for Drip, Sprinkler, and Flood irrigation methods
- **Responsive Web Interface**: Clean, mobile-friendly HTML interface

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenWeatherMap API key:
```
OPENWEATHER_API_KEY=your_api_key_here
```

Get a free API key from [OpenWeatherMap](https://openweathermap.org/api).

### 3. Start the System

```bash
python start_server.py
```

The system will:
- Set up necessary directories
- Train ML models (first run takes a few minutes)
- Start the web server at http://localhost:8000

### 4. Use the Application

Open your browser and go to http://localhost:8000 to access the irrigation calculator.

## System Architecture

### Machine Learning Pipeline

1. **Data Generation**: Creates synthetic training data based on agricultural research
2. **Feature Engineering**: Extracts relevant features from farm, crop, soil, and weather data
3. **Model Training**: Trains separate models for:
   - Irrigation timing prediction
   - Water requirement calculation
   - Priority classification
4. **Prediction**: Combines ML predictions with agronomic principles

### Key Components

- **Weather Service** (`irrigation_ml/weather.py`): Fetches and processes weather data
- **ML Models** (`irrigation_ml/models.py`): Random Forest and XGBoost implementations
- **Calculator Engine** (`irrigation_ml/calculator.py`): Core irrigation calculation logic
- **Data Models** (`irrigation_ml/data_model.py`): Agricultural database and feature definitions
- **Model Manager** (`irrigation_ml/model_manager.py`): Model persistence and retraining

## API Endpoints

### Calculate Irrigation
```
POST /api/calculate-irrigation
```

Request body:
```json
{
  "farmSize": 2.5,
  "unit": "hectares",
  "crop": "rice",
  "soil": "loamy",
  "method": "drip",
  "lastIrrigation": "2024-01-15", // Date format: YYYY-MM-DD
  "location": "Tamil Nadu, India"
}
```

Response:
```json
{
  "nextIrrigationDate": "2024-01-18",
  "waterLiters": 12500,
  "tip": "Drip irrigation: Apply water slowly and frequently for best efficiency",
  "weatherInfo": {
    "temperature": 32,
    "humidity": 65,
    "rainfall_forecast_3day": 8
  }
}
```

### Get Weather Data
```
GET /api/weather/{location}
```

## Testing

Run the comprehensive test suite:

```bash
python test_irrigation_system.py
```

Or use pytest for detailed testing:

```bash
pip install pytest
pytest test_irrigation_system.py -v
```

## Model Training

The system automatically trains ML models on first startup. Models are retrained periodically based on:
- Time since last training (default: 30 days)
- Availability of new feedback data

### Manual Retraining

```python
from irrigation_ml.model_manager import model_manager

# Force retrain with more samples
model_manager.retrain_models(n_samples=20000)
```

## Agricultural Science Background

The system is based on established agricultural principles:

### Crop Coefficients (Kc)
- Based on FAO guidelines for different growth stages
- Accounts for crop water requirements throughout the season

### Soil Properties
- Field capacity and wilting point for different soil types
- Infiltration rates and water holding capacity

### Evapotranspiration
- Simplified Penman-Monteith equation for reference ET
- Crop-specific ET calculation using crop coefficients

### Irrigation Efficiency
- Application efficiency factors for different irrigation methods
- Water loss considerations

## Customization

### Adding New Crops

1. Update `CropType` enum in `data_model.py`
2. Add crop coefficients to `AgriculturalDatabase._initialize_crop_coefficients()`
3. Update the HTML form options

### Adding New Soil Types

1. Update `SoilType` enum in `data_model.py`
2. Add soil properties to `AgriculturalDatabase._initialize_soil_properties()`

### Modifying ML Models

The system uses scikit-learn and XGBoost models. You can modify model parameters in `models.py`:

```python
# Example: Increase Random Forest trees
rf_model = RandomForestRegressor(
    n_estimators=200,  # Increased from 100
    max_depth=20,      # Increased depth
    # ... other parameters
)
```

## Production Deployment

### Environment Variables

```bash
# Required
OPENWEATHER_API_KEY=your_api_key

# Optional
DEBUG=False
LOG_LEVEL=WARNING
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "start_server.py"]
```

### Performance Considerations

- Models are cached in memory after training
- Weather data can be cached to reduce API calls
- Consider using a production WSGI server like Gunicorn

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For questions or issues:
- Check the test suite for usage examples
- Review the API documentation at `/docs`
- Open an issue on GitHub

---

**Note**: This system provides recommendations based on general agricultural principles and machine learning predictions. Always consult with local agricultural experts and consider specific field conditions when making irrigation decisions.
