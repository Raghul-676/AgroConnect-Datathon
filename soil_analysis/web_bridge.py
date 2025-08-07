#!/usr/bin/env python3
"""
Web Bridge for Frontend-Backend Connection
Simple HTTP server to connect HTML frontend to soil analysis backend
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import os
from soil_analyzer import TerminalSoilAnalyzer

class SoilAnalysisHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.analyzer = TerminalSoilAnalyzer()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests - serve HTML file"""
        if self.path == '/' or self.path == '/index.html':
            self.serve_html()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests - process soil analysis"""
        if self.path == '/analyze':
            self.handle_analysis()
        else:
            self.send_error(404)
    
    def serve_html(self):
        """Serve the HTML file"""
        try:
            with open('index.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "index.html not found")
    
    def handle_analysis(self):
        """Process soil analysis request"""
        try:
            # Get POST data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parse form data
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            # Extract and convert form data to soil analysis format
            soil_data = self.convert_form_data(form_data)
            
            if 'error' in soil_data:
                self.send_json_response(soil_data, 400)
                return
            
            # Perform analysis
            result = self.analyzer.analyze_from_json(json.dumps(soil_data))
            
            # Send response
            self.send_json_response(result)
            
        except Exception as e:
            error_response = {"error": f"Analysis failed: {str(e)}"}
            self.send_json_response(error_response, 500)
    
    def convert_form_data(self, form_data):
        """Convert HTML form data to soil analysis format"""
        try:
            # Helper function to get form value
            def get_value(key, default=0):
                return float(form_data.get(key, [default])[0]) if form_data.get(key, [''])[0] else default
            
            # Basic parameters
            ph = get_value('ph')
            salinity = get_value('salinity')
            texture = form_data.get('texture', ['loam'])[0].lower().strip()
            bulk_density = get_value('density', 1.2)
            
            # Map texture names if needed
            texture_mapping = {
                'loamy': 'loam',
                'clay loam': 'clay_loam',
                'sandy loam': 'sandy_loam',
                'silt loam': 'silt_loam',
                'sandy clay': 'sandy_clay',
                'silty clay': 'silty_clay',
                'sandy clay loam': 'sandy_clay_loam',
                'silty clay loam': 'silty_clay_loam'
            }
            texture = texture_mapping.get(texture, texture)
            
            # Validate basic parameters
            if not (0 <= ph <= 14):
                return {"error": "pH must be between 0 and 14"}
            if salinity < 0:
                return {"error": "Salinity must be non-negative"}
            if not (0.5 <= bulk_density <= 2.5):
                return {"error": "Bulk density must be between 0.5 and 2.5 g/cm³"}
            
            # Nutrients
            nutrients = {
                "nitrogen": get_value('n', 120),
                "phosphorus": get_value('p', 25),
                "potassium": get_value('k', 50),
                "calcium": get_value('ca', 1500),
                "magnesium": get_value('mg', 200),
                "sulfur": get_value('s', 12),
                "iron": get_value('fe', 6),
                "manganese": get_value('mn', 4),
                "zinc": get_value('zn', 1.2)
            }
            
            # Get crop from form
            crop = form_data.get('crop', ['wheat'])[0].lower().strip()
            valid_crops = ["wheat", "rice", "corn", "tomato", "potato", "soybean"]
            if crop not in valid_crops:
                return {"error": f"Invalid crop. Must be one of: {', '.join(valid_crops)}"}
            
            return {
                "ph": ph,
                "salinity": salinity,
                "texture": texture,
                "bulk_density": bulk_density,
                "nutrients": nutrients,
                "crop": crop
            }
            
        except (ValueError, KeyError) as e:
            return {"error": f"Invalid form data: {str(e)}"}
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server(port=8080):
    """Run the web server"""
    server_address = ('', port)
    
    # Create handler class with analyzer instance
    class Handler(SoilAnalysisHandler):
        def __init__(self, *args, **kwargs):
            self.analyzer = TerminalSoilAnalyzer()
            super(BaseHTTPRequestHandler, self).__init__(*args, **kwargs)
    
    httpd = HTTPServer(server_address, Handler)
    print(f"🌱 Soil Analysis Web Server running on http://localhost:{port}")
    print(f"📱 Open your browser and go to: http://localhost:{port}")
    print("🔄 Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped!")
        httpd.server_close()

if __name__ == "__main__":
    # Check if index.html exists
    if not os.path.exists('index.html'):
        print("❌ Error: index.html not found in current directory")
        print("Make sure you're running this from the same folder as index.html")
        exit(1)
    
    run_server()
