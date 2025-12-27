#!/usr/bin/env python3
"""
MY FIRST TRADING BOT - Step by Step Guide
==========================================

This example will help you understand how the trading bot works.
We'll create a simple bot that analyzes Apple stock (AAPL) using
the Moving Average strategy.

What this bot does:
1. Connects to Alpaca (your paper trading account)
2. Fetches recent price data for AAPL
3. Runs a Moving Average strategy to generate signals
4. Shows you what trades it would make
5. Displays your portfolio status
"""

from dotenv import load_dotenv
from trader.core.portfolio import Portfolio
from trader.risk.risk_manager import RiskManager
from trader.bots.stock_bot import StockBot
from trader.strategies.moving_average import MovingAverageCrossover
from trader.utils.logger import setup_logger

# Load your API keys from .env file
load_dotenv()

# Setup logger so we can see what's happening
logger = setup_logger("MyFirstBot", log_level="INFO")

print("\n" + "="*60)
print("🤖 MY FIRST TRADING BOT")
print("="*60)

# ============================================================
# STEP 1: Create a Portfolio
# ============================================================
print("\n📊 STEP 1: Creating Portfolio")
print("-" * 60)

# Start with $10,000 virtual money
INITIAL_CAPITAL = 10000
portfolio = Portfolio(INITIAL_CAPITAL)

print(f"✓ Portfolio created with ${portfolio.initial_capital:,.2f}")
print(f"  Available cash: ${portfolio.cash:,.2f}")

# ============================================================
# STEP 2: Create a Trading Strategy
# ============================================================
print("\n📈 STEP 2: Creating Trading Strategy")
print("-" * 60)

# Moving Average Crossover Strategy:
# - Fast MA (10 days) crosses above Slow MA (30 days) = BUY signal
# - Fast MA crosses below Slow MA = SELL signal
strategy = MovingAverageCrossover({
    'fast_period': 10,  # 10-day moving average
    'slow_period': 30,  # 30-day moving average
    'ma_type': 'sma'    # Simple Moving Average
})

print(f"✓ Strategy created: {strategy.name}")
print(f"  Fast period: {strategy.params['fast_period']} days")
print(f"  Slow period: {strategy.params['slow_period']} days")

# ============================================================
# STEP 3: Setup Risk Management
# ============================================================
print("\n🛡️  STEP 3: Setting Up Risk Management")
print("-" * 60)

risk_manager = RiskManager(
    max_position_size=0.2,      # Use max 20% of portfolio per trade
    max_portfolio_risk=0.02,    # Risk max 2% per trade
    stop_loss_pct=0.05,         # Auto sell if price drops 5%
    take_profit_pct=0.10,       # Auto sell if price gains 10%
    max_positions=3             # Hold max 3 stocks at once
)

print("✓ Risk management configured:")
print(f"  Max position size: 20% of portfolio")
print(f"  Stop loss: 5% (auto-sell if drops)")
print(f"  Take profit: 10% (auto-sell if gains)")
print(f"  Max positions: 3 stocks")

# ============================================================
# STEP 4: Create the Stock Bot
# ============================================================
print("\n🤖 STEP 4: Creating Stock Trading Bot")
print("-" * 60)

# Stocks to analyze
SYMBOLS = ['AAPL']  # Start with just Apple

bot = StockBot(
    portfolio=portfolio,
    strategies=[strategy],      # Can add multiple strategies
    symbols=SYMBOLS,
    risk_manager=risk_manager,
    paper_trading=True          # IMPORTANT: Paper trading = no real money!
)

print(f"✓ Stock bot created")
print(f"  Trading mode: PAPER (simulation)")
print(f"  Symbols: {', '.join(SYMBOLS)}")
print(f"  Strategies: {len([strategy])} active")

# ============================================================
# STEP 5: Connect to Alpaca
# ============================================================
print("\n🔌 STEP 5: Connecting to Alpaca")
print("-" * 60)

bot.start()

# ============================================================
# STEP 6: Run the Trading Analysis
# ============================================================
print("\n🔍 STEP 6: Analyzing Stocks")
print("-" * 60)

print("\nFetching market data and running strategies...")
print("This will:")
print("  1. Get recent price data from Alpaca")
print("  2. Calculate moving averages")
print("  3. Generate BUY/SELL/HOLD signals")
print("  4. Show you what the bot would do")
print()

# Run one iteration of the trading loop
bot.run_trading_loop()

# ============================================================
# STEP 7: Check Portfolio Status
# ============================================================
print("\n💼 STEP 7: Portfolio Summary")
print("-" * 60)

summary = portfolio.get_summary()

print(f"\n📊 Current Portfolio Status:")
print(f"  Initial Capital:  ${summary['initial_capital']:,.2f}")
print(f"  Current Value:    ${summary['total_value']:,.2f}")
print(f"  Cash Available:   ${summary['cash']:,.2f}")
print(f"  Positions Value:  ${summary['positions_value']:,.2f}")
print(f"  Total P&L:        ${summary['total_pnl']:,.2f} ({summary['total_pnl_pct']:.2f}%)")
print(f"  Open Positions:   {summary['num_positions']}")

if summary['num_positions'] > 0:
    print(f"\n📈 Open Positions:")
    for symbol, pos in summary['positions'].items():
        print(f"  {symbol}:")
        print(f"    Quantity: {pos['quantity']:.2f}")
        print(f"    Entry Price: ${pos['entry_price']:.2f}")
        print(f"    Current Price: ${pos['current_price']:.2f}")
        print(f"    Value: ${pos['value']:.2f}")
        print(f"    P&L: ${pos['pnl']:.2f} ({pos['pnl_pct']:.2f}%)")

# ============================================================
# STEP 8: Disconnect
# ============================================================
print("\n🔌 STEP 8: Disconnecting")
print("-" * 60)

bot.stop()

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*60)
print("✅ COMPLETE!")
print("="*60)

print("\n📚 What just happened:")
print("  1. Created a portfolio with $10,000")
print("  2. Set up a Moving Average trading strategy")
print("  3. Connected to your Alpaca paper trading account")
print("  4. Analyzed AAPL stock")
print("  5. Generated trading signals (BUY/SELL/HOLD)")
print("  6. Showed portfolio status")

print("\n🎯 Next Steps:")
print("  • Check the logs/ folder for detailed logs")
print("  • Try adding more symbols: SYMBOLS = ['AAPL', 'GOOGL', 'MSFT']")
print("  • Try different strategies (RSI, MACD)")
print("  • Run multiple times to see how it adapts")
print("  • Check your Alpaca dashboard to see paper trades")

print("\n💡 Understanding the Output:")
print("  • BUY signal = Strategy thinks price will go up")
print("  • SELL signal = Strategy thinks price will go down")
print("  • HOLD signal = No clear direction, wait")
print("  • [SIMULATION] = Not real money, just testing")

print("\n⚠️  Remember:")
print("  • This is PAPER TRADING (no real money)")
print("  • Signals are suggestions, not guarantees")
print("  • Always test thoroughly before going live")

print("\n" + "="*60 + "\n")
