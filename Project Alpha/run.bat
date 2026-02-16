@echo off
REM Trading Bot Startup Script for Windows
REM This script helps you run the entire system

setlocal enabledelayedexpansion

:menu
cls
echo.
echo ============================================================
echo         Trading Bot - Hybrid System Launcher
echo ============================================================
echo.
echo Select what to run:
echo.
echo 1. Start Backend Server (FastAPI)
echo 2. Start Mobile App (Kivy)
echo 3. Start Web Dashboard (Dash)
echo 4. Run All (3 windows)
echo 5. Build APK
echo 6. Test API Connection
echo 7. Install Dependencies
echo 8. Exit
echo.
set /p choice="Enter your choice (1-8): "

if "%choice%"=="1" goto backend
if "%choice%"=="2" goto mobile
if "%choice%"=="3" goto web
if "%choice%"=="4" goto all
if "%choice%"=="5" goto apk
if "%choice%"=="6" goto test
if "%choice%"=="7" goto install
if "%choice%"=="8" goto exit

echo Invalid choice. Please try again.
pause
goto menu

:backend
echo.
echo Starting Backend Server...
echo.
python backend/main.py
pause
goto menu

:mobile
echo.
echo Starting Mobile App (Kivy)...
echo.
python mobile/trading_bot_app.py
pause
goto menu

:web
echo.
echo Starting Web Dashboard (Dash)...
echo.
python app.py
pause
goto menu

:all
echo.
echo Starting all components...
echo.
echo - Backend will open in window 1
echo - Mobile app will open in window 2
echo - Web dashboard will open in window 3
echo.
pause

start "Backend Server" python backend/main.py
timeout /t 2 /nobreak
start "Mobile App (Kivy)" python mobile/trading_bot_app.py
timeout /t 2 /nobreak
start "Web Dashboard (Dash)" python app.py

echo.
echo All components started!
echo.
echo Backend:   http://localhost:8000
echo Dashboard: http://localhost:8050
echo.
pause
goto menu

:apk
echo.
echo Building APK...
echo.
echo This will take 5-10 minutes on first build.
echo.
pause

buildozer android debug

echo.
echo APK build complete!
echo Location: bin/tradingbot-0.1-debug.apk
echo.
pause
goto menu

:test
echo.
echo Testing API Connection...
echo.
python -c "
import requests
import json

try:
    response = requests.get('http://localhost:8000/api/broker/status', timeout=5)
    print('Backend Status: CONNECTED')
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f'Backend Status: DISCONNECTED')
    print(f'Error: {e}')
    print()
    print('Make sure to start the backend server first:')
    print('  python backend/main.py')
"

pause
goto menu

:install
echo.
echo Installing Python Dependencies...
echo.
pip install -r requirements.txt --upgrade

echo.
echo Installation complete!
echo.
pause
goto menu

:exit
echo.
echo Goodbye!
echo.
exit /b 0
