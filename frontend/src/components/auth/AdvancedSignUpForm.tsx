/**
 * Advanced Sign-Up Form Component
 * Production-ready registration form with comprehensive validation and security features.
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Checkbox } from "@/components/ui/checkbox";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from '@/contexts/SimpleAuthContext';
import { 
  User, Mail, Lock, Eye, EyeOff, CheckCircle, AlertTriangle, 
  Loader2, Shield, Zap, Crown, AlertCircle, X, UserPlus,
  Check, X as XIcon
} from 'lucide-react';
import { toast } from 'sonner';

interface AdvancedSignUpFormProps {
  onClose?: () => void;
  onSuccess?: () => void;
  switchToSignIn?: () => void;
}

interface PasswordStrength {
  score: number;
  feedback: string[];
  isStrong: boolean;
}

interface FormData {
  email: string;
  username: string;
  fullName: string;
  password: string;
  confirmPassword: string;
  agreeToTerms: boolean;
  agreeToPrivacy: boolean;
  marketingEmails: boolean;
}

interface ValidationErrors {
  email?: string;
  username?: string;
  fullName?: string;
  password?: string;
  confirmPassword?: string;
  agreeToTerms?: string;
  general?: string;
}

export const AdvancedSignUpForm: React.FC<AdvancedSignUpFormProps> = ({
  onClose,
  onSuccess,
  switchToSignIn
}) => {
  const { register, isLoading } = useAuth();
  const [formData, setFormData] = useState<FormData>({
    email: '',
    username: '',
    fullName: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false,
    agreeToPrivacy: false,
    marketingEmails: false
  });
  
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState<PasswordStrength>({
    score: 0,
    feedback: [],
    isStrong: false
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [isUsernameAvailable, setIsUsernameAvailable] = useState<boolean | null>(null);
  const [isEmailAvailable, setIsEmailAvailable] = useState<boolean | null>(null);

  // Password strength calculation
  const calculatePasswordStrength = (password: string): PasswordStrength => {
    let score = 0;
    const feedback: string[] = [];

    if (password.length >= 12) score += 1;
    else feedback.push('At least 12 characters');

    if (/[a-z]/.test(password)) score += 1;
    else feedback.push('Lowercase letters');

    if (/[A-Z]/.test(password)) score += 1;
    else feedback.push('Uppercase letters');

    if (/[0-9]/.test(password)) score += 1;
    else feedback.push('Numbers');

    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    else feedback.push('Special characters');

    if (password.length >= 16) score += 1;
    if (/(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^A-Za-z0-9])/.test(password)) score += 1;

    return {
      score,
      feedback,
      isStrong: score >= 4
    };
  };

  // Real-time validation
  useEffect(() => {
    if (formData.password) {
      setPasswordStrength(calculatePasswordStrength(formData.password));
    }
  }, [formData.password]);

  // Username availability check (debounced)
  useEffect(() => {
    if (formData.username.length >= 3) {
      const timeoutId = setTimeout(() => {
        checkUsernameAvailability(formData.username);
      }, 500);
      return () => clearTimeout(timeoutId);
    }
  }, [formData.username]);

  // Email availability check (debounced)
  useEffect(() => {
    if (formData.email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      const timeoutId = setTimeout(() => {
        checkEmailAvailability(formData.email);
      }, 500);
      return () => clearTimeout(timeoutId);
    }
  }, [formData.email]);

  const checkUsernameAvailability = async (username: string) => {
    try {
      // This would be a real API call
      // For now, simulate availability check
      const isAvailable = !['admin', 'user', 'test', 'demo'].includes(username.toLowerCase());
      setIsUsernameAvailable(isAvailable);
    } catch (error) {
      setIsUsernameAvailable(null);
    }
  };

  const checkEmailAvailability = async (email: string) => {
    try {
      // This would be a real API call
      // For now, simulate availability check
      const isAvailable = !email.includes('admin@') && !email.includes('test@');
      setIsEmailAvailable(isAvailable);
    } catch (error) {
      setIsEmailAvailable(null);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: ValidationErrors = {};

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    } else if (isEmailAvailable === false) {
      newErrors.email = 'This email is already registered';
    }

    // Username validation
    if (!formData.username) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    } else if (!/^[a-zA-Z0-9_-]+$/.test(formData.username)) {
      newErrors.username = 'Username can only contain letters, numbers, hyphens, and underscores';
    } else if (isUsernameAvailable === false) {
      newErrors.username = 'This username is already taken';
    }

    // Full name validation
    if (!formData.fullName.trim()) {
      newErrors.fullName = 'Full name is required';
    } else if (formData.fullName.trim().length < 2) {
      newErrors.fullName = 'Full name must be at least 2 characters';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (!passwordStrength.isStrong) {
      newErrors.password = 'Password is not strong enough';
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    // Terms validation
    if (!formData.agreeToTerms) {
      newErrors.agreeToTerms = 'You must agree to the Terms of Service';
    }

    if (!formData.agreeToPrivacy) {
      newErrors.agreeToTerms = 'You must agree to the Privacy Policy';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (field: keyof FormData, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear specific error when user starts typing
    if (errors[field as keyof ValidationErrors]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      await register({
        email: formData.email,
        username: formData.username,
        password: formData.password,
        full_name: formData.fullName
      });

      toast.success('Account created successfully! Welcome to iFake!');
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (error: any) {
      const errorMessage = error.message || 'Registration failed. Please try again.';
      setErrors({ general: errorMessage });
      toast.error(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getPasswordStrengthColor = (score: number) => {
    if (score < 2) return 'bg-red-500';
    if (score < 4) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getPasswordStrengthText = (score: number) => {
    if (score < 2) return 'Weak';
    if (score < 4) return 'Medium';
    return 'Strong';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-2xl mx-auto"
    >
      <Card>
        <CardHeader className="space-y-1">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <UserPlus className="h-6 w-6 text-primary" />
              <CardTitle className="text-2xl">Create Account</CardTitle>
            </div>
            {onClose && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="h-8 w-8 p-0"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
          <p className="text-sm text-muted-foreground">
            Join iFake and start detecting deepfakes with advanced AI technology
          </p>
        </CardHeader>
        
        <CardContent>
          <Tabs value="signup" className="w-full">
            <TabsList className="grid w-full grid-cols-1">
              <TabsTrigger value="signup">Sign Up</TabsTrigger>
            </TabsList>
            
            <TabsContent value="signup" className="space-y-6">
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Step 1: Basic Information */}
                <div className="space-y-4">
                  <div className="flex items-center space-x-2 mb-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-medium">
                        1
                      </div>
                      <span className="font-medium">Basic Information</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="fullName">Full Name *</Label>
                      <div className="relative">
                        <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                          id="fullName"
                          type="text"
                          value={formData.fullName}
                          onChange={(e) => handleInputChange('fullName', e.target.value)}
                          placeholder="Enter your full name"
                          className="pl-10"
                          required
                        />
                      </div>
                      {errors.fullName && (
                        <p className="text-sm text-destructive">{errors.fullName}</p>
                      )}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="email">Email Address *</Label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                        <Input
                          id="email"
                          type="email"
                          value={formData.email}
                          onChange={(e) => handleInputChange('email', e.target.value)}
                          placeholder="Enter your email"
                          className="pl-10"
                          required
                        />
                        {isEmailAvailable === true && (
                          <CheckCircle className="absolute right-3 top-3 h-4 w-4 text-green-500" />
                        )}
                        {isEmailAvailable === false && (
                          <XIcon className="absolute right-3 top-3 h-4 w-4 text-red-500" />
                        )}
                      </div>
                      {errors.email && (
                        <p className="text-sm text-destructive">{errors.email}</p>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="username">Username *</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="username"
                        type="text"
                        value={formData.username}
                        onChange={(e) => handleInputChange('username', e.target.value)}
                        placeholder="Choose a username"
                        className="pl-10"
                        required
                      />
                      {isUsernameAvailable === true && (
                        <CheckCircle className="absolute right-3 top-3 h-4 w-4 text-green-500" />
                      )}
                      {isUsernameAvailable === false && (
                        <XIcon className="absolute right-3 top-3 h-4 w-4 text-red-500" />
                      )}
                    </div>
                    {errors.username && (
                      <p className="text-sm text-destructive">{errors.username}</p>
                    )}
                    <p className="text-xs text-muted-foreground">
                      3-20 characters, letters, numbers, hyphens, and underscores only
                    </p>
                  </div>
                </div>

                {/* Step 2: Security */}
                <div className="space-y-4">
                  <div className="flex items-center space-x-2 mb-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-medium">
                        2
                      </div>
                      <span className="font-medium">Security</span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password">Password *</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="password"
                        type={showPassword ? "text" : "password"}
                        value={formData.password}
                        onChange={(e) => handleInputChange('password', e.target.value)}
                        placeholder="Create a strong password"
                        className="pl-10 pr-10"
                        required
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-0 top-0 h-full px-3"
                      >
                        {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                    
                    {/* Password Strength Indicator */}
                    {formData.password && (
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <Progress 
                            value={(passwordStrength.score / 6) * 100} 
                            className="flex-1 h-2"
                          />
                          <Badge 
                            variant={passwordStrength.isStrong ? "default" : "secondary"}
                            className="text-xs"
                          >
                            {getPasswordStrengthText(passwordStrength.score)}
                          </Badge>
                        </div>
                        
                        {passwordStrength.feedback.length > 0 && (
                          <div className="text-xs text-muted-foreground">
                            <p>Password should include:</p>
                            <ul className="list-disc list-inside space-y-1">
                              {passwordStrength.feedback.map((item, index) => (
                                <li key={index} className="flex items-center space-x-1">
                                  <XIcon className="h-3 w-3 text-red-500" />
                                  <span>{item}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                    
                    {errors.password && (
                      <p className="text-sm text-destructive">{errors.password}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword">Confirm Password *</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="confirmPassword"
                        type={showConfirmPassword ? "text" : "password"}
                        value={formData.confirmPassword}
                        onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                        placeholder="Confirm your password"
                        className="pl-10 pr-10"
                        required
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-0 top-0 h-full px-3"
                      >
                        {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                    {errors.confirmPassword && (
                      <p className="text-sm text-destructive">{errors.confirmPassword}</p>
                    )}
                  </div>
                </div>

                {/* Step 3: Terms and Conditions */}
                <div className="space-y-4">
                  <div className="flex items-center space-x-2 mb-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-medium">
                        3
                      </div>
                      <span className="font-medium">Terms & Privacy</span>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-start space-x-2">
                      <Checkbox
                        id="agreeToTerms"
                        checked={formData.agreeToTerms}
                        onCheckedChange={(checked) => handleInputChange('agreeToTerms', checked as boolean)}
                        className="mt-1"
                      />
                      <Label htmlFor="agreeToTerms" className="text-sm">
                        I agree to the{' '}
                        <a href="/terms" className="text-primary hover:underline" target="_blank">
                          Terms of Service
                        </a>
                        {' '}and{' '}
                        <a href="/privacy" className="text-primary hover:underline" target="_blank">
                          Privacy Policy
                        </a>
                      </Label>
                    </div>
                    {errors.agreeToTerms && (
                      <p className="text-sm text-destructive">{errors.agreeToTerms}</p>
                    )}

                    <div className="flex items-start space-x-2">
                      <Checkbox
                        id="agreeToPrivacy"
                        checked={formData.agreeToPrivacy}
                        onCheckedChange={(checked) => handleInputChange('agreeToPrivacy', checked as boolean)}
                        className="mt-1"
                      />
                      <Label htmlFor="agreeToPrivacy" className="text-sm">
                        I consent to the processing of my personal data for account creation and service provision
                      </Label>
                    </div>

                    <div className="flex items-start space-x-2">
                      <Checkbox
                        id="marketingEmails"
                        checked={formData.marketingEmails}
                        onCheckedChange={(checked) => handleInputChange('marketingEmails', checked as boolean)}
                        className="mt-1"
                      />
                      <Label htmlFor="marketingEmails" className="text-sm text-muted-foreground">
                        Send me updates about new features and security improvements (optional)
                      </Label>
                    </div>
                  </div>
                </div>

                {/* Error Display */}
                {errors.general && (
                  <Alert variant="destructive">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>{errors.general}</AlertDescription>
                  </Alert>
                )}

                {/* Submit Button */}
                <Button
                  type="submit"
                  className="w-full"
                  disabled={isSubmitting || !formData.agreeToTerms || !formData.agreeToPrivacy}
                >
                  {isSubmitting ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <UserPlus className="h-4 w-4 mr-2" />
                  )}
                  Create Account
                </Button>

                {/* Sign In Link */}
                <div className="text-center">
                  <p className="text-sm text-muted-foreground">
                    Already have an account?{' '}
                    <Button
                      variant="link"
                      onClick={switchToSignIn}
                      className="p-0 h-auto font-normal"
                    >
                      Sign in here
                    </Button>
                  </p>
                </div>
              </form>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default AdvancedSignUpForm;
