#!/usr/bin/env python3
"""
Comprehensive fix for the Tomato/Coimbatore market analysis issue
"""

import requests
import json
import time
import subprocess
import sys
import os

def check_server_status():
    """Check if the market analysis server is running"""
    print("🔍 Checking Market Analysis Server Status...")
    
    try:
        response = requests.get("http://localhost:8003/health", timeout=5)
        if response.status_code == 200:
            print("✅ Market Analysis Server is running")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"⚠️ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Market Analysis Server is NOT running")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def start_server():
    """Start the market analysis server"""
    print("🚀 Starting Market Analysis Server...")
    
    if not os.path.exists("market_api.py"):
        print("❌ market_api.py not found. Please run this script from the market-analysis directory.")
        return False
    
    try:
        # Install requirements first
        print("📦 Installing requirements...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        
        print("✅ Requirements installed")
        print("🌐 Starting server on http://localhost:8003")
        print("💡 Server will run in the background. Press Ctrl+C to stop this script.")
        
        # Start server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "market_api:app", 
            "--host", "0.0.0.0", 
            "--port", "8003", 
            "--reload"
        ])
        
        # Wait a bit for server to start
        time.sleep(5)
        
        # Check if it started successfully
        if check_server_status():
            print("✅ Server started successfully!")
            return True
        else:
            print("❌ Server failed to start properly")
            process.terminate()
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def test_agmarknet_api():
    """Test direct AGMARKNET API access"""
    print("\n🌐 Testing Direct AGMARKNET API Access...")
    
    api_key = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"
    base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    
    params = {
        'api-key': api_key,
        'format': 'json',
        'limit': 5,
        'filters[commodity]': 'Tomato'
    }
    
    try:
        print(f"📡 Making request to: {base_url}")
        print(f"📤 Parameters: {params}")
        
        response = requests.get(base_url, params=params, timeout=15)
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            print(f"✅ AGMARKNET API is working! Found {len(records)} records")
            
            if records:
                print("📊 Sample data:")
                for i, record in enumerate(records[:2], 1):
                    print(f"   {i}. Market: {record.get('market', 'N/A')}")
                    print(f"      State: {record.get('state', 'N/A')}")
                    print(f"      Price: ₹{record.get('modal_price', 'N/A')}")
            return True
        else:
            print(f"❌ AGMARKNET API error: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ AGMARKNET API request timed out")
        return False
    except Exception as e:
        print(f"❌ AGMARKNET API error: {e}")
        return False

def test_market_analysis():
    """Test the specific failing case"""
    print("\n🍅 Testing Market Analysis for Tomato in Tamil Nadu, Coimbatore...")
    
    test_data = {
        "crop": "tomato",
        "state": "tamil nadu",
        "district": "coimbatore"
    }
    
    try:
        print(f"📤 Request: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(
            "http://localhost:8003/analyze",
            json=test_data,
            timeout=30
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! Market analysis completed")
            print(f"📊 Results:")
            print(f"   State Avg Price: ₹{data['state_avg_price']}")
            print(f"   District Avg Price: ₹{data.get('district_avg_price', 'N/A')}")
            print(f"   Price Trend: {data['price_trend']} ({data['trend_percentage']}%)")
            print(f"   Recommendation: {data['recommendation']}")
            print(f"   Confidence: {data['prediction_confidence']}")
            return True
        else:
            print(f"❌ FAILED! Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def clear_browser_cache_instructions():
    """Provide instructions to clear browser cache"""
    print("\n🧹 Browser Cache Clearing Instructions:")
    print("=" * 50)
    print("The 'weather data' error might be from cached JavaScript.")
    print("Please clear your browser cache:")
    print()
    print("🌐 Chrome/Edge:")
    print("   1. Press Ctrl+Shift+Delete")
    print("   2. Select 'Cached images and files'")
    print("   3. Click 'Clear data'")
    print()
    print("🦊 Firefox:")
    print("   1. Press Ctrl+Shift+Delete")
    print("   2. Select 'Cache'")
    print("   3. Click 'Clear Now'")
    print()
    print("🔄 Alternative: Hard refresh the page")
    print("   Press Ctrl+F5 or Ctrl+Shift+R")

def main():
    print("🌾 AgroConnect Market Analysis - Issue Fix Tool")
    print("🎯 Fixing: Tomato in Tamil Nadu, Coimbatore")
    print("=" * 60)
    
    # Step 1: Check if server is running
    server_running = check_server_status()
    
    if not server_running:
        print("\n💡 Server is not running. Would you like to start it? (y/n)")
        choice = input().lower().strip()
        if choice == 'y':
            if not start_server():
                print("❌ Failed to start server. Please start manually:")
                print("   python start_market_api.py")
                return
            server_running = True
        else:
            print("❌ Please start the server manually and run this script again:")
            print("   python start_market_api.py")
            return
    
    # Step 2: Test AGMARKNET API
    print("\n" + "=" * 60)
    agmarknet_working = test_agmarknet_api()
    
    # Step 3: Test market analysis
    print("\n" + "=" * 60)
    analysis_working = test_market_analysis()
    
    # Step 4: Provide summary and next steps
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSIS SUMMARY")
    print("=" * 60)
    print(f"✅ Market Analysis Server: {'Working' if server_running else 'Not Working'}")
    print(f"✅ AGMARKNET API: {'Working' if agmarknet_working else 'Not Working'}")
    print(f"✅ Tomato Analysis: {'Working' if analysis_working else 'Not Working'}")
    
    if server_running and analysis_working:
        print("\n🎉 EVERYTHING IS WORKING!")
        print("💡 Next steps:")
        print("1. Open market-analysis/market.html in your browser")
        print("2. Clear browser cache (Ctrl+F5)")
        print("3. Select: Tomato → Tamil Nadu → Coimbatore")
        print("4. Click 'Analyze Market'")
        print("5. You should see results without any 'weather data' error")
        
    else:
        print("\n🔧 TROUBLESHOOTING NEEDED:")
        if not server_running:
            print("❌ Start the market analysis server first")
        if not agmarknet_working:
            print("❌ Check internet connection for AGMARKNET API")
        if not analysis_working:
            print("❌ Check server logs for detailed error messages")
    
    # Always show cache clearing instructions
    clear_browser_cache_instructions()
    
    print("\n📞 If issues persist:")
    print("1. Check browser console (F12) for JavaScript errors")
    print("2. Ensure you're using the correct URL: market-analysis/market.html")
    print("3. Verify server is running on http://localhost:8003")

if __name__ == "__main__":
    main()
