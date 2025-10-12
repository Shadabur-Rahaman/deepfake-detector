import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { toast } from 'sonner';
import { useAuth } from './SimpleAuthContext';
import { WS_URL } from '@/config/api';

export interface NotificationRequest {
  id: string;
  userId: string;
  userEmail: string;
  userName: string;
  requestType: 'try_access' | 'detection_access' | 'premium_upgrade' | 'signup_verification';
  status: 'pending' | 'approved' | 'rejected';
  timestamp: string;
  updatedAt?: string;
  message?: string;
  adminNotes?: string;
  isGenuine: boolean;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  source: 'web' | 'api' | 'mobile';
  userAgent?: string;
  ipAddress?: string;
  location?: {
    country?: string;
    city?: string;
  };
  metadata?: {
    previousRequests?: number;
    userTier?: string;
    accountAge?: number;
  };
}

export interface NotificationStats {
  totalRequests: number;
  pendingRequests: number;
  approvedRequests: number;
  rejectedRequests: number;
  genuineUsers: number;
  suspiciousUsers: number;
  averageResponseTime: number;
  requestsByType: Record<string, number>;
  requestsByHour: Record<string, number>;
  topRequestSources: Array<{ source: string; count: number }>;
}

export interface NotificationSettings {
  soundEnabled: boolean;
  desktopNotifications: boolean;
  autoRefresh: boolean;
  refreshInterval: number;
  showToastNotifications: boolean;
  priorityFilter: string[];
  requestTypeFilter: string[];
  maxNotificationsToShow: number;
}

interface EnhancedNotificationContextType {
  // State
  notifications: NotificationRequest[];
  pendingNotifications: NotificationRequest[];
  isConnected: boolean;
  isLoading: boolean;
  settings: NotificationSettings;
  stats: NotificationStats;
  
  // Actions
  addNotification: (notification: NotificationRequest) => void;
  updateNotificationStatus: (id: string, status: 'approved' | 'rejected', adminNotes?: string) => Promise<void>;
  bulkUpdateStatus: (ids: string[], status: 'approved' | 'rejected', adminNotes?: string) => Promise<void>;
  clearNotifications: (status?: 'pending' | 'approved' | 'rejected') => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  
  // Settings
  updateSettings: (newSettings: Partial<NotificationSettings>) => void;
  
  // Utils
  getNotificationCount: (status?: 'pending' | 'approved' | 'rejected') => number;
  getNotificationsByType: (type: string) => NotificationRequest[];
  getNotificationsByPriority: (priority: string) => NotificationRequest[];
  searchNotifications: (query: string) => NotificationRequest[];
  refreshNotifications: () => Promise<void>;
  
  // WebSocket
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
}

const EnhancedNotificationContext = createContext<EnhancedNotificationContextType | null>(null);

export const useEnhancedNotifications = () => {
  const context = useContext(EnhancedNotificationContext);
  if (!context) {
    throw new Error('useEnhancedNotifications must be used within an EnhancedNotificationProvider');
  }
  return context;
};

const DEFAULT_SETTINGS: NotificationSettings = {
  soundEnabled: true,
  desktopNotifications: true,
  autoRefresh: true,
  refreshInterval: 30000, // 30 seconds
  showToastNotifications: true,
  priorityFilter: ['urgent', 'high', 'medium', 'low'],
  requestTypeFilter: ['try_access', 'detection_access', 'premium_upgrade', 'signup_verification'],
  maxNotificationsToShow: 50
};

