from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta

from trader.api.models import (
    PortfolioCreate, PortfolioResponse, PortfolioSummary,
    SnapshotResponse, PerformanceMetrics
)
from trader.database.db_manager import DatabaseManager
from trader.core.portfolio_with_db import PortfolioWithDB

router = APIRouter()
db_manager = DatabaseManager()


@router.post("/", response_model=PortfolioResponse)
def create_portfolio(portfolio: PortfolioCreate):
    """Create a new portfolio"""
    try:
        db_portfolio = db_manager.create_portfolio(
            name=portfolio.name,
            initial_capital=portfolio.initial_capital
        )
        return db_portfolio
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[PortfolioResponse])
def list_portfolios():
    """Get all portfolios"""
    session = db_manager.get_session()
    try:
        from trader.database.models import Portfolio
        portfolios = session.query(Portfolio).all()
        return portfolios
    finally:
        session.close()


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
def get_portfolio(portfolio_id: int):
    """Get portfolio by ID"""
    portfolio = db_manager.get_portfolio(portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio


@router.get("/{portfolio_id}/summary", response_model=PortfolioSummary)
def get_portfolio_summary(portfolio_id: int):
    """Get portfolio summary with current positions"""
    portfolio = db_manager.get_portfolio(portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Load portfolio with DB
    portfolio_obj = PortfolioWithDB(
        initial_capital=portfolio.initial_capital,
        name=portfolio.name,
        db_manager=db_manager
    )
    
    return portfolio_obj.get_summary()


@router.get("/{portfolio_id}/snapshots", response_model=List[SnapshotResponse])
def get_portfolio_snapshots(
    portfolio_id: int,
    limit: Optional[int] = Query(50, description="Number of snapshots to return")
):
    """Get portfolio historical snapshots"""
    snapshots = db_manager.get_snapshots(portfolio_id=portfolio_id, limit=limit)
    return snapshots


@router.get("/{portfolio_id}/performance", response_model=PerformanceMetrics)
def get_portfolio_performance(portfolio_id: int):
    """Get portfolio performance metrics"""
    stats = db_manager.get_portfolio_stats(portfolio_id)
    
    if not stats:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    return PerformanceMetrics(
        total_return=stats['total_pnl'],
        total_return_pct=stats['total_pnl_pct'],
        win_rate=stats['win_rate'],
        total_trades=stats['total_trades'],
        winning_trades=stats['winning_trades'],
        losing_trades=stats['losing_trades']
    )


@router.delete("/{portfolio_id}")
def delete_portfolio(portfolio_id: int):
    """Deactivate a portfolio"""
    session = db_manager.get_session()
    try:
        from trader.database.models import Portfolio
        portfolio = session.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        portfolio.is_active = False
        session.commit()
        
        return {"message": "Portfolio deactivated", "portfolio_id": portfolio_id}
    finally:
        session.close()
