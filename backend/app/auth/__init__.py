"""
Production-Ready Authentication & Authorization Module
for iFake Deepfake Detection Platform

This module provides enterprise-grade authentication and authorization
capabilities with comprehensive security features.

Author: Senior Backend Engineer
Version: 1.0.0
"""

from .core import AuthCore
from .models import User, Role, Permission, UserRole
from .security import SecurityManager, PasswordManager, TokenManager
from .rbac import RBACManager
from .middleware import AuthMiddleware, RateLimitMiddleware
from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    TokenExpiredError,
    InvalidCredentialsError,
    AccountLockedError,
    RateLimitExceededError
)

__all__ = [
    'AuthCore',
    'User', 'Role', 'Permission', 'UserRole',
    'SecurityManager', 'PasswordManager', 'TokenManager',
    'RBACManager',
    'AuthMiddleware', 'RateLimitMiddleware',
    'AuthenticationError', 'AuthorizationError', 'TokenExpiredError',
    'InvalidCredentialsError', 'AccountLockedError', 'RateLimitExceededError'
]

__version__ = "1.0.0"


