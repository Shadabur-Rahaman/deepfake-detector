/**
 * Simple Authentication Guard Component
 * A simplified version that works with the existing authentication system.
 */

import React from 'react';
import { useAuth } from '@/contexts/SimpleAuthContext';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, Shield, AlertTriangle } from 'lucide-react';

interface SimpleAuthGuardProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  requiredPermissions?: string[];
  requiredRoles?: string[];
}

export const SimpleAuthGuard: React.FC<SimpleAuthGuardProps> = ({
  children,
  requireAuth = true,
  requiredPermissions = [],
  requiredRoles = []
}) => {
  const { user, isAuthenticated, isLoading } = useAuth();

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Card className="w-full max-w-md">
          <CardContent className="flex flex-col items-center justify-center p-8">
            <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
            <p className="text-muted-foreground">Loading authentication...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Check if authentication is required
  if (requireAuth && !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <Shield className="h-12 w-12 text-primary" />
            </div>
            <CardTitle>Authentication Required</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                You need to sign in to access this feature. Please sign in to continue.
              </AlertDescription>
            </Alert>
            <Button 
              onClick={() => window.location.href = '/'}
              className="w-full"
            >
              Go to Home
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Check permissions if user is authenticated
  if (isAuthenticated && user) {
    // Check roles
    if (requiredRoles.length > 0) {
      const hasRequiredRole = requiredRoles.some(role => 
        user.roles?.includes(role)
      );
      if (!hasRequiredRole) {
        return (
          <div className="min-h-screen flex items-center justify-center bg-background p-4">
            <Card className="w-full max-w-md">
              <CardHeader className="text-center">
                <div className="flex justify-center mb-4">
                  <AlertTriangle className="h-12 w-12 text-destructive" />
                </div>
                <CardTitle>Access Denied</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    You don't have the required permissions to access this feature.
                  </AlertDescription>
                </Alert>
                <Button 
                  onClick={() => window.location.href = '/'}
                  className="w-full"
                >
                  Go to Home
                </Button>
              </CardContent>
            </Card>
          </div>
        );
      }
    }

    // Check permissions
    if (requiredPermissions.length > 0) {
      const hasRequiredPermission = requiredPermissions.some(permission => 
        user.permissions?.includes(permission)
      );
      if (!hasRequiredPermission) {
        return (
          <div className="min-h-screen flex items-center justify-center bg-background p-4">
            <Card className="w-full max-w-md">
              <CardHeader className="text-center">
                <div className="flex justify-center mb-4">
                  <AlertTriangle className="h-12 w-12 text-destructive" />
                </div>
                <CardTitle>Access Denied</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    You don't have the required permissions to access this feature.
                  </AlertDescription>
                </Alert>
                <Button 
                  onClick={() => window.location.href = '/'}
                  className="w-full"
                >
                  Go to Home
                </Button>
              </CardContent>
            </Card>
          </div>
        );
      }
    }
  }

  // If all checks pass, render children
  return <>{children}</>;
};

export default SimpleAuthGuard;
