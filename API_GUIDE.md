# Trading Bot API Guide

## 🚀 Quick Start

### Start the API Server

```bash
poetry run python api_server.py
```

The server will start at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Health Check

**GET** `/api/health`

Check if the API is running.

```bash
curl http://localhost:8000/api/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-27T11:42:00",
  "service": "Trading Bot API"
}
```

---

## 💼 Portfolio Management

### Create Portfolio

**POST** `/api/portfolio/`

```bash
curl -X POST http://localhost:8000/api/portfolio/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_portfolio",
    "initial_capital": 10000
  }'
```

### List All Portfolios

**GET** `/api/portfolio/`

```bash
curl http://localhost:8000/api/portfolio/
```

### Get Portfolio Details

**GET** `/api/portfolio/{portfolio_id}`

```bash
curl http://localhost:8000/api/portfolio/1
```

### Get Portfolio Summary

**GET** `/api/portfolio/{portfolio_id}/summary`

Returns current positions, cash, P&L, etc.

```bash
curl http://localhost:8000/api/portfolio/1/summary
```

Response:
```json
{
  "initial_capital": 10000,
  "cash": 8500,
  "positions_value": 2000,
  "total_value": 10500,
  "total_pnl": 500,
  "total_pnl_pct": 5.0,
  "num_positions": 2,
  "positions": {
    "AAPL": {
      "quantity": 10,
      "entry_price": 150.0,
      "current_price": 155.0,
      "value": 1550,
      "pnl": 50,
      "pnl_pct": 3.33
    }
  }
}
```

### Get Portfolio Snapshots

**GET** `/api/portfolio/{portfolio_id}/snapshots?limit=50`

Historical portfolio values over time.

```bash
curl http://localhost:8000/api/portfolio/1/snapshots?limit=20
```

### Get Portfolio Performance

**GET** `/api/portfolio/{portfolio_id}/performance`

```bash
curl http://localhost:8000/api/portfolio/1/performance
```

Response:
```json
{
  "total_return": 500,
  "total_return_pct": 5.0,
  "win_rate": 66.67,
  "total_trades": 10,
  "winning_trades": 6,
  "losing_trades": 4
}
```

---

## 🤖 Bot Control

### Start Bot

**POST** `/api/bot/start`

```bash
curl -X POST http://localhost:8000/api/bot/start \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "MSFT", "GOOGL"],
    "strategies": ["moving_average", "rsi"],
    "paper_trading": true,
    "max_position_size": 0.1,
    "stop_loss_pct": 0.05,
    "take_profit_pct": 0.10
  }'
```

Response:
```json
{
  "message": "Bot started successfully",
  "portfolio_id": 1,
  "symbols": ["AAPL", "MSFT", "GOOGL"],
  "strategies": ["moving_average", "rsi"]
}
```

### Stop Bot

**POST** `/api/bot/stop`

```bash
curl -X POST http://localhost:8000/api/bot/stop
```

### Get Bot Status

**GET** `/api/bot/status`

```bash
curl http://localhost:8000/api/bot/status
```

Response:
```json
{
  "status": "running",
  "is_running": true,
  "portfolio_id": 1,
  "symbols": ["AAPL", "MSFT", "GOOGL"],
  "strategies": ["moving_average", "rsi"],
  "uptime_seconds": 3600
}
```

### Run Bot Once (Test Mode)

**POST** `/api/bot/run-once`

Runs the bot for one iteration without starting continuous mode.

```bash
curl -X POST http://localhost:8000/api/bot/run-once \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL"],
    "strategies": ["moving_average"],
    "paper_trading": true,
    "max_position_size": 0.1,
    "stop_loss_pct": 0.05,
    "take_profit_pct": 0.10
  }'
```

---

## 📊 Trades & Signals

### Get Trade History

**GET** `/api/trades/?portfolio_id=1&limit=50`

```bash
curl "http://localhost:8000/api/trades/?portfolio_id=1&limit=20"
```

Filter by symbol:
```bash
curl "http://localhost:8000/api/trades/?symbol=AAPL&limit=10"
```

### Get Trading Signals

**GET** `/api/trades/signals?limit=50`

```bash
curl "http://localhost:8000/api/trades/signals?limit=20"
```

Filter by signal type:
```bash
curl "http://localhost:8000/api/trades/signals?signal_type=BUY&limit=10"
```

Filter by strategy:
```bash
curl "http://localhost:8000/api/trades/signals?strategy_name=moving_average"
```

### Get Specific Trade

**GET** `/api/trades/{trade_id}`

```bash
curl http://localhost:8000/api/trades/123
```

---

## 📈 Strategies

### List Available Strategies

**GET** `/api/strategies/`

```bash
curl http://localhost:8000/api/strategies/
```

Response:
```json
[
  {
    "name": "moving_average",
    "description": "Moving Average Crossover - Buy when fast MA crosses above slow MA",
    "parameters": {
      "fast_period": {"type": "int", "default": 10},
      "slow_period": {"type": "int", "default": 30},
      "ma_type": {"type": "string", "default": "sma", "options": ["sma", "ema"]}
    }
  },
  {
    "name": "rsi",
    "description": "RSI Strategy - Buy when oversold, sell when overbought",
    "parameters": {
      "period": {"type": "int", "default": 14},
      "oversold": {"type": "int", "default": 30},
      "overbought": {"type": "int", "default": 70}
    }
  }
]
```

