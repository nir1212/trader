# Quick Start Guide

## 1. Install Dependencies

```bash
poetry install
```

## 2. Test Installation

```bash
poetry run python test_setup.py
```

You should see "ALL TESTS PASSED! ✓"

## 3. Configure API Keys (Optional for Testing)

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
- **Alpaca** (stocks): Get free paper trading keys at https://alpaca.markets/
- **Binance** (crypto): Get keys at https://www.binance.com/

**Note:** You can run in simulation mode without API keys!

## 4. Run Your First Backtest

```bash
poetry run python examples/backtest_example.py
```

This will:
- Fetch 1 year of AAPL historical data
- Run multiple trading strategies
- Show performance metrics
- Generate a chart with results

## 5. Try Live Paper Trading

```bash
poetry run python examples/live_trading_example.py
```

This will:
- Run 3 trading iterations
- Analyze AAPL, GOOGL, and MSFT
- Generate trading signals
- Show portfolio performance

## 6. Customize Your Bot

Edit `config/config.yaml` to:
- Change trading symbols/pairs
- Enable/disable strategies
- Adjust risk management settings
- Set initial capital

## 7. Run the Full Bot

```bash
poetry run python main.py
```

This runs continuously until you press Ctrl+C.

## Available Strategies

1. **Moving Average Crossover** - Trend following
2. **RSI Strategy** - Mean reversion
3. **MACD Strategy** - Momentum
4. **Bollinger Bands** - Volatility breakout

## Project Structure

```
src/trader/
├── core/          # Base classes (bot, strategy, portfolio)
├── bots/          # Stock and crypto bot implementations
├── strategies/    # Trading strategies
├── indicators/    # Technical indicators
├── backtesting/   # Backtesting engine
├── risk/          # Risk management
└── utils/         # Utilities (logger, data fetcher)
```

## Common Commands

```bash
# Install dependencies
poetry install

# Run main bot
poetry run python main.py

# Run backtest
poetry run python examples/backtest_example.py

# Run tests
poetry run python test_setup.py

# Add new dependency
poetry add package-name
```

## Tips

- Start with backtesting to test strategies
- Use paper trading before going live
- Monitor logs in the `logs/` directory
- Adjust risk management settings conservatively
- Test with small capital amounts first

## Need Help?

Check the full README.md for detailed documentation.
