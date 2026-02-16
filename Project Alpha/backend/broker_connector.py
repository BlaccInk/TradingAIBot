"""
Hybrid Broker Connector - Supports Deriv, MT5, Exness, and XM
Includes market scanning capabilities
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

try:
    from deriv_api import DerivAPI, DerivAPIError, DerivAPILoggedOutError
except ImportError:
    DerivAPI = None

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

logger = logging.getLogger(__name__)


class BrokerType(Enum):
    DERIV = "deriv"
    MT5 = "mt5"
    EXNESS = "exness"
    XM = "xm"


@dataclass
class BrokerConfig:
    """Configuration for broker connection"""
    broker_type: BrokerType
    api_token: Optional[str] = None  # For Deriv
    mt5_login: Optional[int] = None  # For MT5
    mt5_password: Optional[str] = None
    mt5_server: Optional[str] = None


@dataclass
class Order:
    """Unified order structure across brokers"""
    symbol: str
    direction: str  # "BUY" or "SELL"
    entry_price: float
    stake: float
    stop_loss: float
    take_profit: float
    broker_type: BrokerType
    order_id: Optional[str] = None
    status: str = "PENDING"
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class MarketData:
    """Unified market data structure"""
    symbol: str
    bid: float
    ask: float
    high: float
    low: float
    close: float
    volume: int
    timestamp: datetime
    broker_type: BrokerType


class BrokerInterface(ABC):
    """Abstract base class for broker implementations"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to broker"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from broker"""
        pass
    
    @abstractmethod
    async def get_all_symbols(self) -> List[str]:
        """Get all tradable symbols"""
        pass

    @abstractmethod
    async def get_market_data(self, symbol: str, timeframe: int = 60) -> Optional[MarketData]:
        """Get current market data for symbol"""
        pass
    
    @abstractmethod
    async def get_history(self, symbol: str, timeframe: int = 60, count: int = 100) -> List[Dict]:
        """Get historical OHLC data"""
        pass
    
    @abstractmethod
    async def place_order(self, order: Order) -> Tuple[bool, str]:
        """Place trading order"""
        pass
    
    @abstractmethod
    async def close_order(self, order_id: str) -> Tuple[bool, str]:
        """Close an open order"""
        pass
    
    @abstractmethod
    async def get_balance(self) -> Optional[float]:
        """Get account balance"""
        pass
    
    @abstractmethod
    async def get_open_orders(self) -> List[Order]:
        """Get list of open orders"""
        pass


class DerivBroker(BrokerInterface):
    """Deriv broker implementation"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.deriv_api = None
        self.is_connected = False
    
    async def connect(self) -> bool:
        """Connect to Deriv API"""
        if not DerivAPI:
            logger.error("DerivAPI not installed. Install with: pip install deriv-api")
            return False
        
        try:
            self.deriv_api = DerivAPI(app_id=12345, creds={
                'token': self.api_token
            })
            await self.deriv_api.authorize()
            self.is_connected = True
            logger.info("Connected to Deriv API")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Deriv: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Deriv API"""
        if self.deriv_api:
            await self.deriv_api.disconnect()
            self.is_connected = False
            logger.info("Disconnected from Deriv")
        return True
    
    async def get_all_symbols(self) -> List[str]:
        if not self.is_connected: return []
        try:
            response = await self.deriv_api.get_active_symbols()
            return [s['symbol'] for s in response.get('active_symbols', [])]
        except: return []

    async def get_market_data(self, symbol: str, timeframe: int = 60) -> Optional[MarketData]:
        """Get current market data from Deriv"""
        if not self.is_connected:
            return None
        
        try:
            response = await self.deriv_api.get_tick(symbol)
            tick = response['tick']
            
            return MarketData(
                symbol=symbol,
                bid=tick.get('bid'),
                ask=tick.get('ask'),
                high=tick.get('high'),
                low=tick.get('low'),
                close=tick.get('quote'),
                volume=0,
                timestamp=datetime.fromtimestamp(tick.get('epoch')),
                broker_type=BrokerType.DERIV
            )
        except Exception as e:
            logger.error(f"Error getting market data from Deriv for {symbol}: {e}")
            return None
    
    async def get_history(self, symbol: str, timeframe: int = 60, count: int = 100) -> List[Dict]:
        """Get historical data from Deriv"""
        if not self.is_connected:
            return []
        
        try:
            response = await self.deriv_api.get_candles(
                symbol=symbol,
                granularity=timeframe,
                count=count
            )
            candles = response.get('candles', [])
            
            history = []
            for candle in candles:
                history.append({
                    'open': candle.get('open'),
                    'high': candle.get('high'),
                    'low': candle.get('low'),
                    'close': candle.get('close'),
                    'volume': 0,
                    'time': datetime.fromtimestamp(candle.get('epoch'))
                })
            return history
        except Exception as e:
            logger.error(f"Error getting history from Deriv for {symbol}: {e}")
            return []
    
    async def place_order(self, order: Order) -> Tuple[bool, str]:
        """Place order on Deriv"""
        if not self.is_connected:
            return False, "Not connected"
        
        try:
            contract_type = "CALL" if order.direction == "BUY" else "PUT"
            response = await self.deriv_api.buy_contract(
                contract_type=contract_type,
                currency="USD",
                amount=order.stake,
                symbol=order.symbol,
                duration=1,
                duration_unit="h"
            )
            order_id = response.get('buy', {}).get('contract_id')
            return True, order_id
        except Exception as e:
            logger.error(f"Error placing order on Deriv: {e}")
            return False, str(e)
    
    async def close_order(self, order_id: str) -> Tuple[bool, str]:
        """Close order on Deriv"""
        if not self.is_connected:
            return False, "Not connected"
        
        try:
            await self.deriv_api.close_contract(contract_id=order_id)
            return True, "Order closed"
        except Exception as e:
            logger.error(f"Error closing order on Deriv: {e}")
            return False, str(e)
    
    async def get_balance(self) -> Optional[float]:
        """Get account balance from Deriv"""
        if not self.is_connected:
            return None
        
        try:
            response = await self.deriv_api.get_account_status()
            return response.get('account_status', {}).get('balance')
        except Exception as e:
            logger.error(f"Error getting balance from Deriv: {e}")
            return None
    
    async def get_open_orders(self) -> List[Order]:
        """Get open orders from Deriv"""
        if not self.is_connected:
            return []
        
        try:
            response = await self.deriv_api.get_open_contracts()
            orders = []
            # Parse response and convert to Order objects
            return orders
        except Exception as e:
            logger.error(f"Error getting open orders from Deriv: {e}")
            return []


class MT5Broker(BrokerInterface):
    """MetaTrader 5 broker implementation (Universal for Exness, XM, etc.)"""
    
    def __init__(self, login: int, password: str, server: str, broker_label: BrokerType = BrokerType.MT5):
        self.login = login
        self.password = password
        self.server = server
        self.broker_label = broker_label
        self.is_connected = False
    
    async def connect(self) -> bool:
        """Connect to MetaTrader 5"""
        if not mt5:
            logger.error("MetaTrader5 not installed. Install with: pip install MetaTrader5")
            return False
        
        try:
            if not mt5.initialize(
                path=None,
                login=self.login,
                password=self.password,
                server=self.server,
                timeout=60000
            ):
                logger.error(f"MT5 initialization failed for {self.server}: {mt5.last_error()}")
                return False
            
            self.is_connected = True
            logger.info(f"Connected to {self.broker_label.value.upper()} via MT5: {self.server}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MT5 ({self.server}): {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from MetaTrader 5"""
        if mt5 and self.is_connected:
            mt5.shutdown()
            self.is_connected = False
            logger.info(f"Disconnected from {self.broker_label.value.upper()}")
        return True
    
    async def get_all_symbols(self) -> List[str]:
        if not self.is_connected: return []
        try:
            symbols = mt5.symbols_get()
            return [s.name for s in symbols] if symbols else []
        except: return []

    async def get_market_data(self, symbol: str, timeframe: int = 60) -> Optional[MarketData]:
        """Get current market data from MT5"""
        if not self.is_connected:
            return None
        
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.error(f"Failed to get tick for {symbol}")
                return None
            
            return MarketData(
                symbol=symbol,
                bid=tick.bid,
                ask=tick.ask,
                high=tick.ask,  # MT5 doesn't provide high/low in tick
                low=tick.bid,
                close=tick.last,
                volume=tick.volume,
                timestamp=datetime.fromtimestamp(tick.time),
                broker_type=self.broker_label
            )
        except Exception as e:
            logger.error(f"Error getting market data from MT5 for {symbol}: {e}")
            return None
    
    async def get_history(self, symbol: str, timeframe: int = 60, count: int = 100) -> List[Dict]:
        """Get historical data from MT5"""
        if not self.is_connected:
            return []
        
        try:
            # Convert timeframe to MT5 timeframe
            mt5_timeframes = {
                60: mt5.TIMEFRAME_H1,
                300: mt5.TIMEFRAME_H4,
                3600: mt5.TIMEFRAME_D1,
            }
            tf = mt5_timeframes.get(timeframe, mt5.TIMEFRAME_H1)
            
            rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
            if rates is None:
                logger.error(f"Failed to get rates for {symbol}")
                return []
            
            history = []
            for rate in rates:
                history.append({
                    'open': rate['open'],
                    'high': rate['high'],
                    'low': rate['low'],
                    'close': rate['close'],
                    'volume': rate['tick_volume'],
                    'time': datetime.fromtimestamp(rate['time'])
                })
            return history
        except Exception as e:
            logger.error(f"Error getting history from MT5 for {symbol}: {e}")
            return []
    
    async def place_order(self, order: Order) -> Tuple[bool, str]:
        """Place order on MetaTrader 5"""
        if not self.is_connected:
            return False, "Not connected"
        
        try:
            order_type = mt5.ORDER_TYPE_BUY if order.direction == "BUY" else mt5.ORDER_TYPE_SELL
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": order.symbol,
                "volume": order.stake,
                "type": order_type,
                "price": order.entry_price,
                "sl": order.stop_loss,
                "tp": order.take_profit,
                "comment": f"{self.broker_label.value.upper()} Bot Order",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Order failed: {result.comment}")
                return False, result.comment
            
            return True, str(result.order)
        except Exception as e:
            logger.error(f"Error placing order on MT5: {e}")
            return False, str(e)
    
    async def close_order(self, order_id: str) -> Tuple[bool, str]:
        """Close order on MetaTrader 5"""
        if not self.is_connected:
            return False, "Not connected"
        
        try:
            # Get the position and close it
            result = mt5.order_send({
                "action": mt5.TRADE_ACTION_DEAL,
                "position": int(order_id),
                "type": mt5.ORDER_TYPE_SELL,
                "volume": 0,
            })
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return False, result.comment
            return True, "Order closed"
        except Exception as e:
            logger.error(f"Error closing order on MT5: {e}")
            return False, str(e)
    
    async def get_balance(self) -> Optional[float]:
        """Get account balance from MetaTrader 5"""
        if not self.is_connected:
            return None
        
        try:
            account_info = mt5.account_info()
            if account_info is None:
                return None
            return account_info.balance
        except Exception as e:
            logger.error(f"Error getting balance from MT5: {e}")
            return None
    
    async def get_open_orders(self) -> List[Order]:
        """Get open orders from MetaTrader 5"""
        if not self.is_connected:
            return []
        
        try:
            positions = mt5.positions_get()
            orders = []
            
            if positions:
                for position in positions:
                    order = Order(
                        symbol=position.symbol,
                        direction="BUY" if position.type == mt5.ORDER_TYPE_BUY else "SELL",
                        entry_price=position.price_open,
                        stake=position.volume,
                        stop_loss=position.sl,
                        take_profit=position.tp,
                        broker_type=self.broker_label,
                        order_id=str(position.ticket),
                        status="OPEN",
                        timestamp=datetime.fromtimestamp(position.time)
                    )
                    orders.append(order)
            
            return orders
        except Exception as e:
            logger.error(f"Error getting open orders from MT5: {e}")
            return []


