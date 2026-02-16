# API Testing & Debugging Guide

## Quick API Testing

### Using cURL

#### 1. Check Broker Status
```bash
curl http://localhost:8000/api/broker/status
```

Expected response (not connected):
```json
{
  "connected": false,
  "primary_broker": null,
  "active_broker": null,
  "balance": null
}
```

#### 2. Configure Deriv Broker
```bash
curl -X POST http://localhost:8000/api/broker/configure \
  -H "Content-Type: application/json" \
  -d '{
    "primary_broker": "deriv",
    "fallback_broker": null,
    "deriv_token": "your_token_here"
  }'
```

Response (success):
```json
{
  "success": true,
  "message": "Broker configured successfully",
  "primary": "deriv",
  "fallback": null
}
```

#### 3. Get Account Balance
```bash
curl http://localhost:8000/api/account/balance
```

Response:
```json
{
  "balance": 5000.50,
  "broker_type": "deriv"
}
```

#### 4. Get Market Data
```bash
curl http://localhost:8000/api/market/data/frxEURUSD
```

Response:
```json
{
  "symbol": "frxEURUSD",
  "bid": 1.08523,
  "ask": 1.08533,
  "high": 1.08750,
  "low": 1.08400,
  "close": 1.08500,
  "timestamp": "2024-02-03T12:34:56",
  "broker_type": "deriv"
}
```

#### 5. Get Historical Data
```bash
curl "http://localhost:8000/api/market/history/frxEURUSD?timeframe=60&count=10"
```

Response:
```json
{
  "symbol": "frxEURUSD",
  "data": [
    {
      "open": 1.08400,
      "high": 1.08750,
      "low": 1.08350,
      "close": 1.08500,
      "volume": 1000,
      "time": "2024-02-03T11:00:00"
    },
    ...
  ]
}
```

#### 6. Place an Order
```bash
curl -X POST http://localhost:8000/api/orders/place \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "frxEURUSD",
    "direction": "BUY",
    "entry_price": 1.08523,
    "stake": 10,
    "stop_loss": 1.08400,
    "take_profit": 1.08650
  }'
```

Response (success):
```json
{
  "success": true,
  "order_id": "12345678",
  "message": "Order placed"
}
```

#### 7. Get Open Orders
```bash
curl http://localhost:8000/api/orders/open
```

Response:
```json
[
  {
    "order_id": "12345678",
    "symbol": "frxEURUSD",
    "direction": "BUY",
    "entry_price": 1.08523,
    "stake": 10,
    "stop_loss": 1.08400,
    "take_profit": 1.08650,
    "status": "OPEN",
    "timestamp": "2024-02-03T12:00:00"
  }
]
```

#### 8. Close an Order
```bash
curl -X POST http://localhost:8000/api/orders/close/12345678
```

Response:
```json
{
  "success": true,
  "order_id": "12345678",
  "message": "Order closed"
}
```

---

## Using Python Requests

### Example Script

```python
import requests
import json

API_URL = "http://localhost:8000/api"

class TradingBotClient:
    def __init__(self, api_url=API_URL):
        self.api_url = api_url
        self.session = requests.Session()
    
    def configure_broker(self, primary, deriv_token=None, 
                        mt5_login=None, mt5_password=None, 
                        mt5_server=None, fallback=None):
        """Configure broker connection"""
        data = {
            "primary_broker": primary,
            "fallback_broker": fallback,
            "deriv_token": deriv_token,
            "mt5_login": mt5_login,
            "mt5_password": mt5_password,
            "mt5_server": mt5_server,
        }
        response = self.session.post(
            f"{self.api_url}/broker/configure",
            json=data
        )
        return response.json()
    
    def get_status(self):
        """Get broker status"""
        response = self.session.get(f"{self.api_url}/broker/status")
        return response.json()
    
    def get_balance(self):
        """Get account balance"""
        response = self.session.get(f"{self.api_url}/account/balance")
        return response.json()
    
    def get_market_data(self, symbol):
        """Get current market data"""
        response = self.session.get(
            f"{self.api_url}/market/data/{symbol}"
        )
        return response.json()
    
    def get_history(self, symbol, timeframe=60, count=100):
        """Get historical data"""
        response = self.session.get(
            f"{self.api_url}/market/history/{symbol}",
            params={"timeframe": timeframe, "count": count}
        )
        return response.json()
    
    def place_order(self, symbol, direction, entry_price, 
                   stake, stop_loss, take_profit):
        """Place a trading order"""
        data = {
            "symbol": symbol,
            "direction": direction,
            "entry_price": entry_price,
            "stake": stake,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
        }
        response = self.session.post(
            f"{self.api_url}/orders/place",
            json=data
        )
        return response.json()
    
    def get_open_orders(self):
        """Get all open orders"""
        response = self.session.get(f"{self.api_url}/orders/open")
        return response.json()
    
    def close_order(self, order_id):
        """Close an order"""
        response = self.session.post(
            f"{self.api_url}/orders/close/{order_id}"
        )
        return response.json()


# Usage Example
if __name__ == "__main__":
    client = TradingBotClient()
    
    # Configure Deriv
    print("Configuring broker...")
    result = client.configure_broker(
        primary="deriv",
        deriv_token="your_token_here"
    )
    print(json.dumps(result, indent=2))
    
    # Check status
    print("\nBroker status:")
    status = client.get_status()
    print(json.dumps(status, indent=2))
    
    if status['connected']:
        # Get balance
        print("\nAccount balance:")
        balance = client.get_balance()
        print(json.dumps(balance, indent=2))
        
        # Get market data
        print("\nMarket data for EURUSD:")
        data = client.get_market_data("frxEURUSD")
        print(json.dumps(data, indent=2))
        
        # Get history
        print("\nHistorical data:")
        history = client.get_history("frxEURUSD", timeframe=60, count=5)
        print(json.dumps(history, indent=2))
        
        # Place order
        print("\nPlacing test order...")
        order = client.place_order(
            symbol="frxEURUSD",
            direction="BUY",
            entry_price=1.08523,
            stake=10,
            stop_loss=1.08400,
            take_profit=1.08650
        )
        print(json.dumps(order, indent=2))
        
        if order['success']:
            order_id = order['order_id']
            
            # Get open orders
            print("\nOpen orders:")
            orders = client.get_open_orders()
            print(json.dumps(orders, indent=2))
            
            # Close order
            print(f"\nClosing order {order_id}...")
            close_result = client.close_order(order_id)
            print(json.dumps(close_result, indent=2))
```

