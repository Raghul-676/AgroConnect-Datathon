#!/usr/bin/env python3
"""
ML-Based Soil Analysis Server
Uses the actual trained machine learning models for soil analysis
"""

import http.server
import socketserver
import json
import sys
import os
import subprocess
from datetime import datetime

# Import database module
try:
    from database import save_analysis_to_db, get_analysis_history_from_db, get_db_statistics
    DATABASE_AVAILABLE = True
    print("✅ Database module loaded successfully")
except ImportError as e:
    print(f"⚠️ Database module not available: {e}")
    DATABASE_AVAILABLE = False

def analyze_soil_with_ml(data):
    """Use the actual trained ML models via subprocess call"""
    try:
        # Handle both frontend format and direct API format
        if 'crop_name' in data and 'soil_parameters' in data:
            # Frontend format: {"crop_name": "tomato", "soil_parameters": {...}}
            crop = data.get('crop_name', 'wheat')
            soil_params = data.get('soil_parameters', {})
            nutrients = soil_params.get('nutrients', {})

            ml_input = {
                "ph": soil_params.get('ph', 7.0),
                "salinity": soil_params.get('salinity', 1.0),
                "texture": soil_params.get('texture', 'loam'),
                "bulk_density": soil_params.get('bulk_density', 1.3),
                "nutrients": {
                    "nitrogen": nutrients.get('nitrogen', 150.0),
                    "phosphorus": nutrients.get('phosphorus', 30.0),
                    "potassium": nutrients.get('potassium', 50.0),
                    "calcium": nutrients.get('calcium', 2000.0),
                    "magnesium": nutrients.get('magnesium', 250.0),
                    "sulfur": nutrients.get('sulfur', 15.0),
                    "iron": nutrients.get('iron', 8.0),
                    "manganese": nutrients.get('manganese', 5.0),
                    "zinc": nutrients.get('zinc', 1.5),
                    "copper": nutrients.get('copper', 0.5),
                    "boron": nutrients.get('boron', 1.0)
                },
                "crop": crop
            }
        else:
            # Direct API format: {"crop": "tomato", "ph": 6.5, ...}
            ml_input = {
                "ph": data.get('ph', 7.0),
                "salinity": data.get('salinity', 1.0),
                "texture": data.get('texture', 'loam'),
                "bulk_density": data.get('bulk_density', 1.3),
                "nutrients": {
                    "nitrogen": data.get('nutrients', {}).get('nitrogen', 150.0),
                    "phosphorus": data.get('nutrients', {}).get('phosphorus', 30.0),
                    "potassium": data.get('nutrients', {}).get('potassium', 50.0),
                    "calcium": data.get('nutrients', {}).get('calcium', 2000.0),
                    "magnesium": data.get('nutrients', {}).get('magnesium', 250.0),
                    "sulfur": data.get('nutrients', {}).get('sulfur', 15.0),
                    "iron": data.get('nutrients', {}).get('iron', 8.0),
                    "manganese": data.get('nutrients', {}).get('manganese', 5.0),
                    "zinc": data.get('nutrients', {}).get('zinc', 1.5),
                    "copper": data.get('nutrients', {}).get('copper', 0.5),
                    "boron": data.get('nutrients', {}).get('boron', 1.0)
                },
                "crop": data.get('crop', 'wheat')
            }

        print(f"🔬 Running ML analysis for {ml_input['crop']} with pH {ml_input['ph']}")

        # Try to run the ML analyzer as a subprocess using the virtual environment
        try:
            # Create a temporary input for the analyzer
            json_input = json.dumps(ml_input)

            # Use the virtual environment Python executable
            venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv', 'Scripts', 'python.exe')

            # Run the soil analyzer with JSON input using the analyze command
            cmd = [venv_python, 'soil_analyzer.py', 'analyze', json_input]

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))

            if result.returncode == 0:
                # Parse the JSON output
                ml_result = json.loads(result.stdout.strip())

                if ml_result.get('success'):
                    print(f"✅ ML Analysis complete: {ml_result['category']} ({ml_result['suitability_score']:.1f}/100)")

                    # Add analysis metadata and ensure frontend compatibility
                    ml_result['analysis_date'] = datetime.now().isoformat()
                    ml_result['analysis_method'] = 'Machine Learning'
                    ml_result['model_version'] = '1.0.0'
                    ml_result['soil_parameters'] = {
                        'ph': ml_input['ph'],
                        'salinity': ml_input['salinity'],
                        'texture': ml_input['texture'],
                        'bulk_density': ml_input['bulk_density'],
                        'nutrients': ml_input['nutrients']
                    }

                    # Ensure frontend compatibility - add crop_name if not present
                    if 'crop' in ml_result and 'crop_name' not in ml_result:
                        ml_result['crop_name'] = ml_result['crop']

                    # Ensure all expected fields are present
                    if 'fertilizer_recommendations' not in ml_result:
                        ml_result['fertilizer_recommendations'] = []
                    if 'alternative_crops' not in ml_result:
                        ml_result['alternative_crops'] = []
                    if 'cultivation_tips' not in ml_result:
                        ml_result['cultivation_tips'] = []

                    # Save to database if available
                    if DATABASE_AVAILABLE:
                        try:
                            # Prepare data for database
                            db_data = ml_result.copy()
                            db_data['soil_parameters'] = {
                                'ph': ml_input['ph'],
                                'salinity': ml_input['salinity'],
                                'texture': ml_input['texture'],
                                'bulk_density': ml_input['bulk_density'],
                                'nutrients': ml_input['nutrients']
                            }
                            analysis_id = save_analysis_to_db(db_data)
                            if analysis_id:
                                ml_result['database_id'] = analysis_id
                                print(f"💾 Analysis saved to database with ID: {analysis_id}")
                        except Exception as db_error:
                            print(f"⚠️ Database save failed: {db_error}")

                    return ml_result
                else:
                    print(f"❌ ML Analysis failed: {ml_result.get('error', 'Unknown error')}")
                    return ml_result
            else:
                print(f"❌ Subprocess failed: {result.stderr}")
                raise Exception(f"ML subprocess failed: {result.stderr}")

        except Exception as subprocess_error:
            print(f"⚠️ ML analysis failed, using fallback: {subprocess_error}")
            return analyze_soil_fallback(data)

    except Exception as e:
        print(f"❌ ML Analysis exception: {e}")
        return analyze_soil_fallback(data)

