"""
Production-Grade Notification Models
Enhanced notification system with comprehensive data models and validation
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum
import uuid

Base = declarative_base()

class NotificationType(str, Enum):
    """Notification types for different user actions"""
    TRY_ACCESS_REQUEST = "try_access_request"
    DETECTION_ACCESS_REQUEST = "detection_access_request"
    PREMIUM_UPGRADE_REQUEST = "premium_upgrade_request"
    SIGNUP_VERIFICATION = "signup_verification"
    SYSTEM_ALERT = "system_alert"
    USER_ACTIVITY = "user_activity"
    DETECTION_COMPLETE = "detection_complete"
    ACCOUNT_SUSPENDED = "account_suspended"
    PAYMENT_FAILED = "payment_failed"
    FEATURE_ANNOUNCEMENT = "feature_announcement"

class NotificationPriority(str, Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class NotificationStatus(str, Enum):
    """Notification status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    PUSH = "push"

class UserNotification(Base):
    """User notification requests and responses"""
    __tablename__ = "user_notifications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    user_email = Column(String(255), nullable=False, index=True)
    user_name = Column(String(255), nullable=False)
    
    # Notification details
    notification_type = Column(SQLEnum(NotificationType), nullable=False)
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.MEDIUM)
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING)
    
    # Request content
    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional data like detection results, etc.
    
    # Admin management
    admin_id = Column(String(36), nullable=True)
    admin_notes = Column(Text, nullable=True)
    admin_action_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Delivery tracking
    channels_sent = Column(JSON, nullable=True)  # Track which channels were used
    delivery_status = Column(JSON, nullable=True)  # Track delivery success/failure
    
    # User interaction
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Analytics
    view_count = Column(Integer, default=0)
    action_taken = Column(String(100), nullable=True)  # What action user took
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "user_name": self.user_name,
            "notification_type": self.notification_type,
            "priority": self.priority,
            "status": self.status,
            "title": self.title,
            "message": self.message,
            "metadata": self.metadata,
            "admin_id": self.admin_id,
            "admin_notes": self.admin_notes,
            "admin_action_timestamp": self.admin_action_timestamp.isoformat() if self.admin_action_timestamp else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "channels_sent": self.channels_sent,
            "delivery_status": self.delivery_status,
            "is_read": self.is_read,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "view_count": self.view_count,
            "action_taken": self.action_taken
        }

class NotificationTemplate(Base):
    """Notification templates for consistent messaging"""
    __tablename__ = "notification_templates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    notification_type = Column(SQLEnum(NotificationType), nullable=False)
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.MEDIUM)
    
    # Template content
    title_template = Column(String(500), nullable=False)
    message_template = Column(Text, nullable=False)
    
    # Delivery settings
    default_channels = Column(JSON, nullable=True)  # Default delivery channels
    auto_expire_hours = Column(Integer, nullable=True)  # Auto-expire after X hours
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def render_template(self, **kwargs):
        """Render template with provided variables"""
        try:
            title = self.title_template.format(**kwargs)
            message = self.message_template.format(**kwargs)
            return {"title": title, "message": message}
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")

class NotificationSettings(Base):
    """User notification preferences"""
    __tablename__ = "notification_settings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, unique=True, index=True)
    
    # Channel preferences
    email_enabled = Column(Boolean, default=True)
    in_app_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    push_enabled = Column(Boolean, default=True)
    
    # Type preferences
    type_preferences = Column(JSON, nullable=True)  # Per-type preferences
    
    # Frequency settings
    digest_frequency = Column(String(20), default="immediate")  # immediate, hourly, daily, weekly
    quiet_hours_start = Column(String(5), nullable=True)  # HH:MM format
    quiet_hours_end = Column(String(5), nullable=True)    # HH:MM format
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class NotificationAnalytics(Base):
    """Notification analytics and metrics"""
    __tablename__ = "notification_analytics"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    notification_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    
    # Event tracking
    event_type = Column(String(50), nullable=False)  # created, sent, delivered, opened, clicked, dismissed
    channel = Column(SQLEnum(NotificationChannel), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Additional data
    metadata = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "notification_id": self.notification_id,
            "user_id": self.user_id,
            "event_type": self.event_type,
            "channel": self.channel,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent
        }
