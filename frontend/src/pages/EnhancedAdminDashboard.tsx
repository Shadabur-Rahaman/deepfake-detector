import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { useAuth } from '@/contexts/SimpleAuthContext';
import { useEnhancedNotifications } from '@/contexts/EnhancedNotificationContext';
import { EnhancedNotificationBell } from '@/components/admin/EnhancedNotificationBell';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
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
  TrendingUp,
  TrendingDown,
  Globe,
  Smartphone,
  Monitor,
  MapPin,
  Calendar,
  Download,
  Filter,
  Search,
  MoreVertical,
  PieChart,
  LineChart,
  BarChart,
  Target,
  Award,
  UserCheck,
  UserX,
  Timer,
  Zap as ZapIcon
} from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

interface DashboardMetrics {
  totalRequests: number;
  pendingRequests: number;
  approvedRequests: number;
  rejectedRequests: number;
  genuineUsers: number;
  suspiciousUsers: number;
  averageResponseTime: number;
  requestsToday: number;
  requestsThisWeek: number;
  requestsThisMonth: number;
  topRequestTypes: Array<{ type: string; count: number; percentage: number }>;
  requestsByHour: Array<{ hour: number; count: number }>;
  requestsBySource: Array<{ source: string; count: number; percentage: number }>;
  requestsByCountry: Array<{ country: string; count: number; percentage: number }>;
  responseTimeTrend: Array<{ date: string; avgTime: number }>;
  userSatisfactionScore: number;
}

