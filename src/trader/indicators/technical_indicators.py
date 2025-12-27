import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange


class TechnicalIndicators:
    """Technical indicators for trading analysis"""
    
    @staticmethod
    def add_sma(data: pd.DataFrame, period: int = 20, column: str = 'close') -> pd.DataFrame:
        """Add Simple Moving Average"""
        data[f'sma_{period}'] = SMAIndicator(close=data[column], window=period).sma_indicator()
        return data
    
    @staticmethod
    def add_ema(data: pd.DataFrame, period: int = 20, column: str = 'close') -> pd.DataFrame:
        """Add Exponential Moving Average"""
        data[f'ema_{period}'] = EMAIndicator(close=data[column], window=period).ema_indicator()
        return data
    
    @staticmethod
    def add_rsi(data: pd.DataFrame, period: int = 14, column: str = 'close') -> pd.DataFrame:
        """Add Relative Strength Index"""
        data['rsi'] = RSIIndicator(close=data[column], window=period).rsi()
        return data
    
    @staticmethod
    def add_macd(
        data: pd.DataFrame,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
        column: str = 'close'
    ) -> pd.DataFrame:
        """Add MACD indicator"""
        macd = MACD(close=data[column], window_fast=fast, window_slow=slow, window_sign=signal)
        data['macd'] = macd.macd()
        data['macd_signal'] = macd.macd_signal()
        data['macd_diff'] = macd.macd_diff()
        return data
    
    @staticmethod
    def add_bollinger_bands(
        data: pd.DataFrame,
        period: int = 20,
        std_dev: int = 2,
        column: str = 'close'
    ) -> pd.DataFrame:
        """Add Bollinger Bands"""
        bb = BollingerBands(close=data[column], window=period, window_dev=std_dev)
        data['bb_upper'] = bb.bollinger_hband()
        data['bb_middle'] = bb.bollinger_mavg()
        data['bb_lower'] = bb.bollinger_lband()
        data['bb_width'] = bb.bollinger_wband()
        return data
    
    @staticmethod
    def add_atr(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Add Average True Range"""
        data['atr'] = AverageTrueRange(
            high=data['high'],
            low=data['low'],
            close=data['close'],
            window=period
        ).average_true_range()
        return data
    
    @staticmethod
    def add_stochastic(
        data: pd.DataFrame,
        k_period: int = 14,
        d_period: int = 3
    ) -> pd.DataFrame:
        """Add Stochastic Oscillator"""
        stoch = StochasticOscillator(
            high=data['high'],
            low=data['low'],
            close=data['close'],
            window=k_period,
            smooth_window=d_period
        )
        data['stoch_k'] = stoch.stoch()
        data['stoch_d'] = stoch.stoch_signal()
        return data
    
    @staticmethod
    def add_volume_sma(data: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Add Volume Simple Moving Average"""
        data[f'volume_sma_{period}'] = data['volume'].rolling(window=period).mean()
        return data
    
    @staticmethod
    def add_all_indicators(data: pd.DataFrame) -> pd.DataFrame:
        """Add all common indicators"""
        data = TechnicalIndicators.add_sma(data, 20)
        data = TechnicalIndicators.add_sma(data, 50)
        data = TechnicalIndicators.add_ema(data, 12)
        data = TechnicalIndicators.add_ema(data, 26)
        data = TechnicalIndicators.add_rsi(data)
        data = TechnicalIndicators.add_macd(data)
        data = TechnicalIndicators.add_bollinger_bands(data)
        data = TechnicalIndicators.add_atr(data)
        data = TechnicalIndicators.add_volume_sma(data)
        return data
