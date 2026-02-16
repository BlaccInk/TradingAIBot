# Trading Bot Configuration Examples

## Default Configuration (BotConfig class)

The bot uses a dataclass-based configuration system that can be customized:

### Technical Indicator Settings
```python
rsi_period: int = 14              # RSI period for overbought/oversold
atr_period: int = 14              # ATR period for volatility measurement
adx_period: int = 14              # ADX period for trend strength
bb_period: int = 20               # Bollinger Bands period
```

### Trading Risk Settings
```python
risk_percent: float = 0.01        # Risk 1% of account balance per trade
rr_ratio: float = 3.0             # Risk-to-Reward ratio (1:3)
sentiment_threshold: float = 0.5  # Sentiment filter threshold
```

### API & Cache Settings
```python
app_id: int = 1089                # Deriv app ID
token: str = "<YOUR_TOKEN>"       # Deriv API token
news_api_key: str = ""            # NewsAPI.org key
news_cache_minutes: int = 60      # Cache sentiment for 60 minutes
min_candles: int = 60             # Minimum candles required for analysis
check_interval: int = 60          # Check signals every 60 seconds
```

## Multi-Pair Configuration

### Forex Major Pairs (4 pairs)
```
frxEURUSD - Euro/US Dollar
frxGBPUSD - British Pound/US Dollar
frxUSDJPY - US Dollar/Japanese Yen
frxUSDCHF - US Dollar/Swiss Franc
```

### Forex Exotic Pairs (4 pairs)
```
frxEURZAR - Euro/South African Rand
frxGBPZAR - British Pound/South African Rand
frxUSDZAR - US Dollar/South African Rand
frxEURNZD - Euro/New Zealand Dollar
```

### Synthetic Pairs (4 pairs)
```
R_100      - Volatility Index 100
R_50       - Volatility Index 50
VOLATILITY_25INDEX  - Volatility 25 Index
VOLATILITY_50INDEX  - Volatility 50 Index
```

### Indices (6 pairs)
```
AS_INDEX   - Australian Stock Index
HK_INDEX   - Hong Kong Stock Index
DE_INDEX   - German Stock Index
JP_INDEX   - Japanese Stock Index
ES_INDEX   - US Stock Index (S&P 500)
UK_INDEX   - UK Stock Index
```

### Commodities & Metals (2 pairs)
```
XAUUSD     - Gold/US Dollar
XAGUSD     - Silver/US Dollar
```

## Customization Examples

### 1. Trade Only Forex Majors (Conservative)
```python
trading_pairs: List[str] = field(default_factory=lambda: [
    "frxEURUSD", "frxGBPUSD", "frxUSDJPY", "frxUSDCHF",
])
```

### 2. High-Risk Configuration
```python
risk_percent: float = 0.05        # 5% risk per trade
rr_ratio: float = 5.0             # Higher reward target
rsi_period: int = 9               # Faster RSI
```

### 3. Conservative Configuration
```python
risk_percent: float = 0.005       # 0.5% risk per trade
rr_ratio: float = 2.0             # Lower reward target
sentiment_threshold: float = 0.7  # Stronger sentiment required
adx_period: int = 21              # Stronger trend requirement
```

### 4. Volatile Instruments Only
```python
trading_pairs: List[str] = field(default_factory=lambda: [
    "R_100", "R_50", "VOLATILITY_25INDEX", "VOLATILITY_50INDEX",
    "XAUUSD", "XAGUSD",
])
check_interval: int = 30          # Check more frequently
```

### 5. Metals & Indices Only
```python
trading_pairs: List[str] = field(default_factory=lambda: [
    "XAUUSD", "XAGUSD",
    "AS_INDEX", "HK_INDEX", "DE_INDEX", "JP_INDEX", "ES_INDEX", "UK_INDEX",
])
```

## Environment Variable Override

You can also set values via .env file:
```
DERIV_APP_ID=1089
DERIV_TOKEN=your_token_here
NEWS_API_KEY=your_newsapi_key
```

## How to Modify Configuration

### Option 1: Edit .env file (Recommended)
Edit `.env` for credentials and non-technical parameters

### Option 2: Modify BotConfig in code
For technical parameters, edit the BotConfig dataclass:
```python
@dataclass
class BotConfig:
    # Your custom defaults here
    risk_percent: float = 0.02  # Changed from 0.01
    rsi_period: int = 9         # Changed from 14
```

### Option 3: Runtime Configuration
Pass custom config when initializing:
```python
config = BotConfig()
config.risk_percent = 0.02
bot = DerivTradingBot(config)
```

## Recommended Starting Settings

### For Beginners
- Start with 1-3 pairs (EURUSD, GBPUSD)
- Risk: 0.5% per trade
- Reward: 1:2 ratio
- Check interval: 300 seconds

### For Intermediate
- 6-8 pairs mixed asset classes
- Risk: 1% per trade
- Reward: 1:3 ratio
- Check interval: 60 seconds

### For Advanced
- 15+ pairs (all available)
- Risk: 1-2% per trade
- Reward: 1:4 ratio
- Check interval: 30 seconds

## Performance Optimization

### To Reduce API Calls
- Increase `check_interval` (60 → 120 seconds)
- Increase `news_cache_minutes` (60 → 120 minutes)
- Reduce number of `trading_pairs`

### To Increase Signal Frequency
- Decrease `check_interval` (60 → 30 seconds)
- Use lower `rsi_period` (14 → 9)
- Decrease `sentiment_threshold` (0.5 → 0.3)

### To Increase Trade Quality
- Increase `adx_period` (14 → 21)
- Increase `sentiment_threshold` (0.5 → 0.7)
- Add more pairs for diversification
