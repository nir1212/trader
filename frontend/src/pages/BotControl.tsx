import { useEffect, useState } from 'react';
import { Play, Square, RefreshCw } from 'lucide-react';
import { startBot, stopBot, getBotStatus, getStrategies } from '../services/api';
import type { BotStatus, Strategy, BotConfig } from '../types';

export default function BotControl() {
  const [botStatus, setBotStatus] = useState<BotStatus | null>(null);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(false);
  
  const [config, setConfig] = useState<BotConfig>({
    symbols: ['AAPL', 'MSFT', 'GOOGL'],
    strategies: ['moving_average', 'rsi'],
    paper_trading: true,
    max_position_size: 0.1,
    stop_loss_pct: 0.05,
    take_profit_pct: 0.10,
  });

  useEffect(() => {
    loadData();
    const interval = setInterval(loadBotStatus, 5000); // Check status every 5s
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [statusData, strategiesData] = await Promise.all([
        getBotStatus(),
        getStrategies()
      ]);
      setBotStatus(statusData);
      setStrategies(strategiesData);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const loadBotStatus = async () => {
    try {
      const statusData = await getBotStatus();
      setBotStatus(statusData);
    } catch (error) {
      console.error('Error loading bot status:', error);
    }
  };

  const handleStart = async () => {
    setLoading(true);
    try {
      await startBot(config);
      await loadBotStatus();
      alert('Bot started successfully!');
    } catch (error: any) {
      alert(`Failed to start bot: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      await stopBot();
      await loadBotStatus();
      alert('Bot stopped successfully!');
    } catch (error: any) {
      alert(`Failed to stop bot: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const toggleStrategy = (strategyName: string) => {
    setConfig(prev => ({
      ...prev,
      strategies: prev.strategies.includes(strategyName)
        ? prev.strategies.filter(s => s !== strategyName)
        : [...prev.strategies, strategyName]
    }));
  };

  const addSymbol = () => {
    const symbol = prompt('Enter symbol (e.g., AAPL):');
    if (symbol && !config.symbols.includes(symbol.toUpperCase())) {
      setConfig(prev => ({
        ...prev,
        symbols: [...prev.symbols, symbol.toUpperCase()]
      }));
    }
  };

  const removeSymbol = (symbol: string) => {
    setConfig(prev => ({
      ...prev,
      symbols: prev.symbols.filter(s => s !== symbol)
    }));
  };

  const isRunning = botStatus?.is_running || false;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Bot Control</h1>
        <p className="text-gray-600">Start, stop, and configure your trading bot</p>
      </div>

      {/* Bot Status */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">Bot Status</h2>
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${isRunning ? 'bg-green-500' : 'bg-gray-400'}`} />
            <span className="text-sm font-medium text-gray-700">
              {isRunning ? 'Running' : 'Stopped'}
            </span>
          </div>
        </div>

        {botStatus && isRunning && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-gray-600">Symbols</p>
              <p className="font-medium">{botStatus.symbols.join(', ')}</p>
            </div>
            <div>
              <p className="text-gray-600">Strategies</p>
              <p className="font-medium">{botStatus.strategies.length}</p>
            </div>
            <div>
              <p className="text-gray-600">Uptime</p>
              <p className="font-medium">
                {botStatus.uptime_seconds ? `${Math.floor(botStatus.uptime_seconds / 60)}m` : '-'}
              </p>
            </div>
            <div>
              <p className="text-gray-600">Portfolio ID</p>
              <p className="font-medium">{botStatus.portfolio_id || '-'}</p>
            </div>
          </div>
        )}

        <div className="flex gap-4 mt-6">
          <button
            onClick={handleStart}
            disabled={isRunning || loading}
            className="flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
          >
            <Play className="w-5 h-5" />
            Start Bot
          </button>
          <button
            onClick={handleStop}
            disabled={!isRunning || loading}
            className="flex items-center gap-2 px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
          >
            <Square className="w-5 h-5" />
            Stop Bot
          </button>
          <button
            onClick={loadBotStatus}
            disabled={loading}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition"
          >
            <RefreshCw className="w-5 h-5" />
            Refresh
          </button>
        </div>
      </div>

      {/* Configuration */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Configuration</h2>

        {/* Symbols */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Trading Symbols
          </label>
          <div className="flex flex-wrap gap-2 mb-2">
            {config.symbols.map(symbol => (
              <span
                key={symbol}
                className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
              >
                {symbol}
                <button
                  onClick={() => removeSymbol(symbol)}
                  className="hover:text-blue-600"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
          <button
            onClick={addSymbol}
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            + Add Symbol
          </button>
        </div>

        {/* Strategies */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Trading Strategies
          </label>
          <div className="space-y-2">
            {strategies.map(strategy => (
              <label key={strategy.name} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={config.strategies.includes(strategy.name)}
                  onChange={() => toggleStrategy(strategy.name)}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <span className="text-sm text-gray-700">{strategy.description}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Risk Settings */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Position Size (% of portfolio)
            </label>
            <input
              type="number"
              value={config.max_position_size * 100}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                max_position_size: parseFloat(e.target.value) / 100
              }))}
              min="1"
              max="100"
              step="1"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Stop Loss (%)
            </label>
            <input
              type="number"
              value={config.stop_loss_pct * 100}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                stop_loss_pct: parseFloat(e.target.value) / 100
              }))}
              min="1"
              max="50"
              step="0.5"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Take Profit (%)
            </label>
            <input
              type="number"
              value={config.take_profit_pct * 100}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                take_profit_pct: parseFloat(e.target.value) / 100
              }))}
              min="1"
              max="100"
              step="0.5"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Trading Mode
            </label>
            <select
              value={config.paper_trading ? 'paper' : 'live'}
              onChange={(e) => setConfig(prev => ({
                ...prev,
                paper_trading: e.target.value === 'paper'
              }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="paper">Paper Trading (Simulation)</option>
              <option value="live">Live Trading (Real Money)</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}
