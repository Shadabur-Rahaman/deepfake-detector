/**
 * Protected Route Component
 * Production-ready route protection with comprehensive security features.
 * 
 * Provides:
 * - Authentication requirement
 * - Role-based access control
 * - Permission-based access control
 * - Loading states
 * - Error handling
 * - Redirect functionality
 * 
 * Author: Senior Backend Engineer
 */

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useAuth } from '@/contexts/SimpleAuthContext';
import { AccessRequestModal } from './AccessRequestModal';
import { 
  Lock, Shield, Crown, AlertTriangle, Loader2, 
  ArrowRight, Key, Users, Settings, Zap, Send
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  requiredRoles?: string[];
  requiredPermissions?: string[];
  requiredResource?: string;
  requiredAction?: string;
  fallback?: React.ReactNode;
  redirectTo?: string;
  showUpgrade?: boolean;
}

interface AccessDeniedProps {
  reason: 'not_authenticated' | 'insufficient_role' | 'insufficient_permission' | 'loading';
  requiredRoles?: string[];
  requiredPermissions?: string[];
  requiredResource?: string;
  requiredAction?: string;
  onRetry?: () => void;
}

const AccessDenied: React.FC<AccessDeniedProps> = ({
  reason,
  requiredRoles = [],
  requiredPermissions = [],
  requiredResource,
  requiredAction,
  onRetry
}) => {
  const navigate = useNavigate();
  const { login, user, isAuthenticated } = useAuth();
  const [showRequestModal, setShowRequestModal] = useState(false);

  const getReasonInfo = () => {
    switch (reason) {
      case 'not_authenticated':
        return {
          icon: <Lock className="w-12 h-12 text-blue-500" />,
          title: "Authentication Required",
          description: "Please sign in to access this feature.",
          action: "Sign In",
          actionHandler: () => navigate('/login')
        };
      
      case 'insufficient_role':
        return {
          icon: <Crown className="w-12 h-12 text-yellow-500" />,
          title: "Insufficient Role",
          description: `This feature requires one of the following roles: ${requiredRoles.join(', ')}`,
          action: "Upgrade Account",
          actionHandler: () => navigate('/upgrade')
        };
      
      case 'insufficient_permission':
        return {
          icon: <Shield className="w-12 h-12 text-red-500" />,
          title: "Access Denied",
          description: `You don't have permission to ${requiredAction || 'access'} ${requiredResource || 'this resource'}.`,
          action: "Request Access",
          actionHandler: () => navigate('/contact')
        };
      
      case 'loading':
        return {
          icon: <Loader2 className="w-12 h-12 text-gray-500 animate-spin" />,
          title: "Loading...",
          description: "Please wait while we verify your access.",
          action: null,
          actionHandler: null
        };
      
      default:
        return {
          icon: <AlertTriangle className="w-12 h-12 text-gray-500" />,
          title: "Access Denied",
          description: "You don't have permission to access this feature.",
          action: "Go Back",
          actionHandler: () => navigate(-1)
        };
    }
  };

  const reasonInfo = getReasonInfo();

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-background to-muted/20">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="w-full max-w-lg"
      >
        <Card className="neural-card text-center p-8 shadow-2xl border-2 border-primary/20 bg-gradient-to-br from-primary/5 via-background to-accent/5 backdrop-blur-sm">
          <CardHeader>
            <div className="flex justify-center mb-6">
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.2, duration: 0.5 }}
                className="w-16 h-16 bg-gradient-to-br from-primary/20 to-accent/20 rounded-full flex items-center justify-center neural-glow"
              >
                {reasonInfo.icon}
              </motion.div>
            </div>
            <CardTitle className="text-3xl font-bold gradient-text neural-text mb-2">
              {reasonInfo.title}
            </CardTitle>
            <p className="text-lg text-muted-foreground neural-text">
              {reasonInfo.description}
            </p>
          </CardHeader>
          
          <CardContent className="space-y-6">
            {/* Show required roles */}
            {requiredRoles.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.5 }}
                className="space-y-3"
              >
                <p className="text-sm font-medium text-muted-foreground neural-text">Required Roles:</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {requiredRoles.map((role) => (
                    <Badge 
                      key={role} 
                      variant="secondary"
                      className="neural-card bg-primary/10 text-primary border-primary/20 hover:bg-primary/20 transition-colors"
                    >
                      <Users className="w-3 h-3 mr-1" />
                      {role}
                    </Badge>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Show required permissions */}
            {requiredPermissions.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4, duration: 0.5 }}
                className="space-y-3"
              >
                <p className="text-sm font-medium text-muted-foreground neural-text">Required Permissions:</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {requiredPermissions.map((permission) => (
                    <Badge 
                      key={permission} 
                      variant="outline"
                      className="neural-card bg-accent/10 text-accent border-accent/20 hover:bg-accent/20 transition-colors"
                    >
                      <Shield className="w-3 h-3 mr-1" />
                      {permission}
                    </Badge>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Action buttons */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.5 }}
              className="flex flex-col sm:flex-row gap-3 justify-center"
            >
              {reasonInfo.action && reasonInfo.actionHandler && (
                <Button 
                  onClick={reasonInfo.actionHandler}
                  className="neural-button hover-lift bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-lg hover:shadow-xl transition-all duration-300 px-8 py-3"
                >
                  {reasonInfo.action}
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              )}
              
              {onRetry && reason !== 'loading' && (
                <Button 
                  variant="outline" 
                  onClick={onRetry}
                  className="neural-button hover-lift bg-background border-border text-foreground hover:bg-accent hover:text-accent-foreground shadow-md hover:shadow-lg transition-all duration-300 px-8 py-3"
                >
                  <Loader2 className="w-4 h-4 mr-2" />
                  Retry
                </Button>
              )}
            </motion.div>

            {/* Additional help */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.5 }}
            >
              {reason === 'not_authenticated' && (
                <Alert className="neural-card text-left bg-muted/30 border-border/50">
                  <Key className="h-4 w-4" />
                  <AlertDescription className="neural-text">
                    <strong>Need an account?</strong> You can create one for free and start detecting deepfakes immediately.
                  </AlertDescription>
                </Alert>
              )}

              {reason === 'insufficient_role' && (
                <Alert className="neural-card text-left bg-warning/10 border-warning/20">
                  <Crown className="h-4 w-4" />
                  <AlertDescription className="neural-text">
                    <strong>Upgrade your account</strong> to access advanced features and higher detection limits.
                  </AlertDescription>
                </Alert>
              )}

              {reason === 'insufficient_permission' && (
                <Alert className="neural-card text-left bg-destructive/10 border-destructive/20">
                  <Shield className="h-4 w-4" />
                  <AlertDescription className="neural-text">
                    <strong>Contact support</strong> if you believe you should have access to this feature.
                  </AlertDescription>
                </Alert>
              )}
            </motion.div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Access Request Modal */}
      <AccessRequestModal
        isOpen={showRequestModal}
        onClose={() => setShowRequestModal(false)}
        requestType={reason === 'insufficient_role' ? 'premium_upgrade' : 'detection_access'}
      />
    </div>
  );
};

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireAuth = true,
  requiredRoles = [],
  requiredPermissions = [],
  requiredResource,
  requiredAction,
  fallback,
  redirectTo,
  showUpgrade = true
}) => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const [accessChecked, setAccessChecked] = useState(false);
  const [accessDenied, setAccessDenied] = useState(false);
  const [denialReason, setDenialReason] = useState<'not_authenticated' | 'insufficient_role' | 'insufficient_permission' | 'loading'>('loading');

  // Check access permissions
  useEffect(() => {
    const checkAccess = async () => {
      if (isLoading) {
        setDenialReason('loading');
        return;
      }

      // Check authentication requirement
      if (requireAuth && !isAuthenticated) {
        setDenialReason('not_authenticated');
        setAccessDenied(true);
        setAccessChecked(true);
        return;
      }

      // If no authentication required and user is not authenticated, allow access
      if (!requireAuth && !isAuthenticated) {
        setAccessDenied(false);
        setAccessChecked(true);
        return;
      }

      // If user is authenticated, check roles and permissions
      if (isAuthenticated && user) {
        // Check roles
        if (requiredRoles.length > 0) {
          const hasRequiredRole = requiredRoles.some(role => user.roles && user.roles.includes(role));
          if (!hasRequiredRole) {
            setDenialReason('insufficient_role');
            setAccessDenied(true);
            setAccessChecked(true);
            return;
          }
        }

        // Check permissions
        if (requiredPermissions.length > 0) {
          const hasRequiredPermission = requiredPermissions.some(permission => 
            user.permissions && user.permissions.includes(permission)
          );
          if (!hasRequiredPermission) {
            setDenialReason('insufficient_permission');
            setAccessDenied(true);
            setAccessChecked(true);
            return;
          }
        }

        // Check resource-specific permission
        if (requiredResource && requiredAction) {
          const hasResourcePermission = (user.permissions && (
            user.permissions.includes(`${requiredResource}:${requiredAction}`) ||
            user.permissions.includes(`${requiredResource}:*`) ||
            user.permissions.includes(`*:${requiredAction}`)
          ));
          if (!hasResourcePermission) {
            setDenialReason('insufficient_permission');
            setAccessDenied(true);
            setAccessChecked(true);
            return;
          }
        }
      }

      // Access granted
      setAccessDenied(false);
      setAccessChecked(true);
    };

    checkAccess();
  }, [isAuthenticated, isLoading, user, requireAuth, requiredRoles, requiredPermissions, requiredResource, requiredAction]);

  // Show loading state
  if (!accessChecked || isLoading) {
    return (
      <AccessDenied 
        reason="loading"
        onRetry={() => setAccessChecked(false)}
      />
    );
  }

  // Show access denied
  if (accessDenied) {
    if (fallback) {
      return <>{fallback}</>;
    }

    return (
      <AccessDenied
        reason={denialReason}
        requiredRoles={requiredRoles}
        requiredPermissions={requiredPermissions}
        requiredResource={requiredResource}
        requiredAction={requiredAction}
        onRetry={() => {
          setAccessChecked(false);
          setAccessDenied(false);
        }}
      />
    );
  }

  // Access granted - render children
  return <>{children}</>;
};

// Higher-order component for easier usage
export const withAuth = (
  WrappedComponent: React.ComponentType<any>,
  options: Omit<ProtectedRouteProps, 'children'> = {}
) => {
  return (props: any) => (
    <ProtectedRoute {...options}>
      <WrappedComponent {...props} />
    </ProtectedRoute>
  );
};

// Permission-based component wrapper
export const withPermission = (
  WrappedComponent: React.ComponentType<any>,
  permission: string,
  resource?: string
) => {
  return withAuth(WrappedComponent, {
    requiredPermissions: [permission],
    requiredResource: resource,
    requiredAction: permission.split(':')[1] || 'read'
  });
};

// Role-based component wrapper
export const withRole = (
  WrappedComponent: React.ComponentType<any>,
  role: string
) => {
  return withAuth(WrappedComponent, {
    requiredRoles: [role]
  });
};

// Admin-only component wrapper
export const withAdmin = (WrappedComponent: React.ComponentType<any>) => {
  return withRole(WrappedComponent, 'admin');
};
