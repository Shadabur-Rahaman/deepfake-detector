"""
Authentication Dependencies for FastAPI
Provides dependency injection for authentication, authorization, and security features.
"""

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, List
import logging
from datetime import datetime

from .security import security_manager, SessionManager
from .models import User, UserRole, UserStatus, AuditLog
from .database import get_db

logger = logging.getLogger(__name__)

# Security scheme
security_scheme = HTTPBearer()

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    try:
        # Verify JWT token
        payload = security_manager.verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )
        
        # Check if user is suspended
        if user.status == UserStatus.SUSPENDED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is suspended"
            )
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked"
            )
        
        # Log successful authentication
        security_manager.log_security_event(
            event_type="user_authenticated",
            user_id=str(user.id),
            ip_address=request.client.host,
            details={"user_agent": request.headers.get("user-agent")}
        )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (additional check for active status)"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current verified user"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    return current_user

def require_role(required_roles: List[UserRole]):
    """Dependency factory for role-based access control"""
    async def role_checker(current_user: User = Depends(get_current_verified_user)):
        if current_user.plan not in [role.value for role in required_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

def require_permission(permission: str):
    """Dependency factory for permission-based access control"""
    async def permission_checker(current_user: User = Depends(get_current_verified_user)):
        # This would check against user permissions in a more complex system
        # For now, we'll use role-based checks
        if current_user.plan == UserRole.FREE and permission in ["unlimited_detections", "advanced_analysis"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Premium feature - upgrade required"
            )
        return current_user
    return permission_checker

async def check_rate_limit(request: Request):
    """Check rate limiting for requests"""
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    # Create identifier for rate limiting
    identifier = f"{client_ip}:{hash(user_agent)}"
    
    if not security_manager.check_rate_limit(identifier, limit=100, window=3600):  # 100 requests per hour
        security_manager.log_security_event(
            event_type="rate_limit_exceeded",
            user_id=None,
            ip_address=client_ip,
            details={"user_agent": user_agent, "identifier": identifier}
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )

async def check_brute_force_protection(
    request: Request,
    db: Session = Depends(get_db)
):
    """Check brute force protection for authentication endpoints"""
    client_ip = request.client.host
    
    # Check IP-based rate limiting for auth endpoints
    if not security_manager.check_rate_limit(f"auth:{client_ip}", limit=5, window=900):  # 5 attempts per 15 minutes
        security_manager.log_security_event(
            event_type="brute_force_attempt",
            user_id=None,
            ip_address=client_ip,
            details={"user_agent": request.headers.get("user-agent")}
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many authentication attempts. Please try again later."
        )

async def validate_csrf_token(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Validate CSRF token for state-changing operations"""
    csrf_token = request.headers.get("X-CSRF-Token")
    if not csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token required"
        )
    
    if not security_manager.verify_csrf_token(str(current_user.id), csrf_token):
        security_manager.log_security_event(
            event_type="csrf_token_invalid",
            user_id=str(current_user.id),
            ip_address=request.client.host,
            details={"user_agent": request.headers.get("user-agent")}
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token"
        )

async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(request, credentials, db)
    except HTTPException:
        return None

# Permission decorators
def require_admin():
    """Require admin role"""
    return require_role([UserRole.ADMIN])

def require_premium():
    """Require premium or higher role"""
    return require_role([UserRole.PREMIUM, UserRole.ENTERPRISE, UserRole.ADMIN])

def require_enterprise():
    """Require enterprise or admin role"""
    return require_role([UserRole.ENTERPRISE, UserRole.ADMIN])

# Feature-specific permissions
def require_detection_access():
    """Require detection access permission"""
    return require_permission("detection_access")

def require_unlimited_detections():
    """Require unlimited detections permission"""
    return require_permission("unlimited_detections")

def require_advanced_analysis():
    """Require advanced analysis permission"""
    return require_permission("advanced_analysis")

def require_api_access():
    """Require API access permission"""
    return require_permission("api_access")

# Security event logging
def log_security_event(event_type: str, severity: str = "info"):
    """Decorator to log security events"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request and user from args
            request = None
            user = None
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                elif isinstance(arg, User):
                    user = arg
            
            # Log the event
            if request:
                security_manager.log_security_event(
                    event_type=event_type,
                    user_id=str(user.id) if user else None,
                    ip_address=request.client.host,
                    details={
                        "function": func.__name__,
                        "user_agent": request.headers.get("user-agent")
                    }
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
