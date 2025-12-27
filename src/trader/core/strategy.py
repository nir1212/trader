from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
import pandas as pd


class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class Signal:
    signal_type: SignalType
    symbol: str
    price: float
    quantity: Optional[float] = None
    confidence: float = 1.0
    metadata: Optional[Dict[str, Any]] = None
    
    def __str__(self):
        return f"{self.signal_type.value} {self.symbol} @ ${self.price:.2f}"


class Strategy(ABC):
    """Base class for all trading strategies"""
    
    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None):
        self.name = name
        self.params = params or {}
        
    @abstractmethod
    def generate_signal(self, symbol: str, data: pd.DataFrame) -> Signal:
        """
        Generate trading signal based on market data
        
        Args:
            symbol: Trading symbol (e.g., 'AAPL', 'BTC/USDT')
            data: DataFrame with OHLCV data
            
        Returns:
            Signal object with trading recommendation
        """
        pass
    
    @abstractmethod
    def validate_params(self) -> bool:
        """Validate strategy parameters"""
        pass
    
    def __str__(self):
        return f"{self.name} Strategy"
