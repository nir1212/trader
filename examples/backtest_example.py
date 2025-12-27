#!/usr/bin/env python3
"""
Example: Running a backtest on historical data
"""

from trader.core.portfolio import Portfolio
from trader.risk.risk_manager import RiskManager
from trader.strategies.moving_average import MovingAverageCrossover
from trader.strategies.rsi_strategy import RSIStrategy
from trader.strategies.macd_strategy import MACDStrategy
from trader.backtesting.backtest_engine import BacktestEngine
from trader.utils.data_fetcher import DataFetcher
from trader.utils.logger import setup_logger

# Setup logger
logger = setup_logger("BacktestExample")

# Configuration
SYMBOL = "AAPL"
PERIOD = "1y"
INITIAL_CAPITAL = 10000

logger.info(f"Running backtest for {SYMBOL} over {PERIOD}")

# Fetch historical data
logger.info("Fetching historical data...")
data = DataFetcher.fetch_stock_data(SYMBOL, period=PERIOD, interval='1d')

if data is None or data.empty:
    logger.error(f"Failed to fetch data for {SYMBOL}")
    exit(1)

logger.info(f"Loaded {len(data)} days of data")

# Create strategies
strategies = [
    MovingAverageCrossover({'fast_period': 10, 'slow_period': 30}),
    RSIStrategy({'period': 14, 'oversold': 30, 'overbought': 70}),
    MACDStrategy({'fast_period': 12, 'slow_period': 26, 'signal_period': 9})
]

logger.info(f"Using {len(strategies)} strategies")

# Create risk manager
risk_manager = RiskManager(
    max_position_size=0.1,
    max_portfolio_risk=0.02,
    stop_loss_pct=0.05,
    take_profit_pct=0.10,
    max_positions=5
)

# Create backtest engine
engine = BacktestEngine(INITIAL_CAPITAL, strategies, risk_manager)

# Run backtest
logger.info("Running backtest...")
results = engine.run_backtest(SYMBOL, data, commission=0.001)

# Print results
engine.print_summary()

# Display trades
print("\nTrade History:")
print(results['trades'].to_string())

# Plot results
plot_path = f"backtest_{SYMBOL}_{PERIOD}.png"
engine.plot_results(save_path=plot_path)
logger.info(f"Results saved to {plot_path}")
