import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, func, and_, desc
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
import json

from trader.database.models import Base, Trade, Portfolio, PortfolioSnapshot, Signal, Performance, Position, Bot


class DatabaseManager:
    """Manage database connections and operations"""
    
    def __init__(self, db_path: str = "data/trading_bot.db"):
        """Initialize database manager"""
        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create engine
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        
        # Create tables
        Base.metadata.create_all(self.engine)
        
        # Create session factory
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    # ==================== Portfolio Operations ====================
    
    def create_portfolio(self, name: str, initial_capital: float) -> Portfolio:
        """Create a new portfolio"""
        session = self.get_session()
        try:
            portfolio = Portfolio(
                name=name,
                initial_capital=initial_capital,
                current_cash=initial_capital,
                total_value=initial_capital
            )
            session.add(portfolio)
            session.commit()
            session.refresh(portfolio)
            return portfolio
        finally:
            session.close()
    
    def get_portfolio(self, portfolio_id: int) -> Optional[Portfolio]:
        """Get portfolio by ID"""
        session = self.get_session()
        try:
            return session.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        finally:
            session.close()
    
    def get_active_portfolio(self, name: str = None) -> Optional[Portfolio]:
        """Get active portfolio by name or the most recent one"""
        session = self.get_session()
        try:
            query = session.query(Portfolio).filter(Portfolio.is_active == True)
            if name:
                query = query.filter(Portfolio.name == name)
            return query.order_by(desc(Portfolio.created_at)).first()
        finally:
            session.close()
    
    def update_portfolio(self, portfolio_id: int, cash: float, total_value: float):
        """Update portfolio values"""
        session = self.get_session()
        try:
            portfolio = session.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if portfolio:
                portfolio.current_cash = cash
                portfolio.total_value = total_value
                portfolio.updated_at = datetime.now()
                session.commit()
        finally:
            session.close()
    
    # ==================== Trade Operations ====================
    
    def record_trade(
        self,
        portfolio_id: int,
        symbol: str,
        action: str,
        quantity: float,
        price: float,
        value: float,
        strategy_name: str = None,
        bot_name: str = None,
        commission: float = 0.0
    ) -> Trade:
        """Record a trade execution"""
        session = self.get_session()
        try:
            trade = Trade(
                portfolio_id=portfolio_id,
                symbol=symbol,
                action=action,
                quantity=quantity,
                price=price,
                value=value,
                strategy_name=strategy_name,
                bot_name=bot_name,
                commission=commission
            )
            session.add(trade)
            session.commit()
            session.refresh(trade)
            return trade
        finally:
            session.close()
    
    def get_trades(
        self,
        portfolio_id: int = None,
        symbol: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = None
    ) -> List[Trade]:
        """Get trades with optional filters"""
        session = self.get_session()
        try:
            query = session.query(Trade)
            
            if portfolio_id:
                query = query.filter(Trade.portfolio_id == portfolio_id)
            if symbol:
                query = query.filter(Trade.symbol == symbol)
            if start_date:
                query = query.filter(Trade.timestamp >= start_date)
            if end_date:
                query = query.filter(Trade.timestamp <= end_date)
            
            query = query.order_by(desc(Trade.timestamp))
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        finally:
            session.close()
    
    # ==================== Portfolio Snapshot Operations ====================
    
    def save_snapshot(
        self,
        portfolio_id: int,
        total_value: float,
        cash: float,
        positions_value: float,
        total_pnl: float,
        total_pnl_pct: float,
        num_positions: int
    ) -> PortfolioSnapshot:
        """Save a portfolio snapshot"""
        session = self.get_session()
        try:
            snapshot = PortfolioSnapshot(
                portfolio_id=portfolio_id,
                total_value=total_value,
                cash=cash,
                positions_value=positions_value,
                total_pnl=total_pnl,
                total_pnl_pct=total_pnl_pct,
                num_positions=num_positions
            )
            session.add(snapshot)
            session.commit()
            session.refresh(snapshot)
            return snapshot
        finally:
            session.close()
    
    def get_snapshots(
        self,
        portfolio_id: int,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = None
    ) -> List[PortfolioSnapshot]:
        """Get portfolio snapshots"""
        session = self.get_session()
        try:
            query = session.query(PortfolioSnapshot).filter(
                PortfolioSnapshot.portfolio_id == portfolio_id
            )
            
            if start_date:
                query = query.filter(PortfolioSnapshot.timestamp >= start_date)
            if end_date:
                query = query.filter(PortfolioSnapshot.timestamp <= end_date)
            
            query = query.order_by(desc(PortfolioSnapshot.timestamp))
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        finally:
            session.close()
    
    # ==================== Signal Operations ====================
    
    def record_signal(
        self,
        symbol: str,
        signal_type: str,
        strategy_name: str,
        price: float,
        bot_id: int = None,
        confidence: float = 1.0,
        executed: bool = False,
        metadata: Dict = None
    ) -> Signal:
        """Record a trading signal"""
        session = self.get_session()
        try:
            signal = Signal(
                bot_id=bot_id,
                symbol=symbol,
                signal_type=signal_type,
                strategy_name=strategy_name,
                price=price,
                confidence=confidence,
                executed=executed,
                signal_metadata=json.dumps(metadata) if metadata else None
            )
            session.add(signal)
            session.commit()
            session.refresh(signal)
            return signal
        finally:
            session.close()
    
    def get_signals(
        self,
        symbol: str = None,
        signal_type: str = None,
        strategy_name: str = None,
        start_date: datetime = None,
        limit: int = None
    ) -> List[Signal]:
        """Get signals with optional filters"""
        session = self.get_session()
        try:
            query = session.query(Signal)
            
            if symbol:
                query = query.filter(Signal.symbol == symbol)
            if signal_type:
                query = query.filter(Signal.signal_type == signal_type)
            if strategy_name:
                query = query.filter(Signal.strategy_name == strategy_name)
            if start_date:
                query = query.filter(Signal.timestamp >= start_date)
            
            query = query.order_by(desc(Signal.timestamp))
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        finally:
            session.close()
    
    # ==================== Position Operations ====================
    
    def save_position(
        self,
        portfolio_id: int,
        symbol: str,
        quantity: float,
        entry_price: float,
        current_price: float,
        stop_loss: float = None,
        take_profit: float = None,
        position_type: str = 'LONG'
    ) -> Position:
        """Save or update a position"""
        session = self.get_session()
        try:
            # Check if position already exists
            position = session.query(Position).filter(
                and_(
                    Position.portfolio_id == portfolio_id,
                    Position.symbol == symbol,
                    Position.is_open == True
                )
            ).first()
            
            if position:
                # Update existing position
                position.quantity = quantity
                position.current_price = current_price
                if stop_loss:
                    position.stop_loss = stop_loss
                if take_profit:
                    position.take_profit = take_profit
            else:
                # Create new position
                position = Position(
                    portfolio_id=portfolio_id,
                    symbol=symbol,
                    quantity=quantity,
                    entry_price=entry_price,
                    current_price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    position_type=position_type
                )
                session.add(position)
            
            session.commit()
            session.refresh(position)
            return position
        finally:
            session.close()
    
    def close_position(self, portfolio_id: int, symbol: str):
        """Close a position"""
        session = self.get_session()
        try:
            position = session.query(Position).filter(
                and_(
                    Position.portfolio_id == portfolio_id,
                    Position.symbol == symbol,
                    Position.is_open == True
                )
            ).first()
            
            if position:
                position.is_open = False
                position.closed_at = datetime.now()
                session.commit()
        finally:
            session.close()
    
    def get_open_positions(self, portfolio_id: int) -> List[Position]:
        """Get all open positions for a portfolio"""
        session = self.get_session()
        try:
            return session.query(Position).filter(
                and_(
                    Position.portfolio_id == portfolio_id,
                    Position.is_open == True
                )
            ).all()
        finally:
            session.close()
    
    # ==================== Performance Operations ====================
    
    def save_performance(
        self,
        portfolio_id: int,
        period: str,
        metrics: Dict[str, Any]
    ) -> Performance:
        """Save performance metrics"""
        session = self.get_session()
        try:
            performance = Performance(
                portfolio_id=portfolio_id,
                period=period,
                **metrics
            )
            session.add(performance)
            session.commit()
            session.refresh(performance)
            return performance
        finally:
            session.close()
    
    def get_performance(
        self,
        portfolio_id: int,
        period: str = None
    ) -> List[Performance]:
        """Get performance metrics"""
        session = self.get_session()
        try:
            query = session.query(Performance).filter(
                Performance.portfolio_id == portfolio_id
            )
            
            if period:
                query = query.filter(Performance.period == period)
            
            return query.order_by(desc(Performance.timestamp)).all()
        finally:
            session.close()
    
    # ==================== Analytics ====================
    
    def get_portfolio_stats(self, portfolio_id: int) -> Dict[str, Any]:
        """Get comprehensive portfolio statistics"""
        session = self.get_session()
        try:
            portfolio = session.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not portfolio:
                return {}
            
            # Get trade statistics
            trades = session.query(Trade).filter(Trade.portfolio_id == portfolio_id).all()
            
            buy_trades = [t for t in trades if t.action == 'BUY']
            sell_trades = [t for t in trades if t.action in ['SELL', 'STOP_LOSS', 'TAKE_PROFIT']]
            
            # Calculate win rate
            winning_trades = 0
            losing_trades = 0
            
            for sell in sell_trades:
                # Find corresponding buy
                buys = [b for b in buy_trades if b.symbol == sell.symbol and b.timestamp < sell.timestamp]
                if buys:
                    buy = buys[-1]
                    if sell.price > buy.price:
                        winning_trades += 1
                    else:
                        losing_trades += 1
            
            total_trades = winning_trades + losing_trades
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            # Get latest snapshot
            latest_snapshot = session.query(PortfolioSnapshot).filter(
                PortfolioSnapshot.portfolio_id == portfolio_id
            ).order_by(desc(PortfolioSnapshot.timestamp)).first()
            
            return {
                'portfolio_name': portfolio.name,
                'initial_capital': portfolio.initial_capital,
                'current_value': portfolio.total_value,
                'total_pnl': portfolio.total_value - portfolio.initial_capital,
                'total_pnl_pct': ((portfolio.total_value - portfolio.initial_capital) / portfolio.initial_capital * 100),
                'total_trades': len(trades),
                'buy_trades': len(buy_trades),
                'sell_trades': len(sell_trades),
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'latest_snapshot': latest_snapshot
            }
        finally:
            session.close()
