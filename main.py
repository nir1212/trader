#!/usr/bin/env python3
"""
Trading Bot System - Main Entry Point
"""

import yaml
import time
from pathlib import Path
from dotenv import load_dotenv

from trader.core.portfolio import Portfolio
from trader.risk.risk_manager import RiskManager
from trader.bots.stock_bot import StockBot
from trader.bots.crypto_bot import CryptoBot
from trader.strategies.moving_average import MovingAverageCrossover
from trader.strategies.rsi_strategy import RSIStrategy
from trader.strategies.macd_strategy import MACDStrategy
from trader.strategies.bollinger_bands import BollingerBandsStrategy
from trader.backtesting.backtest_engine import BacktestEngine
from trader.utils.logger import setup_logger
from trader.utils.data_fetcher import DataFetcher

# Load environment variables
load_dotenv()


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def create_strategies(config: dict) -> list:
    """Create strategy instances from config"""
    strategies = []
    
    strategy_map = {
        'moving_average_crossover': MovingAverageCrossover,
        'rsi_strategy': RSIStrategy,
        'macd_strategy': MACDStrategy,
        'bollinger_bands': BollingerBandsStrategy
    }
    
    for strategy_config in config.get('strategies', []):
        if not strategy_config.get('enabled', False):
            continue
        
        strategy_name = strategy_config['name']
        strategy_class = strategy_map.get(strategy_name)
        
        if strategy_class:
            strategy = strategy_class(strategy_config.get('params', {}))
            strategies.append(strategy)
    
    return strategies


def run_backtest(config: dict, logger):
    """Run backtesting mode"""
    logger.info("Starting backtesting mode...")
    
    backtest_config = config.get('backtesting', {})
    symbol = backtest_config.get('symbol', 'AAPL')
    period = backtest_config.get('period', '1y')
    commission = backtest_config.get('commission', 0.001)
    
    # Fetch historical data
    logger.info(f"Fetching historical data for {symbol}...")
    data = DataFetcher.fetch_stock_data(symbol, period=period, interval='1d')
    
    if data is None or data.empty:
        logger.error(f"Failed to fetch data for {symbol}")
        return
    
    logger.info(f"Loaded {len(data)} days of data")
    
    # Create strategies
    strategies = create_strategies(config)
    logger.info(f"Loaded {len(strategies)} strategies")
    
    # Create risk manager
    risk_config = config.get('risk_management', {})
    risk_manager = RiskManager(
        max_position_size=risk_config.get('max_position_size', 0.1),
        max_portfolio_risk=risk_config.get('max_portfolio_risk', 0.02),
        stop_loss_pct=risk_config.get('stop_loss_pct', 0.05),
        take_profit_pct=risk_config.get('take_profit_pct', 0.10),
        max_positions=risk_config.get('max_positions', 10)
    )
    
    # Create backtest engine
    initial_capital = config['trading']['initial_capital']
    engine = BacktestEngine(initial_capital, strategies, risk_manager)
    
    # Run backtest
    logger.info("Running backtest...")
    results = engine.run_backtest(symbol, data, commission)
    
    # Print results
    engine.print_summary()
    
    # Plot results
    plot_path = f"backtest_{symbol}_{period}.png"
    engine.plot_results(save_path=plot_path)
    logger.info(f"Backtest complete. Results saved to {plot_path}")


def run_live_trading(config: dict, logger):
    """Run live/paper trading mode"""
    logger.info("Starting live trading mode...")
    
    # Create strategies
    strategies = create_strategies(config)
    logger.info(f"Loaded {len(strategies)} strategies: {[s.name for s in strategies]}")
    
    # Create risk manager
    risk_config = config.get('risk_management', {})
    risk_manager = RiskManager(
        max_position_size=risk_config.get('max_position_size', 0.1),
        max_portfolio_risk=risk_config.get('max_portfolio_risk', 0.02),
        stop_loss_pct=risk_config.get('stop_loss_pct', 0.05),
        take_profit_pct=risk_config.get('take_profit_pct', 0.10),
        max_positions=risk_config.get('max_positions', 10)
    )
    
    # Create portfolio
    initial_capital = config['trading']['initial_capital']
    portfolio = Portfolio(initial_capital)
    
    bots = []
    
    # Create stock bot
    if config.get('stock_bot', {}).get('enabled', False):
        stock_config = config['stock_bot']
        stock_bot = StockBot(
            portfolio=portfolio,
            strategies=strategies,
            symbols=stock_config['symbols'],
            risk_manager=risk_manager,
            paper_trading=stock_config.get('paper_trading', True)
        )
        bots.append(stock_bot)
        logger.info(f"Stock bot created with symbols: {stock_config['symbols']}")
    
    # Create crypto bot
    if config.get('crypto_bot', {}).get('enabled', False):
        crypto_config = config['crypto_bot']
        crypto_bot = CryptoBot(
            portfolio=portfolio,
            strategies=strategies,
            pairs=crypto_config['pairs'],
            exchange_name=crypto_config.get('exchange', 'binance'),
            risk_manager=risk_manager,
            testnet=crypto_config.get('testnet', True)
        )
        bots.append(crypto_bot)
        logger.info(f"Crypto bot created with pairs: {crypto_config['pairs']}")
    
    if not bots:
        logger.error("No bots enabled. Check your configuration.")
        return
    
    # Start bots
    for bot in bots:
        bot.start()
    
    try:
        # Main trading loop
        logger.info("Trading bots are running. Press Ctrl+C to stop.")
        
        while True:
            for bot in bots:
                try:
                    bot.run_trading_loop()
                except Exception as e:
                    logger.error(f"Error in {bot.name}: {e}")
            
            # Wait before next iteration (e.g., 5 minutes)
            logger.info("Waiting for next iteration...")
            time.sleep(300)
    
    except KeyboardInterrupt:
        logger.info("Stopping trading bots...")
    
    finally:
        # Stop bots
        for bot in bots:
            bot.stop()
        
        # Print final portfolio summary
        summary = portfolio.get_summary()
        logger.info("\n" + "="*50)
        logger.info("FINAL PORTFOLIO SUMMARY")
        logger.info("="*50)
        logger.info(f"Initial Capital: ${summary['initial_capital']:,.2f}")
        logger.info(f"Final Value:     ${summary['total_value']:,.2f}")
        logger.info(f"Total P&L:       ${summary['total_pnl']:,.2f} ({summary['total_pnl_pct']:.2f}%)")
        logger.info(f"Cash:            ${summary['cash']:,.2f}")
        logger.info(f"Positions Value: ${summary['positions_value']:,.2f}")
        logger.info(f"Open Positions:  {summary['num_positions']}")
        logger.info("="*50)


def main():
    """Main entry point"""
    # Setup logger
    logger = setup_logger("TradingBot", log_level="INFO")
    
    logger.info("="*50)
    logger.info("TRADING BOT SYSTEM")
    logger.info("="*50)
    
    # Load configuration
    try:
        config = load_config()
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return
    
    # Check mode
    if config.get('backtesting', {}).get('enabled', False):
        run_backtest(config, logger)
    else:
        run_live_trading(config, logger)


if __name__ == "__main__":
    main()
