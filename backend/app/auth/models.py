"""
Database Models for Authentication & Authorization
Production-ready SQLAlchemy models with comprehensive security features.

This module defines all database models for:
- User management
- Role-based access control (RBAC)
- Session management
- Audit logging
- API key management

Author: Senior Backend Engineer
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, JSON, 
    ForeignKey, Table, UniqueConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid

Base = declarative_base()

# Association tables for many-to-many relationships
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', String(36), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', String(36), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', DateTime(timezone=True), server_default=func.now()),
    Column('assigned_by', String(36), ForeignKey('users.id', name='fk_user_roles_assigned_by')),
    Index('idx_user_roles_user_id', 'user_id'),
    Index('idx_user_roles_role_id', 'role_id')
)

role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', String(36), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', String(36), ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', DateTime(timezone=True), server_default=func.now()),
    Column('assigned_by', String(36), ForeignKey('users.id', name='fk_role_permissions_assigned_by')),
    Index('idx_role_permissions_role_id', 'role_id'),
    Index('idx_role_permissions_permission_id', 'permission_id')
)

class UserStatus(str, Enum):
    """User account status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    LOCKED = "locked"

class UserRole(str, Enum):
    """User role enumeration for subscription plans."""
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"

class User(Base):
    """
    User model with comprehensive security features.
    
    Implements enterprise-grade user management with:
    - Secure password storage
    - Account status tracking
    - Multi-factor authentication support
    - Audit trail
    - Session management
    """
    __tablename__ = "users"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Basic information
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_2fa_enabled = Column(Boolean, default=False, nullable=False)
    status = Column(String(50), default=UserStatus.PENDING_VERIFICATION, nullable=False)
    
    # Security features
    totp_secret = Column(String(32), nullable=True)  # 2FA secret
    backup_codes = Column(JSON, nullable=True)  # 2FA backup codes
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String(45), nullable=True)
    last_login_user_agent = Column(Text, nullable=True)
    
    # Account creation tracking
    created_ip = Column(String(45), nullable=True)
    created_user_agent = Column(Text, nullable=True)
    
    # Relationships (simplified for now)
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    roles = relationship("Role", secondary=user_roles, backref="users", 
                        primaryjoin="User.id == user_roles.c.user_id",
                        secondaryjoin="Role.id == user_roles.c.role_id")
    
    @property
    def permissions(self):
        """Get all permissions for this user through their roles"""
        permissions = set()
        for role in self.roles:
            for permission in role.permissions:
                permissions.add(permission.name)
        return list(permissions)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_users_email_active', 'email', 'is_active'),
        Index('idx_users_username_active', 'username', 'is_active'),
        Index('idx_users_status', 'status'),
        Index('idx_users_created_at', 'created_at'),
    )
    
    @validates('email')
    def validate_email(self, key, email):
        """Validate email format."""
        if '@' not in email or '.' not in email.split('@')[1]:
            raise ValueError("Invalid email format")
        return email.lower()
    
    @validates('username')
    def validate_username(self, key, username):
        """Validate username format."""
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not username.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Username can only contain letters, numbers, hyphens, and underscores")
        return username.lower()
    
    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}', username='{self.username}')>"

class Role(Base):
    """
    Role model for role-based access control.
    
    Defines user roles with hierarchical permissions and
    comprehensive access control capabilities.
    """
    __tablename__ = "roles"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Role information
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Role hierarchy
    parent_role_id = Column(String(36), ForeignKey('roles.id'), nullable=True)
    level = Column(Integer, default=0, nullable=False)  # Hierarchy level
    
    # Role settings
    is_active = Column(Boolean, default=True, nullable=False)
    is_system_role = Column(Boolean, default=False, nullable=False)  # Cannot be deleted
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships (simplified for now)
    parent_role = relationship("Role", remote_side=[id], backref="child_roles")
    permissions = relationship("Permission", secondary=role_permissions, backref="roles",
                              primaryjoin="Role.id == role_permissions.c.role_id",
                              secondaryjoin="Permission.id == role_permissions.c.permission_id")
    
    # Indexes
    __table_args__ = (
        Index('idx_roles_name_active', 'name', 'is_active'),
        Index('idx_roles_level', 'level'),
        Index('idx_roles_parent', 'parent_role_id'),
    )
    
    def __repr__(self):
        return f"<Role(id='{self.id}', name='{self.name}', level={self.level})>"

class Permission(Base):
    """
    Permission model for granular access control.
    
    Defines specific permissions that can be assigned to roles
    for fine-grained access control.
    """
    __tablename__ = "permissions"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Permission information
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Permission categorization
    category = Column(String(100), nullable=False, index=True)  # e.g., 'detection', 'admin', 'user'
    resource = Column(String(100), nullable=True)  # e.g., 'video', 'user', 'system'
    action = Column(String(50), nullable=False)  # e.g., 'read', 'write', 'delete', 'execute'
    
    # Permission settings
    is_active = Column(Boolean, default=True, nullable=False)
    is_system_permission = Column(Boolean, default=False, nullable=False)  # Cannot be deleted
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships (simplified for now)
    
    # Indexes
    __table_args__ = (
        Index('idx_permissions_name_active', 'name', 'is_active'),
        Index('idx_permissions_category', 'category'),
        Index('idx_permissions_resource_action', 'resource', 'action'),
    )
    
    def __repr__(self):
        return f"<Permission(id='{self.id}', name='{self.name}', resource='{self.resource}', action='{self.action}')>"

class UserSession(Base):
    """
    User session model for session management.
    
    Tracks user sessions with comprehensive security features
    including IP tracking, user agent validation, and session hijacking protection.
    """
    __tablename__ = "user_sessions"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Session information
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Security tracking
    ip_address = Column(String(45), nullable=False, index=True)
    user_agent = Column(Text, nullable=True)
    device_fingerprint = Column(String(255), nullable=True)  # Browser fingerprint
    
    # Session state
    is_active = Column(Boolean, default=True, nullable=False)
    is_secure = Column(Boolean, default=True, nullable=False)  # HTTPS session
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    # Indexes
    __table_args__ = (
        Index('idx_sessions_user_active', 'user_id', 'is_active'),
        Index('idx_sessions_expires', 'expires_at'),
        Index('idx_sessions_ip', 'ip_address'),
    )
    
    def __repr__(self):
        return f"<UserSession(id='{self.id}', user_id='{self.user_id}', active={self.is_active})>"

class APIKey(Base):
    """
    API key model for programmatic access.
    
    Manages API keys for programmatic access with
    comprehensive security and monitoring features.
    """
    __tablename__ = "api_keys"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # API key information
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(255), nullable=False)  # User-defined name
    key_hash = Column(String(255), unique=True, nullable=False, index=True)  # Hashed key
    
    # Access control
    permissions = Column(JSON, nullable=True)  # Specific permissions for this key
    allowed_ips = Column(JSON, nullable=True)  # IP whitelist
    rate_limit = Column(Integer, default=1000, nullable=False)  # Requests per hour
    
    # Status and tracking
    is_active = Column(Boolean, default=True, nullable=False)
    last_used = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(Integer, default=0, nullable=False)
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    # Indexes
    __table_args__ = (
        Index('idx_api_keys_user_active', 'user_id', 'is_active'),
        Index('idx_api_keys_hash', 'key_hash'),
        Index('idx_api_keys_expires', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<APIKey(id='{self.id}', name='{self.name}', user_id='{self.user_id}')>"

class AuditLog(Base):
    """
    Audit log model for comprehensive security monitoring.
    
    Records all security-relevant events for compliance,
    monitoring, and forensic analysis.
    """
    __tablename__ = "audit_logs"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Event information
    user_id = Column(String(36), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    event_category = Column(String(50), nullable=False, index=True)  # auth, security, api, etc.
    
    # Context information
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    session_id = Column(String(36), nullable=True, index=True)
    
    # Event details
    details = Column(JSON, nullable=True)
    severity = Column(String(20), default="info", nullable=False, index=True)  # info, warning, error, critical
    
    # Resource information
    resource_type = Column(String(100), nullable=True)  # user, video, model, etc.
    resource_id = Column(String(36), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_logs_user_event', 'user_id', 'event_type'),
        Index('idx_audit_logs_category_severity', 'event_category', 'severity'),
        Index('idx_audit_logs_created_at', 'created_at'),
        Index('idx_audit_logs_ip', 'ip_address'),
    )
    
    def __repr__(self):
        return f"<AuditLog(id='{self.id}', event_type='{self.event_type}', user_id='{self.user_id}')>"

class PasswordReset(Base):
    """
    Password reset token model.
    
    Manages password reset tokens with security features
    including expiration and single-use validation.
    """
    __tablename__ = "password_resets"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Reset information
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    
    # Security tracking
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Status
    is_used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_password_resets_user', 'user_id'),
        Index('idx_password_resets_token', 'token_hash'),
        Index('idx_password_resets_expires', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<PasswordReset(id='{self.id}', user_id='{self.user_id}', used={self.is_used})>"