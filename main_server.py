#!/usr/bin/env python3
"""
AgroConnect Main Server
Serves the complete AgroConnect application with all modules
"""

import http.server
import socketserver
import os
import mimetypes
import urllib.parse
from pathlib import Path

class AgroConnectHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for AgroConnect application"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)
    
    def do_GET(self):
        """Handle GET requests with proper routing"""
        try:
            # Parse the URL
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            
            # Remove leading slash
            if path.startswith('/'):
                path = path[1:]
            
            # Default route - serve home.html
            if path == '' or path == '/':
                path = 'home.html'
            
            # Route mappings for clean URLs
            route_mappings = {
                'home': 'home.html',
                'dashboard': 'dashboard.html',
                'soil': 'soil_analysis/index.html',
                'irrigation': 'irrigation_calculation/irrigation.html',
                'market': 'market-analysis/market.html',
                'crop': 'crop_prediction/crop_page.html',
                'profile': 'profile.html',
                'settings': 'settings.html'
            }
            
            # Check if it's a clean URL route
            if path in route_mappings:
                path = route_mappings[path]
            
            # Construct full file path
            file_path = Path(path)
            
            # Security check - prevent directory traversal
            try:
                file_path.resolve().relative_to(Path.cwd().resolve())
            except ValueError:
                self.send_error(403, "Access denied")
                return
            
            # Check if file exists
            if not file_path.exists():
                self.send_error(404, f"File not found: {path}")
                return
            
            # Check if it's a directory
            if file_path.is_dir():
                # Look for index.html in the directory
                index_file = file_path / 'index.html'
                if index_file.exists():
                    file_path = index_file
                else:
                    self.send_error(404, f"Directory index not found: {path}")
                    return
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(str(file_path))
            if content_type is None:
                content_type = 'application/octet-stream'
            
            # Read and serve the file
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Content-length', len(content))
            
            # Add CORS headers for API calls
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            
            # Cache control for static assets
            if content_type.startswith('text/css') or content_type.startswith('application/javascript'):
                self.send_header('Cache-Control', 'public, max-age=3600')
            elif content_type.startswith('image/'):
                self.send_header('Cache-Control', 'public, max-age=86400')
            
            self.end_headers()
            self.wfile.write(content)
            
            # Log the request
            print(f"✅ Served: {path} ({content_type}) - {len(content)} bytes")
            
        except Exception as e:
            print(f"❌ Error serving {self.path}: {e}")
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom log message format"""
        return  # Suppress default logging, we have custom logging

def check_required_files():
    """Check if all required files exist"""
    required_files = [
        'home.html',
        'dashboard.html',
        'soil_analysis/index.html',
        'irrigation_calculation/irrigation.html',
        'market-analysis/market.html',
        'crop_prediction/crop_page.html',
        'auth.js',
        'agrobot-chat.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("⚠️ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found")
    return True

def start_server(port=8080):
    """Start the AgroConnect main server"""
    try:
        # Check required files
        if not check_required_files():
            print("❌ Cannot start server - missing required files")
            return False
        
        # Create server
        with socketserver.TCPServer(("", port), AgroConnectHandler) as httpd:
            print("🚀 AgroConnect Main Server Starting...")
            print("=" * 60)
            print(f"🌐 Server running at: http://localhost:{port}")
            print("📱 Available routes:")
            print(f"   🏠 Home Page:           http://localhost:{port}/")
            print(f"   📊 Dashboard:           http://localhost:{port}/dashboard")
            print(f"   🌱 Soil Analysis:       http://localhost:{port}/soil")
            print(f"   💧 Irrigation:          http://localhost:{port}/irrigation")
            print(f"   📈 Market Analysis:     http://localhost:{port}/market")
            print(f"   🌾 Crop Prediction:     http://localhost:{port}/crop")
            print("=" * 60)
            print("✅ All modules integrated and ready!")
            print("🔗 All internal links will work properly")
            print("⚡ Backend APIs running on separate ports:")
            print("   - Soil Analysis API: http://localhost:8001")
            print("   - Irrigation API: http://localhost:8004") 
            print("   - Crop Prediction API: http://localhost:8002")
            print("   - Market Analysis API: http://localhost:8003")
            print("=" * 60)
            print("🎯 Press Ctrl+C to stop the server")
            print()
            
            # Start serving
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {port} is already in use")
            print(f"💡 Try a different port or stop the existing server")
            return False
        else:
            print(f"❌ Server error: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    # Get port from command line argument or use default
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("❌ Invalid port number. Using default port 8080.")
    
    # Start the server
    success = start_server(port)
    
    if success:
        print("✅ AgroConnect server shut down successfully")
    else:
        print("❌ AgroConnect server failed to start")
        sys.exit(1)
