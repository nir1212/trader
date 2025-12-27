import axios from 'axios';
import type {
  Portfolio,
  PortfolioSummary,
  Trade,
  Signal,
  BotStatus,
  BotConfig,
  Strategy,
  PerformanceMetrics,
  Snapshot
} from '../types';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

// Portfolio
export const getPortfolios = async (): Promise<Portfolio[]> => {
  const response = await api.get('/portfolio/');
  return response.data;
};

export const getPortfolio = async (id: number): Promise<Portfolio> => {
  const response = await api.get(`/portfolio/${id}`);
  return response.data;
};

export const getPortfolioSummary = async (id: number): Promise<PortfolioSummary> => {
  const response = await api.get(`/portfolio/${id}/summary`);
  return response.data;
};

export const getPortfolioSnapshots = async (id: number, limit = 50): Promise<Snapshot[]> => {
  const response = await api.get(`/portfolio/${id}/snapshots`, { params: { limit } });
  return response.data;
};

export const getPortfolioPerformance = async (id: number): Promise<PerformanceMetrics> => {
  const response = await api.get(`/portfolio/${id}/performance`);
  return response.data;
};

export const createPortfolio = async (name: string, initial_capital: number): Promise<Portfolio> => {
  const response = await api.post('/portfolio/', { name, initial_capital });
  return response.data;
};

// Bot Control
export const startBot = async (config: BotConfig) => {
  const response = await api.post('/bot/start', config);
  return response.data;
};

export const stopBot = async () => {
  const response = await api.post('/bot/stop');
  return response.data;
};

export const getBotStatus = async (): Promise<BotStatus> => {
  const response = await api.get('/bot/status');
  return response.data;
};

export const runBotOnce = async (config: BotConfig) => {
  const response = await api.post('/bot/run-once', config);
  return response.data;
};

// Trades & Signals
export const getTrades = async (portfolioId?: number, symbol?: string, limit = 50): Promise<Trade[]> => {
  const params: any = { limit };
  if (portfolioId) params.portfolio_id = portfolioId;
  if (symbol) params.symbol = symbol;
  
  const response = await api.get('/trades/', { params });
  return response.data;
};

export const getSignals = async (
  symbol?: string,
  signalType?: string,
  strategyName?: string,
  limit = 50
): Promise<Signal[]> => {
  const params: any = { limit };
  if (symbol) params.symbol = symbol;
  if (signalType) params.signal_type = signalType;
  if (strategyName) params.strategy_name = strategyName;
  
  const response = await api.get('/trades/signals', { params });
  return response.data;
};

// Strategies
export const getStrategies = async (): Promise<Strategy[]> => {
  const response = await api.get('/strategies/');
  return response.data;
};

export default api;
