# 📊 AgroConnect Market Analysis System

## 🎯 Overview

The Market Analysis System provides real-time agricultural market data using the **AGMARKNET API** with **Machine Learning predictions** for price trends and selling recommendations.

## 🚀 Features

### **Real-Time Market Data**
- **AGMARKNET Integration**: Government of India's official agricultural market data
- **Live Prices**: Current market prices from mandis across India
- **Multiple Markets**: Compare prices across different locations
- **Historical Trends**: Price movement analysis

### **Machine Learning Predictions**
- **Price Trend Analysis**: Linear regression-based trend prediction
- **Selling Recommendations**: AI-powered advice on optimal selling time
- **Confidence Scoring**: Prediction reliability metrics
- **Pattern Recognition**: Market behavior analysis

### **Interactive Dashboard**
- **Dynamic Filters**: Select crop, state, and district
- **Real-time Updates**: Auto-refresh market data
- **Visual Analytics**: Charts and trend indicators
- **Export Reports**: PDF generation with analysis

## 🛠️ Technical Stack

### **Backend API**
- **FastAPI**: High-performance Python web framework
- **Scikit-learn**: Machine learning for trend analysis
- **Pandas/NumPy**: Data processing and analysis
- **Requests**: AGMARKNET API integration

### **Frontend**
- **HTML5/CSS3**: Modern responsive design
- **JavaScript ES6**: Dynamic user interactions
- **Tailwind CSS**: Professional styling
- **Chart.js**: Data visualization

### **Data Source**
- **API**: AGMARKNET (Government of India)
- **API Key**: `579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b`
- **Endpoint**: `https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070`

## 📦 Installation & Setup

### **1. Install Dependencies**
```bash
cd market-analysis
pip install -r requirements.txt
```

### **2. Start the API Server**
```bash
python start_market_api.py
```

### **3. Access the Application**
- **Frontend**: Open `market.html` in your browser
- **API Documentation**: http://localhost:8003/docs
- **Health Check**: http://localhost:8003/health

## 🎮 How to Use

### **Step 1: Select Parameters**
1. Choose a **Crop** (Tomato, Onion, Potato, etc.)
2. Select a **State** (Tamil Nadu, Karnataka, etc.)
3. Optionally select a **District** for local data

### **Step 2: Analyze Market**
- Click **"📊 Analyze Market"** button
- System fetches real-time data from AGMARKNET
- ML algorithms process the data for trends

### **Step 3: View Results**
- **State Average Price**: Regional price average
- **District Average Price**: Local market price
- **Price Trend**: Increasing/Decreasing/Stable with percentage
- **AI Recommendation**: When to sell for optimal profit

### **Step 4: Export Report**
- Click **"📥 Download Report as PDF"**
- Get comprehensive analysis report

## 🧠 Machine Learning Features

### **Price Trend Analysis**
```python
# Linear regression for trend prediction
model = LinearRegression()
model.fit(time_series_data, prices)
trend_direction = model.coef_[0]  # Slope indicates trend
```

### **Recommendation Engine**
- **Increasing Trend (>5%)**: "Wait 3-5 days - prices are rising"
- **Decreasing Trend (<-5%)**: "Sell immediately - prices are falling"
- **Stable Market**: "Good time to sell - stable market"
- **Mixed Signals**: "Monitor for 1-2 days"

### **Confidence Scoring**
- **R² Score**: Model fit quality (0-1)
- **Data Freshness**: Recent data availability
- **Market Volatility**: Price stability factor

## 📊 Supported Crops

### **Vegetables**
- 🍅 Tomato
- 🧅 Onion  
- 🥔 Potato
- 🍆 Brinjal
- 🌶️ Chillies
- 🥬 Cauliflower
- 🥬 Cabbage
- 🥕 Carrot

### **States Covered**
- Tamil Nadu
- Andhra Pradesh
- Karnataka
- Punjab
- Maharashtra
- Gujarat
- Rajasthan
- Uttar Pradesh

## 🔧 API Endpoints

### **POST /analyze**
Analyze market data for specific crop and location
```json
{
  "crop": "tomato",
  "state": "tamil nadu",
  "district": "erode"
}
```

### **GET /health**
Check API server status

### **GET /crops**
Get list of supported crops

### **GET /states**
Get list of supported states

## 📈 Sample Response

```json
{
  "crop": "tomato",
  "state": "tamil nadu",
  "district": "erode",
  "state_avg_price": 2850.50,
  "district_avg_price": 2920.00,
  "price_trend": "increasing",
  "trend_percentage": 3.2,
  "recommendation": "Wait 2-3 days - slight upward trend",
  "prediction_confidence": 0.78,
  "market_data": [
    {
      "market": "Erode Market",
      "district": "Erode",
      "modal_price": "2900",
      "min_price": "2500",
      "max_price": "3200",
      "arrival_date": "06/08/2025"
    }
  ]
}
```

## 🎯 Benefits

### **For Farmers**
- **Optimal Selling Time**: Know when to sell for maximum profit
- **Market Intelligence**: Compare prices across regions
- **Trend Awareness**: Understand market movements
- **Data-Driven Decisions**: Scientific approach to selling

### **For Traders**
- **Price Discovery**: Real-time market rates
- **Regional Comparison**: Multi-state price analysis
- **Trend Prediction**: Future price movements
- **Risk Management**: Market volatility insights

## 🔄 Data Flow

```
User Selection → Frontend → API Request → AGMARKNET → Data Processing → ML Analysis → Results Display
```

1. **User Input**: Crop, State, District selection
2. **API Call**: Frontend sends request to backend
3. **Data Fetch**: Backend queries AGMARKNET API
4. **ML Processing**: Trend analysis and predictions
5. **Response**: Formatted results with recommendations
6. **Display**: Interactive dashboard with insights

## 🚨 Error Handling

- **API Failures**: Fallback to cached data
- **Network Issues**: User-friendly error messages
- **Invalid Inputs**: Input validation and suggestions
- **No Data**: Alternative crop/state suggestions

## 🔮 Future Enhancements

- **Weather Integration**: Weather impact on prices
- **Seasonal Patterns**: Historical seasonal analysis
- **Price Alerts**: Notification system for price changes
- **Mobile App**: React Native mobile application
- **Advanced ML**: Deep learning for better predictions

## 📞 Support

For technical support or feature requests:
- **Email**: support@agroconnect.in
- **Phone**: +91 98765 43210

---

**🌾 Powered by AgroConnect - Smart Agriculture Solutions**
