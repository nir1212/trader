"""
Bot Management API Routes
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from trader.core.bot_manager import BotManager
from trader.database.db_manager import DatabaseManager

router = APIRouter(prefix="/bots", tags=["bots"])

# Initialize managers
db_manager = DatabaseManager()
bot_manager = BotManager(db_manager)


# ==================== Pydantic Models ====================

class BotConfigModel(BaseModel):
    """Bot configuration"""
    symbols: List[str]
    strategies: List[str]
    initial_capital: float = 10000
    paper_trading: bool = True
    timeframe: str = "1d"
    run_interval_seconds: int = 60
    max_position_size: float = 0.1
    stop_loss_pct: float = 0.05
    take_profit_pct: float = 0.10
    max_portfolio_risk: float = 0.02


class CreateBotRequest(BaseModel):
    """Request to create a new bot"""
    name: str
    description: Optional[str] = ""
    portfolio_id: int
    config: BotConfigModel


class UpdateBotRequest(BaseModel):
    """Request to update a bot"""
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[BotConfigModel] = None


class StartBotRequest(BaseModel):
    """Request to start a bot"""
    api_key: Optional[str] = None
    api_secret: Optional[str] = None


class BotResponse(BaseModel):
    """Bot response"""
    id: int
    name: str
    description: Optional[str]
    portfolio_id: int
    status: str
    is_running: bool
    created_at: Optional[str]
    last_run_at: Optional[str]
    config: Dict[str, Any]
    portfolio_summary: Optional[Dict[str, Any]] = None


# ==================== API Endpoints ====================

@router.post("/", response_model=BotResponse, status_code=status.HTTP_201_CREATED)
async def create_bot(request: CreateBotRequest):
    """
    Create a new trading bot
    
    - **name**: Unique bot name
    - **description**: Bot description
    - **portfolio_id**: Portfolio to use for trading
    - **config**: Bot configuration (symbols, strategies, risk params)
    """
    try:
        bot = bot_manager.create_bot(
            name=request.name,
            description=request.description,
            portfolio_id=request.portfolio_id,
            config=request.config.dict()
        )
        
        return bot_manager.get_bot_status(bot.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create bot: {str(e)}")


@router.get("/", response_model=List[BotResponse])
async def list_bots(active_only: bool = True):
    """
    List all bots
    
    - **active_only**: Only return active bots (default: true)
    """
    try:
        statuses = bot_manager.list_bot_statuses()
        if active_only:
            statuses = [s for s in statuses if s.get('status') != 'deleted']
        return statuses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list bots: {str(e)}")


@router.get("/{bot_id}", response_model=BotResponse)
async def get_bot(bot_id: int):
    """
    Get bot details by ID
    
    - **bot_id**: Bot ID
    """
    try:
        bot_status = bot_manager.get_bot_status(bot_id)
        if not bot_status:
            raise HTTPException(status_code=404, detail=f"Bot {bot_id} not found")
        return bot_status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bot: {str(e)}")


@router.put("/{bot_id}", response_model=BotResponse)
async def update_bot(bot_id: int, request: UpdateBotRequest):
    """
    Update bot configuration
    
    - **bot_id**: Bot ID
    - **name**: New bot name (optional)
    - **description**: New description (optional)
    - **config**: New configuration (optional)
    """
    try:
        # Check if bot is running
        bot_status = bot_manager.get_bot_status(bot_id)
        if not bot_status:
            raise HTTPException(status_code=404, detail=f"Bot {bot_id} not found")
        
        if bot_status['is_running']:
            raise HTTPException(
                status_code=400,
                detail="Cannot update bot while it's running. Stop the bot first."
            )
        
        # Prepare update data
        update_data = {}
        if request.name:
            update_data['name'] = request.name
        if request.description is not None:
            update_data['description'] = request.description
        if request.config:
            update_data['config'] = request.config.dict()
        
        bot_manager.update_bot(bot_id, **update_data)
        return bot_manager.get_bot_status(bot_id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update bot: {str(e)}")


@router.delete("/{bot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bot(bot_id: int):
    """
    Delete a bot (soft delete)
    
    - **bot_id**: Bot ID
    """
    try:
        success = bot_manager.delete_bot(bot_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Bot {bot_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete bot: {str(e)}")


@router.post("/{bot_id}/start", response_model=BotResponse)
async def start_bot(bot_id: int, request: StartBotRequest = None):
    """
    Start a bot
    
    - **bot_id**: Bot ID
    - **api_key**: Alpaca API key (optional, uses env if not provided)
    - **api_secret**: Alpaca API secret (optional, uses env if not provided)
    """
    try:
        bot_status = bot_manager.get_bot_status(bot_id)
        if not bot_status:
            raise HTTPException(status_code=404, detail=f"Bot {bot_id} not found")
        
        if bot_status['is_running']:
            raise HTTPException(status_code=400, detail="Bot is already running")
        
        api_key = request.api_key if request else None
        api_secret = request.api_secret if request else None
        
        success = bot_manager.start_bot(bot_id, api_key, api_secret)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to start bot")
        
        return bot_manager.get_bot_status(bot_id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start bot: {str(e)}")


@router.post("/{bot_id}/stop", response_model=BotResponse)
async def stop_bot(bot_id: int):
    """
    Stop a running bot
    
    - **bot_id**: Bot ID
    """
    try:
        bot_status = bot_manager.get_bot_status(bot_id)
        if not bot_status:
            raise HTTPException(status_code=404, detail=f"Bot {bot_id} not found")
        
        if not bot_status['is_running']:
            raise HTTPException(status_code=400, detail="Bot is not running")
        
        success = bot_manager.stop_bot(bot_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to stop bot")
        
        return bot_manager.get_bot_status(bot_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop bot: {str(e)}")


@router.post("/{bot_id}/restart", response_model=BotResponse)
async def restart_bot(bot_id: int):
    """
    Restart a bot (stop then start)
    
    - **bot_id**: Bot ID
    """
    try:
        bot_status = bot_manager.get_bot_status(bot_id)
        if not bot_status:
            raise HTTPException(status_code=404, detail=f"Bot {bot_id} not found")
        
        # Stop if running
        if bot_status['is_running']:
            bot_manager.stop_bot(bot_id)
        
        # Start
        success = bot_manager.start_bot(bot_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to restart bot")
        
        return bot_manager.get_bot_status(bot_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restart bot: {str(e)}")


@router.get("/{bot_id}/signals")
async def get_bot_signals(bot_id: int, limit: int = 50):
    """
    Get signals generated by a specific bot
    
    - **bot_id**: Bot ID
    - **limit**: Maximum number of signals to return
    """
    try:
        with db_manager.get_session() as session:
            from trader.database.models import Signal
            signals = session.query(Signal).filter(
                Signal.bot_id == bot_id
            ).order_by(Signal.timestamp.desc()).limit(limit).all()
            
            return [
                {
                    'id': s.id,
                    'timestamp': s.timestamp.isoformat(),
                    'symbol': s.symbol,
                    'signal_type': s.signal_type,
                    'strategy_name': s.strategy_name,
                    'price': s.price,
                    'confidence': s.confidence,
                    'executed': s.executed
                }
                for s in signals
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get signals: {str(e)}")


@router.get("/strategies/available")
async def get_available_strategies():
    """
    Get list of available trading strategies
    """
    return {
        'strategies': [
            {
                'name': 'moving_average',
                'display_name': 'Moving Average Crossover',
                'description': 'Generates signals based on moving average crossovers'
            },
            {
                'name': 'rsi',
                'display_name': 'RSI Strategy',
                'description': 'Relative Strength Index momentum strategy'
            },
            {
                'name': 'macd',
                'display_name': 'MACD Strategy',
                'description': 'Moving Average Convergence Divergence strategy'
            },
            {
                'name': 'bollinger_bands',
                'display_name': 'Bollinger Bands',
                'description': 'Volatility-based trading strategy'
            }
        ]
    }
