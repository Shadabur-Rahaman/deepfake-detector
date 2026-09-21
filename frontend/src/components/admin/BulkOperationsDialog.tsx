import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useEnhancedNotifications } from '@/contexts/EnhancedNotificationContext';
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Users, 
  MessageSquare,
  Shield,
  Clock,
  Eye,
  Zap,
  Crown,
  User
} from 'lucide-react';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

interface BulkOperationsDialogProps {
  isOpen: boolean;
  onClose: () => void;
  selectedNotifications: string[];
  onClearSelection: () => void;
}

export const BulkOperationsDialog: React.FC<BulkOperationsDialogProps> = ({
  isOpen,
  onClose,
  selectedNotifications,
  onClearSelection
}) => {
  const { notifications, bulkUpdateStatus } = useEnhancedNotifications();
  const [action, setAction] = useState<'approve' | 'reject' | null>(null);
  const [adminNotes, setAdminNotes] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const selectedNotificationDetails = notifications.filter(n => selectedNotifications.includes(n.id));

  const handleBulkAction = async (status: 'approved' | 'rejected') => {
    if (selectedNotifications.length === 0) return;

    setIsProcessing(true);
    try {
      await bulkUpdateStatus(selectedNotifications, status, adminNotes || undefined);
      
      toast.success(
        `Bulk ${status} completed`, 
        {
          description: `${selectedNotifications.length} requests have been ${status}`
        }
      );
      
      onClearSelection();
      onClose();
    } catch (error) {
      toast.error(`Failed to ${status} requests`);
      console.error('Bulk operation error:', error);
    } finally {
      setIsProcessing(false);
    }
  };

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

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // Group notifications by type
  const notificationsByType = selectedNotificationDetails.reduce((acc, n) => {
    if (!acc[n.requestType]) {
      acc[n.requestType] = [];
    }
    acc[n.requestType].push(n);
    return acc;
  }, {} as Record<string, typeof selectedNotificationDetails>);

  // Group notifications by priority
  const notificationsByPriority = selectedNotificationDetails.reduce((acc, n) => {
    if (!acc[n.priority]) {
      acc[n.priority] = [];
    }
    acc[n.priority].push(n);
    return acc;
  }, {} as Record<string, typeof selectedNotificationDetails>);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="neural-card w-full max-w-2xl max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gradient-to-br from-primary/20 to-primary/30 rounded-full flex items-center justify-center neural-glow">
                  <Users className="w-4 h-4 text-primary" />
                </div>
                Bulk Operations
              </CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="neural-button"
              >
                ×
              </Button>
            </div>
          </CardHeader>

          <CardContent className="space-y-6">
            {/* Selection Summary */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Selected Notifications</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-muted/50 rounded-lg">
                  <div className="text-2xl font-bold neural-text">{selectedNotifications.length}</div>
                  <div className="text-sm text-muted-foreground">Total Selected</div>
                </div>
                <div className="p-3 bg-muted/50 rounded-lg">
                  <div className="text-2xl font-bold text-primary">
                    {Object.keys(notificationsByType).length}
                  </div>
                  <div className="text-sm text-muted-foreground">Request Types</div>
                </div>
              </div>
            </div>

            {/* Breakdown by Type */}
            <div>
              <h4 className="font-medium mb-2">Breakdown by Request Type</h4>
              <div className="space-y-2">
                {Object.entries(notificationsByType).map(([type, notifications]) => (
                  <div key={type} className="flex items-center justify-between p-2 bg-muted/30 rounded">
                    <div className="flex items-center gap-2">
                      {getRequestTypeIcon(type)}
                      <span className="text-sm">{getRequestTypeLabel(type)}</span>
                    </div>
                    <Badge variant="secondary" className="neural-card">
                      {notifications.length}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>

            {/* Breakdown by Priority */}
            <div>
              <h4 className="font-medium mb-2">Breakdown by Priority</h4>
              <div className="space-y-2">
                {Object.entries(notificationsByPriority).map(([priority, notifications]) => (
                  <div key={priority} className="flex items-center justify-between p-2 bg-muted/30 rounded">
                    <div className="flex items-center gap-2">
                      <Badge className={cn("text-xs", getPriorityColor(priority))}>
                        {priority.toUpperCase()}
                      </Badge>
                    </div>
                    <Badge variant="secondary" className="neural-card">
                      {notifications.length}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>

            {/* Action Selection */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Select Action</h3>
              <div className="grid grid-cols-2 gap-4">
                <Button
                  variant={action === 'approve' ? 'default' : 'outline'}
                  onClick={() => setAction('approve')}
                  className={cn(
                    "neural-button h-16 flex flex-col gap-2",
                    action === 'approve' && "bg-green-600 hover:bg-green-700"
                  )}
                >
                  <CheckCircle className="w-6 h-6" />
                  <span>Approve All</span>
                </Button>
                <Button
                  variant={action === 'reject' ? 'default' : 'outline'}
                  onClick={() => setAction('reject')}
                  className={cn(
                    "neural-button h-16 flex flex-col gap-2",
                    action === 'reject' && "bg-red-600 hover:bg-red-700"
                  )}
                >
                  <XCircle className="w-6 h-6" />
                  <span>Reject All</span>
                </Button>
              </div>
            </div>

            {/* Admin Notes */}
            {action && (
              <div>
                <h4 className="font-medium mb-2 flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" />
                  Admin Notes (Optional)
                </h4>
                <Textarea
                  placeholder={`Add notes for bulk ${action} operation...`}
                  value={adminNotes}
                  onChange={(e) => setAdminNotes(e.target.value)}
                  className="min-h-[100px]"
                />
                <p className="text-sm text-muted-foreground mt-1">
                  These notes will be applied to all selected notifications.
                </p>
              </div>
            )}

            {/* Warning for High Priority */}
            {action && Object.keys(notificationsByPriority).includes('urgent') && (
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  <strong>Warning:</strong> You are about to {action} {notificationsByPriority.urgent.length} urgent requests. 
                  Please ensure this action is intentional.
                </AlertDescription>
              </Alert>
            )}

            {/* Action Buttons */}
            <div className="flex items-center justify-between pt-4 border-t">
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  onClick={onClearSelection}
                  className="neural-button"
                >
                  Clear Selection
                </Button>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  onClick={onClose}
                  className="neural-button"
                >
                  Cancel
                </Button>
                {action && (
                  <Button
                    onClick={() => handleBulkAction(action)}
                    disabled={isProcessing}
                    className={cn(
                      "neural-button",
                      action === 'approve' && "bg-green-600 hover:bg-green-700",
                      action === 'reject' && "bg-red-600 hover:bg-red-700"
                    )}
                  >
                    {isProcessing ? (
                      <>
                        <Clock className="w-4 h-4 mr-2 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Shield className="w-4 h-4 mr-2" />
                        {action === 'approve' ? 'Approve All' : 'Reject All'} ({selectedNotifications.length})
                      </>
                    )}
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};
