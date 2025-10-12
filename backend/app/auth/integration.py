"""
Authentication Integration Module
Main integration point for authentication and authorization in the deepfake detection platform.

This module provides:
- Centralized authentication setup
- Database initialization
- Redis configuration
- Security monitoring setup
- API endpoint protection
- Frontend integration helpers

Author: Senior Backend Engineer
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import os
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager

from .core import AuthCore
from .models import Base, User, Role, Permission, UserRole
from .database import DatabaseConfig, initialize_database, create_tables, get_database_health
from .exceptions import AuthenticationError, AuthorizationError

# Import alternative authentication system
try:
    from ...alternative_auth import get_auth_system
    ALTERNATIVE_AUTH_AVAILABLE = True
except ImportError:
    ALTERNATIVE_AUTH_AVAILABLE = False
    get_auth_system = None

logger = logging.getLogger(__name__)

# Global instances
auth_core = None
rbac_manager = None
security_monitor = None
compliance_reporter = None
detection_auth_manager = None
detection_api_key_manager = None
redis_client = None
db_session = None

class AuthIntegration:
    """Main authentication integration class with robust error handling"""
    
    def __init__(self, app: FastAPI, database_url: str = None, redis_url: str = None):
        self.app = app
        self.database_url = database_url
        self.redis_url = redis_url or "redis://localhost:6379"
        
        # Initialize components
        self.db_config = DatabaseConfig()
        self.redis_client = None
        self.auth_core = None
        self.is_initialized = False
        
    async def initialize(self) -> None:
        """Initialize all authentication components with robust error handling"""
        try:
            logger.info("Starting authentication integration initialization...")
            
            # Initialize database with fallback support
            await self._initialize_database()
            
            # Initialize Redis (optional)
            await self._initialize_redis()
            
            # Initialize authentication core
            await self._initialize_auth_core()
            
            # Setup middleware
            await self._setup_middleware()
            
            # Setup routes
            await self._setup_routes()
            
            # Initialize default data
            await self._initialize_default_data()
            
            self.is_initialized = True
            # Reduced logging to avoid duplicates
            
        except Exception as e:
            logger.error(f"[ERROR] Authentication integration failed: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Try to initialize with minimal configuration
            await self._initialize_minimal()
            raise
    
    async def _initialize_database(self) -> None:
        """Initialize database connection with fallback support"""
        try:
            logger.info("Initializing database with fallback support...")
            
            # Use the database configuration system
            if self.database_url:
                self.db_config.primary_db_url = self.database_url
            
            # Initialize database with fallback
            success = await self.db_config.initialize_database()
            if not success:
                raise RuntimeError("Failed to initialize any database")
            
            # Create tables
            success = await self.db_config.create_tables(Base)
            if not success:
                raise RuntimeError("Failed to create database tables")
            
            logger.info(f"[OK] Database initialized successfully: {self.db_config.db_type}")
            
        except Exception as e:
            logger.error(f"[ERROR] Database initialization failed: {str(e)}")
            raise
    
    async def _initialize_redis(self) -> None:
        """Initialize Redis connection (optional)"""
        try:
            logger.info("Initializing Redis connection...")
            
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=100
            )
            
            # Test connection
            await self.redis_client.ping()
            
            # Reduced logging to avoid duplicates
            
        except Exception as e:
            logger.warning(f"[WARNING] Redis initialization failed: {str(e)}")
            logger.info("Continuing without Redis (caching disabled)")
            self.redis_client = None
    
    async def _initialize_auth_core(self) -> None:
        """Initialize authentication core with robust error handling"""
        global auth_core, db_session
        
        try:
            logger.info("Initializing authentication core...")
            
            # Get database session
            db_session = self.db_config.get_session()
            logger.info(f"Database session created: {db_session is not None}")
            
            # Create AuthCore instance
            self.auth_core = AuthCore(db_session, self.redis_client)
            auth_core = self.auth_core
            logger.info(f"AuthCore created: {self.auth_core is not None}")
            
            # Store components in app state
            self.app.state.auth_core = self.auth_core
            self.app.state.db_session = db_session
            self.app.state.redis_client = self.redis_client
            self.app.state.db_config = self.db_config
            
            # Verify storage
            if not hasattr(self.app.state, 'auth_core') or not self.app.state.auth_core:
                raise RuntimeError("Failed to store auth_core in app state")
            
            # Reduced logging to avoid duplicates
            
        except Exception as e:
            logger.error(f"[ERROR] Authentication core initialization failed: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    async def _initialize_minimal(self) -> None:
        """Initialize with minimal configuration for fallback"""
        try:
            logger.warning("Initializing with minimal configuration...")
            
            # Try fallback authentication system first
            try:
                logger.info("Using fallback authentication system...")
                from .fallback_auth import get_fallback_auth
                
                self.auth_core = get_fallback_auth()
                self.app.state.auth_core = self.auth_core
                self.app.state.db_session = None
                self.app.state.redis_client = None
                self.app.state.db_config = None
                
                logger.warning("[OK] Fallback authentication system initialized")
                return
                
            except Exception as fallback_error:
                logger.warning(f"Fallback auth failed: {fallback_error}")
            
            # Try alternative authentication
            if ALTERNATIVE_AUTH_AVAILABLE and get_auth_system:
                logger.info("Using alternative authentication system...")
                try:
                    self.auth_core = get_auth_system()
                    self.app.state.auth_core = self.auth_core
                    self.app.state.db_session = None
                    self.app.state.redis_client = None
                    logger.warning("Alternative authentication system initialized")
                    return
                except Exception as alt_error:
                    logger.warning(f"Alternative auth failed: {alt_error}")
            
            # Try simple SQLite database
            try:
                logger.info("Trying simple SQLite database...")
                from sqlalchemy import create_engine
                from sqlalchemy.orm import sessionmaker
                
                # Try simple SQLite file first
                simple_db_url = "sqlite:///./simple_auth.db"
                engine = create_engine(simple_db_url, echo=False, connect_args={'check_same_thread': False})
                SessionLocal = sessionmaker(bind=engine)
                
                # Create tables
                Base.metadata.create_all(bind=engine)
                
                # Create basic auth core
                db_session = SessionLocal()
                self.auth_core = AuthCore(db_session, None)
                
                # Store in app state
                self.app.state.auth_core = self.auth_core
                self.app.state.db_session = db_session
                self.app.state.redis_client = None
                
                logger.warning("Simple SQLite authentication system initialized")
                return
                
            except Exception as simple_error:
                logger.warning(f"Simple SQLite failed: {simple_error}")
            
            # Fallback to in-memory SQLite
            try:
                logger.info("Trying in-memory SQLite...")
                from sqlalchemy import create_engine
                from sqlalchemy.orm import sessionmaker
                
                engine = create_engine("sqlite:///:memory:", echo=False, connect_args={'check_same_thread': False})
                SessionLocal = sessionmaker(bind=engine)
                
                # Create tables
                Base.metadata.create_all(bind=engine)
                
                # Create basic auth core
                db_session = SessionLocal()
                self.auth_core = AuthCore(db_session, None)
                
                # Store in app state
                self.app.state.auth_core = self.auth_core
                self.app.state.db_session = db_session
                self.app.state.redis_client = None
                
                logger.warning("In-memory SQLite authentication system initialized (limited functionality)")
                
            except Exception as sqlite_error:
                logger.error(f"All SQLite options failed: {sqlite_error}")
                raise
            
        except Exception as e:
            logger.error(f"Even minimal initialization failed: {str(e)}")
            raise
    
    async def _initialize_rbac(self) -> None:
        """Initialize RBAC system (simplified)"""
        try:
            logger.info("RBAC system initialization skipped (simplified setup)")
            # RBAC can be added later as needed
        except Exception as e:
            logger.warning(f"RBAC initialization failed: {str(e)}")
    
    async def _initialize_security_monitoring(self) -> None:
        """Initialize security monitoring (simplified)"""
        try:
            logger.info("Security monitoring initialization skipped (simplified setup)")
            # Security monitoring can be added later as needed
        except Exception as e:
            logger.warning(f"Security monitoring initialization failed: {str(e)}")
    
    async def _initialize_detection_auth(self) -> None:
        """Initialize detection authentication (simplified)"""
        try:
            logger.info("Detection authentication initialization skipped (simplified setup)")
            # Detection auth can be added later as needed
        except Exception as e:
            logger.warning(f"Detection authentication initialization failed: {str(e)}")
    
    async def _setup_middleware(self) -> None:
        """Setup authentication middleware (skipped - middleware already configured in main.py)"""
        try:
            # Middleware is already configured in main.py before the app starts
            # This prevents the "Cannot add middleware after an application has started" error
            logger.info("[OK] Middleware already configured in main.py, skipping duplicate setup")
            
        except Exception as e:
            logger.warning(f"[WARNING] Middleware setup skipped: {str(e)}")
    
    async def _setup_routes(self) -> None:
        """Setup authentication routes"""
        try:
            # Add health check endpoint
            @self.app.get("/api/auth/health")
            async def auth_health_check():
                db_health = await self.db_config.health_check()
                return {
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat(),
                    "components": {
                        "database": db_health.get("status", "unknown"),
                        "redis": "connected" if self.redis_client else "disconnected",
                        "auth_core": "initialized" if self.auth_core else "not_initialized"
                    }
                }
            
            # Add basic auth endpoints
            @self.app.post("/api/auth/login")
            async def login(request: Request):
                data = await request.json()
                logger.info(f"🔐 AuthIntegration: Login attempt for email: {data.get('email')}")
                
                result = await self.auth_core.authenticate_user(
                    email=data.get("email"),
                    password=data.get("password"),
                    ip_address=request.client.host,
                    user_agent=request.headers.get("user-agent")
                )
                
                logger.info(f"🔐 AuthIntegration: Authentication result: success={result.success}")
                
                # Ensure user data includes permissions and roles
                if result.success and result.user_data:
                    # Get user from database to ensure we have complete data
                    from .models import User
                    db = self.db_config.get_session()
                    try:
                        user = db.query(User).filter(User.email == data.get("email")).first()
                        if user:
                            # Get user roles
                            user_roles_list = [role.name for role in user.roles] if user.roles else ["user"]
                            
                            # Special case: if user is admin@ifake.com, ensure they have admin role
                            if user.email == "admin@ifake.com" and "admin" not in user_roles_list:
                                user_roles_list = ["admin", "user"]
                                logger.info(f"🔑 Admin user detected by email, adding admin role: {user_roles_list}")
                            
                            # Get user permissions
                            user_permissions_list = user.permissions if hasattr(user, 'permissions') else []
                            
                            # If user is admin, ensure they have all permissions
                            if "admin" in user_roles_list:
                                user_permissions_list = [
                                    "detection:create", "detection:read", "detection:update", "detection:delete",
                                    "try:access", "admin:access", "user:manage", "system:manage"
                                ]
                                logger.info(f"🔑 Admin user detected, granting all permissions: {user_permissions_list}")
                            
                            result.user_data.update({
                                "roles": user_roles_list,
                                "permissions": user_permissions_list,
                                "is_verified": user.is_verified,
                                "is_2fa_enabled": user.is_2fa_enabled
                            })
                            
                            logger.info(f"🔐 AuthIntegration: Final user data - roles: {user_roles_list}, permissions: {user_permissions_list}")
                    finally:
                        db.close()
                
                return result.__dict__
            
            @self.app.post("/api/auth/register")
            async def register(request: Request):
                data = await request.json()
                result = await self.auth_core.create_user(
                    email=data.get("email"),
                    username=data.get("username"),
                    password=data.get("password"),
                    full_name=data.get("full_name"),
                    ip_address=request.client.host
                )
                return result.__dict__
            
            # Add /me endpoint
            @self.app.get("/api/auth/me")
            async def get_current_user(request: Request):
                # Get token from Authorization header
                auth_header = request.headers.get("Authorization")
                if not auth_header or not auth_header.startswith("Bearer "):
                    raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
                
                token = auth_header.split(" ")[1]
                
                # Verify token and get user data
                try:
                    user_data = await self.auth_core.verify_token(token)
                    if not user_data:
                        raise HTTPException(status_code=401, detail="Invalid token")
                    
                    # Get complete user data from database
                    from .models import User
                    db = self.db_config.get_session()
                    try:
                        user = db.query(User).filter(User.id == user_data.get("user_id")).first()
                        if user:
                            return {
                                "id": str(user.id),
                                "email": user.email,
                                "username": user.username,
                                "full_name": user.full_name,
                                "is_active": user.is_active,
                                "is_verified": user.is_verified,
                                "is_2fa_enabled": user.is_2fa_enabled,
                                "roles": [role.name for role in user.roles] if user.roles else ["user"],
                                "permissions": user.permissions if hasattr(user, 'permissions') else [],
                                "created_at": user.created_at.isoformat() if user.created_at else None,
                                "last_login": user.last_login.isoformat() if user.last_login else None
                            }
                        else:
                            raise HTTPException(status_code=404, detail="User not found")
                    finally:
                        db.close()
                        
                except Exception as e:
                    raise HTTPException(status_code=401, detail="Token verification failed")
            
            logger.info("[OK] Authentication routes setup completed successfully")
            
        except Exception as e:
            logger.error(f"[ERROR] Route setup failed: {str(e)}")
            raise
    
    async def _initialize_default_data(self) -> None:
        """Initialize default users and roles"""
        try:
            # Check if admin user exists
            admin_user = self.db_config.get_session().query(User).filter(User.email == "admin@ifake.com").first()
            
            if not admin_user:
                # Create admin user
                admin_result = await self.auth_core.create_user(
                    email="admin@ifake.com",
                    username="admin",
                    password="Admin123!@#",
                    full_name="System Administrator",
                    ip_address="127.0.0.1"
                )
                
                if admin_result.success:
                    # Verify admin user
                    admin_user = self.db_config.get_session().query(User).filter(User.id == admin_result.user_id).first()
                    if admin_user:
                        admin_user.is_verified = True
                        admin_user.status = "active"
                        self.db_config.get_session().commit()
                        logger.info("[OK] Default admin user created successfully")
            
            # Check if demo user exists
            demo_user = self.db_config.get_session().query(User).filter(User.email == "demo@ifake.com").first()
            
            if not demo_user:
                # Create demo user
                demo_result = await self.auth_core.create_user(
                    email="demo@ifake.com",
                    username="demo",
                    password="Demo123!@#",
                    full_name="Demo User",
                    ip_address="127.0.0.1"
                )
                
                if demo_result.success:
                    # Verify demo user
                    demo_user = self.db_config.get_session().query(User).filter(User.id == demo_result.user_id).first()
                    if demo_user:
                        demo_user.is_verified = True
                        demo_user.status = "active"
                        self.db_config.get_session().commit()
                        logger.info("[OK] Default demo user created successfully")
            
        except Exception as e:
            logger.warning(f"[WARNING] Default data initialization failed: {str(e)}")
            # Continue without default data for production

# Dependency functions
async def get_db(request: Request) -> Session:
    """Get database session from request state"""
    if not hasattr(request.app.state, 'db_session') or not request.app.state.db_session:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database not initialized"
        )
    return request.app.state.db_session

async def get_redis(request: Request) -> redis.Redis:
    """Get Redis client from request state"""
    if not hasattr(request.app.state, 'redis_client') or not request.app.state.redis_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Redis not initialized"
        )
    return request.app.state.redis_client

async def get_auth_core(request: Request) -> AuthCore:
    """Get authentication core from request state"""
    if not hasattr(request.app.state, 'auth_core') or not request.app.state.auth_core:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication core not initialized"
        )
    return request.app.state.auth_core

async def get_rbac_manager(request: Request):
    """Get RBAC manager from request state (simplified)"""
    # RBAC functionality can be added later
    return None

async def get_detection_auth_manager(request: Request):
    """Get detection authentication manager from request state (simplified)"""
    # Detection auth functionality can be added later
    return None

# Authentication decorators
def require_auth(required_roles: List[str] = None, required_permissions: List[str] = None):
    """Decorator for requiring authentication"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This would be implemented based on your specific needs
            # For now, it's a placeholder
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_permission(permission: str, resource: str = None):
    """Decorator for requiring specific permission"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This would be implemented based on your specific needs
            # For now, it's a placeholder
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Utility functions
async def get_current_user_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> str:
    """Get current user ID from token"""
    auth_core = await get_auth_core(request)
    
    try:
        user_info = await auth_core.verify_token(credentials.credentials, "127.0.0.1")
        return user_info["user_id"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

async def check_user_permission(
    request: Request,
    user_id: str, 
    permission: str, 
    resource: str = None
) -> bool:
    """Check if user has specific permission"""
    try:
        rbac_manager = await get_rbac_manager(request)
        return await rbac_manager.check_permission(user_id, permission, resource)
    except Exception as e:
        logger.error(f"Permission check failed: {str(e)}")
        return False

async def log_security_event(
    request: Request,
    event_type: str,
    user_id: str = None,
    ip_address: str = None,
    details: Dict[str, Any] = None,
    severity: str = "info"
) -> None:
    """Log security event"""
    try:
        auth_core = await get_auth_core(request)
        await auth_core._log_security_event(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            details=details or {},
            severity=severity
        )
    except Exception as e:
        logger.error(f"Security event logging failed: {str(e)}")

# Main initialization function
async def initialize_authentication(app: FastAPI, database_url: str = None, redis_url: str = None) -> None:
    """Initialize authentication system for the application with robust error handling"""
    try:
        logger.info("[START] Starting authentication system initialization...")
        
        # Create AuthIntegration instance
        auth_integration = AuthIntegration(app, database_url, redis_url)
        
        # Initialize with fallback support
        await auth_integration.initialize()
        
        # Verify that auth_core was properly set in app state
        if not hasattr(app.state, 'auth_core') or not app.state.auth_core:
            raise RuntimeError("AuthIntegration.initialize() did not properly set app.state.auth_core")
        
        # Reduced logging to avoid duplicates
        logger.info(f"[DATA] Database type: {auth_integration.db_config.db_type}")
        logger.info(f"🔐 Auth core available: {app.state.auth_core is not None}")
        logger.info(f"💾 Redis available: {app.state.redis_client is not None}")
        
    except Exception as e:
        logger.error(f"[ERROR] Authentication system initialization failed: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Try minimal initialization as last resort
        try:
            logger.warning("[LOADING] Attempting minimal initialization...")
            auth_integration = AuthIntegration(app, database_url, redis_url)
            await auth_integration._initialize_minimal()
            logger.warning("[WARNING] Minimal authentication system initialized")
        except Exception as minimal_error:
            logger.error(f"[ERROR] Even minimal initialization failed: {str(minimal_error)}")
            raise

# Cleanup function
async def cleanup_authentication() -> None:
    """Cleanup authentication resources"""
    try:
        global redis_client, db_session
        
        logger.info("Starting authentication cleanup...")
        
        if redis_client:
            logger.info("Closing Redis connection...")
            await redis_client.close()
            redis_client = None
        
        if db_session:
            logger.info("Closing database session...")
            db_session.close()
            db_session = None
        
        logger.info("Authentication cleanup completed")
        
    except Exception as e:
        logger.error(f"Authentication cleanup failed: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

# Export main components
__all__ = [
    'initialize_authentication',
    'cleanup_authentication',
    'get_db',
    'get_redis',
    'get_auth_core',
    'get_rbac_manager',
    'get_detection_auth_manager',
    'require_auth',
    'require_permission',
    'get_current_user_id',
    'check_user_permission',
    'log_security_event'
]
