"""
Deepfake Detection Authentication Integration
Specialized authentication and authorization for deepfake detection endpoints.

This module provides:
- Detection-specific permissions
- Resource-based access control
- Usage tracking and limits
- Detection history management
- API rate limiting for detection endpoints

Author: Senior Backend Engineer
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import redis.asyncio as redis

from .models import User, AuditLog, APIKey
from .core import AuthCore
from .rbac import RBACManager
from .config import SecurityConfig, SecurityEventTypes

logger = logging.getLogger(__name__)

class DetectionPermission(Enum):
    """Detection-specific permissions"""
    CREATE_DETECTION = "detection:create"
    READ_DETECTION = "detection:read"
    UPDATE_DETECTION = "detection:update"
    DELETE_DETECTION = "detection:delete"
    BATCH_DETECTION = "detection:batch"
    REAL_TIME_DETECTION = "detection:realtime"
    DOWNLOAD_RESULTS = "detection:download"
    SHARE_RESULTS = "detection:share"
    EXPORT_RESULTS = "detection:export"
    VIEW_ANALYTICS = "detection:analytics"

class DetectionResource(Enum):
    """Detection resource types"""
    VIDEO = "video"
    IMAGE = "image"
    STREAM = "stream"
    BATCH = "batch"
    RESULT = "result"
    MODEL = "model"

@dataclass
class DetectionUsage:
    """Detection usage tracking"""
    user_id: str
    detection_type: str
    file_size: int
    processing_time: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None

class DetectionAuthManager:
    """Authentication manager for deepfake detection operations"""
    
    def __init__(self, auth_core: AuthCore, db_session: Session, redis_client: redis.Redis):
        self.auth_core = auth_core
        self.db = db_session
        self.redis = redis_client
        self.config = SecurityConfig()
        self.rbac_manager = RBACManager(db_session)
        
        # Usage tracking
        self.usage_limits = {
            'free_user': {
                'daily_detections': 10,
                'max_file_size_mb': 50,
                'max_batch_size': 5,
                'retention_days': 7
            },
            'premium_user': {
                'daily_detections': 100,
                'max_file_size_mb': 500,
                'max_batch_size': 50,
                'retention_days': 30
            },
            'enterprise_user': {
                'daily_detections': 1000,
                'max_file_size_mb': 2000,
                'max_batch_size': 200,
                'retention_days': 90
            }
        }
    
    async def authorize_detection_request(
        self,
        user_id: str,
        detection_type: str,
        file_size: int,
        resource_type: str,
        ip_address: str
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Authorize a detection request.
        
        Args:
            user_id: User ID
            detection_type: Type of detection (video, image, batch, etc.)
            file_size: Size of file in bytes
            resource_type: Type of resource being processed
            ip_address: Client IP address
            
        Returns:
            Tuple of (authorized, reason, usage_info)
        """
        try:
            # Check basic authentication
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                return False, "User not authenticated or inactive", {}
            
            # Check if user is locked
            if await self.auth_core._is_account_locked(user_id):
                return False, "Account is locked", {}
            
            # Check detection-specific permissions
            permission = f"detection:{detection_type}"
            has_permission = await self.rbac_manager.check_permission(
                user_id, permission, resource_type
            )
            
            if not has_permission:
                await self._log_detection_event(
                    "detection_denied_permission",
                    user_id,
                    ip_address,
                    {
                        'detection_type': detection_type,
                        'resource_type': resource_type,
                        'reason': 'insufficient_permission'
                    }
                )
                return False, "Insufficient permissions for this detection type", {}
            
            # Check usage limits
            usage_info = await self._check_usage_limits(user_id, detection_type, file_size)
            if not usage_info['within_limits']:
                await self._log_detection_event(
                    "detection_denied_limit",
                    user_id,
                    ip_address,
                    {
                        'detection_type': detection_type,
                        'file_size': file_size,
                        'reason': 'usage_limit_exceeded',
                        'limits': usage_info['limits']
                    }
                )
                return False, f"Usage limit exceeded: {usage_info['reason']}", usage_info
            
            # Check rate limiting
            rate_limited = await self._check_rate_limits(user_id, ip_address, detection_type)
            if rate_limited:
                await self._log_detection_event(
                    "detection_denied_rate_limit",
                    user_id,
                    ip_address,
                    {
                        'detection_type': detection_type,
                        'reason': 'rate_limit_exceeded'
                    }
                )
                return False, "Rate limit exceeded for detection requests", {}
            
            # Check file size limits
            if not await self._check_file_size_limits(user_id, file_size):
                await self._log_detection_event(
                    "detection_denied_file_size",
                    user_id,
                    ip_address,
                    {
                        'detection_type': detection_type,
                        'file_size': file_size,
                        'reason': 'file_size_exceeded'
                    }
                )
                return False, "File size exceeds allowed limit", {}
            
            # Log successful authorization
            await self._log_detection_event(
                "detection_authorized",
                user_id,
                ip_address,
                {
                    'detection_type': detection_type,
                    'resource_type': resource_type,
                    'file_size': file_size
                }
            )
            
            return True, "Authorized", usage_info
            
        except Exception as e:
            logger.error(f"Detection authorization failed: {str(e)}")
            return False, "Authorization check failed", {}
    
    async def track_detection_usage(
        self,
        user_id: str,
        detection_type: str,
        file_size: int,
        processing_time: float,
        success: bool,
        error_message: Optional[str] = None
    ) -> None:
        """Track detection usage for billing and analytics"""
        try:
            usage = DetectionUsage(
                user_id=user_id,
                detection_type=detection_type,
                file_size=file_size,
                processing_time=processing_time,
                timestamp=datetime.utcnow(),
                success=success,
                error_message=error_message
            )
            
            # Store in Redis for real-time tracking
            usage_key = f"detection_usage:{user_id}:{datetime.utcnow().strftime('%Y-%m-%d')}"
            await self.redis.lpush(usage_key, str(usage.__dict__))
            await self.redis.expire(usage_key, 86400 * 7)  # Keep for 7 days
            
            # Update daily usage counter
            daily_key = f"daily_usage:{user_id}:{datetime.utcnow().strftime('%Y-%m-%d')}"
            await self.redis.incr(daily_key)
            await self.redis.expire(daily_key, 86400 * 7)
            
            # Log usage event
            await self._log_detection_event(
                "detection_usage_tracked",
                user_id,
                None,
                {
                    'detection_type': detection_type,
                    'file_size': file_size,
                    'processing_time': processing_time,
                    'success': success,
                    'error_message': error_message
                }
            )
            
        except Exception as e:
            logger.error(f"Usage tracking failed: {str(e)}")
    
    async def get_user_detection_limits(self, user_id: str) -> Dict[str, Any]:
        """Get user's detection limits based on their subscription"""
        try:
            # Get user roles to determine subscription level
            user_roles = await self.rbac_manager.get_user_roles(user_id)
            role_names = [role['name'] for role in user_roles]
            
            # Determine subscription level
            if 'enterprise' in role_names:
                subscription_level = 'enterprise_user'
            elif 'premium' in role_names:
                subscription_level = 'premium_user'
            else:
                subscription_level = 'free_user'
            
            limits = self.usage_limits[subscription_level].copy()
            
            # Get current usage
            today = datetime.utcnow().strftime('%Y-%m-%d')
            daily_usage = await self.redis.get(f"daily_usage:{user_id}:{today}")
            limits['current_daily_usage'] = int(daily_usage) if daily_usage else 0
            
            limits['subscription_level'] = subscription_level
            limits['remaining_detections'] = limits['daily_detections'] - limits['current_daily_usage']
            
            return limits
            
        except Exception as e:
            logger.error(f"Failed to get user limits: {str(e)}")
            return self.usage_limits['free_user']
    
    async def _check_usage_limits(
        self, 
        user_id: str, 
        detection_type: str, 
        file_size: int
    ) -> Dict[str, Any]:
        """Check if user is within usage limits"""
        try:
            limits = await self.get_user_detection_limits(user_id)
            
            # Check daily detection limit
            if limits['current_daily_usage'] >= limits['daily_detections']:
                return {
                    'within_limits': False,
                    'reason': 'Daily detection limit exceeded',
                    'limits': limits
                }
            
            # Check file size limit
            max_file_size = limits['max_file_size_mb'] * 1024 * 1024  # Convert to bytes
            if file_size > max_file_size:
                return {
                    'within_limits': False,
                    'reason': 'File size exceeds limit',
                    'limits': limits
                }
            
            # Check batch size limit (if applicable)
            if detection_type == 'batch':
                # This would need to be passed as a parameter
                # For now, we'll assume it's within limits
                pass
            
            return {
                'within_limits': True,
                'limits': limits
            }
            
        except Exception as e:
            logger.error(f"Usage limit check failed: {str(e)}")
            return {
                'within_limits': False,
                'reason': 'Error checking limits',
                'limits': {}
            }
    
    async def _check_rate_limits(
        self, 
        user_id: str, 
        ip_address: str, 
        detection_type: str
    ) -> bool:
        """Check rate limits for detection requests"""
        try:
            # Check user-specific rate limit
            user_key = f"detection_rate:{user_id}:{detection_type}"
            user_count = await self.redis.incr(user_key)
            if user_count == 1:
                await self.redis.expire(user_key, 3600)  # 1 hour
            
            # Different rate limits for different detection types
            rate_limits = {
                'video': 10,  # 10 per hour
                'image': 50,  # 50 per hour
                'batch': 5,   # 5 per hour
                'realtime': 20  # 20 per hour
            }
            
            if user_count > rate_limits.get(detection_type, 10):
                return True
            
            # Check IP-based rate limit
            ip_key = f"detection_rate_ip:{ip_address}"
            ip_count = await self.redis.incr(ip_key)
            if ip_count == 1:
                await self.redis.expire(ip_key, 3600)
            
            if ip_count > 100:  # 100 requests per hour per IP
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {str(e)}")
            return False
    
    async def _check_file_size_limits(self, user_id: str, file_size: int) -> bool:
        """Check if file size is within limits"""
        try:
            limits = await self.get_user_detection_limits(user_id)
            max_size = limits['max_file_size_mb'] * 1024 * 1024
            return file_size <= max_size
        except Exception as e:
            logger.error(f"File size check failed: {str(e)}")
            return False
    
    async def _log_detection_event(
        self,
        event_type: str,
        user_id: str,
        ip_address: Optional[str],
        details: Dict[str, Any]
    ) -> None:
        """Log detection-related security event"""
        try:
            audit_log = AuditLog(
                user_id=user_id,
                event_type=event_type,
                event_category='detection',
                ip_address=ip_address,
                details=details,
                severity='info'
            )
            self.db.add(audit_log)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log detection event: {str(e)}")