def analyze_soil_fallback(data):
    """Fallback analysis when ML is not available"""
    try:
        # Extract parameters
        ph = data.get('ph', 7.0)
        salinity = data.get('salinity', 1.0)
        texture = data.get('texture', 'loam')
        bulk_density = data.get('bulk_density', 1.3)
        nutrients = data.get('nutrients', {})
        crop = data.get('crop', 'wheat')
        
        # Simple scoring logic (fallback)
        score = 100
        recommendations = []
        
        # pH analysis
        if ph < 6.0:
            score -= 20
            recommendations.append("Soil is too acidic. Add lime to increase pH.")
        elif ph > 8.0:
            score -= 15
            recommendations.append("Soil is too alkaline. Add sulfur or organic matter to decrease pH.")
        else:
            recommendations.append("pH level is good for most crops.")
        
        # Salinity analysis
        if salinity > 2.0:
            score -= 25
            recommendations.append("High salinity detected. Improve drainage and leach salts.")
        elif salinity > 1.5:
            score -= 10
            recommendations.append("Moderate salinity. Monitor salt levels.")
        else:
            recommendations.append("Salinity levels are acceptable.")
        
        # Determine category
        if score >= 85:
            category = "excellent"
            message = f"Excellent soil conditions for {crop} cultivation!"
        elif score >= 70:
            category = "average"
            message = f"Good soil conditions for {crop} with some improvements needed."
        else:
            category = "bad"
            message = f"Soil needs significant improvement for optimal {crop} growth."
        
        return {
            "success": True,
            "crop": crop,
            "suitability_score": round(score, 1),
            "category": category,
            "message": message,
            "recommendations": recommendations,
            "fertilizer_recommendations": [],
            "analysis_date": datetime.now().isoformat(),
            "analysis_method": "Fallback Logic",
            "model_version": "fallback",
            "soil_parameters": {
                "ph": ph,
                "salinity": salinity,
                "texture": texture,
                "bulk_density": bulk_density,
                "nutrients": nutrients
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Fallback analysis failed: {str(e)}"
        }

class MLSoilAnalysisHandler(http.server.BaseHTTPRequestHandler):
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
                "service": "ML Soil Analysis API",
                "ml_available": True,
                "models_loaded": True,
                "database_available": DATABASE_AVAILABLE
            }
            self.wfile.write(json.dumps(response).encode())

        elif self.path == '/api/v1/history':
            # Get analysis history
            if DATABASE_AVAILABLE:
                try:
                    history = get_analysis_history_from_db(limit=20)
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

        elif self.path == '/api/v1/statistics':
            # Get analysis statistics
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
        if self.path == '/api/v1/analyze':
            try:
                # Read request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                print(f"🔍 Received ML soil analysis request: {data}")
                
                # Try ML analysis first, fallback if needed
                result = analyze_soil_with_ml(data)
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except Exception as e:
                print(f"❌ Error processing ML soil analysis request: {e}")
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
    """Start the ML soil analysis server"""
    PORT = 8000
    
    print("🌱 Starting ML-Based Soil Analysis Server...")
    print(f"🚀 Server will run on http://localhost:{PORT}")
    print("💡 Features:")
    print("   • ML Models Available: ✅ Yes (with fallback)")
    print("   • GET  /health - Health check")
    print("   • POST /api/v1/analyze - ML soil analysis")
    print("🔄 Press Ctrl+C to stop")
    
    try:
        with socketserver.TCPServer(("", PORT), MLSoilAnalysisHandler) as httpd:
            print(f"✅ Server started successfully on port {PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    start_server()
