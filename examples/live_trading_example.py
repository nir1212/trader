#!/usr/bin/env python3
"""
Example: Running live/paper trading
"""

import time
from dotenv import load_dotenv

from trader.core.portfolio import Portfolio
from trader.risk.risk_manager import RiskManager
from trader.bots.stock_bot import StockBot
from trader.strategies.moving_average import MovingAverageCrossover
from trader.strategies.rsi_strategy import RSIStrategy
from trader.utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger("LiveTradingExample")

# Configuration
INITIAL_CAPITAL = 10000
SYMBOLS = ['AAPL', 'GOOGL', 'MSFT']
PAPER_TRADING = True

logger.info("Starting live trading example...")

# Create portfolio
portfolio = Portfolio(INITIAL_CAPITAL)

# Create strategies
strategies = [
    MovingAverageCrossover({'fast_period': 10, 'slow_period': 30}),
    RSIStrategy({'period': 14, 'oversold': 30, 'overbought': 70})
]

# Create risk manager
risk_manager = RiskManager(
    max_position_size=0.1,
    max_portfolio_risk=0.02,
    stop_loss_pct=0.05,
    take_profit_pct=0.10,
    max_positions=5
)

# Create stock bot
bot = StockBot(
    portfolio=portfolio,
    strategies=strategies,
    symbols=SYMBOLS,
    risk_manager=risk_manager,
    paper_trading=PAPER_TRADING
)

# Start bot
bot.start()

try:
    # Run for a few iterations
    for i in range(3):
        logger.info(f"\n--- Iteration {i+1} ---")
        bot.run_trading_loop()
        
        # Wait before next iteration
        if i < 2:
            logger.info("Waiting 60 seconds before next iteration...")
            time.sleep(60)

except KeyboardInterrupt:
    logger.info("Stopping bot...")

finally:
    # Stop bot
    bot.stop()
    
    # Print final summary
    summary = portfolio.get_summary()
    logger.info("\n" + "="*50)
    logger.info("FINAL PORTFOLIO SUMMARY")
    logger.info("="*50)
    logger.info(f"Initial Capital: ${summary['initial_capital']:,.2f}")
    logger.info(f"Final Value:     ${summary['total_value']:,.2f}")
    logger.info(f"Total P&L:       ${summary['total_pnl']:,.2f} ({summary['total_pnl_pct']:.2f}%)")
    logger.info("="*50)
