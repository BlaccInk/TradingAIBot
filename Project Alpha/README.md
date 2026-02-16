# Trading AI Bot - Enhanced Multi-Pair Version

A comprehensive async trading bot that monitors multiple trading pairs including Forex, Synthetic, Indices, Equities, and Metals with sentiment analysis and advanced pattern detection.

## Features

### ✅ Multi-Pair Scanning
- **Forex Major Pairs**: EURUSD, GBPUSD, USDJPY, USDCHF
- **Forex Exotic Pairs**: EURZAR, GBPZAR, USDZAR, EURNZD
- **Synthetic Pairs**: R_100, R_50, VOLATILITY_25INDEX, VOLATILITY_50INDEX
- **Indices**: AS_INDEX, HK_INDEX, DE_INDEX, JP_INDEX, ES_INDEX, UK_INDEX
- **Commodities & Metals**: XAUUSD (Gold), XAGUSD (Silver)

### ✅ Enhanced Features
- **Logging System**: Comprehensive logging to file and console
- **Trade History Tracking**: All trades recorded in JSON format
- **Performance Metrics**: Win rate, total profit, open trades calculation
- **Sentiment Caching**: News sentiment analyzed once per hour for efficiency
- **Environment Configuration**: Credentials and settings via `.env` file
- **Type Hints**: Full type hints throughout the codebase
- **Comprehensive Documentation**: Docstrings for all methods
- **Error Handling**: Robust error handling with retry logic
- **Multi-Symbol Monitoring**: Simultaneous scanning of all pairs

### ✅ Trading Logic
- **Confluence-Based Entry**: Combines bias + patterns + indicators + sentiment
- **Candlestick Patterns**: Morning Star, Evening Star, Engulfing, Hammer, Shooting Star, etc.
- **Technical Indicators**: RSI, ATR, ADX, Bollinger Bands
- **Dynamic Position Sizing**: Based on account balance and risk percentage
- **Stop Loss & Take Profit**: Automatic calculation based on ATR and risk/reward ratio

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Edit `.env` file with your credentials:
```
DERIV_APP_ID=your_app_id
DERIV_TOKEN=your_token_here
NEWS_API_KEY=your_newsapi_key
```

### 3. Get API Keys
- **Deriv API**: https://app.deriv.com/account/api-token
- **News API**: https://newsapi.org

### 4. Run the Bot
```bash
python TradingAIBot.py
```

## Configuration

Edit the `BotConfig` dataclass in `TradingAIBot.py` to customize:
- `rsi_period`, `atr_period`, `adx_period`, `bb_period`: Technical indicator periods
- `rr_ratio`: Risk-to-reward ratio (default 3.0 = 1:3)
- `risk_percent`: Risk per trade as % of balance (default 0.01 = 1%)
- `sentiment_threshold`: Sentiment score threshold (-1 to 1)
- `news_cache_minutes`: How often to fetch new sentiment data
- `check_interval`: How often to check for signals (seconds)
- `trading_pairs`: List of symbols to monitor

## Output Files

### Logs
- `trading_bot.log`: Complete trading activity log

### Trade History
- `trade_history.json`: All executed trades with entry/exit details

## Trading Signals

### Bullish Entry (BULLISH Bias)
- ✅ Morning Star, Hammer, Bullish Engulfing, Piercing Line, or Three White Soldiers pattern
- ✅ ADX > 25 (strong trend)
- ✅ RSI < 70 (not overbought)
- ✅ Sentiment not too bearish
- ✅ Price confluences (multiple signals align)

### Bearish Entry (BEARISH Bias)
- ✅ Evening Star, Shooting Star, Bearish Engulfing, Dark Cloud Cover, or Three Black Crows
- ✅ ADX > 25 (strong trend)
- ✅ RSI > 30 (not oversold)
- ✅ Sentiment not too bullish
- ✅ Price confluences (multiple signals align)

## Performance Metrics

The bot logs performance metrics including:
- Total trades executed
- Win rate percentage
- Total profit/loss
- Open trades count

View metrics in `trading_bot.log` or at bot shutdown.

## Architecture

### Core Components
1. **BotConfig**: Configuration management with environment variables
2. **TradeRecord**: Dataclass for tracking individual trades
3. **DerivTradingBot**: Main bot class with all trading logic
4. **Logging**: Structured logging for debugging and monitoring

### Key Methods
- `run_multi_pair_strategy()`: Main loop monitoring all pairs
- `process_symbol()`: Analyzes single symbol for signals
- `execute_trade()`: Places trade with proper risk management
- `get_market_sentiment()`: Analyzes market sentiment from news

## Risk Management

- **Dynamic Position Sizing**: Automatically adjusts stake based on account balance
- **Stop Loss & Take Profit**: Set automatically based on ATR
- **Sentiment Filter**: Prevents trading against market sentiment
- **Pattern Confluence**: Requires multiple signals before trading
- **Trade History**: Full audit trail of all decisions

## Troubleshooting

### No trades executing?
- Check logs in `trading_bot.log`
- Verify API credentials in `.env`
- Ensure sufficient account balance
- Check sentiment score and pattern signals

### API Connection Issues?
- Verify DERIV_TOKEN is valid and not expired
- Check internet connection
- Review error logs

### Slow performance?
- Reduce number of trading pairs
- Increase `check_interval` in config
- Increase `news_cache_minutes` for less frequent sentiment checks

## Safety Notice

⚠️ **DISCLAIMER**: This bot trades with real money. Use at your own risk.
- Start with small position sizes
- Test on demo account first
- Monitor bot activity regularly
- Never leave bot unattended for extended periods

## License

Proprietary - Use only with explicit permission
