from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
from nlp_pipeline import translate_to_english
import pandas as pd
import joblib
import uvicorn
from typing import Optional

app = FastAPI(title="Crop Yield Prediction API", version="1.0.0")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"🌐 {request.method} {request.url.path} - Headers: {dict(request.headers)}")
    response = await call_next(request)
    print(f"📤 Response status: {response.status_code}")
    return response

# Serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="."), name="static")

# Load model and encoders
try:
    model = joblib.load('multi_output_crop_model.pkl')
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

AGMARKNET_API_KEY = '579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b'

class PredictionRequest(BaseModel):
    crop: str
    soil_type: str
    season: str
    irrigation_type: str
    field_size: float
    investment: Optional[float] = 0.0

class PredictionResponse(BaseModel):
    expected_yield: float
    market_price: float
    estimated_revenue: float
    profit: float
    performance_rating: str

def get_market_price(crop_name):
    """Get market price for a crop (fallback to default if API fails)"""
    try:
        response = requests.get(
            f"https://api.agrimarket.api/price?apikey={AGMARKNET_API_KEY}&commodity={crop_name}",
            timeout=5
        )
        data = response.json()
        return float(data['price'])
    except:
        return 2000.0  # fallback price

def calculate_performance_rating(yield_value, revenue, investment):
    """Calculate performance rating based on yield and profit"""
    profit = revenue - investment
    profit_margin = (profit / investment * 100) if investment > 0 else 0

    if profit_margin > 100 and yield_value > 100:
        return "Excellent"
    elif profit_margin > 50 and yield_value > 50:
        return "Good"
    elif profit_margin > 20 and yield_value > 30:
        return "Average"
    else:
        return "Poor"

@app.get("/")
async def serve_frontend():
    """Serve the main HTML page"""
    return FileResponse("crop_page.html")

@app.post("/predict", response_model=PredictionResponse)
async def predict_yield(request: PredictionRequest):
    """Predict crop yield based on input parameters"""
    try:
        print(f"🔍 Received request: {request}")

        if model is None:
            raise HTTPException(status_code=500, detail="Model not loaded")

        # Translate inputs to English and preprocess
        crop = translate_to_english(request.crop).lower().strip()
        soil = translate_to_english(request.soil_type).lower().strip()
        season = translate_to_english(request.season).lower().strip()
        irrigation = translate_to_english(request.irrigation_type).lower().strip()

        print(f"🔄 Translated inputs: crop={crop}, soil={soil}, season={season}, irrigation={irrigation}")

        # Prepare DataFrame for prediction
        input_df = pd.DataFrame([{
            'Crop': crop,
            'SoilType': soil,
            'Season': season,
            'IrrigationType': irrigation,
            'FieldSize': request.field_size
        }])

        print(f"📊 Input DataFrame: {input_df.to_dict()}")

        # Predict
        prediction = model.predict(input_df)[0]
        expected_yield, market_price, estimated_revenue = prediction

        print(f"🎯 Raw prediction: yield={expected_yield}, price={market_price}, revenue={estimated_revenue}")

        # Calculate profit and performance rating
        profit = estimated_revenue - request.investment
        performance_rating = calculate_performance_rating(
            expected_yield, estimated_revenue, request.investment
        )

        result = PredictionResponse(
            expected_yield=round(expected_yield, 2),
            market_price=round(market_price, 2),
            estimated_revenue=round(estimated_revenue, 2),
            profit=round(profit, 2),
            performance_rating=performance_rating
        )

        print(f"✅ Final result: {result}")
        return result

    except Exception as e:
        print(f"❌ Error in prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": model is not None}

@app.get("/predict")
async def predict_get():
    """GET endpoint for debugging - should return method not allowed"""
    return {"error": "Use POST method for predictions"}

@app.options("/predict")
async def predict_options():
    """OPTIONS endpoint for CORS preflight"""
    return {"methods": ["POST"]}

if __name__ == '__main__':
    uvicorn.run("app:app", host="0.0.0.0", port=8002, reload=True)
