# APK Build & Deployment Guide

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│        CLOUD BACKEND (FastAPI)              │
│  - Deriv Broker Integration                 │
│  - MetaTrader 5 Integration                 │
│  - Hybrid Fallback Support                  │
└────────┬────────────────────────────────┬───┘
         │                                │
    ┌────▼──────┐              ┌──────────▼──────┐
    │   WEB UI  │              │    MOBILE APP   │
    │  (Dash)   │              │    (Kivy APK)   │
    │  Existing │              │   New Native    │
    └───────────┘              └─────────────────┘
```

## Quick Start - Build APK

### Prerequisites

**On Windows:**
```bash
# Install Java Development Kit (JDK 11+)
# Download from: https://www.oracle.com/java/technologies/downloads/

# Install Android SDK & NDK
# Download Android Studio: https://developer.android.com/studio

# Set environment variables
setx JAVA_HOME "C:\Program Files\Java\jdk-11"
setx ANDROID_SDK_ROOT "C:\Android\sdk"
setx ANDROID_NDK_ROOT "C:\Android\ndk\27.0.11902837"
```

**On Linux/Mac:**
```bash
# Install JDK
sudo apt-get install openjdk-11-jdk  # Ubuntu/Debian
brew install openjdk@11              # Mac

# Install Android SDK/NDK (via Android Studio or command line tools)
```

### Step 1: Install Build Tools

```bash
pip install buildozer cython

# Windows-specific
pip install buildozer --upgrade

# Install garden for Kivy
garden install matplotlib
```

### Step 2: Configure buildozer.spec

The `buildozer.spec` file is pre-configured. Key sections:

```ini
[app]
title = Trading AI Bot
package.name = tradingbot
python_version = 3.11
requirements = python3,kivy,requests,pillow,matplotlib

[app:android]
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.minapi = 21
android.targetapi = 33
android.archs = arm64-v8a,armeabi-v7a
```

### Step 3: Build APK

```bash
# Navigate to project directory
cd c:\Users\BlaccPrideSA\Project Alpha

# Build debug APK (faster)
buildozer android debug

# Build release APK (sign with key)
buildozer android release

# Clean build
buildozer android clean
buildozer android debug
```

**Build Output:**
- Debug APK: `bin/tradingbot-0.1-debug.apk`
- Release APK: `bin/tradingbot-0.1-release.apk`

### Step 4: Deploy to Phone

**Via ADB (Android Debug Bridge):**

```bash
# List connected devices
adb devices

# Install APK
adb install bin/tradingbot-0.1-debug.apk

# View logs
adb logcat -s python
```

**Manually:**
- Copy APK file to phone
- Open file manager → tap APK → install

---

## Server Deployment (Cloud)

### Option 1: Docker Deployment

```bash
# Build Docker image
docker build -t trading-bot .

# Run container locally
docker run -p 8000:8000 \
  -e DERIV_TOKEN="your_token" \
  -e MT5_LOGIN="your_login" \
  -e MT5_PASSWORD="your_password" \
  -e MT5_SERVER="your_server" \
  trading-bot

# Using Docker Compose
docker-compose up -d
```

### Option 2: Heroku Deployment

```bash
# Install Heroku CLI
brew install heroku  # Mac
# or download from https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create Heroku app
heroku create your-trading-bot

# Set environment variables
heroku config:set DERIV_TOKEN="your_token"
heroku config:set MT5_LOGIN="your_login"
heroku config:set MT5_PASSWORD="your_password"
heroku config:set MT5_SERVER="your_server"

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

**Procfile** (already created):
```
web: python backend/main.py
```

### Option 3: AWS/DigitalOcean/VPS

```bash
# SSH to server
ssh user@your_server_ip

# Clone repository
git clone https://github.com/your-repo/trading-bot.git
cd trading-bot

# Setup Python environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DERIV_TOKEN="your_token"
export MT5_LOGIN="your_login"
export MT5_PASSWORD="your_password"
export MT5_SERVER="your_server"

# Run with gunicorn/supervisor for persistence
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 backend.main:app
```

---

## Mobile App Configuration

### Connect to Remote Server

1. Open Trading Bot app on phone
2. Go to **Settings** tab
3. Update **API URL** (if needed):
   - Local: `http://192.168.x.x:8000/api`
   - Remote: `https://your-domain.com/api`
4. Enter broker credentials
5. Tap **Connect**

### Local Development (No Server)

The mobile app can run with a local Python server:

