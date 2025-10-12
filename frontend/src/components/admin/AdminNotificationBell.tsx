import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useAdminNotifications } from '@/contexts/AdminNotificationContext';
import { 
  Bell, 
  CheckCircle, 
  XCircle, 
  Eye, 
  Zap, 
  Crown,
  Clock,
  User
} from 'lucide-react';

export const AdminNotificationBell: React.FC = () => {
  const { pendingRequests, updateRequestStatus, clearNotifications } = useAdminNotifications();
  const [isOpen, setIsOpen] = useState(false);

  const getRequestTypeIcon = (type: string) => {
    switch (type) {
      case 'try_access': return <Eye className="w-4 h-4 text-blue-600" />;
      case 'detection_access': return <Zap className="w-4 h-4 text-purple-600" />;
      case 'premium_upgrade': return <Crown className="w-4 h-4 text-yellow-600" />;
      default: return <User className="w-4 h-4 text-gray-600" />;
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

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date();
    const requestTime = new Date(timestamp);
    const diffInSeconds = Math.floor((now.getTime() - requestTime.getTime()) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
  };

  return (
    <div className="relative">
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className="neural-button relative hover-lift"
      >
        <Bell className="w-4 h-4" />
        {pendingRequests.length > 0 && (
          <Badge 
            className="neural-card absolute -top-2 -right-2 h-5 w-5 flex items-center justify-center p-0 text-xs bg-destructive hover:bg-destructive/90 text-destructive-foreground"
          >
            {pendingRequests.length}
          </Badge>
        )}
      </Button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute right-0 top-12 w-96 z-50"
          >
            <Card className="neural-card shadow-lg border-0 bg-background/95 backdrop-blur-sm">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center gap-2 neural-text">
                    <div className="w-6 h-6 bg-gradient-to-br from-primary/20 to-primary/30 rounded-full flex items-center justify-center neural-glow">
                      <Bell className="w-3 h-3 text-primary" />
                    </div>
                    Notifications
                    {pendingRequests.length > 0 && (
                      <Badge variant="secondary" className="neural-card ml-2">
                        {pendingRequests.length} pending
                      </Badge>
                    )}
                  </CardTitle>
                  {pendingRequests.length > 0 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={clearNotifications}
                      className="neural-button text-xs hover-lift"
                    >
                      Clear All
                    </Button>
                  )}
                </div>
              </CardHeader>
              
              <CardContent className="p-0">
                <ScrollArea className="h-96">
                  {pendingRequests.length === 0 ? (
                    <div className="p-6 text-center text-muted-foreground">
                      <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p className="neural-text">No pending requests</p>
                    </div>
                  ) : (
                    <div className="space-y-2 p-2">
                      {pendingRequests.map((request) => (
                        <motion.div
                          key={request.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          className="neural-card p-3 border border-border/50 rounded-lg hover:bg-muted/50 transition-colors"
                        >
                          <div className="flex items-start gap-3">
                            <div className="w-8 h-8 bg-gradient-to-br from-accent/20 to-accent/30 rounded-lg flex items-center justify-center neural-glow">
                              {getRequestTypeIcon(request.requestType)}
                            </div>
                            
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <p className="font-medium text-sm truncate neural-text">
                                  {request.userName}
                                </p>
                                <Badge variant="outline" className="neural-card text-xs">
                                  {getRequestTypeLabel(request.requestType)}
                                </Badge>
                              </div>
                              
                              <p className="text-xs text-muted-foreground neural-text mb-2 truncate">
                                {request.userEmail}
                              </p>
                              
                              {request.message && (
                                <p className="text-xs text-muted-foreground neural-text mb-2 line-clamp-2">
                                  "{request.message}"
                                </p>
                              )}
                              
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-1 text-xs text-muted-foreground neural-text">
                                  <Clock className="w-3 h-3" />
                                  {formatTimeAgo(request.timestamp)}
                                </div>
                                
                                <div className="flex gap-1">
                                  <Button
                                    size="sm"
                                    variant="ghost"
                                    onClick={() => updateRequestStatus(request.id, 'approved')}
                                    className="neural-button h-6 px-2 text-success hover:bg-success/10"
                                  >
                                    <CheckCircle className="w-3 h-3" />
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="ghost"
                                    onClick={() => updateRequestStatus(request.id, 'rejected')}
                                    className="neural-button h-6 px-2 text-destructive hover:bg-destructive/10"
                                  >
                                    <XCircle className="w-3 h-3" />
                                  </Button>
                                </div>
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
