#!/usr/bin/env python3
"""
Test the Trading Bot API
========================
Quick script to test API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("\n" + "="*70)
print("🧪 TESTING TRADING BOT API")
print("="*70)

# Test 1: Health Check
print("\n1️⃣ Testing Health Check...")
response = requests.get(f"{BASE_URL}/api/health")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

# Test 2: List Strategies
print("\n2️⃣ Testing List Strategies...")
response = requests.get(f"{BASE_URL}/api/strategies/")
print(f"   Status: {response.status_code}")
strategies = response.json()
print(f"   Found {len(strategies)} strategies:")
for s in strategies:
    print(f"   • {s['name']}: {s['description']}")

# Test 3: List Portfolios
print("\n3️⃣ Testing List Portfolios...")
response = requests.get(f"{BASE_URL}/api/portfolio/")
print(f"   Status: {response.status_code}")
portfolios = response.json()
print(f"   Found {len(portfolios)} portfolio(s)")

# Test 4: Get Bot Status
print("\n4️⃣ Testing Bot Status...")
response = requests.get(f"{BASE_URL}/api/bot/status")
print(f"   Status: {response.status_code}")
status = response.json()
print(f"   Bot Status: {status['status']}")
print(f"   Is Running: {status['is_running']}")

# Test 5: Run Bot Once (Test Mode)
print("\n5️⃣ Testing Run Bot Once...")
config = {
    "symbols": ["AAPL"],
    "strategies": ["moving_average"],
    "paper_trading": True,
    "max_position_size": 0.1,
    "stop_loss_pct": 0.05,
    "take_profit_pct": 0.10
}
response = requests.post(f"{BASE_URL}/api/bot/run-once", json=config)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"   Message: {result['message']}")
    summary = result.get('portfolio_summary', {})
    print(f"   Portfolio Value: ${summary.get('total_value', 0):,.2f}")
    print(f"   P&L: ${summary.get('total_pnl', 0):,.2f} ({summary.get('total_pnl_pct', 0):.2f}%)")

# Test 6: Get Portfolio Summary
print("\n6️⃣ Testing Portfolio Summary...")
if portfolios:
    portfolio_id = portfolios[0]['id']
    response = requests.get(f"{BASE_URL}/api/portfolio/{portfolio_id}/summary")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        summary = response.json()
        print(f"   Total Value: ${summary['total_value']:,.2f}")
        print(f"   Cash: ${summary['cash']:,.2f}")
        print(f"   Positions: {summary['num_positions']}")

# Test 7: Get Recent Trades
print("\n7️⃣ Testing Recent Trades...")
response = requests.get(f"{BASE_URL}/api/trades/?limit=5")
print(f"   Status: {response.status_code}")
trades = response.json()
print(f"   Found {len(trades)} recent trade(s)")
for trade in trades[:3]:
    print(f"   • {trade['timestamp']}: {trade['action']} {trade['quantity']:.2f} {trade['symbol']} @ ${trade['price']:.2f}")

# Test 8: Get Recent Signals
print("\n8️⃣ Testing Recent Signals...")
response = requests.get(f"{BASE_URL}/api/trades/signals?limit=5")
print(f"   Status: {response.status_code}")
signals = response.json()
print(f"   Found {len(signals)} recent signal(s)")
for signal in signals[:3]:
    print(f"   • {signal['timestamp']}: {signal['signal_type']} {signal['symbol']} @ ${signal['price']:.2f} ({signal['strategy_name']})")

print("\n" + "="*70)
print("✅ API TESTS COMPLETE!")
print("="*70)

print("\n💡 Next Steps:")
print("   • Open http://localhost:8000/docs for interactive API docs")
print("   • Start building your frontend!")
print("   • Use these endpoints to control the bot")

print("\n" + "="*70 + "\n")
