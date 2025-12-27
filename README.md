# Trading Bot System

Advanced stocks and crypto trading bot system with Python, featuring multiple strategies, risk management, and backtesting capabilities.

## Features

- **Multi-Asset Support**: Trade both stocks (via Alpaca) and cryptocurrencies (via Binance/CCXT)
- **Multiple Trading Strategies**:
  - Moving Average Crossover (SMA/EMA)
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
- **Risk Management**: Position sizing, stop-loss, take-profit, portfolio limits
- **Backtesting Engine**: Test strategies on historical data with performance metrics
- **Paper Trading**: Test in simulation mode before going live
- **Comprehensive Logging**: Colored console output and file logging

## Project Structure

```
trader/
├── src/trader/
│   ├── core/           # Core framework (base bot, strategy, portfolio)
│   ├── bots/           # Stock and crypto bot implementations
│   ├── strategies/     # Trading strategies
│   ├── indicators/     # Technical indicators
│   ├── backtesting/    # Backtesting engine
│   ├── risk/           # Risk management
│   └── utils/          # Utilities (logger, data fetcher)
├── config/
│   └── config.yaml     # Configuration file
├── main.py             # Main entry point
└── pyproject.toml      # Poetry dependencies
```

## Installation

### 1. Install Dependencies

```bash
poetry install
```

### 2. Configure API Keys

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Alpaca (for stocks)
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Binance (for crypto)
BINANCE_API_KEY=your_key_here
BINANCE_SECRET_KEY=your_secret_here
```

**Get API Keys:**
- **Alpaca** (Stocks): [https://alpaca.markets/](https://alpaca.markets/) - Free paper trading account
- **Binance** (Crypto): [https://www.binance.com/](https://www.binance.com/) - Create account and generate API keys

### 3. Configure Trading Settings

Edit `config/config.yaml` to customize:
- Trading symbols/pairs
- Strategies and parameters
- Risk management settings
- Initial capital

## Usage

### Run Live/Paper Trading

```bash
poetry run python main.py
```

This will:
1. Load configuration from `config/config.yaml`
2. Initialize enabled bots (stock and/or crypto)
3. Run trading strategies continuously
4. Execute trades based on signals
5. Monitor positions and apply risk management

### Run Backtesting

Edit `config/config.yaml` and set:

```yaml
backtesting:
  enabled: true
  symbol: AAPL
  period: 1y
  commission: 0.001
```

Then run:

```bash
poetry run python main.py
```

This will:
1. Fetch historical data
2. Run strategies on historical data
3. Calculate performance metrics
4. Generate equity curve and trade plots

## Configuration

### Trading Mode

```yaml
trading:
  mode: paper  # paper or live
  initial_capital: 10000
  log_level: INFO
```

### Stock Bot

```yaml
stock_bot:
  enabled: true
  symbols:
    - AAPL
    - GOOGL
    - MSFT
  paper_trading: true
```

### Crypto Bot

```yaml
crypto_bot:
  enabled: true
  exchange: binance
  pairs:
    - BTC/USDT
    - ETH/USDT
  testnet: true
```

### Strategies

```yaml
strategies:
  - name: moving_average_crossover
    enabled: true
    params:
      fast_period: 10
      slow_period: 30
      
  - name: rsi_strategy
    enabled: true
    params:
      period: 14
      oversold: 30
      overbought: 70
```

### Risk Management

```yaml
risk_management:
  max_position_size: 0.1      # 10% per position
  max_portfolio_risk: 0.02    # 2% risk per trade
  stop_loss_pct: 0.05         # 5% stop loss
  take_profit_pct: 0.10       # 10% take profit
  max_positions: 5
```

## Trading Strategies

### Moving Average Crossover
Generates buy signals when fast MA crosses above slow MA, and sell signals when it crosses below.

### RSI Strategy
Buys when RSI crosses above oversold level (default 30), sells when it crosses below overbought level (default 70).

### MACD Strategy
Buys when MACD line crosses above signal line, sells when it crosses below.

### Bollinger Bands
Buys when price crosses above lower band, sells when it crosses below upper band.

## Creating Custom Strategies

Create a new file in `src/trader/strategies/`:

```python
from trader.core.strategy import Strategy, Signal, SignalType
import pandas as pd

class MyStrategy(Strategy):
    def __init__(self, params=None):
        super().__init__("My Strategy", params)
    
    def validate_params(self) -> bool:
        return True
    
    def generate_signal(self, symbol: str, data: pd.DataFrame) -> Signal:
        # Your strategy logic here
        current_price = data['close'].iloc[-1]
        
        if should_buy:
            return Signal(SignalType.BUY, symbol, current_price)
        elif should_sell:
            return Signal(SignalType.SELL, symbol, current_price)
        else:
            return Signal(SignalType.HOLD, symbol, current_price)
```

## Backtesting Results

The backtesting engine provides:
- **Total Return**: Percentage gain/loss
- **Sharpe Ratio**: Risk-adjusted return
- **Max Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of winning trades
- **Equity Curve**: Visual representation of portfolio value over time

## Safety Features

- **Paper Trading Mode**: Test without real money
- **Risk Management**: Automatic position sizing and stop-losses
- **Portfolio Limits**: Maximum positions and risk per trade
- **Simulation Mode**: Runs without API keys for testing

## Logging

Logs are saved to the `logs/` directory with:
- Colored console output
- Daily log files
- Trade execution history
- Error tracking

## Development

### Project uses Poetry for dependency management

```bash
# Install dependencies
poetry install

# Add new dependency
poetry add package-name

# Run tests
poetry run pytest

# Format code
poetry run black src/

# Type checking
poetry run mypy src/
```

## Important Notes

⚠️ **Trading involves risk. This bot is for educational purposes.**

- Start with paper trading to test strategies
- Never invest more than you can afford to lose
- Past performance doesn't guarantee future results
- Always monitor your bots and positions
- Use proper risk management

## Troubleshooting

### API Connection Issues
- Verify API keys in `.env` file
- Check if using correct base URL (paper vs live)
- Ensure API keys have trading permissions

### Data Fetching Errors
- Check internet connection
- Verify symbol format (stocks: AAPL, crypto: BTC/USDT)
- Try fallback to yfinance if exchange API fails

### Strategy Not Executing
- Check if strategy is enabled in config
- Verify sufficient historical data
- Review logs for error messages

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review log files for errors