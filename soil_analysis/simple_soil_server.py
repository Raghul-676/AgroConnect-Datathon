#!/usr/bin/env python3
"""
Simple Soil Analysis Server
Lightweight HTTP server for soil analysis without heavy dependencies
"""

import http.server
import socketserver
import json
import urllib.parse
from datetime import datetime

# Simple soil analysis logic
def analyze_soil_simple(data):
    """Simple soil analysis without ML dependencies"""
    try:
        # Extract parameters
        ph = data.get('ph', 7.0)
        salinity = data.get('salinity', 1.0)
        texture = data.get('texture', 'loam')
        bulk_density = data.get('bulk_density', 1.3)
        nutrients = data.get('nutrients', {})
        crop = data.get('crop', 'wheat')
        
        # Simple scoring logic
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
        
        # Bulk density analysis
        if bulk_density > 1.6:
            score -= 15
            recommendations.append("Soil compaction detected. Consider deep tillage.")
        elif bulk_density < 1.0:
            score -= 5
            recommendations.append("Soil may be too loose. Add organic matter.")
        else:
            recommendations.append("Soil density is good for root development.")
        
        # Nutrient analysis
        nitrogen = nutrients.get('nitrogen', 100)
        phosphorus = nutrients.get('phosphorus', 25)
        potassium = nutrients.get('potassium', 40)
        
        if nitrogen < 80:
            score -= 15
            recommendations.append("Low nitrogen. Apply nitrogen-rich fertilizer or compost.")
        elif nitrogen > 200:
            score -= 5
            recommendations.append("High nitrogen. Reduce nitrogen fertilization.")
        
        if phosphorus < 20:
            score -= 10
            recommendations.append("Low phosphorus. Apply phosphate fertilizer.")
        elif phosphorus > 50:
            score -= 3
            recommendations.append("High phosphorus. Monitor to prevent runoff.")
        
        if potassium < 30:
            score -= 10
            recommendations.append("Low potassium. Apply potash fertilizer.")
        elif potassium > 80:
            score -= 3
            recommendations.append("High potassium levels detected.")
        
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
        
        # Fertilizer recommendations
        fertilizer_recommendations = []
        
        if nitrogen < 100:
            fertilizer_recommendations.append({
                "name": "Urea",
                "amount": f"{max(10, (100-nitrogen)/10):.1f}",
                "unit": "kg/acre",
                "application_method": "Broadcast and incorporate",
                "timing": "Before planting"
            })
        
        if phosphorus < 25:
            fertilizer_recommendations.append({
                "name": "DAP (Diammonium Phosphate)",
                "amount": f"{max(5, (25-phosphorus)/5):.1f}",
                "unit": "kg/acre",
                "application_method": "Band application",
                "timing": "At planting"
            })
        
        if potassium < 40:
            fertilizer_recommendations.append({
                "name": "Muriate of Potash",
                "amount": f"{max(5, (40-potassium)/8):.1f}",
                "unit": "kg/acre",
                "application_method": "Broadcast",
                "timing": "Before planting"
            })
        
        return {
            "success": True,
            "crop": crop,
            "suitability_score": round(score, 1),
            "category": category,
            "message": message,
            "recommendations": recommendations,
            "fertilizer_recommendations": fertilizer_recommendations,
            "analysis_date": datetime.now().isoformat(),
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
            "error": f"Analysis failed: {str(e)}"
        }

class SoilAnalysisHandler(http.server.BaseHTTPRequestHandler):
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
            response = {"status": "healthy", "service": "Soil Analysis API"}
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
                
                print(f"🔍 Received soil analysis request: {data}")
                
                # Perform analysis
                result = analyze_soil_simple(data)
                
                print(f"✅ Analysis result: Score={result.get('suitability_score', 0)}, Category={result.get('category', 'unknown')}")
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except Exception as e:
                print(f"❌ Error processing request: {e}")
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
    """Start the soil analysis server"""
    PORT = 8000
    
    print("🌱 Starting Simple Soil Analysis Server...")
    print(f"🚀 Server will run on http://localhost:{PORT}")
    print("💡 Endpoints:")
    print("   • GET  /health - Health check")
    print("   • POST /api/v1/analyze - Soil analysis")
    print("🔄 Press Ctrl+C to stop")
    
    try:
        with socketserver.TCPServer(("", PORT), SoilAnalysisHandler) as httpd:
            print(f"✅ Server started successfully on port {PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    start_server()