```bash
# Start backend locally
python backend/main.py

# On mobile, connect to:
# http://YOUR_COMPUTER_IP:8000/api

# Find your IP:
ipconfig  # Windows
ifconfig  # Mac/Linux
```

---

## Broker Setup

### Deriv API

1. Create account: https://deriv.com
2. Get API token:
   - Go to Settings → API Tokens
   - Create new token with scopes: `read`, `trade`, `admin`
3. Add to `.env` or settings:
   ```
   DERIV_TOKEN=your_token_here
   ```

### MetaTrader 5

1. Install MetaTrader 5: https://www.metatrader5.com/
2. Create trading account
3. Enable MQL5 API in terminal settings
4. Get credentials:
   - Login ID
   - Password
   - Server name (e.g., "ICMarkets-Demo")
5. Add to settings in mobile app

---

## Architecture Details

### File Structure

```
Project Alpha/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── broker_connector.py     # Hybrid broker implementation
│   └── __init__.py
├── mobile/
│   └── trading_bot_app.py      # Kivy mobile app
├── app.py                      # Original Dash web UI
├── TradingAIBot.py             # Original trading logic
├── buildozer.spec              # APK build configuration
├── Dockerfile                  # Docker container config
├── docker-compose.yml          # Docker Compose config
├── requirements.txt            # Python dependencies
└── .env                        # Environment variables
```

### API Endpoints

**Broker Management:**
- `POST /api/broker/configure` - Configure broker connection
- `GET /api/broker/status` - Get connection status

**Market Data:**
- `GET /api/market/data/{symbol}` - Current market data
- `GET /api/market/history/{symbol}` - Historical OHLC data

**Orders:**
- `POST /api/orders/place` - Place trade order
- `POST /api/orders/close/{order_id}` - Close order
- `GET /api/orders/open` - Get open orders

**Account:**
- `GET /api/account/balance` - Get account balance

**WebSocket:**
- `WS /ws/market/{symbol}` - Real-time market data stream

### Hybrid Broker Logic

The system supports simultaneous connections to both Deriv and MetaTrader 5:

```python
# Primary: Deriv, Fallback: MT5
broker = HybridBroker(
    primary=DerivBroker(token),
    fallback=MT5Broker(login, password, server)
)

# If Deriv disconnects, automatically switches to MT5
await broker.connect()
```

---

## Troubleshooting

### APK Build Issues

**Problem:** Gradle build fails
```bash
# Clean and rebuild
buildozer android clean
buildozer android debug --debug
```

**Problem:** "Java not found"
```bash
# Set JAVA_HOME
export JAVA_HOME=/path/to/java  # Linux/Mac
setx JAVA_HOME "path\to\java"   # Windows
```

**Problem:** NDK not found
```bash
# Edit buildozer.spec
android.ndk = /path/to/android-ndk
```

### Connection Issues

**Mobile can't reach backend:**
```bash
# Check backend is running
curl http://localhost:8000/api/broker/status

# Verify firewall allows port 8000
# Check mobile has internet permission in AndroidManifest.xml
```

**Broker won't connect:**
```bash
# Verify credentials
# Check API token is valid
# Ensure broker API is accessible from network
```

### Performance Issues

- **Optimize for mobile:** Reduce update frequency in settings
- **Use cloud backend:** Offload processing from phone
- **Enable lite mode:** Dashboard shows essential data only

---

## Next Steps

1. **Test locally first:**
   ```bash
-  python backend/main.py
-  python mobile/trading_bot_app.py
+  # To run the mobile app, execute the following command in your terminal:
+  # python mobile/trading_bot_app.py
+
+  # To run the backend server, execute the following command in your terminal:
+  # python backend/main.py
   ```

2. **Deploy backend to cloud:** Choose Docker, Heroku, or VPS

3. **Update mobile app API URL** to point to cloud server

4. **Build APK** for production

5. **Sign APK** for Play Store distribution (optional)

---

## Support & Monitoring

### Logs

**Backend:**
```bash
# Docker
docker logs -f trading-bot-api

# Direct run
tail -f trading_bot.log
```

**Mobile:**
```bash
adb logcat -s python
```

### Health Checks

```bash
# API health
curl http://localhost:8000/api/broker/status

# Market data
curl http://localhost:8000/api/market/data/frxEURUSD
```

### Scaling

For production with multiple users:
- Use load balancer (Nginx, HAProxy)
- Database for persistent order history
- Redis for caching market data
- Kubernetes for auto-scaling

See `DEPLOYMENT.md` for advanced configuration.
