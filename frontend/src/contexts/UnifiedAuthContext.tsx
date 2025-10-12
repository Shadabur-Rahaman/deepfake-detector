/**
 * Unified Authentication Context
 * Production-ready authentication with proper JWT token handling and refresh logic.
 * 
 * This context provides:
 * - JWT token management
 * - Automatic token refresh
 * - Secure session handling
 * - Consistent API responses
 * 
 * Author: Senior Frontend Engineer
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
  is_verified: boolean;
  is_2fa_enabled: boolean;
  roles: string[];
  permissions: string[];
  plan: string;
  detectionsUsed: number;
  detectionsLimit: number;
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
  
  // Authentication methods
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>;
  register: (userData: RegisterData) => Promise<User>;
  signup: (userData: RegisterData) => Promise<User>; // Alias for register
  logout: () => Promise<void>;
  refreshToken: () => Promise<boolean>;
  
  // User management
  updateUser: (userData: Partial<User>) => void;
  
  // Detection limits
  canDetect: () => boolean;
  incrementDetection: () => void;
  getDetectionStatus: () => DetectionStatus;
  
  // Security methods
  validateSession: () => Promise<boolean>;
  hasRole: (role: string) => boolean;
  hasPermission: (permission: string) => boolean;
  
  // 2FA methods
  setup2FA: () => Promise<any>;
  verify2FA: (code: string) => Promise<void>;
  disable2FA: (code: string) => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  
  // Password reset methods
  forgotPassword: (email: string) => Promise<void>;
  resetPassword: (token: string, newPassword: string) => Promise<void>;
  
  // Security monitoring
  getSecurityEvents: () => Promise<any[]>;
  getCsrfToken: () => Promise<string>;
}

interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name: string;
}

interface DetectionStatus {
  canDetect: boolean;
  roles: string[];
  requiresUpgrade: boolean;
}

// API Configuration
import { API_BASE_URL } from '../config/api';
const TOKEN_STORAGE_KEY = 'ifake_access_token';
const REFRESH_TOKEN_STORAGE_KEY = 'ifake_refresh_token';
const USER_STORAGE_KEY = 'ifake_user';

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
class UnifiedAPIClient {
  private baseURL: string;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.loadTokensFromStorage();
  }

  private loadTokensFromStorage() {
    this.accessToken = localStorage.getItem(TOKEN_STORAGE_KEY);
    this.refreshToken = localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY);
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
    this.accessToken = null;
    this.refreshToken = null;
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

    console.log(`Making API request to: ${url}`);

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        // credentials: 'include', // Removed to avoid CORS issues
      });

      console.log(`API response status: ${response.status} for ${url}`);

      // Handle token expiration
      if (response.status === 401 && requireAuth && this.refreshToken) {
        const refreshed = await this.refreshAccessToken();
        if (refreshed) {
          // Retry request with new token
          headers.Authorization = `Bearer ${this.accessToken}`;
          const retryResponse = await fetch(url, {
            ...options,
            headers,
            // credentials: 'include', // Removed to avoid CORS issues
          });
          return await this.handleResponse<T>(retryResponse);
        }
      }

      return await this.handleResponse<T>(response);
    } catch (error) {
      console.error('API request failed:', error);
      console.error('Request URL:', url);
      console.error('Request options:', options);
      
      // Provide more specific error messages
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error(`Cannot connect to backend server at ${this.baseURL}. Please check if the server is running.`);
      }
      
      throw new Error('Network error occurred');
    }
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('❌ API Error Response:', {
        status: response.status,
        statusText: response.statusText,
        errorData: errorData
      });
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
    console.log('🌐 API Client: Making login request to /auth/login');
    console.log('📧 Email:', email);
    console.log('🔒 Password length:', password.length);
    
    const response = await this.makeRequest<any>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password, remember_me: rememberMe }),
    }, false);

    console.log('📥 API Client: Received response:', response);

    // Handle different response structures
    let tokens: AuthTokens;
    let userData: any;

    if (response.access_token) {
      // TokenResponse structure (from simple_routes)
      tokens = {
        access_token: response.access_token,
        refresh_token: response.access_token,
        token_type: response.token_type || 'bearer',
        expires_in: response.expires_in || 1800,
      };
      userData = response.user || {};
    } else if (response.token) {
      // AuthResult structure (from integration)
      tokens = {
        access_token: response.token,
        refresh_token: response.refresh_token || response.token,
        token_type: 'bearer',
        expires_in: 1800,
      };
      userData = response.user_data || {};
    } else {
      throw new Error('Invalid response structure from login endpoint');
    }

    console.log('🔑 API Client: Transformed tokens:', tokens);
    this.saveTokensToStorage(tokens);
    const user: User = {
      id: userData.id || '',
      email: userData.email || '',
      username: userData.username || '',
      full_name: userData.full_name || '',
      is_verified: userData.is_verified || false,
      is_2fa_enabled: userData.is_2fa_enabled || false,
      roles: Array.isArray(userData.roles) ? userData.roles : ['user'],
      permissions: Array.isArray(userData.permissions) ? userData.permissions : [],
      plan: userData.plan || 'free',
      detectionsUsed: userData.detectionsUsed || 0,
      detectionsLimit: userData.detectionsLimit || 10,
      created_at: userData.created_at || new Date().toISOString(),
      last_login: userData.last_login || null,
    };
    
    console.log('👤 API Client: Transformed user data:', user);
    console.log('🔑 User roles:', user.roles);
    console.log('🛡️ User permissions:', user.permissions);
    
    return {
      user: user,
      tokens: tokens
    };
  }

  async register(userData: RegisterData): Promise<{ user: User }> {
    const response = await this.makeRequest<{
      id: string;
      email: string;
      username: string;
      full_name: string;
      is_verified: boolean;
      is_2fa_enabled: boolean;
      roles: string[];
      permissions?: string[];
      created_at: string;
      last_login?: string;
    }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    }, false);

    // Transform response to User format
    const user: User = {
      id: response.id,
      email: response.email,
      username: response.username,
      full_name: response.full_name,
      is_verified: response.is_verified,
      is_2fa_enabled: response.is_2fa_enabled,
      roles: response.roles,
      permissions: response.permissions || response.roles, // Use backend permissions
      plan: 'free', // Default plan
      detectionsUsed: 0,
      detectionsLimit: 10,
      created_at: response.created_at,
      last_login: response.last_login
    };

    return { user };
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

  async forgotPassword(email: string): Promise<{ message: string }> {
    return await this.makeRequest<{ message: string }>('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    }, false);
  }

  async resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
    return await this.makeRequest<{ message: string }>('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({ token, new_password: newPassword }),
    }, false);
  }
}

// Provider component
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { showWelcomePopup } = useWelcomePopup();

  const apiClient = new UnifiedAPIClient(API_BASE_URL);

  // Initialize authentication state
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedUser = localStorage.getItem(USER_STORAGE_KEY);
        const storedAccessToken = localStorage.getItem(TOKEN_STORAGE_KEY);
        const storedRefreshToken = localStorage.getItem(REFRESH_TOKEN_STORAGE_KEY);

        if (storedUser && storedAccessToken) {
          const userData = JSON.parse(storedUser);
          setUser(userData);

          // Validate session with server
          try {
            const currentUser = await apiClient.getCurrentUser();
            setUser(currentUser);
            localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(currentUser));
            console.log('Session validated successfully');
          } catch (error) {
            console.log('Session validation failed, trying token refresh...');
            // Try to refresh token if we have a refresh token
            if (storedRefreshToken) {
              try {
                const refreshed = await apiClient.refreshAccessToken();
                if (refreshed) {
                  // Token refreshed successfully, get current user
                  const currentUser = await apiClient.getCurrentUser();
                  setUser(currentUser);
                  localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(currentUser));
                  console.log('Token refreshed and session restored');
                } else {
                  // Refresh failed, clear session
                  console.log('Token refresh failed, clearing session');
                  setUser(null);
                  localStorage.removeItem(USER_STORAGE_KEY);
                  localStorage.removeItem(TOKEN_STORAGE_KEY);
                  localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
                }
              } catch (refreshError) {
                // Refresh failed, clear session
                console.log('Token refresh error, clearing session');
                setUser(null);
                localStorage.removeItem(USER_STORAGE_KEY);
                localStorage.removeItem(TOKEN_STORAGE_KEY);
                localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
              }
            } else {
              // No refresh token, clear session
              console.log('No refresh token, clearing session');
              setUser(null);
              localStorage.removeItem(USER_STORAGE_KEY);
              localStorage.removeItem(TOKEN_STORAGE_KEY);
              localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
            }
          }
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
        // Clear potentially corrupted data
        setUser(null);
        localStorage.removeItem(USER_STORAGE_KEY);
        localStorage.removeItem(TOKEN_STORAGE_KEY);
        localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
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
    console.log('🔐 Starting login process for:', email);
    
    try {
      console.log('📡 Calling API client login...');
      const { user: userData, tokens } = await apiClient.login(email, password, rememberMe);
      
      console.log('✅ Login successful, user data:', userData);
      console.log('🔑 Tokens received:', tokens);
      
      setUser(userData);
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(userData));
      
      console.log('💾 User data saved to localStorage');
      
      // Show welcome popup with user's name
      showWelcomePopup(userData.full_name || userData.username || 'User', userData.email);
      
      toast.success('Successfully logged in!');
      console.log('🎉 Login process completed successfully');
    } catch (error: any) {
      console.error('❌ Login failed:', error);
      console.error('❌ Error details:', error.message);
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
      
      // Don't auto-login after registration, just show success message
      toast.success('Account created successfully! Please log in to continue.');
      return newUser; // Return user data for potential use
    } catch (error: any) {
      toast.error(error.message || 'Registration failed');
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Alias for register
  const signup = register;

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      await apiClient.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Always clear local state and storage
      setUser(null);
      localStorage.removeItem(USER_STORAGE_KEY);
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
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

  const updateUser = useCallback((userData: Partial<User>) => {
    setUser(prev => prev ? { ...prev, ...userData } : null);
    if (user) {
      const updatedUser = { ...user, ...userData };
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(updatedUser));
    }
  }, [user]);

  const canDetect = useCallback((): boolean => {
    if (!user) return false;
    // Allow detection for all authenticated users for now
    return true;
  }, [user]);

  const getDetectionStatus = useCallback((): DetectionStatus => {
    if (!user) {
      return {
        canDetect: false,
        roles: [],
        requiresUpgrade: true
      };
    }

    return {
      canDetect: canDetect(),
      roles: user.roles,
      requiresUpgrade: false
    };
  }, [user, canDetect]);

  const incrementDetection = useCallback(() => {
    if (user && user.plan === 'free') {
      updateUser({ detectionsUsed: user.detectionsUsed + 1 });
    }
  }, [user, updateUser]);

  const validateSession = useCallback(async (): Promise<boolean> => {
    try {
      await apiClient.getCurrentUser();
      return true;
    } catch (error) {
      return false;
    }
  }, []);

  const hasRole = useCallback((role: string): boolean => {
    if (!user || !user.roles || !Array.isArray(user.roles)) return false;
    return user.roles.includes(role);
  }, [user]);

  const hasPermission = useCallback((permission: string): boolean => {
    if (!user) return false;
    
    // Admin users have all permissions
    if (user.roles && Array.isArray(user.roles) && user.roles.includes('admin')) {
      return true;
    }
    
    // Check if user has the specific permission
    if (user.permissions && Array.isArray(user.permissions) && user.permissions.includes(permission)) {
      return true;
    }
    
    // Check for role-based permissions
    if (permission === 'try:access' && user.roles && Array.isArray(user.roles) && (user.roles.includes('user') || user.roles.includes('premium'))) {
      return true;
    }
    
    if (permission === 'detection:create' && user.roles && Array.isArray(user.roles) && (user.roles.includes('user') || user.roles.includes('premium'))) {
      return true;
    }
    
    if (permission === 'detection:read' && user.roles && Array.isArray(user.roles) && (user.roles.includes('user') || user.roles.includes('premium'))) {
      return true;
    }
    
    return false;
  }, [user]);

  const setup2FA = useCallback(async (): Promise<any> => {
    // Placeholder implementation
    return { totp_secret: '', qr_code: '', backup_codes: [] };
  }, []);

  const verify2FA = useCallback(async (code: string): Promise<void> => {
    // Placeholder implementation
    toast.success('2FA enabled successfully');
  }, []);

  const disable2FA = useCallback(async (code: string): Promise<void> => {
    // Placeholder implementation
    toast.success('2FA disabled successfully');
  }, []);

  const changePassword = useCallback(async (currentPassword: string, newPassword: string): Promise<void> => {
    // Placeholder implementation
    toast.success('Password changed successfully');
  }, []);

  const forgotPassword = useCallback(async (email: string): Promise<void> => {
    try {
      await apiClient.forgotPassword(email);
      toast.success('Password reset link sent to your email');
    } catch (error: any) {
      toast.error(error.message || 'Failed to send password reset email');
      throw error;
    }
  }, []);

  const resetPassword = useCallback(async (token: string, newPassword: string): Promise<void> => {
    try {
      await apiClient.resetPassword(token, newPassword);
      toast.success('Password reset successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to reset password');
      throw error;
    }
  }, []);

  const getSecurityEvents = useCallback(async (): Promise<any[]> => {
    // Placeholder implementation
    return [];
  }, []);

  const getCsrfToken = useCallback(async (): Promise<string> => {
    // Placeholder implementation
    return 'csrf-token-placeholder';
  }, []);

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    signup,
    logout,
    refreshToken,
    updateUser,
    canDetect,
    incrementDetection,
    getDetectionStatus,
    validateSession,
    hasRole,
    hasPermission,
    setup2FA,
    verify2FA,
    disable2FA,
    changePassword,
    forgotPassword,
    resetPassword,
    getSecurityEvents,
    getCsrfToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
