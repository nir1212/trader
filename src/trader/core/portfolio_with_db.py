from typing import Dict, List, Optional
from datetime import datetime
from trader.core.portfolio import Portfolio as BasePortfolio, Position, PositionType
from trader.database.db_manager import DatabaseManager


class PortfolioWithDB(BasePortfolio):
    """Portfolio with database persistence"""
    
    def __init__(self, initial_capital: float, name: str = "default", db_manager: DatabaseManager = None):
        super().__init__(initial_capital)
        self.name = name
        self.db_manager = db_manager or DatabaseManager()
        
        # Try to load existing portfolio or create new one
        existing = self.db_manager.get_active_portfolio(name)
        if existing:
            self.portfolio_id = existing.id
            self.initial_capital = existing.initial_capital
            self.cash = existing.current_cash
            # Load positions from database
            self._load_positions()
        else:
            # Create new portfolio in database
            db_portfolio = self.db_manager.create_portfolio(name, initial_capital)
            self.portfolio_id = db_portfolio.id
    
    def _load_positions(self):
        """Load open positions from database"""
        db_positions = self.db_manager.get_open_positions(self.portfolio_id)
        for db_pos in db_positions:
            position = Position(
                symbol=db_pos.symbol,
                quantity=db_pos.quantity,
                entry_price=db_pos.entry_price,
                current_price=db_pos.current_price,
                position_type=PositionType.LONG if db_pos.position_type == 'LONG' else PositionType.SHORT,
                entry_time=db_pos.entry_time,
                stop_loss=db_pos.stop_loss,
                take_profit=db_pos.take_profit
            )
            self.positions[db_pos.symbol] = position
    
    def add_position(self, position: Position):
        """Add position and save to database"""
        super().add_position(position)
        
        # Save to database
        self.db_manager.save_position(
            portfolio_id=self.portfolio_id,
            symbol=position.symbol,
            quantity=position.quantity,
            entry_price=position.entry_price,
            current_price=position.current_price,
            stop_loss=position.stop_loss,
            take_profit=position.take_profit,
            position_type=position.position_type.value
        )
        
        # Record trade
        self.db_manager.record_trade(
            portfolio_id=self.portfolio_id,
            symbol=position.symbol,
            action='BUY',
            quantity=position.quantity,
            price=position.entry_price,
            value=position.cost_basis
        )
        
        # Update portfolio in database
        self._update_db()
        
        # Save snapshot
        self._save_snapshot()
    
    def remove_position(self, symbol: str, quantity: Optional[float] = None):
        """Remove position and update database"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        sell_quantity = quantity if quantity else position.quantity
        
        # Record trade before removing
        self.db_manager.record_trade(
            portfolio_id=self.portfolio_id,
            symbol=symbol,
            action='SELL',
            quantity=sell_quantity,
            price=position.current_price,
            value=sell_quantity * position.current_price
        )
        
        # Remove from parent class
        super().remove_position(symbol, quantity)
        
        # Close position in database if fully sold
        if symbol not in self.positions:
            self.db_manager.close_position(self.portfolio_id, symbol)
        else:
            # Update position quantity
            self.db_manager.save_position(
                portfolio_id=self.portfolio_id,
                symbol=symbol,
                quantity=self.positions[symbol].quantity,
                entry_price=self.positions[symbol].entry_price,
                current_price=self.positions[symbol].current_price,
                stop_loss=self.positions[symbol].stop_loss,
                take_profit=self.positions[symbol].take_profit
            )
        
        # Update portfolio in database
        self._update_db()
        
        # Save snapshot
        self._save_snapshot()
    
    def update_prices(self, prices: Dict[str, float]):
        """Update prices and save to database"""
        super().update_prices(prices)
        
        # Update positions in database
        for symbol, position in self.positions.items():
            self.db_manager.save_position(
                portfolio_id=self.portfolio_id,
                symbol=symbol,
                quantity=position.quantity,
                entry_price=position.entry_price,
                current_price=position.current_price,
                stop_loss=position.stop_loss,
                take_profit=position.take_profit
            )
        
        # Update portfolio value
        self._update_db()
    
    def _update_db(self):
        """Update portfolio values in database"""
        self.db_manager.update_portfolio(
            portfolio_id=self.portfolio_id,
            cash=self.cash,
            total_value=self.total_value
        )
    
    def _save_snapshot(self):
        """Save current portfolio state as snapshot"""
        summary = self.get_summary()
        self.db_manager.save_snapshot(
            portfolio_id=self.portfolio_id,
            total_value=summary['total_value'],
            cash=summary['cash'],
            positions_value=summary['positions_value'],
            total_pnl=summary['total_pnl'],
            total_pnl_pct=summary['total_pnl_pct'],
            num_positions=summary['num_positions']
        )
    
    def get_trade_history(self, limit: int = None) -> List:
        """Get trade history from database"""
        return self.db_manager.get_trades(portfolio_id=self.portfolio_id, limit=limit)
    
    def get_snapshots(self, limit: int = None) -> List:
        """Get portfolio snapshots from database"""
        return self.db_manager.get_snapshots(portfolio_id=self.portfolio_id, limit=limit)
    
    def get_stats(self) -> Dict:
        """Get comprehensive statistics from database"""
        return self.db_manager.get_portfolio_stats(self.portfolio_id)
