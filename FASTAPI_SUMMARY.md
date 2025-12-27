# FastAPI Backend - Complete Implementation

## 🎉 What You Now Have

Your trading bot now has a **complete REST API backend** that you can use to build a frontend!

## 🚀 Starting the API Server

```bash
poetry run python api_server.py
```

The server will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs ← **Try this first!**
- **ReDoc**: http://localhost:8000/redoc

## 📁 Project Structure

```
src/trader/api/
├── main.py              # FastAPI app setup
├── models.py            # Pydantic models (request/response)
└── routers/
    ├── health.py        # Health check endpoint
    ├── portfolio.py     # Portfolio management
    ├── bot.py           # Bot control (start/stop)
    ├── trades.py        # Trade history & signals
    └── strategies.py    # Available strategies

api_server.py            # Server startup script
test_api.py             # API test script
API_GUIDE.md            # Complete API documentation
```

## 🎯 Key Features

### 1. **Portfolio Management**
- Create/list portfolios
- Get portfolio summary (cash, positions, P&L)
- View historical snapshots
- Get performance metrics

### 2. **Bot Control**
- Start/stop bot
- Configure strategies and symbols
- Get bot status
- Run bot once (test mode)

### 3. **Data Access**
- Trade history with filters
- Trading signals from strategies
- Portfolio snapshots over time
- Performance analytics

### 4. **Strategy Info**
- List available strategies
- Get strategy parameters
- See descriptions

## 📊 API Endpoints Summary

### Health & Info
- `GET /api/health` - Health check
- `GET /` - API info

### Portfolio
- `POST /api/portfolio/` - Create portfolio
- `GET /api/portfolio/` - List portfolios
- `GET /api/portfolio/{id}` - Get portfolio
- `GET /api/portfolio/{id}/summary` - Portfolio summary
- `GET /api/portfolio/{id}/snapshots` - Historical data
- `GET /api/portfolio/{id}/performance` - Performance metrics

### Bot Control
- `POST /api/bot/start` - Start bot
- `POST /api/bot/stop` - Stop bot
- `GET /api/bot/status` - Get status
- `POST /api/bot/run-once` - Run one iteration

### Trades & Signals
- `GET /api/trades/` - Trade history
- `GET /api/trades/signals` - Trading signals
- `GET /api/trades/{id}` - Specific trade

### Strategies
- `GET /api/strategies/` - List strategies

## 🧪 Testing the API

### Option 1: Interactive Docs (Recommended)
1. Start server: `poetry run python api_server.py`
2. Open: http://localhost:8000/docs
3. Try endpoints directly in browser!

### Option 2: Test Script
```bash
poetry run python test_api.py
```

### Option 3: cURL
```bash
# Health check
curl http://localhost:8000/api/health

# List strategies
curl http://localhost:8000/api/strategies/

# Get bot status
curl http://localhost:8000/api/bot/status
```

## 💻 Frontend Integration Examples

### React/TypeScript