---

## 🔧 Configuration Options

### Bot Config

```json
{
  "symbols": ["AAPL", "MSFT", "GOOGL"],
  "strategies": ["moving_average", "rsi", "macd", "bollinger_bands"],
  "paper_trading": true,
  "max_position_size": 0.1,
  "stop_loss_pct": 0.05,
  "take_profit_pct": 0.10
}
```

**Available Strategies:**
- `moving_average` - MA Crossover
- `rsi` - RSI Strategy
- `macd` - MACD Strategy
- `bollinger_bands` - Bollinger Bands

---

## 💡 Example Workflows

### 1. Start Trading

```bash
# 1. Create portfolio
curl -X POST http://localhost:8000/api/portfolio/ \
  -H "Content-Type: application/json" \
  -d '{"name": "my_portfolio", "initial_capital": 10000}'

# 2. Start bot
curl -X POST http://localhost:8000/api/bot/start \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "MSFT"],
    "strategies": ["moving_average", "rsi"],
    "paper_trading": true,
    "max_position_size": 0.1,
    "stop_loss_pct": 0.05,
    "take_profit_pct": 0.10
  }'

# 3. Check status
curl http://localhost:8000/api/bot/status
```

### 2. Monitor Performance

```bash
# Get portfolio summary
curl http://localhost:8000/api/portfolio/1/summary

# Get recent trades
curl "http://localhost:8000/api/trades/?portfolio_id=1&limit=10"

# Get performance metrics
curl http://localhost:8000/api/portfolio/1/performance
```

### 3. Stop Trading

```bash
# Stop the bot
curl -X POST http://localhost:8000/api/bot/stop

# Check final portfolio
curl http://localhost:8000/api/portfolio/1/summary
```

---

## 🌐 CORS Configuration

The API is configured to allow all origins for development. For production:

Edit `src/trader/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🔐 Authentication (Future)

Currently, the API has no authentication. For production, add:

1. **API Keys**
2. **JWT Tokens**
3. **OAuth2**

---

## 📱 Frontend Integration

### React Example

```javascript
// Start bot
const startBot = async () => {
  const response = await fetch('http://localhost:8000/api/bot/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      symbols: ['AAPL', 'MSFT'],
      strategies: ['moving_average', 'rsi'],
      paper_trading: true,
      max_position_size: 0.1,
      stop_loss_pct: 0.05,
      take_profit_pct: 0.10
    })
  });
  const data = await response.json();
  console.log(data);
};

// Get portfolio
const getPortfolio = async (portfolioId) => {
  const response = await fetch(`http://localhost:8000/api/portfolio/${portfolioId}/summary`);
  const data = await response.json();
  return data;
};

// Get bot status
const getBotStatus = async () => {
  const response = await fetch('http://localhost:8000/api/bot/status');
  const data = await response.json();
  return data;
};
```

### Vue Example

```javascript
// In your Vue component
export default {
  data() {
    return {
      botStatus: null,
      portfolio: null
    }
  },
  methods: {
    async startBot() {
      const response = await fetch('http://localhost:8000/api/bot/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbols: ['AAPL', 'MSFT'],
          strategies: ['moving_average'],
          paper_trading: true,
          max_position_size: 0.1,
          stop_loss_pct: 0.05,
          take_profit_pct: 0.10
        })
      });
      const data = await response.json();
      this.botStatus = data;
    },
    async getPortfolio(id) {
      const response = await fetch(`http://localhost:8000/api/portfolio/${id}/summary`);
      this.portfolio = await response.json();
    }
  }
}
```

---

## 🧪 Testing with Swagger UI

1. Start the server: `poetry run python api_server.py`
2. Open browser: http://localhost:8000/docs
3. Try out endpoints interactively
4. See request/response examples

---

## 📊 Response Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

---

## 🎯 Next Steps for Frontend

### Recommended Pages

1. **Dashboard**
   - Portfolio summary
   - Current positions
   - P&L chart
   - Bot status

2. **Trading**
   - Start/stop bot
   - Configure strategies
   - Select symbols
   - Risk settings

3. **History**
   - Trade history table
   - Signals timeline
   - Performance charts

4. **Analytics**
   - Win rate
   - Strategy performance
   - Portfolio growth chart
   - Drawdown analysis

### Recommended Tech Stack

- **React** + TypeScript + Vite
- **TailwindCSS** for styling
- **Recharts** or **Chart.js** for charts
- **React Query** for data fetching
- **Zustand** or **Redux** for state management

---

## 🚀 Production Deployment

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

COPY . .

CMD ["poetry", "run", "python", "api_server.py"]
```

### Environment Variables

```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost/trading_bot
ALPACA_API_KEY=your_key
ALPACA_SECRET_KEY=your_secret
BINANCE_API_KEY=your_key
BINANCE_SECRET_KEY=your_secret
```

---

Your API is ready for frontend development! 🎉
