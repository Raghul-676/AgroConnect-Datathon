from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from irrigation_ml.models import IrrigationPredictor
from irrigation_ml.weather import WeatherService
from irrigation_ml.calculator import IrrigationCalculator

app = FastAPI(title="Irrigation Calculator API", version="1.0.0")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Note: Removed static file mounting to avoid API route conflicts

# Initialize services lazily
weather_service = None
irrigation_predictor = None
irrigation_calculator = None

def get_services():
    global weather_service, irrigation_predictor, irrigation_calculator
    if weather_service is None:
        weather_service = WeatherService()
        irrigation_predictor = IrrigationPredictor()
        # Ensure models are trained
        if not irrigation_predictor.is_trained:
            irrigation_predictor.train_models(n_samples=5000)
        irrigation_calculator = IrrigationCalculator(irrigation_predictor, weather_service)
    return weather_service, irrigation_predictor, irrigation_calculator

class IrrigationRequest(BaseModel):
    farmSize: float
    unit: str
    crop: str
    soil: str
    method: str
    bulkDensity: float
    lastIrrigation: str
    location: Optional[str] = "Tamil Nadu, India"

class IrrigationResponse(BaseModel):
    nextIrrigationDate: str
    waterLiters: float
    tip: str
    weatherInfo: dict

@app.get("/")
async def serve_html():
    """Serve the main HTML file"""
    return FileResponse("irrigation.html")

@app.get("/api/test")
async def test_api():
    """Test endpoint to verify API is working"""
    return {"status": "API is working", "message": "All endpoints should be available"}

@app.post("/api/calculate-irrigation", response_model=IrrigationResponse)
async def calculate_irrigation(request: IrrigationRequest):
    """Calculate irrigation requirements based on input parameters and weather data"""
    print(f"🌱 Received irrigation request: {request}")
    try:
        # Get services
        weather_service, irrigation_predictor, irrigation_calculator = get_services()

        # Get current weather data
        weather_data = await weather_service.get_weather_data(request.location)

        # Calculate irrigation requirements
        print(f"🌦️ Weather data for calculation: {weather_data}")
        result = irrigation_calculator.calculate_irrigation(
            farm_size=request.farmSize,
            unit=request.unit,
            crop=request.crop,
            soil=request.soil,
            method=request.method,
            bulk_density=request.bulkDensity,
            last_irrigation=request.lastIrrigation,
            weather_data=weather_data
        )
        print(f"🌱 Calculation result: {result}")

        return IrrigationResponse(
            nextIrrigationDate=result["next_irrigation_date"],
            waterLiters=result["water_liters"],
            tip=result["tip"],
            weatherInfo=weather_data
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

@app.get("/api/weather/{location}")
async def get_weather(location: str):
    """Get current weather data for a location"""
    print(f"🌦️ Received weather request for: {location}")
    try:
        # Get services
        weather_service, _, _ = get_services()
        weather_data = await weather_service.get_weather_data(location)
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather data error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
