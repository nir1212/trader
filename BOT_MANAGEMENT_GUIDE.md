# Bot Management System - Complete Guide

## 🎉 What's New

Your trading bot system now supports **multiple bots** with full management capabilities!

## 🏗️ Architecture

### **Database Schema**

**New Tables:**
- `bots` - Bot instances with configuration
- `signals` now linked to specific bots via `bot_id`

**Bot Table Structure:**
```sql
bots:
  - id (primary key)
  - name (unique)
  - description
  - portfolio_id (foreign key)
  - status (stopped, running, paused, error)
  - config (JSON: symbols, strategies, risk params)
  - created_at, updated_at, last_run_at
  - is_active
```

### **Components**

1. **BotManager** (`src/trader/core/bot_manager.py`)
   - Manages bot lifecycle (create, start, stop, delete)
   - Runs bots in separate threads
   - Tracks running bot instances

2. **Bot API** (`src/trader/api/routers/bots.py`)
   - RESTful endpoints for bot management
   - Full CRUD operations
   - Bot control (start/stop/restart)

3. **Database Models** (Updated)
   - Bot model with relationships
   - Signal model linked to bots

## 📡 API Endpoints

### **Bot CRUD Operations**

#### Create Bot
```http
POST /api/bots/
Content-Type: application/json

{
  "name": "My Trading Bot",
  "description": "AAPL momentum strategy",
  "portfolio_id": 1,
  "config": {
    "symbols": ["AAPL", "MSFT", "GOOGL"],
    "strategies": ["moving_average", "rsi"],
    "initial_capital": 10000,
    "paper_trading": true,
    "timeframe": "1d",
    "run_interval_seconds": 60,
    "max_position_size": 0.1,
    "stop_loss_pct": 0.05,
    "take_profit_pct": 0.10,
    "max_portfolio_risk": 0.02
  }
}
```

#### List All Bots
```http
GET /api/bots/?active_only=true
```

#### Get Bot Details
```http
GET /api/bots/{bot_id}
```

#### Update Bot
```http
PUT /api/bots/{bot_id}
Content-Type: application/json

{
  "name": "Updated Bot Name",
  "description": "New description",
  "config": {
    "symbols": ["AAPL", "TSLA"],
    "strategies": ["macd"]
  }
}
```

#### Delete Bot
```http
DELETE /api/bots/{bot_id}
```

### **Bot Control**

#### Start Bot
```http
POST /api/bots/{bot_id}/start
Content-Type: application/json

{
  "api_key": "your_alpaca_key",
  "api_secret": "your_alpaca_secret"
}
```

#### Stop Bot
```http
POST /api/bots/{bot_id}/stop
```

#### Restart Bot
```http
POST /api/bots/{bot_id}/restart
```

### **Bot Data**

#### Get Bot Signals
```http
GET /api/bots/{bot_id}/signals?limit=50
```

#### Get Available Strategies
```http
GET /api/bots/strategies/available
```

## 🎯 Bot Configuration

### **Required Fields**

```json
{
  "symbols": ["AAPL", "MSFT"],      // Trading symbols
  "strategies": ["moving_average"]   // Strategy names
}
```

### **Optional Fields**

```json
{
  "initial_capital": 10000,          // Starting capital
  "paper_trading": true,             // Paper vs live trading
  "timeframe": "1d",                 // Data timeframe
  "run_interval_seconds": 60,        // How often to run
  "max_position_size": 0.1,          // Max 10% per position
  "stop_loss_pct": 0.05,             // 5% stop loss
  "take_profit_pct": 0.10,           // 10% take profit
  "max_portfolio_risk": 0.02         // Max 2% portfolio risk
}
```

### **Available Strategies**

- `moving_average` - Moving Average Crossover
- `rsi` - Relative Strength Index
- `macd` - MACD Strategy
- `bollinger_bands` - Bollinger Bands

## 💻 Usage Examples

### **Python Client**

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Create a bot
bot_config = {
    "name": "AAPL Trader",
    "description": "Trades AAPL using MA and RSI",
    "portfolio_id": 1,
    "config": {
        "symbols": ["AAPL"],
        "strategies": ["moving_average", "rsi"],
        "paper_trading": True,
        "max_position_size": 0.15
    }
}

response = requests.post(f"{BASE_URL}/bots/", json=bot_config)
bot = response.json()
bot_id = bot['id']

# Start the bot
requests.post(f"{BASE_URL}/bots/{bot_id}/start")

# Check status
status = requests.get(f"{BASE_URL}/bots/{bot_id}").json()
print(f"Bot status: {status['status']}")
print(f"Is running: {status['is_running']}")

# Get signals
signals = requests.get(f"{BASE_URL}/bots/{bot_id}/signals").json()
print(f"Generated {len(signals)} signals")

# Stop the bot
requests.post(f"{BASE_URL}/bots/{bot_id}/stop")
```

### **JavaScript/TypeScript**

```typescript
const BASE_URL = 'http://localhost:8000/api';

