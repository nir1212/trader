from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class BotStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class PortfolioCreate(BaseModel):
    name: str = Field(..., description="Portfolio name")
    initial_capital: float = Field(..., gt=0, description="Initial capital amount")


class PortfolioResponse(BaseModel):
    id: int
    name: str
    initial_capital: float
    current_cash: float
    total_value: float
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class PortfolioSummary(BaseModel):
    initial_capital: float
    cash: float
    positions_value: float
    total_value: float
    total_pnl: float
    total_pnl_pct: float
    num_positions: int
    positions: Dict[str, Any]


class TradeResponse(BaseModel):
    id: int
    timestamp: datetime
    symbol: str
    action: str
    quantity: float
    price: float
    value: float
    strategy_name: Optional[str]
    
    class Config:
        from_attributes = True


class SignalResponse(BaseModel):
    id: int
    timestamp: datetime
    symbol: str
    signal_type: str
    strategy_name: str
    price: float
    confidence: float
    executed: bool
    
    class Config:
        from_attributes = True


class SnapshotResponse(BaseModel):
    id: int
    timestamp: datetime
    total_value: float
    cash: float
    positions_value: float
    total_pnl: float
    total_pnl_pct: float
    num_positions: int
    
    class Config:
        from_attributes = True


class BotConfig(BaseModel):
    symbols: List[str] = Field(..., description="List of symbols to trade")
    strategies: List[str] = Field(..., description="List of strategy names")
    paper_trading: bool = Field(True, description="Paper trading mode")
    max_position_size: float = Field(0.1, description="Max position size as % of portfolio")
    stop_loss_pct: float = Field(0.05, description="Stop loss percentage")
    take_profit_pct: float = Field(0.10, description="Take profit percentage")


class BotStatusResponse(BaseModel):
    status: BotStatus
    is_running: bool
    portfolio_id: Optional[int]
    symbols: List[str]
    strategies: List[str]
    uptime_seconds: Optional[float]


class StrategyInfo(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


class PerformanceMetrics(BaseModel):
    total_return: float
    total_return_pct: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
