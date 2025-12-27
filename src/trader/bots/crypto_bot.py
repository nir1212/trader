import os
import pandas as pd
from typing import List, Optional
import ccxt
from dotenv import load_dotenv

from trader.core.base_bot import BaseBot
from trader.core.strategy import Strategy, Signal, SignalType
from trader.core.portfolio import Portfolio
from trader.risk.risk_manager import RiskManager
from trader.utils.data_fetcher import DataFetcher

load_dotenv()


class CryptoBot(BaseBot):
    """Crypto trading bot using CCXT (supports multiple exchanges)"""
    
    def __init__(
        self,
        portfolio: Portfolio,
        strategies: List[Strategy],
        pairs: List[str],
        exchange_name: str = 'binance',
        risk_manager: Optional[RiskManager] = None,
        testnet: bool = True
    ):
        super().__init__("CryptoBot", portfolio, strategies, risk_manager)
        
        self.pairs = pairs
        self.exchange_name = exchange_name
        self.testnet = testnet
        self.exchange = None
        
        # Get API credentials
        self.api_key = os.getenv(f'{exchange_name.upper()}_API_KEY')
        self.secret_key = os.getenv(f'{exchange_name.upper()}_SECRET_KEY')
    
    def connect(self):
        """Connect to crypto exchange"""
        try:
            if not self.api_key or not self.secret_key:
                self.logger.warning(f"{self.exchange_name} API keys not found. Running in simulation mode.")
                self.exchange = None
                return
            
            # Initialize exchange
            exchange_class = getattr(ccxt, self.exchange_name)
            
            config = {
                'apiKey': self.api_key,
                'secret': self.secret_key,
                'enableRateLimit': True,
            }
            
            if self.testnet:
                config['options'] = {'defaultType': 'future'}
                if self.exchange_name == 'binance':
                    config['options']['testnet'] = True
            
            self.exchange = exchange_class(config)
            
            # Test connection
            balance = self.exchange.fetch_balance()
            self.logger.info(f"Connected to {self.exchange_name}")
            self.logger.info(f"Available balance: {balance.get('free', {})}")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to {self.exchange_name}: {e}")
            self.exchange = None
    
    def disconnect(self):
        """Disconnect from exchange"""
        if self.exchange:
            self.exchange.close()
        self.exchange = None
        self.logger.info(f"Disconnected from {self.exchange_name}")
    
    def get_market_data(self, symbol: str, timeframe: str = '1d', limit: int = 100) -> pd.DataFrame:
        """Fetch market data for a crypto pair"""
        try:
            if self.exchange:
                # Use exchange API
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                
                df = pd.DataFrame(
                    ohlcv,
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                
                return df
            
            # Fallback to yfinance
            return DataFetcher.fetch_crypto_data(symbol, timeframe, limit)
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            return DataFetcher.fetch_crypto_data(symbol, timeframe, limit)
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price for a crypto pair"""
        try:
            if self.exchange:
                ticker = self.exchange.fetch_ticker(symbol)
                return float(ticker['last'])
            else:
                return DataFetcher.get_current_price(symbol, is_crypto=True)
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol}: {e}")
            return DataFetcher.get_current_price(symbol, is_crypto=True)
    
    def execute_order(self, signal: Signal) -> bool:
        """Execute a trading order"""
        try:
            if not self.exchange:
                self.logger.info(f"[SIMULATION] Would execute: {signal}")
                return True
            
            if signal.signal_type == SignalType.BUY:
                order = self.exchange.create_market_buy_order(
                    signal.symbol,
                    signal.quantity
                )
                self.logger.info(f"Buy order executed: {order['id']}")
                return True
                
            elif signal.signal_type == SignalType.SELL:
                order = self.exchange.create_market_sell_order(
                    signal.symbol,
                    signal.quantity
                )
                self.logger.info(f"Sell order executed: {order['id']}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error executing order: {e}")
            return False
    
    def run_trading_loop(self):
        """Main trading loop"""
        self.logger.info("Starting crypto trading loop...")
        
        for pair in self.pairs:
            self.logger.info(f"Analyzing {pair}...")
            
            # Run strategies
            signals = self.run_strategies(pair)
            
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
