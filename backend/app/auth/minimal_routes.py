"""
Minimal Authentication Routes (No Complex Dependencies)
=====================================================

This version provides basic authentication without complex dependencies
to avoid hanging issues during startup.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, field_validator
import jwt

logger = logging.getLogger(__name__)

# Security scheme
security_scheme = HTTPBearer()

# Router
router = APIRouter(prefix="/auth", tags=["authentication"])

# JWT settings
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Pydantic models
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v.lower()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: dict

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    is_active: bool
    is_verified: bool
    is_2fa_enabled: bool
    roles: List[str]
    permissions: List[str]
    created_at: datetime
    last_login: Optional[datetime] = None

# Utility functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

# Routes
@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    """Register a new user (mock implementation)"""
    try:
        # Mock user creation - in real implementation, this would save to database
        mock_user_id = "user_123"
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": mock_user_id}, expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": mock_user_id,
                "email": user_data.email,
                "username": user_data.username,
                "full_name": user_data.full_name,
                "is_active": True
            }
        )
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin):
    """Authenticate user and return access token (mock implementation)"""
    try:
        # Mock authentication - in real implementation, this would check database
        if user_credentials.email == "test@example.com" and user_credentials.password == "password123":
            mock_user_id = "user_123"
            
            # Create access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": mock_user_id}, expires_delta=access_token_expires
            )
            
            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user={
                    "id": mock_user_id,
                    "email": user_credentials.email,
                    "username": "testuser",
                    "full_name": "Test User",
                    "is_active": True,
                    "is_verified": True,
                    "is_2fa_enabled": False,
                    "roles": ["user"],
                    "permissions": ["detection:create", "detection:read", "try:access"],
                    "created_at": datetime.utcnow().isoformat(),
                    "last_login": datetime.utcnow().isoformat()
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info():
    """Get current user information (mock implementation)"""
    return UserResponse(
        id="user_123",
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        is_active=True,
        is_verified=True,
        is_2fa_enabled=False,
        roles=["user"],
        permissions=["detection:create", "detection:read", "try:access"],
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    )

@router.post("/logout")
async def logout():
    """Logout user (simple implementation)"""
    return {"message": "Successfully logged out"}

@router.get("/health")
async def auth_health():
    """Authentication service health check"""
    return {
        "status": "healthy",
        "service": "authentication",
        "timestamp": datetime.utcnow().isoformat()
    }
