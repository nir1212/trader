import pandas as pd
import numpy as np
from typing import List, Dict, Any
from datetime import datetime
import matplotlib.pyplot as plt

from trader.core.strategy import Strategy, Signal, SignalType
from trader.core.portfolio import Portfolio, Position, PositionType
from trader.risk.risk_manager import RiskManager


class BacktestEngine:
    """Backtesting engine for trading strategies"""
    
    def __init__(
        self,
        initial_capital: float,
        strategies: List[Strategy],
        risk_manager: RiskManager = None
    ):
        self.initial_capital = initial_capital
        self.strategies = strategies
        self.risk_manager = risk_manager
        self.results = None
        
    def run_backtest(
        self,
        symbol: str,
        data: pd.DataFrame,
        commission: float = 0.001
    ) -> Dict[str, Any]:
        """
        Run backtest on historical data
        
        Args:
            symbol: Trading symbol
            data: Historical OHLCV data
            commission: Commission rate (default 0.1%)
        
        Returns:
            Dictionary with backtest results
        """
        portfolio = Portfolio(self.initial_capital)
        trades = []
        equity_curve = []
        
        # Iterate through data
        for i in range(len(data)):
            if i < 50:  # Need enough data for indicators
                continue
            
            current_data = data.iloc[:i+1].copy()
            current_price = current_data['close'].iloc[-1]
            current_date = current_data.index[-1]
            
            # Update portfolio prices
            if portfolio.has_position(symbol):
                portfolio.update_prices({symbol: current_price})
            
            # Generate signals
            signals = []
            for strategy in self.strategies:
                try:
                    signal = strategy.generate_signal(symbol, current_data)
                    signals.append(signal)
                except Exception as e:
                    continue
            
            # Aggregate signals
            final_signal = self._aggregate_signals(signals, symbol, current_price)
            
            # Process signal
            if final_signal.signal_type == SignalType.BUY and not portfolio.has_position(symbol):
                # Calculate position size
                if self.risk_manager:
                    quantity = self.risk_manager.calculate_position_size(final_signal, portfolio)
                else:
                    quantity = (portfolio.cash * 0.95) / current_price
                
                if quantity > 0:
                    cost = quantity * current_price * (1 + commission)
                    
                    if cost <= portfolio.cash:
                        position = Position(
                            symbol=symbol,
                            quantity=quantity,
                            entry_price=current_price,
                            current_price=current_price
                        )
                        
                        if self.risk_manager:
                            position.stop_loss = self.risk_manager.calculate_stop_loss(final_signal)
                            position.take_profit = self.risk_manager.calculate_take_profit(final_signal)
                        
                        portfolio.add_position(position)
                        
                        trades.append({
                            'date': current_date,
                            'action': 'BUY',
                            'price': current_price,
                            'quantity': quantity,
                            'value': cost
                        })
            
            elif final_signal.signal_type == SignalType.SELL and portfolio.has_position(symbol):
                position = portfolio.get_position(symbol)
                quantity = position.quantity
                value = quantity * current_price * (1 - commission)
                
                portfolio.remove_position(symbol)
                
                trades.append({
                    'date': current_date,
                    'action': 'SELL',
                    'price': current_price,
                    'quantity': quantity,
                    'value': value
                })
            
            # Check stop-loss and take-profit
            if portfolio.has_position(symbol):
                position = portfolio.get_position(symbol)
                
                if position.should_stop_loss():
                    quantity = position.quantity
                    value = quantity * current_price * (1 - commission)
                    portfolio.remove_position(symbol)
                    
                    trades.append({
                        'date': current_date,
                        'action': 'STOP_LOSS',
                        'price': current_price,
                        'quantity': quantity,
                        'value': value
                    })
                
                elif position.should_take_profit():
                    quantity = position.quantity
                    value = quantity * current_price * (1 - commission)
                    portfolio.remove_position(symbol)
                    
                    trades.append({
                        'date': current_date,
                        'action': 'TAKE_PROFIT',
                        'price': current_price,
                        'quantity': quantity,
                        'value': value
                    })
            
            # Record equity
            equity_curve.append({
                'date': current_date,
                'equity': portfolio.total_value,
                'cash': portfolio.cash,
                'positions_value': portfolio.positions_value
            })
        
        # Close any remaining positions
        if portfolio.positions:
            final_price = data['close'].iloc[-1]
            for symbol in list(portfolio.positions.keys()):
                position = portfolio.get_position(symbol)
                quantity = position.quantity
                value = quantity * final_price * (1 - commission)
                portfolio.remove_position(symbol)
                
                trades.append({
                    'date': data.index[-1],
                    'action': 'CLOSE',
                    'price': final_price,
                    'quantity': quantity,
                    'value': value
                })
        
        # Calculate metrics
        metrics = self._calculate_metrics(
            portfolio,
            pd.DataFrame(equity_curve),
            pd.DataFrame(trades)
        )
        
        self.results = {
            'metrics': metrics,
            'trades': pd.DataFrame(trades),
            'equity_curve': pd.DataFrame(equity_curve),
            'final_portfolio': portfolio.get_summary()
        }
        
        return self.results
    
    def _aggregate_signals(self, signals: List[Signal], symbol: str, price: float) -> Signal:
        """Aggregate multiple signals"""
        if not signals:
            return Signal(SignalType.HOLD, symbol, price)
        
        buy_count = sum(1 for s in signals if s.signal_type == SignalType.BUY)
        sell_count = sum(1 for s in signals if s.signal_type == SignalType.SELL)
        
        if buy_count > sell_count:
            return Signal(SignalType.BUY, symbol, price)
        elif sell_count > buy_count:
            return Signal(SignalType.SELL, symbol, price)
        else:
            return Signal(SignalType.HOLD, symbol, price)
    
    def _calculate_metrics(
        self,
        portfolio: Portfolio,
        equity_curve: pd.DataFrame,
        trades: pd.DataFrame
    ) -> Dict[str, Any]:
        """Calculate performance metrics"""
        
        total_return = portfolio.total_pnl_pct
        
        # Calculate returns
        equity_curve['returns'] = equity_curve['equity'].pct_change()
        
        # Sharpe Ratio (annualized)
        if len(equity_curve) > 1:
            returns_std = equity_curve['returns'].std()
            if returns_std > 0:
                sharpe_ratio = (equity_curve['returns'].mean() / returns_std) * np.sqrt(252)
            else:
                sharpe_ratio = 0
        else:
            sharpe_ratio = 0
        
        # Max Drawdown
        equity_curve['cummax'] = equity_curve['equity'].cummax()
        equity_curve['drawdown'] = (equity_curve['equity'] - equity_curve['cummax']) / equity_curve['cummax']
        max_drawdown = equity_curve['drawdown'].min() * 100
        
        # Win Rate
        if len(trades) > 0:
            winning_trades = 0
            losing_trades = 0
            
            for i in range(0, len(trades), 2):
                if i + 1 < len(trades):
                    buy_trade = trades.iloc[i]
                    sell_trade = trades.iloc[i + 1]
                    
                    if sell_trade['value'] > buy_trade['value']:
                        winning_trades += 1
                    else:
                        losing_trades += 1
            
            total_trades = winning_trades + losing_trades
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        else:
            win_rate = 0
            total_trades = 0
        
        return {
            'initial_capital': self.initial_capital,
            'final_value': portfolio.total_value,
            'total_return': total_return,
            'total_return_pct': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': len(trades),
            'win_rate': win_rate
        }
    
    def plot_results(self, save_path: str = None):
        """Plot backtest results"""
        if not self.results:
            print("No results to plot. Run backtest first.")
            return
        
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        
        equity_curve = self.results['equity_curve']
        trades = self.results['trades']
        
        # Plot equity curve
        axes[0].plot(equity_curve['date'], equity_curve['equity'], label='Portfolio Value')
        axes[0].axhline(y=self.initial_capital, color='r', linestyle='--', label='Initial Capital')
        axes[0].set_title('Equity Curve')
        axes[0].set_ylabel('Value ($)')
        axes[0].legend()
        axes[0].grid(True)
        
        # Plot drawdown
        equity_curve['cummax'] = equity_curve['equity'].cummax()
        equity_curve['drawdown'] = (equity_curve['equity'] - equity_curve['cummax']) / equity_curve['cummax'] * 100
        axes[1].fill_between(equity_curve['date'], equity_curve['drawdown'], 0, alpha=0.3, color='red')
        axes[1].set_title('Drawdown')
        axes[1].set_ylabel('Drawdown (%)')
        axes[1].grid(True)
        
        # Plot trades
        buy_trades = trades[trades['action'] == 'BUY']
        sell_trades = trades[trades['action'].isin(['SELL', 'STOP_LOSS', 'TAKE_PROFIT', 'CLOSE'])]
        
        axes[2].scatter(buy_trades['date'], buy_trades['price'], color='green', marker='^', s=100, label='Buy')
        axes[2].scatter(sell_trades['date'], sell_trades['price'], color='red', marker='v', s=100, label='Sell')
        axes[2].set_title('Trade Signals')
        axes[2].set_ylabel('Price ($)')
        axes[2].legend()
        axes[2].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            print(f"Plot saved to {save_path}")
        else:
            plt.show()
    
    def print_summary(self):
        """Print backtest summary"""
        if not self.results:
            print("No results to display. Run backtest first.")
            return
        
        metrics = self.results['metrics']
        
        print("\n" + "="*50)
        print("BACKTEST RESULTS")
        print("="*50)
        print(f"Initial Capital:    ${metrics['initial_capital']:,.2f}")
        print(f"Final Value:        ${metrics['final_value']:,.2f}")
        print(f"Total Return:       ${metrics['final_value'] - metrics['initial_capital']:,.2f}")
        print(f"Total Return %:     {metrics['total_return_pct']:.2f}%")
        print(f"Sharpe Ratio:       {metrics['sharpe_ratio']:.2f}")
        print(f"Max Drawdown:       {metrics['max_drawdown']:.2f}%")
        print(f"Total Trades:       {metrics['total_trades']}")
        print(f"Win Rate:           {metrics['win_rate']:.2f}%")
        print("="*50 + "\n")