class DetectionAPIKeyManager:
    """API key management for detection endpoints"""
    
    def __init__(self, db_session: Session, redis_client: redis.Redis):
        self.db = db_session
        self.redis = redis_client
        self.config = SecurityConfig()
    
    async def create_detection_api_key(
        self,
        user_id: str,
        name: str,
        permissions: List[str],
        rate_limit: int = 1000,
        expires_days: int = 365
    ) -> Dict[str, Any]:
        """Create API key for detection endpoints"""
        try:
            # Generate API key
            api_key = f"{self.config.API_KEY_PREFIX}{secrets.token_urlsafe(self.config.API_KEY_LENGTH)}"
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            # Create API key record
            api_key_record = APIKey(
                user_id=user_id,
                name=name,
                key_hash=key_hash,
                permissions=permissions,
                rate_limit=rate_limit,
                expires_at=datetime.utcnow() + timedelta(days=expires_days)
            )
            
            self.db.add(api_key_record)
            self.db.commit()
            
            # Log API key creation
            audit_log = AuditLog(
                user_id=user_id,
                event_type=SecurityEventTypes.API_KEY_CREATED,
                event_category='api',
                details={
                    'key_name': name,
                    'permissions': permissions,
                    'rate_limit': rate_limit,
                    'expires_days': expires_days
                },
                severity='info'
            )
            self.db.add(audit_log)
            self.db.commit()
            
            return {
                'api_key': api_key,
                'key_id': str(api_key_record.id),
                'name': name,
                'permissions': permissions,
                'rate_limit': rate_limit,
                'expires_at': api_key_record.expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"API key creation failed: {str(e)}")
            raise
    
    async def validate_detection_api_key(
        self,
        api_key: str,
        required_permission: str
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Validate API key for detection operations"""
        try:
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            # Get API key from database
            api_key_record = self.db.query(APIKey).filter(
                and_(
                    APIKey.key_hash == key_hash,
                    APIKey.is_active == True,
                    or_(
                        APIKey.expires_at.is_(None),
                        APIKey.expires_at > datetime.utcnow()
                    )
                )
            ).first()
            
            if not api_key_record:
                return False, None
            
            # Check permission
            if required_permission not in (api_key_record.permissions or []):
                return False, None
            
            # Check rate limit
            rate_key = f"api_rate:{api_key_record.id}"
            current_count = await self.redis.incr(rate_key)
            if current_count == 1:
                await self.redis.expire(rate_key, 3600)  # 1 hour
            
            if current_count > api_key_record.rate_limit:
                return False, None
            
            # Update usage
            api_key_record.usage_count += 1
            api_key_record.last_used = datetime.utcnow()
            self.db.commit()
            
            return True, {
                'user_id': api_key_record.user_id,
                'permissions': api_key_record.permissions,
                'rate_limit': api_key_record.rate_limit,
                'usage_count': api_key_record.usage_count
            }
            
        except Exception as e:
            logger.error(f"API key validation failed: {str(e)}")
            return False, None

# Global instances
detection_auth_manager = None
detection_api_key_manager = None

async def initialize_detection_auth(auth_core: AuthCore, db_session: Session, redis_client: redis.Redis):
    """Initialize detection authentication systems"""
    global detection_auth_manager, detection_api_key_manager
    
    detection_auth_manager = DetectionAuthManager(auth_core, db_session, redis_client)
    detection_api_key_manager = DetectionAPIKeyManager(db_session, redis_client)
