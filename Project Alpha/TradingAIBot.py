import asyncio
import pandas as pd
import talib
from deriv_api import DerivAPI, DerivAPILoggedOutError, DerivAPIError
import time
import requests
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field
import json
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- LOGGING CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- CONFIGURATION CLASS ---
@dataclass
class BotConfig:
    """Configuration for the Trading Bot"""
    app_id: int = int(os.getenv('DERIV_APP_ID', 1089))
    token: str = os.getenv('DERIV_TOKEN', '<YOUR_TOKEN_HERE>')
    rsi_period: int = 14
    atr_period: int = 14
    adx_period: int = 14
    bb_period: int = 20
    rr_ratio: float = 3.0
    risk_percent: float = 0.01
    news_api_key: str = os.getenv('NEWS_API_KEY', '')
    sentiment_threshold: float = 0.5
    news_cache_minutes: int = 60
    min_candles: int = 60
    check_interval: int = 60
    
    # Multi-pair configuration
    trading_pairs: List[str] = field(default_factory=lambda: [
        # Forex Major Pairs
        "frxEURUSD", "frxGBPUSD", "frxUSDJPY", "frxUSDCHF",
        # Forex Exotic Pairs
        "frxEURZAR", "frxGBPZAR", "frxUSDZAR", "frxEURNZD",
        # Synthetic Pairs
        "R_100", "R_50", "VOLATILITY_25INDEX", "VOLATILITY_50INDEX",
        # Indices
        "AS_INDEX", "HK_INDEX", "DE_INDEX", "JP_INDEX", "ES_INDEX", "UK_INDEX",
        # Commodities & Metals
        "XAUUSD", "XAGUSD",
    ])

# --- TRADE HISTORY & PERFORMANCE TRACKING ---
@dataclass
class TradeRecord:
    """Record of a single trade"""
    timestamp: datetime
    symbol: str
    direction: str  # "BULLISH" or "BEARISH"
    entry_price: float
    stake: float
    stop_loss: float
    take_profit: float
    status: str = "OPEN"  # "OPEN", "WON", "LOST", "CANCELLED"
    exit_price: Optional[float] = None
    exit_timestamp: Optional[datetime] = None
    profit_loss: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'symbol': self.symbol,
            'direction': self.direction,
            'entry_price': self.entry_price,
            'stake': self.stake,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'status': self.status,
            'exit_price': self.exit_price,
            'exit_timestamp': self.exit_timestamp.isoformat() if self.exit_timestamp else None,
            'profit_loss': self.profit_loss
        }


