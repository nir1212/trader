#!/usr/bin/env python3
"""
SIMPLE TRADING BOT EXAMPLE
==========================
This shows you exactly what the bot does with clear output
"""

from dotenv import load_dotenv
from trader.core.portfolio import Portfolio
from trader.risk.risk_manager import RiskManager
from trader.bots.stock_bot import StockBot
from trader.strategies.moving_average import MovingAverageCrossover
from trader.strategies.rsi_strategy import RSIStrategy
from trader.utils.logger import setup_logger

load_dotenv()

print("\n" + "="*70)
print("🤖 SIMPLE TRADING BOT - UNDERSTANDING THE OUTPUT")
print("="*70)

# Create portfolio with $10,000
portfolio = Portfolio(10000)
print(f"\n💰 Starting with: ${portfolio.cash:,.2f}")

# Create strategies
strategies = [
    MovingAverageCrossover({'fast_period': 10, 'slow_period': 30}),
    RSIStrategy({'period': 14, 'oversold': 30, 'overbought': 70})
]

print(f"📊 Using {len(strategies)} strategies:")
for s in strategies:
    print(f"   • {s.name}")

# Risk management
risk_manager = RiskManager(
    max_position_size=0.2,
    stop_loss_pct=0.05,
    take_profit_pct=0.10
)

# Create bot
symbols = ['AAPL', 'MSFT', 'GOOGL']
bot = StockBot(
    portfolio=portfolio,
    strategies=strategies,
    symbols=symbols,
    risk_manager=risk_manager,
    paper_trading=True
)

print(f"\n🎯 Analyzing stocks: {', '.join(symbols)}")
print("\n" + "-"*70)

# Start bot
bot.start()

print("\n📈 RUNNING ANALYSIS...\n")

# Run the trading loop
bot.run_trading_loop()

# Show results
print("\n" + "="*70)
print("📊 PORTFOLIO SUMMARY")
print("="*70)

summary = portfolio.get_summary()

print(f"\n💵 Cash:              ${summary['cash']:,.2f}")
print(f"📈 Positions Value:   ${summary['positions_value']:,.2f}")
print(f"💼 Total Value:       ${summary['total_value']:,.2f}")
print(f"📊 Profit/Loss:       ${summary['total_pnl']:,.2f} ({summary['total_pnl_pct']:.2f}%)")
print(f"🔢 Open Positions:    {summary['num_positions']}")

if summary['num_positions'] > 0:
    print(f"\n📍 YOUR POSITIONS:")
    for symbol, pos in summary['positions'].items():
        print(f"\n   {symbol}:")
        print(f"   • Shares: {pos['quantity']:.2f}")
        print(f"   • Bought at: ${pos['entry_price']:.2f}")
        print(f"   • Current: ${pos['current_price']:.2f}")
        print(f"   • Value: ${pos['value']:,.2f}")
        print(f"   • P&L: ${pos['pnl']:.2f} ({pos['pnl_pct']:.2f}%)")
else:
    print("\n   No positions opened (all signals were HOLD)")

# Stop bot
bot.stop()

print("\n" + "="*70)
print("✅ DONE!")
print("="*70)

print("\n📚 WHAT HAPPENED:")
print("   1. Bot connected to Alpaca (your paper trading account)")
print("   2. Fetched recent price data for each stock")
print("   3. Ran 2 strategies on each stock")
print("   4. Generated BUY/SELL/HOLD signals")
print("   5. Risk manager decided if trades were safe")
print("   6. Executed approved trades (in simulation)")

print("\n💡 UNDERSTANDING SIGNALS:")
print("   • BUY = Both strategies think price will go up")
print("   • SELL = Both strategies think price will go down")
print("   • HOLD = Mixed signals or no clear direction")

print("\n🔍 CHECK THE LOGS:")
print("   Look in logs/StockBot_*.log for detailed information")
print("   You'll see exactly what each strategy decided")

print("\n🎯 TRY THIS:")
print("   1. Run this script multiple times")
print("   2. Check your Alpaca dashboard (paper trading)")
print("   3. Modify the symbols list")
print("   4. Try different strategy parameters")

print("\n⚠️  REMEMBER:")
print("   • This is PAPER TRADING (fake money)")
print("   • Signals are based on technical analysis")
print("   • Not financial advice - for learning only!")

print("\n" + "="*70 + "\n")
