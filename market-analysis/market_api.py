#!/usr/bin/env python3
"""
Market Analysis API with AGMARKNET Integration and ML Predictions
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from datetime import datetime, timedelta
from typing import List, Optional
import json
import statistics
import warnings
warnings.filterwarnings('ignore')

# Import database module
try:
    from database import save_analysis_to_db, get_analysis_history_from_db, get_price_trends_from_db, get_db_statistics
    DATABASE_AVAILABLE = True
    print("✅ Database module loaded successfully")
except ImportError as e:
    print(f"⚠️ Database module not available: {e}")
    DATABASE_AVAILABLE = False

app = FastAPI(title="Market Analysis API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# AGMARKNET API Configuration
AGMARKNET_API_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"
AGMARKNET_BASE_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

# Crop mappings for API calls
CROP_MAPPINGS = {
    'tomato': ['Tomato', 'tomato'],
    'onion': ['Onion', 'onion'],
    'potato': ['Potato', 'potato'],
    'brinjal': ['Brinjal', 'brinjal', 'eggplant'],
    'chillies': ['Chillies', 'chilli', 'chili'],
    'cauliflower': ['Cauliflower', 'cauliflower'],
    'cabbage': ['Cabbage', 'cabbage'],
    'carrot': ['Carrot', 'carrot'],
    'beans': ['Beans', 'beans'],
    'peas': ['Peas', 'peas']
}

# State mappings
STATE_MAPPINGS = {
    'tamil nadu': 'Tamil Nadu',
    'andhra pradesh': 'Andhra Pradesh',
    'karnataka': 'Karnataka',
    'punjab': 'Punjab',
    'maharashtra': 'Maharashtra',
    'gujarat': 'Gujarat',
    'rajasthan': 'Rajasthan',
    'uttar pradesh': 'Uttar Pradesh'
}

class MarketRequest(BaseModel):
    crop: str
    state: str
    district: Optional[str] = None

class MarketResponse(BaseModel):
    crop: str
    state: str
    district: Optional[str]
    state_avg_price: float
    district_avg_price: Optional[float]
    price_trend: str
    trend_percentage: float
    recommendation: str
    prediction_confidence: float
    market_data: List[dict]

def get_agmarknet_data(crop_name: str, state: str = None, limit: int = 50):
    """Fetch data from AGMARKNET API"""
    try:
        print(f"🔍 Fetching data for crop: {crop_name}, state: {state}")

        # Try different crop name variations
        crop_variations = CROP_MAPPINGS.get(crop_name.lower(), [crop_name])
        print(f"🔄 Trying crop variations: {crop_variations}")

        for crop_variant in crop_variations:
            params = {
                'api-key': AGMARKNET_API_KEY,
                'format': 'json',
                'limit': limit,
                'filters[commodity]': crop_variant
            }

            if state:
                state_mapped = STATE_MAPPINGS.get(state.lower(), state)
                params['filters[state]'] = state_mapped
                print(f"🗺️ Using state filter: {state_mapped}")

            print(f"🌐 Making API call with params: {params}")
            response = requests.get(AGMARKNET_BASE_URL, params=params, timeout=15)
            print(f"📡 API Response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                records = data.get('records', [])
                print(f"📊 Found {len(records)} records for {crop_variant}")
                if records:  # If we found data, return it
                    return records
            else:
                print(f"⚠️ API returned status {response.status_code} for {crop_variant}")

        print("❌ No data found for any crop variation")
        return []  # No data found for any variation

    except requests.exceptions.Timeout:
        print("⏰ API request timed out")
        return []
    except requests.exceptions.ConnectionError:
        print("🌐 Connection error to AGMARKNET API")
        return []
    except Exception as e:
        print(f"❌ Error fetching AGMARKNET data: {e}")
        return []

def calculate_price_trend(prices: List[float]) -> tuple:
    """Calculate price trend using simple statistics"""
    if len(prices) < 2:
        return "stable", 0.0, 0.5

    try:
        # Calculate percentage change from first to last price
        if len(prices) >= 2:
            percentage_change = ((prices[-1] - prices[0]) / prices[0]) * 100
        else:
            percentage_change = 0.0

        # Simple trend calculation based on recent vs older prices
        if len(prices) >= 4:
            # Compare recent half with older half
            mid_point = len(prices) // 2
            older_avg = statistics.mean(prices[:mid_point])
            recent_avg = statistics.mean(prices[mid_point:])
            trend_change = ((recent_avg - older_avg) / older_avg) * 100
        else:
            trend_change = percentage_change

        # Determine trend direction
        if abs(trend_change) < 2:
            trend = "stable"
        elif trend_change > 0:
            trend = "increasing"
        else:
            trend = "decreasing"

        # Simple confidence based on data consistency
        if len(prices) >= 5:
            # Calculate coefficient of variation as confidence measure
            mean_price = statistics.mean(prices)
            std_price = statistics.stdev(prices) if len(prices) > 1 else 0
            cv = std_price / mean_price if mean_price > 0 else 1
            confidence = max(0.3, min(0.9, 1 - cv))  # Inverse of coefficient of variation
        else:
            confidence = 0.5

        return trend, trend_change, confidence

    except Exception as e:
        print(f"Error calculating trend: {e}")
        return "stable", 0.0, 0.5

def generate_recommendation(trend: str, percentage: float, avg_price: float) -> str:
    """Generate selling recommendation based on trend analysis"""
    if trend == "increasing" and percentage > 5:
        return "Wait 3-5 days - prices are rising"
    elif trend == "decreasing" and percentage < -5:
        return "Sell immediately - prices are falling"
    elif trend == "stable":
        return "Good time to sell - stable market"
    elif trend == "increasing" and percentage <= 5:
        return "Wait 2-3 days - slight upward trend"
    else:
        return "Monitor for 1-2 days - mixed signals"

def process_market_data(records: List[dict], state: str, district: str = None) -> dict:
    """Process raw market data and calculate analytics"""
    if not records:
        return {
            'state_avg_price': 0.0,
            'district_avg_price': 0.0,
            'prices': [],
            'filtered_records': []
        }

    # Clean and convert price data
    prices = []
    state_prices = []
    district_prices = []
    filtered_records = []

    for record in records:
        try:
            # Extract modal price (most common price)
            modal_price = record.get('modal_price', '0')
            if isinstance(modal_price, str):
                modal_price = float(modal_price.replace(',', ''))
            else:
                modal_price = float(modal_price)

            if modal_price > 0:
                prices.append(modal_price)
                filtered_records.append(record)

                # Filter by state
                record_state = record.get('state', '').lower()
                if state.lower() in record_state:
                    state_prices.append(modal_price)

                    # Filter by district if specified
                    if district:
                        record_district = record.get('district', '').lower()
                        if district.lower() in record_district:
                            district_prices.append(modal_price)
        except:
            continue

    return {
        'state_avg_price': statistics.mean(state_prices) if state_prices else statistics.mean(prices) if prices else 0.0,
        'district_avg_price': statistics.mean(district_prices) if district_prices else None,
        'prices': prices,
        'filtered_records': filtered_records[:10]  # Return top 10 records
    }

def calculate_price_volatility(prices):
    """Calculate price volatility based on price variations"""
    if len(prices) < 2:
        return 0.1

    mean_price = statistics.mean(prices)
    variance = statistics.variance(prices) if len(prices) > 1 else 0
    volatility = (variance ** 0.5) / mean_price if mean_price > 0 else 0.1
    return round(min(volatility, 1.0), 3)

def get_seasonal_factor(crop):
    """Get seasonal factor for the crop"""
    seasonal_factors = {
        'tomato': 1.2,  # High demand in winter
        'onion': 0.9,   # Lower prices during harvest
        'potato': 1.1,  # Steady demand
        'rice': 1.0,    # Stable throughout year
        'wheat': 1.0,   # Stable throughout year
        'brinjal': 1.1, # Moderate seasonal variation
    }
    return seasonal_factors.get(crop.lower(), 1.0)

def estimate_demand_supply_ratio(crop, current_price):
    """Estimate demand-supply ratio based on price levels"""
    base_prices = {
        'tomato': 2500, 'onion': 2000, 'potato': 1800,
        'rice': 2200, 'wheat': 2100, 'brinjal': 3000
    }

    base_price = base_prices.get(crop.lower(), 2000)
    ratio = current_price / base_price
    return round(min(max(ratio, 0.5), 2.0), 2)

def determine_quality_grade(price, crop):
    """Determine quality grade based on price levels"""
    premium_thresholds = {
        'tomato': 3000, 'onion': 2500, 'potato': 2200,
        'rice': 2800, 'wheat': 2600, 'brinjal': 3500
    }

    threshold = premium_thresholds.get(crop.lower(), 2500)
    if price >= threshold * 1.2:
        return 'Premium'
    elif price >= threshold:
        return 'A'
    elif price >= threshold * 0.8:
        return 'B'
    else:
        return 'C'

def estimate_transportation_cost(state, district):
    """Estimate transportation cost based on location"""
    base_costs = {
        'tamil nadu': 150, 'karnataka': 180, 'andhra pradesh': 160,
        'maharashtra': 200, 'punjab': 250, 'uttar pradesh': 220,
        'bihar': 240, 'west bengal': 210
    }

    base_cost = base_costs.get(state.lower(), 200)
    # Add district factor (rural areas typically cost more)
    district_factor = 1.2 if district and len(district) > 10 else 1.0
    return round(base_cost * district_factor, 2)

def get_storage_recommendation(trend, crop):
    """Get storage recommendation based on trend and crop type"""
    storage_life = {
        'tomato': 7, 'onion': 90, 'potato': 120,
        'rice': 365, 'wheat': 365, 'brinjal': 5
    }

    days = storage_life.get(crop.lower(), 30)

    if trend == 'increasing':
        return f"Store for {min(days, 15)} days - prices rising"
    elif trend == 'decreasing':
        return f"Sell immediately - prices falling"
    else:
        return f"Can store for {min(days, 7)} days - stable market"

def get_best_selling_time(trend, percentage):
    """Determine best selling time based on trend"""
    if trend == 'increasing' and percentage > 5:
        return "Wait 2-3 days for better prices"
    elif trend == 'decreasing' and percentage < -3:
        return "Sell immediately"
    elif abs(percentage) < 2:
        return "Current time is good for selling"
    else:
        return "Monitor for 1-2 days"

def assess_market_risk(confidence, percentage):
    """Assess market risk level"""
    if confidence > 0.8 and abs(percentage) < 3:
        return 'Low'
    elif confidence > 0.6 and abs(percentage) < 8:
        return 'Medium'
    else:
        return 'High'

@app.post("/analyze", response_model=MarketResponse)
async def analyze_market(request: MarketRequest):
    """Analyze market data for given crop, state, and district"""
    try:
        print(f"🔍 Analyzing market for: {request.crop} in {request.state}")
        
        # Fetch data from AGMARKNET
        records = get_agmarknet_data(request.crop, request.state)
        
        if not records:
            print("⚠️ No data from AGMARKNET API, using fallback data")
            # Return realistic fallback data based on crop and state
            fallback_prices = {
                'tomato': {'tamil nadu': 2800, 'karnataka': 2650, 'andhra pradesh': 2750},
                'onion': {'tamil nadu': 2200, 'maharashtra': 2100, 'karnataka': 2300},
                'potato': {'punjab': 1800, 'uttar pradesh': 1750, 'bihar': 1900},
                'brinjal': {'tamil nadu': 3200, 'karnataka': 3100, 'andhra pradesh': 3300}
            }

            base_price = fallback_prices.get(request.crop.lower(), {}).get(request.state.lower(), 2500.0)
            district_price = base_price + 50  # District usually slightly higher

            return MarketResponse(
                crop=request.crop,
                state=request.state,
                district=request.district,
                state_avg_price=base_price,
                district_avg_price=district_price,
                price_trend="stable",
                trend_percentage=0.0,
                recommendation="Monitor market - using estimated prices (API data unavailable)",
                prediction_confidence=0.3,
                market_data=[{
                    'market': f'{request.state.title()} Market',
                    'district': request.district or 'Various',
                    'modal_price': str(int(base_price)),
                    'min_price': str(int(base_price * 0.9)),
                    'max_price': str(int(base_price * 1.1)),
                    'arrival_date': 'Estimated'
                }]
            )
        
        # Process the data
        processed_data = process_market_data(records, request.state, request.district)
        
        # Calculate trend
        trend, percentage, confidence = calculate_price_trend(processed_data['prices'])
        
        # Generate recommendation
        recommendation = generate_recommendation(trend, percentage, processed_data['state_avg_price'])
        
        # Format market data for response
        market_data = []
        for record in processed_data['filtered_records']:
            market_data.append({
                'market': record.get('market', 'Unknown'),
                'district': record.get('district', 'Unknown'),
                'modal_price': record.get('modal_price', '0'),
                'min_price': record.get('min_price', '0'),
                'max_price': record.get('max_price', '0'),
                'arrival_date': record.get('arrival_date', 'Unknown')
            })
        
        # Create enhanced analysis result
        analysis_result = {
            'crop': request.crop,
            'state': request.state,
            'district': request.district,
            'state_avg_price': round(processed_data['state_avg_price'], 2),
            'district_avg_price': round(processed_data['district_avg_price'], 2) if processed_data['district_avg_price'] else None,
            'price_trend': trend,
            'trend_percentage': round(percentage, 2),
            'recommendation': recommendation,
            'prediction_confidence': round(confidence, 2),
            'market_data': market_data,
            # Enhanced analysis fields
            'price_volatility': calculate_price_volatility(processed_data['prices']),
            'seasonal_factor': get_seasonal_factor(request.crop),
            'demand_supply_ratio': estimate_demand_supply_ratio(request.crop, processed_data['state_avg_price']),
            'quality_grade': determine_quality_grade(processed_data['state_avg_price'], request.crop),
            'transportation_cost': estimate_transportation_cost(request.state, request.district),
            'storage_recommendation': get_storage_recommendation(trend, request.crop),
            'best_selling_time': get_best_selling_time(trend, percentage),
            'risk_level': assess_market_risk(confidence, percentage),
            'analysis_date': datetime.now().isoformat()
        }

        # Save to database if available
        if DATABASE_AVAILABLE:
            try:
                analysis_id = save_analysis_to_db(analysis_result)
                if analysis_id:
                    analysis_result['database_id'] = analysis_id
                    print(f"💾 Market analysis saved to database with ID: {analysis_id}")
            except Exception as db_error:
                print(f"⚠️ Database save failed: {db_error}")

        return MarketResponse(
            crop=analysis_result['crop'],
            state=analysis_result['state'],
            district=analysis_result['district'],
            state_avg_price=analysis_result['state_avg_price'],
            district_avg_price=analysis_result['district_avg_price'],
            price_trend=analysis_result['price_trend'],
            trend_percentage=analysis_result['trend_percentage'],
            recommendation=analysis_result['recommendation'],
            prediction_confidence=analysis_result['prediction_confidence'],
            market_data=analysis_result['market_data']
        )
        
    except Exception as e:
        print(f"❌ Error in market analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Market Analysis API",
        "database_available": DATABASE_AVAILABLE
    }

@app.get("/api/history")
async def get_analysis_history(crop: Optional[str] = None, state: Optional[str] = None, limit: int = 20):
    """Get market analysis history"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        history = get_analysis_history_from_db(crop, state, limit)
        return {"success": True, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@app.get("/api/statistics")
async def get_market_statistics():
    """Get market analysis statistics"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        stats = get_db_statistics()
        return {"success": True, "statistics": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@app.get("/api/trends/{crop}/{state}")
async def get_price_trends(crop: str, state: str, days: int = 30):
    """Get price trends for a specific crop and state"""
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        trends = get_price_trends_from_db(crop, state, days)
        return {"success": True, "trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trends: {str(e)}")

@app.get("/crops")
async def get_supported_crops():
    """Get list of supported crops"""
    return {"crops": list(CROP_MAPPINGS.keys())}

@app.get("/states")
async def get_supported_states():
    """Get list of supported states"""
    return {"states": list(STATE_MAPPINGS.keys())}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("market_api:app", host="0.0.0.0", port=8003, reload=True)
