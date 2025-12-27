# Trading Bot Frontend - Setup Guide

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

This will install all required packages:
- React & React DOM
- React Router for navigation
- Axios for API calls
- Recharts for charts
- Lucide React for icons
- TailwindCSS for styling

### 2. Start Development Server

```bash
npm run dev
```

The frontend will start at **http://localhost:3000**

### 3. Make Sure Backend is Running

In another terminal, start the FastAPI backend:

```bash
cd ..
poetry run python api_server.py
```

The backend should be running at **http://localhost:8000**

## 📁 Project Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── Dashboard.tsx      # Portfolio overview
│   │   ├── BotControl.tsx     # Start/stop bot
│   │   └── History.tsx        # Trades & signals
│   ├── services/
│   │   └── api.ts             # API service layer
│   ├── types/
│   │   └── index.ts           # TypeScript types
│   ├── App.tsx                # Main app with routing
│   ├── main.tsx               # Entry point
│   └── index.css              # Tailwind styles
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## 🎨 Features

### Dashboard Page (`/`)
- Portfolio value and P&L
- Cash available
- Open positions
- Portfolio value chart
- Positions table

### Bot Control Page (`/bot`)
- Start/stop bot
- Configure symbols
- Select strategies
- Adjust risk settings
- Real-time bot status

### History Page (`/history`)
- Trade history table
- Trading signals
- Filter and search

## 🔧 Configuration

### API Proxy

The frontend is configured to proxy API requests to the backend:

```typescript
// vite.config.ts
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

This means requests to `/api/*` are forwarded to `http://localhost:8000/api/*`

### Environment Variables

Create `.env` file if needed:

```env
VITE_API_URL=http://localhost:8000
```

## 📦 Available Scripts

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 🎯 How It Works

### 1. API Service Layer

All API calls go through `src/services/api.ts`:

```typescript
import { getPortfolioSummary, startBot, getTrades } from './services/api';

// Get portfolio data
const summary = await getPortfolioSummary(1);

// Start the bot
await startBot(config);

// Get trades
const trades = await getTrades();
```

### 2. TypeScript Types

All data types are defined in `src/types/index.ts`:

```typescript
interface PortfolioSummary {
  total_value: number;
  cash: number;
  positions: Record<string, Position>;
  // ...
}
```

### 3. React Router

Navigation is handled by React Router:

```typescript
<Routes>
  <Route path="/" element={<Dashboard />} />
  <Route path="/bot" element={<BotControl />} />
  <Route path="/history" element={<History />} />
</Routes>
```

## 🐛 Troubleshooting

### Module not found errors

Run `npm install` to install all dependencies.

### API connection errors

1. Make sure backend is running at http://localhost:8000
2. Check the proxy configuration in `vite.config.ts`
3. Verify CORS is enabled in the backend

### Tailwind not working

1. Make sure `tailwind.config.js` and `postcss.config.js` exist
2. Check that `@tailwind` directives are in `index.css`
3. Restart the dev server

### Port already in use

Change the port in `vite.config.ts`:

```typescript
server: {
  port: 3001, // Change to different port
}
```

## 🎨 Customization

### Change Theme Colors

Edit `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: '#your-color',
    }
  }
}
```

### Add New Pages

1. Create component in `src/pages/`
2. Add route in `App.tsx`
3. Add navigation item in Navigation component

## 📚 Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router** - Routing
- **TailwindCSS** - Styling
- **Axios** - HTTP client
- **Recharts** - Charts
- **Lucide React** - Icons

## 🚀 Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

The build output will be in the `dist/` folder.

## 📝 Next Steps

1. **Install dependencies**: `npm install`
2. **Start dev server**: `npm run dev`
3. **Start backend**: `poetry run python api_server.py`
4. **Open browser**: http://localhost:3000
5. **Start trading!**

Your trading bot dashboard is ready! 🎉
