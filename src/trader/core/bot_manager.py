"""
Bot Manager - Manages multiple trading bot instances
"""
import json
import threading
from typing import Dict, List, Optional
from datetime import datetime
from trader.database.db_manager import DatabaseManager
from trader.database.models import Bot
from trader.core.portfolio_with_db import PortfolioWithDB
from trader.bots.stock_bot import StockBot
from trader.strategies.moving_average import MovingAverageCrossover
from trader.strategies.rsi_strategy import RSIStrategy
from trader.strategies.macd_strategy import MACDStrategy
from trader.strategies.bollinger_bands import BollingerBandsStrategy
from trader.risk.risk_manager import RiskManager


class BotManager:
    """Manages multiple trading bot instances"""
    
    # Strategy mapping
    STRATEGY_MAP = {
        'moving_average': MovingAverageCrossover,
        'rsi': RSIStrategy,
        'macd': MACDStrategy,
        'bollinger_bands': BollingerBandsStrategy,
    }
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()
        self.running_bots: Dict[int, dict] = {}  # bot_id -> {bot_instance, thread, stop_flag}
        self._lock = threading.Lock()
    
    def create_bot(self, name: str, description: str, portfolio_id: int, config: dict) -> Bot:
        """Create a new bot with configuration"""
        # Validate config
        self._validate_config(config)
        
        # Create bot in database
        session = self.db_manager.get_session()
        try:
            bot = Bot(
                name=name,
                description=description,
                portfolio_id=portfolio_id,
                status='stopped',
                config=json.dumps(config)
            )
            session.add(bot)
            session.commit()
            session.refresh(bot)
            return bot
        finally:
            session.close()
    
    def get_bot(self, bot_id: int) -> Optional[Bot]:
        """Get bot by ID"""
        session = self.db_manager.get_session()
        try:
            return session.query(Bot).filter(Bot.id == bot_id).first()
        finally:
            session.close()
    
    def list_bots(self, active_only: bool = True) -> List[Bot]:
        """List all bots"""
        session = self.db_manager.get_session()
        try:
            query = session.query(Bot)
            if active_only:
                query = query.filter(Bot.is_active == True)
            return query.all()
        finally:
            session.close()
    
    def update_bot(self, bot_id: int, **kwargs) -> Bot:
        """Update bot configuration"""
        session = self.db_manager.get_session()
        try:
            bot = session.query(Bot).filter(Bot.id == bot_id).first()
            if not bot:
                raise ValueError(f"Bot {bot_id} not found")
            
            # Update fields
            for key, value in kwargs.items():
                if key == 'config' and isinstance(value, dict):
                    self._validate_config(value)
                    value = json.dumps(value)
                setattr(bot, key, value)
            
            bot.updated_at = datetime.now()
            session.commit()
            session.refresh(bot)
            return bot
        finally:
            session.close()
    
    def delete_bot(self, bot_id: int) -> bool:
        """Soft delete a bot"""
        # Stop bot if running
        if bot_id in self.running_bots:
            self.stop_bot(bot_id)
        
        session = self.db_manager.get_session()
        try:
            bot = session.query(Bot).filter(Bot.id == bot_id).first()
            if not bot:
                return False
            
            bot.is_active = False
            bot.status = 'deleted'
            session.commit()
            return True
        finally:
            session.close()
    
    def start_bot(self, bot_id: int, api_key: str = None, api_secret: str = None) -> bool:
        """Start a bot"""
        with self._lock:
            # Check if already running
            if bot_id in self.running_bots:
                return False
            
            # Get bot from database
            bot = self.get_bot(bot_id)
            if not bot:
                raise ValueError(f"Bot {bot_id} not found")
            
            # Parse config
            config = json.loads(bot.config)
            
            # Create portfolio
            portfolio = PortfolioWithDB(
                initial_capital=config.get('initial_capital', 10000),
                name=f"bot_{bot_id}_portfolio",
                db_manager=self.db_manager
            )
            
            # Create strategies
            strategies = []
            for strategy_name in config.get('strategies', []):
                strategy_class = self.STRATEGY_MAP.get(strategy_name)
                if strategy_class:
                    strategies.append(strategy_class())
            
            if not strategies:
                raise ValueError("No valid strategies configured")
            
            # Create risk manager
            risk_manager = RiskManager(
                max_position_size=config.get('max_position_size', 0.1),
                stop_loss_pct=config.get('stop_loss_pct', 0.05),
                take_profit_pct=config.get('take_profit_pct', 0.10),
                max_portfolio_risk=config.get('max_portfolio_risk', 0.02)
            )
            
            # Create bot instance
            bot_instance = StockBot(
                portfolio=portfolio,
                strategies=strategies,
                risk_manager=risk_manager,
                symbols=config.get('symbols', []),
                timeframe=config.get('timeframe', '1d'),
                paper_trading=config.get('paper_trading', True)
            )
            
            # Connect to broker
            if api_key and api_secret:
                bot_instance.connect(api_key=api_key, api_secret=api_secret)
            
            # Create stop flag
            stop_flag = threading.Event()
            
            # Create and start thread
            def run_bot():
                try:
                    # Update status
                    self._update_bot_status(bot_id, 'running')
                    
                    while not stop_flag.is_set():
                        # Run one iteration
                        bot_instance.run_once()
                        
                        # Save signals to database with bot_id
                        # (This will be handled in the bot's run_once method)
                        
                        # Update last_run_at
                        self._update_bot_last_run(bot_id)
                        
                        # Wait for interval
                        interval = config.get('run_interval_seconds', 60)
                        stop_flag.wait(interval)
                    
                except Exception as e:
                    print(f"Bot {bot_id} error: {e}")
                    self._update_bot_status(bot_id, 'error')
                finally:
                    bot_instance.stop()
                    self._update_bot_status(bot_id, 'stopped')
            
            thread = threading.Thread(target=run_bot, daemon=True)
            thread.start()
            
            # Store bot info
            self.running_bots[bot_id] = {
                'bot_instance': bot_instance,
                'thread': thread,
                'stop_flag': stop_flag,
                'portfolio': portfolio
            }
            
            return True
    
    def stop_bot(self, bot_id: int) -> bool:
        """Stop a running bot"""
        with self._lock:
            if bot_id not in self.running_bots:
                return False
            
            bot_info = self.running_bots[bot_id]
            bot_info['stop_flag'].set()
            bot_info['thread'].join(timeout=5)
            
            del self.running_bots[bot_id]
            self._update_bot_status(bot_id, 'stopped')
            
            return True
    
    def get_bot_status(self, bot_id: int) -> dict:
        """Get bot status and info"""
        bot = self.get_bot(bot_id)
        if not bot:
            return None
        
        is_running = bot_id in self.running_bots
        
        status = {
            'id': bot.id,
            'name': bot.name,
            'description': bot.description,
            'status': bot.status,
            'is_running': is_running,
            'portfolio_id': bot.portfolio_id,
            'created_at': bot.created_at.isoformat() if bot.created_at else None,
            'last_run_at': bot.last_run_at.isoformat() if bot.last_run_at else None,
            'config': json.loads(bot.config)
        }
        
        # Add runtime info if running
        if is_running:
            bot_info = self.running_bots[bot_id]
            portfolio = bot_info['portfolio']
            summary = portfolio.get_summary()
            status['portfolio_summary'] = summary
        
        return status
    
    def list_bot_statuses(self) -> List[dict]:
        """List all bot statuses"""
        bots = self.list_bots()
        return [self.get_bot_status(bot.id) for bot in bots]
    
    def _validate_config(self, config: dict):
        """Validate bot configuration"""
        required_fields = ['symbols', 'strategies']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required config field: {field}")
        
        # Validate strategies
        for strategy in config['strategies']:
            if strategy not in self.STRATEGY_MAP:
                raise ValueError(f"Unknown strategy: {strategy}")
    
    def _update_bot_status(self, bot_id: int, status: str):
        """Update bot status in database"""
        session = self.db_manager.get_session()
        try:
            bot = session.query(Bot).filter(Bot.id == bot_id).first()
            if bot:
                bot.status = status
                bot.updated_at = datetime.now()
                session.commit()
        finally:
            session.close()
    
    def _update_bot_last_run(self, bot_id: int):
        """Update bot last_run_at timestamp"""
        session = self.db_manager.get_session()
        try:
            bot = session.query(Bot).filter(Bot.id == bot_id).first()
            if bot:
                bot.last_run_at = datetime.now()
                session.commit()
        finally:
            session.close()
    
    def stop_all_bots(self):
        """Stop all running bots"""
        bot_ids = list(self.running_bots.keys())
        for bot_id in bot_ids:
            self.stop_bot(bot_id)
