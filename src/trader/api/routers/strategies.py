from fastapi import APIRouter
from typing import List

from trader.api.models import StrategyInfo

router = APIRouter()


@router.get("/", response_model=List[StrategyInfo])
def list_strategies():
    """Get list of available strategies"""
    strategies = [
        StrategyInfo(
            name="moving_average",
            description="Moving Average Crossover - Buy when fast MA crosses above slow MA",
            parameters={
                "fast_period": {"type": "int", "default": 10, "description": "Fast MA period"},
                "slow_period": {"type": "int", "default": 30, "description": "Slow MA period"},
                "ma_type": {"type": "string", "default": "sma", "options": ["sma", "ema"]}
            }
        ),
        StrategyInfo(
            name="rsi",
            description="RSI Strategy - Buy when oversold, sell when overbought",
            parameters={
                "period": {"type": "int", "default": 14, "description": "RSI period"},
                "oversold": {"type": "int", "default": 30, "description": "Oversold threshold"},
                "overbought": {"type": "int", "default": 70, "description": "Overbought threshold"}
            }
        ),
        StrategyInfo(
            name="macd",
            description="MACD Strategy - Buy on bullish crossover, sell on bearish",
            parameters={
                "fast_period": {"type": "int", "default": 12, "description": "Fast EMA period"},
                "slow_period": {"type": "int", "default": 26, "description": "Slow EMA period"},
                "signal_period": {"type": "int", "default": 9, "description": "Signal line period"}
            }
        ),
        StrategyInfo(
            name="bollinger_bands",
            description="Bollinger Bands - Buy at lower band, sell at upper band",
            parameters={
                "period": {"type": "int", "default": 20, "description": "BB period"},
                "std_dev": {"type": "int", "default": 2, "description": "Standard deviations"}
            }
        )
    ]
    
    return strategies
