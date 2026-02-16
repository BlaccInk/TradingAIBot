# Deployment Checklist

## Pre-Deployment Setup

### Account & API Setup
- [ ] Create Deriv account (https://www.deriv.com)
- [ ] Fund account with trading capital
- [ ] Generate API token (https://app.deriv.com/account/api-token)
- [ ] Store token securely in `.env` file
- [ ] Test API connection with small balance

### Dependencies
- [ ] Install Python 3.8+ 
- [ ] Run: `pip install -r requirements.txt`
- [ ] Verify all imports work: `python -c "import talib; print('TA-Lib OK')"`
- [ ] Verify pandas, asyncio, requests installed

### Configuration Files
- [ ] Create/update `.env` file with:
  - [ ] `DERIV_APP_ID` (from API page)
  - [ ] `DERIV_TOKEN` (newly generated)
  - [ ] `NEWS_API_KEY` (optional, from newsapi.org)
- [ ] Review `BotConfig` settings in code
- [ ] Adjust `risk_percent` for your comfort level
- [ ] Adjust `trading_pairs` if needed

### Documentation Review
- [ ] Read `README.md` - Full documentation
- [ ] Read `QUICKSTART.md` - Quick setup guide
- [ ] Read `CONFIGURATION.md` - All available settings
- [ ] Review `ENHANCEMENTS.md` - What was improved

---

## Testing Phase (Do NOT skip this!)

### Demo Account Testing (48+ hours)
- [ ] Run bot on demo account for at least 48 hours
- [ ] Monitor `trading_bot.log` for errors
- [ ] Verify trades are executing properly
- [ ] Check `trade_history.json` for correct data
- [ ] Verify sentiment analysis working
- [ ] Test all 18 trading pairs
- [ ] Check performance metrics

### Monitoring During Testing
- [ ] Watch logs in real-time: `tail -f trading_bot.log`
- [ ] Review trades every hour
- [ ] Verify stop losses are set
- [ ] Check account balance changes
- [ ] Test bot restart/recovery

### Safety Verification
- [ ] Verify API connection stable
- [ ] Test Ctrl+C shutdown gracefully
- [ ] Verify trade history saves
- [ ] Check log file is being written
- [ ] Test with minimum position size

### Signal Quality Check
- [ ] Review signal detection logic
- [ ] Check if patterns detected correctly
- [ ] Verify sentiment scores make sense
- [ ] Confirm bias calculation per symbol
- [ ] Test on known chart patterns

---

## Pre-Live Trading Checklist

### Final Configuration
- [ ] Risk settings appropriate for account size
- [ ] Trading pairs verified (18 default or custom)
- [ ] API credentials correct
- [ ] Check interval set appropriately
- [ ] Sentiment threshold tuned
- [ ] Technical indicator periods confirmed

### Account Preparation
- [ ] Account funded with sufficient capital
- [ ] Account verified (if required by broker)
- [ ] No pending deposits/withdrawals
- [ ] Withdrawal method configured
- [ ] Phone/email verified

### Risk Management Setup
- [ ] Position size calculated: `balance * risk_percent`
- [ ] Stop loss mechanism verified
- [ ] Take profit targets confirmed
- [ ] Daily loss limit considered
- [ ] Maximum open trades defined

### Monitoring Setup
- [ ] Terminal window set up to watch logs
- [ ] `trade_history.json` location known
- [ ] Backup trading platform logged in
- [ ] Phone nearby for emergencies
- [ ] Trading plan documented

### Security
- [ ] `.env` file never committed to Git
- [ ] API token with minimal permissions only
- [ ] No credentials in code
- [ ] Backup of `.env` stored safely
- [ ] Computer secured (firewall, antivirus)

---

## Live Trading Day 1

### Before Starting
- [ ] Read this entire checklist again
- [ ] Verify all files in place:
  - [ ] `TradingAIBot.py`
  - [ ] `.env` (with credentials)
  - [ ] `requirements.txt`
  - [ ] `README.md`, `QUICKSTART.md`
- [ ] Verify Python environment activated
- [ ] Check internet connection stable
- [ ] Clear old log files (optional): `del trading_bot.log`

### Starting the Bot
- [ ] Run: `python TradingAIBot.py`
- [ ] Watch for initialization messages
- [ ] Verify all 18 symbols initializing (or custom count)
- [ ] See "Bot ready. Starting strategy..." message
- [ ] Check initial market sentiment score

### First Hour Monitoring
- [ ] Monitor every 15 minutes
- [ ] Check `trading_bot.log` for any errors
- [ ] Verify API connection staying active
- [ ] Watch for first signal generation
- [ ] See if any trades execute
- [ ] Verify stop losses on open trades

### Day 1 Checkpoints
- [ ] **Hour 1**: No errors, connected, monitoring
- [ ] **Hour 4**: At least checking signals properly
- [ ] **Hour 8**: First trade may have executed
- [ ] **Hour 24**: Multiple data points collected

### What to Watch For
- ❌ API connection errors (STOP and diagnose)
- ❌ Infinite loops or CPU high usage (STOP)
- ❌ Missing trades on obvious signals (review logic)
- ✅ Consistent sentiment scores updating
- ✅ New candles being fetched
- ✅ Proper error recovery

---

## Ongoing Monitoring

### Daily Tasks
- [ ] Check `trading_bot.log` for errors
- [ ] Review open positions in Deriv account
- [ ] Verify bot process still running
- [ ] Check account balance
- [ ] Review new trades in `trade_history.json`

### Weekly Review
- [ ] Calculate weekly profit/loss
- [ ] Review signal quality
- [ ] Check if adjustments needed
- [ ] Analyze trade patterns
- [ ] Compare against benchmarks

### Monthly Review
- [ ] Full performance analysis
- [ ] Win rate calculation
- [ ] Risk-adjusted returns
- [ ] Identify profitable pairs
- [ ] Identify losing pairs
- [ ] Adjust strategy if needed

### Performance Metrics to Track
- Win rate (target: > 50%)
- Average win size
- Average loss size
- Profit factor (wins/losses)
- Risk-adjusted returns
- Maximum drawdown

---

## Troubleshooting During Live Trading

### Bot Won't Start
```
Check:
1. Python installed correctly
2. All packages in requirements.txt installed
3. .env file exists and readable
4. No syntax errors in TradingAIBot.py
Run: python TradingAIBot.py (watch for error messages)
```

### API Connection Failed
```
Check:
1. DERIV_TOKEN in .env is correct
2. Token not expired (generate new one if needed)
3. Internet connection working
4. Deriv servers not down (check status page)
Bot will auto-reconnect, watch logs
```

### No Trades Executing
```
Check:
1. Recent log entries showing sentiment scores
2. Pattern detection finding candlesticks
3. Bias calculated per symbol
4. Check individual trading_bot.log entries
5. Verify all technical indicators calculating
6. May be market conditions unsuitable for signals
```

### Unexpected Large Loss
```
1. IMMEDIATELY check open positions in Deriv account
2. Manually close any positions if needed
3. STOP the bot (Ctrl+C)
4. Review trading_bot.log for what happened
5. Review trade_history.json
6. Do NOT restart until issue identified
```

### High CPU / Resource Usage
```
1. STOP the bot (Ctrl+C)
2. Check if infinite loop in logs
3. Reduce number of trading_pairs
4. Increase check_interval (60 → 120 seconds)
5. Restart with reduced load
```

---

## Emergency Procedures

### Complete Bot Shutdown
```bash
# Press Ctrl+C in terminal
# Or if stuck: 
# Open Task Manager → Find python.exe → End Task
```

### Recover from Crash
```bash
1. Check if account has open positions
2. Manually close any positions in Deriv app
3. Read trading_bot.log to understand crash
4. Fix identified issue
5. Restart with caution
```

### Network Issues
```bash
Bot will:
1. Log warning on API error
2. Attempt to reconnect automatically
3. Retry up to 3 times
4. If persistent, manual restart required
```

### Insufficient Funds
```bash
Bot will:
1. Fail on trade execution
2. Log the error
3. Continue monitoring (no further trades until funded)
Check account balance and fund if needed
```

---

## Success Criteria

### Week 1
- ✅ Zero critical errors
- ✅ Bot running continuously
- ✅ Trades executing per strategy
- ✅ Performance tracking working

### Month 1
- ✅ Win rate > 40%
- ✅ Positive cumulative P&L
- ✅ All 18 pairs monitored successfully
- ✅ No unexpected behavior

### Month 3
- ✅ Win rate > 50%
- ✅ Consistent monthly profits
- ✅ Identified best performing pairs
- ✅ Ready to scale position sizes

---

## When to Stop & Review

**STOP the bot if:**
- ❌ API connection error lasting > 30 minutes
- ❌ Daily loss exceeds planned maximum
- ❌ Unusual market conditions (gap moves, news events)
- ❌ Visible technical issues in logs
- ❌ Account balance too low for minimum stake

**ADJUST settings if:**
- Win rate < 40% for 2+ weeks
- Consecutive losses > 3 trades
- Specific pair consistently losing
- Market volatility changed significantly
- Trading hours changed (different liquidity)

---

## Support & Help

### If Issues Occur
1. Check `trading_bot.log` first
2. Search logs for ERROR or WARN
3. Review `README.md` troubleshooting section
4. Check `ENHANCEMENTS.md` for architecture
5. Review your configuration in `.env`

### Documentation
- `README.md` - Full user guide
- `QUICKSTART.md` - 5-minute setup
- `CONFIGURATION.md` - All settings
- `ENHANCEMENTS.md` - Technical details

### Before Contacting Support
1. Provide last 50 lines of `trading_bot.log`
2. Provide your configuration (without token!)
3. Describe exactly what happened
4. Include any error messages

---

## Final Reminder

⚠️ **This bot trades with real money. Only proceed if you:**
- [ ] Understand trading risks
- [ ] Can afford to lose the capital
- [ ] Have tested extensively on demo
- [ ] Have proper risk management
- [ ] Monitor the bot regularly

**Start small. Scale gradually. Monitor always.**

Good luck with your automated trading! 🚀