class DerivTradingBot:
    """Multi-pair trading bot with sentiment analysis and advanced pattern detection"""
    
    def __init__(self, config: BotConfig):
        """Initialize the trading bot
        
        Args:
            config: BotConfig object with all settings
        """
        self.config = config
        self.api: Optional[DerivAPI] = None
        self.bias: Dict[str, str] = {}  # Bias per symbol
        self.stakes: Dict[str, float] = {}  # Dynamic stake per symbol
        self.trade_history: List[TradeRecord] = []
        self.last_sentiment_check: Optional[datetime] = None
        self.cached_sentiment: float = 0.0
        logger.info(f"Trading Bot initialized with {len(config.trading_pairs)} pairs")

    async def get_market_sentiment(self) -> float:
        """Fetch and analyze market sentiment with caching
        
        Returns:
            float: Sentiment score from -1.0 to +1.0
        """
        # Return cached sentiment if fresh
        if self.last_sentiment_check:
            time_diff = datetime.now() - self.last_sentiment_check
            if time_diff.total_seconds() < self.config.news_cache_minutes * 60:
                logger.debug(f"Using cached sentiment: {self.cached_sentiment:.2f}")
                return self.cached_sentiment
        
        try:
            if not self.config.news_api_key:
                logger.warning("News API key not configured, using neutral sentiment")
                return 0.0
            
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": "stock market forex",
                "language": "en",
                "sortBy": "publishedAt",
                "apiKey": self.config.news_api_key,
                "pageSize": 10,
            }
            response = requests.get(url, params, timeout=10)
            articles = response.json().get("articles", [])

            if not articles:
                logger.warning("No articles found for sentiment analysis")
                return 0.0
            
            # Simple sentiment analysis based on keywords
            positive_keywords = ['bullish', 'surge', 'gain', 'rally', 'growth', 'up']
            negative_keywords = ['bearish', 'decline', 'loss', 'fall', 'crash', 'down']
            
            compound_score = 0
            for article in articles:
                title = article['title'].lower()
                for keyword in positive_keywords:
                    if keyword in title:
                        compound_score += 0.5
                for keyword in negative_keywords:
                    if keyword in title:
                        compound_score -= 0.5
            
            avg_sentiment = compound_score / len(articles)
            avg_sentiment = max(-1.0, min(1.0, avg_sentiment))  # Clamp to [-1, 1]
            
            self.cached_sentiment = avg_sentiment
            self.last_sentiment_check = datetime.now()
            
            logger.info(f"Market Sentiment Updated: {avg_sentiment:.2f}")
            return avg_sentiment
        
        except Exception as e:
            logger.error(f"Error fetching sentiment: {e}")
            return 0.0

    async def calculate_dynamic_stake(self, symbol: str, risk_percent: Optional[float] = None) -> float:
        """Calculate position size based on account balance and risk percentage
        
        Args:
            symbol: Trading symbol
            risk_percent: Risk percentage (uses config default if None)
            
        Returns:
            float: Calculated stake amount
        """
        try:
            if risk_percent is None:
                risk_percent = self.config.risk_percent
            
            account_status = await self.api.balance()
            balance = account_status['balance']['balance']

            stake = round(balance * risk_percent, 2)
            
            if stake < 1.0:
                stake = 1.0

            self.stakes[symbol] = stake
            logger.info(f"[{symbol}] Balance: ${balance:.2f}, Stake: ${stake:.2f}")
            return stake

        except Exception as e:
            logger.error(f"Error calculating stake: {e}")
            if symbol not in self.stakes:
                self.stakes[symbol] = 1.0
            return self.stakes[symbol]

    async def connect(self) -> None:
        """Connect and authorize to Deriv API"""
        try:
            self.api = DerivAPI(app_id=self.config.app_id)
            await self.api.authorize(self.config.token)
            logger.info("Connected and Authorized to Deriv")
        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise

    async def get_candles(self, symbol: str, granularity: int, count: int) -> Optional[pd.DataFrame]:
        """Fetch historical candle data
        
        Args:
            symbol: Trading symbol
            granularity: Time period in seconds
            count: Number of candles to fetch
            
        Returns:
            Optional[pd.DataFrame]: Candle data or None on error
        """
        try:
            payload = {
                "ticks_history": symbol,
                "count": count,
                "end": "latest",
                "granularity": granularity,
                "style": "candles"
            }
            res = await self.api.ticks_history(payload)
            
            if 'candles' not in res or not res['candles']:
                logger.warning(f"[{symbol}] No candle data received")
                return None
            
            df = pd.DataFrame(res['candles'])
            for col in ['open', 'high', 'low', 'close']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.dropna()
            
            if len(df) < self.config.min_candles:
                logger.warning(f"[{symbol}] Insufficient candles: {len(df)}")
                return None
                
            return df
        except Exception as e:
            logger.error(f"[{symbol}] Error fetching candles: {e}")
            return None
    
    async def update_symbol_bias(self, symbol: str) -> None:
        """Update trend bias for a symbol using monthly candles
        
        Args:
            symbol: Trading symbol
        """
        try:
            df = await self.get_candles(symbol, 25920000, 2)  # Monthly
            if df is None or len(df) < 1:
                logger.warning(f"[{symbol}] Could not determine bias")
                self.bias[symbol] = "NEUTRAL"
                return
            
            last = df.iloc[-1]
            self.bias[symbol] = "BULLISH" if last['close'] > last['open'] else "BEARISH"
            logger.info(f"[{symbol}] Bias: {self.bias[symbol]}")
        except Exception as e:
            logger.error(f"[{symbol}] Error updating bias: {e}")
            self.bias[symbol] = "NEUTRAL"

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            pd.DataFrame: DataFrame with indicators
        """
        try:
            df['RSI'] = talib.RSI(df['close'], timeperiod=self.config.rsi_period)
            df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=self.config.atr_period)
            df['ADX'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=self.config.adx_period)
            df['BB_upper'], df['BB_middle'], df['BB_lower'] = talib.BBANDS(
                df['close'], timeperiod=self.config.bb_period, nbdevup=2, nbdevdn=2, matype=0
            )
            df = df.dropna()
            return df
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return df
        
    def calculate_atr_limits(self, df: pd.DataFrame, symbol: str) -> Tuple[float, float]:
        """Calculate stop loss and take profit based on ATR
        
        Args:
            df: DataFrame with ATR indicator
            symbol: Trading symbol
            
        Returns:
            Tuple[float, float]: (stop_loss_pips, take_profit_pips)
        """
        try:
            stake = self.stakes.get(symbol, 1.0)
            sl_amount = stake
            tp_amount = stake * self.config.rr_ratio
            return sl_amount, tp_amount
        except Exception as e:
            logger.error(f"[{symbol}] Error calculating limits: {e}")
            return 0.0, 0.0
    
    def detect_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect bullish and bearish candlestick patterns
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            pd.DataFrame: DataFrame with pattern indicators
        """
        try:
            # Reversal Patterns
            df['Bullish_Engulfing'] = talib.CDLENGULFING(df['open'], df['high'], df['low'], df['close'])
            df['Bearish_Engulfing'] = talib.CDLENGULFING(df['open'], df['high'], df['low'], df['close']) * -1
            df['Hammer'] = talib.CDLHAMMER(df['open'], df['high'], df['low'], df['close'])
            df['Shooting_Star'] = talib.CDLSHOOTINGSTAR(df['open'], df['high'], df['low'], df['close']) * -1
            df['Piercing_Line'] = talib.CDLPIERCING(df['open'], df['high'], df['low'], df['close'])
            df['DarkCloud'] = talib.CDLDARKCLOUDCOVER(df['open'], df['high'], df['low'], df['close']) * -1
            
            # Other patterns
            df['Morning_Star'] = talib.CDLMORNINGSTAR(df['open'], df['high'], df['low'], df['close'])
            df['Evening_Star'] = talib.CDLEVENINGSTAR(df['open'], df['high'], df['low'], df['close']) * -1
            df['Three_White_Soldiers'] = talib.CDL3WHITESOLDIERS(df['open'], df['high'], df['low'], df['close'])
            df['Three_Black_Crows'] = talib.CDL3BLACKCROWS(df['open'], df['high'], df['low'], df['close']) * -1
            
            return df
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return df
    def save_trade(self, trade: TradeRecord) -> None:
        """Save trade to history and file
        
        Args:
            trade: TradeRecord to save
        """
        self.trade_history.append(trade)
        try:
            with open('trade_history.json', 'a') as f:
                f.write(json.dumps(trade.to_dict()) + '\n')
            logger.info(f"Trade saved: {trade.symbol} - {trade.direction}")
        except Exception as e:
            logger.error(f"Error saving trade: {e}")

    def get_performance_metrics(self) -> Dict:
        """Calculate performance metrics from trade history
        
        Returns:
            Dict: Performance metrics
        """
        if not self.trade_history:
            return {"total_trades": 0, "win_rate": 0, "total_profit": 0}
        
        closed_trades = [t for t in self.trade_history if t.status in ['WON', 'LOST']]
        won_trades = [t for t in closed_trades if t.status == 'WON']
        
        total_profit = sum(t.profit_loss for t in closed_trades if t.profit_loss)
        win_rate = len(won_trades) / len(closed_trades) if closed_trades else 0
        
        return {
            "total_trades": len(closed_trades),
            "win_rate": f"{win_rate * 100:.2f}%",
            "total_profit": f"${total_profit:.2f}",
            "open_trades": len(self.trade_history) - len(closed_trades)
        }

    async def run_multi_pair_strategy(self) -> None:
        """Main strategy loop for scanning multiple pairs
        
        Monitors all configured pairs for signals and executes trades
        """
        logger.info(f"Starting multi-pair strategy for {len(self.config.trading_pairs)} pairs")
        
        while True:
            try:
                # Get sentiment once per loop (cached for efficiency)
                current_sentiment = await self.get_market_sentiment()
                
                # Scan all pairs
                for symbol in self.config.trading_pairs:
                    try:
                        await self.process_symbol(symbol, current_sentiment)
                    except Exception as e:
                        logger.error(f"[{symbol}] Error processing: {e}")
                        continue
                
                # Log performance every hour
                if len(self.trade_history) % 10 == 0 and self.trade_history:
                    metrics = self.get_performance_metrics()
                    logger.info(f"Performance Metrics: {metrics}")
                
                await asyncio.sleep(self.config.check_interval)
                
            except Exception as e:
                logger.error(f"Error in strategy loop: {e}")
                await asyncio.sleep(10)

    async def process_symbol(self, symbol: str, sentiment: float) -> None:
        """Process a single symbol for trading signals
        
        Args:
            symbol: Trading symbol to analyze
            sentiment: Current market sentiment score
        """
        # Fetch and analyze data
        df_15min = await self.get_candles(symbol, 900, self.config.min_candles)
        if df_15min is None or len(df_15min) < 2:
            return
        
        df_15min = self.detect_patterns(df_15min)
        df_15min = self.calculate_indicators(df_15min)
        last_row = df_15min.iloc[-1]
        
        # Get symbol bias
        if symbol not in self.bias:
            await self.update_symbol_bias(symbol)
        
        current_bias = self.bias.get(symbol, "NEUTRAL")
        
        # Signal detection with confluence
        signal_found = False
        signal_type = None
        
        if current_bias == "BULLISH":
            bullish_patterns = [
                last_row.get('Morning_Star', 0) > 0,
                last_row.get('Hammer', 0) > 0,
                last_row.get('Bullish_Engulfing', 0) > 0,
                last_row.get('Piercing_Line', 0) > 0,
                last_row.get('Three_White_Soldiers', 0) > 0,
            ]
            
            # Confluence: Pattern + Trend + Sentiment
            if any(bullish_patterns):
                if sentiment > -self.config.sentiment_threshold:  # Not too bearish
                    if last_row.get('RSI', 50) < 70:  # Not overbought
                        if last_row.get('ADX', 0) > 25:  # Strong trend
                            signal_found = True
                            signal_type = "BULLISH"
        
        elif current_bias == "BEARISH":
            bearish_patterns = [
                last_row.get('Evening_Star', 0) < 0,
                last_row.get('Shooting_Star', 0) < 0,
                last_row.get('Bearish_Engulfing', 0) < 0,
                last_row.get('DarkCloud', 0) < 0,
                last_row.get('Three_Black_Crows', 0) < 0,
            ]
            
            if any(bearish_patterns):
                if sentiment < self.config.sentiment_threshold:  # Not too bullish
                    if last_row.get('RSI', 50) > 30:  # Not oversold
                        if last_row.get('ADX', 0) > 25:  # Strong trend
                            signal_found = True
                            signal_type = "BEARISH"
        
        # Execute trade if signal found
        if signal_found and signal_type:
            if symbol not in self.stakes:
                await self.calculate_dynamic_stake(symbol)
            
            sl, tp = self.calculate_atr_limits(df_15min, symbol)
            await self.execute_trade(symbol, signal_type, sl, tp)
            await asyncio.sleep(900)  # Avoid double entries

    async def execute_trade(self, symbol: str, direction: str, sl: float, tp: float) -> None:
        """Execute a trade with proper error handling and retry logic
        
        Args:
            symbol: Trading symbol
            direction: "BULLISH" or "BEARISH"
            sl: Stop loss amount
            tp: Take profit amount
        """
        try:
            stake = self.stakes.get(symbol, 1.0)
            
            # Get current price for entry
            df = await self.get_candles(symbol, 60, 1)
            if df is None or len(df) < 1:
                logger.warning(f"[{symbol}] Could not get entry price")
                return
            
            entry_price = df.iloc[-1]['close']
            
            # Create trade record
            trade = TradeRecord(
                timestamp=datetime.now(),
                symbol=symbol,
                direction=direction,
                entry_price=entry_price,
                stake=stake,
                stop_loss=sl,
                take_profit=tp
            )
            
            # Attempt to get proposal
            try:
                proposal = await self.api.proposal({
                    "proposal": 1,
                    "amount": stake,
                    "symbol": symbol,
                    "contract_type": "CALL" if direction == "BULLISH" else "PUT",
                    "currency": "USD",
                    "multiplier": 1
                })
                
                proposal_id = proposal['proposal']['id']
                ask_price = proposal['proposal']['ask_price']
                
                # Execute trade
                buy_res = await self.api.buy({
                    "buy": proposal_id,
                    "price": ask_price,
                    "limit_order": {
                        "stop_loss": sl,
                        "take_profit": tp
                    }
                })
                
                trade.status = "OPEN"
                self.save_trade(trade)
                logger.info(f"[{symbol}] Trade Executed - {direction} at {entry_price:.4f}")
                
            except DerivAPILoggedOutError:
                logger.warning("API session expired, reconnecting...")
                await self.connect()
            except DerivAPIError as e:
                logger.error(f"[{symbol}] Deriv API Error: {e}")
            except Exception as e:
                logger.error(f"[{symbol}] Trade execution error: {e}")
                
        except Exception as e:
            logger.error(f"[{symbol}] Unexpected error during trade: {e}")


async def main() -> None:
    """Main entry point for the trading bot
    
    Initializes the bot, connects to API, and starts the multi-pair strategy
    """
    config = BotConfig()
    
    logger.info("=" * 60)
    logger.info("Trading Bot Starting")
    logger.info(f"Monitoring {len(config.trading_pairs)} trading pairs")
    logger.info("=" * 60)
    
    bot = DerivTradingBot(config)
    
    try:
        await bot.connect()
        
        # Initialize all symbols
        logger.info("Initializing symbols...")
        for symbol in config.trading_pairs:
            try:
                await bot.calculate_dynamic_stake(symbol)
                await bot.update_symbol_bias(symbol)
                await asyncio.sleep(0.1)  # Rate limiting
            except Exception as e:
                logger.error(f"[{symbol}] Failed to initialize: {e}")
        
        logger.info("Bot ready. Starting strategy...")
        await bot.run_multi_pair_strategy()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        if bot.api:
            try:
                await bot.api.close()
                logger.info("API connection closed")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
        
        # Log final performance
        metrics = bot.get_performance_metrics()
        logger.info("=" * 60)
        logger.info("Final Performance Metrics:")
        for key, value in metrics.items():
            logger.info(f"{key}: {value}")
        logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())