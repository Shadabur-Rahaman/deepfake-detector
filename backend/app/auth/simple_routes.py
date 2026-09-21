"""
Simple Authentication Routes (No Redis Required)
===============================================

This version provides basic authentication without Redis dependencies
to avoid hanging issues during startup.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator
import jwt
from passlib.context import CryptContext

from ..database import get_db
from .models import User

logger = logging.getLogger(__name__)

# Security scheme
security_scheme = HTTPBearer()

# Router
router = APIRouter(prefix="/auth", tags=["authentication"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-to-a-long-random-string")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

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
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

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

# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
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
            
    except Exception:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user

# Routes
@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(new_user.id)}, expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user={
                "id": str(new_user.id),
                "email": new_user.email,
                "username": new_user.username,
                "full_name": new_user.full_name,
                "is_active": new_user.is_active
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token"""
    try:
        logger.info(f"🔐 Login attempt for email: {user_credentials.email}")
        
        # Find user by email
        user = db.query(User).filter(User.email == user_credentials.email).first()
        
        if user:
            logger.info(f"👤 User found: {user.username} (ID: {user.id})")
            logger.info(f"🔑 User roles: {[role.name for role in user.roles] if user.roles else 'None'}")
            logger.info(f"🛡️ User permissions: {user.permissions if hasattr(user, 'permissions') else 'None'}")
        else:
            logger.warning(f"❌ User not found for email: {user_credentials.email}")
            
            # If admin user doesn't exist, create it
            if user_credentials.email == "admin@ifake.com":
                logger.info("🔧 Creating admin user...")
                from passlib.context import CryptContext
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                
                import uuid
                user = User(
                    id=str(uuid.uuid4()),  # Explicitly set the ID
                    email="admin@ifake.com",
                    username="admin",
                    full_name="System Administrator",
                    hashed_password=pwd_context.hash("Admin123!@#"),
                    is_active=True,
                    is_verified=True,
                    is_2fa_enabled=False,
                    status="active"
                )
                db.add(user)
                db.commit()
                logger.info(f"✅ Admin user created successfully with ID: {user.id}")
        
        if not user or not verify_password(user_credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not user.is_active:
            logger.warning(f"❌ Account deactivated for user: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        logger.info(f"✅ Password verified for user: {user.username}")
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        logger.info(f"🎫 Access token created for user: {user.username}")
        
        # Get user roles
        user_roles_list = [role.name for role in user.roles] if user.roles else ["user"]
        
        # Special case: if user is admin@ifake.com, ensure they have admin role
        if user.email == "admin@ifake.com" and "admin" not in user_roles_list:
            user_roles_list = ["admin", "user"]
            logger.info(f"🔑 Admin user detected by email, adding admin role: {user_roles_list}")
        
        # Get user permissions
        user_permissions_list = user.permissions if hasattr(user, 'permissions') else []
        
        # If user is admin, ensure they have all permissions
        if "admin" in user_roles_list:
            user_permissions_list = [
                "detection:create", "detection:read", "detection:update", "detection:delete",
                "try:access", "admin:access", "user:manage", "system:manage"
            ]
            logger.info(f"🔑 Admin user detected, granting all permissions: {user_permissions_list}")
        
        user_response = {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "is_2fa_enabled": user.is_2fa_enabled,
            "roles": user_roles_list,
            "permissions": user_permissions_list,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
        
        logger.info(f"📤 Returning user data: roles={user_response['roles']}, permissions={user_response['permissions']}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
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
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        is_2fa_enabled=current_user.is_2fa_enabled,
        roles=[role.name for role in current_user.roles] if current_user.roles else ["user"],
        permissions=current_user.permissions if hasattr(current_user, 'permissions') else [],
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
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
