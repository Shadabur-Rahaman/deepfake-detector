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
import { useAdminDashboard } from '@/hooks/useAdminDashboard';
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

  // Enhanced admin dashboard hook
  const {
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
    isConnected: adminConnected,
    refreshSystemData,
    updateContactRequestStatus,
    updateAuthRequestStatus,
    updateSystemSettings,
    updateAccessControlSettings,
    updateEmailSettings,
    testEmailConfiguration,
    totalRequests,
    totalPendingRequests
  } = useAdminDashboard();
  
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
            </div>
            <div className="flex items-center gap-4">
              <Badge variant="outline" className="neural-card bg-success/10 text-success border-success/20 hover:bg-success/20 transition-colors">
                <Activity className="w-3 h-3 mr-1" />
                System Healthy
              </Badge>
              <Button variant="outline" size="sm" className="neural-button hover-lift">
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </motion.div>

        {/* Connection Status */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="mb-6"
        >
          <Alert className={`neural-card ${isConnected ? "border-success/20 bg-success/10" : "border-destructive/20 bg-destructive/10"}`}>
            <Activity className={`h-4 w-4 ${isConnected ? 'text-success' : 'text-destructive'}`} />
            <AlertDescription className="neural-text">
              {isConnected ? 'Real-time connection active' : 'Real-time connection disconnected'}
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
                  <p className="text-2xl font-bold neural-text">{totalUsers.toLocaleString()}</p>
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
                  <p className="text-2xl font-bold text-success neural-text">{genuineUsers}</p>
                </div>
                <div className="w-12 h-12 bg-gradient-to-br from-success/20 to-success/30 rounded-full flex items-center justify-center neural-glow">
                  <Activity className="w-6 h-6 text-success" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="neural-card hover-lift">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground neural-text">Pending Requests</p>
                  <p className="text-2xl font-bold text-warning neural-text">{pendingRequests.length}</p>
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
                  <p className="text-2xl font-bold text-accent neural-text">{userRequests.length}</p>
                </div>
                <div className="w-12 h-12 bg-gradient-to-br from-accent/20 to-accent/30 rounded-full flex items-center justify-center neural-glow">
                  <BarChart3 className="w-6 h-6 text-accent" />
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
                <CardTitle className="flex items-center gap-2 neural-text">
                  <div className="w-8 h-8 bg-gradient-to-br from-primary/20 to-primary/30 rounded-full flex items-center justify-center neural-glow">
                    <Bell className="w-4 h-4 text-primary" />
                  </div>
                  Authentication Requests
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {userRequests.map((request) => (
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
                              onClick={() => handleApproveRequest(request.id)}
                              className="neural-button bg-success hover:bg-success/90 text-success-foreground"
                            >
                              <CheckCircle className="w-4 h-4 mr-1" />
                              Approve
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleRejectRequest(request.id)}
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
            <Card className="neural-card hover-lift">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 neural-text">
                  <div className="w-8 h-8 bg-gradient-to-br from-primary/20 to-primary/30 rounded-full flex items-center justify-center neural-glow">
                    <Settings className="w-4 h-4 text-primary" />
                  </div>
                  System Settings
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div>
                    <h3 className="font-semibold mb-3 neural-text">Access Control</h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between neural-card p-3 rounded-lg">
                        <span className="neural-text">Auto-approve Try Access</span>
                        <Button variant="outline" size="sm" className="neural-button">Configure</Button>
                      </div>
                      <div className="flex items-center justify-between neural-card p-3 rounded-lg">
                        <span className="neural-text">Auto-approve Detection Access</span>
                        <Button variant="outline" size="sm" className="neural-button">Configure</Button>
                      </div>
                      <div className="flex items-center justify-between neural-card p-3 rounded-lg">
                        <span className="neural-text">Email Notifications</span>
                        <Button variant="outline" size="sm" className="neural-button">Configure</Button>
                      </div>
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
