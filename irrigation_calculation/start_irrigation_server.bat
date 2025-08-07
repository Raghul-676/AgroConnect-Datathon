@echo off
echo Starting Irrigation Calculation Backend Server...
echo.

REM Check if virtual environment exists
if not exist "irrigation_env\Scripts\activate.bat" (
    echo Virtual environment not found. Creating one...
    python -m venv irrigation_env
    echo.
    echo Installing requirements...
    call irrigation_env\Scripts\activate.bat
    pip install -r requirements.txt
    echo.
) else (
    echo Virtual environment found. Activating...
    call irrigation_env\Scripts\activate.bat
)

REM Start the FastAPI server
echo.
echo Starting Irrigation FastAPI server on http://localhost:8001
echo Press Ctrl+C to stop the server
echo Open http://localhost:8001/api/test to test the API
echo.
python main.py

pause