export const EnhancedNotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  
  // State
  const [notifications, setNotifications] = useState<NotificationRequest[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [settings, setSettings] = useState<NotificationSettings>(() => {
    const saved = localStorage.getItem('notification-settings');
    return saved ? { ...DEFAULT_SETTINGS, ...JSON.parse(saved) } : DEFAULT_SETTINGS;
  });
  const [stats, setStats] = useState<NotificationStats>({
    totalRequests: 0,
    pendingRequests: 0,
    approvedRequests: 0,
    rejectedRequests: 0,
    genuineUsers: 0,
    suspiciousUsers: 0,
    averageResponseTime: 0,
    requestsByType: {},
    requestsByHour: {},
    topRequestSources: []
  });

  // Refs
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  // Load notifications from localStorage on mount
  useEffect(() => {
    const savedNotifications = localStorage.getItem('notifications');
    if (savedNotifications) {
      try {
        const parsed = JSON.parse(savedNotifications);
        setNotifications(parsed);
      } catch (error) {
        console.error('Error loading saved notifications:', error);
      }
    }
  }, []);

  // Save notifications to localStorage whenever they change
  useEffect(() => {
    if (notifications.length > 0) {
      localStorage.setItem('notifications', JSON.stringify(notifications));
    }
  }, [notifications]);

  // Save settings to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('notification-settings', JSON.stringify(settings));
  }, [settings]);

  // Calculate stats whenever notifications change
  useEffect(() => {
    calculateStats();
  }, [notifications]);

  // WebSocket connection
  const connectWebSocket = useCallback(() => {
    if (!user || !isAuthenticated || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('Enhanced notification WebSocket connected');
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
        
        // Send authentication
        ws.send(JSON.stringify({
          type: 'auth',
          token: localStorage.getItem('ifake_access_token'),
          userId: user.id,
          role: user.roles?.[0] || 'user',
          context: 'notifications'
        }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onclose = (event) => {
        console.log('Enhanced notification WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
          reconnectAttemptsRef.current++;
          
          reconnectTimeoutRef.current = setTimeout(() => {
            if (user && isAuthenticated) {
              connectWebSocket();
            }
          }, delay);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
    }
  }, [user, isAuthenticated]);

  const disconnectWebSocket = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (refreshIntervalRef.current) {
      clearInterval(refreshIntervalRef.current);
      refreshIntervalRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
  }, []);

  // Initialize WebSocket connection
  useEffect(() => {
    if (user && isAuthenticated && user.roles?.includes('admin')) {
      connectWebSocket();
    }

    return () => {
      disconnectWebSocket();
    };
  }, [user, isAuthenticated, connectWebSocket, disconnectWebSocket]);

  // Auto-refresh setup
  useEffect(() => {
    if (settings.autoRefresh && settings.refreshInterval > 0) {
      refreshIntervalRef.current = setInterval(() => {
        refreshNotifications();
      }, settings.refreshInterval);
    }

    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, [settings.autoRefresh, settings.refreshInterval]);

  const handleWebSocketMessage = useCallback((data: any) => {
    switch (data.type) {
      case 'auth_success':
        console.log('Enhanced notification WebSocket authenticated');
        break;
        
      case 'new_request':
        addNotification(data.request);
        break;
        
      case 'request_updated':
        setNotifications(prev => 
          prev.map(notification => 
            notification.id === data.requestId 
              ? { 
                  ...notification, 
                  status: data.status, 
                  adminNotes: data.adminNotes,
                  updatedAt: new Date().toISOString()
                }
              : notification
          )
        );
        break;
        
      case 'bulk_update':
        setNotifications(prev => 
          prev.map(notification => 
            data.requestIds.includes(notification.id)
              ? { 
                  ...notification, 
                  status: data.status, 
                  adminNotes: data.adminNotes,
                  updatedAt: new Date().toISOString()
                }
              : notification
          )
        );
        break;
        
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  }, []);

  const addNotification = useCallback((notification: NotificationRequest) => {
    setNotifications(prev => {
      // Check if notification already exists
      const exists = prev.some(n => n.id === notification.id);
      if (exists) return prev;
      
      const newNotifications = [notification, ...prev];
      
      // Keep only the most recent notifications based on settings
      return newNotifications.slice(0, settings.maxNotificationsToShow);
    });

    // Show toast notification if enabled
    if (settings.showToastNotifications) {
      const priorityEmoji = {
        urgent: '🚨',
        high: '⚠️',
        medium: 'ℹ️',
        low: '📝'
      };

      toast.info(
        `${priorityEmoji[notification.priority]} New ${notification.requestType.replace('_', ' ')} Request`,
        {
          description: `${notification.userName} (${notification.userEmail})`,
          duration: 5000,
          action: {
            label: 'View',
            onClick: () => {
              // Could navigate to specific notification or admin dashboard
              console.log('Navigate to notification:', notification.id);
            }
          }
        }
      );
    }

    // Play sound if enabled
    if (settings.soundEnabled) {
      try {
        const audio = new Audio('/notification-sound.mp3');
        audio.volume = 0.3;
        audio.play().catch(() => {
          // Ignore errors if audio can't play
        });
      } catch (error) {
        // Ignore audio errors
      }
    }

    // Show desktop notification if enabled
    if (settings.desktopNotifications && 'Notification' in window) {
      if (Notification.permission === 'granted') {
        new Notification(`New ${notification.requestType.replace('_', ' ')} Request`, {
          body: `${notification.userName} is requesting access`,
          icon: '/favicon.ico',
          tag: notification.id
        });
      }
    }
  }, [settings]);

  const updateNotificationStatus = useCallback(async (id: string, status: 'approved' | 'rejected', adminNotes?: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: status === 'approved' ? 'approve_request' : 'reject_request',
        requestId: id,
        adminNotes,
        userId: user?.id,
        timestamp: new Date().toISOString()
      }));
    }

    // Update local state immediately for better UX
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === id 
          ? { 
              ...notification, 
              status, 
              adminNotes,
              updatedAt: new Date().toISOString()
            }
          : notification
      )
    );

    const notification = notifications.find(n => n.id === id);
    if (notification) {
      toast.success(`Request ${status} for ${notification.userName}`, {
        description: `${notification.requestType.replace('_', ' ')} access has been ${status}`
      });
    }
  }, [notifications, user?.id]);

  const bulkUpdateStatus = useCallback(async (ids: string[], status: 'approved' | 'rejected', adminNotes?: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'bulk_update_requests',
        requestIds: ids,
        status,
        adminNotes,
        userId: user?.id,
        timestamp: new Date().toISOString()
      }));
    }

    // Update local state immediately
    setNotifications(prev => 
      prev.map(notification => 
        ids.includes(notification.id)
          ? { 
              ...notification, 
              status, 
              adminNotes,
              updatedAt: new Date().toISOString()
            }
          : notification
      )
    );

    toast.success(`Bulk ${status} completed`, {
      description: `${ids.length} requests have been ${status}`
    });
  }, [user?.id]);

  const clearNotifications = useCallback((status?: 'pending' | 'approved' | 'rejected') => {
    if (status) {
      setNotifications(prev => prev.filter(n => n.status !== status));
    } else {
      setNotifications([]);
    }
    
    toast.info('Notifications cleared', {
      description: status ? `Cleared ${status} notifications` : 'Cleared all notifications'
    });
  }, []);

  const markAsRead = useCallback((id: string) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === id 
          ? { ...notification, status: notification.status as any } // Mark as read in future enhancement
          : notification
      )
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    // Implementation for marking all as read
    toast.info('All notifications marked as read');
  }, []);

  const updateSettings = useCallback((newSettings: Partial<NotificationSettings>) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
    toast.success('Settings updated');
  }, []);

  const getNotificationCount = useCallback((status?: 'pending' | 'approved' | 'rejected') => {
    if (status) {
      return notifications.filter(n => n.status === status).length;
    }
    return notifications.length;
  }, [notifications]);

  const getNotificationsByType = useCallback((type: string) => {
    return notifications.filter(n => n.requestType === type);
  }, [notifications]);

  const getNotificationsByPriority = useCallback((priority: string) => {
    return notifications.filter(n => n.priority === priority);
  }, [notifications]);

  const searchNotifications = useCallback((query: string) => {
    const lowercaseQuery = query.toLowerCase();
    return notifications.filter(n => 
      n.userName.toLowerCase().includes(lowercaseQuery) ||
      n.userEmail.toLowerCase().includes(lowercaseQuery) ||
      n.requestType.toLowerCase().includes(lowercaseQuery) ||
      n.message?.toLowerCase().includes(lowercaseQuery) ||
      n.adminNotes?.toLowerCase().includes(lowercaseQuery)
    );
  }, [notifications]);

  const refreshNotifications = useCallback(async () => {
    setIsLoading(true);
    try {
      // In a real implementation, this would fetch from the server
      // For now, we'll just simulate a refresh
      await new Promise(resolve => setTimeout(resolve, 500));
      
      toast.success('Notifications refreshed');
    } catch (error) {
      toast.error('Failed to refresh notifications');
      console.error('Error refreshing notifications:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const calculateStats = useCallback(() => {
    const stats: NotificationStats = {
      totalRequests: notifications.length,
      pendingRequests: notifications.filter(n => n.status === 'pending').length,
      approvedRequests: notifications.filter(n => n.status === 'approved').length,
      rejectedRequests: notifications.filter(n => n.status === 'rejected').length,
      genuineUsers: notifications.filter(n => n.isGenuine).length,
      suspiciousUsers: notifications.filter(n => !n.isGenuine).length,
      averageResponseTime: 0, // Calculate based on timestamps
      requestsByType: {},
      requestsByHour: {},
      topRequestSources: []
    };

    // Calculate requests by type
    notifications.forEach(n => {
      stats.requestsByType[n.requestType] = (stats.requestsByType[n.requestType] || 0) + 1;
    });

    // Calculate requests by hour
    notifications.forEach(n => {
      const hour = new Date(n.timestamp).getHours();
      stats.requestsByHour[hour.toString()] = (stats.requestsByHour[hour.toString()] || 0) + 1;
    });

    // Calculate top request sources
    const sourceCount: Record<string, number> = {};
    notifications.forEach(n => {
      sourceCount[n.source] = (sourceCount[n.source] || 0) + 1;
    });
    stats.topRequestSources = Object.entries(sourceCount)
      .map(([source, count]) => ({ source, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);

    setStats(stats);
  }, [notifications]);

  const pendingNotifications = notifications.filter(n => n.status === 'pending');

  const value: EnhancedNotificationContextType = {
    notifications,
    pendingNotifications,
    isConnected,
    isLoading,
    settings,
    stats,
    addNotification,
    updateNotificationStatus,
    bulkUpdateStatus,
    clearNotifications,
    markAsRead,
    markAllAsRead,
    updateSettings,
    getNotificationCount,
    getNotificationsByType,
    getNotificationsByPriority,
    searchNotifications,
    refreshNotifications,
    connectWebSocket,
    disconnectWebSocket
  };

  return (
    <EnhancedNotificationContext.Provider value={value}>
      {children}
    </EnhancedNotificationContext.Provider>
  );
};
