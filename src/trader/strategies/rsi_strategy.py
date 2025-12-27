import pandas as pd
from typing import Dict, Any
from trader.core.strategy import Strategy, Signal, SignalType
from trader.indicators.technical_indicators import TechnicalIndicators


class RSIStrategy(Strategy):
    """RSI (Relative Strength Index) Strategy"""
    
    def __init__(self, params: Dict[str, Any] = None):
        default_params = {
            'period': 14,
            'oversold': 30,
            'overbought': 70
        }
        if params:
            default_params.update(params)
        
        super().__init__("RSI Strategy", default_params)
        self.validate_params()
    
    def validate_params(self) -> bool:
        """Validate strategy parameters"""
        period = self.params.get('period', 0)
        oversold = self.params.get('oversold', 0)
        overbought = self.params.get('overbought', 0)
        
        if period <= 0:
            raise ValueError("Period must be positive")
        
        if not (0 < oversold < overbought < 100):
            raise ValueError("Invalid oversold/overbought levels")
        
        return True
    
    def generate_signal(self, symbol: str, data: pd.DataFrame) -> Signal:
        """Generate signal based on RSI levels"""
        
        if len(data) < self.params['period'] + 1:
            return Signal(SignalType.HOLD, symbol, data['close'].iloc[-1])
        
        # Add RSI
        data = TechnicalIndicators.add_rsi(data, self.params['period'])
        
        current_rsi = data['rsi'].iloc[-1]
        prev_rsi = data['rsi'].iloc[-2]
        current_price = data['close'].iloc[-1]
        
        oversold = self.params['oversold']
        overbought = self.params['overbought']
        
        # RSI crossing above oversold level (bullish)
        if prev_rsi <= oversold and current_rsi > oversold:
            confidence = min(1.0, (oversold - prev_rsi + 5) / 10)
            return Signal(SignalType.BUY, symbol, current_price, confidence=confidence)
        
        # RSI crossing below overbought level (bearish)
        elif prev_rsi >= overbought and current_rsi < overbought:
            confidence = min(1.0, (prev_rsi - overbought + 5) / 10)
            return Signal(SignalType.SELL, symbol, current_price, confidence=confidence)
        
        return Signal(SignalType.HOLD, symbol, current_price)
