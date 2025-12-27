from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from trader.api.routers import portfolio, bot, trades, strategies, health, bots

app = FastAPI(
    title="Trading Bot API",
    description="REST API for managing your trading bot",
    version="2.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(bot.router, prefix="/api/bot", tags=["Bot Control (Legacy)"])
app.include_router(bots.router, prefix="/api", tags=["Bot Management"])
app.include_router(trades.router, prefix="/api/trades", tags=["Trades"])
app.include_router(strategies.router, prefix="/api/strategies", tags=["Strategies"])

@app.get("/")
def root():
    return {
        "message": "Trading Bot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }
