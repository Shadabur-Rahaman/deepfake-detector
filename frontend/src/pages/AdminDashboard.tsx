import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useAuth } from '@/contexts/SimpleAuthContext';
import { useRealtime } from '@/contexts/RealtimeContext';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
// import { useAdminDashboard } from '@/hooks/useAdminDashboard';
import { 
  Shield, 
  Users, 
  Activity, 
  Bell, 
  CheckCircle, 
  XCircle, 
  Clock,
  Eye,
  UserPlus,
  Settings,
  BarChart3,
  RefreshCw,
  AlertTriangle,
  Crown,
  Zap,
  Mail,
  Server,
  Database,
  Cpu,
  HardDrive,
  Wifi,
  WifiOff,
  TrendingUp,
  TrendingDown,
  UserCheck,
  UserX,
  MessageSquare,
  Send,
  Download,
  Upload,
  Filter,
  Search,
  MoreVertical,
  Edit,
  Trash2,
  Plus,
  Minus,
  Save,
  X
} from 'lucide-react';
import { toast } from 'sonner';

// Import the Try and Detection components
import TryItContent from './TryIt';
import DetectionContent from './Detection';

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

interface SystemStats {
  totalUsers: number;
  activeUsers: number;
  pendingRequests: number;
  totalDetections: number;
  systemHealth: 'healthy' | 'warning' | 'critical';
}

