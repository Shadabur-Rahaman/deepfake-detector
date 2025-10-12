"""
Security Configuration for iFake Deepfake Detection Platform
Centralized configuration for all security-related settings and policies.
"""

import os
from typing import List, Dict, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, use system environment variables

class SecurityConfig(BaseSettings):
    """Security configuration settings"""
    
    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_EXPIRE_HOURS: int = 1
    
    # Password Policy
    MIN_PASSWORD_LENGTH: int = 12
    REQUIRE_UPPERCASE: bool = True
    REQUIRE_LOWERCASE: bool = True
    REQUIRE_NUMBERS: bool = True
    REQUIRE_SPECIAL_CHARS: bool = True
    MAX_PASSWORD_AGE_DAYS: int = 90
    PASSWORD_HISTORY_COUNT: int = 5
    
    # Account Lockout Policy
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30
    LOCKOUT_ESCALATION: bool = True
    ESCALATION_MULTIPLIER: float = 2.0
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 1000
    RATE_LIMIT_AUTH_ATTEMPTS_PER_15MIN: int = 5
    RATE_LIMIT_PASSWORD_RESET_PER_HOUR: int = 3
    
    # Session Management
    SESSION_TIMEOUT_MINUTES: int = 30
    SESSION_EXTEND_ON_ACTIVITY: bool = True
    MAX_CONCURRENT_SESSIONS: int = 5
    SESSION_CLEANUP_INTERVAL_MINUTES: int = 60
    
    # 2FA Configuration
    TOTP_ISSUER: str = "iFake Deepfake Detection"
    TOTP_WINDOW: int = 1
    BACKUP_CODES_COUNT: int = 10
    BACKUP_CODE_LENGTH: int = 8
    
    # CSRF Protection
    CSRF_TOKEN_EXPIRE_MINUTES: int = 60
    CSRF_HEADER_NAME: str = "X-CSRF-Token"
    CSRF_COOKIE_NAME: str = "csrf_token"
    
    # Security Headers
    SECURITY_HEADERS: Dict[str, str] = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    }
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://ifake.com",
        "https://www.ifake.com"
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    CORS_EXPOSE_HEADERS: List[str] = ["X-CSRF-Token"]
    
    # Database Security
    DB_SSL_MODE: str = "require"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_PRE_PING: bool = True
    
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    REDIS_SSL: bool = False
    REDIS_MAX_CONNECTIONS: int = 100
    
    # Encryption
    ENCRYPTION_KEY_FILE: str = "encryption.key"
    ENCRYPTION_ALGORITHM: str = "AES-256-GCM"
    
    # Audit Logging
    AUDIT_LOG_RETENTION_DAYS: int = 90
    AUDIT_LOG_LEVEL: str = "INFO"
    AUDIT_LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Security Monitoring
    ENABLE_SECURITY_MONITORING: bool = True
    SECURITY_ALERT_EMAIL: str = "security@ifake.com"
    SUSPICIOUS_ACTIVITY_THRESHOLD: int = 10
    
    # API Security
    API_RATE_LIMIT_ENABLED: bool = True
    API_KEY_LENGTH: int = 32
    API_KEY_PREFIX: str = "ifake_"
    API_KEY_EXPIRE_DAYS: int = 365
    
    # File Upload Security
    MAX_FILE_SIZE_MB: int = 100
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "video/mp4", "video/avi", "video/mov", "video/wmv"
    ]
    SCAN_UPLOADED_FILES: bool = True
    
    # Email Security
    EMAIL_VERIFICATION_REQUIRED: bool = True
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_EMAIL_TEMPLATE: str = "password_reset.html"
    VERIFICATION_EMAIL_TEMPLATE: str = "email_verification.html"
    
    # Development vs Production
    DEBUG: bool = False
    TESTING: bool = False
    
    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')
        return v
    
    @field_validator('JWT_SECRET_KEY')
    @classmethod
    def validate_jwt_secret_key(cls, v):
        if not v or len(v) < 16:
            raise ValueError('JWT_SECRET_KEY is required and must be at least 16 characters long')
        return v
    
    @field_validator('CORS_ORIGINS')
    @classmethod
    def validate_cors_origins(cls, v):
        if not v:
            raise ValueError('CORS_ORIGINS cannot be empty')
        return v
    
    @field_validator('MIN_PASSWORD_LENGTH')
    @classmethod
    def validate_password_length(cls, v):
        if v < 8:
            raise ValueError('MIN_PASSWORD_LENGTH must be at least 8')
        return v
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }

