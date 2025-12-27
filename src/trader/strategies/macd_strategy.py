import pandas as pd
from typing import Dict, Any
from trader.core.strategy import Strategy, Signal, SignalType
from trader.indicators.technical_indicators import TechnicalIndicators


class MACDStrategy(Strategy):
    """MACD (Moving Average Convergence Divergence) Strategy"""
    
    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9
        }
        if params:
            default_params.update(params)
        
        super().__init__("MACD Strategy", default_params)
        self.validate_params()
    
    def validate_params(self) -> bool:
        """Validate strategy parameters"""
        fast = self.params.get('fast_period', 0)
        slow = self.params.get('slow_period', 0)
        signal = self.params.get('signal_period', 0)
        
        if fast <= 0 or slow <= 0 or signal <= 0:
            raise ValueError("All periods must be positive")
        
        if fast >= slow:
            raise ValueError("Fast period must be less than slow period")
        
        return True
    
    def generate_signal(self, symbol: str, data: pd.DataFrame) -> Signal:
        """Generate signal based on MACD crossover"""
        
        min_periods = self.params['slow_period'] + self.params['signal_period']
        if len(data) < min_periods:
            return Signal(SignalType.HOLD, symbol, data['close'].iloc[-1])
        
        # Add MACD
        data = TechnicalIndicators.add_macd(
            data,
            self.params['fast_period'],
            self.params['slow_period'],
            self.params['signal_period']
        )
        
        current_macd = data['macd'].iloc[-1]
        current_signal = data['macd_signal'].iloc[-1]
        prev_macd = data['macd'].iloc[-2]
        prev_signal = data['macd_signal'].iloc[-2]
        
        current_price = data['close'].iloc[-1]
        
        # MACD crossing above signal line (bullish)
        if prev_macd <= prev_signal and current_macd > current_signal:
            # Calculate confidence based on histogram strength
            histogram = abs(current_macd - current_signal)
            confidence = min(1.0, 0.6 + histogram * 0.1)
            return Signal(SignalType.BUY, symbol, current_price, confidence=confidence)
        
        # MACD crossing below signal line (bearish)
        elif prev_macd >= prev_signal and current_macd < current_signal:
            histogram = abs(current_macd - current_signal)
            confidence = min(1.0, 0.6 + histogram * 0.1)
            return Signal(SignalType.SELL, symbol, current_price, confidence=confidence)
        
        return Signal(SignalType.HOLD, symbol, current_price)