```typescript
// api.ts
const API_BASE = 'http://localhost:8000';

export const api = {
  // Start bot
  startBot: async (config: BotConfig) => {
    const response = await fetch(`${API_BASE}/api/bot/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });
    return response.json();
  },

  // Get portfolio summary
  getPortfolio: async (id: number) => {
    const response = await fetch(`${API_BASE}/api/portfolio/${id}/summary`);
    return response.json();
  },

  // Get bot status
  getBotStatus: async () => {
    const response = await fetch(`${API_BASE}/api/bot/status`);
    return response.json();
  },

  // Get trades
  getTrades: async (portfolioId?: number, limit = 50) => {
    const params = new URLSearchParams();
    if (portfolioId) params.append('portfolio_id', portfolioId.toString());
    params.append('limit', limit.toString());
    
    const response = await fetch(`${API_BASE}/api/trades/?${params}`);
    return response.json();
  }
};
```

### Vue/Nuxt

```javascript
// composables/useApi.js
export const useApi = () => {
  const baseUrl = 'http://localhost:8000';

  const startBot = async (config) => {
    const response = await $fetch(`${baseUrl}/api/bot/start`, {
      method: 'POST',
      body: config
    });
    return response;
  };

  const getPortfolio = async (id) => {
    return await $fetch(`${baseUrl}/api/portfolio/${id}/summary`);
  };

  const getBotStatus = async () => {
    return await $fetch(`${baseUrl}/api/bot/status`);
  };

  return { startBot, getPortfolio, getBotStatus };
};
```

## 🎨 Recommended Frontend Pages

### 1. Dashboard
- Portfolio value chart
- Current positions table
- P&L summary
- Bot status indicator

### 2. Trading Control
- Start/stop bot button
- Symbol selection
- Strategy selection
- Risk settings sliders

### 3. History
- Trade history table
- Signals timeline
- Performance charts

### 4. Analytics
- Win rate gauge
- Strategy comparison
- Equity curve
- Drawdown chart

## 🛠️ Frontend Tech Stack Recommendations

### Modern Stack
- **Framework**: React + TypeScript + Vite
- **Styling**: TailwindCSS
- **Charts**: Recharts or Chart.js
- **State**: Zustand or React Query
- **UI Components**: shadcn/ui or MUI

### Alternative Stack
- **Framework**: Vue 3 + TypeScript + Nuxt
- **Styling**: TailwindCSS
- **Charts**: Vue-ChartJS
- **State**: Pinia
- **UI Components**: Vuetify or PrimeVue

## 📦 Example Bot Configuration

```json
{
  "symbols": ["AAPL", "MSFT", "GOOGL", "TSLA"],
  "strategies": ["moving_average", "rsi", "macd"],
  "paper_trading": true,
  "max_position_size": 0.1,
  "stop_loss_pct": 0.05,
  "take_profit_pct": 0.10
}
```

## 🔄 Typical API Flow

```
1. User opens frontend
   ↓
2. Frontend calls GET /api/portfolio/ (list portfolios)
   ↓
3. Frontend calls GET /api/bot/status (check if running)
   ↓
4. User clicks "Start Bot"
   ↓
5. Frontend calls POST /api/bot/start (with config)
   ↓
6. Bot starts trading
   ↓
7. Frontend polls GET /api/portfolio/{id}/summary (every 30s)
   ↓
8. Frontend displays updated portfolio data
   ↓
9. User clicks "Stop Bot"
   ↓
10. Frontend calls POST /api/bot/stop
```

## 🔐 Security Notes

**Current State**: No authentication (development only)

**For Production**:
1. Add JWT authentication
2. Use HTTPS
3. Add rate limiting
4. Validate all inputs
5. Use environment variables for secrets
6. Update CORS to specific domains

## 🐛 Debugging

### Check if server is running
```bash
curl http://localhost:8000/api/health
```

### View server logs
The server prints logs to console. Look for:
- Request logs
- Error messages
- Bot activity

### Common Issues

**Port already in use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

**Import errors:**
```bash
# Reinstall dependencies
poetry install
```

## 📚 Full Documentation

- **API_GUIDE.md** - Complete API reference with examples
- **Interactive Docs** - http://localhost:8000/docs
- **ReDoc** - http://localhost:8000/redoc

## 🎯 Next Steps

### 1. Test the API
```bash
# Start server
poetry run python api_server.py

# In another terminal, test it
poetry run python test_api.py

# Or open browser
open http://localhost:8000/docs
```

### 2. Build Frontend
- Choose your framework (React/Vue/etc)
- Set up project
- Install axios or fetch
- Create API service layer
- Build UI components

### 3. Connect Frontend to API
- Use the endpoints from API_GUIDE.md
- Handle loading states
- Show error messages
- Update UI on data changes

## 🌟 Features You Can Build

### Essential
- ✅ Start/stop bot
- ✅ View portfolio
- ✅ See trades
- ✅ Monitor performance

### Advanced
- 📊 Real-time charts
- 🔔 Notifications
- 📈 Strategy backtesting UI
- 🎯 Custom strategy builder
- 📱 Mobile responsive
- 🌙 Dark mode

## 🎉 You're Ready!

Your trading bot now has:
- ✅ Database persistence
- ✅ REST API backend
- ✅ Complete documentation
- ✅ Ready for frontend development

**Start building your frontend and create an amazing trading dashboard!** 🚀
