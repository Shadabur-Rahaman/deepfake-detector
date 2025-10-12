import React from 'react';
import { useAuth } from '@/contexts/SimpleAuthContext';
import { Shield, Crown, Zap } from 'lucide-react';

interface AdminBypassProps {
  children: React.ReactNode;
  feature: 'try' | 'detection';
  fallbackComponent?: React.ComponentType<any>;
}

export const AdminBypass: React.FC<AdminBypassProps> = ({ 
  children, 
  feature, 
  fallbackComponent: FallbackComponent 
}) => {
  const { user, isAuthenticated } = useAuth();

  // Debug logging (removed for production)
  // console.log('AdminBypass Debug:', {
  //   isAuthenticated,
  //   user: user ? { 
  //     id: user.id, 
  //     email: user.email, 
  //     username: user.username,
  //     fullName: user.fullName
  //   } : null,
  //   feature
  // });

  // For simple auth, we'll allow access to all authenticated users
  // In a real app, you'd implement proper admin role checking
  if (isAuthenticated && user) {
    return (
      <div className="admin-bypass-container">
        <div className="bg-gradient-to-r from-green-50 to-blue-50 p-4 rounded-lg border border-green-200 mb-4">
          <div className="flex items-center gap-2 mb-2">
            <Shield className="w-5 h-5 text-green-600" />
            <h3 className="font-semibold text-green-800">Access Granted</h3>
            <Zap className="w-4 h-4 text-blue-600" />
          </div>
          <p className="text-sm text-green-700">
            Access granted to {feature} section for user: {user.fullName || user.username}
          </p>
        </div>
        {children}
      </div>
    );
  }

  // For non-admin users, render the fallback component (ProtectedRoute)
  if (FallbackComponent) {
    return <FallbackComponent>{children}</FallbackComponent>;
  }

  // If no fallback component provided, render children normally
  return <>{children}</>;
};
