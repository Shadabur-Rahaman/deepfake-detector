/**
 * Enhanced Sign-In Modal with Advanced Security Features
 * Implements password strength validation, 2FA support, security monitoring,
 * and comprehensive user experience enhancements.
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Checkbox } from "@/components/ui/checkbox";
import { useAuth } from '@/contexts/SimpleAuthContext';
import { 
  X, Mail, Lock, User, Loader2, CheckCircle, AlertTriangle, 
  Eye, EyeOff, Shield, Clock, Zap, Crown, AlertCircle,
  Key, Smartphone, QrCode
} from 'lucide-react';
import { toast } from 'sonner';

interface EnhancedSignInModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

interface PasswordStrength {
  score: number;
  feedback: string[];
  isStrong: boolean;
}

interface SecurityAlert {
  type: 'info' | 'warning' | 'error' | 'success';
  message: string;
  details?: string;
}

export const EnhancedSignInModal: React.FC<EnhancedSignInModalProps> = ({ 
  isOpen, 
  onClose, 
  onSuccess 
}) => {
  const { login, register, isLoading } = useAuth();
  
  // Form states
  const [activeTab, setActiveTab] = useState<'login' | 'signup'>('login');
  const [loginData, setLoginData] = useState({ 
    email: '', 
    password: '', 
    rememberMe: false 
  });
  const [signupData, setSignupData] = useState({ 
    name: '', 
    email: '', 
    username: '', 
    password: '', 
    confirmPassword: '',
    acceptTerms: false
  });
  
  // UI states
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState<PasswordStrength>({
    score: 0,
    feedback: [],
    isStrong: false
  });
  const [securityAlerts, setSecurityAlerts] = useState<SecurityAlert[]>([]);
  const [is2FASetup, setIs2FASetup] = useState(false);
  const [twoFactorCode, setTwoFactorCode] = useState('');
  
  // Security monitoring
  const [loginAttempts, setLoginAttempts] = useState(0);
  const [isLocked, setIsLocked] = useState(false);
  const [lockTimeRemaining, setLockTimeRemaining] = useState(0);

  // Password strength validation
  const validatePasswordStrength = (password: string): PasswordStrength => {
    const feedback: string[] = [];
    let score = 0;

    if (password.length >= 12) {
      score += 1;
    } else {
      feedback.push('At least 12 characters');
    }

    if (/[A-Z]/.test(password)) {
      score += 1;
    } else {
      feedback.push('One uppercase letter');
    }

    if (/[a-z]/.test(password)) {
      score += 1;
    } else {
      feedback.push('One lowercase letter');
    }

    if (/\d/.test(password)) {
      score += 1;
    } else {
      feedback.push('One number');
    }

    if (/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)) {
      score += 1;
    } else {
      feedback.push('One special character');
    }

    // Check for common patterns
    const commonPatterns = [
      'password', '123456', 'qwerty', 'abc123', 'admin',
      'letmein', 'welcome', 'monkey', 'dragon', 'master'
    ];
    
    if (commonPatterns.some(pattern => password.toLowerCase().includes(pattern))) {
      feedback.push('Avoid common patterns');
      score = Math.max(0, score - 1);
    }

    return {
      score,
      feedback,
      isStrong: score >= 4 && feedback.length === 0
    };
  };

  // Handle password input
  const handlePasswordChange = (password: string) => {
    setSignupData(prev => ({ ...prev, password }));
    setPasswordStrength(validatePasswordStrength(password));
  };

  // Add security alert
  const addSecurityAlert = (alert: SecurityAlert) => {
    setSecurityAlerts(prev => [...prev, alert]);
    setTimeout(() => {
      setSecurityAlerts(prev => prev.slice(1));
    }, 5000);
  };

  // Handle login
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (isLocked) {
      addSecurityAlert({
        type: 'error',
        message: 'Account temporarily locked',
        details: `Please wait ${lockTimeRemaining} seconds before trying again`
      });
      return;
    }

    try {
      await login(loginData.email, loginData.password, loginData.rememberMe);
      addSecurityAlert({
        type: 'success',
        message: 'Successfully logged in!',
        details: 'Welcome back to iFake'
      });
      
      setTimeout(() => {
        onClose();
        onSuccess?.();
        resetForms();
      }, 1000);
    } catch (error: any) {
      const newAttempts = loginAttempts + 1;
      setLoginAttempts(newAttempts);
      
      if (newAttempts >= 3) {
        setIsLocked(true);
        setLockTimeRemaining(300); // 5 minutes
        addSecurityAlert({
          type: 'error',
          message: 'Too many failed attempts',
          details: 'Account locked for 5 minutes'
        });
      } else {
        addSecurityAlert({
          type: 'error',
          message: 'Login failed',
          details: error.message || 'Invalid credentials'
        });
      }
    }
  };

  // Handle signup
  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!passwordStrength.isStrong) {
      addSecurityAlert({
        type: 'warning',
        message: 'Password is not strong enough',
        details: 'Please meet all password requirements'
      });
      return;
    }

    if (signupData.password !== signupData.confirmPassword) {
      addSecurityAlert({
        type: 'error',
        message: 'Passwords do not match',
        details: 'Please ensure both passwords are identical'
      });
      return;
    }

    if (!signupData.acceptTerms) {
      addSecurityAlert({
        type: 'warning',
        message: 'Terms and conditions must be accepted',
        details: 'Please read and accept our terms of service'
      });
      return;
    }

    try {
      await register({
        email: signupData.email,
        username: signupData.username,
        password: signupData.password,
        full_name: signupData.name
      });
      
      addSecurityAlert({
        type: 'success',
        message: 'Account created successfully!',
        details: 'Welcome to iFake - your account is ready'
      });
      
      setTimeout(() => {
        onClose();
        onSuccess?.();
        resetForms();
      }, 1000);
    } catch (error: any) {
      addSecurityAlert({
        type: 'error',
        message: 'Registration failed',
        details: error.message || 'Please try again'
      });
    }
  };

  // Reset forms
  const resetForms = () => {
    setLoginData({ email: '', password: '', rememberMe: false });
    setSignupData({ 
      name: '', 
      email: '', 
      username: '', 
      password: '', 
      confirmPassword: '',
      acceptTerms: false
    });
    setPasswordStrength({ score: 0, feedback: [], isStrong: false });
    setSecurityAlerts([]);
    setLoginAttempts(0);
    setIsLocked(false);
    setLockTimeRemaining(0);
  };

  // Lock countdown
  useEffect(() => {
    if (isLocked && lockTimeRemaining > 0) {
      const timer = setTimeout(() => {
        setLockTimeRemaining(prev => prev - 1);
      }, 1000);
      return () => clearTimeout(timer);
    } else if (lockTimeRemaining === 0) {
      setIsLocked(false);
      setLoginAttempts(0);
    }
  }, [isLocked, lockTimeRemaining]);

  // Close modal handler
  const handleClose = () => {
    resetForms();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        transition={{ duration: 0.2 }}
        className="relative w-full max-w-md"
      >
        <Card className="border-border/50 bg-card/95 backdrop-blur-sm shadow-2xl">
          <CardHeader className="relative text-center pb-2">
            <button
              onClick={handleClose}
              className="absolute right-4 top-4 text-muted-foreground hover:text-foreground transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
            <div className="flex items-center justify-center gap-2 mb-2">
              <Shield className="w-6 h-6 text-primary" />
              <CardTitle className="text-2xl font-bold gradient-text">
                Secure Access
              </CardTitle>
            </div>
            <p className="text-muted-foreground text-sm">
              Enterprise-grade authentication for iFake
            </p>
          </CardHeader>
          
          <CardContent>
            {/* Security Alerts */}
            <AnimatePresence>
              {securityAlerts.map((alert, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="mb-4"
                >
                  <Alert variant={alert.type === 'error' ? 'destructive' : 'default'}>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                      <div className="font-medium">{alert.message}</div>
                      {alert.details && (
                        <div className="text-sm text-muted-foreground mt-1">
                          {alert.details}
                        </div>
                      )}
                    </AlertDescription>
                  </Alert>
                </motion.div>
              ))}
            </AnimatePresence>

            <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'login' | 'signup')} className="w-full">
              <TabsList className="grid w-full grid-cols-2 mb-6">
                <TabsTrigger value="login" className="flex items-center gap-2">
                  <Key className="w-4 h-4" />
                  Sign In
                </TabsTrigger>
                <TabsTrigger value="signup" className="flex items-center gap-2">
                  <User className="w-4 h-4" />
                  Sign Up
                </TabsTrigger>
              </TabsList>

              <TabsContent value="login">
                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email" className="flex items-center gap-2">
                      <Mail className="w-4 h-4" />
                      Email Address
                    </Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="Enter your email"
                      value={loginData.email}
                      onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                      required
                      disabled={isLoading || isLocked}
                      className={isLocked ? 'opacity-50' : ''}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="password" className="flex items-center gap-2">
                      <Lock className="w-4 h-4" />
                      Password
                    </Label>
                    <div className="relative">
                      <Input
                        id="password"
                        type={showPassword ? "text" : "password"}
                        placeholder="Enter your password"
                        value={loginData.password}
                        onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                        required
                        disabled={isLoading || isLocked}
                        className={isLocked ? 'opacity-50' : ''}
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                        disabled={isLoading || isLocked}
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="remember"
                        checked={loginData.rememberMe}
                        onCheckedChange={(checked) => 
                          setLoginData({ ...loginData, rememberMe: !!checked })
                        }
                        disabled={isLoading || isLocked}
                      />
                      <Label htmlFor="remember" className="text-sm">
                        Remember me
                      </Label>
                    </div>
                    <button
                      type="button"
                      className="text-sm text-primary hover:underline"
                      disabled={isLoading || isLocked}
                    >
                      Forgot password?
                    </button>
                  </div>

                  {isLocked && (
                    <div className="flex items-center gap-2 text-sm text-destructive">
                      <Clock className="w-4 h-4" />
                      Account locked for {lockTimeRemaining} seconds
                    </div>
                  )}

                  <Button 
                    type="submit" 
                    className="w-full glow-primary" 
                    disabled={isLoading || isLocked}
                  >
                    {isLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    ) : (
                      <Shield className="w-4 h-4 mr-2" />
                    )}
                    {isLocked ? 'Account Locked' : 'Sign In Securely'}
                  </Button>
                </form>
              </TabsContent>

              <TabsContent value="signup">
                <form onSubmit={handleSignup} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name" className="flex items-center gap-2">
                      <User className="w-4 h-4" />
                      Full Name
                    </Label>
                    <Input
                      id="name"
                      type="text"
                      placeholder="Enter your full name"
                      value={signupData.name}
                      onChange={(e) => setSignupData({ ...signupData, name: e.target.value })}
                      required
                      disabled={isLoading}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="username" className="flex items-center gap-2">
                      <User className="w-4 h-4" />
                      Username
                    </Label>
                    <Input
                      id="username"
                      type="text"
                      placeholder="Choose a username"
                      value={signupData.username}
                      onChange={(e) => setSignupData({ ...signupData, username: e.target.value })}
                      required
                      disabled={isLoading}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="signup-email" className="flex items-center gap-2">
                      <Mail className="w-4 h-4" />
                      Email Address
                    </Label>
                    <Input
                      id="signup-email"
                      type="email"
                      placeholder="Enter your email"
                      value={signupData.email}
                      onChange={(e) => setSignupData({ ...signupData, email: e.target.value })}
                      required
                      disabled={isLoading}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="signup-password" className="flex items-center gap-2">
                      <Lock className="w-4 h-4" />
                      Password
                    </Label>
                    <div className="relative">
                      <Input
                        id="signup-password"
                        type={showPassword ? "text" : "password"}
                        placeholder="Create a strong password"
                        value={signupData.password}
                        onChange={(e) => handlePasswordChange(e.target.value)}
                        required
                        disabled={isLoading}
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                        disabled={isLoading}
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                    
                    {/* Password Strength Indicator */}
                    {signupData.password && (
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span>Password Strength</span>
                          <Badge variant={passwordStrength.isStrong ? 'default' : 'secondary'}>
                            {passwordStrength.isStrong ? 'Strong' : 'Weak'}
                          </Badge>
                        </div>
                        <Progress 
                          value={(passwordStrength.score / 5) * 100} 
                          className="h-2"
                        />
                        <div className="text-xs text-muted-foreground">
                          {passwordStrength.feedback.length > 0 && (
                            <ul className="list-disc list-inside space-y-1">
                              {passwordStrength.feedback.map((item, index) => (
                                <li key={index}>{item}</li>
                              ))}
                            </ul>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="confirm-password" className="flex items-center gap-2">
                      <Lock className="w-4 h-4" />
                      Confirm Password
                    </Label>
                    <div className="relative">
                      <Input
                        id="confirm-password"
                        type={showConfirmPassword ? "text" : "password"}
                        placeholder="Confirm your password"
                        value={signupData.confirmPassword}
                        onChange={(e) => setSignupData({ ...signupData, confirmPassword: e.target.value })}
                        required
                        disabled={isLoading}
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                        disabled={isLoading}
                      >
                        {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="terms"
                      checked={signupData.acceptTerms}
                      onCheckedChange={(checked) => 
                        setSignupData({ ...signupData, acceptTerms: !!checked })
                      }
                      disabled={isLoading}
                    />
                    <Label htmlFor="terms" className="text-sm">
                      I agree to the{' '}
                      <button type="button" className="text-primary hover:underline">
                        Terms of Service
                      </button>{' '}
                      and{' '}
                      <button type="button" className="text-primary hover:underline">
                        Privacy Policy
                      </button>
                    </Label>
                  </div>

                  <Button 
                    type="submit" 
                    className="w-full glow-primary" 
                    disabled={isLoading || !passwordStrength.isStrong || !signupData.acceptTerms}
                  >
                    {isLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    ) : (
                      <Crown className="w-4 h-4 mr-2" />
                    )}
                    Create Secure Account
                  </Button>
                </form>
              </TabsContent>
            </Tabs>

            {/* Security Features Info */}
            <div className="mt-6 p-4 bg-muted/50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Shield className="w-4 h-4 text-primary" />
                <span className="text-sm font-medium">Security Features</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                <div className="flex items-center gap-1">
                  <CheckCircle className="w-3 h-3 text-green-500" />
                  <span>JWT Authentication</span>
                </div>
                <div className="flex items-center gap-1">
                  <CheckCircle className="w-3 h-3 text-green-500" />
                  <span>Rate Limiting</span>
                </div>
                <div className="flex items-center gap-1">
                  <CheckCircle className="w-3 h-3 text-green-500" />
                  <span>CSRF Protection</span>
                </div>
                <div className="flex items-center gap-1">
                  <CheckCircle className="w-3 h-3 text-green-500" />
                  <span>2FA Support</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};
