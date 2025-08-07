#!/usr/bin/env python3
"""
Market Analysis Demo Script
Demonstrates the ML-powered market analysis features
"""

import requests
import json
import time
from datetime import datetime

API_BASE_URL = "http://localhost:8003"

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"🌾 {title}")
    print("=" * 60)

def print_analysis_result(data):
    """Print formatted analysis result"""
    print(f"\n📊 Market Analysis Results for {data['crop'].title()} in {data['state'].title()}")
    print("-" * 50)
    
    # Price information
    print(f"🏛️  State Average Price: ₹{data['state_avg_price']:,.2f} per quintal")
    if data['district_avg_price']:
        print(f"🏘️  District Average Price: ₹{data['district_avg_price']:,.2f} per quintal")
    
    # Trend analysis
    trend_icon = "📈" if data['price_trend'] == 'increasing' else "📉" if data['price_trend'] == 'decreasing' else "➡️"
    print(f"{trend_icon} Price Trend: {data['price_trend'].title()} ({data['trend_percentage']:+.1f}%)")
    
    # AI Recommendation
    print(f"💡 AI Recommendation: {data['recommendation']}")
    print(f"🎯 Prediction Confidence: {data['prediction_confidence']*100:.1f}%")
    
    # Market data
    if data['market_data']:
        print(f"\n📍 Recent Market Data ({len(data['market_data'])} markets):")
        for i, market in enumerate(data['market_data'][:3], 1):
            print(f"   {i}. {market['market']}, {market['district']}")
            print(f"      Modal Price: ₹{market['modal_price']} | Range: ₹{market['min_price']}-₹{market['max_price']}")
    
    print("-" * 50)

