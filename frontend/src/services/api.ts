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
  Snapshot,
  Bot,
  CreateBotRequest,
  UpdateBotRequest,
  AvailableStrategy
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

// Bot Control (Legacy - single bot)
export const startLegacyBot = async (config: BotConfig) => {
  const response = await api.post('/bot/start', config);
  return response.data;
};

export const stopLegacyBot = async () => {
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

// Bot Management
export const createBot = async (botData: CreateBotRequest): Promise<Bot> => {
  const response = await api.post('/bots/', botData);
  return response.data;
};

export const getBots = async (activeOnly = true): Promise<Bot[]> => {
  const response = await api.get('/bots/', { params: { active_only: activeOnly } });
  return response.data;
};

export const getBot = async (botId: number): Promise<Bot> => {
  const response = await api.get(`/bots/${botId}`);
  return response.data;
};

export const updateBot = async (botId: number, updates: UpdateBotRequest): Promise<Bot> => {
  const response = await api.put(`/bots/${botId}`, updates);
  return response.data;
};

export const deleteBot = async (botId: number): Promise<void> => {
  await api.delete(`/bots/${botId}`);
};

export const startBot = async (botId: number, apiKey?: string, apiSecret?: string): Promise<Bot> => {
  const response = await api.post(`/bots/${botId}/start`, {
    api_key: apiKey,
    api_secret: apiSecret
  });
  return response.data;
};

export const stopBot = async (botId: number): Promise<Bot> => {
  const response = await api.post(`/bots/${botId}/stop`);
  return response.data;
};

export const restartBot = async (botId: number): Promise<Bot> => {
  const response = await api.post(`/bots/${botId}/restart`);
  return response.data;
};

export const getBotSignals = async (botId: number, limit = 50): Promise<Signal[]> => {
  const response = await api.get(`/bots/${botId}/signals`, { params: { limit } });
  return response.data;
};

export const getAvailableStrategies = async (): Promise<AvailableStrategy[]> => {
  const response = await api.get('/bots/strategies/available');
  return response.data.strategies;
};

export default api;
