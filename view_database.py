#!/usr/bin/env python3
"""
DATABASE VIEWER - View your trading data
=========================================
This script lets you view all the data stored in your database.
"""

from trader.database.db_manager import DatabaseManager
from datetime import datetime, timedelta
import sys

db_manager = DatabaseManager("data/trading_bot.db")

print("\n" + "="*70)
print("🗄️  TRADING BOT DATABASE VIEWER")
print("="*70)

# Get all portfolios
session = db_manager.get_session()
from trader.database.models import Portfolio, Trade, PortfolioSnapshot, Signal

try:
    portfolios = session.query(Portfolio).all()
    
    if not portfolios:
        print("\n⚠️  No portfolios found in database.")
        print("   Run example_with_database.py first to create data.")
        sys.exit(0)
    
    print(f"\n📊 Found {len(portfolios)} portfolio(s)")
    
    for portfolio in portfolios:
        print("\n" + "="*70)
        print(f"💼 Portfolio: {portfolio.name} (ID: {portfolio.id})")
        print("="*70)
        
        print(f"\n💰 Overview:")
        print(f"   Created:          {portfolio.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Initial Capital:  ${portfolio.initial_capital:,.2f}")
        print(f"   Current Cash:     ${portfolio.current_cash:,.2f}")
        print(f"   Total Value:      ${portfolio.total_value:,.2f}")
        print(f"   P&L:              ${portfolio.total_value - portfolio.initial_capital:,.2f} ({((portfolio.total_value - portfolio.initial_capital) / portfolio.initial_capital * 100):.2f}%)")
        print(f"   Status:           {'Active' if portfolio.is_active else 'Inactive'}")
        
        # Get trades
        trades = session.query(Trade).filter(Trade.portfolio_id == portfolio.id).order_by(Trade.timestamp.desc()).limit(20).all()
        print(f"\n📝 Trades ({len(trades)} total, showing last 20):")
        if trades:
            print(f"   {'Date/Time':<20} {'Action':<12} {'Symbol':<8} {'Quantity':<10} {'Price':<12} {'Value':<15}")
            print(f"   {'-'*20} {'-'*12} {'-'*8} {'-'*10} {'-'*12} {'-'*15}")
            for trade in trades:
                print(f"   {trade.timestamp.strftime('%Y-%m-%d %H:%M'):<20} {trade.action:<12} {trade.symbol:<8} {trade.quantity:<10.2f} ${trade.price:<11.2f} ${trade.value:<14,.2f}")
        else:
            print("   No trades yet")
        
        # Get snapshots
        snapshots = session.query(PortfolioSnapshot).filter(
            PortfolioSnapshot.portfolio_id == portfolio.id
        ).order_by(PortfolioSnapshot.timestamp.desc()).limit(10).all()
        
        print(f"\n📸 Portfolio Snapshots (showing last 10):")
        if snapshots:
            print(f"   {'Date/Time':<20} {'Total Value':<15} {'Cash':<12} {'Positions':<12} {'P&L':<15} {'P&L %':<10}")
            print(f"   {'-'*20} {'-'*15} {'-'*12} {'-'*12} {'-'*15} {'-'*10}")
            for snap in snapshots:
                print(f"   {snap.timestamp.strftime('%Y-%m-%d %H:%M'):<20} ${snap.total_value:<14,.2f} ${snap.cash:<11,.2f} ${snap.positions_value:<11,.2f} ${snap.total_pnl:<14,.2f} {snap.total_pnl_pct:<9.2f}%")
        else:
            print("   No snapshots yet")
        
        # Get signals
        signals = session.query(Signal).order_by(Signal.timestamp.desc()).limit(20).all()
        print(f"\n🎯 Trading Signals (showing last 20):")
        if signals:
            print(f"   {'Date/Time':<20} {'Type':<6} {'Symbol':<8} {'Price':<12} {'Strategy':<30} {'Exec':<5}")
            print(f"   {'-'*20} {'-'*6} {'-'*8} {'-'*12} {'-'*30} {'-'*5}")
            for signal in signals:
                executed = "✓" if signal.executed else "✗"
                print(f"   {signal.timestamp.strftime('%Y-%m-%d %H:%M'):<20} {signal.signal_type:<6} {signal.symbol:<8} ${signal.price:<11.2f} {signal.strategy_name:<30} {executed:<5}")
        else:
            print("   No signals yet")
        
        # Get statistics
        stats = db_manager.get_portfolio_stats(portfolio.id)
        print(f"\n📊 Statistics:")
        print(f"   Total Trades:     {stats['total_trades']}")
        print(f"   Buy Orders:       {stats['buy_trades']}")
        print(f"   Sell Orders:      {stats['sell_trades']}")
        print(f"   Winning Trades:   {stats['winning_trades']}")
        print(f"   Losing Trades:    {stats['losing_trades']}")
        print(f"   Win Rate:         {stats['win_rate']:.2f}%")

finally:
    session.close()

print("\n" + "="*70)
print("✅ Database viewing complete!")
print("="*70)

print("\n💡 Tips:")
print("   • Run example_with_database.py to generate more data")
print("   • All data persists between runs")
print("   • Database file: data/trading_bot.db")

print("\n" + "="*70 + "\n")
