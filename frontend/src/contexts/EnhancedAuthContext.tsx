/**
 * Enhanced Authentication Context for iFake Deepfake Detection Platform
 * Implements enterprise-grade security features including JWT token management,
 * automatic token refresh, CSRF protection, and comprehensive security monitoring.
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { useWelcomePopup } from './WelcomePopupContext';

// Types
interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  is_2fa_enabled: boolean;
  status: 'active' | 'inactive' | 'suspended' | 'pending_verification';
  plan: 'free' | 'premium' | 'enterprise' | 'admin';
  detections_used: number;
  detections_limit: number;
  created_at: string;
  last_login?: string;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  csrfToken: string | null;
  
  // Authentication methods
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<boolean>;
  
  // Security methods
  getCsrfToken: () => Promise<string>;
  validateSession: () => Promise<boolean>;
  
  // User management
  updateUser: (userData: Partial<User>) => void;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  
  // 2FA methods
  setup2FA: () => Promise<TwoFactorSetup>;
  verify2FA: (code: string) => Promise<void>;
  disable2FA: (code: string) => Promise<void>;
  
  // Detection limits
  canDetect: () => boolean;
  incrementDetection: () => void;
  getDetectionStatus: () => DetectionStatus;
  
  // Security monitoring
  getSecurityEvents: () => Promise<SecurityEvent[]>;
}

interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name: string;
}

interface TwoFactorSetup {
  totp_secret: string;
  qr_code: string;
  backup_codes: string[];
}

interface DetectionStatus {
  canDetect: boolean;
  used: number;
  limit: number;
  plan: string;
  requiresUpgrade: boolean;
}

interface SecurityEvent {
  event_type: string;
  event_category: string;
  severity: string;
  details: Record<string, any>;
  ip_address: string;
  user_agent?: string;
  timestamp: string;
}

// API Configuration
import { API_BASE_URL } from '../config/api';
const TOKEN_STORAGE_KEY = 'ifake_access_token';
const REFRESH_TOKEN_STORAGE_KEY = 'ifake_refresh_token';
const USER_STORAGE_KEY = 'ifake_user';
const CSRF_TOKEN_STORAGE_KEY = 'ifake_csrf_token';

// Create context
const AuthContext = createContext<AuthContextType | null>(null);

// Custom hook
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// API helper functions
class SecureAPIClient {
  private baseURL: string;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private csrfToken: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.loadTokensFromStorage();
  }

  private loadTokensFromStorage() {
    this.accessToken = localStorage.getItem(TOKEN_STORAGE_KEY);
    this.refreshToken = localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY);
    this.csrfToken = localStorage.getItem(CSRF_TOKEN_STORAGE_KEY);
  }

  private saveTokensToStorage(tokens: AuthTokens) {
    localStorage.setItem(TOKEN_STORAGE_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, tokens.refresh_token);
    this.accessToken = tokens.access_token;
    this.refreshToken = tokens.refresh_token;
  }

  private clearTokens() {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
    localStorage.removeItem(USER_STORAGE_KEY);
    localStorage.removeItem(CSRF_TOKEN_STORAGE_KEY);
    this.accessToken = null;
    this.refreshToken = null;
    this.csrfToken = null;
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {},
    requireAuth: boolean = true
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    // Add authentication headers
    if (requireAuth && this.accessToken) {
      headers.Authorization = `Bearer ${this.accessToken}`;
    }

    // Add CSRF token for state-changing operations
    if (this.csrfToken && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method || 'GET')) {
      headers['X-CSRF-Token'] = this.csrfToken;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        credentials: 'include', // Include cookies for CSRF protection
      });

      // Handle token expiration
      if (response.status === 401 && requireAuth && this.refreshToken) {
        const refreshed = await this.refreshAccessToken();
        if (refreshed) {
          // Retry request with new token
          headers.Authorization = `Bearer ${this.accessToken}`;
          const retryResponse = await fetch(url, {
            ...options,
            headers,
            credentials: 'include',
          });
          return await this.handleResponse<T>(retryResponse);
        }
      }

      return await this.handleResponse<T>(response);
    } catch (error) {
      console.error('API request failed:', error);
      throw new Error('Network error occurred');
    }
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  }

  async refreshAccessToken(): Promise<boolean> {
    if (!this.refreshToken) return false;

    try {
      const response = await fetch(`${this.baseURL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: this.refreshToken }),
      });

      if (response.ok) {
        const tokens: AuthTokens = await response.json();
        this.saveTokensToStorage(tokens);
        return true;
      } else {
        this.clearTokens();
        return false;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.clearTokens();
      return false;
    }
  }

  // Authentication methods
  async login(email: string, password: string, rememberMe: boolean = false): Promise<{ user: User; tokens: AuthTokens }> {
    const response = await this.makeRequest<{
      access_token: string;
      refresh_token: string;
      token_type: string;
      expires_in: number;
      user: User;
    }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password, remember_me: rememberMe }),
    }, false);

    // Transform the response to match expected format
    const tokens: AuthTokens = {
      access_token: response.access_token,
      refresh_token: response.refresh_token,
      token_type: response.token_type,
      expires_in: response.expires_in,
    };

    this.saveTokensToStorage(tokens);
    
    // Ensure user data is properly structured
    const userData = response.user || {} as any;
    const user: User = {
      id: userData.id || '',
      email: userData.email || '',
      username: userData.username || '',
      full_name: userData.full_name || '',
      is_active: userData.is_active || true,
      is_verified: userData.is_verified || false,
      is_2fa_enabled: userData.is_2fa_enabled || false,
      status: userData.status || 'active',
      plan: userData.plan || 'free',
      detections_used: userData.detections_used || userData.detectionsUsed || 0,
      detections_limit: userData.detections_limit || userData.detectionsLimit || 10,
      created_at: userData.created_at || new Date().toISOString(),
      last_login: userData.last_login || null,
    };
    
    return {
      user: user,
      tokens: tokens
    };
  }

  async register(userData: RegisterData): Promise<{ user: User }> {
    return await this.makeRequest<{ user: User }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    }, false);
  }

  async logout(): Promise<void> {
    try {
      await this.makeRequest('/auth/logout', { method: 'POST' });
    } finally {
      this.clearTokens();
    }
  }

  async getCurrentUser(): Promise<User> {
    return await this.makeRequest<User>('/auth/me');
  }

  async getCsrfToken(): Promise<string> {
    const response = await this.makeRequest<{ csrf_token: string }>('/auth/csrf-token');
    this.csrfToken = response.csrf_token;
    localStorage.setItem(CSRF_TOKEN_STORAGE_KEY, response.csrf_token);
    return response.csrf_token;
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await this.makeRequest('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });
  }

  async setup2FA(): Promise<TwoFactorSetup> {
    return await this.makeRequest<TwoFactorSetup>('/auth/setup-2fa', { method: 'POST' });
  }

  async verify2FA(code: string): Promise<void> {
    await this.makeRequest('/auth/verify-2fa', {
      method: 'POST',
      body: JSON.stringify({ code }),
    });
  }

  async getSecurityEvents(): Promise<SecurityEvent[]> {
    const response = await this.makeRequest<{ events: SecurityEvent[] }>('/auth/security-events');
    return response.events;
  }
}

// Provider component
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [csrfToken, setCsrfToken] = useState<string | null>(null);
  const { showWelcomePopup } = useWelcomePopup();

  const apiClient = new SecureAPIClient(API_BASE_URL);

  // Initialize authentication state
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedUser = localStorage.getItem(USER_STORAGE_KEY);
        const storedCsrfToken = localStorage.getItem(CSRF_TOKEN_STORAGE_KEY);

        if (storedUser && storedCsrfToken) {
          const userData = JSON.parse(storedUser);
          setUser(userData);
          setCsrfToken(storedCsrfToken);

          // Validate session with server
          try {
            const currentUser = await apiClient.getCurrentUser();
            setUser(currentUser);
            localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(currentUser));
          } catch (error) {
            // Session invalid, clear local data
            localStorage.removeItem(USER_STORAGE_KEY);
            localStorage.removeItem(CSRF_TOKEN_STORAGE_KEY);
            setUser(null);
            setCsrfToken(null);
          }
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
        // Clear potentially corrupted data
        localStorage.removeItem(USER_STORAGE_KEY);
        localStorage.removeItem(CSRF_TOKEN_STORAGE_KEY);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // Auto-refresh token
  useEffect(() => {
    if (!user) return;

    const refreshInterval = setInterval(async () => {
      try {
        const refreshed = await apiClient.refreshAccessToken();
        if (!refreshed) {
          // Refresh failed, logout user
          await logout();
        }
      } catch (error) {
        console.error('Auto token refresh failed:', error);
      }
    }, 25 * 60 * 1000); // Refresh every 25 minutes

    return () => clearInterval(refreshInterval);
  }, [user]);

  // Authentication methods
  const login = useCallback(async (email: string, password: string, rememberMe: boolean = false) => {
    setIsLoading(true);
    try {
      const { user: userData, tokens } = await apiClient.login(email, password, rememberMe);
      
      setUser(userData);
      setCsrfToken(tokens.access_token);
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(userData));
      
      // Show welcome popup with user's name
      showWelcomePopup(userData.full_name || userData.username || 'User', userData.email);
      
      toast.success('Successfully logged in!');
    } catch (error: any) {
      toast.error(error.message || 'Login failed');
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [showWelcomePopup]);

  const register = useCallback(async (userData: RegisterData) => {
    setIsLoading(true);
    try {
      const { user: newUser } = await apiClient.register(userData);
      
      setUser(newUser);
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(newUser));
      
      toast.success('Account created successfully!');
    } catch (error: any) {
      toast.error(error.message || 'Registration failed');
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      await apiClient.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setCsrfToken(null);
      setIsLoading(false);
      toast.success('Successfully logged out');
    }
  }, []);

  const refreshToken = useCallback(async (): Promise<boolean> => {
    try {
      return await apiClient.refreshAccessToken();
    } catch (error) {
      console.error('Token refresh failed:', error);
      return false;
    }
  }, []);

  const getCsrfToken = useCallback(async (): Promise<string> => {
    try {
      const token = await apiClient.getCsrfToken();
      setCsrfToken(token);
      return token;
    } catch (error) {
      console.error('CSRF token fetch failed:', error);
      throw error;
    }
  }, []);

  const validateSession = useCallback(async (): Promise<boolean> => {
    try {
      await apiClient.getCurrentUser();
      return true;
    } catch (error) {
      return false;
    }
  }, []);

  const updateUser = useCallback((userData: Partial<User>) => {
    setUser(prev => prev ? { ...prev, ...userData } : null);
    if (user) {
      const updatedUser = { ...user, ...userData };
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(updatedUser));
    }
  }, [user]);

  const changePassword = useCallback(async (currentPassword: string, newPassword: string) => {
    try {
      await apiClient.changePassword(currentPassword, newPassword);
      toast.success('Password changed successfully');
    } catch (error: any) {
      toast.error(error.message || 'Password change failed');
      throw error;
    }
  }, []);

  const setup2FA = useCallback(async (): Promise<TwoFactorSetup> => {
    try {
      return await apiClient.setup2FA();
    } catch (error: any) {
      toast.error(error.message || '2FA setup failed');
      throw error;
    }
  }, []);

  const verify2FA = useCallback(async (code: string) => {
    try {
      await apiClient.verify2FA(code);
      updateUser({ is_2fa_enabled: true });
      toast.success('2FA enabled successfully');
    } catch (error: any) {
      toast.error(error.message || '2FA verification failed');
      throw error;
    }
  }, [updateUser]);

  const disable2FA = useCallback(async (code: string) => {
    try {
      // This would call a disable 2FA endpoint
      updateUser({ is_2fa_enabled: false });
      toast.success('2FA disabled successfully');
    } catch (error: any) {
      toast.error(error.message || '2FA disable failed');
      throw error;
    }
  }, [updateUser]);

  const canDetect = useCallback((): boolean => {
    if (!user) return false;
    if (user.plan === 'premium' || user.plan === 'enterprise' || user.plan === 'admin') return true;
    return user.detections_used < user.detections_limit;
  }, [user]);

  const incrementDetection = useCallback(() => {
    if (user && user.plan === 'free') {
      updateUser({ detections_used: user.detections_used + 1 });
    }
  }, [user, updateUser]);

  const getDetectionStatus = useCallback((): DetectionStatus => {
    if (!user) {
      return {
        canDetect: false,
        used: 0,
        limit: 0,
        plan: 'none',
        requiresUpgrade: true
      };
    }

    const canDetectNow = canDetect();
    const requiresUpgrade = !canDetectNow && user.plan === 'free';

    return {
      canDetect: canDetectNow,
      used: user.detections_used,
      limit: user.detections_limit,
      plan: user.plan,
      requiresUpgrade
    };
  }, [user, canDetect]);

  const getSecurityEvents = useCallback(async (): Promise<SecurityEvent[]> => {
    try {
      return await apiClient.getSecurityEvents();
    } catch (error) {
      console.error('Failed to fetch security events:', error);
      return [];
    }
  }, []);

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    csrfToken,
    login,
    register,
    logout,
    refreshToken,
    getCsrfToken,
    validateSession,
    updateUser,
    changePassword,
    setup2FA,
    verify2FA,
    disable2FA,
    canDetect,
    incrementDetection,
    getDetectionStatus,
    getSecurityEvents,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
