import React, { useState, useMemo, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useEnhancedNotifications, NotificationRequest } from '@/contexts/EnhancedNotificationContext';
import { 
  Bell, 
  CheckCircle, 
  XCircle, 
  Eye, 
  Zap, 
  Crown,
  Clock,
  User,
  Search,
  Filter,
  Settings,
  RefreshCw,
  MoreVertical,
  AlertTriangle,
  CheckSquare,
  Square,
  Trash2,
  Download,
  Volume2,
  VolumeX,
  Wifi,
  WifiOff,
  ChevronDown,
  ChevronUp,
  Star,
  Flag,
  Calendar,
  MapPin,
  Globe,
  Smartphone,
  Monitor
} from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

interface EnhancedNotificationBellProps {
  className?: string;
  showStats?: boolean;
  maxHeight?: string;
}

export const EnhancedNotificationBell: React.FC<EnhancedNotificationBellProps> = ({ 
  className,
  showStats = true,
  maxHeight = "500px"
}) => {
  const {
    notifications,
    pendingNotifications,
    isConnected,
    isLoading,
    settings,
    stats,
    updateNotificationStatus,
    bulkUpdateStatus,
    clearNotifications,
    updateSettings,
    getNotificationCount,
    searchNotifications,
    refreshNotifications
  } = useEnhancedNotifications();

  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNotifications, setSelectedNotifications] = useState<string[]>([]);
  const [filterType, setFilterType] = useState<string>('all');
  const [filterPriority, setFilterPriority] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'timestamp' | 'priority' | 'userName'>('timestamp');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [showSettings, setShowSettings] = useState(false);
  const [expandedNotification, setExpandedNotification] = useState<string | null>(null);

  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Filter and sort notifications
  const filteredNotifications = useMemo(() => {
    let filtered = notifications;

    // Apply search filter
    if (searchQuery) {
      filtered = searchNotifications(searchQuery);
    }

    // Apply type filter
    if (filterType !== 'all') {
      filtered = filtered.filter(n => n.requestType === filterType);
    }

    // Apply priority filter
    if (filterPriority !== 'all') {
      filtered = filtered.filter(n => n.priority === filterPriority);
    }

    // Apply status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter(n => n.status === filterStatus);
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
  }, [notifications, searchQuery, filterType, filterPriority, filterStatus, sortBy, sortOrder, searchNotifications]);

  const getRequestTypeIcon = (type: string) => {
    switch (type) {
      case 'try_access': return <Eye className="w-4 h-4 text-blue-600" />;
      case 'detection_access': return <Zap className="w-4 h-4 text-purple-600" />;
      case 'premium_upgrade': return <Crown className="w-4 h-4 text-yellow-600" />;
      case 'signup_verification': return <User className="w-4 h-4 text-green-600" />;
      default: return <User className="w-4 h-4 text-gray-600" />;
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
      case 'high': return <Flag className="w-3 h-3 text-orange-500" />;
      case 'medium': return <Clock className="w-3 h-3 text-yellow-500" />;
      case 'low': return <Star className="w-3 h-3 text-blue-500" />;
      default: return null;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getSourceIcon = (source: string) => {
    switch (source) {
      case 'web': return <Monitor className="w-3 h-3" />;
      case 'mobile': return <Smartphone className="w-3 h-3" />;
      case 'api': return <Globe className="w-3 h-3" />;
      default: return <Globe className="w-3 h-3" />;
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

  const handleSelectAll = () => {
    if (selectedNotifications.length === filteredNotifications.length) {
      setSelectedNotifications([]);
    } else {
      setSelectedNotifications(filteredNotifications.map(n => n.id));
    }
  };

  const handleSelectNotification = (id: string) => {
    setSelectedNotifications(prev => 
      prev.includes(id) 
        ? prev.filter(n => n !== id)
        : [...prev, id]
    );
  };

  const handleBulkApprove = async () => {
    if (selectedNotifications.length === 0) return;
    
    try {
      await bulkUpdateStatus(selectedNotifications, 'approved', 'Bulk approved by admin');
      setSelectedNotifications([]);
      toast.success(`Approved ${selectedNotifications.length} requests`);
    } catch (error) {
      toast.error('Failed to approve requests');
    }
  };

  const handleBulkReject = async () => {
    if (selectedNotifications.length === 0) return;
    
    try {
      await bulkUpdateStatus(selectedNotifications, 'rejected', 'Bulk rejected by admin');
      setSelectedNotifications([]);
      toast.error(`Rejected ${selectedNotifications.length} requests`);
    } catch (error) {
      toast.error('Failed to reject requests');
    }
  };

  const handleToggleSound = () => {
    updateSettings({ soundEnabled: !settings.soundEnabled });
  };

  const pendingCount = getNotificationCount('pending');
  const hasSelection = selectedNotifications.length > 0;

  return (
    <div className={cn("relative", className)} ref={dropdownRef}>
      {/* Notification Bell Button */}
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className="neural-button relative hover-lift"
      >
        <Bell className="w-4 h-4" />
        {pendingCount > 0 && (
          <Badge 
            className="neural-card absolute -top-2 -right-2 h-5 w-5 flex items-center justify-center p-0 text-xs bg-destructive hover:bg-destructive/90 text-destructive-foreground"
          >
            {pendingCount}
          </Badge>
        )}
        {isConnected ? (
          <Wifi className="w-3 h-3 ml-1 text-green-500" />
        ) : (
          <WifiOff className="w-3 h-3 ml-1 text-red-500" />
        )}
      </Button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute right-0 top-12 w-[500px] z-50"
          >
            <Card className="neural-card shadow-xl border-0 bg-background/95 backdrop-blur-sm">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center gap-2 neural-text">
                    <div className="w-6 h-6 bg-gradient-to-br from-primary/20 to-primary/30 rounded-full flex items-center justify-center neural-glow">
                      <Bell className="w-3 h-3 text-primary" />
                    </div>
                    Notifications
                    {pendingCount > 0 && (
                      <Badge variant="secondary" className="neural-card ml-2">
                        {pendingCount} pending
                      </Badge>
                    )}
                    {isConnected ? (
                      <Badge variant="outline" className="neural-card ml-2 text-green-600 border-green-600">
                        <Wifi className="w-3 h-3 mr-1" />
                        Live
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="neural-card ml-2 text-red-600 border-red-600">
                        <WifiOff className="w-3 h-3 mr-1" />
                        Offline
                      </Badge>
                    )}
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleToggleSound}
                      className="neural-button"
                    >
                      {settings.soundEnabled ? (
                        <Volume2 className="w-4 h-4" />
                      ) : (
                        <VolumeX className="w-4 h-4" />
                      )}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowSettings(!showSettings)}
                      className="neural-button"
                    >
                      <Settings className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={refreshNotifications}
                      disabled={isLoading}
                      className="neural-button"
                    >
                      <RefreshCw className={cn("w-4 h-4", isLoading && "animate-spin")} />
                    </Button>
                  </div>
                </div>
              </CardHeader>

              {/* Settings Panel */}
              <AnimatePresence>
                {showSettings && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="px-6 pb-4"
                  >
                    <Alert>
                      <Settings className="h-4 w-4" />
                      <AlertDescription>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span>Auto Refresh</span>
                            <Checkbox 
                              checked={settings.autoRefresh}
                              onCheckedChange={(checked) => 
                                updateSettings({ autoRefresh: checked as boolean })
                              }
                            />
                          </div>
                          <div className="flex items-center justify-between">
                            <span>Desktop Notifications</span>
                            <Checkbox 
                              checked={settings.desktopNotifications}
                              onCheckedChange={(checked) => 
                                updateSettings({ desktopNotifications: checked as boolean })
                              }
                            />
                          </div>
                          <div className="flex items-center justify-between">
                            <span>Toast Notifications</span>
                            <Checkbox 
                              checked={settings.showToastNotifications}
                              onCheckedChange={(checked) => 
                                updateSettings({ showToastNotifications: checked as boolean })
                              }
                            />
                          </div>
                        </div>
                      </AlertDescription>
                    </Alert>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Stats Panel */}
              {showStats && (
                <div className="px-6 pb-4">
                  <div className="grid grid-cols-4 gap-2">
                    <div className="text-center p-2 bg-muted/50 rounded">
                      <div className="text-lg font-bold text-primary">{stats.totalRequests}</div>
                      <div className="text-xs text-muted-foreground">Total</div>
                    </div>
                    <div className="text-center p-2 bg-yellow-100 rounded">
                      <div className="text-lg font-bold text-yellow-800">{stats.pendingRequests}</div>
                      <div className="text-xs text-muted-foreground">Pending</div>
                    </div>
                    <div className="text-center p-2 bg-green-100 rounded">
                      <div className="text-lg font-bold text-green-800">{stats.approvedRequests}</div>
                      <div className="text-xs text-muted-foreground">Approved</div>
                    </div>
                    <div className="text-center p-2 bg-red-100 rounded">
                      <div className="text-lg font-bold text-red-800">{stats.rejectedRequests}</div>
                      <div className="text-xs text-muted-foreground">Rejected</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Search and Filters */}
              <div className="px-6 pb-4 space-y-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    placeholder="Search notifications..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>

                <div className="flex gap-2">
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

                  <Select value={filterPriority} onValueChange={setFilterPriority}>
                    <SelectTrigger className="w-32">
                      <SelectValue placeholder="Priority" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Priorities</SelectItem>
                      <SelectItem value="urgent">Urgent</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                    </SelectContent>
                  </Select>

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
                </div>

                {/* Bulk Actions */}
                {hasSelection && (
                  <div className="flex items-center gap-2 p-2 bg-muted/50 rounded">
                    <span className="text-sm text-muted-foreground">
                      {selectedNotifications.length} selected
                    </span>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleBulkApprove}
                      className="neural-button text-green-600 border-green-600 hover:bg-green-50"
                    >
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Approve
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleBulkReject}
                      className="neural-button text-red-600 border-red-600 hover:bg-red-50"
                    >
                      <XCircle className="w-3 h-3 mr-1" />
                      Reject
                    </Button>
                  </div>
                )}
              </div>
              
              <CardContent className="p-0">
                <ScrollArea className="h-[400px]">
                  {filteredNotifications.length === 0 ? (
                    <div className="p-6 text-center text-muted-foreground">
                      <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p className="neural-text">
                        {searchQuery || filterType !== 'all' || filterPriority !== 'all' || filterStatus !== 'all'
                          ? 'No notifications match your filters'
                          : 'No notifications yet'
                        }
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-1 p-2">
                      {/* Select All */}
                      <div className="flex items-center gap-2 p-2 border-b">
                        <Checkbox
                          checked={selectedNotifications.length === filteredNotifications.length && filteredNotifications.length > 0}
                          onCheckedChange={handleSelectAll}
                        />
                        <span className="text-sm text-muted-foreground">Select All</span>
                      </div>

                      {filteredNotifications.map((notification) => (
                        <motion.div
                          key={notification.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          className={cn(
                            "neural-card p-3 border border-border/50 rounded-lg hover:bg-muted/50 transition-colors",
                            notification.status === 'pending' && "border-l-4 border-l-yellow-500",
                            notification.status === 'approved' && "border-l-4 border-l-green-500",
                            notification.status === 'rejected' && "border-l-4 border-l-red-500"
                          )}
                        >
                          <div className="flex items-start gap-3">
                            <Checkbox
                              checked={selectedNotifications.includes(notification.id)}
                              onCheckedChange={() => handleSelectNotification(notification.id)}
                            />
                            
                            <div className="w-8 h-8 bg-gradient-to-br from-accent/20 to-accent/30 rounded-lg flex items-center justify-center neural-glow">
                              {getRequestTypeIcon(notification.requestType)}
                            </div>
                            
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <p className="font-medium text-sm truncate neural-text">
                                  {notification.userName}
                                </p>
                                <Badge variant="outline" className="neural-card text-xs">
                                  {getRequestTypeLabel(notification.requestType)}
                                </Badge>
                                <Badge className={cn("text-xs", getPriorityColor(notification.priority))}>
                                  {getPriorityIcon(notification.priority)}
                                  <span className="ml-1 capitalize">{notification.priority}</span>
                                </Badge>
                                <Badge variant="secondary" className="neural-card text-xs">
                                  {getSourceIcon(notification.source)}
                                  <span className="ml-1 capitalize">{notification.source}</span>
                                </Badge>
                              </div>
                              
                              <p className="text-xs text-muted-foreground neural-text mb-2 truncate">
                                {notification.userEmail}
                              </p>
                              
                              {notification.message && (
                                <div className="mb-2">
                                  <p className="text-xs text-muted-foreground neural-text line-clamp-2">
                                    "{notification.message}"
                                  </p>
                                  {notification.message.length > 100 && (
                                    <Button
                                      variant="ghost"
                                      size="sm"
                                      onClick={() => setExpandedNotification(
                                        expandedNotification === notification.id ? null : notification.id
                                      )}
                                      className="text-xs p-0 h-auto"
                                    >
                                      {expandedNotification === notification.id ? (
                                        <>
                                          <ChevronUp className="w-3 h-3 mr-1" />
                                          Show Less
                                        </>
                                      ) : (
                                        <>
                                          <ChevronDown className="w-3 h-3 mr-1" />
                                          Show More
                                        </>
                                      )}
                                    </Button>
                                  )}
                                </div>
                              )}

                              {expandedNotification === notification.id && (
                                <motion.div
                                  initial={{ opacity: 0, height: 0 }}
                                  animate={{ opacity: 1, height: 'auto' }}
                                  exit={{ opacity: 0, height: 0 }}
                                  className="mt-2 p-2 bg-muted/30 rounded text-xs space-y-1"
                                >
                                  {notification.location && (
                                    <div className="flex items-center gap-1">
                                      <MapPin className="w-3 h-3" />
                                      <span>{notification.location.city}, {notification.location.country}</span>
                                    </div>
                                  )}
                                  {notification.userAgent && (
                                    <div className="flex items-center gap-1">
                                      <Monitor className="w-3 h-3" />
                                      <span className="truncate">{notification.userAgent}</span>
                                    </div>
                                  )}
                                  {notification.metadata && (
                                    <div className="flex items-center gap-1">
                                      <Star className="w-3 h-3" />
                                      <span>Previous requests: {notification.metadata.previousRequests || 0}</span>
                                    </div>
                                  )}
                                </motion.div>
                              )}
                              
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-1 text-xs text-muted-foreground neural-text">
                                  <Clock className="w-3 h-3" />
                                  {formatTimeAgo(notification.timestamp)}
                                </div>
                                
                                {notification.status === 'pending' && (
                                  <div className="flex gap-1">
                                    <Button
                                      size="sm"
                                      variant="ghost"
                                      onClick={() => updateNotificationStatus(notification.id, 'approved')}
                                      className="neural-button h-6 px-2 text-success hover:bg-success/10"
                                    >
                                      <CheckCircle className="w-3 h-3" />
                                    </Button>
                                    <Button
                                      size="sm"
                                      variant="ghost"
                                      onClick={() => updateNotificationStatus(notification.id, 'rejected')}
                                      className="neural-button h-6 px-2 text-destructive hover:bg-destructive/10"
                                    >
                                      <XCircle className="w-3 h-3" />
                                    </Button>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </CardContent>

              {/* Footer Actions */}
              <div className="flex items-center justify-between p-4 border-t">
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => clearNotifications('pending')}
                    className="neural-button text-xs"
                  >
                    Clear Pending
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => clearNotifications()}
                    className="neural-button text-xs"
                  >
                    Clear All
                  </Button>
                </div>
                <div className="text-xs text-muted-foreground">
                  {filteredNotifications.length} of {notifications.length} notifications
                </div>
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
