"""
Startup Event Handler - Non-blocking FastAPI Startup
Replaces the blocking startup_event functions with async, non-blocking initialization

This module provides:
- Non-blocking startup event handlers
- Background model loading
- Proper async/await handling
- Timeout protection
- Error recovery and fallback mechanisms
- Clear SERVER READY checkpoint

Author: Senior Backend Engineer
Date: 2024
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional
from fastapi import FastAPI

from .async_startup_manager import get_startup_manager, initialize_async_startup

# Configure logging
logger = logging.getLogger(__name__)

class StartupEventHandler:
    """
    Non-blocking startup event handler for FastAPI applications
    """
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.startup_manager = get_startup_manager()
        self.startup_task: Optional[asyncio.Task] = None
        self.startup_results: Optional[Dict[str, Any]] = None
        
    async def handle_startup(self):
        """
        Main startup event handler - truly non-blocking
        """
        logger.info("[START] Starting truly non-blocking startup sequence...")
        
        try:
            # Start async initialization in background without waiting
            self.startup_task = asyncio.create_task(
                self._run_async_initialization()
            )
            
            # Don't wait for completion - let it run in background
            logger.info("[OK] Background model initialization started")
            
            # Server is immediately ready - models will load in background
            self.app.state.startup_complete = True
            self.app.state.startup_results = {
                "status": "models_loading",
                "message": "Server ready, models loading in background",
                "server_ready": True
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Startup event handler failed: {e}")
            # Set fallback state - server still ready
            self.app.state.startup_complete = True
            self.app.state.startup_results = {
                "error": str(e), 
                "fallback": True,
                "server_ready": True
            }
    
    async def _run_async_initialization(self):
        """
        Run async initialization in background with full logging and timeout protection
        """
        try:
            logger.info("[LOADING] Running background model initialization with full logging...")
            logger.info("[INFO] You will see all model loading logs below:")
            logger.info("=" * 60)
            
            # Run the async startup manager with timeout
            self.startup_results = await asyncio.wait_for(
                initialize_async_startup(),
                timeout=120  # 2 minute timeout
            )
            
            # Store results in app state
            self.app.state.startup_results = self.startup_results
            self.app.state.startup_complete = True
            
            # Log completion with SERVER READY checkpoint
            if self.startup_results.get('server_ready', False):
                logger.info("=" * 60)
                logger.info("[COMPLETE] === SERVER READY ===")
                logger.info(f"[MODELS] Models loaded: {len(self.startup_results.get('models_loaded', {}))}")
                logger.info(f"[OK] Test inferences: {len([r for r in self.startup_results.get('test_results', {}).values() if r.get('success')])}")
                logger.info(f"[TIME]  Total time: {self.startup_results.get('total_time', 0):.2f}s")
                logger.info("=" * 60)
            else:
                logger.warning("[WARNING] Background startup completed with issues")
                
        except asyncio.TimeoutError:
            logger.warning("[TIMEOUT] Background model initialization timed out after 2 minutes")
            # Set timeout state - server still ready
            self.app.state.startup_complete = True
            self.app.state.startup_results = {
                "status": "timeout",
                "message": "Model loading timed out, server ready with fallback",
                "server_ready": True,
                "timeout": True
            }
        except Exception as e:
            logger.error(f"[ERROR] Background startup failed: {e}")
            # Set error state - server still ready
            self.app.state.startup_complete = True
            self.app.state.startup_results = {
                "error": str(e),
                "server_ready": True,
                "fallback": True
            }
    
    def get_startup_status(self) -> Dict[str, Any]:
        """
        Get current startup status
        """
        if self.startup_results is not None:
            return self.startup_results
        
        # Return current status from startup manager
        return self.startup_manager.get_startup_status()
    
    def is_startup_complete(self) -> bool:
        """
        Check if startup is complete
        """
        return getattr(self.app.state, 'startup_complete', False)

# Global startup event handler
_startup_handler: Optional[StartupEventHandler] = None

def get_startup_handler(app: FastAPI) -> StartupEventHandler:
    """Get the startup event handler for the app"""
    global _startup_handler
    if _startup_handler is None:
        _startup_handler = StartupEventHandler(app)
    return _startup_handler

async def startup_event_handler(app: FastAPI):
    """
    Non-blocking startup event handler
    """
    handler = get_startup_handler(app)
    await handler.handle_startup()

def get_startup_status(app: FastAPI) -> Dict[str, Any]:
    """Get startup status from app state"""
    return getattr(app.state, 'startup_results', {})

def is_startup_complete(app: FastAPI) -> bool:
    """Check if startup is complete"""
    return getattr(app.state, 'startup_complete', False)