class HybridBroker:
    """
    Unified broker interface supporting both Deriv and MetaTrader 5
    Provides fallback mechanism for hybrid mode
    """
    
    def __init__(self, primary: BrokerInterface, fallback: Optional[BrokerInterface] = None):
        self.primary = primary
        self.fallback = fallback
        self.active_broker = None
    
    async def connect(self) -> bool:
        """Connect to primary broker, fallback if needed"""
        try:
            if await self.primary.connect():
                self.active_broker = self.primary
                logger.info("Connected to primary broker")
                return True
        except Exception as e:
            logger.error(f"Primary broker connection failed: {e}")
        
        if self.fallback:
            try:
                if await self.fallback.connect():
                    self.active_broker = self.fallback
                    logger.warning("Switched to fallback broker")
                    return True
            except Exception as e:
                logger.error(f"Fallback broker connection failed: {e}")
        
        return False
    
    async def disconnect(self) -> bool:
        """Disconnect all brokers"""
        success = True
        if self.primary:
            success &= await self.primary.disconnect()
        if self.fallback:
            success &= await self.fallback.disconnect()
        self.active_broker = None
        return success
    
    async def get_all_symbols(self) -> List[str]:
        if self.active_broker:
            return await self.active_broker.get_all_symbols()
        return []

    async def get_market_data(self, symbol: str, timeframe: int = 60) -> Optional[MarketData]:
        if self.active_broker:
            return await self.active_broker.get_market_data(symbol, timeframe)
        return None
    
    async def get_history(self, symbol: str, timeframe: int = 60, count: int = 100) -> List[Dict]:
        if self.active_broker:
            return await self.active_broker.get_history(symbol, timeframe, count)
        return []
    
    async def place_order(self, order: Order) -> Tuple[bool, str]:
        if self.active_broker:
            return await self.active_broker.place_order(order)
        return False, "No active broker"
    
    async def close_order(self, order_id: str) -> Tuple[bool, str]:
        if self.active_broker:
            return await self.active_broker.close_order(order_id)
        return False, "No active broker"
    
    async def get_balance(self) -> Optional[float]:
        if self.active_broker:
            return await self.active_broker.get_balance()
        return None
    
    async def get_open_orders(self) -> List[Order]:
        if self.active_broker:
            return await self.active_broker.get_open_orders()
        return []
    
    def get_active_broker_type(self) -> Optional[BrokerType]:
        if isinstance(self.active_broker, DerivBroker):
            return BrokerType.DERIV
        elif isinstance(self.active_broker, MT5Broker):
            return self.active_broker.broker_label
        return None
