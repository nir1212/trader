import pandas as pd
from typing import Dict, Any
from trader.core.strategy import Strategy, Signal, SignalType
from trader.indicators.technical_indicators import TechnicalIndicators


class BollingerBandsStrategy(Strategy):
    """Bollinger Bands Strategy"""
    
    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            'period': 20,
            'std_dev': 2
        }
        if params:
            default_params.update(params)
        
        super().__init__("Bollinger Bands Strategy", default_params)
        self.validate_params()
    
    def validate_params(self) -> bool:
        """Validate strategy parameters"""
        period = self.params.get('period', 0)
        std_dev = self.params.get('std_dev', 0)
        
        if period <= 0:
            raise ValueError("Period must be positive")
        
        if std_dev <= 0:
            raise ValueError("Standard deviation must be positive")
        
        return True
    
    def generate_signal(self, symbol: str, data: pd.DataFrame) -> Signal:
        """Generate signal based on Bollinger Bands"""
        
        if len(data) < self.params['period']:
            return Signal(SignalType.HOLD, symbol, data['close'].iloc[-1])
        
        # Add Bollinger Bands
        data = TechnicalIndicators.add_bollinger_bands(
            data,
            self.params['period'],
            self.params['std_dev']
        )
        
        current_price = data['close'].iloc[-1]
        prev_price = data['close'].iloc[-2]
        
        bb_upper = data['bb_upper'].iloc[-1]
        bb_lower = data['bb_lower'].iloc[-1]
        bb_middle = data['bb_middle'].iloc[-1]
        
        prev_bb_lower = data['bb_lower'].iloc[-2]
        prev_bb_upper = data['bb_upper'].iloc[-2]
        
        # Price crossing above lower band (bullish)
        if prev_price <= prev_bb_lower and current_price > bb_lower:
            # Calculate confidence based on distance from middle band
            distance_pct = (bb_middle - current_price) / bb_middle * 100
            confidence = min(1.0, 0.6 + distance_pct / 10)
            return Signal(SignalType.BUY, symbol, current_price, confidence=confidence)
        
        # Price crossing below upper band (bearish)
        elif prev_price >= prev_bb_upper and current_price < bb_upper:
            distance_pct = (current_price - bb_middle) / bb_middle * 100
            confidence = min(1.0, 0.6 + distance_pct / 10)
            return Signal(SignalType.SELL, symbol, current_price, confidence=confidence)
        
        return Signal(SignalType.HOLD, symbol, current_price)
