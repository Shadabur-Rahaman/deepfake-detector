import { useAuth } from '@/contexts/SimpleAuthContext';
import { useMemo } from 'react';

export interface AccessControlConfig {
  feature: 'try' | 'detection';
  requiredRoles: string[];
  requiredPermissions: string[];
}

export const useAccessControl = (config: AccessControlConfig) => {
  const { user, isAuthenticated, isLoading } = useAuth();

  const accessControl = useMemo(() => {
    // Show loading state only when actually loading
    if (isLoading) {
      return {
        hasAccess: false,
        isLoading: true,
        canRequestAccess: false,
        reason: 'loading'
      };
    }

    // If no user, show access denied immediately (no loading state)
    if (!user || !isAuthenticated) {
      return {
        hasAccess: false,
        isLoading: false,
        canRequestAccess: false,
        reason: 'not_authenticated'
      };
    }

    // For simple auth, we'll allow access to authenticated users
    // In a real app, you'd implement proper role/permission checking
    const hasRequiredRole = true; // Simplified for simple auth
    const hasRequiredPermission = true; // Simplified for simple auth
    
    const hasAccess = hasRequiredRole || hasRequiredPermission;
    
    return {
      hasAccess,
      isLoading: false,
      canRequestAccess: !hasAccess && user !== null,
      reason: hasAccess ? 'granted' : 'denied',
      userRoles: (user && user.roles && Array.isArray(user.roles)) ? user.roles : [],
      userPermissions: (user && user.permissions && Array.isArray(user.permissions)) ? user.permissions : []
    };
  }, [user, isAuthenticated, isLoading, config]);

  return accessControl;
};

// Predefined configurations for common features
export const ACCESS_CONFIGS: Record<string, AccessControlConfig> = {
  try: {
    feature: 'try',
    requiredRoles: ['user', 'admin', 'premium'],
    requiredPermissions: ['try:access', 'detection:create']
  },
  detection: {
    feature: 'detection',
    requiredRoles: ['user', 'admin', 'premium'],
    requiredPermissions: ['detection:create', 'detection:read']
  }
};
