import pandas as pd
from typing import Dict, Any
from trader.core.strategy import Strategy, Signal, SignalType
from trader.indicators.technical_indicators import TechnicalIndicators


class MovingAverageCrossover(Strategy):
    """Moving Average Crossover Strategy"""
    
    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            'fast_period': 10,
            'slow_period': 30,
            'ma_type': 'sma'  # 'sma' or 'ema'
        }
        if params:
            default_params.update(params)
        
        super().__init__("Moving Average Crossover", default_params)
        self.validate_params()
    
    def validate_params(self) -> bool:
        """Validate strategy parameters"""
        fast = self.params.get('fast_period', 0)
        slow = self.params.get('slow_period', 0)
        
        if fast <= 0 or slow <= 0:
            raise ValueError("Periods must be positive")
        
        if fast >= slow:
            raise ValueError("Fast period must be less than slow period")
        
        return True
    
    def generate_signal(self, symbol: str, data: pd.DataFrame) -> Signal:
        """Generate signal based on MA crossover"""
        
        if len(data) < self.params['slow_period']:
            return Signal(SignalType.HOLD, symbol, data['close'].iloc[-1])
        
        # Add moving averages
        ma_type = self.params.get('ma_type', 'sma')
        
        if ma_type == 'ema':
            data = TechnicalIndicators.add_ema(data, self.params['fast_period'])
            data = TechnicalIndicators.add_ema(data, self.params['slow_period'])
            fast_ma = f"ema_{self.params['fast_period']}"
            slow_ma = f"ema_{self.params['slow_period']}"
        else:
            data = TechnicalIndicators.add_sma(data, self.params['fast_period'])
            data = TechnicalIndicators.add_sma(data, self.params['slow_period'])
            fast_ma = f"sma_{self.params['fast_period']}"
            slow_ma = f"sma_{self.params['slow_period']}"
        
        # Get current and previous values
        current_fast = data[fast_ma].iloc[-1]
        current_slow = data[slow_ma].iloc[-1]
        prev_fast = data[fast_ma].iloc[-2]
        prev_slow = data[slow_ma].iloc[-2]
        
        current_price = data['close'].iloc[-1]
        
        # Check for crossover
        if prev_fast <= prev_slow and current_fast > current_slow:
            # Bullish crossover
            return Signal(SignalType.BUY, symbol, current_price, confidence=0.8)
        
        elif prev_fast >= prev_slow and current_fast < current_slow:
            # Bearish crossover
            return Signal(SignalType.SELL, symbol, current_price, confidence=0.8)
        
        return Signal(SignalType.HOLD, symbol, current_price)
