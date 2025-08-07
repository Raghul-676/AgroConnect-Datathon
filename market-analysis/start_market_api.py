#!/usr/bin/env python3
"""
Market Analysis API Startup Script
"""

import subprocess
import sys
import os
import time

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False
    return True

def start_api_server():
    """Start the FastAPI server"""
    print("🚀 Starting Market Analysis API server...")
    print("📡 Server will be available at: http://localhost:8003")
    print("📊 API Documentation: http://localhost:8003/docs")
    print("🔄 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "market_api:app", 
            "--host", "0.0.0.0", 
            "--port", "8003", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    print("🌾 AgroConnect Market Analysis API")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("market_api.py"):
        print("❌ market_api.py not found. Please run this script from the market-analysis directory.")
        return
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements. Please check your Python environment.")
        return
    
    print("\n⏳ Starting server in 3 seconds...")
    time.sleep(3)
    
    # Start the API server
    start_api_server()

if __name__ == "__main__":
    main()
