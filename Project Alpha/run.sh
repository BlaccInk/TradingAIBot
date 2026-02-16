#!/bin/bash

# Trading Bot Startup Script for Linux/Mac
# This script helps you run the entire system

show_menu() {
    clear
    echo ""
    echo "============================================================"
    echo "         Trading Bot - Hybrid System Launcher"
    echo "============================================================"
    echo ""
    echo "Select what to run:"
    echo ""
    echo "1. Start Backend Server (FastAPI)"
    echo "2. Start Mobile App (Kivy)"
    echo "3. Start Web Dashboard (Dash)"
    echo "4. Run All (3 terminals)"
    echo "5. Build APK"
    echo "6. Test API Connection"
    echo "7. Install Dependencies"
    echo "8. Exit"
    echo ""
    read -p "Enter your choice (1-8): " choice
    
    case $choice in
        1) start_backend ;;
        2) start_mobile ;;
        3) start_web ;;
        4) run_all ;;
        5) build_apk ;;
        6) test_api ;;
        7) install_deps ;;
        8) exit 0 ;;
        *) echo "Invalid choice. Please try again." && sleep 1 && show_menu ;;
    esac
}

start_backend() {
    echo ""
    echo "Starting Backend Server..."
    echo ""
    python3 backend/main.py
}

start_mobile() {
    echo ""
    echo "Starting Mobile App (Kivy)..."
    echo ""
    python3 mobile/trading_bot_app.py
}

start_web() {
    echo ""
    echo "Starting Web Dashboard (Dash)..."
    echo ""
    python3 app.py
}

run_all() {
    echo ""
    echo "Starting all components..."
    echo ""
    
    # Check if terminal supports split or tabs
    if command -v gnome-terminal &> /dev/null; then
        # GNOME Terminal
        gnome-terminal -- bash -c "cd $(pwd) && python3 backend/main.py; bash" &
        sleep 2
        gnome-terminal -- bash -c "cd $(pwd) && python3 mobile/trading_bot_app.py; bash" &
        sleep 2
        gnome-terminal -- bash -c "cd $(pwd) && python3 app.py; bash" &
    elif command -v konsole &> /dev/null; then
        # KDE Konsole
        konsole --new-tab -e bash -c "cd $(pwd) && python3 backend/main.py" &
        sleep 2
        konsole --new-tab -e bash -c "cd $(pwd) && python3 mobile/trading_bot_app.py" &
        sleep 2
        konsole --new-tab -e bash -c "cd $(pwd) && python3 app.py" &
    elif command -v xterm &> /dev/null; then
        # X Terminal
        xterm -e "cd $(pwd) && python3 backend/main.py" &
        sleep 2
        xterm -e "cd $(pwd) && python3 mobile/trading_bot_app.py" &
        sleep 2
        xterm -e "cd $(pwd) && python3 app.py" &
    else
        # Fallback: Just run sequentially
        echo "Terminal multiplexer not found. Running sequentially..."
        echo "Press Ctrl+C after each component to start the next one."
        echo ""
        python3 backend/main.py &
        BACKEND_PID=$!
        sleep 2
        
        python3 mobile/trading_bot_app.py &
        MOBILE_PID=$!
        sleep 2
        
        python3 app.py &
        WEB_PID=$!
        
        echo ""
        echo "All components started!"
        echo ""
        echo "Backend:   http://localhost:8000"
        echo "Dashboard: http://localhost:8050"
        echo ""
        echo "Press Ctrl+C to stop all processes..."
        wait
    fi
}

build_apk() {
    echo ""
    echo "Building APK..."
    echo ""
    echo "This will take 5-10 minutes on first build."
    echo ""
    
    buildozer android debug
    
    echo ""
    echo "APK build complete!"
    echo "Location: bin/tradingbot-0.1-debug.apk"
    echo ""
    read -p "Press Enter to continue..."
    show_menu
}

test_api() {
    echo ""
    echo "Testing API Connection..."
    echo ""
    
    python3 << EOF
import requests
import json
import sys

try:
    response = requests.get('http://localhost:8000/api/broker/status', timeout=5)
    print('Backend Status: CONNECTED ✓')
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print('Backend Status: DISCONNECTED ✗')
    print(f'Error: {e}')
    print()
    print('Make sure to start the backend server first:')
    print('  python3 backend/main.py')
EOF
    
    echo ""
    read -p "Press Enter to continue..."
    show_menu
}

install_deps() {
    echo ""
    echo "Installing Python Dependencies..."
    echo ""
    
    pip3 install --upgrade pip
    pip3 install -r requirements.txt --upgrade
    
    echo ""
    echo "Installation complete!"
    echo ""
    read -p "Press Enter to continue..."
    show_menu
}

# Make script executable
chmod +x "$0"

# Run main menu loop
while true; do
    show_menu
done
