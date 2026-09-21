import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useEnhancedNotifications, NotificationSettings } from '@/contexts/EnhancedNotificationContext';
import { 
  Settings,
  Bell,
  Volume2,
  VolumeX,
  Monitor,
  Smartphone,
  Globe,
  RefreshCw,
  Clock,
  Shield,
  Eye,
  Zap,
  Crown,
  User,
  Save,
  RotateCcw,
  Info,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';
import { toast } from 'sonner';

interface NotificationSettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

export const NotificationSettingsModal: React.FC<NotificationSettingsProps> = ({ 
  isOpen, 
  onClose 
}) => {
  const { settings, updateSettings } = useEnhancedNotifications();
  const [localSettings, setLocalSettings] = useState<NotificationSettings>(settings);
  const [hasChanges, setHasChanges] = useState(false);

  const handleSettingChange = (key: keyof NotificationSettings, value: any) => {
    const newSettings = { ...localSettings, [key]: value };
    setLocalSettings(newSettings);
    setHasChanges(true);
  };

  const handleSave = () => {
    updateSettings(localSettings);
    setHasChanges(false);
    toast.success('Notification settings saved successfully');
  };

  const handleReset = () => {
    setLocalSettings(settings);
    setHasChanges(false);
    toast.info('Settings reset to current values');
  };

  const requestNotificationPermission = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      if (permission === 'granted') {
        toast.success('Desktop notifications enabled');
      } else {
        toast.error('Desktop notifications blocked');
      }
    }
  };

  const testNotification = () => {
    if (localSettings.soundEnabled) {
      try {
        const audio = new Audio('/notification-sound.mp3');
        audio.volume = 0.3;
        audio.play();
      } catch (error) {
        console.error('Error playing test sound:', error);
      }
    }

    if (localSettings.desktopNotifications && 'Notification' in window) {
      if (Notification.permission === 'granted') {
        new Notification('Test Notification', {
          body: 'This is a test notification from the admin dashboard',
          icon: '/favicon.ico'
        });
      }
    }

    if (localSettings.showToastNotifications) {
      toast.info('Test Notification', {
        description: 'This is a test toast notification'
      });
    }
  };

  const refreshIntervals = [
    { value: 10000, label: '10 seconds' },
    { value: 30000, label: '30 seconds' },
    { value: 60000, label: '1 minute' },
    { value: 300000, label: '5 minutes' },
    { value: 600000, label: '10 minutes' }
  ];

  const maxNotificationsOptions = [
    { value: 25, label: '25 notifications' },
    { value: 50, label: '50 notifications' },
    { value: 100, label: '100 notifications' },
    { value: 200, label: '200 notifications' },
    { value: 500, label: '500 notifications' }
  ];

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
                  <Settings className="w-4 h-4 text-primary" />
                </div>
                Notification Settings
              </CardTitle>
              <div className="flex items-center gap-2">
                {hasChanges && (
                  <Badge variant="outline" className="neural-card text-orange-600 border-orange-600">
                    <AlertTriangle className="w-3 h-3 mr-1" />
                    Unsaved Changes
                  </Badge>
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onClose}
                  className="neural-button"
                >
                  ×
                </Button>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-6">
            {/* General Settings */}
            <div>
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Bell className="w-5 h-5" />
                General Notifications
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Show Toast Notifications</p>
                    <p className="text-sm text-muted-foreground">
                      Display toast messages for new requests
                    </p>
                  </div>
                  <Switch
                    checked={localSettings.showToastNotifications}
                    onCheckedChange={(checked) => handleSettingChange('showToastNotifications', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Sound Notifications</p>
                    <p className="text-sm text-muted-foreground">
                      Play sound when new requests arrive
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {localSettings.soundEnabled ? (
                      <Volume2 className="w-4 h-4 text-green-600" />
                    ) : (
                      <VolumeX className="w-4 h-4 text-muted-foreground" />
                    )}
                    <Switch
                      checked={localSettings.soundEnabled}
                      onCheckedChange={(checked) => handleSettingChange('soundEnabled', checked)}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Desktop Notifications</p>
                    <p className="text-sm text-muted-foreground">
                      Show browser desktop notifications
                    </p>
                    {Notification.permission !== 'granted' && (
                      <Alert className="mt-2">
                        <Info className="h-4 w-4" />
                        <AlertDescription>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={requestNotificationPermission}
                            className="neural-button mt-2"
                          >
                            Enable Desktop Notifications
                          </Button>
                        </AlertDescription>
                      </Alert>
                    )}
                  </div>
                  <Switch
                    checked={localSettings.desktopNotifications}
                    onCheckedChange={(checked) => handleSettingChange('desktopNotifications', checked)}
                  />
                </div>
              </div>
            </div>

            {/* Auto Refresh Settings */}
            <div>
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <RefreshCw className="w-5 h-5" />
                Auto Refresh
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Enable Auto Refresh</p>
                    <p className="text-sm text-muted-foreground">
                      Automatically refresh notifications at intervals
                    </p>
                  </div>
                  <Switch
                    checked={localSettings.autoRefresh}
                    onCheckedChange={(checked) => handleSettingChange('autoRefresh', checked)}
                  />
                </div>

                {localSettings.autoRefresh && (
                  <div>
                    <p className="font-medium mb-2">Refresh Interval</p>
                    <Select
                      value={localSettings.refreshInterval.toString()}
                      onValueChange={(value) => handleSettingChange('refreshInterval', parseInt(value))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {refreshIntervals.map((interval) => (
                          <SelectItem key={interval.value} value={interval.value.toString()}>
                            {interval.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </div>
            </div>

            {/* Display Settings */}
            <div>
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Eye className="w-5 h-5" />
                Display Settings
              </h3>
              <div className="space-y-4">
                <div>
                  <p className="font-medium mb-2">Maximum Notifications to Show</p>
                  <Select
                    value={localSettings.maxNotificationsToShow.toString()}
                    onValueChange={(value) => handleSettingChange('maxNotificationsToShow', parseInt(value))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {maxNotificationsOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value.toString()}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="text-sm text-muted-foreground mt-1">
                    Older notifications will be automatically removed
                  </p>
                </div>
              </div>
            </div>

            {/* Filter Settings */}
            <div>
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Default Filters
              </h3>
              <div className="space-y-4">
                <div>
                  <p className="font-medium mb-2">Priority Levels</p>
                  <div className="grid grid-cols-2 gap-2">
                    {['urgent', 'high', 'medium', 'low'].map((priority) => (
                      <div key={priority} className="flex items-center space-x-2">
                        <Checkbox
                          id={`priority-${priority}`}
                          checked={localSettings.priorityFilter.includes(priority)}
                          onCheckedChange={(checked) => {
                            const newFilter = checked
                              ? [...localSettings.priorityFilter, priority]
                              : localSettings.priorityFilter.filter(p => p !== priority);
                            handleSettingChange('priorityFilter', newFilter);
                          }}
                        />
                        <label
                          htmlFor={`priority-${priority}`}
                          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 capitalize"
                        >
                          {priority}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="font-medium mb-2">Request Types</p>
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { value: 'try_access', label: 'Try Access', icon: Eye },
                      { value: 'detection_access', label: 'Detection Access', icon: Zap },
                      { value: 'premium_upgrade', label: 'Premium Upgrade', icon: Crown },
                      { value: 'signup_verification', label: 'Signup Verification', icon: User }
                    ].map(({ value, label, icon: Icon }) => (
                      <div key={value} className="flex items-center space-x-2">
                        <Checkbox
                          id={`type-${value}`}
                          checked={localSettings.requestTypeFilter.includes(value)}
                          onCheckedChange={(checked) => {
                            const newFilter = checked
                              ? [...localSettings.requestTypeFilter, value]
                              : localSettings.requestTypeFilter.filter(t => t !== value);
                            handleSettingChange('requestTypeFilter', newFilter);
                          }}
                        />
                        <label
                          htmlFor={`type-${value}`}
                          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 flex items-center gap-1"
                        >
                          <Icon className="w-3 h-3" />
                          {label}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Test Section */}
            <div>
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                Test Notifications
              </h3>
              <div className="p-4 bg-muted/50 rounded-lg">
                <p className="text-sm text-muted-foreground mb-3">
                  Test your notification settings to ensure they're working correctly.
                </p>
                <Button
                  onClick={testNotification}
                  className="neural-button"
                >
                  Send Test Notification
                </Button>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-between pt-4 border-t">
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  onClick={handleReset}
                  disabled={!hasChanges}
                  className="neural-button"
                >
                  <RotateCcw className="w-4 h-4 mr-2" />
                  Reset
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
                <Button
                  onClick={handleSave}
                  disabled={!hasChanges}
                  className="neural-button"
                >
                  <Save className="w-4 h-4 mr-2" />
                  Save Settings
                </Button>
              </div>
            </div>
          </CardContent>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};
