import { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardActions,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  IconButton,
  TextField,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  CircularProgress,
  Fab,
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow,
  Stop,
  Delete,
  Edit,
  Refresh,
  SmartToy,
} from '@mui/icons-material';
import {
  getBots,
  createBot,
  startBot,
  stopBot,
  deleteBot,
  getAvailableStrategies,
  getPortfolios,
} from '../services/api';
import type { Bot, CreateBotRequest, AvailableStrategy, Portfolio } from '../types';

export default function BotControl() {
  const [bots, setBots] = useState<Bot[]>([]);
  const [strategies, setStrategies] = useState<AvailableStrategy[]>([]);
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [loading, setLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newBot, setNewBot] = useState<CreateBotRequest>({
    name: '',
    description: '',
    portfolio_id: 1,
    config: {
      symbols: [],
      strategies: [],
      initial_capital: 10000,
      paper_trading: true,
      timeframe: '1d',
      run_interval_seconds: 60,
      max_position_size: 0.1,
      stop_loss_pct: 0.05,
      take_profit_pct: 0.10,
      max_portfolio_risk: 0.02,
    },
  });
  const [symbolInput, setSymbolInput] = useState('');

  useEffect(() => {
    loadData();
    const interval = setInterval(loadBots, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [botsData, strategiesData, portfoliosData] = await Promise.all([
        getBots(),
        getAvailableStrategies(),
        getPortfolios(),
      ]);
      setBots(Array.isArray(botsData) ? botsData : []);
      setStrategies(Array.isArray(strategiesData) ? strategiesData : []);
      setPortfolios(Array.isArray(portfoliosData) ? portfoliosData : []);
    } catch (error) {
      console.error('Error loading data:', error);
      setBots([]);
      setStrategies([]);
      setPortfolios([]);
    } finally {
      setLoading(false);
    }
  };

  const loadBots = async () => {
    try {
      const botsData = await getBots();
      setBots(Array.isArray(botsData) ? botsData : []);
    } catch (error) {
      console.error('Error loading bots:', error);
      setBots([]);
    }
  };

  const handleCreateBot = async () => {
    try {
      await createBot(newBot);
      setCreateDialogOpen(false);
      resetNewBot();
      loadBots();
    } catch (error: any) {
      alert(`Failed to create bot: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleStartBot = async (botId: number) => {
    try {
      await startBot(botId);
      loadBots();
    } catch (error: any) {
      alert(`Failed to start bot: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleStopBot = async (botId: number) => {
    try {
      await stopBot(botId);
      loadBots();
    } catch (error: any) {
      alert(`Failed to stop bot: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleDeleteBot = async (botId: number) => {
    if (confirm('Are you sure you want to delete this bot?')) {
      try {
        await deleteBot(botId);
        loadBots();
      } catch (error: any) {
        alert(`Failed to delete bot: ${error.response?.data?.detail || error.message}`);
      }
    }
  };

  const resetNewBot = () => {
    setNewBot({
      name: '',
      description: '',
      portfolio_id: portfolios[0]?.id || 1,
      config: {
        symbols: [],
        strategies: [],
        initial_capital: 10000,
        paper_trading: true,
        timeframe: '1d',
        run_interval_seconds: 60,
        max_position_size: 0.1,
        stop_loss_pct: 0.05,
        take_profit_pct: 0.10,
        max_portfolio_risk: 0.02,
      },
    });
    setSymbolInput('');
  };

  const addSymbol = () => {
    if (symbolInput && !newBot.config.symbols.includes(symbolInput.toUpperCase())) {
      setNewBot(prev => ({
        ...prev,
        config: {
          ...prev.config,
          symbols: [...prev.config.symbols, symbolInput.toUpperCase()],
        },
      }));
      setSymbolInput('');
    }
  };

  const removeSymbol = (symbol: string) => {
    setNewBot(prev => ({
      ...prev,
      config: {
        ...prev.config,
        symbols: prev.config.symbols.filter(s => s !== symbol),
      },
    }));
  };

  const toggleStrategy = (strategyName: string) => {
    setNewBot(prev => ({
      ...prev,
      config: {
        ...prev.config,
        strategies: prev.config.strategies.includes(strategyName)
          ? prev.config.strategies.filter(s => s !== strategyName)
          : [...prev.config.strategies, strategyName],
      },
    }));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'success';
      case 'stopped': return 'default';
      case 'error': return 'error';
      case 'paused': return 'warning';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            Bot Management
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Create and manage your trading bots
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
          size="large"
        >
          Create Bot
        </Button>
      </Box>

      {bots.length === 0 ? (
        <Card>
          <CardContent>
            <Box textAlign="center" py={4}>
              <SmartToy sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                No bots yet
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Create your first trading bot to get started
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setCreateDialogOpen(true)}
              >
                Create Bot
              </Button>
            </Box>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {bots.map(bot => (
            <Grid item xs={12} md={6} lg={4} key={bot.id} component="div">
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
                    <Box>
                      <Typography variant="h6" fontWeight="bold">
                        {bot.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {bot.description || 'No description'}
                      </Typography>
                    </Box>
                    <Chip
                      label={bot.status}
                      color={getStatusColor(bot.status) as any}
                      size="small"
                    />
                  </Box>

                  <Box mb={2}>
                    <Typography variant="caption" color="text.secondary">
                      Symbols
                    </Typography>
                    <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
                      {bot.config.symbols.map(symbol => (
                        <Chip key={symbol} label={symbol} size="small" variant="outlined" />
                      ))}
                    </Box>
                  </Box>

                  <Box mb={2}>
                    <Typography variant="caption" color="text.secondary">
                      Strategies
                    </Typography>
                    <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
                      {bot.config.strategies.map(strategy => (
                        <Chip key={strategy} label={strategy} size="small" color="primary" variant="outlined" />
                      ))}
                    </Box>
                  </Box>

                  <Box display="grid" gridTemplateColumns="1fr 1fr" gap={1}>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Position Size
                      </Typography>
                      <Typography variant="body2">
                        {(bot.config.max_position_size * 100).toFixed(0)}%
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Stop Loss
                      </Typography>
                      <Typography variant="body2">
                        {(bot.config.stop_loss_pct * 100).toFixed(1)}%
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
                <CardActions>
                  {bot.is_running ? (
                    <Button
                      size="small"
                      startIcon={<Stop />}
                      onClick={() => handleStopBot(bot.id)}
                      color="error"
                    >
                      Stop
                    </Button>
                  ) : (
                    <Button
                      size="small"
                      startIcon={<PlayArrow />}
                      onClick={() => handleStartBot(bot.id)}
                      color="success"
                    >
                      Start
                    </Button>
                  )}
                  <Button
                    size="small"
                    startIcon={<Delete />}
                    onClick={() => handleDeleteBot(bot.id)}
                    color="error"
                    disabled={bot.is_running}
                  >
                    Delete
                  </Button>
                  <Box flexGrow={1} />
                  <IconButton size="small" onClick={loadBots}>
                    <Refresh />
                  </IconButton>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Create Bot Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Bot</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Bot Name"
              value={newBot.name}
              onChange={(e) => setNewBot(prev => ({ ...prev, name: e.target.value }))}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Description"
              value={newBot.description}
              onChange={(e) => setNewBot(prev => ({ ...prev, description: e.target.value }))}
              margin="normal"
              multiline
              rows={2}
            />

            <FormControl fullWidth margin="normal">
              <InputLabel>Portfolio</InputLabel>
              <Select
                value={newBot.portfolio_id}
                onChange={(e) => setNewBot(prev => ({ ...prev, portfolio_id: e.target.value as number }))}
                label="Portfolio"
              >
                {portfolios.map(p => (
                  <MenuItem key={p.id} value={p.id}>{p.name}</MenuItem>
                ))}
              </Select>
            </FormControl>

            <Box mt={2}>
              <Typography variant="subtitle2" gutterBottom>
                Trading Symbols
              </Typography>
              <Box display="flex" gap={1} mb={1}>
                <TextField
                  size="small"
                  placeholder="e.g., AAPL"
                  value={symbolInput}
                  onChange={(e) => setSymbolInput(e.target.value.toUpperCase())}
                  onKeyPress={(e) => e.key === 'Enter' && addSymbol()}
                />
                <Button onClick={addSymbol} variant="outlined">Add</Button>
              </Box>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {newBot.config.symbols.map(symbol => (
                  <Chip
                    key={symbol}
                    label={symbol}
                    onDelete={() => removeSymbol(symbol)}
                    color="primary"
                  />
                ))}
              </Box>
            </Box>

            <Box mt={2}>
              <Typography variant="subtitle2" gutterBottom>
                Strategies
              </Typography>
              {strategies.map(strategy => (
                <FormControlLabel
                  key={strategy.name}
                  control={
                    <Checkbox
                      checked={newBot.config.strategies.includes(strategy.name)}
                      onChange={() => toggleStrategy(strategy.name)}
                    />
                  }
                  label={`${strategy.display_name} - ${strategy.description}`}
                />
              ))}
            </Box>

            <Grid container spacing={2} mt={1}>
              <Grid item xs={6} component="div">
                <TextField
                  fullWidth
                  type="number"
                  label="Initial Capital"
                  value={newBot.config.initial_capital}
                  onChange={(e) => setNewBot(prev => ({
                    ...prev,
                    config: { ...prev.config, initial_capital: parseFloat(e.target.value) }
                  }))}
                />
              </Grid>
              <Grid item xs={6} component="div">
                <TextField
                  fullWidth
                  type="number"
                  label="Max Position Size (%)"
                  value={newBot.config.max_position_size * 100}
                  onChange={(e) => setNewBot(prev => ({
                    ...prev,
                    config: { ...prev.config, max_position_size: parseFloat(e.target.value) / 100 }
                  }))}
                />
              </Grid>
              <Grid item xs={6} component="div">
                <TextField
                  fullWidth
                  type="number"
                  label="Stop Loss (%)"
                  value={newBot.config.stop_loss_pct * 100}
                  onChange={(e) => setNewBot(prev => ({
                    ...prev,
                    config: { ...prev.config, stop_loss_pct: parseFloat(e.target.value) / 100 }
                  }))}
                />
              </Grid>
              <Grid item xs={6} component="div">
                <TextField
                  fullWidth
                  type="number"
                  label="Take Profit (%)"
                  value={newBot.config.take_profit_pct * 100}
                  onChange={(e) => setNewBot(prev => ({
                    ...prev,
                    config: { ...prev.config, take_profit_pct: parseFloat(e.target.value) / 100 }
                  }))}
                />
              </Grid>
            </Grid>

            <FormControlLabel
              control={
                <Checkbox
                  checked={newBot.config.paper_trading}
                  onChange={(e) => setNewBot(prev => ({
                    ...prev,
                    config: { ...prev.config, paper_trading: e.target.checked }
                  }))}
                />
              }
              label="Paper Trading (Simulation Mode)"
              sx={{ mt: 2 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateBot}
            variant="contained"
            disabled={!newBot.name || newBot.config.symbols.length === 0 || newBot.config.strategies.length === 0}
          >
            Create Bot
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
