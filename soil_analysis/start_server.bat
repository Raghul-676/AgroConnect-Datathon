@echo off
echo Starting Soil Analysis Backend Server...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    echo.
    echo Installing requirements...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    pip install pydantic-settings
    echo.
) else (
    echo Virtual environment found. Activating...
    call venv\Scripts\activate.bat
)

REM Start the FastAPI server
echo.
echo Starting FastAPI server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo Open http://localhost:8000 in your browser to test the API
echo.
python main.py

pause
