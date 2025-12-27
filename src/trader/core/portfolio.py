from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class PositionType(Enum):
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass
class Position:
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    position_type: PositionType = PositionType.LONG
    entry_time: datetime = field(default_factory=datetime.now)
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    @property
    def value(self) -> float:
        return self.quantity * self.current_price
    
    @property
    def cost_basis(self) -> float:
        return self.quantity * self.entry_price
    
    @property
    def unrealized_pnl(self) -> float:
        if self.position_type == PositionType.LONG:
            return (self.current_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - self.current_price) * self.quantity
    
    @property
    def unrealized_pnl_pct(self) -> float:
        if self.cost_basis == 0:
            return 0.0
        return (self.unrealized_pnl / self.cost_basis) * 100
    
    def update_price(self, new_price: float):
        self.current_price = new_price
    
    def should_stop_loss(self) -> bool:
        if self.stop_loss is None:
            return False
        if self.position_type == PositionType.LONG:
            return self.current_price <= self.stop_loss
        else:
            return self.current_price >= self.stop_loss
    
    def should_take_profit(self) -> bool:
        if self.take_profit is None:
            return False
        if self.position_type == PositionType.LONG:
            return self.current_price >= self.take_profit
        else:
            return self.current_price <= self.take_profit


class Portfolio:
    """Portfolio management and tracking"""
    
    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[Dict] = []
        
    @property
    def total_value(self) -> float:
        positions_value = sum(pos.value for pos in self.positions.values())
        return self.cash + positions_value
    
    @property
    def total_pnl(self) -> float:
        return self.total_value - self.initial_capital
    
    @property
    def total_pnl_pct(self) -> float:
        return (self.total_pnl / self.initial_capital) * 100
    
    @property
    def positions_value(self) -> float:
        return sum(pos.value for pos in self.positions.values())
    
    def add_position(self, position: Position):
        """Add or update a position"""
        if position.symbol in self.positions:
            existing = self.positions[position.symbol]
            total_quantity = existing.quantity + position.quantity
            avg_price = (existing.entry_price * existing.quantity + 
                        position.entry_price * position.quantity) / total_quantity
            existing.quantity = total_quantity
            existing.entry_price = avg_price
        else:
            self.positions[position.symbol] = position
        
        self.cash -= position.cost_basis
        self._record_trade("BUY", position)
    
    def remove_position(self, symbol: str, quantity: Optional[float] = None):
        """Remove or reduce a position"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        sell_quantity = quantity if quantity else position.quantity
        
        if sell_quantity >= position.quantity:
            self.cash += position.value
            self._record_trade("SELL", position)
            del self.positions[symbol]
        else:
            self.cash += sell_quantity * position.current_price
            position.quantity -= sell_quantity
            self._record_trade("SELL_PARTIAL", position, sell_quantity)
    
    def update_prices(self, prices: Dict[str, float]):
        """Update current prices for all positions"""
        for symbol, price in prices.items():
            if symbol in self.positions:
                self.positions[symbol].update_price(price)
    
    def get_position(self, symbol: str) -> Optional[Position]:
        return self.positions.get(symbol)
    
    def has_position(self, symbol: str) -> bool:
        return symbol in self.positions
    
    def _record_trade(self, action: str, position: Position, quantity: Optional[float] = None):
        """Record trade in history"""
        trade = {
            'timestamp': datetime.now(),
            'action': action,
            'symbol': position.symbol,
            'quantity': quantity if quantity else position.quantity,
            'price': position.current_price,
            'value': (quantity if quantity else position.quantity) * position.current_price
        }
        self.trade_history.append(trade)
    
    def get_summary(self) -> Dict:
        """Get portfolio summary"""
        return {
            'initial_capital': self.initial_capital,
            'cash': self.cash,
            'positions_value': self.positions_value,
            'total_value': self.total_value,
            'total_pnl': self.total_pnl,
            'total_pnl_pct': self.total_pnl_pct,
            'num_positions': len(self.positions),
            'positions': {symbol: {
                'quantity': pos.quantity,
                'entry_price': pos.entry_price,
                'current_price': pos.current_price,
                'value': pos.value,
                'pnl': pos.unrealized_pnl,
                'pnl_pct': pos.unrealized_pnl_pct
            } for symbol, pos in self.positions.items()}
        }
