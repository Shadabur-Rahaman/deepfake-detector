#!/usr/bin/env python3
"""
Alternative Authentication System
In-memory authentication when SQLite3 fails.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib
import secrets

logger = logging.getLogger(__name__)

class InMemoryAuth:
    """In-memory authentication system"""
    
    def __init__(self):
        self.users = {}
        self.sessions = {}
        self.secret_key = os.getenv('JWT_SECRET_KEY', secrets.token_urlsafe(32))
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        
        # Create default users
        self._create_default_users()
    
    def _create_default_users(self):
        """Create default users"""
        # Admin user
        admin_password = hashlib.sha256("Admin123!@#".encode()).hexdigest()
        self.users["admin@ifake.com"] = {
            "id": "admin_001",
            "email": "admin@ifake.com",
            "username": "admin",
            "password": admin_password,
            "full_name": "System Administrator",
            "created_at": datetime.utcnow(),
            "is_active": True,
            "is_verified": True,
            "role": "admin"
        }
        
        # Demo user
        demo_password = hashlib.sha256("Demo123!@#".encode()).hexdigest()
        self.users["demo@ifake.com"] = {
            "id": "demo_001",
            "email": "demo@ifake.com",
            "username": "demo",
            "password": demo_password,
            "full_name": "Demo User",
            "created_at": datetime.utcnow(),
            "is_active": True,
            "is_verified": True,
            "role": "user"
        }
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password"""
        return self.hash_password(password) == hashed
    
    def create_user(self, email: str, password: str, full_name: str = None, username: str = None) -> Dict[str, Any]:
        """Create a new user"""
        if email in self.users:
            return {"success": False, "message": "User already exists"}
        
        user_id = secrets.token_urlsafe(16)
        self.users[email] = {
            "id": user_id,
            "email": email,
            "username": username or email.split('@')[0],
            "password": self.hash_password(password),
            "full_name": full_name or email.split('@')[0],
            "created_at": datetime.utcnow(),
            "is_active": True,
            "is_verified": False,
            "role": "user"
        }
        
        return {"success": True, "user_id": user_id, "message": "User created successfully"}
    
    def authenticate_user(self, email: str, password: str, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Authenticate user"""
        if email not in self.users:
            return {"success": False, "message": "Invalid credentials"}
        
        user = self.users[email]
        if not self.verify_password(password, user["password"]):
            return {"success": False, "message": "Invalid credentials"}
        
        if not user["is_active"]:
            return {"success": False, "message": "Account is disabled"}
        
        # Create session
        session_token = secrets.token_urlsafe(32)
        self.sessions[session_token] = {
            "user_id": user["id"],
            "email": email,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=24),
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        return {
            "success": True,
            "user_id": user["id"],
            "token": session_token,
            "user_data": {
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "full_name": user["full_name"],
                "is_active": user["is_active"],
                "is_verified": user["is_verified"],
                "role": user["role"]
            },
            "message": "Login successful"
        }
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify session token"""
        if token not in self.sessions:
            return None
        
        session = self.sessions[token]
        if datetime.utcnow() > session["expires_at"]:
            del self.sessions[token]
            return None
        
        return session
    
    def logout(self, token: str) -> bool:
        """Logout user"""
        if token in self.sessions:
            del self.sessions[token]
            return True
        return False
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        for user in self.users.values():
            if user["id"] == user_id:
                return user
        return None

# Global instance
auth_system = InMemoryAuth()

def get_auth_system():
    """Get the authentication system"""
    return auth_system

def test_auth_system():
    """Test the authentication system"""
    try:
        # Test admin login
        result = auth_system.authenticate_user("admin@ifake.com", "Admin123!@#")
        if result["success"]:
            logger.info("SUCCESS: Admin authentication works")
        else:
            logger.error(f"ERROR: Admin authentication failed: {result['message']}")
            return False
        
        # Test demo login
        result = auth_system.authenticate_user("demo@ifake.com", "Demo123!@#")
        if result["success"]:
            logger.info("SUCCESS: Demo authentication works")
        else:
            logger.error(f"ERROR: Demo authentication failed: {result['message']}")
            return False
        
        logger.info("SUCCESS: Authentication system test passed")
        return True
        
    except Exception as e:
        logger.error(f"ERROR: Authentication system test failed: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = test_auth_system()
    if success:
        print("SUCCESS: Alternative authentication system is working")
    else:
        print("ERROR: Alternative authentication system failed")
    sys.exit(0 if success else 1)
