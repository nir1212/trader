from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
import threading
import time
from datetime import datetime

from trader.api.models import BotConfig, BotStatusResponse, BotStatus
from trader.database.db_manager import DatabaseManager
from trader.core.portfolio_with_db import PortfolioWithDB
from trader.risk.risk_manager import RiskManager
from trader.bots.stock_bot import StockBot
from trader.strategies.moving_average import MovingAverageCrossover
from trader.strategies.rsi_strategy import RSIStrategy
from trader.strategies.macd_strategy import MACDStrategy
from trader.strategies.bollinger_bands import BollingerBandsStrategy

router = APIRouter()

# Global bot instance and state
bot_instance = None
bot_thread = None
bot_running = False
bot_start_time = None
bot_config = None


def get_strategy_by_name(name: str, params: dict = None):
    """Get strategy instance by name"""
    strategy_map = {
        'moving_average': MovingAverageCrossover,
        'rsi': RSIStrategy,
        'macd': MACDStrategy,
        'bollinger_bands': BollingerBandsStrategy
    }
    
    strategy_class = strategy_map.get(name)
    if strategy_class:
        return strategy_class(params or {})
    return None


def run_bot_loop():
    """Background task to run the bot"""
    global bot_running, bot_instance
    
    while bot_running and bot_instance:
        try:
            bot_instance.run_trading_loop()
            time.sleep(300)  # Run every 5 minutes
        except Exception as e:
            print(f"Error in bot loop: {e}")
            time.sleep(60)


@router.post("/start")
def start_bot(config: BotConfig, background_tasks: BackgroundTasks):
    """Start the trading bot"""
    global bot_instance, bot_thread, bot_running, bot_start_time, bot_config
    
    if bot_running:
        raise HTTPException(status_code=400, detail="Bot is already running")
    
    try:
        # Initialize database
        db_manager = DatabaseManager()
        
        # Get or create portfolio
        portfolio = db_manager.get_active_portfolio("api_portfolio")
        if not portfolio:
            portfolio = db_manager.create_portfolio("api_portfolio", 10000)
        
        portfolio_obj = PortfolioWithDB(
            initial_capital=portfolio.initial_capital,
            name=portfolio.name,
            db_manager=db_manager
        )
        
        # Create strategies
        strategies = []
        for strategy_name in config.strategies:
            strategy = get_strategy_by_name(strategy_name)
            if strategy:
                strategies.append(strategy)
        
        if not strategies:
            raise HTTPException(status_code=400, detail="No valid strategies provided")
        
        # Create risk manager
        risk_manager = RiskManager(
            max_position_size=config.max_position_size,
            stop_loss_pct=config.stop_loss_pct,
            take_profit_pct=config.take_profit_pct
        )
        
        # Create bot
        bot_instance = StockBot(
            portfolio=portfolio_obj,
            strategies=strategies,
            symbols=config.symbols,
            risk_manager=risk_manager,
            paper_trading=config.paper_trading
        )
        
        # Start bot
        bot_instance.start()
        bot_running = True
        bot_start_time = datetime.now()
        bot_config = config
        
        # Start background thread
        bot_thread = threading.Thread(target=run_bot_loop, daemon=True)
        bot_thread.start()
        
        return {
            "message": "Bot started successfully",
            "portfolio_id": portfolio.id,
            "symbols": config.symbols,
            "strategies": config.strategies
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start bot: {str(e)}")


@router.post("/stop")
def stop_bot():
    """Stop the trading bot"""
    global bot_instance, bot_running, bot_start_time
    
    if not bot_running:
        raise HTTPException(status_code=400, detail="Bot is not running")
    
    try:
        bot_running = False
        if bot_instance:
            bot_instance.stop()
        
        uptime = (datetime.now() - bot_start_time).total_seconds() if bot_start_time else 0
        
        return {
            "message": "Bot stopped successfully",
            "uptime_seconds": uptime
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop bot: {str(e)}")


@router.get("/status", response_model=BotStatusResponse)
def get_bot_status():
    """Get current bot status"""
    global bot_instance, bot_running, bot_start_time, bot_config
    
    uptime = None
    if bot_running and bot_start_time:
        uptime = (datetime.now() - bot_start_time).total_seconds()
    
    status = BotStatus.RUNNING if bot_running else BotStatus.STOPPED
    
    portfolio_id = None
    symbols = []
    strategies = []
    
    if bot_config:
        symbols = bot_config.symbols
        strategies = bot_config.strategies
    
    if bot_instance and hasattr(bot_instance, 'portfolio'):
        portfolio_id = getattr(bot_instance.portfolio, 'portfolio_id', None)
    
    return BotStatusResponse(
        status=status,
        is_running=bot_running,
        portfolio_id=portfolio_id,
        symbols=symbols,
        strategies=strategies,
        uptime_seconds=uptime
    )


@router.post("/run-once")
def run_bot_once(config: BotConfig):
    """Run bot for one iteration (useful for testing)"""
    try:
        # Initialize database
        db_manager = DatabaseManager()
        
        # Get or create portfolio
        portfolio = db_manager.get_active_portfolio("api_portfolio")
        if not portfolio:
            portfolio = db_manager.create_portfolio("api_portfolio", 10000)
        
        portfolio_obj = PortfolioWithDB(
            initial_capital=portfolio.initial_capital,
            name=portfolio.name,
            db_manager=db_manager
        )
        
        # Create strategies
        strategies = []
        for strategy_name in config.strategies:
            strategy = get_strategy_by_name(strategy_name)
            if strategy:
                strategies.append(strategy)
        
        # Create risk manager
        risk_manager = RiskManager(
            max_position_size=config.max_position_size,
            stop_loss_pct=config.stop_loss_pct,
            take_profit_pct=config.take_profit_pct
        )
        
        # Create and run bot
        bot = StockBot(
            portfolio=portfolio_obj,
            strategies=strategies,
            symbols=config.symbols,
            risk_manager=risk_manager,
            paper_trading=config.paper_trading
        )
        
        bot.start()
        bot.run_trading_loop()
        bot.stop()
        
        summary = portfolio_obj.get_summary()
        
        return {
            "message": "Bot ran successfully",
            "portfolio_summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run bot: {str(e)}")
