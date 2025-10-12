import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';

interface AuthRequest {
  id: string;
  userId: string;
  userEmail: string;
  userName: string;
  requestType: 'try_access' | 'detection_access' | 'premium_upgrade';
  status: 'pending' | 'approved' | 'rejected';
  timestamp: string;
  message?: string;
  adminNotes?: string;
}

interface AdminNotificationContextType {
  authRequests: AuthRequest[];
  pendingRequests: AuthRequest[];
  addAuthRequest: (request: AuthRequest) => void;
  updateRequestStatus: (requestId: string, status: 'approved' | 'rejected') => void;
  clearNotifications: () => void;
  getRequestCount: () => number;
}

const AdminNotificationContext = createContext<AdminNotificationContextType | null>(null);

export const useAdminNotifications = () => {
  const context = useContext(AdminNotificationContext);
  if (!context) {
    throw new Error('useAdminNotifications must be used within an AdminNotificationProvider');
  }
  return context;
};

export const AdminNotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [authRequests, setAuthRequests] = useState<AuthRequest[]>([]);

  // Simulate real-time notifications (in production, this would use WebSocket or Server-Sent Events)
  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate random auth requests for demo purposes
      if (Math.random() < 0.1) { // 10% chance every 5 seconds
        const newRequest: AuthRequest = {
          id: `req-${Date.now()}`,
          userId: `user-${Math.floor(Math.random() * 1000)}`,
          userEmail: `user${Math.floor(Math.random() * 1000)}@example.com`,
          userName: `User ${Math.floor(Math.random() * 1000)}`,
          requestType: ['try_access', 'detection_access', 'premium_upgrade'][Math.floor(Math.random() * 3)] as any,
          status: 'pending',
          timestamp: new Date().toISOString(),
          message: 'Requesting access to platform features'
        };
        addAuthRequest(newRequest);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const addAuthRequest = useCallback((request: AuthRequest) => {
    setAuthRequests(prev => [request, ...prev]);
    
    // Show toast notification
    toast.info(`New ${request.requestType.replace('_', ' ')} request from ${request.userName}`, {
      description: request.message || 'User is requesting access to platform features',
      duration: 5000,
      action: {
        label: 'View',
        onClick: () => {
          // In a real app, this would navigate to the admin dashboard
          console.log('Navigate to admin dashboard');
        }
      }
    });
  }, []);

  const updateRequestStatus = useCallback((requestId: string, status: 'approved' | 'rejected') => {
    setAuthRequests(prev => 
      prev.map(req => 
        req.id === requestId 
          ? { ...req, status }
          : req
      )
    );
    
    const request = authRequests.find(req => req.id === requestId);
    if (request) {
      toast.success(`Request ${status} for ${request.userName}`, {
        description: `${request.requestType.replace('_', ' ')} access has been ${status}`
      });
    }
  }, [authRequests]);

  const clearNotifications = useCallback(() => {
    setAuthRequests(prev => prev.filter(req => req.status !== 'pending'));
  }, []);

  const getRequestCount = useCallback(() => {
    return authRequests.filter(req => req.status === 'pending').length;
  }, [authRequests]);

  const pendingRequests = authRequests.filter(req => req.status === 'pending');

  const value: AdminNotificationContextType = {
    authRequests,
    pendingRequests,
    addAuthRequest,
    updateRequestStatus,
    clearNotifications,
    getRequestCount
  };

  return (
    <AdminNotificationContext.Provider value={value}>
      {children}
    </AdminNotificationContext.Provider>
  );
};
