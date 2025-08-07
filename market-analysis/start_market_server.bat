@echo off
echo 🌾 AgroConnect Market Analysis Server
echo =====================================

echo 📦 Installing requirements...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Failed to install requirements
    pause
    exit /b 1
)

echo ✅ Requirements installed successfully!
echo.
echo 🚀 Starting Market Analysis API server...
echo 📡 Server will be available at: http://localhost:8003
echo 📊 API Documentation: http://localhost:8003/docs
echo 🔄 Press Ctrl+C to stop the server
echo.

python -m uvicorn market_api:app --host 0.0.0.0 --port 8003 --reload

pause
