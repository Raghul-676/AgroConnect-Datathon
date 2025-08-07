#!/usr/bin/env python3
"""
Simple Irrigation Calculator Server
Lightweight HTTP server for irrigation calculations without heavy ML dependencies
"""

import http.server
import socketserver
import json
import urllib.parse
from datetime import datetime, timedelta
import random

# Import database module
try:
    from database import save_calculation_to_db, get_calculation_history_from_db, get_db_statistics
    DATABASE_AVAILABLE = True
    print("✅ Database module loaded successfully")
except ImportError as e:
    print(f"⚠️ Database module not available: {e}")
    DATABASE_AVAILABLE = False

def calculate_irrigation_simple(data):
    """Simple irrigation calculation logic"""
    try:
        # Extract parameters
        crop = data.get('crop', 'wheat')
        soil_type = data.get('soilType', 'loam')
        field_size = float(data.get('fieldSize', 1.0))
        irrigation_type = data.get('irrigationType', 'drip')
        last_irrigation = data.get('lastIrrigation', '2025-01-01')
        location = data.get('location', 'Tamil Nadu')
        
        # Base water requirements (liters per square meter per day)
        crop_water_needs = {
            'wheat': 4.5,
            'rice': 8.0,
            'corn': 5.5,
            'tomato': 6.0,
            'potato': 4.0,
            'cotton': 5.0,
            'sugarcane': 7.5,
            'onion': 3.5
        }
        
        # Soil type multipliers
        soil_multipliers = {
            'clay': 0.8,    # Retains water better
            'loam': 1.0,    # Balanced
            'sandy': 1.3,   # Drains quickly
            'silt': 0.9     # Good retention
        }
        
        # Irrigation efficiency
        irrigation_efficiency = {
            'drip': 0.9,      # 90% efficient
            'sprinkler': 0.75, # 75% efficient
            'flood': 0.6,     # 60% efficient
            'furrow': 0.65    # 65% efficient
        }
        
        # Calculate base water need
        base_water_need = crop_water_needs.get(crop.lower(), 5.0)
        soil_factor = soil_multipliers.get(soil_type.lower(), 1.0)
        efficiency = irrigation_efficiency.get(irrigation_type.lower(), 0.75)
        
        # Calculate days since last irrigation
        try:
            last_date = datetime.strptime(last_irrigation, '%Y-%m-%d')
            days_since = (datetime.now() - last_date).days
        except:
            days_since = 3  # Default
        
        # Adjust for days since last irrigation
        urgency_factor = min(2.0, 1.0 + (days_since / 7.0))
        
        # Calculate water requirement
        daily_water_need = base_water_need * soil_factor * urgency_factor
        total_water_needed = daily_water_need / efficiency  # Account for efficiency loss
        
        # Scale by field size (assuming field size is in acres, convert to square meters)
        field_size_sqm = field_size * 4047  # 1 acre = 4047 sqm
        total_water_liters = total_water_needed * field_size_sqm
        
        # Determine irrigation frequency
        if days_since >= 7:
            priority = "high"
            next_irrigation = "Today"
            frequency = "Every 3-4 days"
        elif days_since >= 4:
            priority = "medium"
            next_irrigation = "Within 2 days"
            frequency = "Every 4-5 days"
        else:
            priority = "low"
            next_irrigation = "Within 3-4 days"
            frequency = "Every 5-7 days"
        
        # Generate recommendations
        recommendations = []
        
        if irrigation_type.lower() == 'flood':
            recommendations.append("Consider switching to drip irrigation for better water efficiency")
        
        if soil_type.lower() == 'sandy':
            recommendations.append("Sandy soil drains quickly - consider more frequent, lighter irrigation")
        elif soil_type.lower() == 'clay':
            recommendations.append("Clay soil retains water well - avoid overwatering")
        
        if days_since > 7:
            recommendations.append("Immediate irrigation needed - crop may be stressed")
        
        recommendations.append(f"Apply {total_water_liters/field_size_sqm:.1f} liters per square meter")
        recommendations.append(f"Best time: Early morning (6-8 AM) or evening (6-8 PM)")
        
        # Get weather data for the location
        weather_data = get_weather_data(location)

        result = {
            "success": True,
            "crop": crop,
            "field_size_acres": field_size,
            "soil_type": soil_type,
            "irrigation_type": irrigation_type,
            "last_irrigation_date": last_irrigation,
            "location": location,
            "nextIrrigationDate": next_irrigation,
            "waterLiters": round(total_water_liters, 1),
            "water_requirement": {
                "total_liters": round(total_water_liters, 1),
                "liters_per_sqm": round(total_water_liters/field_size_sqm, 2),
                "daily_need": round(daily_water_need, 2)
            },
            "irrigation_schedule": {
                "priority": priority,
                "next_irrigation": next_irrigation,
                "frequency": frequency,
                "days_since_last": days_since
            },
            "recommendations": recommendations,
            "efficiency": {
                "method": irrigation_type,
                "efficiency_percent": int(efficiency * 100),
                "water_saved_vs_flood": f"{int((efficiency - 0.6) * 100)}%" if efficiency > 0.6 else "0%"
            },
            "weatherInfo": {
                "temperature": weather_data["temperature"],
                "rainfall_forecast_3day": weather_data["rainfall_forecast_3day"],
                "humidity": weather_data["humidity"],
                "weather_condition": weather_data["weather_condition"]
            },
            "analysis_date": datetime.now().isoformat()
        }

        # Save to database if available
        if DATABASE_AVAILABLE:
            try:
                calculation_id = save_calculation_to_db(result)
                if calculation_id:
                    result['database_id'] = calculation_id
                    print(f"💾 Calculation saved to database with ID: {calculation_id}")
            except Exception as db_error:
                print(f"⚠️ Database save failed: {db_error}")

        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Calculation failed: {str(e)}"
        }