// Create bot
const createBot = async () => {
  const response = await fetch(`${BASE_URL}/bots/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: 'My Bot',
      portfolio_id: 1,
      config: {
        symbols: ['AAPL', 'MSFT'],
        strategies: ['moving_average'],
        paper_trading: true
      }
    })
  });
  return response.json();
};

// Start bot
const startBot = async (botId: number) => {
  const response = await fetch(`${BASE_URL}/bots/${botId}/start`, {
    method: 'POST'
  });
  return response.json();
};

// Get bot status
const getBotStatus = async (botId: number) => {
  const response = await fetch(`${BASE_URL}/bots/${botId}`);
  return response.json();
};
```

## 🔄 Bot Lifecycle

```
1. CREATE → Bot created in database (status: stopped)
2. START → Bot thread starts, connects to broker (status: running)
3. RUNNING → Bot executes strategies at intervals
4. STOP → Bot thread stops gracefully (status: stopped)
5. DELETE → Bot soft-deleted (status: deleted, is_active: false)
```

## 📊 Bot Status Values

- **stopped** - Bot is not running
- **running** - Bot is actively trading
- **paused** - Bot is temporarily paused
- **error** - Bot encountered an error
- **deleted** - Bot has been deleted

## 🎨 Frontend Integration

### **Bot List Component**

```typescript
interface Bot {
  id: number;
  name: string;
  status: string;
  is_running: boolean;
  config: BotConfig;
}

const BotList = () => {
  const [bots, setBots] = useState<Bot[]>([]);
  
  useEffect(() => {
    fetch('/api/bots/')
      .then(res => res.json())
      .then(setBots);
  }, []);
  
  return (
    <div>
      {bots.map(bot => (
        <BotCard key={bot.id} bot={bot} />
      ))}
    </div>
  );
};
```

### **Bot Control Component**

```typescript
const BotControls = ({ botId }: { botId: number }) => {
  const [status, setStatus] = useState<Bot | null>(null);
  
  const startBot = async () => {
    await fetch(`/api/bots/${botId}/start`, { method: 'POST' });
    refreshStatus();
  };
  
  const stopBot = async () => {
    await fetch(`/api/bots/${botId}/stop`, { method: 'POST' });
    refreshStatus();
  };
  
  return (
    <div>
      <button onClick={startBot} disabled={status?.is_running}>
        Start
      </button>
      <button onClick={stopBot} disabled={!status?.is_running}>
        Stop
      </button>
    </div>
  );
};
```

## 🔐 Security Considerations

### **Production Checklist**

- [ ] Add authentication/authorization
- [ ] Validate API keys securely
- [ ] Rate limit bot creation
- [ ] Limit concurrent bots per user
- [ ] Add bot resource limits
- [ ] Implement proper error handling
- [ ] Add logging and monitoring
- [ ] Secure WebSocket connections

## 🐛 Troubleshooting

### **Bot Won't Start**

1. Check portfolio exists: `GET /api/portfolio/{portfolio_id}`
2. Verify config is valid
3. Check API keys are correct
4. Look for errors in bot status

### **Bot Stops Unexpectedly**

1. Check bot status: `GET /api/bots/{bot_id}`
2. Look for status='error'
3. Check backend logs
4. Verify broker connection

### **Signals Not Saving**

1. Ensure bot_id is passed to signal recording
2. Check database connectivity
3. Verify bot is actually running

## 📈 Performance Tips

### **Optimize Bot Performance**

1. **Adjust run interval**: Longer intervals = less CPU
2. **Limit symbols**: Fewer symbols = faster execution
3. **Choose strategies wisely**: Some strategies are more CPU intensive
4. **Monitor resource usage**: Check thread count and memory

### **Scaling Multiple Bots**

- Each bot runs in its own thread
- Consider resource limits (CPU, memory, API rate limits)
- Use different portfolios for different bots
- Stagger bot start times to avoid API rate limits

## 🎯 Next Steps

### **For Backend**

1. ✅ Database schema updated
2. ✅ BotManager class created
3. ✅ API endpoints implemented
4. ⏳ Add WebSocket for real-time updates
5. ⏳ Add bot performance metrics
6. ⏳ Add bot scheduling (cron-like)

### **For Frontend**

1. ⏳ Create bot list page
2. ⏳ Create bot creation form
3. ⏳ Add bot control buttons
4. ⏳ Show bot status indicators
5. ⏳ Display bot signals
6. ⏳ Add bot configuration editor

## 🎉 Summary

You now have a **complete multi-bot management system** with:

- ✅ Database support for multiple bots
- ✅ Bot lifecycle management (create, start, stop, delete)
- ✅ Full REST API for bot operations
- ✅ Bot configuration with strategies and risk parameters
- ✅ Signal tracking per bot
- ✅ Thread-based bot execution
- ✅ Comprehensive documentation

**Start the API server and test it:**

```bash
poetry run python api_server.py
```

Then open http://localhost:8000/docs to explore the new bot management endpoints!