def demo_crop_analysis():
    """Demo different crop analyses"""
    print_header("CROP MARKET ANALYSIS DEMO")
    
    demo_crops = [
        {"crop": "tomato", "state": "tamil nadu", "district": "erode"},
        {"crop": "onion", "state": "maharashtra"},
        {"crop": "potato", "state": "punjab"},
        {"crop": "chillies", "state": "andhra pradesh"}
    ]
    
    for i, crop_data in enumerate(demo_crops, 1):
        print(f"\n🧪 Demo {i}: Analyzing {crop_data['crop'].title()} market...")
        
        try:
            response = requests.post(f"{API_BASE_URL}/analyze", json=crop_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print_analysis_result(result)
                
                # Simulate user decision making
                if result['recommendation'].lower().startswith('sell'):
                    print("✅ Farmer Decision: Selling immediately based on AI recommendation")
                elif 'wait' in result['recommendation'].lower():
                    print("⏳ Farmer Decision: Waiting for better prices as suggested")
                else:
                    print("🤔 Farmer Decision: Monitoring market for next few days")
                    
            else:
                print(f"❌ Analysis failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        if i < len(demo_crops):
            print("\n⏳ Next analysis in 3 seconds...")
            time.sleep(3)

def demo_state_comparison():
    """Demo price comparison across states"""
    print_header("MULTI-STATE PRICE COMPARISON")
    
    crop = "tomato"
    states = ["tamil nadu", "karnataka", "andhra pradesh", "maharashtra"]
    
    print(f"🍅 Comparing {crop.title()} prices across different states...")
    
    results = []
    for state in states:
        try:
            response = requests.post(
                f"{API_BASE_URL}/analyze", 
                json={"crop": crop, "state": state}, 
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                results.append({
                    'state': state.title(),
                    'price': data['state_avg_price'],
                    'trend': data['price_trend'],
                    'percentage': data['trend_percentage']
                })
                print(f"✅ {state.title()}: ₹{data['state_avg_price']:,.2f}")
            else:
                print(f"❌ {state.title()}: Failed to fetch data")
                
        except Exception as e:
            print(f"❌ {state.title()}: Error - {e}")
        
        time.sleep(1)  # Rate limiting
    
    if results:
        # Find best and worst prices
        best_price = min(results, key=lambda x: x['price'])
        worst_price = max(results, key=lambda x: x['price'])
        
        print(f"\n📊 Price Comparison Summary:")
        print(f"🟢 Lowest Price: {best_price['state']} - ₹{best_price['price']:,.2f}")
        print(f"🔴 Highest Price: {worst_price['state']} - ₹{worst_price['price']:,.2f}")
        
        price_diff = worst_price['price'] - best_price['price']
        price_diff_percent = (price_diff / best_price['price']) * 100
        print(f"💰 Price Difference: ₹{price_diff:,.2f} ({price_diff_percent:.1f}%)")
        
        print(f"\n💡 Trading Opportunity:")
        print(f"   Buy from: {best_price['state']} (₹{best_price['price']:,.2f})")
        print(f"   Sell to: {worst_price['state']} (₹{worst_price['price']:,.2f})")
        print(f"   Potential Profit: ₹{price_diff:,.2f} per quintal")

def demo_ml_predictions():
    """Demo machine learning prediction capabilities"""
    print_header("MACHINE LEARNING PREDICTIONS DEMO")
    
    print("🧠 Demonstrating AI-powered market predictions...")
    
    test_case = {"crop": "onion", "state": "maharashtra"}
    
    try:
        response = requests.post(f"{API_BASE_URL}/analyze", json=test_case, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n🔍 ML Analysis for {data['crop'].title()} in {data['state'].title()}:")
            print(f"📈 Trend Detection: {data['price_trend'].title()}")
            print(f"📊 Trend Strength: {abs(data['trend_percentage']):.1f}%")
            print(f"🎯 Model Confidence: {data['prediction_confidence']*100:.1f}%")
            
            # Explain the ML logic
            print(f"\n🧠 AI Reasoning:")
            if data['price_trend'] == 'increasing':
                print("   • Linear regression detected upward price movement")
                print("   • Historical data shows positive slope")
                print("   • Recommendation: Wait for higher prices")
            elif data['price_trend'] == 'decreasing':
                print("   • Price analysis indicates downward trend")
                print("   • Market data shows declining pattern")
                print("   • Recommendation: Sell before further decline")
            else:
                print("   • Price movements are within stable range")
                print("   • No significant trend detected")
                print("   • Recommendation: Current market conditions are favorable")
            
            # Confidence explanation
            confidence_level = data['prediction_confidence']
            if confidence_level > 0.8:
                print(f"   • High confidence ({confidence_level*100:.1f}%) - Strong data pattern")
            elif confidence_level > 0.6:
                print(f"   • Medium confidence ({confidence_level*100:.1f}%) - Moderate data reliability")
            else:
                print(f"   • Low confidence ({confidence_level*100:.1f}%) - Limited or volatile data")
                
        else:
            print(f"❌ ML analysis failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ML demo error: {e}")

def main():
    print("🌾 AgroConnect Market Analysis - ML Demo")
    print("🤖 Powered by AGMARKNET API + Machine Learning")
    print(f"⏰ Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Market Analysis API server is not running!")
            print("💡 Please start the server first: python start_market_api.py")
            return
    except:
        print("❌ Cannot connect to Market Analysis API server!")
        print("💡 Please start the server first: python start_market_api.py")
        return
    
    print("✅ Connected to Market Analysis API")
    
    # Run demos
    demo_crop_analysis()
    demo_state_comparison()
    demo_ml_predictions()
    
    print_header("DEMO COMPLETED")
    print("🎉 Market Analysis Demo completed successfully!")
    print("\n💡 Next Steps:")
    print("1. Open market-analysis/market.html in your browser")
    print("2. Try different crop and state combinations")
    print("3. Observe real-time ML predictions and recommendations")
    print("4. Download PDF reports for detailed analysis")
    print("\n🚀 The system is ready for production use!")

if __name__ == "__main__":
    main()
