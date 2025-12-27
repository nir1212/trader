import os
import pandas as pd
from typing import List, Optional
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

from trader.core.base_bot import BaseBot
from trader.core.strategy import Strategy, Signal, SignalType
from trader.core.portfolio import Portfolio
from trader.risk.risk_manager import RiskManager
from trader.utils.data_fetcher import DataFetcher

load_dotenv()


class StockBot(BaseBot):
    """Stock trading bot using Alpaca API"""
    
    def __init__(
        self,
        portfolio: Portfolio,
        strategies: List[Strategy],
        symbols: List[str],
        risk_manager: Optional[RiskManager] = None,
        paper_trading: bool = True
    ):
        super().__init__("StockBot", portfolio, strategies, risk_manager)
        
        self.symbols = symbols
        self.paper_trading = paper_trading
        self.api = None
        
        # Get API credentials
        self.api_key = os.getenv('ALPACA_API_KEY')
        self.secret_key = os.getenv('ALPACA_SECRET_KEY')
        
        if paper_trading:
            self.base_url = 'https://paper-api.alpaca.markets'
        else:
            self.base_url = 'https://api.alpaca.markets'
    
    def connect(self):
        """Connect to Alpaca API"""
        try:
            if not self.api_key or not self.secret_key:
                self.logger.warning("Alpaca API keys not found. Running in simulation mode.")
                self.api = None
                return
            
            self.api = tradeapi.REST(
                self.api_key,
                self.secret_key,
                self.base_url,
                api_version='v2'
            )
            
            # Test connection
            account = self.api.get_account()
            self.logger.info(f"Connected to Alpaca. Account status: {account.status}")
            self.logger.info(f"Buying power: ${float(account.buying_power):.2f}")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Alpaca: {e}")
            self.api = None
    
    def disconnect(self):
        """Disconnect from Alpaca API"""
        self.api = None
        self.logger.info("Disconnected from Alpaca")
    
    def get_market_data(self, symbol: str, timeframe: str = '1d', limit: int = 100) -> pd.DataFrame:
        """Fetch market data for a stock symbol"""
        try:
            if self.api:
                # Use Alpaca API - convert timeframe to Alpaca format
                # Alpaca uses: '1Min', '5Min', '15Min', '1Hour', '1Day'
                alpaca_timeframe = timeframe
                if timeframe == '1d':
                    alpaca_timeframe = '1Day'
                elif timeframe == '1h':
                    alpaca_timeframe = '1Hour'
                elif timeframe == '1m':
                    alpaca_timeframe = '1Min'
                
                barset = self.api.get_bars(
                    symbol,
                    alpaca_timeframe,
                    limit=limit
                ).df
                
                if not barset.empty:
                    barset.columns = [col.lower() for col in barset.columns]
                    return barset
            
            # Fallback to yfinance
            return DataFetcher.fetch_stock_data(symbol, period=f"{limit}d", interval=timeframe)
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            return DataFetcher.fetch_stock_data(symbol, period=f"{limit}d", interval=timeframe)
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price for a stock"""
        try:
            if self.api:
                trade = self.api.get_latest_trade(symbol)
                return float(trade.price)
            else:
                return DataFetcher.get_current_price(symbol, is_crypto=False)
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol}: {e}")
            return DataFetcher.get_current_price(symbol, is_crypto=False)
    
    def execute_order(self, signal: Signal) -> bool:
        """Execute a trading order"""
        try:
            if not self.api:
                self.logger.info(f"[SIMULATION] Would execute: {signal}")
                return True
            
            if signal.signal_type == SignalType.BUY:
                order = self.api.submit_order(
                    symbol=signal.symbol,
                    qty=signal.quantity,
                    side='buy',
                    type='market',
                    time_in_force='day'
                )
                self.logger.info(f"Buy order submitted: {order.id}")
                return True
                
            elif signal.signal_type == SignalType.SELL:
                order = self.api.submit_order(
                    symbol=signal.symbol,
                    qty=signal.quantity,
                    side='sell',
                    type='market',
                    time_in_force='day'
                )
                self.logger.info(f"Sell order submitted: {order.id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error executing order: {e}")
            return False
    
    def run_trading_loop(self):
        """Main trading loop"""
        self.logger.info("Starting stock trading loop...")
        
        for symbol in self.symbols:
            self.logger.info(f"Analyzing {symbol}...")
            
            # Run strategies
            signals = self.run_strategies(symbol)
            
            if not signals:
                continue
            
            # Aggregate signals
            final_signal = self.aggregate_signals(signals)
            
            # Process signal
            if final_signal.signal_type != SignalType.HOLD:
                self.process_signal(final_signal)
        
        # Check existing positions
        self.check_positions()
        
        # Log portfolio summary
        summary = self.get_portfolio_summary()
        self.logger.info(f"Portfolio Value: ${summary['total_value']:.2f}")
        self.logger.info(f"P&L: ${summary['total_pnl']:.2f} ({summary['total_pnl_pct']:.2f}%)")
