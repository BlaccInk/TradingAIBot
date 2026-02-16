"""
FastAPI Backend for Trading Bot
Supports Deriv, MT5, Exness, and XM brokers
Includes Market Scanner
"""
from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import asyncio
import logging
import os
from dotenv import load_dotenv
import json

from backend.broker_connector import (
    HybridBroker, DerivBroker, MT5Broker, BrokerConfig, 
    BrokerType, Order, MarketData
)

load_dotenv()

app = FastAPI(
    title="Trading Bot API",
    description="Hybrid broker API with Market Scanning",
    version="1.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
broker: Optional[HybridBroker] = None
active_connections: List[WebSocket] = []
scanner_task: Optional[asyncio.Task] = None
scanned_symbols: List[str] = []
signals: List[Dict] = []


# ============ Pydantic Models ============

class BrokerConfigRequest(BaseModel):
    primary_broker: str
    fallback_broker: Optional[str] = None
    deriv_token: Optional[str] = None
    mt5_login: Optional[int] = None
    mt5_password: Optional[str] = None
    mt5_server: Optional[str] = None

class OrderRequest(BaseModel):
    symbol: str
    direction: str
    entry_price: float
    stake: float
    stop_loss: float
    take_profit: float

class ScannerConfigRequest(BaseModel):
    symbols: List[str]
    interval: int = 60 # seconds

# ============ Scanner Logic ============

async def market_scanner():
    """Background task to scan markets for signals"""
    global signals
    while True:
        try:
            if broker and broker.active_broker and scanned_symbols:
                new_signals = []
                for symbol in scanned_symbols:
                    # Simplified EMA Crossover Strategy for demo
                    history = await broker.get_history(symbol, timeframe=60, count=50)
                    if len(history) >= 20:
                        closes = [h['close'] for h in history]
                        ema8 = sum(closes[-8:]) / 8
                        ema20 = sum(closes[-20:]) / 20

                        prev_ema8 = sum(closes[-9:-1]) / 8
                        prev_ema20 = sum(closes[-21:-1]) / 20

                        if prev_ema8 <= prev_ema20 and ema8 > ema20:
                            new_signals.append({
                                "symbol": symbol,
                                "type": "BUY",
                                "reason": "EMA 8 crossed above EMA 20",
                                "timestamp": datetime.now().isoformat()
                            })
                        elif prev_ema8 >= prev_ema20 and ema8 < ema20:
                            new_signals.append({
                                "symbol": symbol,
                                "type": "SELL",
                                "reason": "EMA 8 crossed below EMA 20",
                                "timestamp": datetime.now().isoformat()
                            })

                signals = new_signals
                if signals:
                    await notify_clients({"type": "scanner_update", "signals": signals})

            await asyncio.sleep(60) # Scan every minute
        except Exception as e:
            logger.error(f"Scanner error: {e}")
            await asyncio.sleep(10)

# ============ API Endpoints ============

@app.on_event("startup")
async def startup_event():
    global scanner_task
    scanner_task = asyncio.create_task(market_scanner())

@app.get("/api/market/symbols")
async def get_symbols():
    if not broker: return []
    return await broker.get_all_symbols()

@app.post("/api/scanner/configure")
async def configure_scanner(config: ScannerConfigRequest):
    global scanned_symbols
    scanned_symbols = config.symbols
    return {"status": "success", "scanning": scanned_symbols}

@app.get("/api/scanner/signals")
async def get_signals():
    return signals

def create_broker_instance(broker_type_str: str, config: BrokerConfigRequest):
    if broker_type_str == "deriv":
        token = config.deriv_token or os.getenv("DERIV_TOKEN")
        if not token: raise ValueError("Deriv token not provided")
        return DerivBroker(token)
    elif broker_type_str in ["mt5", "exness", "xm"]:
        if not all([config.mt5_login, config.mt5_password, config.mt5_server]):
            raise ValueError(f"{broker_type_str.upper()} credentials incomplete")
        b_type = BrokerType.MT5
        if broker_type_str == "exness": b_type = BrokerType.EXNESS
        elif broker_type_str == "xm": b_type = BrokerType.XM
        return MT5Broker(config.mt5_login, config.mt5_password, config.mt5_server, b_type)
    raise ValueError(f"Unknown broker: {broker_type_str}")

@app.post("/api/broker/configure")
async def configure_broker(config: BrokerConfigRequest):
    global broker
    try:
        primary = create_broker_instance(config.primary_broker.lower(), config)
        fallback = None
        if config.fallback_broker and config.fallback_broker != "none":
            fallback = create_broker_instance(config.fallback_broker.lower(), config)
        broker = HybridBroker(primary, fallback)
        if await broker.connect():
            return {"success": True, "message": "Broker configured"}
        raise ConnectionError("Failed to connect")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/broker/status")
async def get_broker_status():
    if not broker: return {"connected": False}
    balance = await broker.get_balance()
    return {
        "connected": broker.active_broker is not None,
        "active_broker": broker.get_active_broker_type().value if broker.active_broker else None,
        "balance": balance
    }

@app.get("/api/account/balance")
async def get_balance():
    if not broker: raise HTTPException(status_code=400, detail="Not connected")
    return {"balance": await broker.get_balance()}

@app.get("/api/orders/open")
async def get_open_orders():
    if not broker: return []
    orders = await broker.get_open_orders()
    return [{"order_id": o.order_id, "symbol": o.symbol, "direction": o.direction, "stake": o.stake} for o in orders]

@app.post("/api/orders/place")
async def place_order(order_req: OrderRequest):
    if not broker: raise HTTPException(status_code=400, detail="Not connected")
    order = Order(
        symbol=order_req.symbol, direction=order_req.direction,
        entry_price=order_req.entry_price, stake=order_req.stake,
        stop_loss=order_req.stop_loss, take_profit=order_req.take_profit,
        broker_type=broker.get_active_broker_type()
    )
    success, res = await broker.place_order(order)
    return {"success": success, "order_id": res if success else None, "message": res}

@app.post("/api/orders/close/{order_id}")
async def close_order(order_id: str):
    if not broker: raise HTTPException(status_code=400, detail="Not connected")
    success, msg = await broker.close_order(order_id)
    return {"success": success, "message": msg}

async def notify_clients(message: Dict):
    for connection in active_connections:
        try: await connection.send_json(message)
        except: pass

@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True: await websocket.receive_text()
    except: active_connections.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
