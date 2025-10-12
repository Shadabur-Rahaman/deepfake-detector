"""
Authentication Exceptions
Custom exceptions for authentication and authorization.

Author: Senior Backend Engineer
"""

class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass

class AuthorizationError(Exception):
    """Raised when authorization fails"""
    pass

class TokenExpiredError(AuthenticationError):
    """Raised when JWT token has expired"""
    pass

class InvalidTokenError(AuthenticationError):
    """Raised when JWT token is invalid"""
    pass

class UserNotFoundError(AuthenticationError):
    """Raised when user is not found"""
    pass

class UserInactiveError(AuthenticationError):
    """Raised when user account is inactive"""
    pass

class PasswordMismatchError(AuthenticationError):
    """Raised when password doesn't match"""
    pass

class RateLimitExceededError(AuthenticationError):
    """Raised when rate limit is exceeded"""
    pass

class SessionExpiredError(AuthenticationError):
    """Raised when user session has expired"""
    pass

class InsufficientPermissionsError(AuthorizationError):
    """Raised when user lacks required permissions"""
    pass

class RoleNotFoundError(AuthorizationError):
    """Raised when role is not found"""
    pass

class PermissionNotFoundError(AuthorizationError):
    """Raised when permission is not found"""
    pass

class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid"""
    pass

class AccountLockedError(AuthenticationError):
    """Raised when account is locked"""
    pass

class SessionNotFoundError(AuthenticationError):
    """Raised when session is not found"""
    pass

class TokenExpiredError(AuthenticationError):
    """Raised when token has expired"""
    pass

class InvalidTokenError(AuthenticationError):
    """Raised when token is invalid"""
    pass