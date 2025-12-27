from typing import Optional
from trader.core.strategy import Signal, SignalType
from trader.core.portfolio import Portfolio


class RiskManager:
    """Risk management for trading operations"""
    
    def __init__(
        self,
        max_position_size: float = 0.1,
        max_portfolio_risk: float = 0.02,
        stop_loss_pct: float = 0.05,
        take_profit_pct: float = 0.10,
        max_positions: int = 10
    ):
        self.max_position_size = max_position_size
        self.max_portfolio_risk = max_portfolio_risk
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.max_positions = max_positions
    
    def can_trade(self, signal: Signal, portfolio: Portfolio) -> bool:
        """Check if trade is allowed based on risk rules"""
        
        # Check if we're at max positions
        if signal.signal_type == SignalType.BUY:
            if len(portfolio.positions) >= self.max_positions:
                return False
        
        # Check if we have enough cash
        if signal.signal_type == SignalType.BUY:
            estimated_cost = self.calculate_position_size(signal, portfolio) * signal.price
            if estimated_cost > portfolio.cash:
                return False
        
        # Check if position exists for sell
        if signal.signal_type == SignalType.SELL:
            if not portfolio.has_position(signal.symbol):
                return False
        
        return True
    
    def calculate_position_size(self, signal: Signal, portfolio: Portfolio) -> float:
        """Calculate position size based on risk management rules"""
        
        if signal.signal_type != SignalType.BUY:
            return 0.0
        
        # Calculate based on max position size
        max_position_value = portfolio.total_value * self.max_position_size
        
        # Calculate based on risk per trade
        risk_amount = portfolio.total_value * self.max_portfolio_risk
        stop_loss_distance = signal.price * self.stop_loss_pct
        risk_based_quantity = risk_amount / stop_loss_distance if stop_loss_distance > 0 else 0
        
        # Use the more conservative approach
        position_value = min(max_position_value, risk_based_quantity * signal.price)
        
        # Ensure we don't exceed available cash
        position_value = min(position_value, portfolio.cash * 0.95)  # Keep 5% cash buffer
        
        quantity = position_value / signal.price
        
        return max(0, quantity)
    
    def calculate_stop_loss(self, signal: Signal) -> float:
        """Calculate stop-loss price"""
        if signal.signal_type == SignalType.BUY:
            return signal.price * (1 - self.stop_loss_pct)
        return 0.0
    
    def calculate_take_profit(self, signal: Signal) -> float:
        """Calculate take-profit price"""
        if signal.signal_type == SignalType.BUY:
            return signal.price * (1 + self.take_profit_pct)
        return 0.0
    
    def check_drawdown(self, portfolio: Portfolio) -> bool:
        """Check if portfolio drawdown exceeds limits"""
        drawdown_pct = abs(portfolio.total_pnl_pct)
        max_drawdown = 20.0  # 20% max drawdown
        
        if drawdown_pct > max_drawdown:
            return False
        return True
