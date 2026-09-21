import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useEnhancedNotifications } from '@/contexts/EnhancedNotificationContext';
import { EnhancedNotificationBell } from './EnhancedNotificationBell';
import { NotificationSettingsModal } from './NotificationSettings';
import { NotificationHistory } from './NotificationHistory';
import { BulkOperationsDialog } from './BulkOperationsDialog';
import { 
  Bell, 
  Settings, 
  History, 
  Users, 
  BarChart3,
  Activity,
  Shield,
  CheckCircle,
  AlertTriangle,
  Info
} from 'lucide-react';

interface NotificationSystemDemoProps {
  className?: string;
}

export const NotificationSystemDemo: React.FC<NotificationSystemDemoProps> = ({ className }) => {
  const { 
    notifications, 
    pendingNotifications, 
    isConnected, 
    stats,
    generateDemoData,
    clearNotifications
  } = useEnhancedNotifications();

  const [showSettings, setShowSettings] = useState(false);
  const [showBulkOperations, setShowBulkOperations] = useState(false);
  const [selectedNotifications, setSelectedNotifications] = useState<string[]>([]);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold neural-text">Enhanced Notification System</h1>
          <p className="text-muted-foreground">
            Production-grade real-time notification management with advanced analytics
          </p>
        </div>
        <div className="flex items-center gap-4">
          <EnhancedNotificationBell />
          <Button
            variant="outline"
            onClick={() => setShowSettings(true)}
            className="neural-button"
          >
            <Settings className="w-4 h-4 mr-2" />
            Settings
          </Button>
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="neural-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Requests</p>
                <p className="text-2xl font-bold neural-text">{stats.totalRequests}</p>
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
                <p className="text-sm font-medium text-muted-foreground">Pending</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.pendingRequests}</p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-br from-yellow-500/20 to-yellow-600/30 rounded-full flex items-center justify-center neural-glow">
                <Bell className="w-6 h-6 text-yellow-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="neural-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Approved</p>
                <p className="text-2xl font-bold text-green-600">{stats.approvedRequests}</p>
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
                <p className="text-sm font-medium text-muted-foreground">Connection</p>
                <p className="text-lg font-bold">
                  {isConnected ? (
                    <span className="text-green-600">Connected</span>
                  ) : (
                    <span className="text-red-600">Disconnected</span>
                  )}
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500/20 to-blue-600/30 rounded-full flex items-center justify-center neural-glow">
                <Activity className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Features Overview */}
      <Card className="neural-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-5 h-5" />
            System Features
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="p-4 border border-border/50 rounded-lg">
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                <Bell className="w-4 h-4 text-primary" />
                Real-time Notifications
              </h4>
              <p className="text-sm text-muted-foreground">
                WebSocket-powered real-time updates with automatic reconnection and offline support.
              </p>
            </div>

            <div className="p-4 border border-border/50 rounded-lg">
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                <Users className="w-4 h-4 text-primary" />
                Bulk Operations
              </h4>
              <p className="text-sm text-muted-foreground">
                Efficiently manage multiple requests with bulk approve/reject functionality.
              </p>
            </div>

            <div className="p-4 border border-border/50 rounded-lg">
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-primary" />
                Advanced Analytics
              </h4>
              <p className="text-sm text-muted-foreground">
                Comprehensive analytics with charts, trends, and performance metrics.
              </p>
            </div>

            <div className="p-4 border border-border/50 rounded-lg">
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                <Settings className="w-4 h-4 text-primary" />
                Customizable Settings
              </h4>
              <p className="text-sm text-muted-foreground">
                Personalized notification preferences with sound, desktop, and filter options.
              </p>
            </div>

            <div className="p-4 border border-border/50 rounded-lg">
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                <History className="w-4 h-4 text-primary" />
                Complete History
              </h4>
              <p className="text-sm text-muted-foreground">
                Full notification history with search, filtering, and export capabilities.
              </p>
            </div>

            <div className="p-4 border border-border/50 rounded-lg">
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                <Shield className="w-4 h-4 text-primary" />
                Production Ready
              </h4>
              <p className="text-sm text-muted-foreground">
                Enterprise-grade security, persistence, and error handling.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card className="neural-card">
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <Button
              onClick={generateDemoData}
              className="neural-button"
            >
              <Users className="w-4 h-4 mr-2" />
              Generate Demo Data
            </Button>
            
            <Button
              variant="outline"
              onClick={() => clearNotifications('pending')}
              className="neural-button"
            >
              <Bell className="w-4 h-4 mr-2" />
              Clear Pending
            </Button>
            
            <Button
              variant="outline"
              onClick={() => setShowBulkOperations(true)}
              disabled={selectedNotifications.length === 0}
              className="neural-button"
            >
              <Users className="w-4 h-4 mr-2" />
              Bulk Operations ({selectedNotifications.length})
            </Button>
            
            <Button
              variant="outline"
              onClick={() => clearNotifications()}
              className="neural-button"
            >
              <AlertTriangle className="w-4 h-4 mr-2" />
              Clear All
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Demo Information */}
      <Alert>
        <Info className="h-4 w-4" />
        <AlertDescription>
          <strong>Demo Mode:</strong> This is a demonstration of the enhanced notification system. 
          Click "Generate Demo Data" to add sample notifications, or use the notification bell 
          in the header to see the full interface. All data is stored locally and will persist 
          between sessions.
        </AlertDescription>
      </Alert>

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <Card className="neural-card">
            <CardHeader>
              <CardTitle>Recent Notifications</CardTitle>
            </CardHeader>
            <CardContent>
              {pendingNotifications.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Bell className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No pending notifications</p>
                  <p className="text-sm">Generate demo data to see notifications in action</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {pendingNotifications.slice(0, 5).map((notification) => (
                    <div key={notification.id} className="flex items-center justify-between p-3 border border-border/50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-gradient-to-br from-accent/20 to-accent/30 rounded-lg flex items-center justify-center">
                          <Bell className="w-4 h-4 text-accent" />
                        </div>
                        <div>
                          <p className="font-medium">{notification.userName}</p>
                          <p className="text-sm text-muted-foreground">{notification.userEmail}</p>
                        </div>
                      </div>
                      <Badge variant="outline" className="neural-card">
                        {notification.requestType.replace('_', ' ')}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history">
          <NotificationHistory />
        </TabsContent>

        <TabsContent value="analytics">
          <Card className="neural-card">
            <CardHeader>
              <CardTitle>System Analytics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-3">Request Distribution</h4>
                  <div className="space-y-2">
                    {Object.entries(stats.requestsByType).map(([type, count]) => (
                      <div key={type} className="flex items-center justify-between">
                        <span className="text-sm">{type.replace('_', ' ')}</span>
                        <div className="flex items-center gap-2">
                          <div className="w-20 bg-muted rounded-full h-2">
                            <div 
                              className="bg-primary h-2 rounded-full"
                              style={{ width: `${(count / stats.totalRequests) * 100}%` }}
                            />
                          </div>
                          <span className="text-sm text-muted-foreground w-8 text-right">
                            {count}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-3">Performance Metrics</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Total Requests</span>
                      <span className="font-semibold">{stats.totalRequests}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Approval Rate</span>
                      <span className="font-semibold text-green-600">
                        {stats.totalRequests > 0 ? ((stats.approvedRequests / stats.totalRequests) * 100).toFixed(1) : 0}%
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Response Time</span>
                      <span className="font-semibold">{Math.round(stats.averageResponseTime)}m</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Genuine Users</span>
                      <span className="font-semibold text-blue-600">{stats.genuineUsers}</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Modals */}
      <NotificationSettingsModal 
        isOpen={showSettings} 
        onClose={() => setShowSettings(false)} 
      />
      
      <BulkOperationsDialog
        isOpen={showBulkOperations}
        onClose={() => setShowBulkOperations(false)}
        selectedNotifications={selectedNotifications}
        onClearSelection={() => setSelectedNotifications([])}
      />
    </div>
  );
};
