# Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies (2 min)
```bash
pip install -r requirements.txt
```

### Step 2: Configure Credentials (2 min)
1. Open `.env` file
2. Add your Deriv API token:
   ```
   DERIV_TOKEN=your_actual_token_here
   ```
3. (Optional) Add NewsAPI key for sentiment:
   ```
   NEWS_API_KEY=your_newsapi_key_here
   ```

### Step 3: Run the Bot (1 min)
```bash
python TradingAIBot.py
```

You should see:
```
============================================================
Trading Bot Starting
Monitoring 18 trading pairs
============================================================
Initializing symbols...
Bot ready. Starting strategy...
```

## What the Bot Does

1. **Monitors 18 trading pairs** (Forex, Synthetics, Indices, Metals)
2. **Analyzes market sentiment** from news (hourly, cached)
3. **Detects candlestick patterns** (Morning Star, Engulfing, etc.)
4. **Calculates technical indicators** (RSI, ATR, ADX, Bollinger Bands)
5. **Executes trades** when multiple signals align
6. **Tracks performance** automatically

## Check Logs

Open `trading_bot.log` to see:
- When trades are opened/closed
- Sentiment scores
- Performance metrics
- Any errors

Example log entry:
```
2026-02-01 10:45:23 - __main__ - INFO - [frxEURUSD] Trade Executed - BULLISH at 1.0850
2026-02-01 10:46:15 - __main__ - INFO - Market Sentiment Updated: 0.65
```

## View Trade History

`trade_history.json` contains all executed trades:
```json
{"timestamp": "2026-02-01T10:45:23", "symbol": "frxEURUSD", "direction": "BULLISH", "entry_price": 1.0850, "stake": 50.0, "status": "OPEN"}
```

## Stop the Bot

Press `Ctrl+C` in the terminal. Bot will:
1. Stop accepting new trades
2. Log final performance metrics
3. Close API connection
4. Save all trade data

## Troubleshooting

### Bot won't start?
```
ERROR: ModuleNotFoundError: No module named 'talib'
```
**Solution**: Run `pip install TA-Lib` (requires specific setup on Windows)

### No trades executing?
- Check `trading_bot.log` for errors
- Verify API token in `.env` is valid
- Ensure account has sufficient balance
- Check sentiment score in logs

### API authentication failed?
```
ERROR: DerivAPILoggedOutError
```
**Solution**: 
1. Generate new API token from https://app.deriv.com/account/api-token
2. Update `.env` with new token
3. Restart bot

### Slow performance?
- Reduce number of pairs in `BotConfig`
- Increase `check_interval` from 60 to 120 seconds
- Disable sentiment analysis: set `NEWS_API_KEY=""` in `.env`

## Next Steps

1. **Test on Demo Account First**
   - Use demo trading account to verify bot works correctly
   - Run for 24-48 hours before live trading

2. **Adjust Risk Settings**
   - Edit `risk_percent` in `.env` or code
   - Start with 0.5% per trade for safety

3. **Customize Trading Pairs**
   - Edit `trading_pairs` in BotConfig
   - See CONFIGURATION.md for examples

4. **Monitor Performance**
   - Review logs daily
   - Check trade_history.json for results
   - Adjust indicators if needed

## Key Files

| File | Purpose |
|------|---------|
| `TradingAIBot.py` | Main bot code |
| `.env` | Configuration (credentials) |
| `trading_bot.log` | Activity logs |
| `trade_history.json` | All executed trades |
| `README.md` | Full documentation |
| `CONFIGURATION.md` | Advanced settings |

## Safety Checklist

- [ ] Tested bot on demo account for 24+ hours
- [ ] Started with small position sizes (0.5-1%)
- [ ] Set API token with restricted permissions
- [ ] Monitor logs regularly
- [ ] Have stop-loss protection enabled
- [ ] Keep `.env` file secret (don't commit to git)

## Support

Check logs in this order:
1. `trading_bot.log` - Search for ERROR or WARN
2. `trade_history.json` - Review recent trades
3. Terminal output - See real-time messages

## Emergency Stop

If anything goes wrong:
1. Press `Ctrl+C` to stop bot immediately
2. Log in to https://app.deriv.com to close any open trades
3. Review `trading_bot.log` to understand what happened
4. Fix configuration and restart

---

**Happy Trading! Remember: Start small, test thoroughly, monitor carefully.** 🚀
