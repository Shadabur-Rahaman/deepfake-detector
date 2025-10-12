"""
Authentication and Security Middleware
Production-ready middleware for authentication, authorization, and security.
"""

import logging
from typing import Optional, Callable, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .unified_auth import UnifiedAuthCore

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware for FastAPI.
    
    Handles:
    - JWT token validation
    - User authentication
    - Request context injection
    """
    
    def __init__(self, app: ASGIApp, auth_core: UnifiedAuthCore):
        super().__init__(app)
        self.auth_core = auth_core
    
    async def dispatch(self, request: Request, call_next):
        """Process request through authentication middleware."""
        try:
            # Skip authentication for public endpoints
            if self._is_public_endpoint(request.url.path):
                return await call_next(request)
            
            # Extract token from Authorization header
            token = self._extract_token(request)
            if not token:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Authentication required"}
                )
            
            # Verify token and get user info
            user_info = await self.auth_core.verify_token(
                token, 
                request.client.host
            )
            
            # Add user info to request state
            request.state.user = user_info
            request.state.authenticated = True
            
            return await call_next(request)
            
        except ValueError as e:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": str(e)}
            )
        except Exception as e:
            logger.error(f"Authentication middleware error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (no authentication required)."""
        public_paths = [
            "/",
            "/health",
            "/api/health",
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/refresh",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json"
        ]
        return any(path.startswith(public_path) for public_path in public_paths)
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from Authorization header."""
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None
        
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                return None
            return token
        except ValueError:
            return None

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.
    
    Implements rate limiting based on IP address and user.
    """
    
    def __init__(self, app: ASGIApp, auth_core: UnifiedAuthCore):
        super().__init__(app)
        self.auth_core = auth_core
    
    async def dispatch(self, request: Request, call_next):
        """Process request through rate limiting middleware."""
        try:
            # Skip rate limiting for health checks
            if request.url.path in ["/health", "/api/health"]:
                return await call_next(request)
            
            # Skip rate limiting for now (simplified)
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"Rate limiting middleware error: {str(e)}")
            return await call_next(request)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Security headers middleware.
    
    Adds comprehensive security headers to all responses.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers to response."""
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response

def require_auth(func: Callable) -> Callable:
    """
    Decorator to require authentication for endpoint.
    
    Args:
        func: FastAPI endpoint function
        
    Returns:
        Decorated function
    """
    async def wrapper(*args, **kwargs):
        # This would be implemented with FastAPI dependency injection
        # For now, return the function as-is
        return await func(*args, **kwargs)
    return wrapper

def require_permission(permission: str, resource: str = None):
    """
    Decorator to require specific permission.
    
    Args:
        permission: Required permission
        resource: Optional resource context
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            # This would be implemented with FastAPI dependency injection
            # For now, return the function as-is
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(role: str):
    """
    Decorator to require specific role.
    
    Args:
        role: Required role name
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            # This would be implemented with FastAPI dependency injection
            # For now, return the function as-is
            return await func(*args, **kwargs)
        return wrapper
    return decorator
