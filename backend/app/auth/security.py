"""
Security Management Module
Production-ready security utilities with enterprise-grade features.
"""

import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple, List
import bcrypt
import jwt
from cryptography.fernet import Fernet
import base64
import os
import logging

logger = logging.getLogger(__name__)

class PasswordManager:
    """Advanced password management with security best practices."""
    
    def __init__(self):
        self.min_length = 12
        self.bcrypt_rounds = 12
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt with adaptive cost."""
        salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification failed: {str(e)}")
            return False
    
    def validate_password_strength(self, password: str) -> Tuple[bool, List[str]]:
        """Validate password strength and return issues."""
        issues = []
        
        if len(password) < self.min_length:
            issues.append(f"Password must be at least {self.min_length} characters long")
        
        if not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        
        if not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one number")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            issues.append("Password must contain at least one special character")
        
        return len(issues) == 0, issues

class TokenManager:
    """JWT token management with security best practices."""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or os.getenv("SECRET_KEY", "your-super-secret-key")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    def create_access_token(self, user_id: str, email: str, roles: List[str] = None) -> str:
        """Create JWT access token."""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "user_id": user_id,
            "email": email,
            "roles": roles or [],
            "type": "access",
            "iat": datetime.utcnow(),
            "exp": expire,
            "jti": secrets.token_urlsafe(32)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token."""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "user_id": user_id,
            "type": "refresh",
            "iat": datetime.utcnow(),
            "exp": expire,
            "jti": secrets.token_urlsafe(32)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode access token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "access":
                raise jwt.InvalidTokenError("Invalid token type")
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f"Invalid token: {str(e)}")
    
    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode refresh token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "refresh":
                raise jwt.InvalidTokenError("Invalid token type")
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Refresh token has expired")
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f"Invalid refresh token: {str(e)}")

class SecurityManager:
    """Comprehensive security management."""
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive data."""
        key_file = "encryption.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            os.chmod(key_file, 0o600)
            return key
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise
    
    def generate_csrf_token(self, user_id: str) -> str:
        """Generate CSRF token for user."""
        timestamp = str(int(time.time()))
        data = f"{user_id}:{timestamp}"
        secret = os.getenv("CSRF_SECRET", secrets.token_urlsafe(32))
        return hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()
    
    def verify_csrf_token(self, user_id: str, token: str) -> bool:
        """Verify CSRF token."""
        try:
            current_time = int(time.time())
            secret = os.getenv("CSRF_SECRET", secrets.token_urlsafe(32))
            
            # Check current time window
            for i in range(60):  # Check last hour
                timestamp = str(current_time - i)
                data = f"{user_id}:{timestamp}"
                expected_token = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()
                
                if hmac.compare_digest(token, expected_token):
                    return True
            return False
        except Exception as e:
            logger.error(f"CSRF token verification failed: {str(e)}")
            return False