---

## WebSocket Real-time Data

### Using Python

```python
import asyncio
import websockets
import json

async def listen_market_data(symbol):
    """Listen to real-time market data via WebSocket"""
    uri = f"ws://localhost:8000/ws/market/{symbol}"
    
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {symbol} stream")
        
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                print(f"{data['symbol']}: Bid={data['bid']}, Ask={data['ask']}")
            except Exception as e:
                print(f"Error: {e}")
                break

# Run
asyncio.run(listen_market_data("frxEURUSD"))
```

### Using JavaScript (Browser/Node.js)

```javascript
const socket = new WebSocket('ws://localhost:8000/ws/market/frxEURUSD');

socket.addEventListener('open', (event) => {
    console.log('Connected to market data stream');
});

socket.addEventListener('message', (event) => {
    const data = JSON.parse(event.data);
    console.log(`${data.symbol}: Bid=${data.bid}, Ask=${data.ask}`);
});

socket.addEventListener('close', (event) => {
    console.log('Disconnected from stream');
});
```

---

## Error Responses

### Common Errors

#### 400 - Bad Request
```json
{
  "detail": "Broker not connected"
}
```
**Solution:** Configure broker first

#### 404 - Not Found
```json
{
  "detail": "Failed to get data for frxXXXXXX"
}
```
**Solution:** Check symbol name is correct

#### 422 - Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "stake"],
      "msg": "value is not a valid number",
      "type": "type_error.float"
    }
  ]
}
```
**Solution:** Check parameter types and values

---

## Debugging Tips

### Enable Debug Logging

```python
# In backend/main.py
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

### Check Server Logs

```bash
# If running directly
python backend/main.py

# If using Docker
docker logs -f trading-bot-api

# If using Heroku
heroku logs --tail
```

### Test Connectivity

```bash
# Ping server
curl -i http://localhost:8000/api/broker/status

# Check if CORS is working
curl -i -X OPTIONS http://localhost:8000/api/broker/status \
  -H "Origin: http://localhost:3000"

# Test with timeout
curl --max-time 5 http://localhost:8000/api/broker/status
```

### Monitor WebSocket Connections

```bash
# Using wscat (npm install -g wscat)
wscat -c ws://localhost:8000/ws/market/frxEURUSD
```

---

## Performance Testing

### Load Testing with Apache Bench

```bash
# Install: apt-get install apache2-utils

# Test market data endpoint
ab -n 100 -c 10 http://localhost:8000/api/market/data/frxEURUSD

# Results show:
# Requests per second
# Mean time per request
# Response times
```

### Using wrk (Modern alternative)

```bash
# Install: https://github.com/wg/wrk

wrk -t4 -c100 -d30s http://localhost:8000/api/broker/status
```

---

## Broker-Specific Testing

### Testing Deriv Connection

```python
from backend.broker_connector import DerivBroker

async def test_deriv():
    broker = DerivBroker("your_token")
    
    # Test connection
    connected = await broker.connect()
    print(f"Connected: {connected}")
    
    # Get balance
    balance = await broker.get_balance()
    print(f"Balance: {balance}")
    
    # Get market data
    data = await broker.get_market_data("frxEURUSD")
    print(f"EURUSD: {data}")
    
    await broker.disconnect()

# Run test
import asyncio
asyncio.run(test_deriv())
```

### Testing MetaTrader 5 Connection

```python
from backend.broker_connector import MT5Broker

async def test_mt5():
    broker = MT5Broker(
        login=123456,
        password="password",
        server="ICMarkets-Demo"
    )
    
    # Test connection
    connected = await broker.connect()
    print(f"Connected: {connected}")
    
    # Get balance
    balance = await broker.get_balance()
    print(f"Balance: {balance}")
    
    # Get market data
    data = await broker.get_market_data("EURUSD")
    print(f"EURUSD: {data}")
    
    await broker.disconnect()

# Run test
import asyncio
asyncio.run(test_mt5())
```

---

## Integration Testing Checklist

- [ ] Backend starts without errors
- [ ] API responds to requests
- [ ] Deriv connection works
- [ ] MT5 connection works (if available)
- [ ] Market data retrieves correctly
- [ ] Orders place successfully
- [ ] Orders close successfully
- [ ] Balance updates correctly
- [ ] WebSocket sends real-time data
- [ ] Mobile app connects to API
- [ ] Web dashboard works

---

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Connection refused" | Backend not running | `python backend/main.py` |
| "Broker not connected" | No broker configured | Call `/broker/configure` first |
| "Failed to get data" | Invalid symbol | Use correct symbol name |
| "Order failed" | Insufficient balance | Add funds to broker account |
| "WebSocket timeout" | Network issue | Check firewall, try localhost |
| 503 Service Unavailable | Server overloaded | Restart or scale horizontally |

---

**Ready to test your trading bot!** 🚀
