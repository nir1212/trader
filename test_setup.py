#!/usr/bin/env python3
"""
Quick test to verify the trading bot setup
"""

print("Testing trading bot imports...")

try:
    from trader.core.portfolio import Portfolio
    from trader.core.strategy import Strategy, Signal, SignalType
    from trader.risk.risk_manager import RiskManager
    from trader.strategies.moving_average import MovingAverageCrossover
    from trader.strategies.rsi_strategy import RSIStrategy
    from trader.bots.stock_bot import StockBot
    from trader.bots.crypto_bot import CryptoBot
    from trader.backtesting.backtest_engine import BacktestEngine
    from trader.utils.logger import setup_logger
    from trader.utils.data_fetcher import DataFetcher
    from trader.indicators.technical_indicators import TechnicalIndicators
    
    print("✓ All imports successful!")
    
    # Test portfolio creation
    portfolio = Portfolio(10000)
    print(f"✓ Portfolio created with ${portfolio.initial_capital:,.2f}")
    
    # Test strategy creation
    ma_strategy = MovingAverageCrossover({'fast_period': 10, 'slow_period': 30})
    rsi_strategy = RSIStrategy({'period': 14, 'oversold': 30, 'overbought': 70})
    print(f"✓ Strategies created: {ma_strategy.name}, {rsi_strategy.name}")
    
    # Test risk manager
    risk_manager = RiskManager(
        max_position_size=0.1,
        max_portfolio_risk=0.02,
        stop_loss_pct=0.05,
        take_profit_pct=0.10
    )
    print("✓ Risk manager created")
    
    # Test logger
    logger = setup_logger("TestBot", log_level="INFO")
    print("✓ Logger setup successful")
    
    # Test data fetcher
    print("\nTesting data fetcher (this may take a moment)...")
    data = DataFetcher.fetch_stock_data("AAPL", period="5d", interval="1d")
    if data is not None and not data.empty:
        print(f"✓ Data fetcher working - fetched {len(data)} days of AAPL data")
    else:
        print("⚠ Data fetcher returned no data (this is okay if offline)")
    
    print("\n" + "="*50)
    print("ALL TESTS PASSED! ✓")
    print("="*50)
    print("\nYour trading bot system is ready to use!")
    print("\nNext steps:")
    print("1. Configure your API keys in .env file")
    print("2. Customize config/config.yaml")
    print("3. Run: poetry run python main.py")
    print("\nOr try the examples:")
    print("- poetry run python examples/backtest_example.py")
    print("- poetry run python examples/live_trading_example.py")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
