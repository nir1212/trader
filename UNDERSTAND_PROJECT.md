# Understanding Your Trading Bot Project

## 🎯 The Big Picture

```
YOU (configure settings)
  ↓
main.py (starts the bot)
  ↓
Bot (connects to Alpaca/Binance)
  ↓
Strategies (analyze prices)
  ↓
Signals (BUY/SELL/HOLD)
  ↓
Risk Manager (checks if safe)
  ↓
Execute Trade (if approved)
  ↓
Portfolio (tracks your money)
```

## 📁 File Structure Explained

### **Files You'll Use:**

1. **`simple_example.py`** ← START HERE
   - Easiest to understand
   - Shows clear output
   - Analyzes 3 stocks
   - Run: `poetry run python simple_example.py`

2. **`my_first_bot.py`** ← LEARNING
   - Step-by-step guide
   - Explains each part
   - Great for understanding
   - Run: `poetry run python my_first_bot.py`

3. **`examples/backtest_example.py`** ← TEST STRATEGIES
   - Tests on historical data
   - Shows if strategy would have worked
   - No real trading
   - Run: `poetry run python examples/backtest_example.py`

4. **`main.py`** ← FULL BOT
   - Runs continuously
   - Monitors multiple stocks
   - For long-term automated trading
   - Run: `poetry run python main.py`

5. **`config/config.yaml`** ← YOUR SETTINGS
   - Which stocks to trade
   - Which strategies to use
   - Risk management rules
   - Edit this to customize

### **Folders You Should Know:**

```
src/trader/
├── bots/           ← StockBot and CryptoBot (the workers)
├── strategies/     ← Trading strategies (the brains)
├── core/           ← Portfolio, base classes (the foundation)
├── risk/           ← Risk management (the safety guard)
└── utils/          ← Logger, data fetcher (helpers)
```

## 🧠 How Strategies Work

### **Moving Average Crossover**
```
Price chart:
         ___/‾‾‾\___
Fast MA: ___/‾‾‾\___  (10 days)
Slow MA: _____/‾‾‾\_  (30 days)

When fast crosses ABOVE slow = BUY
When fast crosses BELOW slow = SELL
```

### **RSI (Relative Strength Index)**
```
RSI Scale: 0 to 100

0-30:  OVERSOLD → BUY signal
30-70: NEUTRAL → HOLD
70-100: OVERBOUGHT → SELL signal
```

### **MACD**
```
MACD Line vs Signal Line:

MACD crosses above Signal = BUY
MACD crosses below Signal = SELL
```

## 🎮 How to Use the Bot

### **Beginner Path:**

1. **Run simple_example.py** (you just did this!)
   ```bash
   poetry run python simple_example.py
   ```
   - See what the bot does
   - Understand the output

2. **Run backtest_example.py**
   ```bash
   poetry run python examples/backtest_example.py
   ```
   - Test strategies on past data
   - See if they would have worked
   - Check performance metrics

3. **Customize config.yaml**
   - Change which stocks to trade
   - Adjust strategy parameters
   - Modify risk settings

4. **Run main.py for continuous trading**
   ```bash
   poetry run python main.py
   ```
   - Runs every 5 minutes
   - Monitors all your stocks
   - Executes trades automatically

### **What Each File Does:**

| File | What It Does | When to Use |
|------|-------------|-------------|
| `simple_example.py` | Quick test with 3 stocks | Learning, testing |
| `my_first_bot.py` | Detailed walkthrough | Understanding |
| `examples/backtest_example.py` | Test on history | Strategy testing |
| `examples/live_trading_example.py` | Short live session | Quick trading test |
| `main.py` | Full automated bot | Long-term trading |

## 🔧 Customizing Your Bot

### **Change Stocks (config.yaml):**
```yaml
stock_bot:
  symbols:
    - AAPL
    - MSFT
    - GOOGL
    - TSLA    # Add more here
```

