from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import datetime

from trader.api.models import TradeResponse, SignalResponse
from trader.database.db_manager import DatabaseManager

router = APIRouter()
db_manager = DatabaseManager()


@router.get("/", response_model=List[TradeResponse])
def get_trades(
    portfolio_id: Optional[int] = Query(None, description="Filter by portfolio ID"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    limit: Optional[int] = Query(50, description="Number of trades to return")
):
    """Get trade history"""
    trades = db_manager.get_trades(
        portfolio_id=portfolio_id,
        symbol=symbol,
        limit=limit
    )
    return trades


@router.get("/signals", response_model=List[SignalResponse])
def get_signals(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    signal_type: Optional[str] = Query(None, description="Filter by signal type (BUY/SELL/HOLD)"),
    strategy_name: Optional[str] = Query(None, description="Filter by strategy name"),
    limit: Optional[int] = Query(50, description="Number of signals to return")
):
    """Get trading signals"""
    signals = db_manager.get_signals(
        symbol=symbol,
        signal_type=signal_type,
        strategy_name=strategy_name,
        limit=limit
    )
    return signals


@router.get("/{trade_id}", response_model=TradeResponse)
def get_trade(trade_id: int):
    """Get specific trade by ID"""
    session = db_manager.get_session()
    try:
        from trader.database.models import Trade
        trade = session.query(Trade).filter(Trade.id == trade_id).first()
        
        if not trade:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Trade not found")
        
        return trade
    finally:
        session.close()
