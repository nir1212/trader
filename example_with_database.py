#!/usr/bin/env python3
"""
TRADING BOT WITH DATABASE - Example
====================================
This example shows how the bot now persists all data to a database.

What gets saved:
- All trades (buy/sell)
- Portfolio snapshots over time
- Trading signals from strategies
- Performance metrics
- Open positions
"""

from dotenv import load_dotenv
from trader.core.portfolio_with_db import PortfolioWithDB
from trader.database.db_manager import DatabaseManager
from trader.risk.risk_manager import RiskManager
from trader.bots.stock_bot import StockBot
from trader.strategies.moving_average import MovingAverageCrossover
from trader.strategies.rsi_strategy import RSIStrategy
from trader.utils.logger import setup_logger
from datetime import datetime, timedelta

load_dotenv()

print("\n" + "="*70)
print("🗄️  TRADING BOT WITH DATABASE PERSISTENCE")
print("="*70)

# Initialize database
db_manager = DatabaseManager("data/trading_bot.db")
print("\n✓ Database initialized at: data/trading_bot.db")

# Create or load portfolio with database
portfolio = PortfolioWithDB(
    initial_capital=10000,
    name="my_trading_portfolio",
    db_manager=db_manager
)

print(f"\n💼 Portfolio: {portfolio.name}")
print(f"   ID: {portfolio.portfolio_id}")
print(f"   Initial Capital: ${portfolio.initial_capital:,.2f}")
print(f"   Current Cash: ${portfolio.cash:,.2f}")
print(f"   Total Value: ${portfolio.total_value:,.2f}")

# Check if we have previous trades
previous_trades = portfolio.get_trade_history(limit=5)
if previous_trades:
    print(f"\n📊 Found {len(previous_trades)} previous trades")
    print("   Last 5 trades:")
    for trade in previous_trades[:5]:
        print(f"   • {trade.timestamp.strftime('%Y-%m-%d %H:%M')} - {trade.action} {trade.quantity:.2f} {trade.symbol} @ ${trade.price:.2f}")
else:
    print("\n📊 No previous trades found (new portfolio)")

# Create strategies
strategies = [
    MovingAverageCrossover({'fast_period': 10, 'slow_period': 30}),
    RSIStrategy({'period': 14, 'oversold': 30, 'overbought': 70})
]

# Risk management
risk_manager = RiskManager(
    max_position_size=0.2,
    stop_loss_pct=0.05,
    take_profit_pct=0.10
)

# Create bot (note: we pass the portfolio with DB)
symbols = ['AAPL', 'MSFT']
bot = StockBot(
    portfolio=portfolio,
    strategies=strategies,
    symbols=symbols,
    risk_manager=risk_manager,
    paper_trading=True
)

print(f"\n🤖 Bot configured to analyze: {', '.join(symbols)}")
print("\n" + "-"*70)

# Start bot
bot.start()

print("\n📈 Running trading analysis...\n")

# Run trading loop
bot.run_trading_loop()

# Stop bot
bot.stop()

print("\n" + "="*70)
print("📊 PORTFOLIO SUMMARY (FROM DATABASE)")
print("="*70)

# Get comprehensive stats from database
stats = portfolio.get_stats()

print(f"\n💰 Financial Summary:")
print(f"   Initial Capital:  ${stats['initial_capital']:,.2f}")
print(f"   Current Value:    ${stats['current_value']:,.2f}")
print(f"   Total P&L:        ${stats['total_pnl']:,.2f} ({stats['total_pnl_pct']:.2f}%)")

print(f"\n📈 Trading Activity:")
print(f"   Total Trades:     {stats['total_trades']}")
print(f"   Buy Orders:       {stats['buy_trades']}")
print(f"   Sell Orders:      {stats['sell_trades']}")
print(f"   Winning Trades:   {stats['winning_trades']}")
print(f"   Losing Trades:    {stats['losing_trades']}")
print(f"   Win Rate:         {stats['win_rate']:.2f}%")

# Show recent trades
print(f"\n📝 Recent Trades:")
recent_trades = portfolio.get_trade_history(limit=10)
if recent_trades:
    for trade in recent_trades:
        print(f"   {trade.timestamp.strftime('%Y-%m-%d %H:%M')} | {trade.action:10} | {trade.symbol:6} | {trade.quantity:8.2f} @ ${trade.price:8.2f} | ${trade.value:10,.2f}")
else:
    print("   No trades yet")

# Show portfolio snapshots
print(f"\n📸 Portfolio History (Last 5 snapshots):")
snapshots = portfolio.get_snapshots(limit=5)
if snapshots:
    for snap in snapshots:
        print(f"   {snap.timestamp.strftime('%Y-%m-%d %H:%M')} | Value: ${snap.total_value:10,.2f} | P&L: ${snap.total_pnl:8,.2f} ({snap.total_pnl_pct:6.2f}%) | Positions: {snap.num_positions}")
else:
    print("   No snapshots yet")

# Show signals generated
print(f"\n🎯 Recent Trading Signals:")
signals = db_manager.get_signals(limit=10)
if signals:
    for signal in signals:
        executed = "✓" if signal.executed else "✗"
        print(f"   {executed} {signal.timestamp.strftime('%Y-%m-%d %H:%M')} | {signal.signal_type:4} | {signal.symbol:6} | ${signal.price:8.2f} | {signal.strategy_name}")
else:
    print("   No signals recorded yet")

print("\n" + "="*70)
print("✅ ALL DATA SAVED TO DATABASE!")
print("="*70)

print("\n💡 What's Stored in the Database:")
print("   • All trades (buy/sell with timestamps)")
print("   • Portfolio value over time (snapshots)")
print("   • Trading signals from each strategy")
print("   • Open and closed positions")
print("   • Performance metrics")

print("\n🔍 Database Location:")
print("   data/trading_bot.db")

print("\n📊 You Can Now:")
print("   • Run this script multiple times - data persists!")
print("   • Analyze your trading history")
print("   • Track performance over time")
print("   • See which strategies work best")
print("   • Resume trading from where you left off")

print("\n🎯 Next Steps:")
print("   1. Run this script again - it will load your existing portfolio")
print("   2. Check the database file: data/trading_bot.db")
print("   3. Use the reporting tools to analyze performance")
print("   4. Your portfolio state is now persistent!")

print("\n" + "="*70 + "\n")
