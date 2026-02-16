# Hybrid Trading Bot - Quick Setup

## What You Now Have

✅ **FastAPI Backend** - Unified API for both Deriv and MetaTrader 5
✅ **Kivy Mobile App** - Full-featured Android APK
✅ **Web Dashboard** - Original Dash interface (unchanged)
✅ **Hybrid Broker Support** - Automatic fallback between brokers
✅ **Cloud Ready** - Docker setup for deployment

---

## 5-Minute Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Brokers (Choose One or Both)

**Option A: Deriv Only**
```bash
# Create .env file
echo DERIV_TOKEN=your_token_here > .env
```

**Option B: MetaTrader 5 Only**
```bash
# MT5 will auto-detect from your installed terminal
# Or set in mobile app settings
```

**Option C: Both (Hybrid)**
```bash
# .env file
DERIV_TOKEN=your_token_here
MT5_LOGIN=your_login
MT5_PASSWORD=your_password
MT5_SERVER=your_server
```

### 3. Start Backend Server

```bash
python backend/main.py
```

You'll see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. Test Backend

In a new terminal:
```bash
curl http://localhost:8000/api/broker/status
```

Response:
```json
{"connected": false, "active_broker": null}
```

### 5. Start Mobile App (Development)

```bash
python mobile/trading_bot_app.py
```

Or build APK:
```bash
buildozer android debug
```

---

## Mobile App Usage

### First Time Setup
1. **Settings** → Configure broker (Deriv token / MT5 credentials)
2. Tap **Connect**
3. Dashboard shows account balance

### Place a Trade
1. **Trading** tab
2. Select symbol (frxEURUSD, R_100, etc.)
3. Set direction, prices, and stake
4. Tap **Place Order**

### Monitor Trades
1. **Orders** tab - See all open positions
2. **Dashboard** - Real-time balance and P&L
3. **Markets** - Live price data

---

## Web Dashboard (Original)

Still works as before:
```bash
python app.py
# Visit http://localhost:8050
```

---

## Build APK for Production

```bash
# Debug APK (for testing)
buildozer android debug

# Release APK (for Play Store)
buildozer android release

# Install on phone
adb install bin/tradingbot-0.1-debug.apk
```

---

## Deploy to Cloud

### Option 1: Docker (Recommended)

```bash
# Build
docker build -t trading-bot .

# Run with environment variables
docker run -p 8000:8000 \
  -e DERIV_TOKEN=your_token \
  trading-bot

# Or use Docker Compose
docker-compose up -d
```

### Option 2: Heroku

```bash
heroku create your-app-name
heroku config:set DERIV_TOKEN=your_token
git push heroku main
```

### Option 3: VPS (Digital Ocean, AWS, etc.)

```bash
ssh user@your_server
git clone your_repo
cd trading-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
nohup python backend/main.py > bot.log 2>&1 &
```

---

## Architecture

### Backend Flow

```
Mobile/Web Client
       ↓
   FastAPI API
       ↓
  HybridBroker
    ↙      ↘
Deriv   MetaTrader 5
```

### Key Features

- **Automatic Failover**: If Deriv disconnects, switches to MT5
- **Unified API**: Same API regardless of broker
- **Real-time WebSocket**: Live market data streaming
- **Cross-Platform**: Works on Windows, Mac, Linux, Android

---

## API Examples

### Configure Broker

```bash
curl -X POST http://localhost:8000/api/broker/configure \
  -H "Content-Type: application/json" \
  -d '{
    "primary_broker": "deriv",
    "fallback_broker": "mt5",
    "deriv_token": "your_token",
    "mt5_login": 12345,
    "mt5_password": "password",
    "mt5_server": "ICMarkets-Demo"
  }'
```

### Place Order

```bash
curl -X POST http://localhost:8000/api/orders/place \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "frxEURUSD",
    "direction": "BUY",
    "entry_price": 1.0850,
    "stake": 10,
    "stop_loss": 1.0800,
    "take_profit": 1.0900
  }'
```

### Get Market Data

```bash
curl http://localhost:8000/api/market/data/frxEURUSD
```

Response:
```json
{
  "symbol": "frxEURUSD",
  "bid": 1.08523,
  "ask": 1.08533,
  "timestamp": "2024-02-03T12:34:56"
}
```

---

## File Overview

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI server |
| `backend/broker_connector.py` | Broker implementations |
| `mobile/trading_bot_app.py` | Kivy mobile app |
| `app.py` | Original Dash web UI |
| `TradingAIBot.py` | Original trading bot logic |
| `buildozer.spec` | APK build config |
| `docker-compose.yml` | Docker deployment |

---

## Next Steps

1. ✅ **Test Locally**: Run backend + mobile app on your computer
2. ✅ **Configure Brokers**: Add your API credentials
3. ✅ **Build APK**: Create Android app
4. ✅ **Deploy Backend**: Choose cloud hosting option
5. ✅ **Go Live**: Point mobile app to live server

---

## Troubleshooting

**Mobile can't connect to backend?**
- Check backend is running: `curl http://localhost:8000/api/broker/status`
- Verify firewall allows port 8000
- Use phone IP instead of localhost: `http://192.168.x.x:8000`

**Broker connection fails?**
- Verify API token/credentials in settings
- Check broker account is active
- Ensure internet connection is working

**APK build fails?**
- Install Java: https://www.oracle.com/java/technologies/downloads/
- Install Android SDK/NDK via Android Studio
- Run: `buildozer android clean && buildozer android debug`

---

## Support Files

📄 **Detailed Guides:**
- `APK_BUILD_GUIDE.md` - Complete build & deployment instructions
- `DEPLOYMENT.md` - Production deployment strategy
- `ENHANCEMENTS.md` - Feature roadmap

**Total Setup Time:** ~15 minutes ⚡