def get_weather_data(location):
    """Simple weather data simulation"""
    # Simulate weather data for different locations
    weather_patterns = {
        'tamil nadu': {'temp': 28, 'humidity': 75, 'rainfall': 2.5},
        'punjab': {'temp': 25, 'humidity': 65, 'rainfall': 1.2},
        'maharashtra': {'temp': 30, 'humidity': 70, 'rainfall': 1.8},
        'karnataka': {'temp': 27, 'humidity': 72, 'rainfall': 2.1}
    }

    base_weather = weather_patterns.get(location.lower(), {'temp': 28, 'humidity': 70, 'rainfall': 2.0})

    # Add some random variation
    temp = base_weather['temp'] + random.randint(-3, 3)
    rainfall = base_weather['rainfall'] + random.uniform(-0.5, 1.0)

    return {
        "location": location.title(),
        "temperature": temp,
        "humidity": base_weather['humidity'] + random.randint(-5, 5),
        "rainfall_last_7_days": rainfall,
        "rainfall_forecast_3day": rainfall * 0.6,  # Add the expected property
        "weather_condition": random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Light Rain"]),
        "wind_speed": random.randint(5, 15),
        "forecast": "Moderate weather conditions expected for next 3 days",
        "last_updated": datetime.now().isoformat()
    }

class IrrigationHandler(http.server.BaseHTTPRequestHandler):
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
                "service": "Irrigation Calculator API",
                "database_available": DATABASE_AVAILABLE
            }
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path.startswith('/api/weather/'):
            # Extract location from path
            location = urllib.parse.unquote(self.path.split('/api/weather/')[-1])
            print(f"🌤️ Weather request for: {location}")
            
            weather_data = get_weather_data(location)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(weather_data).encode())

        elif self.path == '/api/history':
            # Get calculation history
            if DATABASE_AVAILABLE:
                try:
                    history = get_calculation_history_from_db(limit=20)
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
            # Get calculation statistics
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
        if self.path == '/api/calculate-irrigation':
            try:
                # Read request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                print(f"💧 Received irrigation calculation request: {data}")
                
                # Perform calculation
                result = calculate_irrigation_simple(data)
                
                print(f"✅ Calculation result: {result.get('water_requirement', {}).get('total_liters', 0)} liters needed")
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except Exception as e:
                print(f"❌ Error processing irrigation request: {e}")
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
    """Start the irrigation calculator server"""
    PORT = 8001
    
    print("💧 Starting Simple Irrigation Calculator Server...")
    print(f"🚀 Server will run on http://localhost:{PORT}")
    print("💡 Endpoints:")
    print("   • GET  /health - Health check")
    print("   • GET  /api/weather/{location} - Weather data")
    print("   • POST /api/calculate-irrigation - Irrigation calculation")
    print("🔄 Press Ctrl+C to stop")
    
    try:
        with socketserver.TCPServer(("", PORT), IrrigationHandler) as httpd:
            print(f"✅ Server started successfully on port {PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    start_server()
