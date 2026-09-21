"""
Authentication Core Module
Production-ready authentication system with comprehensive security features.

This module provides:
- User authentication and authorization
- Password hashing and validation
- JWT token management
- Session management
- Security monitoring
- Rate limiting

Author: Senior Backend Engineer
"""

import asyncio
import logging
import secrets
import hashlib
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

import jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt, argon2
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from .models import User, UserSession, AuditLog, PasswordReset, Role
from .exceptions import AuthenticationError, AuthorizationError

logger = logging.getLogger(__name__)

@dataclass
class AuthResult:
    """Authentication result container"""
    success: bool
    user_id: Optional[str] = None
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    message: Optional[str] = None
    user_data: Optional[Dict[str, Any]] = None

class AuthCore:
    """Core authentication system with enterprise-grade security"""
    
    def __init__(self, db_session: Session, redis_client: Optional[redis.Redis] = None):
        self.db_session = db_session
        self.redis_client = redis_client
        
        # Security configuration
        self.secret_key = self._get_secret_key()
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        self.max_login_attempts = 5
        self.lockout_duration_minutes = 15
        
        # Password hashing context
        self.pwd_context = CryptContext(
            schemes=["argon2", "bcrypt"],
            default="argon2",
            argon2__memory_cost=65536,
            argon2__time_cost=3,
            argon2__parallelism=4,
            argon2__hash_len=32,
            bcrypt__rounds=12
        )
        
        # Rate limiting
        self.rate_limits = {
            "login": {"requests": 5, "window": 300},  # 5 requests per 5 minutes
            "register": {"requests": 3, "window": 3600},  # 3 requests per hour
            "password_reset": {"requests": 3, "window": 3600}  # 3 requests per hour
        }
    
    def _get_secret_key(self) -> str:
        """Get or generate secret key for JWT signing"""
        secret_key = os.getenv('JWT_SECRET_KEY')
        if not secret_key:
            # Generate a secure random key
            secret_key = secrets.token_urlsafe(32)
            logger.warning("JWT_SECRET_KEY not set, using generated key (not suitable for production)")
        return secret_key
    
    def _hash_password(self, password: str) -> str:
        """Hash password using the configured context"""
        try:
            return self.pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Password hashing failed: {str(e)}")
            raise AuthenticationError("Password hashing failed")
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification failed: {str(e)}")
            return False
    
    def _generate_tokens(self, user_id: str, user_data: Dict[str, Any], access_token_expire_minutes: int = None, refresh_token_expire_days: int = None) -> Tuple[str, str]:
        """Generate access and refresh tokens"""
        try:
            # Use provided values or defaults
            if access_token_expire_minutes is None:
                access_token_expire_minutes = self.access_token_expire_minutes
            if refresh_token_expire_days is None:
                refresh_token_expire_days = self.refresh_token_expire_days
            
            # Access token
            access_payload = {
                "user_id": user_id,
                "email": user_data.get("email"),
                "username": user_data.get("username"),
                "roles": user_data.get("roles", []),
                "exp": datetime.utcnow() + timedelta(minutes=access_token_expire_minutes),
                "iat": datetime.utcnow(),
                "type": "access"
            }
            access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
            
            # Refresh token
            refresh_payload = {
                "user_id": user_id,
                "exp": datetime.utcnow() + timedelta(days=refresh_token_expire_days),
                "iat": datetime.utcnow(),
                "type": "refresh"
            }
            refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
            
            return access_token, refresh_token
            
        except Exception as e:
            logger.error(f"Token generation failed: {str(e)}")
            raise AuthenticationError("Token generation failed")
    
    def _verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise AuthenticationError("Token verification failed")
    
    async def _check_rate_limit(self, identifier: str, action: str, ip_address: str) -> bool:
        """Check if request is within rate limits"""
        try:
            if not self.redis_client:
                return True  # No rate limiting without Redis
            
            rate_limit = self.rate_limits.get(action)
            if not rate_limit:
                return True
            
            key = f"rate_limit:{action}:{identifier}:{ip_address}"
            current_requests = await self.redis_client.get(key)
            
            if current_requests is None:
                await self.redis_client.setex(key, rate_limit["window"], 1)
                return True
            
            if int(current_requests) >= rate_limit["requests"]:
                return False
            
            await self.redis_client.incr(key)
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {str(e)}")
            return True  # Allow on error
    
    async def _log_security_event(
        self, 
        event_type: str, 
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "info"
    ) -> None:
        """Log security event to database and Redis"""
        try:
            # Log to database
            audit_log = AuditLog(
                user_id=user_id,
                event_type=event_type,
                event_category="authentication",
                ip_address=ip_address,
                details=details or {},
                severity=severity
            )
            self.db_session.add(audit_log)
            self.db_session.commit()
            
            # Log to Redis for real-time monitoring
            if self.redis_client:
                await self.redis_client.lpush(
                    "security_events",
                    f"{datetime.utcnow().isoformat()}:{event_type}:{user_id or 'anonymous'}:{severity}"
                )
                await self.redis_client.ltrim("security_events", 0, 999)  # Keep last 1000 events
            
        except Exception as e:
            logger.error(f"Security event logging failed: {str(e)}")
    
    async def authenticate_user(
        self,
        email: str,
        password: str,
        ip_address: str,
        user_agent: str = None,
        remember_me: bool = False
    ) -> AuthResult:
        """Authenticate user with comprehensive security checks"""
        try:
            # Check rate limits
            if not await self._check_rate_limit(email, "login", ip_address):
                await self._log_security_event(
                    "login_rate_limited",
                    ip_address=ip_address,
                    details={"email": email},
                    severity="warning"
                )
                return AuthResult(
                    success=False,
                    message="Too many login attempts. Please try again later."
                )
            
            # Find user
            user = self.db_session.query(User).filter(User.email == email.lower()).first()
            if not user:
                await self._log_security_event(
                    "login_user_not_found",
                    ip_address=ip_address,
                    details={"email": email},
                    severity="warning"
                )
                return AuthResult(success=False, message="Invalid credentials")
            
            # Check if account is locked
            if user.locked_until and user.locked_until > datetime.utcnow():
                await self._log_security_event(
                    "login_account_locked",
                    user_id=user.id,
                    ip_address=ip_address,
                    details={"locked_until": user.locked_until.isoformat()},
                    severity="warning"
                )
                return AuthResult(
                    success=False,
                    message="Account is temporarily locked due to too many failed attempts"
                )
            
            # Check if account is active
            if not user.is_active or user.status != "active":
                await self._log_security_event(
                    "login_inactive_account",
                    user_id=user.id,
                    ip_address=ip_address,
                    details={"status": user.status, "is_active": user.is_active},
                    severity="warning"
                )
                return AuthResult(success=False, message="Account is not active")
            
            # Verify password
            if not self._verify_password(password, user.hashed_password):
                # Increment failed login attempts
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= self.max_login_attempts:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=self.lockout_duration_minutes)
                
                self.db_session.commit()
                
                await self._log_security_event(
                    "login_failed",
                    user_id=user.id,
                    ip_address=ip_address,
                    details={"failed_attempts": user.failed_login_attempts},
                    severity="warning"
                )
                return AuthResult(success=False, message="Invalid credentials")
            
            # Reset failed login attempts
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.utcnow()
            user.last_login_ip = ip_address
            user.last_login_user_agent = user_agent
            
            self.db_session.commit()
            
            # Generate tokens
            user_data = {
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "roles": [role.name for role in user.roles] if user.roles else ["user"]
            }
            
            # Adjust token expiration based on remember_me
            if remember_me:
                access_token_expire_minutes = self.access_token_expire_minutes * 24  # 24x longer for remember me
                refresh_token_expire_days = 30  # 30 days for remember me
            else:
                access_token_expire_minutes = self.access_token_expire_minutes
                refresh_token_expire_days = 7  # 7 days default
            
            access_token, refresh_token = self._generate_tokens(user.id, user_data, access_token_expire_minutes, refresh_token_expire_days)
            
            # Create session
            session = UserSession(
                user_id=user.id,
                session_token=access_token,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=datetime.utcnow() + timedelta(minutes=access_token_expire_minutes)
            )
            self.db_session.add(session)
            self.db_session.commit()
            
            # Log successful login
            await self._log_security_event(
                "user_logged_in",
                user_id=user.id,
                ip_address=ip_address,
                details={"user_agent": user_agent},
                severity="info"
            )
            
            return AuthResult(
                success=True,
                user_id=user.id,
                token=access_token,
                refresh_token=refresh_token,
                user_data=user_data,
                message="Login successful"
            )
            
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Database error during authentication: {str(e)}")
            return AuthResult(success=False, message="Authentication failed due to database error")
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return AuthResult(success=False, message="Authentication failed")
    
    async def verify_token(self, token: str, ip_address: str) -> Dict[str, Any]:
        """Verify JWT token and return user information"""
        try:
            payload = self._verify_token(token)
            
            if payload.get("type") != "access":
                raise AuthenticationError("Invalid token type")
            
            # Check if session exists and is active
            session = self.db_session.query(UserSession).filter(
                UserSession.session_token == token,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            ).first()
            
            if not session:
                raise AuthenticationError("Session not found or expired")
            
            # Update last activity
            session.last_activity = datetime.utcnow()
            self.db_session.commit()
            
            return payload
            
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise AuthenticationError("Token verification failed")
    
    async def create_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: str,
        ip_address: str,
        role_names: List[str] = None
    ) -> AuthResult:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = self.db_session.query(User).filter(
                (User.email == email.lower()) | (User.username == username.lower())
            ).first()
            
            if existing_user:
                return AuthResult(success=False, message="User already exists")
            
            # Create user
            hashed_password = self._hash_password(password)
            user = User(
                email=email.lower(),
                username=username.lower(),
                full_name=full_name,
                hashed_password=hashed_password,
                created_ip=ip_address,
                status="active"
            )
            
            self.db_session.add(user)
            self.db_session.flush()  # Flush to get the user ID
            
            # Assign default role if no roles specified
            if not role_names:
                role_names = ["user"]
            
            # Find and assign roles
            for role_name in role_names:
                role = self.db_session.query(Role).filter(Role.name == role_name).first()
                if role:
                    user.roles.append(role)
            
            self.db_session.commit()
            
            # Log successful creation
            await self._log_security_event(
                "user_created",
                user_id=user.id,
                ip_address=ip_address,
                details={"email": email, "username": username},
                severity="info"
            )
            
            return AuthResult(
                success=True,
                user_id=user.id,
                message="User created successfully",
                user_data={
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "is_verified": user.is_verified,
                    "is_2fa_enabled": user.is_2fa_enabled,
                    "roles": role_names or ["user"],
                    "status": user.status,
                    "created_at": user.created_at
                }
            )
            
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Database error during user creation: {str(e)}")
            return AuthResult(success=False, message="User creation failed due to database error")
        except Exception as e:
            logger.error(f"User creation failed: {str(e)}")
            return AuthResult(success=False, message="User creation failed")