/**
 * Custom hook for Admin Dashboard functionality
 * Provides real-time data, system monitoring, and admin operations
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '@/contexts/SimpleAuthContext';
import adminService from '@/services/adminService';
import { toast } from 'sonner';

export const useAdminDashboard = () => {
  const { user, isAuthenticated } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  // System Data
  const [systemHealth, setSystemHealth] = useState({
    status: 'unknown',
    database: 'unknown',
    authentication: 'unknown',
    detectionAPI: 'unknown',
    websocket: 'disconnected',
    lastCheck: null
  });

  const [systemStats, setSystemStats] = useState({
    totalUsers: 0,
    activeUsers: 0,
    genuineUsers: 0,
    pendingRequests: 0,
    totalRequests: 0,
    totalDetections: 0,
    systemUptime: 0,
    memoryUsage: 0,
    cpuUsage: 0
  });

  // Contact Requests
  const [contactRequests, setContactRequests] = useState([]);
  const [pendingContactRequests, setPendingContactRequests] = useState(0);

  // Auth Requests
  const [authRequests, setAuthRequests] = useState([]);
  const [pendingAuthRequests, setPendingAuthRequests] = useState(0);

  // Settings
  const [systemSettings, setSystemSettings] = useState({
    autoApproveTryAccess: false,
    autoApproveDetectionAccess: false,
    emailNotifications: true,
    maintenanceMode: false,
    maxFileSize: 10485760, // 10MB
    allowedFileTypes: ['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov'],
    rateLimiting: {
      enabled: true,
      maxRequestsPerMinute: 60,
      maxRequestsPerHour: 1000
    }
  });

  // Connection status
  const [isConnected, setIsConnected] = useState(false);
  const [connectionAttempts, setConnectionAttempts] = useState(0);

  // Refs for cleanup
  const refreshIntervalRef = useRef(null);
  const healthCheckIntervalRef = useRef(null);

  // Initialize dashboard data
  const initializeDashboard = useCallback(async () => {
    if (!isAuthenticated || !user) return;

    setIsLoading(true);
    setError(null);

    try {
      // Fetch all dashboard data in parallel
      const [
        healthData,
        statsData,
        contactData,
        authData,
        settingsData
      ] = await Promise.all([
        adminService.getSystemHealth(),
        adminService.getSystemStats(),
        adminService.getContactRequests(),
        adminService.getAuthRequests(),
        adminService.getSystemSettings()
      ]);

      // Update state with fetched data
      setSystemHealth(healthData);
      setSystemStats(statsData);
      setContactRequests(contactData.requests || []);
      setPendingContactRequests(contactData.pending || 0);
      setAuthRequests(authData.requests || []);
      setPendingAuthRequests(authData.pending || 0);
      setSystemSettings(settingsData);

      setLastUpdated(new Date());
    } catch (err) {
      console.error('Failed to initialize dashboard:', err);
      setError(err.message);
      toast.error('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated, user]);

  // Refresh system data
  const refreshSystemData = useCallback(async () => {
    try {
      const { health, stats } = await adminService.refreshSystemData();
      setSystemHealth(health);
      setSystemStats(stats);
      setLastUpdated(new Date());
      toast.success('System data refreshed');
    } catch (err) {
      console.error('Failed to refresh system data:', err);
      toast.error('Failed to refresh system data');
    }
  }, []);

  // Update contact request status
  const updateContactRequestStatus = useCallback(async (requestId, status, adminNotes) => {
    try {
      await adminService.updateContactRequest(requestId, status, adminNotes);
      
      // Update local state
      setContactRequests(prev => 
        prev.map(req => 
          req.id === requestId 
            ? { ...req, status, adminNotes, updatedAt: new Date().toISOString() }
            : req
        )
      );

      // Update pending count
      setPendingContactRequests(prev => 
        status === 'pending' ? prev + 1 : Math.max(0, prev - 1)
      );

      toast.success(`Contact request ${status}`);
    } catch (err) {
      console.error('Failed to update contact request:', err);
      toast.error('Failed to update contact request');
    }
  }, []);

  // Update auth request status
  const updateAuthRequestStatus = useCallback(async (requestId, status, adminNotes) => {
    try {
      if (status === 'approved') {
        await adminService.approveAuthRequest(requestId, adminNotes);
      } else {
        await adminService.rejectAuthRequest(requestId, adminNotes);
      }

      // Update local state
      setAuthRequests(prev => 
        prev.map(req => 
          req.id === requestId 
            ? { ...req, status, adminNotes, updatedAt: new Date().toISOString() }
            : req
        )
      );

      // Update pending count
      setPendingAuthRequests(prev => Math.max(0, prev - 1));

      toast.success(`Auth request ${status}`);
    } catch (err) {
      console.error('Failed to update auth request:', err);
      toast.error('Failed to update auth request');
    }
  }, []);

  // Update system settings
  const updateSystemSettings = useCallback(async (newSettings) => {
    try {
      await adminService.updateSystemSettings(newSettings);
      setSystemSettings(prev => ({ ...prev, ...newSettings }));
      toast.success('System settings updated');
    } catch (err) {
      console.error('Failed to update system settings:', err);
      toast.error('Failed to update system settings');
    }
  }, []);

  // Update access control settings
  const updateAccessControlSettings = useCallback(async (settings) => {
    try {
      await adminService.updateAccessControlSettings(settings);
      setSystemSettings(prev => ({ ...prev, ...settings }));
      toast.success('Access control settings updated');
    } catch (err) {
      console.error('Failed to update access control settings:', err);
      toast.error('Failed to update access control settings');
    }
  }, []);

  // Update email settings
  const updateEmailSettings = useCallback(async (settings) => {
    try {
      await adminService.updateEmailSettings(settings);
      toast.success('Email settings updated');
    } catch (err) {
      console.error('Failed to update email settings:', err);
      toast.error('Failed to update email settings');
    }
  }, []);

  // Test email configuration
  const testEmailConfiguration = useCallback(async () => {
    try {
      await adminService.testEmailConfiguration();
      toast.success('Test email sent successfully');
    } catch (err) {
      console.error('Failed to send test email:', err);
      toast.error('Failed to send test email');
    }
  }, []);

  // WebSocket event handlers
  useEffect(() => {
    if (!isAuthenticated || !user) return;

    const handleAuthSuccess = () => {
      setIsConnected(true);
      setConnectionAttempts(0);
    };

    const handleStatsUpdate = (stats) => {
      setSystemStats(prev => ({ ...prev, ...stats }));
      setLastUpdated(new Date());
    };

    const handleHealthUpdate = (health) => {
      setSystemHealth(prev => ({ ...prev, ...health }));
      setLastUpdated(new Date());
    };

    const handleNewContact = (request) => {
      setContactRequests(prev => [request, ...prev]);
      setPendingContactRequests(prev => prev + 1);
      toast.info('New contact request received');
    };

    const handleNewAuthRequest = (request) => {
      setAuthRequests(prev => [request, ...prev]);
      setPendingAuthRequests(prev => prev + 1);
      toast.info('New auth request received');
    };

    const handleRequestUpdated = (data) => {
      if (data.type === 'contact') {
        setContactRequests(prev => 
          prev.map(req => 
            req.id === data.requestId 
              ? { ...req, status: data.status, adminNotes: data.adminNotes }
              : req
          )
        );
      } else if (data.type === 'auth') {
        setAuthRequests(prev => 
          prev.map(req => 
            req.id === data.requestId 
              ? { ...req, status: data.status, adminNotes: data.adminNotes }
              : req
          )
        );
      }
    };

    // Register event listeners
    adminService.on('auth_success', handleAuthSuccess);
    adminService.on('stats_update', handleStatsUpdate);
    adminService.on('health_update', handleHealthUpdate);
    adminService.on('new_contact', handleNewContact);
    adminService.on('new_auth_request', handleNewAuthRequest);
    adminService.on('request_updated', handleRequestUpdated);

    // Connect WebSocket
    adminService.connectWebSocket();

    return () => {
      // Cleanup event listeners
      adminService.off('auth_success', handleAuthSuccess);
      adminService.off('stats_update', handleStatsUpdate);
      adminService.off('health_update', handleHealthUpdate);
      adminService.off('new_contact', handleNewContact);
      adminService.off('new_auth_request', handleNewAuthRequest);
      adminService.off('request_updated', handleRequestUpdated);
    };
  }, [isAuthenticated, user]);

  // Auto-refresh system data
  useEffect(() => {
    if (!isAuthenticated) return;

    // Refresh every 30 seconds
    refreshIntervalRef.current = setInterval(() => {
      refreshSystemData();
    }, 30000);

    // Health check every 10 seconds
    healthCheckIntervalRef.current = setInterval(async () => {
      try {
        const health = await adminService.getSystemHealth();
        setSystemHealth(health);
      } catch (err) {
        console.warn('Health check failed:', err);
      }
    }, 10000);

    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
      if (healthCheckIntervalRef.current) {
        clearInterval(healthCheckIntervalRef.current);
      }
    };
  }, [isAuthenticated, refreshSystemData]);

  // Initialize dashboard on mount
  useEffect(() => {
    initializeDashboard();
  }, [initializeDashboard]);

  return {
    // State
    isLoading,
    error,
    lastUpdated,
    systemHealth,
    systemStats,
    contactRequests,
    pendingContactRequests,
    authRequests,
    pendingAuthRequests,
    systemSettings,
    isConnected,
    connectionAttempts,

    // Actions
    refreshSystemData,
    updateContactRequestStatus,
    updateAuthRequestStatus,
    updateSystemSettings,
    updateAccessControlSettings,
    updateEmailSettings,
    testEmailConfiguration,
    initializeDashboard,

    // Computed values
    totalRequests: contactRequests.length + authRequests.length,
    totalPendingRequests: pendingContactRequests + pendingAuthRequests
  };
};
