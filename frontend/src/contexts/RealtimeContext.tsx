import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { useAuth } from './SimpleAuthContext';
import { WS_URL } from '@/config/api';

interface UserRequest {
  id: string;
  userId: string;
  userEmail: string;
  userName: string;
  requestType: 'try_access' | 'detection_access' | 'premium_upgrade' | 'signup_verification';
  status: 'pending' | 'approved' | 'rejected';
  timestamp: string;
  message?: string;
  adminNotes?: string;
  isGenuine: boolean;
}

interface RealtimeContextType {
  userRequests: UserRequest[];
  pendingRequests: UserRequest[];
  genuineUsers: number;
  totalUsers: number;
  isConnected: boolean;
  addUserRequest: (request: UserRequest) => void;
  updateRequestStatus: (requestId: string, status: 'approved' | 'rejected', adminNotes?: string) => void;
  clearNotifications: () => void;
  getRequestCount: () => number;
}

const RealtimeContext = createContext<RealtimeContextType | null>(null);

export const useRealtime = () => {
  const context = useContext(RealtimeContext);
  if (!context) {
    throw new Error('useRealtime must be used within a RealtimeProvider');
  }
  return context;
};

export const RealtimeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [userRequests, setUserRequests] = useState<UserRequest[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);

  // Initialize WebSocket connection with retry logic
  useEffect(() => {
    if (!user) return;

    let reconnectAttempts = 0;
    const maxReconnectAttempts = 3;
    let reconnectTimeout: NodeJS.Timeout;

    const connectWebSocket = () => {
      // Use the WebSocket URL from config
      const wsUrl = WS_URL;
      
      const websocket = new WebSocket(wsUrl);
      
      websocket.onopen = () => {
        // console.log('WebSocket connected');
        setIsConnected(true);
        reconnectAttempts = 0; // Reset retry counter on successful connection
        
        // Send authentication message
        websocket.send(JSON.stringify({
          type: 'auth',
          token: localStorage.getItem('ifake_access_token'),
          userId: user.id,
          role: user.roles?.[0] || 'user'
        }));
      };

      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      websocket.onclose = (event) => {
        // console.log('WebSocket disconnected');
        setIsConnected(false);
        
        // Only log error if it's not a clean close and we haven't exceeded retry attempts
        if (event.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
          console.warn(`WebSocket disconnected (attempt ${reconnectAttempts + 1}/${maxReconnectAttempts})`);
          
          // Exponential backoff for reconnection
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
          reconnectAttempts++;
          
          reconnectTimeout = setTimeout(() => {
            if (user) {
              connectWebSocket();
            }
          }, delay);
        } else if (reconnectAttempts >= maxReconnectAttempts) {
          console.warn('WebSocket: Max reconnection attempts reached. Real-time features disabled.');
        }
      };

      websocket.onerror = (error) => {
        // Only log error on first few attempts to avoid spam
        if (reconnectAttempts < 2) {
          console.warn('WebSocket connection error:', error);
        }
        setIsConnected(false);
      };

      setWs(websocket);
    };

    connectWebSocket();

    return () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      if (ws) {
        ws.close();
      }
    };
  }, [user]);

  const handleWebSocketMessage = useCallback((data: any) => {
    switch (data.type) {
      case 'connection_ready':
        // console.log('WebSocket connection ready:', data.message);
        break;
      case 'auth_success':
        // console.log('WebSocket authentication successful:', data.message);
        break;
      case 'new_request':
        addUserRequest(data.request);
        break;
      case 'request_updated':
        updateRequestStatus(data.requestId, data.status, data.adminNotes);
        break;
      case 'user_stats':
        // Handle user statistics updates
        break;
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  }, []);

  const addUserRequest = useCallback((request: UserRequest) => {
    setUserRequests(prev => {
      // Check if request already exists
      const exists = prev.some(req => req.id === request.id);
      if (exists) return prev;
      
      return [request, ...prev];
    });
  }, []);

  const updateRequestStatus = useCallback((requestId: string, status: 'approved' | 'rejected', adminNotes?: string) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      // Send update to server
      ws.send(JSON.stringify({
        type: status === 'approved' ? 'approve_request' : 'reject_request',
        requestId,
        adminNotes,
        userId: user?.id
      }));
    }
    
    // Update local state
    setUserRequests(prev => 
      prev.map(req => 
        req.id === requestId 
          ? { ...req, status, adminNotes }
          : req
      )
    );
  }, [ws, user?.id]);

  const clearNotifications = useCallback(() => {
    setUserRequests(prev => prev.filter(req => req.status !== 'pending'));
  }, []);

  const getRequestCount = useCallback(() => {
    return userRequests.filter(req => req.status === 'pending').length;
  }, [userRequests]);

  const pendingRequests = userRequests.filter(req => req.status === 'pending');
  const genuineUsers = userRequests.filter(req => req.isGenuine && req.status === 'approved').length;
  const totalUsers = userRequests.filter(req => req.isGenuine).length;

  const value: RealtimeContextType = {
    userRequests,
    pendingRequests,
    genuineUsers,
    totalUsers,
    isConnected,
    addUserRequest,
    updateRequestStatus,
    clearNotifications,
    getRequestCount
  };

  return (
    <RealtimeContext.Provider value={value}>
      {children}
    </RealtimeContext.Provider>
  );
};
