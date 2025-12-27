import pandas as pd
import yfinance as yf
from typing import Optional
from datetime import datetime, timedelta


class DataFetcher:
    """Fetch historical market data"""
    
    @staticmethod
    def fetch_stock_data(
        symbol: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch stock data from Yahoo Finance
        
        Args:
            symbol: Stock ticker (e.g., 'AAPL')
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                return None
            
            # Standardize column names
            data.columns = [col.lower() for col in data.columns]
            
            return data
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    @staticmethod
    def fetch_crypto_data(
        symbol: str,
        timeframe: str = "1d",
        limit: int = 100
    ) -> Optional[pd.DataFrame]:
        """
        Fetch crypto data (using yfinance for now)
        
        Args:
            symbol: Crypto pair (e.g., 'BTC-USD')
            timeframe: Timeframe
            limit: Number of candles
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Convert symbol format for yfinance
            if '/' in symbol:
                symbol = symbol.replace('/', '-')
            
            ticker = yf.Ticker(symbol)
            
            # Calculate period based on limit and timeframe
            if timeframe == '1d':
                period = f"{limit}d"
            elif timeframe == '1h':
                period = f"{limit//24}d"
            else:
                period = "1mo"
            
            data = ticker.history(period=period, interval=timeframe)
            
            if data.empty:
                return None
            
            # Standardize column names
            data.columns = [col.lower() for col in data.columns]
            
            return data.tail(limit)
            
        except Exception as e:
            print(f"Error fetching crypto data for {symbol}: {e}")
            return None
    
    @staticmethod
    def get_current_price(symbol: str, is_crypto: bool = False) -> Optional[float]:
        """Get current price for a symbol"""
        try:
            if is_crypto and '/' in symbol:
                symbol = symbol.replace('/', '-')
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d', interval='1m')
            
            if data.empty:
                return None
            
            return float(data['Close'].iloc[-1])
            
        except Exception as e:
            print(f"Error fetching current price for {symbol}: {e}")
            return None
