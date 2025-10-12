"""
User Routes
==========
Basic user management routes
"""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import jwt

logger = logging.getLogger(__name__)

# Security scheme
security_scheme = HTTPBearer()

# Router
router = APIRouter(prefix="/users", tags=["users"])

# JWT settings
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

# Pydantic models
class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    is_active: bool
    created_at: datetime

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

# Utility functions
def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> dict:
    """Get the current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # Mock user data - in real implementation, this would come from database
        return {
            "id": user_id,
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "is_active": True,
            "created_at": datetime.utcnow()
        }
            
    except Exception:
        raise credentials_exception

# Routes
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(**current_user)

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update current user information"""
    try:
        # Mock update - in real implementation, this would update database
        updated_user = current_user.copy()
        
        if user_update.full_name is not None:
            updated_user["full_name"] = user_update.full_name
        
        if user_update.email is not None:
            updated_user["email"] = user_update.email
        
        return UserResponse(**updated_user)
        
    except Exception as e:
        logger.error(f"User update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User update failed"
        )

@router.get("/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile information"""
    return {
        "user": current_user,
        "profile": {
            "detection_count": 0,
            "last_activity": datetime.utcnow().isoformat(),
            "preferences": {
                "theme": "light",
                "notifications": True
            }
        }
    }

@router.get("/stats")
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    """Get user statistics"""
    return {
        "user_id": current_user["id"],
        "total_detections": 0,
        "successful_detections": 0,
        "failed_detections": 0,
        "account_created": current_user["created_at"].isoformat(),
        "last_login": datetime.utcnow().isoformat()
    }

@router.get("/usage")
async def get_user_usage(current_user: dict = Depends(get_current_user)):
    """Get user usage statistics"""
    return {
        "user_id": current_user["id"],
        "detections_used": 0,
        "detections_limit": 100,
        "plan": "free",
        "usage_percentage": 0.0,
        "reset_date": "2024-12-31T23:59:59Z",
        "features": {
            "real_time_detection": True,
            "file_upload": True,
            "batch_processing": False,
            "api_access": False
        }
    }

@router.get("/health")
async def users_health():
    """User service health check"""
    return {
        "status": "healthy",
        "service": "users",
        "timestamp": datetime.utcnow().isoformat()
    }
