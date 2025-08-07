#!/usr/bin/env python3
"""
Test script to verify web connection is working
"""

import requests
import json

def test_web_connection():
    """Test the web bridge connection"""
    print("🧪 Testing Web Bridge Connection...")
    
    # Test data (excellent wheat soil)
    test_data = {
        'ph': '6.5',
        'salinity': '1.0',
        'texture': 'loam',
        'density': '1.2',
        'n': '150',
        'p': '30',
        'k': '50',
        'ca': '2000',
        'mg': '250',
        's': '15',
        'fe': '8',
        'mn': '5',
        'zn': '1.5',
        'crop': 'wheat'
    }
    
    try:
        # Send POST request to web bridge
        response = requests.post('http://localhost:8080/analyze', data=test_data)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Connection successful!")
            print(f"📊 Category: {result.get('category', 'N/A').upper()}")
            print(f"🎯 Score: {result.get('suitability_score', 'N/A')}/100")
            print(f"🌾 Crop: {result.get('crop', 'N/A').title()}")
            print(f"💬 Message: {result.get('message', 'N/A')[:100]}...")
            
            if result.get('fertilizer_recommendations'):
                print(f"🧪 Fertilizers: {len(result['fertilizer_recommendations'])} recommendations")
            
            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure the web server is running:")
        print("   python web_bridge.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_web_connection()
