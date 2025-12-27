from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging
from datetime import datetime
import pandas as pd

from trader.core.strategy import Strategy, Signal, SignalType
from trader.core.portfolio import Portfolio, Position, PositionType
from trader.risk.risk_manager import RiskManager


class BaseBot(ABC):
    """Base class for all trading bots"""
    
    def __init__(
        self,
        name: str,
        portfolio: Portfolio,
        strategies: List[Strategy],
        risk_manager: Optional[RiskManager] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.name = name
        self.portfolio = portfolio
        self.strategies = strategies
        self.risk_manager = risk_manager
        self.logger = logger or logging.getLogger(self.name)
        self.is_running = False
        
    @abstractmethod
    def connect(self):
        """Connect to trading API/exchange"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Disconnect from trading API/exchange"""
        pass
    
    @abstractmethod
    def get_market_data(self, symbol: str, timeframe: str = '1d', limit: int = 100) -> pd.DataFrame:
        """Fetch market data for a symbol"""
        pass
    
    @abstractmethod
    def execute_order(self, signal: Signal) -> bool:
        """Execute a trading order"""
        pass
    
    @abstractmethod
    def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        pass
    
    def start(self):
        """Start the trading bot"""
        self.logger.info(f"Starting {self.name}...")
        self.connect()
        self.is_running = True
        self.logger.info(f"{self.name} started successfully")
    
    def stop(self):
        """Stop the trading bot"""
        self.logger.info(f"Stopping {self.name}...")
        self.is_running = False
        self.disconnect()
        self.logger.info(f"{self.name} stopped")
    
    def run_strategies(self, symbol: str) -> List[Signal]:
        """Run all strategies and collect signals"""
        signals = []
        
        try:
            data = self.get_market_data(symbol)
            
            if data is None or data.empty:
                self.logger.warning(f"No data available for {symbol}")
                return signals
            
            for strategy in self.strategies:
                try:
                    signal = strategy.generate_signal(symbol, data)
                    signals.append(signal)
                    self.logger.debug(f"{strategy.name}: {signal}")
                except Exception as e:
                    self.logger.error(f"Error in {strategy.name} for {symbol}: {e}")
        
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
        
        return signals
    
    def aggregate_signals(self, signals: List[Signal]) -> Signal:
        """Aggregate multiple signals into one decision"""
        if not signals:
            return Signal(SignalType.HOLD, signals[0].symbol if signals else "", 0.0)
        
        buy_count = sum(1 for s in signals if s.signal_type == SignalType.BUY)
        sell_count = sum(1 for s in signals if s.signal_type == SignalType.SELL)
        
        symbol = signals[0].symbol
        price = signals[0].price
        
        if buy_count > sell_count:
            confidence = buy_count / len(signals)
            return Signal(SignalType.BUY, symbol, price, confidence=confidence)
        elif sell_count > buy_count:
            confidence = sell_count / len(signals)
            return Signal(SignalType.SELL, symbol, price, confidence=confidence)
        else:
            return Signal(SignalType.HOLD, symbol, price)
    
    def process_signal(self, signal: Signal) -> bool:
        """Process a trading signal"""
        if signal.signal_type == SignalType.HOLD:
            return False
        
        # Check risk management
        if self.risk_manager:
            if not self.risk_manager.can_trade(signal, self.portfolio):
                self.logger.warning(f"Risk manager rejected trade: {signal}")
                return False
            
            # Calculate position size
            signal.quantity = self.risk_manager.calculate_position_size(
                signal, self.portfolio
            )
        
        # Execute the order
        try:
            success = self.execute_order(signal)
            if success:
                self.logger.info(f"Executed: {signal}")
                self._update_portfolio(signal)
            return success
        except Exception as e:
            self.logger.error(f"Failed to execute {signal}: {e}")
            return False
    
    def _update_portfolio(self, signal: Signal):
        """Update portfolio after trade execution"""
        if signal.signal_type == SignalType.BUY:
            position = Position(
                symbol=signal.symbol,
                quantity=signal.quantity,
                entry_price=signal.price,
                current_price=signal.price,
                position_type=PositionType.LONG
            )
            
            if self.risk_manager:
                position.stop_loss = self.risk_manager.calculate_stop_loss(signal)
                position.take_profit = self.risk_manager.calculate_take_profit(signal)
            
            self.portfolio.add_position(position)
            
        elif signal.signal_type == SignalType.SELL:
            self.portfolio.remove_position(signal.symbol, signal.quantity)
    
    def check_positions(self):
        """Check all positions for stop-loss or take-profit"""
        for symbol, position in list(self.portfolio.positions.items()):
            try:
                current_price = self.get_current_price(symbol)
                position.update_price(current_price)
                
                if position.should_stop_loss():
                    self.logger.warning(f"Stop-loss triggered for {symbol}")
                    signal = Signal(SignalType.SELL, symbol, current_price, position.quantity)
                    self.process_signal(signal)
                    
                elif position.should_take_profit():
                    self.logger.info(f"Take-profit triggered for {symbol}")
                    signal = Signal(SignalType.SELL, symbol, current_price, position.quantity)
                    self.process_signal(signal)
                    
            except Exception as e:
                self.logger.error(f"Error checking position {symbol}: {e}")
    
    def get_portfolio_summary(self) -> Dict:
        """Get current portfolio summary"""
        return self.portfolio.get_summary()
