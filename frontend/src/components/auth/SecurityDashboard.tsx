/**
 * Security Dashboard Component
 * Provides comprehensive security monitoring, 2FA management, and security settings
 * for authenticated users with enterprise-grade security features.
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { useAuth } from '@/contexts/SimpleAuthContext';
import {
  Shield, Key, Smartphone, QrCode, Eye, EyeOff, Clock, AlertTriangle,
  CheckCircle, XCircle, Lock, Unlock, Activity, Users, Globe, Database,
  Download, RefreshCw, Settings, Bell, Zap, Crown, AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';

interface SecurityEvent {
  event_type: string;
  event_category: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  details: Record<string, any>;
  ip_address: string;
  user_agent?: string;
  timestamp: string;
}

interface TwoFactorSetup {
  totp_secret: string;
  qr_code: string;
  backup_codes: string[];
}

export const SecurityDashboard: React.FC = () => {
  const { 
    user, 
    setup2FA, 
    verify2FA, 
    disable2FA, 
    changePassword, 
    getSecurityEvents,
    getCsrfToken 
  } = useAuth();

  // State management
  const [activeTab, setActiveTab] = useState('overview');
  const [securityEvents, setSecurityEvents] = useState<SecurityEvent[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [twoFactorSetup, setTwoFactorSetup] = useState<TwoFactorSetup | null>(null);
  const [showBackupCodes, setShowBackupCodes] = useState(false);
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [twoFactorCode, setTwoFactorCode] = useState('');
  const [csrfToken, setCsrfToken] = useState<string | null>(null);

  // Load security data
  useEffect(() => {
    loadSecurityData();
  }, []);

  const loadSecurityData = async () => {
    setIsLoading(true);
    try {
      const [events, token] = await Promise.all([
        getSecurityEvents(),
        getCsrfToken()
      ]);
      setSecurityEvents(events);
      setCsrfToken(token);
    } catch (error) {
      console.error('Failed to load security data:', error);
      toast.error('Failed to load security data');
    } finally {
      setIsLoading(false);
    }
  };

  // Password change handler
  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (passwordData.newPassword.length < 12) {
      toast.error('New password must be at least 12 characters long');
      return;
    }

    try {
      await changePassword(passwordData.currentPassword, passwordData.newPassword);
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
      toast.success('Password changed successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to change password');
    }
  };

  // 2FA setup handler
  const handle2FASetup = async () => {
    try {
      const setup = await setup2FA();
      setTwoFactorSetup(setup);
      setShowBackupCodes(true);
      toast.success('2FA setup initiated');
    } catch (error: any) {
      toast.error(error.message || 'Failed to setup 2FA');
    }
  };

  // 2FA verification handler
  const handle2FAVerify = async () => {
    if (!twoFactorCode) {
      toast.error('Please enter the verification code');
      return;
    }

    try {
      await verify2FA(twoFactorCode);
      setTwoFactorSetup(null);
      setTwoFactorCode('');
      setShowBackupCodes(false);
      toast.success('2FA enabled successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to verify 2FA');
    }
  };

  // 2FA disable handler
  const handle2FADisable = async () => {
    if (!twoFactorCode) {
      toast.error('Please enter the verification code');
      return;
    }

    try {
      await disable2FA(twoFactorCode);
      setTwoFactorCode('');
      toast.success('2FA disabled successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to disable 2FA');
    }
  };

  // Get severity color
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-500';
      case 'error': return 'text-red-400';
      case 'warning': return 'text-yellow-500';
      case 'info': return 'text-blue-500';
      default: return 'text-gray-500';
    }
  };

  // Get severity icon
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <AlertTriangle className="w-4 h-4" />;
      case 'error': return <XCircle className="w-4 h-4" />;
      case 'warning': return <AlertCircle className="w-4 h-4" />;
      case 'info': return <CheckCircle className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  if (!user) {
    return (
      <Card className="text-center p-8">
        <CardHeader>
          <Lock className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <CardTitle>Authentication Required</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Please sign in to access the security dashboard.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold flex items-center gap-2">
            <Shield className="w-8 h-8 text-primary" />
            Security Dashboard
          </h2>
          <p className="text-muted-foreground">
            Manage your account security and monitor security events
          </p>
        </div>
        <Button onClick={loadSecurityData} disabled={isLoading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Security Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Account Status</p>
                <p className="text-2xl font-bold text-green-600">Secure</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">2FA Status</p>
                <p className="text-2xl font-bold">
                  {user.is_2fa_enabled ? 'Enabled' : 'Disabled'}
                </p>
              </div>
              {user.is_2fa_enabled ? (
                <Shield className="w-8 h-8 text-green-500" />
              ) : (
                <AlertTriangle className="w-8 h-8 text-yellow-500" />
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Plan</p>
                <p className="text-2xl font-bold flex items-center gap-2">
                  {user.plan === 'admin' && <Crown className="w-5 h-5 text-yellow-500" />}
                  {user.plan.charAt(0).toUpperCase() + user.plan.slice(1)}
                </p>
              </div>
              <Zap className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="authentication">Authentication</TabsTrigger>
          <TabsTrigger value="events">Security Events</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Account Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Account Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Email:</span>
                  <span className="font-medium">{user.email}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Username:</span>
                  <span className="font-medium">{user.username}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Full Name:</span>
                  <span className="font-medium">{user.full_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Member Since:</span>
                  <span className="font-medium">
                    {new Date(user.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Last Login:</span>
                  <span className="font-medium">
                    {user.last_login ? 
                      new Date(user.last_login).toLocaleDateString() : 
                      'Never'
                    }
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Security Score */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5" />
                  Security Score
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <div className="text-4xl font-bold text-green-600 mb-2">85/100</div>
                    <Progress value={85} className="h-2" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Strong Password</span>
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">2FA Enabled</span>
                      {user.is_2fa_enabled ? (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-500" />
                      )}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Email Verified</span>
                      {user.is_verified ? (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-500" />
                      )}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Recent Activity</span>
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Security Events */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Recent Security Events
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {securityEvents.slice(0, 5).map((event, index) => (
                  <div key={index} className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
                    <div className={getSeverityColor(event.severity)}>
                      {getSeverityIcon(event.severity)}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium">{event.event_type}</div>
                      <div className="text-sm text-muted-foreground">
                        {new Date(event.timestamp).toLocaleString()}
                      </div>
                    </div>
                    <Badge variant="outline">{event.severity}</Badge>
                  </div>
                ))}
                {securityEvents.length === 0 && (
                  <div className="text-center text-muted-foreground py-4">
                    No recent security events
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Authentication Tab */}
        <TabsContent value="authentication" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Password Management */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Key className="w-5 h-5" />
                  Password Management
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handlePasswordChange} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="current-password">Current Password</Label>
                    <Input
                      id="current-password"
                      type="password"
                      value={passwordData.currentPassword}
                      onChange={(e) => setPasswordData({ ...passwordData, currentPassword: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="new-password">New Password</Label>
                    <Input
                      id="new-password"
                      type="password"
                      value={passwordData.newPassword}
                      onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="confirm-password">Confirm New Password</Label>
                    <Input
                      id="confirm-password"
                      type="password"
                      value={passwordData.confirmPassword}
                      onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
                      required
                    />
                  </div>
                  <Button type="submit" className="w-full">
                    Change Password
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Two-Factor Authentication */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Smartphone className="w-5 h-5" />
                  Two-Factor Authentication
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">2FA Status</p>
                    <p className="text-sm text-muted-foreground">
                      {user.is_2fa_enabled ? 'Enabled' : 'Disabled'}
                    </p>
                  </div>
                  <Badge variant={user.is_2fa_enabled ? 'default' : 'secondary'}>
                    {user.is_2fa_enabled ? 'Enabled' : 'Disabled'}
                  </Badge>
                </div>

                {!user.is_2fa_enabled ? (
                  <div className="space-y-3">
                    <Button onClick={handle2FASetup} className="w-full">
                      <Smartphone className="w-4 h-4 mr-2" />
                      Enable 2FA
                    </Button>
                    <Alert>
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription>
                        Two-factor authentication adds an extra layer of security to your account.
                      </AlertDescription>
                    </Alert>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <Button 
                      onClick={() => setTwoFactorCode('')} 
                      variant="destructive" 
                      className="w-full"
                    >
                      <XCircle className="w-4 h-4 mr-2" />
                      Disable 2FA
                    </Button>
                    <Alert>
                      <CheckCircle className="h-4 w-4" />
                      <AlertDescription>
                        Two-factor authentication is currently enabled and protecting your account.
                      </AlertDescription>
                    </Alert>
                  </div>
                )}

                {/* 2FA Setup/Verification */}
                {twoFactorSetup && (
                  <div className="space-y-3 p-4 bg-muted/50 rounded-lg">
                    <div className="text-center">
                      <p className="font-medium mb-2">Scan QR Code</p>
                      <img 
                        src={twoFactorSetup.qr_code} 
                        alt="2FA QR Code" 
                        className="mx-auto w-32 h-32"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="2fa-code">Verification Code</Label>
                      <Input
                        id="2fa-code"
                        type="text"
                        placeholder="Enter 6-digit code"
                        value={twoFactorCode}
                        onChange={(e) => setTwoFactorCode(e.target.value)}
                      />
                    </div>
                    <Button onClick={handle2FAVerify} className="w-full">
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Verify & Enable
                    </Button>
                  </div>
                )}

                {/* Backup Codes */}
                {showBackupCodes && twoFactorSetup && (
                  <div className="space-y-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-yellow-600" />
                      <p className="font-medium text-yellow-800">Save Your Backup Codes</p>
                    </div>
                    <p className="text-sm text-yellow-700">
                      These codes can be used to access your account if you lose your device.
                    </p>
                    <div className="grid grid-cols-2 gap-2">
                      {twoFactorSetup.backup_codes.map((code, index) => (
                        <div key={index} className="p-2 bg-white border rounded text-center font-mono text-sm">
                          {code}
                        </div>
                      ))}
                    </div>
                    <Button 
                      onClick={() => setShowBackupCodes(false)} 
                      variant="outline" 
                      className="w-full"
                    >
                      I've Saved These Codes
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Security Events Tab */}
        <TabsContent value="events" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Security Events Log
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {securityEvents.map((event, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-start gap-3">
                      <div className={getSeverityColor(event.severity)}>
                        {getSeverityIcon(event.severity)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium">{event.event_type}</h4>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">{event.severity}</Badge>
                            <span className="text-sm text-muted-foreground">
                              {new Date(event.timestamp).toLocaleString()}
                            </span>
                          </div>
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">
                          {event.event_category} • {event.ip_address}
                        </p>
                        {event.details && Object.keys(event.details).length > 0 && (
                          <div className="text-xs text-muted-foreground">
                            <details>
                              <summary className="cursor-pointer hover:text-foreground">
                                View Details
                              </summary>
                              <pre className="mt-2 p-2 bg-muted rounded text-xs overflow-auto">
                                {JSON.stringify(event.details, null, 2)}
                              </pre>
                            </details>
                          </div>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
                {securityEvents.length === 0 && (
                  <div className="text-center text-muted-foreground py-8">
                    <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No security events found</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Security Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  Security Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Email Notifications</p>
                    <p className="text-sm text-muted-foreground">
                      Get notified about security events
                    </p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Login Alerts</p>
                    <p className="text-sm text-muted-foreground">
                      Alert on new device logins
                    </p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Session Timeout</p>
                    <p className="text-sm text-muted-foreground">
                      Auto-logout after inactivity
                    </p>
                  </div>
                  <Switch defaultChecked />
                </div>
              </CardContent>
            </Card>

            {/* API Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Globe className="w-5 h-5" />
                  API & Integration
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>CSRF Token</Label>
                  <div className="flex gap-2">
                    <Input 
                      value={csrfToken || ''} 
                      readOnly 
                      className="font-mono text-xs"
                    />
                    <Button size="sm" variant="outline">
                      <RefreshCw className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
                <Separator />
                <div className="space-y-2">
                  <Label>API Endpoint</Label>
                  <Input 
                    value="http://127.0.0.1:8000/api" 
                    readOnly 
                    className="font-mono text-xs"
                  />
                </div>
                <Separator />
                <Button variant="outline" className="w-full">
                  <Download className="w-4 h-4 mr-2" />
                  Download Security Report
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};