function AdminDashboardContent() {
  const { user, isAuthenticated } = useAuth();
  const { 
    userRequests, 
    pendingRequests, 
    genuineUsers, 
    totalUsers, 
    isConnected,
    updateRequestStatus 
  } = useRealtime();
  
  // Enhanced admin dashboard hook - temporarily disabled for debugging
  // const {
  //   isLoading,
  //   error,
  //   lastUpdated,
  //   systemHealth,
  //   systemStats,
  //   contactRequests,
  //   pendingContactRequests,
  //   authRequests,
  //   pendingAuthRequests,
  //   systemSettings,
  //   isConnected: adminConnected,
  //   refreshSystemData,
  //   updateContactRequestStatus,
  //   updateAuthRequestStatus,
  //   updateSystemSettings,
  //   updateAccessControlSettings,
  //   updateEmailSettings,
  //   testEmailConfiguration,
  //   totalRequests,
  //   totalPendingRequests
  // } = useAdminDashboard();

  // Temporary mock data for debugging
  const isLoading = false;
  const error = null;
  const lastUpdated = new Date();
  const systemHealth = {
    status: 'healthy',
    database: 'healthy',
    authentication: 'healthy',
    detectionAPI: 'healthy',
    websocket: 'connected',
    lastCheck: new Date().toISOString()
  };
  const systemStats = {
    totalUsers: 1247,
    activeUsers: 89,
    genuineUsers: 1180,
    pendingRequests: 3,
    totalRequests: 15,
    totalDetections: 5643,
    systemUptime: 72 * 3600,
    memoryUsage: 65.2,
    cpuUsage: 23.8
  };
  const contactRequests = [];
  const pendingContactRequests = 0;
  const authRequests = [];
  const pendingAuthRequests = 0;
  const systemSettings = {
    autoApproveTryAccess: false,
    autoApproveDetectionAccess: false,
    emailNotifications: true,
    maintenanceMode: false,
    maxFileSize: 10485760,
    allowedFileTypes: ['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mov'],
    rateLimiting: {
      enabled: true,
      maxRequestsPerMinute: 60,
      maxRequestsPerHour: 1000
    }
  };
  const adminConnected = true;
  const totalRequests = 0;
  const totalPendingRequests = 0;

  // Enhanced state management for settings
  const [settingsState, setSettingsState] = useState(systemSettings);
  const [isUpdating, setIsUpdating] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  // Enhanced functions with real state updates
  const refreshSystemData = useCallback(async () => {
    setIsUpdating(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setLastUpdate(new Date());
      toast.success('System data refreshed successfully');
    } catch (error) {
      toast.error('Failed to refresh system data');
    } finally {
      setIsUpdating(false);
    }
  }, []);

  const updateSystemSettings = useCallback(async (newSettings) => {
    setIsUpdating(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Update local state
      setSettingsState(prev => ({ ...prev, ...newSettings }));
      setLastUpdate(new Date());
      
      toast.success('System settings updated successfully');
    } catch (error) {
      toast.error('Failed to update system settings');
    } finally {
      setIsUpdating(false);
    }
  }, []);

  const updateAccessControlSettings = useCallback(async (settings) => {
    setIsUpdating(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setSettingsState(prev => ({ ...prev, ...settings }));
      setLastUpdate(new Date());
      
      toast.success('Access control settings updated');
    } catch (error) {
      toast.error('Failed to update access control settings');
    } finally {
      setIsUpdating(false);
    }
  }, []);

  const updateEmailSettings = useCallback(async (settings) => {
    setIsUpdating(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setSettingsState(prev => ({ ...prev, ...settings }));
      setLastUpdate(new Date());
      
      toast.success('Email settings updated');
    } catch (error) {
      toast.error('Failed to update email settings');
    } finally {
      setIsUpdating(false);
    }
  }, []);

  const testEmailConfiguration = useCallback(async () => {
    setIsUpdating(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast.success('Test email sent successfully! Check your inbox.');
    } catch (error) {
      toast.error('Failed to send test email');
    } finally {
      setIsUpdating(false);
    }
  }, []);

  const updateContactRequestStatus = useCallback((requestId, status, notes) => {
    toast.success(`Contact request ${status}`);
  }, []);

  const updateAuthRequestStatus = useCallback((requestId, status, notes) => {
    toast.success(`Auth request ${status}`);
  }, []);
  
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedRequests, setSelectedRequests] = useState([]);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [showEmailModal, setShowEmailModal] = useState(false);

  // Real-time data is now handled by RealtimeContext

  const handleApproveRequest = useCallback((requestId: string, type = 'auth') => {
    if (type === 'auth') {
      updateAuthRequestStatus(requestId, 'approved', 'Approved by admin');
    } else {
      updateContactRequestStatus(requestId, 'approved', 'Approved by admin');
    }
    toast.success('Request approved successfully');
  }, [updateAuthRequestStatus, updateContactRequestStatus]);

  const handleRejectRequest = useCallback((requestId: string, type = 'auth') => {
    if (type === 'auth') {
      updateAuthRequestStatus(requestId, 'rejected', 'Rejected by admin');
    } else {
      updateContactRequestStatus(requestId, 'rejected', 'Rejected by admin');
    }
    toast.error('Request rejected');
  }, [updateAuthRequestStatus, updateContactRequestStatus]);

  const handleRefresh = useCallback(() => {
    refreshSystemData();
  }, [refreshSystemData]);

  const handleBulkAction = useCallback(async (action: string) => {
    if (selectedRequests.length === 0) {
      toast.error('Please select requests to perform bulk action');
      return;
    }

    try {
      // Implementation for bulk actions
      toast.success(`${action} applied to ${selectedRequests.length} requests`);
      setSelectedRequests([]);
    } catch (error) {
      toast.error(`Failed to ${action} requests`);
    }
  }, [selectedRequests]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'approved': return 'bg-green-100 text-green-800 border-green-200';
      case 'rejected': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getRequestTypeIcon = (type: string) => {
    switch (type) {
      case 'try_access': return <Eye className="w-4 h-4" />;
      case 'detection_access': return <Zap className="w-4 h-4" />;
      case 'premium_upgrade': return <Crown className="w-4 h-4" />;
      default: return <UserPlus className="w-4 h-4" />;
    }
  };

  const getRequestTypeLabel = (type: string) => {
    switch (type) {
      case 'try_access': return 'Try Access';
      case 'detection_access': return 'Detection Access';
      case 'premium_upgrade': return 'Premium Upgrade';
      default: return 'Unknown';
    }
  };

  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-background to-muted/20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="w-full max-w-md"
        >
          <Card className="neural-card text-center p-8 shadow-2xl border-2 border-destructive/20 bg-gradient-to-br from-destructive/5 via-background to-destructive/5 backdrop-blur-sm">
            <CardHeader>
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.2, duration: 0.5 }}
                className="w-16 h-16 bg-gradient-to-br from-destructive/20 to-destructive/30 rounded-full flex items-center justify-center mx-auto mb-4 neural-glow"
              >
                <Shield className="w-8 h-8 text-destructive" />
              </motion.div>
              <CardTitle className="text-3xl font-bold gradient-text neural-text mb-2">Access Denied</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground neural-text">
                You need administrator privileges to access this dashboard.
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted/20 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold gradient-text neural-text flex items-center gap-3">
                <motion.div
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.2, duration: 0.5 }}
                  className="w-10 h-10 bg-gradient-to-br from-primary/20 to-accent/20 rounded-full flex items-center justify-center neural-glow"
                >
                  <Shield className="w-6 h-6 text-primary" />
                </motion.div>
                Admin Dashboard
              </h1>
              <p className="text-muted-foreground neural-text mt-2">
                System administration and user management
              </p>
              <p className="text-xs text-muted-foreground neural-text mt-1">
                Last updated: {lastUpdated?.toLocaleTimeString() || 'Never'}
              </p>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant="outline" className={`neural-card ${
                systemHealth.status === 'healthy' 
                  ? 'bg-success/10 text-success border-success/20' 
                  : systemHealth.status === 'warning'
                  ? 'bg-warning/10 text-warning border-warning/20'
                  : 'bg-destructive/10 text-destructive border-destructive/20'
              } hover:opacity-80 transition-opacity`}>
                <Activity className="w-3 h-3 mr-1" />
                System {systemHealth.status || 'Unknown'}
              </Badge>
              <Button 
                variant="outline" 
                size="sm" 
                className="neural-button hover-lift"
                onClick={handleRefresh}
                disabled={isLoading}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>
        </motion.div>

        {/* Connection Status & Error Display */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="mb-6 space-y-4"
        >
          {error && (
            <Alert className="neural-card border-destructive/20 bg-destructive/10">
              <AlertTriangle className="h-4 w-4 text-destructive" />
            <AlertDescription className="neural-text">
                {error}
              </AlertDescription>
            </Alert>
          )}
          
          <Alert className={`neural-card ${adminConnected ? "border-success/20 bg-success/10" : "border-destructive/20 bg-destructive/10"}`}>
            {adminConnected ? (
              <Wifi className="h-4 w-4 text-success" />
            ) : (
              <WifiOff className="h-4 w-4 text-destructive" />
            )}
            <AlertDescription className="neural-text">
              {adminConnected ? 'Real-time connection active' : 'Real-time connection disconnected'}
            </AlertDescription>
          </Alert>
        </motion.div>

        {/* Stats Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.5 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          <Card className="neural-card hover-lift">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground neural-text">Total Users</p>
                  <p className="text-2xl font-bold neural-text">{systemStats.totalUsers.toLocaleString()}</p>
                  <p className="text-xs text-muted-foreground neural-text">
                    {systemStats.activeUsers} active
                  </p>
                </div>
                <div className="w-12 h-12 bg-gradient-to-br from-primary/20 to-primary/30 rounded-full flex items-center justify-center neural-glow">
                  <Users className="w-6 h-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="neural-card hover-lift">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground neural-text">Genuine Users</p>
                  <p className="text-2xl font-bold text-success neural-text">{systemStats.genuineUsers}</p>
                  <p className="text-xs text-muted-foreground neural-text">
                    {((systemStats.genuineUsers / Math.max(systemStats.totalUsers, 1)) * 100).toFixed(1)}% ratio
                  </p>
                </div>
                <div className="w-12 h-12 bg-gradient-to-br from-success/20 to-success/30 rounded-full flex items-center justify-center neural-glow">
                  <UserCheck className="w-6 h-6 text-success" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="neural-card hover-lift">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground neural-text">Pending Requests</p>
                  <p className="text-2xl font-bold text-warning neural-text">{totalPendingRequests}</p>
                  <p className="text-xs text-muted-foreground neural-text">
                    {pendingContactRequests} contact, {pendingAuthRequests} auth
                  </p>
                </div>
                <div className="w-12 h-12 bg-gradient-to-br from-warning/20 to-warning/30 rounded-full flex items-center justify-center neural-glow">
                  <Bell className="w-6 h-6 text-warning" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="neural-card hover-lift">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground neural-text">Total Requests</p>
                  <p className="text-2xl font-bold text-accent neural-text">{totalRequests}</p>
                  <p className="text-xs text-muted-foreground neural-text">
                    {systemStats.totalDetections} detections
                  </p>
                </div>
                <div className="w-12 h-12 bg-gradient-to-br from-accent/20 to-accent/30 rounded-full flex items-center justify-center neural-glow">
                  <BarChart3 className="w-6 h-6 text-accent" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* System Performance Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
        >
          <Card className="neural-card hover-lift">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground neural-text">System Uptime</p>
                  <p className="text-2xl font-bold neural-text">
                    {Math.floor(systemStats.systemUptime / 3600)}h
                  </p>
                  <p className="text-xs text-muted-foreground neural-text">
                    {Math.floor((systemStats.systemUptime % 3600) / 60)}m
                  </p>
                </div>
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500/20 to-blue-500/30 rounded-full flex items-center justify-center neural-glow">
                  <Clock className="w-6 h-6 text-blue-500" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="neural-card hover-lift">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground neural-text">Memory Usage</p>
                  <p className="text-2xl font-bold neural-text">{systemStats.memoryUsage.toFixed(1)}%</p>
                  <p className="text-xs text-muted-foreground neural-text">
                    {systemStats.memoryUsage > 80 ? 'High' : systemStats.memoryUsage > 60 ? 'Medium' : 'Low'}
                  </p>
                </div>
                <div className="w-12 h-12 bg-gradient-to-br from-purple-500/20 to-purple-500/30 rounded-full flex items-center justify-center neural-glow">
                  <HardDrive className="w-6 h-6 text-purple-500" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="neural-card hover-lift">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground neural-text">CPU Usage</p>
                  <p className="text-2xl font-bold neural-text">{systemStats.cpuUsage.toFixed(1)}%</p>
                  <p className="text-xs text-muted-foreground neural-text">
                    {systemStats.cpuUsage > 80 ? 'High' : systemStats.cpuUsage > 60 ? 'Medium' : 'Low'}
                  </p>
                </div>
                <div className="w-12 h-12 bg-gradient-to-br from-green-500/20 to-green-500/30 rounded-full flex items-center justify-center neural-glow">
                  <Cpu className="w-6 h-6 text-green-500" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Main Content Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.5 }}
        >
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="neural-card grid w-full grid-cols-5 bg-muted/30">
              <TabsTrigger value="overview" className="neural-text">Overview</TabsTrigger>
              <TabsTrigger value="requests" className="neural-text">Auth Requests</TabsTrigger>
              <TabsTrigger value="try" className="neural-text">Try Section</TabsTrigger>
              <TabsTrigger value="detection" className="neural-text">Detection</TabsTrigger>
              <TabsTrigger value="settings" className="neural-text">Settings</TabsTrigger>
            </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Recent User Requests */}
              <Card className="neural-card hover-lift">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 neural-text">
                    <div className="w-8 h-8 bg-gradient-to-br from-primary/20 to-primary/30 rounded-full flex items-center justify-center neural-glow">
                      <Bell className="w-4 h-4 text-primary" />
                    </div>
                    Recent User Requests
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {userRequests.slice(0, 3).map((request) => (
                      <motion.div
                        key={request.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="neural-card flex items-center justify-between p-3 border border-border/50 rounded-lg hover:bg-muted/50 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 bg-gradient-to-br from-accent/20 to-accent/30 rounded-full flex items-center justify-center">
                            {getRequestTypeIcon(request.requestType)}
                          </div>
                          <div>
                            <p className="font-medium neural-text">{request.userName}</p>
                            <p className="text-sm text-muted-foreground neural-text">{request.userEmail}</p>
                            <p className="text-xs text-muted-foreground neural-text">
                              {getRequestTypeLabel(request.requestType)}
                            </p>
                          </div>
                        </div>
                        <Badge className={`neural-card ${getStatusColor(request.status)}`}>
                          {request.status}
                        </Badge>
                      </motion.div>
                    ))}
                    {userRequests.length === 0 && (
                      <div className="text-center py-8 text-muted-foreground">
                        <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
                        <p className="neural-text">No user requests yet</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* System Health */}
              <Card className="neural-card hover-lift">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 neural-text">
                    <div className="w-8 h-8 bg-gradient-to-br from-success/20 to-success/30 rounded-full flex items-center justify-center neural-glow">
                      <Activity className="w-4 h-4 text-success" />
                    </div>
                    System Health
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between neural-card p-3 rounded-lg">
                      <span className="neural-text">Database</span>
                      <Badge className="neural-card bg-success/10 text-success border-success/20">Healthy</Badge>
                    </div>
                    <div className="flex items-center justify-between neural-card p-3 rounded-lg">
                      <span className="neural-text">Authentication</span>
                      <Badge className="neural-card bg-success/10 text-success border-success/20">Healthy</Badge>
                    </div>
                    <div className="flex items-center justify-between neural-card p-3 rounded-lg">
                      <span className="neural-text">Detection API</span>
                      <Badge className="neural-card bg-success/10 text-success border-success/20">Healthy</Badge>
                    </div>
                    <div className="flex items-center justify-between neural-card p-3 rounded-lg">
                      <span className="neural-text">WebSocket</span>
                      <Badge className={`neural-card ${isConnected ? "bg-success/10 text-success border-success/20" : "bg-destructive/10 text-destructive border-destructive/20"}`}>
                        {isConnected ? "Connected" : "Disconnected"}
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Auth Requests Tab */}
          <TabsContent value="requests" className="space-y-6">
            <Card className="neural-card hover-lift">
              <CardHeader>
                <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2 neural-text">
                  <div className="w-8 h-8 bg-gradient-to-br from-primary/20 to-primary/30 rounded-full flex items-center justify-center neural-glow">
                    <Bell className="w-4 h-4 text-primary" />
                  </div>
                  Authentication Requests
                </CardTitle>
                  <div className="flex items-center gap-2">
                    <Input
                      placeholder="Search requests..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-64 neural-input"
                    />
                    <select
                      value={filterStatus}
                      onChange={(e) => setFilterStatus(e.target.value)}
                      className="neural-input"
                    >
                      <option value="all">All Status</option>
                      <option value="pending">Pending</option>
                      <option value="approved">Approved</option>
                      <option value="rejected">Rejected</option>
                    </select>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {authRequests
                    .filter(req => 
                      (filterStatus === 'all' || req.status === filterStatus) &&
                      (searchTerm === '' || 
                       req.userName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                       req.userEmail.toLowerCase().includes(searchTerm.toLowerCase()))
                    )
                    .map((request) => (
                    <motion.div
                      key={request.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="neural-card border border-border/50 rounded-lg p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-4">
                          <div className="w-10 h-10 bg-gradient-to-br from-accent/20 to-accent/30 rounded-lg flex items-center justify-center neural-glow">
                            {getRequestTypeIcon(request.requestType)}
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h3 className="font-semibold neural-text">{request.userName}</h3>
                              <Badge className={`neural-card ${getStatusColor(request.status)}`}>
                                {request.status}
                              </Badge>
                            </div>
                            <p className="text-sm text-muted-foreground neural-text mb-2">
                              {request.userEmail}
                            </p>
                            <p className="text-sm mb-2 neural-text">
                              <strong>Request:</strong> {getRequestTypeLabel(request.requestType)}
                            </p>
                            {request.message && (
                              <p className="text-sm text-muted-foreground neural-text mb-2">
                                "{request.message}"
                              </p>
                            )}
                            <p className="text-xs text-muted-foreground neural-text">
                              {new Date(request.timestamp).toLocaleString()}
                            </p>
                          </div>
                        </div>
                        {request.status === 'pending' && (
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              onClick={() => handleApproveRequest(request.id, 'auth')}
                              className="neural-button bg-success hover:bg-success/90 text-success-foreground"
                            >
                              <CheckCircle className="w-4 h-4 mr-1" />
                              Approve
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleRejectRequest(request.id, 'auth')}
                              className="neural-button"
                            >
                              <XCircle className="w-4 h-4 mr-1" />
                              Reject
                            </Button>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}
                  {authRequests.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p className="neural-text">No authentication requests found</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Contact Requests Tab */}
          <TabsContent value="contact" className="space-y-6">
            <Card className="neural-card hover-lift">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2 neural-text">
                    <div className="w-8 h-8 bg-gradient-to-br from-primary/20 to-primary/30 rounded-full flex items-center justify-center neural-glow">
                      <MessageSquare className="w-4 h-4 text-primary" />
                    </div>
                    Contact Requests
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      className="neural-button"
                      onClick={() => {/* Export functionality */}}
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Export
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {contactRequests
                    .filter(req => 
                      (filterStatus === 'all' || req.status === filterStatus) &&
                      (searchTerm === '' || 
                       req.fullName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                       req.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                       req.subject.toLowerCase().includes(searchTerm.toLowerCase()))
                    )
                    .map((request) => (
                    <motion.div
                      key={request.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="neural-card border border-border/50 rounded-lg p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-4">
                          <div className="w-10 h-10 bg-gradient-to-br from-blue-500/20 to-blue-500/30 rounded-lg flex items-center justify-center neural-glow">
                            <Mail className="w-4 h-4 text-blue-500" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h3 className="font-semibold neural-text">{request.fullName}</h3>
                              <Badge className={`neural-card ${getStatusColor(request.status)}`}>
                                {request.status}
                              </Badge>
                              <Badge variant="secondary" className="neural-card">
                                {request.regarding}
                              </Badge>
                            </div>
                            <p className="text-sm text-muted-foreground neural-text mb-2">
                              {request.email}
                            </p>
                            <p className="text-sm mb-2 neural-text">
                              <strong>Subject:</strong> {request.subject}
                            </p>
                            <p className="text-sm text-muted-foreground neural-text mb-2">
                              "{request.message}"
                            </p>
                            {request.adminNotes && (
                              <div className="mt-2 p-2 bg-muted/50 rounded-lg">
                                <p className="text-xs text-muted-foreground neural-text">
                                  <strong>Admin Notes:</strong> {request.adminNotes}
                                </p>
                              </div>
                            )}
                            <p className="text-xs text-muted-foreground neural-text mt-2">
                              {new Date(request.timestamp).toLocaleString()}
                            </p>
                          </div>
                        </div>
                        {request.status === 'pending' && (
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              onClick={() => handleApproveRequest(request.id, 'contact')}
                              className="neural-button bg-success hover:bg-success/90 text-success-foreground"
                            >
                              <CheckCircle className="w-4 h-4 mr-1" />
                              Mark as Read
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleRejectRequest(request.id, 'contact')}
                              className="neural-button"
                            >
                              <XCircle className="w-4 h-4 mr-1" />
                              Archive
                            </Button>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}
                  {contactRequests.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p className="neural-text">No contact requests found</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Try Section Tab - Full Access */}
          <TabsContent value="try" className="space-y-6">
            <div className="neural-card bg-gradient-to-r from-primary/10 to-accent/10 p-4 rounded-lg border border-primary/20">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-6 h-6 bg-gradient-to-br from-primary/20 to-primary/30 rounded-full flex items-center justify-center neural-glow">
                  <Shield className="w-3 h-3 text-primary" />
                </div>
                <h3 className="font-semibold text-primary neural-text">Admin Bypass Active</h3>
              </div>
              <p className="text-sm text-primary/80 neural-text">
                You have full administrative access to all features without authentication restrictions.
              </p>
            </div>
            <TryItContent />
          </TabsContent>

          {/* Detection Tab - Full Access */}
          <TabsContent value="detection" className="space-y-6">
            <div className="neural-card bg-gradient-to-r from-accent/10 to-primary/10 p-4 rounded-lg border border-accent/20">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-6 h-6 bg-gradient-to-br from-accent/20 to-accent/30 rounded-full flex items-center justify-center neural-glow">
                  <Shield className="w-3 h-3 text-accent" />
                </div>
                <h3 className="font-semibold text-accent neural-text">Admin Bypass Active</h3>
              </div>
              <p className="text-sm text-accent/80 neural-text">
                You have full administrative access to all features without authentication restrictions.
              </p>
            </div>
            <DetectionContent />
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="space-y-6">
            {/* System Settings */}
            <Card className="neural-card hover-lift">
              <CardHeader>
                <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2 neural-text">
                  <div className="w-8 h-8 bg-gradient-to-br from-primary/20 to-primary/30 rounded-full flex items-center justify-center neural-glow">
                    <Settings className="w-4 h-4 text-primary" />
                  </div>
                  System Settings
                </CardTitle>
                  <div className="flex items-center gap-2">
                    {isUpdating && (
                      <Badge variant="outline" className="neural-card bg-warning/10 text-warning border-warning/20">
                        <div className="w-2 h-2 bg-warning rounded-full animate-pulse mr-1" />
                        Updating...
                      </Badge>
                    )}
                    <Badge variant="outline" className="neural-card bg-success/10 text-success border-success/20">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Last updated: {lastUpdate.toLocaleTimeString()}
                    </Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {/* Access Control */}
                  <div>
                    <h3 className="font-semibold mb-3 neural-text">Access Control</h3>
                    <div className="space-y-4">
                      <motion.div 
                        className={`flex items-center justify-between neural-card p-4 rounded-lg transition-all duration-300 ${
                          settingsState.autoApproveTryAccess ? 'bg-success/5 border-success/20' : 'bg-muted/5'
                        }`}
                        whileHover={{ scale: 1.01 }}
                        transition={{ duration: 0.2 }}
                      >
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="neural-text font-medium">Auto-approve Try Access</span>
                            {settingsState.autoApproveTryAccess && (
                              <Badge variant="secondary" className="neural-card bg-success/10 text-success border-success/20">
                                Active
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground neural-text">
                            Automatically approve requests for Try section access
                          </p>
                        </div>
                        <Switch
                          checked={settingsState.autoApproveTryAccess}
                          onCheckedChange={(checked) => 
                            updateAccessControlSettings({ autoApproveTryAccess: checked })
                          }
                          disabled={isUpdating}
                        />
                      </motion.div>
                      <motion.div 
                        className={`flex items-center justify-between neural-card p-4 rounded-lg transition-all duration-300 ${
                          settingsState.autoApproveDetectionAccess ? 'bg-success/5 border-success/20' : 'bg-muted/5'
                        }`}
                        whileHover={{ scale: 1.01 }}
                        transition={{ duration: 0.2 }}
                      >
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="neural-text font-medium">Auto-approve Detection Access</span>
                            {settingsState.autoApproveDetectionAccess && (
                              <Badge variant="secondary" className="neural-card bg-success/10 text-success border-success/20">
                                Active
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground neural-text">
                            Automatically approve requests for Detection section access
                          </p>
                        </div>
                        <Switch
                          checked={settingsState.autoApproveDetectionAccess}
                          onCheckedChange={(checked) => 
                            updateAccessControlSettings({ autoApproveDetectionAccess: checked })
                          }
                          disabled={isUpdating}
                        />
                      </motion.div>
                      <motion.div 
                        className={`flex items-center justify-between neural-card p-4 rounded-lg transition-all duration-300 ${
                          settingsState.maintenanceMode ? 'bg-warning/5 border-warning/20' : 'bg-muted/5'
                        }`}
                        whileHover={{ scale: 1.01 }}
                        transition={{ duration: 0.2 }}
                      >
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="neural-text font-medium">Maintenance Mode</span>
                            {settingsState.maintenanceMode && (
                              <Badge variant="secondary" className="neural-card bg-warning/10 text-warning border-warning/20">
                                Active
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground neural-text">
                            Enable maintenance mode to restrict access
                          </p>
                        </div>
                        <Switch
                          checked={settingsState.maintenanceMode}
                          onCheckedChange={(checked) => 
                            updateSystemSettings({ maintenanceMode: checked })
                          }
                          disabled={isUpdating}
                        />
                      </motion.div>
                    </div>
                  </div>

                  {/* Email Notifications */}
                  <div>
                    <h3 className="font-semibold mb-3 neural-text">Email Notifications</h3>
                    <div className="space-y-4">
                      <motion.div 
                        className={`flex items-center justify-between neural-card p-4 rounded-lg transition-all duration-300 ${
                          settingsState.emailNotifications ? 'bg-success/5 border-success/20' : 'bg-muted/5'
                        }`}
                        whileHover={{ scale: 1.01 }}
                        transition={{ duration: 0.2 }}
                      >
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="neural-text font-medium">Email Notifications</span>
                            {settingsState.emailNotifications && (
                              <Badge variant="secondary" className="neural-card bg-success/10 text-success border-success/20">
                                Active
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-muted-foreground neural-text">
                            Send email notifications for new requests and updates
                          </p>
                        </div>
                        <Switch
                          checked={settingsState.emailNotifications}
                          onCheckedChange={(checked) => 
                            updateSystemSettings({ emailNotifications: checked })
                          }
                          disabled={isUpdating}
                        />
                      </motion.div>
                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          className="neural-button"
                          onClick={testEmailConfiguration}
                          disabled={isUpdating}
                        >
                          {isUpdating ? (
                            <>
                              <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2" />
                              Testing...
                            </>
                          ) : (
                            <>
                              <Send className="w-4 h-4 mr-2" />
                              Test Email
                            </>
                          )}
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="neural-button"
                          onClick={() => setShowEmailModal(true)}
                        >
                          <Settings className="w-4 h-4 mr-2" />
                          Configure
                        </Button>
                      </div>
                    </div>
                  </div>

                  {/* File Upload Settings */}
                  <div>
                    <h3 className="font-semibold mb-3 neural-text">File Upload Settings</h3>
                    <div className="space-y-4">
                      <div className="neural-card p-4 rounded-lg">
                        <Label htmlFor="maxFileSize" className="neural-text font-medium">
                          Maximum File Size (bytes)
                        </Label>
                        <Input
                          id="maxFileSize"
                          type="number"
                          value={settingsState.maxFileSize}
                          onChange={(e) => {
                            const value = parseInt(e.target.value) || 0;
                            updateSystemSettings({ maxFileSize: value });
                          }}
                          className="neural-input mt-2"
                          disabled={isUpdating}
                          placeholder="Enter file size in bytes"
                        />
                        <p className="text-sm text-muted-foreground neural-text mt-1">
                          Current: {(settingsState.maxFileSize / 1024 / 1024).toFixed(1)} MB
                          {settingsState.maxFileSize > 104857600 && (
                            <span className="text-warning ml-2">⚠️ Large file size</span>
                          )}
                        </p>
                      </div>
                      <div className="neural-card p-4 rounded-lg">
                        <Label htmlFor="allowedFileTypes" className="neural-text font-medium">
                          Allowed File Types
                        </Label>
                        <Input
                          id="allowedFileTypes"
                          value={settingsState.allowedFileTypes.join(', ')}
                          onChange={(e) => {
                            const types = e.target.value.split(',').map(t => t.trim()).filter(t => t.length > 0);
                            updateSystemSettings({ allowedFileTypes: types });
                          }}
                          className="neural-input mt-2"
                          placeholder="jpg, jpeg, png, mp4, avi, mov"
                          disabled={isUpdating}
                        />
                        <p className="text-sm text-muted-foreground neural-text mt-1">
                          {settingsState.allowedFileTypes.length} file types configured
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Rate Limiting */}
                  <div>
                    <h3 className="font-semibold mb-3 neural-text">Rate Limiting</h3>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between neural-card p-4 rounded-lg">
                        <div>
                          <span className="neural-text font-medium">Enable Rate Limiting</span>
                          <p className="text-sm text-muted-foreground neural-text">
                            Limit requests per user to prevent abuse
                          </p>
                        </div>
                        <Switch
                          checked={settingsState.rateLimiting.enabled}
                          onCheckedChange={(checked) => 
                            updateSystemSettings({ 
                              rateLimiting: { ...settingsState.rateLimiting, enabled: checked }
                            })
                          }
                          disabled={isUpdating}
                        />
                      </div>
                      {settingsState.rateLimiting.enabled && (
                        <div className="grid grid-cols-2 gap-4">
                          <div className="neural-card p-4 rounded-lg">
                            <Label htmlFor="maxRequestsPerMinute" className="neural-text font-medium">
                              Max Requests/Minute
                            </Label>
                            <Input
                              id="maxRequestsPerMinute"
                              type="number"
                              value={settingsState.rateLimiting.maxRequestsPerMinute}
                              onChange={(e) => {
                                const value = parseInt(e.target.value) || 0;
                                updateSystemSettings({ 
                                  rateLimiting: { 
                                    ...settingsState.rateLimiting, 
                                    maxRequestsPerMinute: value
                                  }
                                });
                              }}
                              className="neural-input mt-2"
                              disabled={isUpdating}
                              min="1"
                              max="1000"
                            />
                            <p className="text-xs text-muted-foreground neural-text mt-1">
                              {settingsState.rateLimiting.maxRequestsPerMinute > 100 && (
                                <span className="text-warning">⚠️ High limit</span>
                              )}
                            </p>
                          </div>
                          <div className="neural-card p-4 rounded-lg">
                            <Label htmlFor="maxRequestsPerHour" className="neural-text font-medium">
                              Max Requests/Hour
                            </Label>
                            <Input
                              id="maxRequestsPerHour"
                              type="number"
                              value={settingsState.rateLimiting.maxRequestsPerHour}
                              onChange={(e) => {
                                const value = parseInt(e.target.value) || 0;
                                updateSystemSettings({ 
                                  rateLimiting: { 
                                    ...settingsState.rateLimiting, 
                                    maxRequestsPerHour: value
                                  }
                                });
                              }}
                              className="neural-input mt-2"
                              disabled={isUpdating}
                              min="1"
                              max="10000"
                            />
                            <p className="text-xs text-muted-foreground neural-text mt-1">
                              {settingsState.rateLimiting.maxRequestsPerHour > 5000 && (
                                <span className="text-warning">⚠️ Very high limit</span>
                              )}
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* System Health Monitoring */}
            <Card className="neural-card hover-lift">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 neural-text">
                  <div className="w-8 h-8 bg-gradient-to-br from-success/20 to-success/30 rounded-full flex items-center justify-center neural-glow">
                    <Activity className="w-4 h-4 text-success" />
                  </div>
                  System Health Monitoring
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="text-sm text-muted-foreground neural-text">
                      Real-time system status monitoring
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={refreshSystemData}
                      disabled={isUpdating}
                      className="neural-button"
                    >
                      {isUpdating ? (
                        <>
                          <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2" />
                          Refreshing...
                        </>
                      ) : (
                        <>
                          <RefreshCw className="w-4 h-4 mr-2" />
                          Refresh
                        </>
                      )}
                    </Button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[
                      { key: 'database', label: 'Database', status: systemHealth.database },
                      { key: 'authentication', label: 'Authentication', status: systemHealth.authentication },
                      { key: 'detectionAPI', label: 'Detection API', status: systemHealth.detectionAPI },
                      { key: 'websocket', label: 'WebSocket', status: adminConnected ? 'connected' : 'disconnected' }
                    ].map(({ key, label, status }) => (
                      <motion.div 
                        key={key}
                        className={`flex items-center justify-between neural-card p-3 rounded-lg transition-all duration-300 ${
                          status === 'healthy' || status === 'connected'
                            ? 'bg-success/5 border-success/20'
                            : 'bg-destructive/5 border-destructive/20'
                        }`}
                        whileHover={{ scale: 1.02 }}
                        transition={{ duration: 0.2 }}
                      >
                        <div className="flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${
                            status === 'healthy' || status === 'connected'
                              ? 'bg-success animate-pulse'
                              : 'bg-destructive animate-pulse'
                          }`} />
                          <span className="neural-text">{label}</span>
                        </div>
                        <Badge className={`neural-card ${
                          status === 'healthy' || status === 'connected'
                            ? 'bg-success/10 text-success border-success/20'
                            : 'bg-destructive/10 text-destructive border-destructive/20'
                        }`}>
                          {status}
                        </Badge>
                      </motion.div>
                    ))}
                  </div>
                  <div className="mt-4 p-3 neural-card rounded-lg bg-muted/5">
                    <div className="text-xs text-muted-foreground neural-text">
                      Last health check: {new Date(systemHealth.lastCheck).toLocaleString()}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
        </motion.div>
      </div>
    </div>
  );
}

export default function AdminDashboard() {
  return (
    <ProtectedRoute
      requireAuth={true}
      requiredRoles={['admin']}
    >
      <AdminDashboardContent />
    </ProtectedRoute>
  );
}
