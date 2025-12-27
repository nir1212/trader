export interface Portfolio {
  id: number;
  name: string;
  initial_capital: number;
  current_cash: number;
  total_value: number;
  created_at: string;
  is_active: boolean;
}

export interface PortfolioSummary {
  initial_capital: number;
  cash: number;
  positions_value: number;
  total_value: number;
  total_pnl: number;
  total_pnl_pct: number;
  num_positions: number;
  positions: Record<string, Position>;
}

export interface Position {
  quantity: number;
  entry_price: number;
  current_price: number;
  value: number;
  pnl: number;
  pnl_pct: number;
}

export interface Trade {
  id: number;
  timestamp: string;
  symbol: string;
  action: string;
  quantity: number;
  price: number;
  value: number;
  strategy_name?: string;
}

export interface Signal {
  id: number;
  timestamp: string;
  symbol: string;
  signal_type: string;
  strategy_name: string;
  price: number;
  confidence: number;
  executed: boolean;
}

export interface BotStatus {
  status: 'running' | 'stopped' | 'error';
  is_running: boolean;
  portfolio_id?: number;
  symbols: string[];
  strategies: string[];
  uptime_seconds?: number;
}

export interface BotConfig {
  symbols: string[];
  strategies: string[];
  paper_trading: boolean;
  max_position_size: number;
  stop_loss_pct: number;
  take_profit_pct: number;
}

export interface Strategy {
  name: string;
  description: string;
  parameters: Record<string, any>;
}

export interface PerformanceMetrics {
  total_return: number;
  total_return_pct: number;
  win_rate: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
}

export interface Snapshot {
  id: number;
  timestamp: string;
  total_value: number;
  cash: number;
  positions_value: number;
  total_pnl: number;
  total_pnl_pct: number;
  num_positions: number;
}
