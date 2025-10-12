"""
Fallback Authentication System

This module provides a simple authentication system that doesn't depend on SQLite3
or any external database. It uses in-memory storage and is suitable for development
and testing environments.

Author: Senior Backend Engineer
Date: 2024
"""

import os
import json
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class User:
    """Simple user model for fallback authentication"""
    id: str
    email: str
    username: str
    password_hash: str
    full_name: str
    is_verified: bool = False
    status: str = "active"
    created_at: str = ""
    last_login: str = ""
    ip_address: str = ""

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

class FallbackAuthCore:
    """Fallback authentication core using in-memory storage"""
    
    def __init__(self, data_file: str = "fallback_auth.json"):
        self.data_file = Path(data_file)
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
        
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
                status="active",
                created_at=datetime.utcnow().isoformat()
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
                status="active",
                created_at=datetime.utcnow().isoformat()
            )
            self.users[demo_user.id] = demo_user
            
            self._save_data()
            logger.info("[OK] Default users created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create default users: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_token(self, user_id: str) -> str:
        """Generate a simple token"""
        token_data = f"{user_id}:{datetime.utcnow().isoformat()}:{secrets.token_urlsafe(16)}"
        return hashlib.sha256(token_data.encode()).hexdigest()
    
    async def create_user(self, email: str, username: str, password: str, 
                         full_name: str, ip_address: str = "127.0.0.1", 
                         role_names: List[str] = None) -> AuthResult:
        """Create a new user"""
        try:
            # Check if user already exists
            for user in self.users.values():
                if user.email == email or user.username == username:
                    return AuthResult(
                        success=False,
                        message="User with this email or username already exists"
                    )
            
            # Create new user
            user_id = f"user-{secrets.token_hex(8)}"
            new_user = User(
                id=user_id,
                email=email,
                username=username,
                password_hash=self._hash_password(password),
                full_name=full_name,
                is_verified=True,  # Auto-verify for fallback
                status="active",   # Set to active
                created_at=datetime.utcnow().isoformat(),
                ip_address=ip_address
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
                "roles": role_names or ["user"],
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
                if u.email == email:
                    user = u
                    break
            
            if not user:
                return AuthResult(
                    success=False,
                    message="Invalid email or password"
                )
            
            # Check password
            if user.password_hash != self._hash_password(password):
                return AuthResult(
                    success=False,
                    message="Invalid email or password"
                )
            
            # Check user status
            if user.status != "active":
                return AuthResult(
                    success=False,
                    message="Account is not active"
                )
            
            # Generate token
            token = self._generate_token(user.id)
            refresh_token = self._generate_token(f"{user.id}_refresh")
            
            # Store session
            self.sessions[token] = {
                "user_id": user.id,
                "created_at": datetime.utcnow().isoformat(),
                "ip_address": ip_address,
                "user_agent": user_agent
            }
            
            # Update last login
            user.last_login = datetime.utcnow().isoformat()
            user.ip_address = ip_address
            self._save_data()
            
            # Create user_data for compatibility
            user_data = {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_verified": user.is_verified,
                "is_2fa_enabled": False,
                "roles": ["user"],
                "status": user.status
            }
            
            logger.info(f"[OK] User authenticated: {email}")
            
            return AuthResult(
                success=True,
                user_id=user.id,
                token=token,
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
    
    async def verify_token(self, token: str, ip_address: str = "127.0.0.1") -> Dict[str, Any]:
        """Verify a token and return user info"""
        try:
            if token not in self.sessions:
                raise ValueError("Invalid token")
            
            session = self.sessions[token]
            user_id = session["user_id"]
            
            if user_id not in self.users:
                raise ValueError("User not found")
            
            user = self.users[user_id]
            
            # Check if user is still active
            if user.status != "active":
                raise ValueError("User account is not active")
            
            return {
                "user_id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_verified": user.is_verified,
                "status": user.status
            }
            
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise ValueError(f"Token verification failed: {str(e)}")
    
    async def logout(self, token: str) -> bool:
        """Logout a user by removing their session"""
        try:
            if token in self.sessions:
                del self.sessions[token]
                self._save_data()
                return True
            return False
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        for user in self.users.values():
            if user.email == email:
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
            "active_users": sum(1 for u in self.users.values() if u.status == "active")
        }

# Global fallback auth instance
_fallback_auth: Optional[FallbackAuthCore] = None

def get_fallback_auth() -> FallbackAuthCore:
    """Get the global fallback auth instance"""
    global _fallback_auth
    if _fallback_auth is None:
        _fallback_auth = FallbackAuthCore()
    return _fallback_auth

def reset_fallback_auth():
    """Reset the fallback auth instance (for testing)"""
    global _fallback_auth
    _fallback_auth = None
