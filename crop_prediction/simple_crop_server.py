#!/usr/bin/env python3
"""
Simple Crop Yield Prediction Server
Lightweight HTTP server for crop predictions without heavy ML dependencies
"""

import http.server
import socketserver
import json
import random
from datetime import datetime

# Import database module
try:
    from database import save_prediction_to_db, get_prediction_history_from_db, get_db_statistics
    DATABASE_AVAILABLE = True
    print("✅ Database module loaded successfully")
except ImportError as e:
    print(f"⚠️ Database module not available: {e}")
    DATABASE_AVAILABLE = False

def predict_crop_yield(data):
    """Simple crop yield prediction logic"""
    try:
        # Extract parameters
        crop = data.get('crop', 'wheat')
        soil_type = data.get('soilType', 'loam')
        season = data.get('season', 'kharif')
        irrigation_type = data.get('irrigationType', 'drip')
        field_size = float(data.get('fieldSize', 1.0))
        
        print(f"🌾 Predicting yield for: {crop}, {soil_type}, {season}, {irrigation_type}, {field_size} acres")
        
        # Base yield data (tons per acre)
        base_yields = {
            'wheat': {'kharif': 2.5, 'rabi': 3.2, 'summer': 2.0},
            'rice': {'kharif': 4.5, 'rabi': 3.8, 'summer': 3.0},
            'corn': {'kharif': 5.2, 'rabi': 4.5, 'summer': 3.8},
            'tomato': {'kharif': 25.0, 'rabi': 30.0, 'summer': 20.0},
            'potato': {'kharif': 18.0, 'rabi': 22.0, 'summer': 15.0},
            'cotton': {'kharif': 1.8, 'rabi': 1.5, 'summer': 1.2},
            'sugarcane': {'kharif': 45.0, 'rabi': 40.0, 'summer': 35.0},
            'onion': {'kharif': 15.0, 'rabi': 18.0, 'summer': 12.0}
        }
        
        # Soil type multipliers
        soil_factors = {
            'clay': 0.95,     # Good for water retention
            'loam': 1.0,      # Ideal soil
            'sandy': 0.85,    # Drains too quickly
            'silt': 0.92,     # Good but can compact
            'black': 1.05,    # Very fertile
            'red': 0.88       # Needs more nutrients
        }
        
        # Irrigation type multipliers
        irrigation_factors = {
            'drip': 1.15,      # Most efficient
            'sprinkler': 1.05, # Good efficiency
            'flood': 0.9,      # Less efficient
            'furrow': 0.95,    # Moderate efficiency
            'rainfed': 0.75    # Depends on rainfall
        }
        
        # Market prices (₹ per quintal)
        market_prices = {
            'wheat': 2200,
            'rice': 2100,
            'corn': 1800,
            'tomato': 1500,
            'potato': 1200,
            'cotton': 5500,
            'sugarcane': 350,
            'onion': 2000
        }
        
        # Get base yield
        crop_yields = base_yields.get(crop.lower(), {'kharif': 3.0, 'rabi': 3.5, 'summer': 2.5})
        base_yield = crop_yields.get(season.lower(), 3.0)
        
        # Apply factors
        soil_factor = soil_factors.get(soil_type.lower(), 1.0)
        irrigation_factor = irrigation_factors.get(irrigation_type.lower(), 1.0)
        
        # Add some randomness for realistic variation (±10%)
        random_factor = random.uniform(0.9, 1.1)
        
        # Calculate expected yield per acre
        yield_per_acre = base_yield * soil_factor * irrigation_factor * random_factor
        
        # Total yield for the field
        total_yield = yield_per_acre * field_size
        
        # Market price calculation
        base_price = market_prices.get(crop.lower(), 2000)
        # Add market variation (±15%)
        market_variation = random.uniform(0.85, 1.15)
        current_price = base_price * market_variation
        
        # Revenue calculation (convert tons to quintals: 1 ton = 10 quintals)
        total_quintals = total_yield * 10
        estimated_revenue = total_quintals * current_price
        
        # Cost estimation (simplified)
        cost_per_acre = {
            'wheat': 25000,
            'rice': 30000,
            'corn': 28000,
            'tomato': 80000,
            'potato': 60000,
            'cotton': 35000,
            'sugarcane': 50000,
            'onion': 45000
        }
        
        base_cost = cost_per_acre.get(crop.lower(), 30000)
        total_cost = base_cost * field_size
        estimated_profit = estimated_revenue - total_cost
        
        # Generate recommendations
        recommendations = []
        
        if soil_factor < 1.0:
            recommendations.append(f"Consider soil improvement for {soil_type} soil - add organic matter")
        
        if irrigation_factor < 1.0:
            recommendations.append(f"Upgrade to drip irrigation for better yield (current: {irrigation_type})")
        
        if season.lower() == 'summer':
            recommendations.append("Summer season may have lower yields - ensure adequate water supply")
        
        if yield_per_acre < base_yield * 0.8:
            recommendations.append("Yield below potential - check soil health and irrigation efficiency")
        
        recommendations.append(f"Optimal planting time for {crop} in {season} season")
        recommendations.append(f"Monitor market prices - current rate: ₹{current_price:.0f}/quintal")
        
        # Risk assessment
        if estimated_profit > 0:
            risk_level = "Low" if estimated_profit > total_cost * 0.3 else "Medium"
        else:
            risk_level = "High"
        
        result = {
            "success": True,
            "crop": crop.title(),
            "field_size_acres": field_size,
            "season": season.title(),
            "soil_type": soil_type.title(),
            "irrigation_type": irrigation_type.title(),
            "predictions": {
                "expected_yield_tons": round(total_yield, 2),
                "yield_per_acre_tons": round(yield_per_acre, 2),
                "total_quintals": round(total_quintals, 1)
            },
            "market_analysis": {
                "current_price_per_quintal": round(current_price, 0),
                "estimated_revenue": round(estimated_revenue, 0),
                "estimated_cost": round(total_cost, 0),
                "estimated_profit": round(estimated_profit, 0),
                "profit_margin_percent": round((estimated_profit/estimated_revenue)*100, 1) if estimated_revenue > 0 else 0
            },
            "risk_assessment": {
                "risk_level": risk_level,
                "factors": {
                    "soil_suitability": f"{int(soil_factor*100)}%",
                    "irrigation_efficiency": f"{int(irrigation_factor*100)}%",
                    "seasonal_factor": "Good" if season.lower() != 'summer' else "Moderate"
                }
            },
            "recommendations": recommendations,
            "analysis_date": datetime.now().isoformat(),
            "confidence_score": round(random.uniform(75, 95), 1)
        }

        # Save to database if available
        if DATABASE_AVAILABLE:
            try:
                prediction_id = save_prediction_to_db(result)
                if prediction_id:
                    result['database_id'] = prediction_id
                    print(f"💾 Prediction saved to database with ID: {prediction_id}")
            except Exception as db_error:
                print(f"⚠️ Database save failed: {db_error}")

        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Prediction failed: {str(e)}"
        }

class CropPredictionHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "status": "healthy",
                "service": "Crop Yield Prediction API",
                "database_available": DATABASE_AVAILABLE
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/api/history':
            # Get prediction history
            if DATABASE_AVAILABLE:
                try:
                    history = get_prediction_history_from_db(limit=20)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {"success": True, "history": history}
                    self.wfile.write(json.dumps(response).encode())
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {"success": False, "error": str(e)}
                    self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(503)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"success": False, "error": "Database not available"}
                self.wfile.write(json.dumps(response).encode())

        elif self.path == '/api/statistics':
            # Get prediction statistics
            if DATABASE_AVAILABLE:
                try:
                    stats = get_db_statistics()
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {"success": True, "statistics": stats}
                    self.wfile.write(json.dumps(response).encode())
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = {"success": False, "error": str(e)}
                    self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(503)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {"success": False, "error": "Database not available"}
                self.wfile.write(json.dumps(response).encode())

        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/predict':
            try:
                # Read request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                print(f"🌾 Received crop prediction request: {data}")
                
                # Perform prediction
                result = predict_crop_yield(data)
                
                if result.get('success'):
                    yield_tons = result['predictions']['expected_yield_tons']
                    revenue = result['market_analysis']['estimated_revenue']
                    print(f"✅ Prediction result: {yield_tons} tons, ₹{revenue:,.0f} revenue")
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except Exception as e:
                print(f"❌ Error processing prediction request: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {"success": False, "error": str(e)}
                self.wfile.write(json.dumps(error_response).encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_server():
    """Start the crop prediction server"""
    PORT = 8002
    
    print("🌾 Starting Simple Crop Yield Prediction Server...")
    print(f"🚀 Server will run on http://localhost:{PORT}")
    print("💡 Endpoints:")
    print("   • GET  /health - Health check")
    print("   • POST /predict - Crop yield prediction")
    print("🔄 Press Ctrl+C to stop")
    
    try:
        with socketserver.TCPServer(("", PORT), CropPredictionHandler) as httpd:
            print(f"✅ Server started successfully on port {PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    start_server()
