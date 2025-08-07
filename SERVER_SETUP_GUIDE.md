# AgroConnect Backend Servers Setup Guide

This guide explains how to run all the backend servers for the AgroConnect project.

## 🚀 Quick Start - Run All Servers

### 1. Soil Analysis Server (Port 8000)
```bash
cd soil_analysis
start_server.bat
```
**Server URL:** http://localhost:8000
**API Docs:** http://localhost:8000/docs

### 2. Irrigation Calculation Server (Port 8001)
```bash
cd irrigation_calculation
start_irrigation_server.bat
```
**Server URL:** http://localhost:8001
**API Test:** http://localhost:8001/api/test

### 3. Crop Prediction Server (Port 8002)
```bash
cd crop_prediction
start_crop_server.bat
```
**Server URL:** http://localhost:8002
**API Test:** http://localhost:8002/health

### 4. Market Analysis Server (Port 8003)
```bash
cd market-analysis
python start_market_api.py
```
**Server URL:** http://localhost:8003
**API Docs:** http://localhost:8003/docs
**API Test:** http://localhost:8003/health

## 📋 Server Details

### Soil Analysis Server
- **Port:** 8000
- **Main Endpoints:**
  - `GET /health` - Health check
  - `POST /api/v1/analyze` - Analyze soil
  - `GET /api/v1/crops` - Get supported crops
  - `GET /api/v1/soil-textures` - Get soil textures

### Irrigation Calculation Server
- **Port:** 8001
- **Main Endpoints:**
  - `GET /api/test` - Test endpoint
  - `POST /api/calculate-irrigation` - Calculate irrigation
  - `GET /api/weather/{location}` - Get weather data

### Crop Prediction Server
- **Port:** 8002
- **Main Endpoints:**
  - `GET /health` - Health check
  - `POST /predict` - Predict crop yield
  - `GET /` - Serve frontend page

### Market Analysis Server
- **Port:** 8003
- **Main Endpoints:**
  - `GET /health` - Health check
  - `POST /analyze` - Analyze market data with ML predictions
  - `GET /crops` - Get supported crops
  - `GET /states` - Get supported states
- **Features:**
  - AGMARKNET API integration
  - Machine learning price trend analysis
  - Selling recommendations
  - Real-time market data

## 🔧 Manual Setup (if needed)

### Soil Analysis
```bash
cd soil_analysis
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Irrigation Calculation
```bash
cd irrigation_calculation
python -m venv irrigation_env
irrigation_env\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Crop Prediction
```bash
cd crop_prediction
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python app.py
```

## ✅ Testing the Servers

### Test Soil Analysis
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/crops
```

### Test Irrigation Calculation
```bash
curl http://localhost:8001/api/test
```

### Test Crop Prediction
```bash
curl http://localhost:8002/health
```

## 🌐 Frontend Access

- **Dashboard:** `dashboard.html`
- **Soil Analysis:** `soil_analysis/index.html`
- **Irrigation Planner:** `irrigation_calculation/irrigation.html`
- **Crop Prediction:** `crop_prediction/crop_page.html`
- **Market Analysis:** `market-analysis/market.html`
- **Floating AgroBot Chat:** Available on all pages (bottom-right corner)

## 🚨 Troubleshooting

**Port Already in Use:**
- Soil Analysis uses port 8000
- Irrigation uses port 8001
- Crop Prediction uses port 8002
- Make sure no other services are using these ports

**Module Not Found:**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**Connection Refused:**
- Check if the server is running
- Verify the correct port number
- Check firewall settings

## 📝 Notes

- All three servers run independently
- Each has its own virtual environment
- Frontend pages are configured to use the correct ports
- All CORS issues are handled by the backend servers
- Crop prediction requires spaCy English model (auto-downloaded)
- Floating AgroBot chat is available on every page via `agrobot-chat.js`
