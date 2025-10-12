import React from 'react';
import { useAuth } from '@/contexts/SimpleAuthContext';

export const AuthDebug: React.FC = () => {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return (
      <div className="fixed top-4 right-4 bg-red-100 border border-red-300 rounded-lg p-4 max-w-sm">
        <h3 className="font-bold text-red-800">Auth Debug - Not Authenticated</h3>
        <p className="text-sm text-red-600">User is not logged in</p>
      </div>
    );
  }

  return (
    <div className="fixed top-4 right-4 bg-blue-100 border border-blue-300 rounded-lg p-4 max-w-sm">
      <h3 className="font-bold text-blue-800">Auth Debug</h3>
      <div className="text-sm text-blue-600 space-y-1">
        <p><strong>User ID:</strong> {user?.id}</p>
        <p><strong>Email:</strong> {user?.email}</p>
        <p><strong>Username:</strong> {user?.username}</p>
        <p><strong>Full Name:</strong> {user?.fullName}</p>
        <p><strong>Is Authenticated:</strong> {isAuthenticated ? '✅ Yes' : '❌ No'}</p>
      </div>
    </div>
  );
};
