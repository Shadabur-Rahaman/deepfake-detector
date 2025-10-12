"""
Role-Based Access Control (RBAC) Module
Production-ready RBAC implementation with hierarchical permissions.

This module provides:
- Role management
- Permission management
- User-role assignments
- Permission checking
- Hierarchical role inheritance

Author: Senior Backend Engineer
"""

import logging
from typing import List, Dict, Any, Optional, Set
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .models import User, Role, Permission

logger = logging.getLogger(__name__)

class RBACManager:
    """
    Role-Based Access Control Manager
    
    Provides comprehensive RBAC functionality with:
    - Role hierarchy support
    - Permission inheritance
    - Dynamic permission checking
    - Resource-based permissions
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def create_role(
        self, 
        name: str, 
        display_name: str, 
        description: str = None,
        parent_role_id: str = None,
        permissions: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new role with permissions.
        
        Args:
            name: Role name (unique identifier)
            display_name: Human-readable role name
            description: Role description
            parent_role_id: Parent role for hierarchy
            permissions: List of permission names
            
        Returns:
            Created role information
        """
        # Check if role already exists
        existing_role = self.db.query(Role).filter(Role.name == name).first()
        if existing_role:
            raise ValueError(f"Role '{name}' already exists")
        
        # Calculate hierarchy level
        level = 0
        if parent_role_id:
            parent_role = self.db.query(Role).filter(Role.id == parent_role_id).first()
            if parent_role:
                level = parent_role.level + 1
        
        # Create role
        role = Role(
            name=name,
            display_name=display_name,
            description=description,
            parent_role_id=parent_role_id,
            level=level
        )
        
        self.db.add(role)
        self.db.flush()  # Get role ID
        
        # Assign permissions
        if permissions:
            await self.assign_permissions_to_role(role.id, permissions)
        
        self.db.commit()
        
        return {
            "id": str(role.id),
            "name": role.name,
            "display_name": role.display_name,
            "description": role.description,
            "level": role.level,
            "permissions": permissions or []
        }
    
    async def create_permission(
        self,
        name: str,
        display_name: str,
        description: str = None,
        category: str = "general",
        resource: str = None,
        action: str = "read"
    ) -> Dict[str, Any]:
        """
        Create a new permission.
        
        Args:
            name: Permission name (unique identifier)
            display_name: Human-readable permission name
            description: Permission description
            category: Permission category
            resource: Resource this permission applies to
            action: Action this permission allows
            
        Returns:
            Created permission information
        """
        # Check if permission already exists
        existing_permission = self.db.query(Permission).filter(Permission.name == name).first()
        if existing_permission:
            raise ValueError(f"Permission '{name}' already exists")
        
        # Create permission
        permission = Permission(
            name=name,
            display_name=display_name,
            description=description,
            category=category,
            resource=resource,
            action=action
        )
        
        self.db.add(permission)
        self.db.commit()
        
        return {
            "id": str(permission.id),
            "name": permission.name,
            "display_name": permission.display_name,
            "category": permission.category,
            "resource": permission.resource,
            "action": permission.action
        }
    
    async def assign_roles_to_user(self, user_id: str, role_names: List[str]) -> bool:
        """
        Assign roles to user.
        
        Args:
            user_id: User ID
            role_names: List of role names to assign
            
        Returns:
            True if successful
        """
        try:
            # Get user
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Get roles
            roles = self.db.query(Role).filter(
                and_(
                    Role.name.in_(role_names),
                    Role.is_active == True
                )
            ).all()
            
            if len(roles) != len(role_names):
                found_names = [role.name for role in roles]
                missing = set(role_names) - set(found_names)
                raise ValueError(f"Roles not found: {missing}")
            
            # Assign roles
            for role in roles:
                if role not in user.roles:
                    user.roles.append(role)
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to assign roles to user {user_id}: {str(e)}")
            self.db.rollback()
            return False
    
    async def remove_roles_from_user(self, user_id: str, role_names: List[str]) -> bool:
        """
        Remove roles from user.
        
        Args:
            user_id: User ID
            role_names: List of role names to remove
            
        Returns:
            True if successful
        """
        try:
            # Get user
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Get roles to remove
            roles_to_remove = self.db.query(Role).filter(
                and_(
                    Role.name.in_(role_names),
                    Role.is_active == True
                )
            ).all()
            
            # Remove roles
            for role in roles_to_remove:
                if role in user.roles:
                    user.roles.remove(role)
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove roles from user {user_id}: {str(e)}")
            self.db.rollback()
            return False
    
    async def assign_permissions_to_role(self, role_id: str, permission_names: List[str]) -> bool:
        """
        Assign permissions to role.
        
        Args:
            role_id: Role ID
            permission_names: List of permission names to assign
            
        Returns:
            True if successful
        """
        try:
            # Get role
            role = self.db.query(Role).filter(Role.id == role_id).first()
            if not role:
                raise ValueError(f"Role {role_id} not found")
            
            # Get permissions
            permissions = self.db.query(Permission).filter(
                and_(
                    Permission.name.in_(permission_names),
                    Permission.is_active == True
                )
            ).all()
            
            if len(permissions) != len(permission_names):
                found_names = [perm.name for perm in permissions]
                missing = set(permission_names) - set(found_names)
                raise ValueError(f"Permissions not found: {missing}")
            
            # Assign permissions
            for permission in permissions:
                if permission not in role.permissions:
                    role.permissions.append(permission)
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to assign permissions to role {role_id}: {str(e)}")
            self.db.rollback()
            return False
    
    async def get_user_permissions(self, user_id: str) -> List[str]:
        """
        Get all permissions for user (including inherited from roles).
        
        Args:
            user_id: User ID
            
        Returns:
            List of permission names
        """
        try:
            # Get user with roles
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return []
            
            # Collect permissions from all roles
            permissions = set()
            for role in user.roles:
                if role.is_active:
                    # Add direct permissions
                    for permission in role.permissions:
                        if permission.is_active:
                            permissions.add(permission.name)
                    
                    # Add inherited permissions from parent roles
                    inherited_permissions = await self._get_inherited_permissions(role.id)
                    permissions.update(inherited_permissions)
            
            return list(permissions)
            
        except Exception as e:
            logger.error(f"Failed to get permissions for user {user_id}: {str(e)}")
            return []
    
    async def check_permission(
        self, 
        user_id: str, 
        permission: str, 
        resource: str = None
    ) -> bool:
        """
        Check if user has specific permission.
        
        Args:
            user_id: User ID
            permission: Permission to check
            resource: Optional resource context
            
        Returns:
            True if user has permission
        """
        try:
            user_permissions = await self.get_user_permissions(user_id)
            
            # Check exact permission
            if permission in user_permissions:
                return True
            
            # Check wildcard permissions
            if resource:
                wildcard_permission = f"{permission}:{resource}"
                if wildcard_permission in user_permissions:
                    return True
            
            # Check category-based permissions
            permission_parts = permission.split(":")
            if len(permission_parts) >= 2:
                category = permission_parts[0]
                action = permission_parts[1]
                
                category_permission = f"{category}:*"
                if category_permission in user_permissions:
                    return True
                
                action_permission = f"*:{action}"
                if action_permission in user_permissions:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Permission check failed for user {user_id}: {str(e)}")
            return False
    
    async def check_role(self, user_id: str, role_name: str) -> bool:
        """
        Check if user has specific role.
        
        Args:
            user_id: User ID
            role_name: Role name to check
            
        Returns:
            True if user has role
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            role_names = [role.name for role in user.roles if role.is_active]
            return role_name in role_names
            
        except Exception as e:
            logger.error(f"Role check failed for user {user_id}: {str(e)}")
            return False
    
    async def _get_inherited_permissions(self, role_id: str) -> Set[str]:
        """
        Get permissions inherited from parent roles.
        
        Args:
            role_id: Role ID
            
        Returns:
            Set of inherited permission names
        """
        try:
            permissions = set()
            
            # Get role
            role = self.db.query(Role).filter(Role.id == role_id).first()
            if not role or not role.parent_role_id:
                return permissions
            
            # Get parent role
            parent_role = self.db.query(Role).filter(Role.id == role.parent_role_id).first()
            if not parent_role or not parent_role.is_active:
                return permissions
            
            # Add parent role permissions
            for permission in parent_role.permissions:
                if permission.is_active:
                    permissions.add(permission.name)
            
            # Recursively get inherited permissions
            inherited = await self._get_inherited_permissions(parent_role.id)
            permissions.update(inherited)
            
            return permissions
            
        except Exception as e:
            logger.error(f"Failed to get inherited permissions for role {role_id}: {str(e)}")
            return set()
    
    async def get_user_roles(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get user roles with details.
        
        Args:
            user_id: User ID
            
        Returns:
            List of role information
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return []
            
            roles = []
            for role in user.roles:
                if role.is_active:
                    roles.append({
                        "id": str(role.id),
                        "name": role.name,
                        "display_name": role.display_name,
                        "description": role.description,
                        "level": role.level
                    })
            
            return roles
            
        except Exception as e:
            logger.error(f"Failed to get roles for user {user_id}: {str(e)}")
            return []
    
    async def initialize_default_roles_and_permissions(self) -> bool:
        """
        Initialize default roles and permissions for the system.
        
        Returns:
            True if successful
        """
        try:
            # Define default permissions
            default_permissions = [
                # Detection permissions
                ("detection:create", "Create Detection", "Create new deepfake detection", "detection", "detection", "create"),
                ("detection:read", "Read Detection", "View detection results", "detection", "detection", "read"),
                ("detection:update", "Update Detection", "Update detection settings", "detection", "detection", "update"),
                ("detection:delete", "Delete Detection", "Delete detection results", "detection", "detection", "delete"),
                
                # User management permissions
                ("user:read", "Read Users", "View user information", "user", "user", "read"),
                ("user:update", "Update Users", "Update user information", "user", "user", "update"),
                ("user:delete", "Delete Users", "Delete user accounts", "user", "user", "delete"),
                
                # Admin permissions
                ("admin:read", "Admin Read", "View admin information", "admin", "system", "read"),
                ("admin:write", "Admin Write", "Modify system settings", "admin", "system", "write"),
                ("admin:delete", "Admin Delete", "Delete system data", "admin", "system", "delete"),
                
                # API permissions
                ("api:read", "API Read", "Access API endpoints", "api", "api", "read"),
                ("api:write", "API Write", "Modify via API", "api", "api", "write"),
            ]
            
            # Create permissions
            for perm_data in default_permissions:
                existing = self.db.query(Permission).filter(Permission.name == perm_data[0]).first()
                if not existing:
                    permission = Permission(
                        name=perm_data[0],
                        display_name=perm_data[1],
                        description=perm_data[2],
                        category=perm_data[3],
                        resource=perm_data[4],
                        action=perm_data[5],
                        is_system_permission=True
                    )
                    self.db.add(permission)
            
            # Define default roles
            default_roles = [
                ("admin", "Administrator", "Full system access", None, [
                    "detection:create", "detection:read", "detection:update", "detection:delete",
                    "user:read", "user:update", "user:delete",
                    "admin:read", "admin:write", "admin:delete",
                    "api:read", "api:write"
                ]),
                ("moderator", "Moderator", "Content moderation access", None, [
                    "detection:create", "detection:read", "detection:update",
                    "user:read", "user:update",
                    "api:read", "api:write"
                ]),
                ("user", "Regular User", "Standard user access", None, [
                    "detection:create", "detection:read",
                    "api:read"
                ]),
            ]
            
            # Create roles
            for role_data in default_roles:
                existing = self.db.query(Role).filter(Role.name == role_data[0]).first()
                if not existing:
                    role = Role(
                        name=role_data[0],
                        display_name=role_data[1],
                        description=role_data[2],
                        parent_role_id=role_data[3],
                        is_system_role=True
                    )
                    self.db.add(role)
                    self.db.flush()  # Get role ID
                    
                    # Assign permissions
                    if role_data[4]:
                        await self.assign_permissions_to_role(role.id, role_data[4])
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize default roles and permissions: {str(e)}")
            self.db.rollback()
            return False