# Global security configuration instance
security_config = SecurityConfig()

# Security policies
class SecurityPolicies:
    """Security policies and rules"""
    
    @staticmethod
    def get_password_requirements() -> Dict[str, Any]:
        """Get password requirements"""
        return {
            "min_length": security_config.MIN_PASSWORD_LENGTH,
            "require_uppercase": security_config.REQUIRE_UPPERCASE,
            "require_lowercase": security_config.REQUIRE_LOWERCASE,
            "require_numbers": security_config.REQUIRE_NUMBERS,
            "require_special_chars": security_config.REQUIRE_SPECIAL_CHARS,
            "max_age_days": security_config.MAX_PASSWORD_AGE_DAYS,
            "history_count": security_config.PASSWORD_HISTORY_COUNT
        }
    
    @staticmethod
    def get_account_lockout_policy() -> Dict[str, Any]:
        """Get account lockout policy"""
        return {
            "max_attempts": security_config.MAX_LOGIN_ATTEMPTS,
            "lockout_duration_minutes": security_config.LOCKOUT_DURATION_MINUTES,
            "escalation_enabled": security_config.LOCKOUT_ESCALATION,
            "escalation_multiplier": security_config.ESCALATION_MULTIPLIER
        }
    
    @staticmethod
    def get_rate_limits() -> Dict[str, Any]:
        """Get rate limiting configuration"""
        return {
            "requests_per_minute": security_config.RATE_LIMIT_REQUESTS_PER_MINUTE,
            "requests_per_hour": security_config.RATE_LIMIT_REQUESTS_PER_HOUR,
            "auth_attempts_per_15min": security_config.RATE_LIMIT_AUTH_ATTEMPTS_PER_15MIN,
            "password_reset_per_hour": security_config.RATE_LIMIT_PASSWORD_RESET_PER_HOUR
        }
    
    @staticmethod
    def get_session_policy() -> Dict[str, Any]:
        """Get session management policy"""
        return {
            "timeout_minutes": security_config.SESSION_TIMEOUT_MINUTES,
            "extend_on_activity": security_config.SESSION_EXTEND_ON_ACTIVITY,
            "max_concurrent": security_config.MAX_CONCURRENT_SESSIONS,
            "cleanup_interval_minutes": security_config.SESSION_CLEANUP_INTERVAL_MINUTES
        }
    
    @staticmethod
    def get_2fa_policy() -> Dict[str, Any]:
        """Get 2FA policy"""
        return {
            "issuer": security_config.TOTP_ISSUER,
            "window": security_config.TOTP_WINDOW,
            "backup_codes_count": security_config.BACKUP_CODES_COUNT,
            "backup_code_length": security_config.BACKUP_CODE_LENGTH
        }

# Security event types
class SecurityEventTypes:
    """Security event type constants"""
    
    # Authentication events
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET_REQUESTED = "password_reset_requested"
    PASSWORD_RESET_COMPLETED = "password_reset_completed"
    
    # Account events
    USER_REGISTERED = "user_registered"
    USER_VERIFIED = "user_verified"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    ACCOUNT_SUSPENDED = "account_suspended"
    
    # 2FA events
    TWO_FACTOR_ENABLED = "two_factor_enabled"
    TWO_FACTOR_DISABLED = "two_factor_disabled"
    TWO_FACTOR_VERIFICATION_FAILED = "two_factor_verification_failed"
    BACKUP_CODE_USED = "backup_code_used"
    
    # Security events
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    CSRF_TOKEN_INVALID = "csrf_token_invalid"
    SESSION_EXPIRED = "session_expired"
    SESSION_HIJACKED = "session_hijacked"
    
    # API events
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    API_RATE_LIMIT_EXCEEDED = "api_rate_limit_exceeded"
    
    # File events
    FILE_UPLOADED = "file_uploaded"
    FILE_SCANNED = "file_scanned"
    MALICIOUS_FILE_DETECTED = "malicious_file_detected"
    
    # System events
    CONFIGURATION_CHANGED = "configuration_changed"
    SECURITY_ALERT = "security_alert"
    SYSTEM_ERROR = "system_error"

# Security severity levels
class SecuritySeverity:
    """Security severity level constants"""
    
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

# Security categories
class SecurityCategories:
    """Security event category constants"""
    
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ACCOUNT = "account"
    SESSION = "session"
    API = "api"
    FILE = "file"
    SYSTEM = "system"
    SECURITY = "security"
