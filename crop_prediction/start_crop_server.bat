@echo off
echo Starting Crop Prediction Backend Server...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    echo.
    echo Installing requirements...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    echo.
    echo Downloading spaCy English model...
    python -m spacy download en_core_web_sm
    echo.
) else (
    echo Virtual environment found. Activating...
    call venv\Scripts\activate.bat
)

REM Start the FastAPI server
echo.
echo Starting Crop Prediction FastAPI server on http://localhost:8002
echo Press Ctrl+C to stop the server
echo Open http://localhost:8002/health to test the API
echo.
python app.py

pause