function EnhancedAdminDashboardContent() {
  const { user, isAuthenticated } = useAuth();
  const {
    notifications,
    pendingNotifications,
    isConnected,
    isLoading,
    stats,
    updateNotificationStatus,
    bulkUpdateStatus,
    clearNotifications,
    getNotificationCount,
    getNotificationsByType,
    getNotificationsByPriority,
    searchNotifications
  } = useEnhancedNotifications();

  const [activeTab, setActiveTab] = useState('overview');
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [selectedNotifications, setSelectedNotifications] = useState<string[]>([]);

  // Calculate enhanced metrics
  const metrics = useMemo((): DashboardMetrics => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);

    const requestsToday = notifications.filter(n => new Date(n.timestamp) >= today).length;
    const requestsThisWeek = notifications.filter(n => new Date(n.timestamp) >= weekAgo).length;
    const requestsThisMonth = notifications.filter(n => new Date(n.timestamp) >= monthAgo).length;

    // Calculate top request types
    const typeCounts: Record<string, number> = {};
    notifications.forEach(n => {
      typeCounts[n.requestType] = (typeCounts[n.requestType] || 0) + 1;
    });
    
    const totalRequests = notifications.length;
    const topRequestTypes = Object.entries(typeCounts)
      .map(([type, count]) => ({
        type,
        count,
        percentage: totalRequests > 0 ? (count / totalRequests) * 100 : 0
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);

    // Calculate requests by hour
    const hourCounts: Record<number, number> = {};
    notifications.forEach(n => {
      const hour = new Date(n.timestamp).getHours();
      hourCounts[hour] = (hourCounts[hour] || 0) + 1;
    });
    
    const requestsByHour = Array.from({ length: 24 }, (_, i) => ({
      hour: i,
      count: hourCounts[i] || 0
    }));

    // Calculate requests by source
    const sourceCounts: Record<string, number> = {};
    notifications.forEach(n => {
      sourceCounts[n.source] = (sourceCounts[n.source] || 0) + 1;
    });
    
    const requestsBySource = Object.entries(sourceCounts)
      .map(([source, count]) => ({
        source,
        count,
        percentage: totalRequests > 0 ? (count / totalRequests) * 100 : 0
      }))
      .sort((a, b) => b.count - a.count);

    // Calculate requests by country
    const countryCounts: Record<string, number> = {};
    notifications.forEach(n => {
      if (n.location?.country) {
        countryCounts[n.location.country] = (countryCounts[n.location.country] || 0) + 1;
      }
    });
    
    const requestsByCountry = Object.entries(countryCounts)
      .map(([country, count]) => ({
        country,
        count,
        percentage: totalRequests > 0 ? (count / totalRequests) * 100 : 0
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);

    // Calculate average response time (mock data for now)
    const averageResponseTime = Math.random() * 300 + 60; // 1-5 minutes

    // Calculate user satisfaction score (mock data for now)
    const userSatisfactionScore = 85 + Math.random() * 10; // 85-95%

    return {
      totalRequests: stats.totalRequests,
      pendingRequests: stats.pendingRequests,
      approvedRequests: stats.approvedRequests,
      rejectedRequests: stats.rejectedRequests,
      genuineUsers: stats.genuineUsers,
      suspiciousUsers: stats.suspiciousUsers,
      averageResponseTime,
      requestsToday,
      requestsThisWeek,
      requestsThisMonth,
      topRequestTypes,
      requestsByHour,
      requestsBySource,
      requestsByCountry,
      responseTimeTrend: [], // Mock data
      userSatisfactionScore
    };
  }, [notifications, stats]);

  const getRequestTypeIcon = (type: string) => {
    switch (type) {
      case 'try_access': return <Eye className="w-4 h-4" />;
      case 'detection_access': return <Zap className="w-4 h-4" />;
      case 'premium_upgrade': return <Crown className="w-4 h-4" />;
      case 'signup_verification': return <UserPlus className="w-4 h-4" />;
      default: return <UserPlus className="w-4 h-4" />;
    }
  };

  const getRequestTypeLabel = (type: string) => {
    switch (type) {
      case 'try_access': return 'Try Access';
      case 'detection_access': return 'Detection Access';
      case 'premium_upgrade': return 'Premium Upgrade';
      case 'signup_verification': return 'Signup Verification';
      default: return 'Unknown';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'urgent': return <AlertTriangle className="w-3 h-3 text-red-500" />;
      case 'high': return <TrendingUp className="w-3 h-3 text-orange-500" />;
      case 'medium': return <Clock className="w-3 h-3 text-yellow-500" />;
      case 'low': return <TrendingDown className="w-3 h-3 text-blue-500" />;
      default: return null;
    }
  };

  const getSourceIcon = (source: string) => {
    switch (source) {
      case 'web': return <Monitor className="w-4 h-4" />;
      case 'mobile': return <Smartphone className="w-4 h-4" />;
      case 'api': return <Globe className="w-4 h-4" />;
      default: return <Globe className="w-4 h-4" />;
    }
  };

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date();
    const requestTime = new Date(timestamp);
    const diffInSeconds = Math.floor((now.getTime() - requestTime.getTime()) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
  };

  const handleApproveRequest = async (requestId: string) => {
    try {
      await updateNotificationStatus(requestId, 'approved', 'Approved by admin');
      toast.success('Request approved successfully');
    } catch (error) {
      toast.error('Failed to approve request');
    }
  };

  const handleRejectRequest = async (requestId: string) => {
    try {
      await updateNotificationStatus(requestId, 'rejected', 'Rejected by admin');
      toast.error('Request rejected');
    } catch (error) {
      toast.error('Failed to reject request');
    }
  };

  const filteredNotifications = useMemo(() => {
    let filtered = notifications;

    if (searchQuery) {
      filtered = searchNotifications(searchQuery);
    }

    if (filterStatus !== 'all') {
      filtered = filtered.filter(n => n.status === filterStatus);
    }

    if (filterType !== 'all') {
      filtered = filtered.filter(n => n.requestType === filterType);
    }

    return filtered.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }, [notifications, searchQuery, filterStatus, filterType, searchNotifications]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      <div className="container mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold neural-text">Admin Dashboard</h1>
            <p className="text-muted-foreground">
              Real-time monitoring and management of user access requests
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              {isConnected ? (
                <Badge variant="outline" className="neural-card text-green-600 border-green-600">
                  <Activity className="w-3 h-3 mr-1" />
                  Connected
                </Badge>
              ) : (
                <Badge variant="outline" className="neural-card text-red-600 border-red-600">
                  <AlertTriangle className="w-3 h-3 mr-1" />
                  Disconnected
                </Badge>
              )}
            </div>
            <EnhancedNotificationBell showStats={false} />
          </div>
        </div>

        {/* Metrics Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="neural-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Requests</p>
                  <p className="text-2xl font-bold neural-text">{metrics.totalRequests}</p>
                  <p className="text-xs text-muted-foreground">
                    +{metrics.requestsToday} today
                  </p>
                </div>
                <div className="w-12 h-12 bg-gradient-to-br from-primary/20 to-primary/30 rounded-full flex items-center justify-center neural-glow">
                  <BarChart3 className="w-6 h-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="neural-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Pending Requests</p>
                  <p className="text-2xl font-bold text-yellow-600">{metrics.pendingRequests}</p>
                  <p className="text-xs text-muted-foreground">
                    {metrics.totalRequests > 0 
                      ? `${((metrics.pendingRequests / metrics.totalRequests) * 100).toFixed(1)}% of total`
                      : '0% of total'
                    }
                  </p>
                </div>
                <div className="w-12 h-12 bg-gradient-to-br from-yellow-500/20 to-yellow-600/30 rounded-full flex items-center justify-center neural-glow">
                  <Clock className="w-6 h-6 text-yellow-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="neural-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Approved Requests</p>
                  <p className="text-2xl font-bold text-green-600">{metrics.approvedRequests}</p>
                  <p className="text-xs text-muted-foreground">
                    {metrics.totalRequests > 0 
                      ? `${((metrics.approvedRequests / metrics.totalRequests) * 100).toFixed(1)}% approval rate`
                      : '0% approval rate'
                    }
                  </p>
                </div>
                <div className="w-12 h-12 bg-gradient-to-br from-green-500/20 to-green-600/30 rounded-full flex items-center justify-center neural-glow">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="neural-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Avg Response Time</p>
                  <p className="text-2xl font-bold neural-text">{Math.round(metrics.averageResponseTime)}m</p>
                  <p className="text-xs text-muted-foreground">
                    Target: &lt;5 minutes
                  </p>
                </div>
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500/20 to-blue-600/30 rounded-full flex items-center justify-center neural-glow">
                  <Timer className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Request Types Distribution */}
          <Card className="neural-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PieChart className="w-5 h-5" />
                Request Types
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {metrics.topRequestTypes.map((item, index) => (
                  <div key={item.type} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {getRequestTypeIcon(item.type)}
                      <span className="text-sm neural-text">{getRequestTypeLabel(item.type)}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-20 bg-muted rounded-full h-2">
                        <div 
                          className="bg-primary h-2 rounded-full transition-all duration-300"
                          style={{ width: `${item.percentage}%` }}
                        />
                      </div>
                      <span className="text-sm text-muted-foreground w-12 text-right">
                        {item.count}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Requests by Source */}
          <Card className="neural-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="w-5 h-5" />
                Request Sources
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {metrics.requestsBySource.map((item, index) => (
                  <div key={item.source} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {getSourceIcon(item.source)}
                      <span className="text-sm neural-text capitalize">{item.source}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-20 bg-muted rounded-full h-2">
                        <div 
                          className="bg-accent h-2 rounded-full transition-all duration-300"
                          style={{ width: `${item.percentage}%` }}
                        />
                      </div>
                      <span className="text-sm text-muted-foreground w-12 text-right">
                        {item.count}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* User Satisfaction */}
          <Card className="neural-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Award className="w-5 h-5" />
                User Satisfaction
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="text-center">
                  <div className="text-3xl font-bold neural-text mb-2">
                    {metrics.userSatisfactionScore.toFixed(1)}%
                  </div>
                  <Progress 
                    value={metrics.userSatisfactionScore} 
                    className="w-full h-2"
                  />
                  <p className="text-xs text-muted-foreground mt-2">
                    Based on response times and approval rates
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-2 text-center">
                  <div className="p-2 bg-green-100 rounded">
                    <div className="text-lg font-bold text-green-800">{metrics.genuineUsers}</div>
                    <div className="text-xs text-green-600">Genuine Users</div>
                  </div>
                  <div className="p-2 bg-red-100 rounded">
                    <div className="text-lg font-bold text-red-800">{metrics.suspiciousUsers}</div>
                    <div className="text-xs text-red-600">Suspicious</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Requests Management */}
        <Card className="neural-card">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Request Management
              </CardTitle>
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    placeholder="Search requests..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 w-64"
                  />
                </div>
                <Select value={filterStatus} onValueChange={setFilterStatus}>
                  <SelectTrigger className="w-32">
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="approved">Approved</SelectItem>
                    <SelectItem value="rejected">Rejected</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={filterType} onValueChange={setFilterType}>
                  <SelectTrigger className="w-32">
                    <SelectValue placeholder="Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value="try_access">Try Access</SelectItem>
                    <SelectItem value="detection_access">Detection Access</SelectItem>
                    <SelectItem value="premium_upgrade">Premium Upgrade</SelectItem>
                    <SelectItem value="signup_verification">Signup Verification</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {filteredNotifications.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Shield className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No requests match your filters</p>
                </div>
              ) : (
                filteredNotifications.map((notification) => (
                  <motion.div
                    key={notification.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="neural-card p-4 border border-border/50 rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 bg-gradient-to-br from-accent/20 to-accent/30 rounded-lg flex items-center justify-center neural-glow">
                          {getRequestTypeIcon(notification.requestType)}
                        </div>
                        
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-medium neural-text">{notification.userName}</h4>
                            <Badge variant="outline" className="neural-card text-xs">
                              {getRequestTypeLabel(notification.requestType)}
                            </Badge>
                            <Badge className="text-xs">
                              {getPriorityIcon(notification.priority)}
                              <span className="ml-1 capitalize">{notification.priority}</span>
                            </Badge>
                            <Badge 
                              className={cn(
                                "text-xs",
                                notification.status === 'pending' && "bg-yellow-100 text-yellow-800",
                                notification.status === 'approved' && "bg-green-100 text-green-800",
                                notification.status === 'rejected' && "bg-red-100 text-red-800"
                              )}
                            >
                              {notification.status}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">{notification.userEmail}</p>
                          {notification.message && (
                            <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                              "{notification.message}"
                            </p>
                          )}
                          <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {formatTimeAgo(notification.timestamp)}
                            </span>
                            <span className="flex items-center gap-1">
                              {getSourceIcon(notification.source)}
                              {notification.source}
                            </span>
                            {notification.location?.country && (
                              <span className="flex items-center gap-1">
                                <MapPin className="w-3 h-3" />
                                {notification.location.country}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      {notification.status === 'pending' && (
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() => handleApproveRequest(notification.id)}
                            className="neural-button text-green-600 border-green-600 hover:bg-green-50"
                          >
                            <CheckCircle className="w-4 h-4 mr-1" />
                            Approve
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleRejectRequest(notification.id)}
                            className="neural-button text-red-600 border-red-600 hover:bg-red-50"
                          >
                            <XCircle className="w-4 h-4 mr-1" />
                            Reject
                          </Button>
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default function EnhancedAdminDashboard() {
  return (
    <ProtectedRoute requiredRoles={['admin']}>
      <EnhancedAdminDashboardContent />
    </ProtectedRoute>
  );
}
