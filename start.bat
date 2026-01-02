@echo off
echo ============================================
echo   PatiPedia Windows Setup & Start Script
echo ============================================

cd /d "%~dp0"

IF NOT EXIST ".venv" (
    echo [INFO] Virtual environment creating...
    python -m venv .venv
    echo [INFO] Virtual environment created.
)

echo [INFO] Activating virtual environment...
call .venv\Scripts\activate

echo [INFO] Installing requirements...
pip install -r requirements.txt

echo [INFO] Starting Application...
python app.py

pause
