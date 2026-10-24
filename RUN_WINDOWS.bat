@echo off
setlocal
cd /d "%~dp0"
echo =======================================
echo       AI Study Buddy - Launcher
echo =======================================
if not exist ".venv\Scripts\python.exe" (
    where py >nul 2>nul
    if not errorlevel 1 (
        py -3 -m venv .venv
    ) else (
        python -m venv .venv
    )
)
if not exist ".venv\Scripts\python.exe" (
    echo Could not create Python environment. Install Python 3.11+ and try again.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Dependency installation failed. Check internet access and Python installation.
    pause
    exit /b 1
)
echo.
echo Starting AI Study Buddy...
echo Your browser should open at http://localhost:8501
".venv\Scripts\python.exe" -m streamlit run app.py
pause