### **Change Strategy Parameters:**
```yaml
strategies:
  - name: moving_average_crossover
    params:
      fast_period: 5    # Make it faster (more trades)
      slow_period: 20   # Or slower (fewer trades)
```

### **Change Risk Settings:**
```yaml
risk_management:
  max_position_size: 0.1    # Use 10% per trade
  stop_loss_pct: 0.03       # Stop loss at 3%
  take_profit_pct: 0.08     # Take profit at 8%
```

## 📊 Understanding the Output

### **When you see this:**
```
2024-12-27 11:30:00 - StockBot - INFO - Analyzing AAPL...
```
**Meaning:** Bot is checking Apple stock

### **When you see this:**
```
Moving Average Crossover: BUY AAPL @ $185.50
RSI Strategy: HOLD AAPL @ $185.50
```
**Meaning:** 
- MA strategy says BUY
- RSI strategy says HOLD
- Bot will aggregate (usually HOLD if mixed)

### **When you see this:**
```
[SIMULATION] Would execute: BUY AAPL @ $185.50
```
**Meaning:** In paper trading mode, simulating the trade

### **When you see this:**
```
Portfolio Value: $10,523.45
P&L: $523.45 (5.23%)
```
**Meaning:** You made $523 profit (5.23% gain)

## 🎯 Common Scenarios

### **Scenario 1: All HOLD signals**
- **What happened:** No clear trading opportunity
- **Is this bad?** NO! Bot is being cautious
- **What to do:** Wait or try different parameters

### **Scenario 2: BUY signal but no trade**
- **What happened:** Risk manager rejected it
- **Why:** Not enough cash, too risky, or at max positions
- **What to do:** Check risk settings in config.yaml

### **Scenario 3: Made a trade**
- **What happened:** Strategy signaled, risk approved, trade executed
- **Check:** Alpaca dashboard to see the paper trade
- **Monitor:** Bot will watch for stop-loss/take-profit

## 🚀 Next Steps for You

1. **✅ You already did:** Run simple_example.py
   
2. **Try next:** Run backtest to see historical performance
   ```bash
   poetry run python examples/backtest_example.py
   ```

3. **Then:** Customize config.yaml with your preferences

4. **Finally:** Run main.py for continuous trading
   ```bash
   poetry run python main.py
   ```

## 💡 Pro Tips

1. **Check logs:** `logs/StockBot_*.log` has detailed info
2. **Start small:** Test with 1-2 stocks first
3. **Be patient:** Good strategies wait for the right moment
4. **Monitor regularly:** Check your bot daily
5. **Test first:** Always backtest before live trading

## 🆘 Troubleshooting

**Problem:** No trades happening
- **Solution:** Normal! Strategies are cautious. Try different stocks or parameters.

**Problem:** Can't connect to Alpaca
- **Solution:** Check .env file has correct API keys

**Problem:** Errors in logs
- **Solution:** Check logs/StockBot_*.log for details

## 📚 Learning Resources

- **HOW_IT_WORKS.md** - Detailed explanation
- **README.md** - Full documentation
- **QUICKSTART.md** - Quick start guide
- **Examples folder** - Working code examples

## 🎓 Understanding Your Results

Your bot just ran and:
- ✅ Connected to Alpaca successfully
- ✅ Fetched real market data
- ✅ Analyzed 3 stocks (AAPL, MSFT, GOOGL)
- ✅ Generated HOLD signals (being cautious)
- ✅ Showed portfolio status

**This is perfect!** Your bot is working correctly. It's just waiting for the right trading opportunity.

## 🔮 What Happens Next?

Run the bot multiple times throughout the day/week:
- Market conditions change
- Strategies will eventually find opportunities
- When they do, you'll see BUY/SELL signals
- Bot will execute trades (in paper mode)
- You'll see positions in your portfolio

**Remember:** Good trading is about patience, not constant action!
