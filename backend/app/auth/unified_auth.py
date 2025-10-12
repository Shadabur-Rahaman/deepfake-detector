"""
Unified Authentication System
Production-ready JWT-based authentication with proper password hashing and token management.

This module provides:
- JWT token generation and validation
- Secure password hashing with bcrypt
- Proper refresh token handling
- Consistent API responses
- Session management

Author: Senior Backend Engineer
"""

import os
import secrets
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

import jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt

logger = logging.getLogger(__name__)

@dataclass
class User:
    """User model for unified authentication"""
    id: str
    email: str
    username: str
    password_hash: str
    full_name: str
    is_verified: bool = True
    is_active: bool = True
    status: str = "active"
    created_at: str = ""
    last_login: Optional[str] = None
    roles: List[str] = None

    def __post_init__(self):
        if self.roles is None:
            self.roles = ["user"]

@dataclass
class AuthResult:
    """Authentication result"""
    success: bool
    user_id: Optional[str] = None
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    message: str = ""
    user: Optional[User] = None
    user_data: Optional[Dict[str, Any]] = None

@dataclass
class TokenData:
    """Token data for JWT payload"""
    user_id: str
    email: str
    username: str
    roles: List[str]
    exp: datetime
    iat: datetime
    type: str

class UnifiedAuthCore:
    """Unified authentication core with proper JWT and password hashing"""
    
    def __init__(self, data_file: str = "unified_auth.json"):
        self.data_file = Path(data_file)
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # JWT configuration
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
        self.jwt_algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        
        # Password hashing context
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            default="bcrypt",
            bcrypt__rounds=12,
            deprecated="auto"  # Handle bcrypt version compatibility
        )
        
        # Load existing data
        self._load_data()
        
        # Create default users if none exist
        if not self.users:
            self._create_default_users()
    
    def _load_data(self):
        """Load user data from file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for user_data in data.get('users', []):
                        user = User(**user_data)
                        self.users[user.id] = user
                    self.sessions = data.get('sessions', {})
                logger.info(f"Loaded {len(self.users)} users from {self.data_file}")
        except Exception as e:
            logger.warning(f"Failed to load auth data: {e}")
    
    def _save_data(self):
        """Save user data to file"""
        try:
            data = {
                'users': [asdict(user) for user in self.users.values()],
                'sessions': self.sessions
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save auth data: {e}")
    
    def _create_default_users(self):
        """Create default users for testing"""
        try:
            # Create admin user
            admin_user = User(
                id="admin-001",
                email="admin@ifake.com",
                username="admin",
                password_hash=self._hash_password("Admin123!@#"),
                full_name="System Administrator",
                is_verified=True,
                is_active=True,
                status="active",
                created_at=datetime.utcnow().isoformat(),
                roles=["admin", "user"]
            )
            self.users[admin_user.id] = admin_user
            
            # Create demo user
            demo_user = User(
                id="demo-001",
                email="demo@ifake.com",
                username="demo",
                password_hash=self._hash_password("Demo123!@#"),
                full_name="Demo User",
                is_verified=True,
                is_active=True,
                status="active",
                created_at=datetime.utcnow().isoformat(),
                roles=["user"]
            )
            self.users[demo_user.id] = demo_user
            
            # Create user for testing
            test_user = User(
                id="test-001",
                email="rahamanshadabur@gmail.com",
                username="rahamanshadabur",
                password_hash=self._hash_password("Test123!@#"),
                full_name="Rahaman Shadabur",
                is_verified=True,
                is_active=True,
                status="active",
                created_at=datetime.utcnow().isoformat(),
                roles=["user"]
            )
            self.users[test_user.id] = test_user
            
            self._save_data()
            logger.info("[OK] Default users created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create default users: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        try:
            return self.pwd_context.hash(password)
        except Exception as e:
            logger.warning(f"bcrypt hashing warning: {e}")
            # Fallback to basic bcrypt if passlib fails
            import bcrypt
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.warning(f"bcrypt verification warning: {e}")
            # Fallback to basic bcrypt if passlib fails
            import bcrypt
            try:
                return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
            except Exception:
                return False
    
    def _generate_tokens(self, user: User, remember_me: bool = False) -> Tuple[str, str]:
        """Generate access and refresh tokens"""
        try:
            now = datetime.utcnow()
            
            # Access token
            access_exp = now + timedelta(minutes=self.access_token_expire_minutes)
            access_payload = {
                "user_id": user.id,
                "email": user.email,
                "username": user.username,
                "roles": user.roles,
                "exp": access_exp,
                "iat": now,
                "type": "access"
            }
            access_token = jwt.encode(access_payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            
            # Refresh token (longer expiration)
            refresh_exp = now + timedelta(days=self.refresh_token_expire_days)
            refresh_payload = {
                "user_id": user.id,
                "exp": refresh_exp,
                "iat": now,
                "type": "refresh"
            }
            refresh_token = jwt.encode(refresh_payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            
            return access_token, refresh_token
            
        except Exception as e:
            logger.error(f"Token generation failed: {e}")
            raise ValueError("Token generation failed")
    
    def _verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise ValueError("Token verification failed")
    
    async def create_user(self, email: str, username: str, password: str, 
                         full_name: str, ip_address: str = "127.0.0.1", 
                         role_names: List[str] = None) -> AuthResult:
        """Create a new user"""
        try:
            # Check if user already exists
            for user in self.users.values():
                if user.email.lower() == email.lower() or user.username.lower() == username.lower():
                    return AuthResult(
                        success=False,
                        message="User with this email or username already exists"
                    )
            
            # Create new user
            user_id = f"user-{secrets.token_hex(8)}"
            new_user = User(
                id=user_id,
                email=email.lower(),
                username=username.lower(),
                password_hash=self._hash_password(password),
                full_name=full_name,
                is_verified=True,
                is_active=True,
                status="active",
                created_at=datetime.utcnow().isoformat(),
                roles=role_names or ["user"]
            )
            
            self.users[user_id] = new_user
            self._save_data()
            
            logger.info(f"[OK] User created: {email}")
            
            # Create user_data for compatibility
            user_data = {
                "id": new_user.id,
                "email": new_user.email,
                "username": new_user.username,
                "full_name": new_user.full_name,
                "is_verified": new_user.is_verified,
                "is_2fa_enabled": False,
                "roles": new_user.roles,
                "status": new_user.status,
                "created_at": new_user.created_at
            }
            
            return AuthResult(
                success=True,
                user_id=user_id,
                message="User created successfully",
                user=new_user,
                user_data=user_data
            )
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return AuthResult(
                success=False,
                message=f"Failed to create user: {str(e)}"
            )
    
    async def authenticate_user(self, email: str, password: str, 
                               ip_address: str = "127.0.0.1", 
                               user_agent: str = "", 
                               remember_me: bool = False) -> AuthResult:
        """Authenticate a user"""
        try:
            # Find user by email
            user = None
            for u in self.users.values():
                if u.email.lower() == email.lower():
                    user = u
                    break
            
            if not user:
                return AuthResult(
                    success=False,
                    message="Invalid email or password"
                )
            
            # Check password
            if not self._verify_password(password, user.password_hash):
                return AuthResult(
                    success=False,
                    message="Invalid email or password"
                )
            
            # Check user status
            if not user.is_active or user.status != "active":
                return AuthResult(
                    success=False,
                    message="Account is not active"
                )
            
            # Generate tokens
            access_token, refresh_token = self._generate_tokens(user, remember_me)
            
            # Store session
            self.sessions[access_token] = {
                "user_id": user.id,
                "created_at": datetime.utcnow().isoformat(),
                "ip_address": ip_address,
                "user_agent": user_agent,
                "refresh_token": refresh_token
            }
            
            # Update last login
            user.last_login = datetime.utcnow().isoformat()
            self._save_data()
            
            # Create user_data for compatibility
            user_data = {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_verified": user.is_verified,
                "is_2fa_enabled": False,
                "roles": user.roles,
                "status": user.status
            }
            
            logger.info(f"[OK] User authenticated: {email}")
            
            return AuthResult(
                success=True,
                user_id=user.id,
                token=access_token,
                refresh_token=refresh_token,
                message="Authentication successful",
                user=user,
                user_data=user_data
            )
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return AuthResult(
                success=False,
                message=f"Authentication failed: {str(e)}"
            )
    
    async def refresh_access_token(self, refresh_token: str, ip_address: str = "127.0.0.1") -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            # Verify refresh token
            payload = self._verify_token(refresh_token)
            
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type")
            
            user_id = payload.get("user_id")
            if not user_id or user_id not in self.users:
                raise ValueError("User not found")
            
            user = self.users[user_id]
            
            # Check if user is still active
            if not user.is_active or user.status != "active":
                raise ValueError("User account is not active")
            
            # Generate new tokens
            access_token, new_refresh_token = self._generate_tokens(user)
            
            # Update session
            self.sessions[access_token] = {
                "user_id": user.id,
                "created_at": datetime.utcnow().isoformat(),
                "ip_address": ip_address,
                "user_agent": "",
                "refresh_token": new_refresh_token
            }
            
            # Remove old session if exists
            old_sessions = [token for token, session in self.sessions.items() 
                          if session.get("refresh_token") == refresh_token and token != access_token]
            for old_token in old_sessions:
                del self.sessions[old_token]
            
            self._save_data()
            
            logger.info(f"[OK] Token refreshed for user: {user.email}")
            
            return {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "roles": user.roles
                }
            }
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise ValueError(f"Token refresh failed: {str(e)}")
    
    async def verify_token(self, token: str, ip_address: str = "127.0.0.1") -> Dict[str, Any]:
        """Verify a token and return user info"""
        try:
            # Verify JWT token
            payload = self._verify_token(token)
            
            if payload.get("type") != "access":
                raise ValueError("Invalid token type")
            
            user_id = payload.get("user_id")
            if not user_id or user_id not in self.users:
                raise ValueError("User not found")
            
            user = self.users[user_id]
            
            # Check if user is still active
            if not user.is_active or user.status != "active":
                raise ValueError("User account is not active")
            
            # Check if session exists
            if token not in self.sessions:
                raise ValueError("Session not found")
            
            return {
                "user_id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_verified": user.is_verified,
                "status": user.status,
                "roles": user.roles
            }
            
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise ValueError(f"Token verification failed: {str(e)}")
    
    async def logout_user(self, user_id: str, ip_address: str = "127.0.0.1") -> bool:
        """Logout a user by removing their sessions"""
        try:
            # Remove all sessions for this user
            sessions_to_remove = [
                token for token, session in self.sessions.items() 
                if session.get("user_id") == user_id
            ]
            
            for token in sessions_to_remove:
                del self.sessions[token]
            
            self._save_data()
            logger.info(f"[OK] User logged out: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        for user in self.users.values():
            if user.email.lower() == email.lower():
                return user
        return None
    
    def list_users(self) -> List[User]:
        """List all users"""
        return list(self.users.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get authentication system statistics"""
        return {
            "total_users": len(self.users),
            "active_sessions": len(self.sessions),
            "verified_users": sum(1 for u in self.users.values() if u.is_verified),
            "active_users": sum(1 for u in self.users.values() if u.is_active and u.status == "active")
        }

# Global unified auth instance
_unified_auth: Optional[UnifiedAuthCore] = None

def get_unified_auth() -> UnifiedAuthCore:
    """Get the global unified auth instance"""
    global _unified_auth
    if _unified_auth is None:
        _unified_auth = UnifiedAuthCore()
    return _unified_auth

def reset_unified_auth():
    """Reset the unified auth instance (for testing)"""
    global _unified_auth
    _unified_auth = None
