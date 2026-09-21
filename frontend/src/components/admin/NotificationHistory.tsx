import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useEnhancedNotifications, NotificationRequest } from '@/contexts/EnhancedNotificationContext';
import { 
  History,
  Search,
  Filter,
  Download,
  Eye,
  Zap,
  Crown,
  User,
  Clock,
  MapPin,
  Globe,
  Smartphone,
  Monitor,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Star,
  Flag,
  Calendar,
  BarChart3,
  PieChart,
  LineChart,
  ChevronLeft,
  ChevronRight,
  MoreVertical,
  ExternalLink
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface NotificationHistoryProps {
  className?: string;
}

export const NotificationHistory: React.FC<NotificationHistoryProps> = ({ className }) => {
  const { notifications, stats } = useEnhancedNotifications();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [filterPriority, setFilterPriority] = useState('all');
  const [filterSource, setFilterSource] = useState('all');
  const [filterDateRange, setFilterDateRange] = useState('all');
  const [sortBy, setSortBy] = useState<'timestamp' | 'priority' | 'userName' | 'status'>('timestamp');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(20);
  const [selectedNotifications, setSelectedNotifications] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState('list');

  // Filter and sort notifications
  const filteredNotifications = useMemo(() => {
    let filtered = notifications;

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(n => 
        n.userName.toLowerCase().includes(query) ||
        n.userEmail.toLowerCase().includes(query) ||
        n.requestType.toLowerCase().includes(query) ||
        n.message?.toLowerCase().includes(query) ||
        n.adminNotes?.toLowerCase().includes(query)
      );
    }

    // Apply status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter(n => n.status === filterStatus);
    }

    // Apply type filter
    if (filterType !== 'all') {
      filtered = filtered.filter(n => n.requestType === filterType);
    }

    // Apply priority filter
    if (filterPriority !== 'all') {
      filtered = filtered.filter(n => n.priority === filterPriority);
    }

    // Apply source filter
    if (filterSource !== 'all') {
      filtered = filtered.filter(n => n.source === filterSource);
    }

    // Apply date range filter
    if (filterDateRange !== 'all') {
      const now = new Date();
      const filterDate = new Date();
      
      switch (filterDateRange) {
        case 'today':
          filterDate.setHours(0, 0, 0, 0);
          break;
        case 'week':
          filterDate.setDate(now.getDate() - 7);
          break;
        case 'month':
          filterDate.setMonth(now.getMonth() - 1);
          break;
        case 'year':
          filterDate.setFullYear(now.getFullYear() - 1);
          break;
      }
      
      filtered = filtered.filter(n => new Date(n.timestamp) >= filterDate);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue: any, bValue: any;
      
      switch (sortBy) {
        case 'timestamp':
          aValue = new Date(a.timestamp).getTime();
          bValue = new Date(b.timestamp).getTime();
          break;
        case 'priority':
          const priorityOrder = { urgent: 4, high: 3, medium: 2, low: 1 };
          aValue = priorityOrder[a.priority];
          bValue = priorityOrder[b.priority];
          break;
        case 'userName':
          aValue = a.userName.toLowerCase();
          bValue = b.userName.toLowerCase();
          break;
        case 'status':
          const statusOrder = { pending: 3, approved: 2, rejected: 1 };
          aValue = statusOrder[a.status];
          bValue = statusOrder[b.status];
          break;
        default:
          return 0;
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return filtered;
  }, [notifications, searchQuery, filterStatus, filterType, filterPriority, filterSource, filterDateRange, sortBy, sortOrder]);

  // Pagination
  const totalPages = Math.ceil(filteredNotifications.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedNotifications = filteredNotifications.slice(startIndex, startIndex + itemsPerPage);

  // Analytics
  const analytics = useMemo(() => {
    const total = filteredNotifications.length;
    const statusCounts = {
      pending: filteredNotifications.filter(n => n.status === 'pending').length,
      approved: filteredNotifications.filter(n => n.status === 'approved').length,
      rejected: filteredNotifications.filter(n => n.status === 'rejected').length,
    };

    const typeCounts = filteredNotifications.reduce((acc, n) => {
      acc[n.requestType] = (acc[n.requestType] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const priorityCounts = filteredNotifications.reduce((acc, n) => {
      acc[n.priority] = (acc[n.priority] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const sourceCounts = filteredNotifications.reduce((acc, n) => {
      acc[n.source] = (acc[n.source] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    // Calculate hourly distribution
    const hourlyDistribution = Array.from({ length: 24 }, (_, i) => {
      const count = filteredNotifications.filter(n => new Date(n.timestamp).getHours() === i).length;
      return { hour: i, count, percentage: total > 0 ? (count / total) * 100 : 0 };
    });

    return {
      total,
      statusCounts,
      typeCounts,
      priorityCounts,
      sourceCounts,
      hourlyDistribution
    };
  }, [filteredNotifications]);

  const getRequestTypeIcon = (type: string) => {
    switch (type) {
      case 'try_access': return <Eye className="w-4 h-4" />;
      case 'detection_access': return <Zap className="w-4 h-4" />;
      case 'premium_upgrade': return <Crown className="w-4 h-4" />;
      case 'signup_verification': return <User className="w-4 h-4" />;
      default: return <User className="w-4 h-4" />;
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

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'approved': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'rejected': return <XCircle className="w-4 h-4 text-red-500" />;
      default: return null;
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

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const exportToCSV = () => {
    const csvData = filteredNotifications.map(n => ({
      'Request ID': n.id,
      'User Name': n.userName,
      'User Email': n.userEmail,
      'Request Type': getRequestTypeLabel(n.requestType),
      'Status': n.status,
      'Priority': n.priority,
      'Source': n.source,
      'Timestamp': formatDate(n.timestamp),
      'Message': n.message || '',
      'Admin Notes': n.adminNotes || '',
      'Location': n.location ? `${n.location.city}, ${n.location.country}` : '',
      'Is Genuine': n.isGenuine ? 'Yes' : 'No'
    }));

    const csvContent = [
      Object.keys(csvData[0]).join(','),
      ...csvData.map(row => Object.values(row).map(value => `"${value}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `notification-history-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className={cn("space-y-6", className)}>
      <Card className="neural-card">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-primary/20 to-primary/30 rounded-full flex items-center justify-center neural-glow">
                <History className="w-4 h-4 text-primary" />
              </div>
              Notification History
            </CardTitle>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                onClick={exportToCSV}
                className="neural-button"
              >
                <Download className="w-4 h-4 mr-2" />
                Export CSV
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="list">List View</TabsTrigger>
              <TabsTrigger value="analytics">Analytics</TabsTrigger>
            </TabsList>

            <TabsContent value="list" className="space-y-4">
              {/* Filters */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    placeholder="Search notifications..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>

                <Select value={filterStatus} onValueChange={setFilterStatus}>
                  <SelectTrigger>
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
                  <SelectTrigger>
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

                <Select value={filterDateRange} onValueChange={setFilterDateRange}>
                  <SelectTrigger>
                    <SelectValue placeholder="Date Range" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Time</SelectItem>
                    <SelectItem value="today">Today</SelectItem>
                    <SelectItem value="week">This Week</SelectItem>
                    <SelectItem value="month">This Month</SelectItem>
                    <SelectItem value="year">This Year</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Results Summary */}
              <div className="flex items-center justify-between">
                <div className="text-sm text-muted-foreground">
                  Showing {startIndex + 1}-{Math.min(startIndex + itemsPerPage, filteredNotifications.length)} of {filteredNotifications.length} notifications
                </div>
                <div className="flex items-center gap-2">
                  <Select value={sortBy} onValueChange={(value: any) => setSortBy(value)}>
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="timestamp">Date</SelectItem>
                      <SelectItem value="priority">Priority</SelectItem>
                      <SelectItem value="userName">User</SelectItem>
                      <SelectItem value="status">Status</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                    className="neural-button"
                  >
                    {sortOrder === 'asc' ? '↑' : '↓'}
                  </Button>
                </div>
              </div>

              {/* Table */}
              <div className="border rounded-lg overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>User</TableHead>
                      <TableHead>Request Type</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Priority</TableHead>
                      <TableHead>Source</TableHead>
                      <TableHead>Location</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {paginatedNotifications.map((notification) => (
                      <TableRow key={notification.id}>
                        <TableCell>
                          <div>
                            <div className="font-medium">{notification.userName}</div>
                            <div className="text-sm text-muted-foreground">{notification.userEmail}</div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {getRequestTypeIcon(notification.requestType)}
                            <span className="text-sm">{getRequestTypeLabel(notification.requestType)}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            className={cn(
                              "flex items-center gap-1 w-fit",
                              notification.status === 'pending' && "bg-yellow-100 text-yellow-800",
                              notification.status === 'approved' && "bg-green-100 text-green-800",
                              notification.status === 'rejected' && "bg-red-100 text-red-800"
                            )}
                          >
                            {getStatusIcon(notification.status)}
                            <span className="capitalize">{notification.status}</span>
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            {getPriorityIcon(notification.priority)}
                            <span className="capitalize text-sm">{notification.priority}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            {getSourceIcon(notification.source)}
                            <span className="capitalize text-sm">{notification.source}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          {notification.location?.country ? (
                            <div className="flex items-center gap-1 text-sm">
                              <MapPin className="w-3 h-3" />
                              {notification.location.city}, {notification.location.country}
                            </div>
                          ) : (
                            <span className="text-muted-foreground text-sm">Unknown</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <div>
                            <div className="text-sm">{formatDate(notification.timestamp)}</div>
                            <div className="text-xs text-muted-foreground">{formatTimeAgo(notification.timestamp)}</div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Button variant="ghost" size="sm" className="neural-button">
                            <MoreVertical className="w-4 h-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {/* Pagination */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">Items per page:</span>
                  <Select value={itemsPerPage.toString()} onValueChange={(value) => setItemsPerPage(parseInt(value))}>
                    <SelectTrigger className="w-20">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="10">10</SelectItem>
                      <SelectItem value="20">20</SelectItem>
                      <SelectItem value="50">50</SelectItem>
                      <SelectItem value="100">100</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                    className="neural-button"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  
                  <span className="text-sm">
                    Page {currentPage} of {totalPages}
                  </span>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                    className="neural-button"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="analytics" className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card className="neural-card">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Total Requests</p>
                        <p className="text-2xl font-bold neural-text">{analytics.total}</p>
                      </div>
                      <BarChart3 className="w-8 h-8 text-primary" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="neural-card">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Approval Rate</p>
                        <p className="text-2xl font-bold text-green-600">
                          {analytics.total > 0 ? ((analytics.statusCounts.approved / analytics.total) * 100).toFixed(1) : 0}%
                        </p>
                      </div>
                      <CheckCircle className="w-8 h-8 text-green-600" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="neural-card">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Pending</p>
                        <p className="text-2xl font-bold text-yellow-600">{analytics.statusCounts.pending}</p>
                      </div>
                      <Clock className="w-8 h-8 text-yellow-600" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="neural-card">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Rejected</p>
                        <p className="text-2xl font-bold text-red-600">{analytics.statusCounts.rejected}</p>
                      </div>
                      <XCircle className="w-8 h-8 text-red-600" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Request Types Distribution */}
                <Card className="neural-card">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <PieChart className="w-5 h-5" />
                      Request Types Distribution
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {Object.entries(analytics.typeCounts).map(([type, count]) => (
                        <div key={type} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            {getRequestTypeIcon(type)}
                            <span className="text-sm">{getRequestTypeLabel(type)}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <div className="w-20 bg-muted rounded-full h-2">
                              <div 
                                className="bg-primary h-2 rounded-full"
                                style={{ width: `${(count / analytics.total) * 100}%` }}
                              />
                            </div>
                            <span className="text-sm text-muted-foreground w-12 text-right">
                              {count}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Hourly Distribution */}
                <Card className="neural-card">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <LineChart className="w-5 h-5" />
                      Hourly Distribution
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {analytics.hourlyDistribution.map(({ hour, count, percentage }) => (
                        <div key={hour} className="flex items-center gap-3">
                          <span className="text-sm w-12">{hour.toString().padStart(2, '0')}:00</span>
                          <div className="flex-1 bg-muted rounded-full h-2">
                            <div 
                              className="bg-accent h-2 rounded-full"
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                          <span className="text-sm text-muted-foreground w-12 text-right">
                            {count}
                          </span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};
